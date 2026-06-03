"""
Module: bouncebox_regle.py
Parseur et interpréteur du DSL BounceBox (.bb).

Le DSL supporte :
  - Variables de configuration : NOM = VALEUR
  - Règles de collision        : JOUEUR frappe BOULE -> ACTION

Exemple de fichier regles.bb :
    POINTS_VICTOIRE  = 5
    NB_BOULES_GRISES = 9
    NB_BOULES_BLEUES = 2

    ROUGE frappe ROUGE -> POINT
    ROUGE frappe GRISE -> COLORIE ROUGE
    BLEU  frappe BLEUE -> POINT

Usage :
    from bouncebox_regle import ChargerRegles
    regles = ChargerRegles("regles.bb")
    regles.appliquer(joueur_actif, boule, tapis)
    nb_points = regles.config["POINTS_VICTOIRE"]
"""

import os


# ── Valeurs par défaut (si le fichier .bb est absent ou incomplet) ──
DEFAUTS = {
    "POINTS_VICTOIRE":  5,
    "NB_BOULES_GRISES": 9,
    "NB_BOULES_BLEUES": 2,
}

# Variables autorisées et leurs contraintes (min, max)
VARIABLES_AUTORISEES = {
    "POINTS_VICTOIRE":  (1, 20),
    "NB_BOULES_GRISES": (0, 30),
    "NB_BOULES_BLEUES": (0, 10),
}

# Couleurs reconnues par le DSL → valeur enum Couleur
COULEURS_DSL = {"ROUGE", "BLEUE", "GRISE", "BLANCHE"}

# Actions reconnues
ACTIONS_DSL = {"POINT", "COLORIE"}


class ErreurDSL(Exception):
    """Levée quand le fichier .bb contient une erreur de syntaxe ou de valeur."""
    pass


class Regle:
    """
    Représente une règle de collision parsée.

    Attributes:
        joueur_couleur (str): Couleur du joueur ("ROUGE" ou "BLEU")
        boule_couleur  (str): Couleur de la boule frappée
        action         (str): "POINT" ou "COLORIE"
        cible_couleur  (str|None): Couleur cible pour COLORIE, None pour POINT
    """

    def __init__(self, joueur_couleur, boule_couleur, action, cible_couleur=None):
        self.joueur_couleur = joueur_couleur
        self.boule_couleur  = boule_couleur
        self.action         = action
        self.cible_couleur  = cible_couleur

    def correspond(self, joueur_actif, boule):
        """
        Vérifie si cette règle s'applique à la situation courante.

        Args:
            joueur_actif : instance Joueur
            boule        : instance BouleCouleur
        Returns:
            bool
        """
        couleur_joueur = joueur_actif.couleur.value.upper()
        couleur_boule  = boule.couleur.value.upper()
        # Normalise "BLEUE" → "BLEU" pour le joueur (l'enum joueur dit "bleue")
        couleur_joueur = "BLEU" if couleur_joueur == "BLEUE" else couleur_joueur
        return (couleur_joueur == self.joueur_couleur and
                couleur_boule  == self.boule_couleur)

    def __repr__(self):
        if self.action == "POINT":
            return f"Regle({self.joueur_couleur} frappe {self.boule_couleur} -> POINT)"
        return (f"Regle({self.joueur_couleur} frappe {self.boule_couleur} "
                f"-> COLORIE {self.cible_couleur})")


class ChargerRegles:
    """
    Charge et expose les règles et la configuration depuis un fichier .bb.

    Attributes:
        config (dict): Variables de configuration lues (POINTS_VICTOIRE, etc.)
        regles (list[Regle]): Liste des règles de collision parsées
    """

    def __init__(self, chemin="regles.bb"):
        """
        Charge le fichier DSL. Utilise les valeurs par défaut si absent.

        Args:
            chemin (str): Chemin vers le fichier .bb
        """
        self.chemin = chemin
        self.config = dict(DEFAUTS)   # copie des défauts
        self.regles = []

        if not os.path.exists(chemin):
            print(f"⚠️  {chemin} introuvable — valeurs par défaut utilisées.")
            return

        self._parser(chemin)
        print(f"✅ Règles chargées depuis {chemin} "
              f"({len(self.regles)} règle(s), config={self.config})")

    # ──────────────────────────────────────────────────────────────
    # Parseur
    # ──────────────────────────────────────────────────────────────

    def _parser(self, chemin):
        """Lit le fichier ligne par ligne et remplit config + regles."""
        with open(chemin, encoding="utf-8") as f:
            for num, ligne in enumerate(f, start=1):
                ligne = ligne.strip()

                # Ignorer lignes vides et commentaires
                if not ligne or ligne.startswith("#"):
                    continue

                # Variable : NOM = VALEUR
                if "=" in ligne and "frappe" not in ligne:
                    self._parser_variable(ligne, num)

                # Règle : JOUEUR frappe BOULE -> ACTION
                elif "frappe" in ligne and "->" in ligne:
                    self._parser_regle(ligne, num)

                else:
                    raise ErreurDSL(
                        f"Ligne {num} non reconnue : «{ligne}»\n"
                        f"Format attendu :\n"
                        f"  NOM = VALEUR\n"
                        f"  JOUEUR frappe BOULE -> ACTION"
                    )

    def _parser_variable(self, ligne, num):
        """Parse une ligne de type  NOM = VALEUR."""
        parties = [p.strip() for p in ligne.split("=", 1)]
        if len(parties) != 2:
            raise ErreurDSL(f"Ligne {num} — syntaxe variable invalide : «{ligne}»")

        nom, valeur_str = parties

        if nom not in VARIABLES_AUTORISEES:
            raise ErreurDSL(
                f"Ligne {num} — variable inconnue : «{nom}»\n"
                f"Variables autorisées : {list(VARIABLES_AUTORISEES.keys())}"
            )

        try:
            valeur = int(valeur_str)
        except ValueError:
            raise ErreurDSL(
                f"Ligne {num} — «{nom}» doit être un entier, reçu : «{valeur_str}»"
            )

        min_val, max_val = VARIABLES_AUTORISEES[nom]
        if not (min_val <= valeur <= max_val):
            raise ErreurDSL(
                f"Ligne {num} — «{nom}» doit être entre {min_val} et {max_val}, "
                f"reçu : {valeur}"
            )

        self.config[nom] = valeur

    def _parser_regle(self, ligne, num):
        """Parse une ligne de type  JOUEUR frappe BOULE -> ACTION [CIBLE]."""
        # Séparer la condition de l'action
        parties = [p.strip() for p in ligne.split("->", 1)]
        if len(parties) != 2:
            raise ErreurDSL(f"Ligne {num} — «->» manquant : «{ligne}»")

        condition_str, action_str = parties

        # Parser la condition : JOUEUR frappe BOULE
        mots_cond = condition_str.split()
        if len(mots_cond) != 3 or mots_cond[1].lower() != "frappe":
            raise ErreurDSL(
                f"Ligne {num} — condition invalide : «{condition_str}»\n"
                f"Format attendu : JOUEUR frappe BOULE"
            )

        joueur_str = mots_cond[0].upper()
        boule_str  = mots_cond[2].upper()

        # Normaliser BLEU/BLEUE → BLEU pour le joueur
        if joueur_str not in ("ROUGE", "BLEU"):
            raise ErreurDSL(
                f"Ligne {num} — joueur invalide : «{joueur_str}» "
                f"(attendu ROUGE ou BLEU)"
            )
        if boule_str not in COULEURS_DSL:
            raise ErreurDSL(
                f"Ligne {num} — couleur de boule invalide : «{boule_str}» "
                f"(attendu : {COULEURS_DSL})"
            )

        # Parser l'action
        mots_action = action_str.split()
        action = mots_action[0].upper()

        if action not in ACTIONS_DSL:
            raise ErreurDSL(
                f"Ligne {num} — action inconnue : «{action}» "
                f"(attendu : {ACTIONS_DSL})"
            )

        cible = None
        if action == "COLORIE":
            if len(mots_action) != 2:
                raise ErreurDSL(
                    f"Ligne {num} — COLORIE nécessite une couleur cible : «{action_str}»"
                )
            cible = mots_action[1].upper()
            if cible not in COULEURS_DSL:
                raise ErreurDSL(
                    f"Ligne {num} — couleur cible invalide : «{cible}» "
                    f"(attendu : {COULEURS_DSL})"
                )
        elif action == "POINT" and len(mots_action) != 1:
            raise ErreurDSL(
                f"Ligne {num} — POINT ne prend pas de paramètre : «{action_str}»"
            )

        self.regles.append(Regle(joueur_str, boule_str, action, cible))

    # ──────────────────────────────────────────────────────────────
    # Interpréteur
    # ──────────────────────────────────────────────────────────────

    def appliquer(self, joueur_actif, boule, tapis):
        """
        Cherche et exécute la première règle qui correspond à la situation.

        Args:
            joueur_actif : instance Joueur
            boule        : instance BouleCouleur
            tapis        : instance Tapis
        Returns:
            bool: True si une règle a été appliquée, False sinon
        """
        from bouncebox_boules import Couleur

        for regle in self.regles:
            if not regle.correspond(joueur_actif, boule):
                continue

            if regle.action == "POINT":
                joueur_actif.incrementer_score()
                tapis.retirer_boule(boule)
                print(f"POINT ! Boule {boule.couleur.value} capturée par "
                      f"{joueur_actif.nom} ({joueur_actif.score}/"
                      f"{self.config['POINTS_VICTOIRE']})")

            elif regle.action == "COLORIE":
                couleur_map = {
                    "ROUGE":   Couleur.ROUGE,
                    "BLEUE":   Couleur.BLEUE,
                    "GRISE":   Couleur.GRISE,
                    "BLANCHE": Couleur.BLANCHE,
                }
                nouvelle = couleur_map[regle.cible_couleur]
                ancienne = boule.couleur.value
                boule.changer_couleur(nouvelle)
                print(f"Boule {ancienne} → {regle.cible_couleur.lower()}")

            return True  # Première règle correspondante appliquée, on s'arrête

        return False  # Aucune règle ne correspond
