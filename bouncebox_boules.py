"""
Module: boules.py
Définition des classes de boules avec leurs propriétés et comportements.
Utilise l'héritage pour différencier les types de boules.
"""

from abc import ABC, abstractmethod
from enum import Enum
from bouncebox_vecteur import Vecteur2D


class Couleur(Enum):
    """Énumération des couleurs possibles des boules."""
    BLANCHE = "blanche"
    GRISE = "grise"
    ROUGE = "rouge"
    BLEUE = "bleue"


class Boule(ABC):
    """
    Classe abstraite représentant une boule du jeu.
    Toutes les boules partagent position, vélocité et rayon.
    """
    
    # Constantes physiques
    RAYON_DEFAUT = 1.5
    RESISTANCE = 0.995  # Coefficient de friction (0 < r < 1)
    GRAVITE = 0.0  # Pas de gravité dans ce jeu
    SEUIL_MOUVEMENT = 0.1  # Vitesse minimale avant arrêt
    
    def __init__(self, position, couleur, rayon=RAYON_DEFAUT):
        """
        Initialise une boule.
        
        Args:
            position (Vecteur2D): Position initiale de la boule
            couleur (Couleur): Couleur de la boule
            rayon (float): Rayon de la boule
        """
        self.position = position
        self.couleur = couleur
        self.rayon = rayon
        self.vitesse = Vecteur2D(0, 0)  # Initialement immobile
        self.en_mouvement = False
    
    @abstractmethod
    def reagir_collision(self, autre_boule):
        """
        Défini le comportement lors d'une collision.
        Chaque type de boule a un comportement différent.
        
        Args:
            autre_boule (Boule): La boule avec laquelle cette boule entre en collision
        """
        pass
    
    def deplacer(self, delta_t=1.0):
        """
        Déplace la boule en fonction de sa vitesse actuelle.
        Applique la résistance.
        
        Args:
            delta_t (float): Intervalle de temps pour le déplacement
        """
        # Mise à jour de la position
        self.position = self.position + self.vitesse * delta_t
        
        # Application de la résistance
        self.vitesse = self.vitesse * self.RESISTANCE
        
        # Arrêt si la vitesse est trop faible
        if self.vitesse.norme() < self.SEUIL_MOUVEMENT:
            self.vitesse = Vecteur2D(0, 0)
            self.en_mouvement = False
        else:
            self.en_mouvement = True
    
    def appliquer_force(self, force):
        """
        Applique une force à la boule (modifie sa vitesse).
        
        Args:
            force (Vecteur2D): Vecteur de force (vitesse initiale)
        """
        self.vitesse = force
        self.en_mouvement = True
    
    def distance_avec(self, autre_boule):
        """
        Calcule la distance entre cette boule et une autre.
        
        Args:
            autre_boule (Boule): L'autre boule
            
        Returns:
            float: Distance entre les centres des boules
        """
        return (self.position - autre_boule.position).norme()
    
    def en_collision_avec(self, autre_boule):
        """
        Vérifie s'il y a collision avec une autre boule.
        
        Args:
            autre_boule (Boule): L'autre boule
            
        Returns:
            bool: True si les boules se chevauchent
        """
        distance = self.distance_avec(autre_boule)
        return distance < (self.rayon + autre_boule.rayon)
    
    def rebound_bordure(self, largeur_tapis, hauteur_tapis):
        """
        Gère le rebond de la boule sur les bordures du tapis.
        Rebond symétrique avec application de résistance.
        
        Args:
            largeur_tapis (float): Largeur du tapis
            hauteur_tapis (float): Hauteur du tapis
        """
        # Rebond sur les bordures horizontales
        if self.position.x - self.rayon < 0:
            self.position.x = self.rayon
            self.vitesse.x = abs(self.vitesse.x) * self.RESISTANCE
        elif self.position.x + self.rayon > largeur_tapis:
            self.position.x = largeur_tapis - self.rayon
            self.vitesse.x = -abs(self.vitesse.x) * self.RESISTANCE
        
        # Rebond sur les bordures verticales
        if self.position.y - self.rayon < 0:
            self.position.y = self.rayon
            self.vitesse.y = abs(self.vitesse.y) * self.RESISTANCE
        elif self.position.y + self.rayon > hauteur_tapis:
            self.position.y = hauteur_tapis - self.rayon
            self.vitesse.y = -abs(self.vitesse.y) * self.RESISTANCE
    
    def __str__(self):
        """Représentation textuelle de la boule."""
        return f"{self.__class__.__name__}({self.couleur.value} à {self.position})"
    
    def __repr__(self):
        """Représentation pour debug."""
        return self.__str__()


class BouleBlanche(Boule):
    """
    La boule blanche lancée par les joueurs.
    C'est la seule boule qui se déplace à l'initiative d'un joueur.
    """
    
    def __init__(self, position):
        """Initialise la boule blanche."""
        super().__init__(position, Couleur.BLANCHE)
    
    def reagir_collision(self, autre_boule):
        """La boule blanche ne change pas en collision (les autres changent)."""
        pass


class BouleCouleur(Boule):
    """
    Classe pour les boules colorées (grises, rouges, bleues).
    Une seule classe qui peut prendre n'importe quelle couleur.
    Peut changer de couleur lors de collisions.
    """
    
    def __init__(self, position, couleur):
        """
        Initialise une boule colorée.
        
        Args:
            position (Vecteur2D): Position initiale
            couleur (Couleur): Couleur initiale de la boule (GRISE, ROUGE ou BLEUE)
        """
        super().__init__(position, couleur)
    
    def changer_couleur(self, nouvelle_couleur):
        """
        Change la couleur de la boule.
        
        Args:
            nouvelle_couleur (Couleur): La nouvelle couleur
        """
        self.couleur = nouvelle_couleur
    
    def reagir_collision(self, autre_boule):
        """
        Comportement lors d'une collision.
        Les boules colorées ne font rien spécial (la logique est dans Partie).
        
        Args:
            autre_boule (Boule): L'autre boule en collision
        """
        pass
    
    def __repr__(self):
        """Représentation texte de la boule colorée."""
        return f"BouleCouleur({self.couleur.value}, pos={self.position})"
