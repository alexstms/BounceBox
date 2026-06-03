"""
Module: bouncebox_ia.py
Intelligence Artificielle pour le jeu BounceBox.

Définit un joueur contrôlé par l'ordinateur (JoueurIA), capable de choisir
automatiquement le meilleur coup à jouer selon un niveau de difficulté.

Classes:
    NiveauIA  -- Enum des niveaux de difficulté (FACILE, MOYEN, DIFFICILE)
    JoueurIA  -- Sous-classe de Joueur avec prise de décision automatique

Figure imposée couverte : Algorithme d'optimisation (recherche du coup optimal
par évaluation de toutes les cibles disponibles, avec bonus combo pour les
boules alignées dans l'axe du tir).

Auteur: Alex / BounceBox
"""

import math
import random
from enum import Enum

from bouncebox_boules import Couleur, BouleBlanche, BouleCouleur
from bouncebox_partie import Joueur


class NiveauIA(Enum):
    """Niveaux de difficulté de l'IA."""
    FACILE    = "facile"
    MOYEN     = "moyen"
    DIFFICILE = "difficile"


class JoueurIA(Joueur):
    """
    Joueur contrôlé par l'ordinateur.
    Hérite de Joueur et ajoute la capacité de choisir automatiquement
    un coup selon un algorithme d'optimisation par évaluation de cibles.

    L'IA évalue chaque boule colorée sur le tapis, lui attribue un score
    selon les règles du jeu, et intègre un bonus combo pour les boules
    supplémentaires alignées dans l'axe du tir. Un bruit gaussien
    proportionnel au niveau simule l'imperfection humaine.
    """

    # Bruit angulaire (σ en radians) par niveau
    _BRUIT_ANGLE = {
        NiveauIA.FACILE:    0.35,   # ~20°
        NiveauIA.MOYEN:     0.12,   # ~7°
        NiveauIA.DIFFICILE: 0.03,   # ~1.7°
    }

    # Délai artificiel avant que l'IA joue (secondes)
    DELAI_REFLEXION = {
        NiveauIA.FACILE:    1.2,
        NiveauIA.MOYEN:     0.9,
        NiveauIA.DIFFICILE: 0.6,
    }

    # Rayon de détection d'un combo (unités logiques) — boule dans le couloir
    _RAYON_COULOIR_COMBO = 3.5

    def __init__(self, nom, couleur, niveau=NiveauIA.MOYEN):
        """
        Initialise le joueur IA.

        Args:
            nom    (str):      Nom affiché
            couleur (Couleur): Couleur attribuée (ROUGE ou BLEUE)
            niveau (NiveauIA): Niveau de difficulté
        """
        super().__init__(nom, couleur)
        self.niveau = niveau
        self._temps_attente = 0.0
        self._coup_joue     = False

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def reinitialiser_pour_nouveau_tour(self):
        """Remet l'IA en état d'attente pour un nouveau tour."""
        self._temps_attente = 0.0
        self._coup_joue     = False

    def doit_jouer(self, delta_t):
        """
        Incrémente le compteur et retourne True quand le délai est écoulé.

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
        Algorithme d'optimisation : choisit le meilleur angle et force.

        Stratégie :
            1. Pour chaque BouleCouleur, calcule l'angle direct boule_blanche→cible.
            2. Évalue le score de la cible (couleur propre > grise > adverse).
            3. Ajoute un bonus combo pour chaque boule supplémentaire de la
               même couleur que la cible qui se trouve dans le couloir de tir
               (distance à l'axe < _RAYON_COULOIR_COMBO), au-delà de la cible.
            4. Sélectionne l'angle au score total maximal.
            5. Ajoute un bruit gaussien calibré par niveau.

        Args:
            tapis (Tapis): Le tapis de jeu courant

        Returns:
            tuple(float, float): (angle en radians, force)
        """
        self._coup_joue = True

        boule_blanche = tapis.obtenir_boule_blanche()
        candidates = [b for b in tapis.boules if isinstance(b, BouleCouleur)]

        if not candidates:
            angle = random.uniform(0, 2 * math.pi)
            force = random.uniform(15.0, 35.0)
            return angle, force

        meilleur_score  = -math.inf
        meilleur_angle  = 0.0
        meilleure_cible = candidates[0]

        for cible in candidates:
            angle_candidat = self._calculer_angle_vers(boule_blanche, cible)
            distance       = boule_blanche.distance_avec(cible)
            score          = self._evaluer_boule(cible, distance)

            # Bonus combo : boules de la même couleur que la cible
            # situées dans le couloir de tir, au-delà de la cible
            score += self._bonus_combo(boule_blanche, cible, angle_candidat, candidates)

            if score > meilleur_score:
                meilleur_score  = score
                meilleur_angle  = angle_candidat
                meilleure_cible = cible

        # Bruit angulaire selon niveau
        sigma = self._BRUIT_ANGLE[self.niveau]
        angle = meilleur_angle + random.gauss(0, sigma)

        # Force proportionnelle à la distance
        distance = boule_blanche.distance_avec(meilleure_cible)
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

    def _evaluer_boule(self, boule, distance):
        """
        Score de base d'une boule cible selon sa couleur et sa proximité.

        Barème :
            - Ma couleur  → 100 (gain direct possible)
            - Grise       →  50 (la colorie à mon avantage)
            - Adverse     →  20 (la neutralise, pas de point mais utile)
        Pénalité distance : -0.5 × distance (préférer les cibles proches).

        Args:
            boule    (BouleCouleur): Boule évaluée
            distance (float):        Distance depuis la boule blanche

        Returns:
            float: Score de base
        """
        if boule.couleur == self.couleur:
            base = 100.0
        elif boule.couleur == Couleur.GRISE:
            base = 50.0
        else:
            base = 20.0
        return base - distance * 0.5

    def _bonus_combo(self, boule_blanche, cible, angle, toutes_boules):
        """
        Calcule un bonus de score si d'autres boules bénéfiques sont
        alignées dans le couloir de tir au-delà de la cible principale.

        Principe : on projette chaque autre boule sur l'axe du tir et on
        mesure sa distance perpendiculaire. Si elle est dans le couloir
        ET plus loin que la cible ET de couleur intéressante, on ajoute
        un bonus décroissant avec la distance.

        Args:
            boule_blanche (BouleBlanche): Point de départ du tir
            cible         (BouleCouleur): Cible principale
            angle         (float):        Angle du tir (radians)
            toutes_boules (list):         Toutes les BouleCouleur

        Returns:
            float: Bonus combo (0 si aucune boule en ligne)
        """
        bonus = 0.0
        ux = math.cos(angle)
        uy = math.sin(angle)

        dist_cible = boule_blanche.distance_avec(cible)

        for boule in toutes_boules:
            if boule is cible:
                continue

            # Vecteur boule_blanche → boule
            dx = boule.position.x - boule_blanche.position.x
            dy = boule.position.y - boule_blanche.position.y

            # Projection sur l'axe du tir (distance le long de l'axe)
            proj = dx * ux + dy * uy

            # On ne considère que les boules AU-DELÀ de la cible
            if proj <= dist_cible:
                continue

            # Distance perpendiculaire à l'axe
            dist_perp = abs(dx * uy - dy * ux)

            if dist_perp > self._RAYON_COULOIR_COMBO:
                continue

            # Boule dans le couloir : bonus selon sa couleur
            if boule.couleur == self.couleur:
                valeur = 60.0   # Boule propre en ligne = très bon
            elif boule.couleur == Couleur.GRISE:
                valeur = 30.0   # Grise en ligne = correct
            else:
                valeur = 5.0    # Adverse en ligne = peu utile

            # Décroissance avec la distance (les boules proches valent plus)
            bonus += valeur / (1.0 + (proj - dist_cible) * 0.1)

        return bonus

    def _calculer_angle_vers(self, boule_blanche, cible):
        """
        Angle (radians) de boule_blanche vers cible.

        Args:
            boule_blanche (BouleBlanche): Point de départ
            cible         (BouleCouleur): Point d'arrivée

        Returns:
            float: Angle en radians (repère trigonométrique)
        """
        dx = cible.position.x - boule_blanche.position.x
        dy = cible.position.y - boule_blanche.position.y
        return math.atan2(dy, dx)

    def __str__(self):
        return f"{self.nom} [IA {self.niveau.value}] ({self.couleur.value}) - Score: {self.score}"

    def __repr__(self):
        return self.__str__()
