"""
Module: tapis.py
Gestion du tapis de jeu, des boules et des collisions physiques.
"""

import random
from bouncebox_vecteur import Vecteur2D
from bouncebox_boules import (
    Boule, BouleBlanche, BouleGrise, BouleRouge, BouleBleue, Couleur
)


class Tapis:
    """
    Représente le tapis de jeu avec ses boules et ses bordures.
    Gère la physique, les déplacements et les collisions.
    """
    
    # Dimensions du tapis
    LARGEUR_DEFAUT = 100.0
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
            self.boules.append(BouleGrise(pos))
        
        # Créer 2 boules bleues
        for _ in range(2):
            pos = self._position_aleatoire()
            self.boules.append(BouleBleue(pos))
    
    def _position_aleatoire(self):
        """
        Génère une position aléatoire sur le tapis sans chevauchement.
        
        Distance minimale entre boules: 4.5 (2 rayons + marge de sécurité)
        
        Returns:
            Vecteur2D: Position aléatoire sans chevauchement
        """
        margin = 3.0  # Marge depuis les bordures
        min_distance = 4.5  # Distance minimale entre CENTRES (rayon 1.0 + rayon 1.0 + marge 2.5)
        max_tentatives = 300  # Nombre de tentatives augmenté
        
        for _ in range(max_tentatives):
            x = random.uniform(margin, self.largeur - margin)
            y = random.uniform(margin, self.hauteur - margin)
            position = Vecteur2D(x, y)
            
            # Vérifier qu'il n'y a pas de chevauchement avec aucune boule existante
            collision = False
            for boule in self.boules:
                distance = (position - boule.position).norme()
                # Si la distance est inférieure au minimum, il y a chevauchement potentiel
                if distance < min_distance:
                    collision = True
                    break
            
            # Si pas de collision, on retourne cette position
            if not collision:
                return position
        
        # Fallback: si les tentatives aléatoires échouent, utiliser une grille
        # Cela garantit qu'on trouvera toujours une position valide
        return self._position_grille()
    
    def _position_grille(self):
        """
        Fallback: Génère une position basée sur une grille régulière.
        Utilisé quand les tentatives aléatoires échouent.
        
        Returns:
            Vecteur2D: Position selon une grille
        """
        # Utiliser le nombre actuel de boules pour créer une position en grille
        index = len(self.boules)
        
        # Paramètres de la grille
        espacement_x = self.largeur / 5
        espacement_y = self.hauteur / 4
        margin = 3.0
        
        # Calculer la position dans la grille
        col = index % 5
        row = index // 5
        
        x = margin + (col * espacement_x)
        y = margin + (row * espacement_y)
        
        # Ajouter un peu de bruit pour ne pas que ce soit trop régulier
        x += random.uniform(-1, 1)
        y += random.uniform(-1, 1)
        
        # S'assurer qu'on est dans les limites
        x = max(margin, min(self.largeur - margin, x))
        y = max(margin, min(self.hauteur - margin, y))
        
        return Vecteur2D(x, y)
    
    def obtenir_boule_blanche(self):
        """
        Retourne la boule blanche.
        
        Returns:
            BouleBlanche: La boule blanche
        """
        return self.boule_blanche
    
    def mettre_a_jour(self, delta_t=1.0):
        """
        Met à jour l'état du tapis : déplace les boules et gère les collisions.
        
        Args:
            delta_t (float): Intervalle de temps
        """
        # Déplacer toutes les boules
        for boule in self.boules:
            boule.deplacer(delta_t)
            boule.rebound_bordure(self.largeur, self.hauteur)
        
        # Détecter et traiter les collisions
        self._gerer_collisions()
    
    def _gerer_collisions(self):
        """
        Détecte et gère toutes les collisions entre boules.
        Utilise un algorithme simple O(n²).
        """
        n = len(self.boules)
        for i in range(n):
            for j in range(i + 1, n):
                boule1 = self.boules[i]
                boule2 = self.boules[j]
                
                if boule1.en_collision_avec(boule2):
                    self._traiter_collision(boule1, boule2)
    
    def _traiter_collision(self, boule1, boule2):
        """
        Traite une collision entre deux boules.
        Gère l'échange de vélocité et les changements de couleur.
        
        Args:
            boule1 (Boule): Première boule
            boule2 (Boule): Deuxième boule
        """
        # Échange de vélocité (collision élastique simplifiée)
        boule1.vitesse, boule2.vitesse = boule2.vitesse, boule1.vitesse
        
        # Déterminer le comportement selon les types de boules
        if isinstance(boule1, BouleBlanche):
            self._appliquer_regles_collision(boule1, boule2)
        elif isinstance(boule2, BouleBlanche):
            self._appliquer_regles_collision(boule2, boule1)
    
    def _appliquer_regles_collision(self, boule_blanche, autre_boule):
        """
        Applique les règles du jeu lors d'une collision avec la boule blanche.
        
        Args:
            boule_blanche (BouleBlanche): La boule blanche
            autre_boule (Boule): L'autre boule
        """
        # Les règles spécifiques seront appliquées au niveau du gestionnaire de partie
        pass
    
    def obtenir_boules_par_couleur(self, couleur):
        """
        Retourne toutes les boules d'une couleur donnée.
        
        Args:
            couleur (Couleur): La couleur à filtrer
            
        Returns:
            list: Liste des boules de cette couleur
        """
        return [b for b in self.boules if b.couleur == couleur]
    
    def obtenir_boules_en_mouvement(self):
        """
        Retourne toutes les boules actuellement en mouvement.
        
        Returns:
            list: Liste des boules en mouvement
        """
        return [b for b in self.boules if b.en_mouvement]
    
    def toutes_boules_immobiles(self):
        """
        Vérifie si toutes les boules sont immobiles.
        
        Returns:
            bool: True si aucune boule ne bouge
        """
        return len(self.obtenir_boules_en_mouvement()) == 0
    
    def retirer_boule(self, boule):
        """
        Retire une boule du tapis (quand elle est gagnée).
        
        Args:
            boule (Boule): La boule à retirer
        """
        if boule in self.boules and boule != self.boule_blanche:
            self.boules.remove(boule)
    
    def reinitialiser_boule_blanche(self):
        """Remet la boule blanche à sa position initiale."""
        if self.boule_blanche:
            self.boule_blanche.position = Vecteur2D(self.largeur / 2, self.hauteur * 0.8)
            self.boule_blanche.vitesse = Vecteur2D(0, 0)
            self.boule_blanche.en_mouvement = False
    
    def obtenir_nombre_boules(self):
        """Retourne le nombre total de boules sur le tapis."""
        return len(self.boules)
    
    def __str__(self):
        """Représentation textuelle du tapis."""
        return f"Tapis({self.largeur}x{self.hauteur}) avec {self.obtenir_nombre_boules()} boules"
