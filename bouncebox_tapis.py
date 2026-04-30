"""
Module: tapis.py
Gestion du tapis de jeu, des boules et des collisions physiques.
"""

import random
from bouncebox_vecteur import Vecteur2D
from bouncebox_boules import (
    Boule, BouleBlanche, BouleCouleur, Couleur
)


class Tapis:
    """
    Représente le tapis de jeu avec ses boules et ses bordures.
    Gère la physique, les déplacements et les collisions.
    """

    # Dimensions du tapis (carré, comme un jeu de billard officiel simplifié)
    LARGEUR_DEFAUT = 50.0
    HAUTEUR_DEFAUT = 50.0

    def __init__(self, largeur=LARGEUR_DEFAUT, hauteur=HAUTEUR_DEFAUT):
        """Initialise un tapis vierge."""
        self.largeur = largeur
        self.hauteur = hauteur
        self.boules = []
        self.boule_blanche = None

    def initialiser_partie(self):
        """
        Initialise le tapis avec les boules pour une nouvelle partie.
        Place 12 boules au hasard : 1 blanche, 9 grises, 2 bleues.
        """
        self.boules.clear()

        boule_blanche = BouleBlanche(
            Vecteur2D(self.largeur / 2, self.hauteur * 0.8)
        )
        self.boules.append(boule_blanche)
        self.boule_blanche = boule_blanche

        for _ in range(9):
            pos = self._position_aleatoire()
            self.boules.append(BouleCouleur(pos, Couleur.GRISE))

        for _ in range(2):
            pos = self._position_aleatoire()
            self.boules.append(BouleCouleur(pos, Couleur.BLEUE))

    def _position_aleatoire(self):
        """Génère une position aléatoire sur le tapis sans chevauchement."""
        margin = 3.0
        min_distance = 2 * Boule.RAYON_DEFAUT + 2.0
        max_tentatives = 300

        for _ in range(max_tentatives):
            x = random.uniform(margin, self.largeur - margin)
            y = random.uniform(margin, self.hauteur - margin)
            position = Vecteur2D(x, y)

            collision = False
            for boule in self.boules:
                distance = (position - boule.position).norme()
                if distance < min_distance:
                    collision = True
                    break

            if not collision:
                return position

        return self._position_grille()

    def _position_grille(self):
        """Fallback: position en grille régulière si l'aléatoire échoue."""
        index = len(self.boules)
        espacement_x = self.largeur / 5
        espacement_y = self.hauteur / 4
        margin = 3.0

        col = index % 5
        row = index // 5

        x = margin + (col * espacement_x) + random.uniform(-1, 1)
        y = margin + (row * espacement_y) + random.uniform(-1, 1)

        x = max(margin, min(self.largeur - margin, x))
        y = max(margin, min(self.hauteur - margin, y))

        return Vecteur2D(x, y)

    def obtenir_boule_blanche(self):
        """Retourne la boule blanche."""
        return self.boule_blanche

    def mettre_a_jour(self, delta_t=1.0):
        """
        Met à jour l'état du tapis : déplace les boules et gère les collisions.
        Plusieurs passes de résolution pour traiter les collisions en cascade.
        """
        for boule in self.boules:
            boule.deplacer(delta_t)
            boule.rebound_bordure(self.largeur, self.hauteur)

        # Plusieurs passes pour bien séparer en cas de collision multi-boules
        for _ in range(3):
            self._gerer_collisions()

    def _gerer_collisions(self):
        """Détecte et gère toutes les collisions entre boules. Algo O(n²)."""
        n = len(self.boules)
        for i in range(n):
            for j in range(i + 1, n):
                boule1 = self.boules[i]
                boule2 = self.boules[j]

                if boule1.en_collision_avec(boule2):
                    self._traiter_collision(boule1, boule2)

    def obtenir_collision_blanche_grise(self):
        """Retourne la première boule grise en collision avec la blanche."""
        boule_blanche = self.boule_blanche
        for boule in self.boules:
            if isinstance(boule, BouleCouleur) and boule.couleur == Couleur.GRISE:
                if boule_blanche.en_collision_avec(boule):
                    return boule
        return None

    def _traiter_collision(self, boule1, boule2):
        """
        Traite une collision élastique entre deux boules de masses égales.

        Ordre crucial :
            1. SÉPARATION TOUJOURS appliquée si chevauchement (même au repos),
               c'est ce qui empêche le chevauchement visuel.
            2. ÉCHANGE DES VITESSES uniquement si les boules s'approchent
               (sinon collage et oscillations parasites).
        """
        delta = boule2.position - boule1.position
        distance = delta.norme()

        # Centres confondus : normale arbitraire pour éviter division par zéro
        if distance == 0:
            normale = Vecteur2D(1.0, 0.0)
            distance = 0.0001
        else:
            normale = delta.normalise()

        # === 1. SÉPARATION (toujours, même si v_rel = 0) ===
        chevauchement = (boule1.rayon + boule2.rayon) - distance
        if chevauchement > 0:
            correction = normale * (chevauchement / 2 + 0.001)
            boule1.position = boule1.position - correction
            boule2.position = boule2.position + correction

        # === 2. ÉCHANGE DE VITESSES (seulement si elles s'approchent) ===
        vitesse_relative = boule1.vitesse - boule2.vitesse
        v_rel_normale = vitesse_relative.produit_scalaire(normale)

        if v_rel_normale > 0:
            impulsion = normale * v_rel_normale
            boule1.vitesse = boule1.vitesse - impulsion
            boule2.vitesse = boule2.vitesse + impulsion

            if boule1.vitesse.norme() > Boule.SEUIL_MOUVEMENT:
                boule1.en_mouvement = True
            if boule2.vitesse.norme() > Boule.SEUIL_MOUVEMENT:
                boule2.en_mouvement = True

        # Règles métier spécifiques boule blanche
        if isinstance(boule1, BouleBlanche):
            self._appliquer_regles_collision(boule1, boule2)
        elif isinstance(boule2, BouleBlanche):
            self._appliquer_regles_collision(boule2, boule1)

    def _appliquer_regles_collision(self, boule_blanche, autre_boule):
        """Règles spécifiques gérées dans la classe Partie."""
        pass

    def obtenir_boules_par_couleur(self, couleur):
        """Retourne toutes les boules d'une couleur donnée."""
        return [b for b in self.boules if b.couleur == couleur]

    def obtenir_boules_en_mouvement(self):
        """Retourne toutes les boules actuellement en mouvement."""
        return [b for b in self.boules if b.en_mouvement]

    def toutes_boules_immobiles(self):
        """Vérifie si toutes les boules sont immobiles."""
        return len(self.obtenir_boules_en_mouvement()) == 0

    def retirer_boule(self, boule):
        """Retire une boule du tapis (quand elle est gagnée)."""
        if boule in self.boules and boule != self.boule_blanche:
            self.boules.remove(boule)

    def obtenir_nombre_boules(self):
        """Retourne le nombre total de boules sur le tapis."""
        return len(self.boules)

    def __str__(self):
        return f"Tapis({self.largeur}x{self.hauteur}) avec {self.obtenir_nombre_boules()} boules"
