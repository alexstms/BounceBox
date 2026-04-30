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

    # Dimensions du tapis
    LARGEUR_DEFAUT = 50.0
    HAUTEUR_DEFAUT = 50.0

    def __init__(self, largeur=LARGEUR_DEFAUT, hauteur=HAUTEUR_DEFAUT):
        """
        Initialise un tapis vierge.

        Args:
            largeur (float): Largeur du tapis en unités
            hauteur (float): Hauteur du tapis en unités
        """
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

        # Créer la boule blanche (au centre bas)
        boule_blanche = BouleBlanche(
            Vecteur2D(self.largeur / 2, self.hauteur * 0.8)
        )
        self.boules.append(boule_blanche)
        self.boule_blanche = boule_blanche

        # Créer 9 boules grises
        for _ in range(9):
            pos = self._position_aleatoire()
            self.boules.append(BouleCouleur(pos, Couleur.GRISE))

        # Créer 2 boules bleues (pour Joueur 2)
        for _ in range(2):
            pos = self._position_aleatoire()
            self.boules.append(BouleCouleur(pos, Couleur.BLEUE))

    def _position_aleatoire(self):
        """
        Génère une position aléatoire sur le tapis sans chevauchement.

        Returns:
            Vecteur2D: Position aléatoire sans chevauchement
        """
        margin = 3.0  # Marge depuis les bordures
        # Distance minimale entre CENTRES = 2 * rayon + marge de sécurité
        min_distance = 2 * Boule.RAYON_DEFAUT + 2.0
        max_tentatives = 300

        for _ in range(max_tentatives):
            x = random.uniform(margin, self.largeur - margin)
            y = random.uniform(margin, self.hauteur - margin)
            position = Vecteur2D(x, y)

            # Vérifier qu'il n'y a pas de chevauchement avec une boule existante
            collision = False
            for boule in self.boules:
                distance = (position - boule.position).norme()
                if distance < min_distance:
                    collision = True
                    break

            if not collision:
                return position

        # Fallback : position en grille si l'aléatoire échoue
        return self._position_grille()

    def _position_grille(self):
        """
        Fallback: Génère une position basée sur une grille régulière.

        Returns:
            Vecteur2D: Position selon une grille
        """
        index = len(self.boules)
        espacement_x = self.largeur / 5
        espacement_y = self.hauteur / 4
        margin = 3.0

        col = index % 5
        row = index // 5

        x = margin + (col * espacement_x)
        y = margin + (row * espacement_y)

        # Bruit léger pour casser la régularité
        x += random.uniform(-1, 1)
        y += random.uniform(-1, 1)

        x = max(margin, min(self.largeur - margin, x))
        y = max(margin, min(self.hauteur - margin, y))

        return Vecteur2D(x, y)

    def obtenir_boule_blanche(self):
        """Retourne la boule blanche."""
        return self.boule_blanche

    def mettre_a_jour(self, delta_t=1.0):
        """
        Met à jour l'état du tapis : déplace les boules et gère les collisions.

        Args:
            delta_t (float): Intervalle de temps
        """
        for boule in self.boules:
            boule.deplacer(delta_t)
            boule.rebound_bordure(self.largeur, self.hauteur)

        self._gerer_collisions()

    def _gerer_collisions(self):
        """
        Détecte et gère toutes les collisions entre boules.
        Algorithme naïf en O(n²).
        """
        n = len(self.boules)
        for i in range(n):
            for j in range(i + 1, n):
                boule1 = self.boules[i]
                boule2 = self.boules[j]

                if boule1.en_collision_avec(boule2):
                    self._traiter_collision(boule1, boule2)

    def obtenir_collision_blanche_grise(self):
        """
        Vérifie s'il y a une collision entre la boule blanche et une boule grise.

        Returns:
            BouleCouleur ou None: La première boule grise en collision, ou None
        """
        boule_blanche = self.boule_blanche

        for boule in self.boules:
            if isinstance(boule, BouleCouleur) and boule.couleur == Couleur.GRISE:
                if boule_blanche.en_collision_avec(boule):
                    return boule

        return None

    def _traiter_collision(self, boule1, boule2):
        """
        Traite une collision élastique entre deux boules de masses égales.

        Algorithme :
            1. Calcul de la normale unitaire entre les centres.
            2. Projection de la vitesse relative sur la normale.
            3. Si les boules s'éloignent, on ne fait rien (évite le collage).
            4. Échange des composantes normales (choc élastique, masses égales).
            5. Correction de position pour éviter le chevauchement.

        Args:
            boule1 (Boule): Première boule
            boule2 (Boule): Deuxième boule
        """
        # 1. Vecteur normal unitaire (de boule1 vers boule2)
        delta = boule2.position - boule1.position
        distance = delta.norme()

        # Sécurité : centres confondus → on évite la division par zéro
        if distance == 0:
            return

        normale = delta * (1.0 / distance)

        # 2. Vitesse relative et projection sur la normale
        vitesse_relative = boule1.vitesse - boule2.vitesse
        v_rel_normale = vitesse_relative.produit_scalaire(normale)

        # 3. Si les boules s'éloignent déjà, ne rien faire
        if v_rel_normale <= 0:
            return

        # 4. Échange des composantes normales
        impulsion = normale * v_rel_normale
        boule1.vitesse = boule1.vitesse - impulsion
        boule2.vitesse = boule2.vitesse + impulsion

        # Réveiller les boules touchées
        if boule1.vitesse.norme() > Boule.SEUIL_MOUVEMENT:
            boule1.en_mouvement = True
        if boule2.vitesse.norme() > Boule.SEUIL_MOUVEMENT:
            boule2.en_mouvement = True

        # 5. Correction de position pour éviter le chevauchement
        chevauchement = (boule1.rayon + boule2.rayon) - distance
        if chevauchement > 0:
            correction = normale * (chevauchement / 2)
            boule1.position = boule1.position - correction
            boule2.position = boule2.position + correction

        # Comportement spécifique aux collisions impliquant la boule blanche
        if isinstance(boule1, BouleBlanche):
            self._appliquer_regles_collision(boule1, boule2)
        elif isinstance(boule2, BouleBlanche):
            self._appliquer_regles_collision(boule2, boule1)

    def _appliquer_regles_collision(self, boule_blanche, autre_boule):
        """
        Applique les règles du jeu lors d'une collision avec la boule blanche.
        Les règles spécifiques (changement de couleur, score) sont gérées
        dans la classe Partie.

        Args:
            boule_blanche (BouleBlanche): La boule blanche
            autre_boule (Boule): L'autre boule
        """
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
        """
        Retire une boule du tapis (quand elle est gagnée).

        Args:
            boule (Boule): La boule à retirer
        """
        if boule in self.boules and boule != self.boule_blanche:
            self.boules.remove(boule)

    def obtenir_nombre_boules(self):
        """Retourne le nombre total de boules sur le tapis."""
        return len(self.boules)

    def __str__(self):
        """Représentation textuelle du tapis."""
        return f"Tapis({self.largeur}x{self.hauteur}) avec {self.obtenir_nombre_boules()} boules"
