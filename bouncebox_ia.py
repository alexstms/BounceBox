"""
Module: bouncebox_ia.py
Intelligence Artificielle pour le jeu BounceBox.

Définit un joueur contrôlé par l'ordinateur (JoueurIA), capable de choisir
automatiquement le meilleur coup à jouer selon un niveau de difficulté.

Classes:
    NiveauIA  -- Enum des niveaux de difficulté (FACILE, MOYEN, DIFFICILE)
    JoueurIA  -- Sous-classe de Joueur avec prise de décision automatique

Figure imposée couverte : Algorithme d'optimisation (recherche du coup optimal
par évaluation de toutes les cibles disponibles et sélection du meilleur score).

Auteur: Alex / BounceBox
"""

import math
import random
from enum import Enum

from bouncebox_boules import Couleur, BouleBlanche, BouleCouleur
from bouncebox_partie import Joueur


class NiveauIA(Enum):
    """Niveaux de difficulté de l'IA."""
    FACILE    = "facile"     # Fort bruit angulaire, force aléatoire
    MOYEN     = "moyen"      # Bruit modéré, cible les meilleures boules
    DIFFICILE = "difficile"  # Quasi-parfait, minimise les erreurs


class JoueurIA(Joueur):
    """
    Joueur contrôlé par l'ordinateur.
    Hérite de Joueur et ajoute la capacité de choisir automatiquement
    un coup selon un algorithme d'optimisation par évaluation de cibles.

    L'IA évalue chaque boule colorée sur le tapis, lui attribue un score
    selon les règles du jeu (sa couleur > neutre > adverse), puis calcule
    l'angle et la force optimaux pour atteindre la cible la mieux notée.
    Un bruit gaussien proportionnel au niveau est ajouté pour simuler
    l'imperfection humaine.
    """

    # Paramètres de bruit angulaire (en radians) par niveau
    _BRUIT_ANGLE = {
        NiveauIA.FACILE:    0.35,   # ~20°
        NiveauIA.MOYEN:     0.12,   # ~7°
        NiveauIA.DIFFICILE: 0.03,   # ~1.7°
    }

    # Délai artificiel (secondes) avant que l'IA joue — pour ne pas être instantané
    DELAI_REFLEXION = {
        NiveauIA.FACILE:    1.2,
        NiveauIA.MOYEN:     0.9,
        NiveauIA.DIFFICILE: 0.6,
    }

    def __init__(self, nom, couleur, niveau=NiveauIA.MOYEN):
        """
        Initialise le joueur IA.

        Args:
            nom    (str):      Nom affiché (ex. "IA Facile")
            couleur (Couleur): Couleur attribuée (ROUGE ou BLEUE)
            niveau (NiveauIA): Niveau de difficulté
        """
        super().__init__(nom, couleur)
        self.niveau = niveau
        self._temps_attente = 0.0      # Temps écoulé depuis le début du tour
        self._coup_joue     = False    # True une fois le coup lancé ce tour

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def reinitialiser_pour_nouveau_tour(self):
        """Remet l'IA en état d'attente pour un nouveau tour."""
        self._temps_attente = 0.0
        self._coup_joue     = False

    def doit_jouer(self, delta_t):
        """
        Indique si l'IA doit lancer son coup maintenant.
        Incrémente le compteur interne et retourne True quand le délai
        de réflexion est écoulé et que le coup n'a pas encore été joué.

        Args:
            delta_t (float): Temps écoulé depuis le dernier frame (secondes)

        Returns:
            bool: True si l'IA doit jouer maintenant
        """
        if self._coup_joue:
            return False
        self._temps_attente += delta_t
        return self._temps_attente >= self.DELAI_REFLEXION[self.niveau]

    def choisir_coup(self, tapis):
        """
        Algorithme central : choisit le meilleur angle et la meilleure
        force pour le coup.

        Stratégie (algorithme d'optimisation par évaluation exhaustive) :
            1. Récupère toutes les BouleCouleur sur le tapis.
            2. Attribue un score à chacune selon les règles de jeu :
               - Boule de la couleur de l'IA : score élevé (gain direct)
               - Boule neutre (grise) : score moyen (prépare la voie)
               - Boule adverse : score faible (la neutralise, mais pas de point)
            3. Trie les cibles par score décroissant → sélectionne la meilleure.
            4. Calcule l'angle parfait boule_blanche → cible.
            5. Ajoute un bruit gaussien (σ selon niveau) sur l'angle.
            6. Choisit une force proportionnelle à la distance + bruit.

        Args:
            tapis (Tapis): Le tapis de jeu courant

        Returns:
            tuple(float, float): (angle en radians, force)
        """
        self._coup_joue = True

        boule_blanche = tapis.obtenir_boule_blanche()
        cible = self._trouver_meilleure_cible(tapis, boule_blanche)

        if cible is None:
            # Aucune cible : coup aléatoire dans une direction quelconque
            angle = random.uniform(0, 2 * math.pi)
            force = random.uniform(15.0, 35.0)
            return angle, force

        # Angle parfait vers la cible
        angle_parfait = self._calculer_angle_vers(boule_blanche, cible)

        # Ajout du bruit angulaire
        sigma = self._BRUIT_ANGLE[self.niveau]
        angle = angle_parfait + random.gauss(0, sigma)

        # Force : distance * facteur + bruit
        distance = boule_blanche.distance_avec(cible)
        force_ideale = min(10.0 + distance * 0.9, 55.0)

        if self.niveau == NiveauIA.FACILE:
            force = force_ideale * random.uniform(0.5, 1.5)
        elif self.niveau == NiveauIA.MOYEN:
            force = force_ideale * random.uniform(0.8, 1.2)
        else:
            force = force_ideale * random.uniform(0.93, 1.07)

        force = max(5.0, min(force, 60.0))
        return angle, force

    # ------------------------------------------------------------------
    # Méthodes internes
    # ------------------------------------------------------------------

    def _trouver_meilleure_cible(self, tapis, boule_blanche):
        """
        Évalue toutes les boules colorées et retourne la cible optimale.

        Système de score :
            - Boule de ma couleur    → 100 − distance  (priorité max)
            - Boule grise            →  50 − distance  (priorité moyenne)
            - Boule de couleur adverse→ 20 − distance  (priorité basse)

        Args:
            tapis         (Tapis):       Tapis de jeu
            boule_blanche (BouleBlanche): La boule blanche

        Returns:
            BouleCouleur | None: La meilleure cible, ou None si aucune
        """
        candidates = [b for b in tapis.boules if isinstance(b, BouleCouleur)]
        if not candidates:
            return None

        meilleure_cible = None
        meilleur_score  = -math.inf

        for boule in candidates:
            distance = boule_blanche.distance_avec(boule)
            score    = self._evaluer_boule(boule, distance)
            if score > meilleur_score:
                meilleur_score  = score
                meilleure_cible = boule

        return meilleure_cible

    def _evaluer_boule(self, boule, distance):
        """
        Calcule le score d'intérêt d'une boule cible.

        Args:
            boule    (BouleCouleur): La boule évaluée
            distance (float):        Distance depuis la boule blanche

        Returns:
            float: Score d'intérêt (plus élevé = plus intéressant)
        """
        if boule.couleur == self.couleur:
            base = 100.0
        elif boule.couleur == Couleur.GRISE:
            base = 50.0
        else:
            # Boule adverse : utile pour la neutraliser si l'IA est en retard
            base = 20.0

        # Pénalité distance : préférer les cibles proches
        return base - distance * 0.5

    def _calculer_angle_vers(self, boule_blanche, cible):
        """
        Calcule l'angle (en radians) de boule_blanche vers cible.

        Args:
            boule_blanche (BouleBlanche): Point de départ
            cible         (BouleCouleur): Point d'arrivée

        Returns:
            float: Angle en radians (repère trigonométrique standard)
        """
        dx = cible.position.x - boule_blanche.position.x
        dy = cible.position.y - boule_blanche.position.y
        return math.atan2(dy, dx)

    def __str__(self):
        return f"{self.nom} [IA {self.niveau.value}] ({self.couleur.value}) - Score: {self.score}"

    def __repr__(self):
        return self.__str__()
