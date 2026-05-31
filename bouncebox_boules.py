"""
Module: boules.py
Définition des classes de boules avec leurs propriétés et comportements.
Utilise l'héritage pour différencier les types de boules.
"""

from abc import ABC
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
    RESISTANCE = 0.99   # Coefficient de friction par frame (0.99^60 ≈ 0.547, soit ~45% de perte/sec à 60 FPS)
    GRAVITE = 0.0       # Pas de gravité dans ce jeu
    SEUIL_MOUVEMENT = 0.3  # Vitesse en-dessous de laquelle on considère la boule arrêtée
    
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

        Args:
            largeur_tapis (float): Largeur du tapis
            hauteur_tapis (float): Hauteur du tapis
        Returns:
            bool: True si un rebond a eu lieu ce frame
        """
        rebond = False

        # Rebond sur les bordures horizontales
        if self.position.x - self.rayon < 0:
            self.position.x = self.rayon
            self.vitesse.x = abs(self.vitesse.x)
            rebond = True
        elif self.position.x + self.rayon > largeur_tapis:
            self.position.x = largeur_tapis - self.rayon
            self.vitesse.x = -abs(self.vitesse.x)
            rebond = True

        # Rebond sur les bordures verticales
        if self.position.y - self.rayon < 0:
            self.position.y = self.rayon
            self.vitesse.y = abs(self.vitesse.y)
            rebond = True
        elif self.position.y + self.rayon > hauteur_tapis:
            self.position.y = hauteur_tapis - self.rayon
            self.vitesse.y = -abs(self.vitesse.y)
            rebond = True

        return rebond
    
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
    
    def __repr__(self):
        """Représentation texte de la boule colorée."""
        return f"BouleCouleur({self.couleur.value}, pos={self.position})"

