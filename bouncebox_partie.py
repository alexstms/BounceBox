"""
Module: partie.py
Gestion de la partie, des joueurs et de l'état du jeu.
Coordonne les interactions entre les joueurs, le tapis et les règles.
"""

from enum import Enum
from datetime import datetime
from bouncebox_boules import Couleur
from bouncebox_tapis import Tapis


class EtatPartie(Enum):
    """Énumération des états possibles de la partie."""
    DEBUT = "debut"
    EN_COURS = "en_cours"
    FIN = "fin"
    PAUSED = "paused"


class Joueur:
    """
    Représente un joueur dans la partie.
    Chaque joueur a une couleur et accumulé des points.
    """
    
    POINTS_VICTOIRE = 5  # Nombre de boules à gagner pour gagner
    TEMPS_TOUR = 45  # Temps limite en secondes
    
    def __init__(self, nom, couleur):
        """
        Initialise un joueur.
        
        Args:
            nom (str): Nom du joueur
            couleur (Couleur): Couleur attribuée au joueur (ROUGE ou BLEUE)
        """
        self.nom = nom
        self.couleur = couleur
        self.score = 0
        self.temps_restant_tour = self.TEMPS_TOUR
    
    def incrementer_score(self):
        """Incrémente le score du joueur (une boule gagnée)."""
        self.score += 1
    
    def a_gagne(self):
        """
        Vérifie si ce joueur a gagné la partie.
        
        Returns:
            bool: True si le score atteint POINTS_VICTOIRE
        """
        return self.score >= self.POINTS_VICTOIRE
    
    def reinitialiser_temps_tour(self):
        """Réinitialise le temps restant pour ce tour."""
        self.temps_restant_tour = self.TEMPS_TOUR
    
    def decrementer_temps(self, delta_t=1):
        """
        Décrémente le temps restant du tour.
        
        Args:
            delta_t (float): Temps écoulé en secondes
        """
        self.temps_restant_tour -= delta_t
        if self.temps_restant_tour < 0:
            self.temps_restant_tour = 0
    
    def temps_ecoule(self):
        """
        Vérifie si le temps du tour est écoulé.
        
        Returns:
            bool: True si le temps restant <= 0
        """
        return self.temps_restant_tour <= 0
    
    def __str__(self):
        """Représentation textuelle du joueur."""
        return f"{self.nom} ({self.couleur.value}) - Score: {self.score}"
    
    def __repr__(self):
        """Représentation pour debug."""
        return self.__str__()


class Partie:
    """
    Classe principale gérant une partie de BounceBox.
    Coordonne les joueurs, le tapis et les règles du jeu.
    """
    
    def __init__(self, nom_joueur1="Joueur 1", nom_joueur2="Joueur 2"):
        """
        Initialise une nouvelle partie.
        
        Args:
            nom_joueur1 (str): Nom du premier joueur (couleur ROUGE)
            nom_joueur2 (str): Nom du deuxième joueur (couleur BLEUE)
        """
        self.joueur1 = Joueur(nom_joueur1, Couleur.ROUGE)
        self.joueur2 = Joueur(nom_joueur2, Couleur.BLEUE)
        self.joueurs = [self.joueur1, self.joueur2]
        
        self.tapis = Tapis()
        self.etat = EtatPartie.DEBUT
        self.joueur_actif = self.joueur1  # Le joueur rouge commence
        self.joueur_inactif = self.joueur2
        self.coup_lance = False  # Flag pour savoir si un coup a été lancé ce tour
        self.dernier_coup_temps = None  # Timestamp du dernier coup
        self.historique_coups = []  # Liste des coups joués
        self.debut_partie = None  # Timestamp du début
    
    def demarrer(self):
        """Démarre une nouvelle partie."""
        self.tapis.initialiser_partie()
        self.etat = EtatPartie.EN_COURS
        self.debut_partie = datetime.now()
        self.joueur_actif.reinitialiser_temps_tour()
        self.joueur_inactif.reinitialiser_temps_tour()
    
    def obtenir_joueur_actif(self):
        """
        Retourne le joueur actuellement actif (qui joue).
        
        Returns:
            Joueur: Le joueur actif
        """
        return self.joueur_actif
    
    def obtenir_joueur_inactif(self):
        """
        Retourne le joueur inactif.
        
        Returns:
            Joueur: Le joueur inactif
        """
        return self.joueur_inactif
    
    def changer_joueur_actif(self):
        """Change le joueur actif (bascule entre les deux joueurs)."""
        self.joueur_actif, self.joueur_inactif = self.joueur_inactif, self.joueur_actif
        self.joueur_actif.reinitialiser_temps_tour()
        self.coup_lance = False
        # ⚠️ NE PAS réinitialiser la boule blanche - elle reste où elle s'est arrêtée!
    
    def lancer_coup(self, angle, force):
        """
        Lance la boule blanche avec l'angle et la force spécifiés.
        
        Args:
            angle (float): Angle en radians (0 = droite, π/2 = haut)
            force (float): Force du tir (0 à 1 généralement)
            
        Returns:
            bool: True si le coup a été lancé avec succès
        """
        import math
        from bouncebox_vecteur import Vecteur2D
        
        if self.coup_lance:
            return False  # Un seul coup par tour
        
        boule_blanche = self.tapis.obtenir_boule_blanche()
        
        # Créer le vecteur de vitesse
        vitesse = Vecteur2D(
            force * math.cos(angle),
            force * math.sin(angle)
        )
        
        boule_blanche.appliquer_force(vitesse)
        self.coup_lance = True
        self.dernier_coup_temps = datetime.now()
        self.historique_coups.append({
            'joueur': self.joueur_actif.nom,
            'angle': angle,
            'force': force,
            'temps': self.dernier_coup_temps
        })
        
        return True
    
    def mettre_a_jour(self, delta_t=0.016):
        """
        Met à jour l'état de la partie (physique, temps, etc).
        À appeler régulièrement (ex: 60 FPS).
        
        Args:
            delta_t (float): Intervalle de temps en secondes
        """
        if self.etat != EtatPartie.EN_COURS:
            return
        
        # Mettre à jour le tapis
        self.tapis.mettre_a_jour(delta_t)
        
        # ✨ GESTION DES COLLISIONS: Boule blanche + Boules colorées
        if self.coup_lance:
            boule_blanche = self.tapis.obtenir_boule_blanche()
            
            # Vérifier collision avec chaque boule
            for boule in list(self.tapis.boules):
                if boule == boule_blanche:
                    continue
                
                if boule_blanche.en_collision_avec(boule):
                    # ===== COLLISION DÉTECTÉE =====
                    
                    from bouncebox_boules import BouleCouleur, Couleur
                    
                    if isinstance(boule, BouleCouleur):
                        # JOUEUR 1 (ROUGE) frappe:
                        if self.joueur_actif.couleur == Couleur.ROUGE:
                            if boule.couleur == Couleur.ROUGE:
                                # CAS: Touche une boule ROUGE (sa couleur)
                                self.joueur_actif.incrementer_score()
                                self.tapis.retirer_boule(boule)
                                print(f"🎯 POINT! Boule rouge capturée par {self.joueur_actif.nom}")
                                print(f"📊 Score {self.joueur_actif.nom}: {self.joueur_actif.score}/5")
                            
                            elif boule.couleur == Couleur.GRISE:
                                # CAS: Touche une boule GRISE
                                boule.changer_couleur(Couleur.ROUGE)
                                print(f"💫 Boule grise → rouge (J1 l'a touchée, pas de point)")
                            
                            elif boule.couleur == Couleur.BLEUE:
                                # CAS: Touche une boule BLEUE (couleur adverse)
                                boule.changer_couleur(Couleur.GRISE)
                                print(f"💫 Boule bleue → grise (J1 rouge l'a touchée)")
                        
                        # JOUEUR 2 (BLEU) frappe:
                        elif self.joueur_actif.couleur == Couleur.BLEUE:
                            if boule.couleur == Couleur.BLEUE:
                                # CAS: Touche une boule BLEUE (sa couleur)
                                self.joueur_actif.incrementer_score()
                                self.tapis.retirer_boule(boule)
                                print(f"🎯 POINT! Boule bleue capturée par {self.joueur_actif.nom}")
                                print(f"📊 Score {self.joueur_actif.nom}: {self.joueur_actif.score}/5")
                            
                            elif boule.couleur == Couleur.GRISE:
                                # CAS: Touche une boule GRISE
                                boule.changer_couleur(Couleur.BLEUE)
                                print(f"💫 Boule grise → bleue (J2 l'a touchée, pas de point)")
                            
                            elif boule.couleur == Couleur.ROUGE:
                                # CAS: Touche une boule ROUGE (couleur adverse)
                                boule.changer_couleur(Couleur.GRISE)
                                print(f"💫 Boule rouge → grise (J2 bleu l'a touchée)")
        
        # Vérifier la fin du tour (tous les boules immobiles)
        if self.coup_lance and self.tapis.toutes_boules_immobiles():
            # Arrêter le timer et passer au joueur suivant
            self._evaluer_tour()
            return  # Ne pas décrémenter le timer si le tour est fini
        
        # Décrémenter le temps du joueur actif SEULEMENT si un coup est lancé
        if self.coup_lance:
            self.joueur_actif.decrementer_temps(delta_t)
            
            # Vérifier si le joueur a dépassé le temps limite
            if self.joueur_actif.temps_ecoule():
                self.changer_joueur_actif()
    
    def _evaluer_tour(self):
        """
        Évalue le tour qui vient de se terminer.
        Change de joueur automatiquement quand les boules s'arrêtent.
        """
        # Passer au joueur suivant
        self.changer_joueur_actif()
        print(f"Tour du {self.joueur_actif.nom} ({self.joueur_actif.couleur.value})")
    
    def est_termines(self):
        """
        Vérifie si la partie est terminée.
        
        Returns:
            bool: True si un joueur a atteint 5 points
        """
        if self.joueur1.a_gagne():
            self.etat = EtatPartie.FIN
            return True
        if self.joueur2.a_gagne():
            self.etat = EtatPartie.FIN
            return True
        return False
    
    def obtenir_gagnant(self):
        """
        Retourne le gagnant de la partie.
        
        Returns:
            Joueur: Le joueur gagnant, ou None si la partie n'est pas finie
        """
        if self.joueur1.a_gagne():
            return self.joueur1
        if self.joueur2.a_gagne():
            return self.joueur2
        return None
    
    def obtenir_temps_partie(self):
        """
        Calcule le temps écoulé depuis le début de la partie.
        
        Returns:
            float: Temps en secondes, ou None si pas commencée
        """
        if self.debut_partie is None:
            return None
        return (datetime.now() - self.debut_partie).total_seconds()
    
    def __str__(self):
        """Représentation textuelle de la partie."""
        return (f"Partie - {self.joueur1.nom} vs {self.joueur2.nom} - "
                f"État: {self.etat.value}")
    
    def __repr__(self):
        """Représentation pour debug."""
        return self.__str__()
