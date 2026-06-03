"""
Module: vecteur.py
Gestion des vecteurs 2D pour les trajectoires et calculs de collisions.
"""

import math


class Vecteur2D:
    """
    Représente un vecteur 2D avec les opérations mathématiques associées.
    Utilisé pour gérer les positions, vitesses et accélérations des boules.
    """
    
    def __init__(self, x=0, y=0):
        """
        Initialise un vecteur 2D.
        
        Args:
            x (float): Composante horizontale
            y (float): Composante verticale
        """
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, autre):
        """Addition de deux vecteurs."""
        return Vecteur2D(self.x + autre.x, self.y + autre.y)
    
    def __sub__(self, autre):
        """Soustraction de deux vecteurs."""
        return Vecteur2D(self.x - autre.x, self.y - autre.y)
    
    def __mul__(self, scalaire):
        """Multiplication par un scalaire."""
        return Vecteur2D(self.x * scalaire, self.y * scalaire)
    
    def __rmul__(self, scalaire):
        """Multiplication par un scalaire (ordre inversé)."""
        return self.__mul__(scalaire)
    
    def __eq__(self, autre):
        """Vérification d'égalité entre deux vecteurs (avec tolérance)."""
        epsilon = 1e-9
        return abs(self.x - autre.x) < epsilon and abs(self.y - autre.y) < epsilon
    
    def norme(self):
        """Retourne la norme (longueur) du vecteur."""
        return math.sqrt(self.x**2 + self.y**2)
    
    def normalise(self):
        """Retourne un vecteur normalisé (norme = 1)."""
        n = self.norme()
        if n == 0:
            return Vecteur2D(0, 0)
        return Vecteur2D(self.x / n, self.y / n)
    
    def produit_scalaire(self, autre):
        """Calcule le produit scalaire avec un autre vecteur."""
        return self.x * autre.x + self.y * autre.y
    
    def angle_avec(self, autre):
        """
        Retourne l'angle en radians entre deux vecteurs.
        Utilisé pour les calculs de réflexion.
        """
        if self.norme() == 0 or autre.norme() == 0:
            return 0
        cos_angle = self.produit_scalaire(autre) / (self.norme() * autre.norme())
        # Clamp pour éviter les erreurs numériques
        cos_angle = max(-1, min(1, cos_angle))
        return math.acos(cos_angle)
    
    def reflexion(self, normale):
        """
        Calcule la réflexion de ce vecteur par rapport à une normale.
        Utilisé pour les rebonds sur les bordures.
        
        Args:
            normale (Vecteur2D): Vecteur normal à la surface
            
        Returns:
            Vecteur2D: Vecteur réfléchi
        """
        normale_norm = normale.normalise()
        dot = self.produit_scalaire(normale_norm)
        return self - (2 * dot) * normale_norm
    
    def __str__(self):
        """Représentation textuelle du vecteur."""
        return f"Vecteur2D({self.x:.2f}, {self.y:.2f})"
    
    def __repr__(self):
        """Représentation du vecteur pour debug."""
        return self.__str__()
    
    def copie(self):
        """Crée une copie du vecteur."""
        return Vecteur2D(self.x, self.y)
