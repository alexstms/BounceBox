"""
Module: bouncebox_gui.py
Interface graphique complète avec Pygame pour BounceBox.

Classes:
    - Afficheur: Gère le rendu graphique
    - GestionnaireEntrees: Gère l'input souris/clavier
    - ApplicationGUI: Boucle principale du jeu
"""

import math
import pygame
from bouncebox_partie import Partie
from bouncebox_couleurs import *


class Afficheur:
    """
    Gère tout le rendu graphique du jeu.
    Responsable de:
    - Convertir les coordonnées logiques en pixels
    - Dessiner les boules, le tapis, les textes
    """
    
    def __init__(self, largeur_ecran, hauteur_ecran, tapis_largeur=50, tapis_hauteur=50):
        """
        Initialise l'afficheur.

        Le plateau est dessiné avec un rapport d'aspect strictement préservé :
        on utilise un facteur d'échelle UNIQUE (le plus contraint des deux),
        puis on centre la zone de jeu dans la fenêtre. Si le tapis logique est
        carré (50x50), la zone affichée sera également un carré parfait.

        Args:
            largeur_ecran (int): Largeur de la fenêtre en pixels
            hauteur_ecran (int): Hauteur de la fenêtre en pixels
            tapis_largeur (float): Largeur logique du tapis
            tapis_hauteur (float): Hauteur logique du tapis
        """
        self.largeur_ecran = largeur_ecran
        self.hauteur_ecran = hauteur_ecran

        self.tapis_largeur = tapis_largeur
        self.tapis_hauteur = tapis_hauteur

        # Marges minimales pour l'interface (scores en haut, timer en bas)
        marge_top_min = 60
        marge_bottom_min = 60
        marge_lat_min = 20

        # Espace disponible pour le tapis
        espace_largeur = largeur_ecran - 2 * marge_lat_min
        espace_hauteur = hauteur_ecran - marge_top_min - marge_bottom_min

        # Échelle UNIFORME : on prend la plus contraignante des deux dimensions
        # pour préserver le rapport d'aspect du tapis logique
        scale_max_x = espace_largeur / tapis_largeur
        scale_max_y = espace_hauteur / tapis_hauteur
        self.scale = min(scale_max_x, scale_max_y)

        # Dimensions réelles de la zone de jeu (en pixels)
        self.zone_largeur = int(self.scale * tapis_largeur)
        self.zone_hauteur = int(self.scale * tapis_hauteur)

        # Centrage de la zone de jeu dans l'espace disponible
        self.marge_left = (largeur_ecran - self.zone_largeur) // 2
        self.marge_top = marge_top_min + (espace_hauteur - self.zone_hauteur) // 2
        self.marge_right = self.marge_left
        self.marge_bottom = hauteur_ecran - self.marge_top - self.zone_hauteur

        # Conservées pour rétrocompatibilité avec convertir_position / convertir_rayon
        self.scale_x = self.scale
        self.scale_y = self.scale

        # Polices
        self.font_grand = pygame.font.Font(None, 40)
        self.font_moyen = pygame.font.Font(None, 30)
        self.font_petit = pygame.font.Font(None, 20)
    
    def convertir_position(self, vecteur_position):
        """
        Convertit une position Vecteur2D en coordonnées pixels.
        
        Args:
            vecteur_position (Vecteur2D): Position logique
            
        Returns:
            tuple: (x_pixel, y_pixel) pour Pygame
        """
        x = int(vecteur_position.x * self.scale_x + self.marge_left)
        y = int(vecteur_position.y * self.scale_y + self.marge_top)
        return (x, y)
    
    def convertir_rayon(self, rayon):
        """
        Convertit un rayon logique en pixels.
        
        Args:
            rayon (float): Rayon logique
            
        Returns:
            int: Rayon en pixels
        """
        return max(int(rayon * self.scale_x), 2)
    
    def convertir_position_inverse(self, x_pixel, y_pixel):
        """
        Convertit des coordonnées pixels en position logique (inverse).
        Utilisé pour gérer l'input souris.
        
        Args:
            x_pixel (int): Position X en pixels
            y_pixel (int): Position Y en pixels
            
        Returns:
            tuple: (x_logique, y_logique)
        """
        x_logique = (x_pixel - self.marge_left) / self.scale_x
        y_logique = (y_pixel - self.marge_top) / self.scale_y
        return (x_logique, y_logique)
    
    def afficher_fond(self, screen):
        """Affiche le fond et les bordures du tapis."""
        # Fond gris
        screen.fill(FOND_ÉCRAN)
        
        # Zone de tapis (vert billard)
        tapis_rect = pygame.Rect(
            self.marge_left,
            self.marge_top,
            self.zone_largeur,
            self.zone_hauteur
        )
        pygame.draw.rect(screen, VERT_TAPIS, tapis_rect)
        
        # Bordures
        pygame.draw.rect(screen, BRUN_BORDURE, tapis_rect, 5)
    
    def afficher_boule(self, screen, boule):
        """
        Dessine une boule sur l'écran.
        
        Args:
            screen: Surface Pygame
            boule (Boule): Boule à dessiner
        """
        centre_pixel = self.convertir_position(boule.position)
        rayon_pixel = self.convertir_rayon(boule.rayon)
        couleur = couleur_boule(boule.couleur)
        
        # Cercle rempli
        pygame.draw.circle(screen, couleur, centre_pixel, rayon_pixel)
        
        # Contour noir pour plus de clarté
        pygame.draw.circle(screen, NOIR, centre_pixel, rayon_pixel, 2)
    
    def afficher_all_boules(self, screen, tapis):
        """
        Affiche toutes les boules du tapis.
        
        Args:
            screen: Surface Pygame
            tapis (Tapis): Tapis contenant les boules
        """
        for boule in tapis.boules:
            self.afficher_boule(screen, boule)
    
    def afficher_interface(self, screen, partie, force_actuelle=0.0):
        """
        Affiche l'interface (scores, temps, etc).
        
        Args:
            screen: Surface Pygame
            partie (Partie): État de la partie
            force_actuelle (float): Force actuelle du régulateur (0-10)
        """
        j1 = partie.joueur1
        j2 = partie.joueur2
        joueur_actif = partie.joueur_actif
        
        # === SCORES EN HAUT ===
        # Joueur 1 (gauche)
        texte_j1 = self.font_moyen.render(
            f"{j1.nom}: {j1.score}/5",
            True,
            couleur_joueur(j1.couleur)
        )
        screen.blit(texte_j1, (20, 15))
        
        # Joueur 2 (droite)
        texte_j2 = self.font_moyen.render(
            f"{j2.nom}: {j2.score}/5",
            True,
            couleur_joueur(j2.couleur)
        )
        screen.blit(
            texte_j2,
            (self.largeur_ecran - texte_j2.get_width() - 20, 15)
        )
        
        # Joueur actif (centre)
        couleur_active = couleur_joueur(joueur_actif.couleur)
        texte_actif = self.font_petit.render(
            f"Au tour de: {joueur_actif.nom}",
            True,
            couleur_active
        )
        screen.blit(
            texte_actif,
            (self.largeur_ecran // 2 - texte_actif.get_width() // 2, 18)
        )
        
        # === TIMER EN BAS ===
        temps_restant = max(0, int(joueur_actif.temps_restant_tour))
        couleur_temps = VERT_OK if temps_restant > 10 else ORANGE if temps_restant > 3 else ROUGE_ERREUR
        texte_temps = self.font_moyen.render(
            f"Temps : {temps_restant}s",
            True,
            couleur_temps
        )
        screen.blit(
            texte_temps,
            (self.largeur_ecran - texte_temps.get_width() - 20,
             self.hauteur_ecran - texte_temps.get_height() - 15)
        )
        
        # === RÉGULATEUR DE FORCE ===
        if force_actuelle > 0:
            # Position et dimensions du régulateur
            reg_x = 20
            reg_y = self.hauteur_ecran - 50
            reg_largeur = 200
            reg_hauteur = 20
            
            # Fond du régulateur
            pygame.draw.rect(screen, GRIS_FONCÉ, (reg_x, reg_y, reg_largeur, reg_hauteur))
            
            # Barre de remplissage
            pourcentage = min(force_actuelle / 10.0, 1.0)
            remplissage = int(reg_largeur * pourcentage)
            couleur_force = (255, int(100 - pourcentage * 100), 0)  # Rouge→Orange
            pygame.draw.rect(screen, couleur_force, (reg_x, reg_y, remplissage, reg_hauteur))
            
            # Bordure
            pygame.draw.rect(screen, BLANC, (reg_x, reg_y, reg_largeur, reg_hauteur), 2)
            
            # Texte force
            texte_force = self.font_petit.render(
                f"Force: {force_actuelle:.1f}/10",
                True,
                BLANC
            )
            screen.blit(texte_force, (reg_x + 5, reg_y - 20))
        
        # === INSTRUCTIONS ===
        if not partie.coup_lance:
            if force_actuelle == 0:
                texte_info = self.font_petit.render(
                    "Maintenez clic pour augmenter la force, puis relâchez pour lancer",
                    True,
                    CYAN
                )
            else:
                texte_info = self.font_petit.render(
                    "Relâchez pour lancer!",
                    True,
                    JAUNE_TEXTE
                )
            screen.blit(texte_info, (20, self.hauteur_ecran - texte_info.get_height() - 70))
    
    def afficher_fin_partie(self, screen, partie):
        """
        Affiche l'écran de fin de partie avec le gagnant.
        
        Args:
            screen: Surface Pygame
            partie (Partie): État de la partie
        """
        gagnant = partie.obtenir_gagnant()
        temps = partie.obtenir_temps_partie()
        
        # Fond semi-transparent
        fond = pygame.Surface((self.largeur_ecran, self.hauteur_ecran))
        fond.set_alpha(200)
        fond.fill(NOIR)
        screen.blit(fond, (0, 0))
        
        # Texte de victoire
        texte_titre = self.font_grand.render(
            f"{gagnant.nom} a gagné !",
            True,
            OR
        )
        
        # Temps de partie
        texte_temps = self.font_moyen.render(
            f"Temps: {temps:.1f}s",
            True,
            BLANC
        )
        
        # Instructions
        texte_info = self.font_petit.render(
            "Appuyez sur ESPACE pour recommencer, ESC pour quitter",
            True,
            CYAN
        )
        
        # Centrer et afficher
        y_centre = self.hauteur_ecran // 2
        
        screen.blit(
            texte_titre,
            (self.largeur_ecran // 2 - texte_titre.get_width() // 2, y_centre - 100)
        )
        screen.blit(
            texte_temps,
            (self.largeur_ecran // 2 - texte_temps.get_width() // 2, y_centre - 20)
        )
        screen.blit(
            texte_info,
            (self.largeur_ecran // 2 - texte_info.get_width() // 2, y_centre + 60)
        )


class GestionnaireEntrees:
    """
    Gère tous les inputs (souris, clavier) pour le jeu.
    """
    
    def __init__(self, afficheur):
        """
        Args:
            afficheur (Afficheur): L'afficheur pour convertir les coordonnées
        """
        self.afficheur = afficheur
        self.clic_en_cours = False
        self.position_clic_debut = None
        self.temps_clic = 0.0  # Temps que le bouton est maintenu
    
    def gerer_clic_debut(self, x_pixel, y_pixel, partie):
        """
        Gère le début du clic (bouton enfoncé).
        
        Args:
            x_pixel (int): Position X du clic en pixels
            y_pixel (int): Position Y du clic en pixels
            partie (Partie): État de la partie
        """
        if partie.coup_lance:
            return  # Un coup est déjà lancé
        
        self.clic_en_cours = True
        self.position_clic_debut = (x_pixel, y_pixel)
        self.temps_clic = 0.0
    
    def gerer_clic_fin(self, x_pixel, y_pixel, partie):
        """
        Gère la fin du clic (bouton relâché) - Lance le coup!
        
        Args:
            x_pixel (int): Position X du relâchement en pixels
            y_pixel (int): Position Y du relâchement en pixels
            partie (Partie): État de la partie
        """
        if not self.clic_en_cours or self.position_clic_debut is None:
            return
        
        self.clic_en_cours = False
        
        # Si un coup est déjà lancé, ignorer
        if partie.coup_lance:
            return
        
        # Position initiale du clic
        x_debut, y_debut = self.position_clic_debut
        
        # Convertir les coordonnées
        x_depart_logique, y_depart_logique = self.afficheur.convertir_position_inverse(x_debut, y_debut)
        x_cible_logique, y_cible_logique = self.afficheur.convertir_position_inverse(x_pixel, y_pixel)
        
        # Obtenir la boule blanche
        boule = partie.tapis.obtenir_boule_blanche()
        
        # Vecteur de tir (du centre de la boule blanche à la cible)
        dx = x_cible_logique - boule.position.x
        dy = y_cible_logique - boule.position.y
        
        # Angle et distance
        import math
        angle = math.atan2(dy, dx)
        distance = math.sqrt(dx**2 + dy**2)
        
        # Force basée sur fonction polynomiale du second degré: f = a*t²
        # Coefficient a = 120 pour atteindre force max 30 à t=0.5s
        # f(0.5) = 120 * 0.5² = 120 * 0.25 = 30
        a = 120
        force = min(max(a * (self.temps_clic ** 2), 0.5), 30)  # f = 120*t²
        
        print(f"Tir: angle={angle:.2f}, force={force:.2f}, temps_clic={self.temps_clic:.2f}s")
        
        # Lancer le coup
        partie.lancer_coup(angle, force)
        
        self.position_clic_debut = None
        self.temps_clic = 0.0
    
    def mettre_a_jour_clic(self, delta_t):
        """
        Met à jour le temps de clic maintenu.
        À appeler chaque frame.
        
        Args:
            delta_t (float): Temps écoulé en secondes
        """
        if self.clic_en_cours:
            self.temps_clic += delta_t
    
    def obtenir_force_actuelle(self):
        """
        Retourne la force actuelle (pour l'affichage du régulateur).
        Utilise formule polynomiale du second degré: f = a*t²
        
        Returns:
            float: Force entre 0.5 et 30
        """
        if not self.clic_en_cours:
            return 0.0
        a = 120  # Coefficient pour f = 120*t²
        return min(max(a * (self.temps_clic ** 2), 0.5), 30)


class ApplicationGUI:
    """
    Classe principale de l'application.
    Gère la boucle principale du jeu.
    """
    
    def __init__(self, largeur=1000, hauteur=600, fps=60):
        """
        Initialise l'application.
        
        Args:
            largeur (int): Largeur de la fenêtre
            hauteur (int): Hauteur de la fenêtre
            fps (int): Nombre de FPS cible
        """
        pygame.init()
        
        self.largeur = largeur
        self.hauteur = hauteur
        self.fps = fps
        
        # Configuration Pygame
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("BounceBox - Jeu de Billard")
        self.clock = pygame.time.Clock()
        
        # Composants
        self.afficheur = Afficheur(largeur, hauteur)
        self.entrees = GestionnaireEntrees(self.afficheur)
        
        # État du jeu
        self.partie = None
        self.running = True
        self.nouvelle_partie()
    
    def nouvelle_partie(self):
        """Crée et démarre une nouvelle partie."""
        self.partie = Partie("Joueur 1", "Joueur 2")
        self.partie.demarrer()
        print("Nouvelle partie démarrée!")
    
    def gerer_events(self):
        """Traite tous les événements pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    x, y = event.pos
                    self.entrees.gerer_clic_debut(x, y, self.partie)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Relâchement clic gauche
                    x, y = event.pos
                    self.entrees.gerer_clic_fin(x, y, self.partie)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Recommencer
                    self.nouvelle_partie()
                
                elif event.key == pygame.K_ESCAPE:
                    # Quitter
                    self.running = False
                
                elif event.key == pygame.K_r:
                    # Reset (raccourci optionnel)
                    self.nouvelle_partie()
    
    def mettre_a_jour(self):
        """Met à jour la logique du jeu."""
        # Obtenir le delta time en secondes
        delta_t = self.clock.get_time() / 1000.0
        
        # Limiter delta_t pour éviter les sauts énormes
        delta_t = min(delta_t, 0.05)
        
        # Mettre à jour le temps de clic pour le régulateur de force
        self.entrees.mettre_a_jour_clic(delta_t)
        
        # Mettre à jour la partie
        self.partie.mettre_a_jour(delta_t)
        
        # Vérifier la fin
        if self.partie.est_termines():
            print(f"Partie terminée! Gagnant: {self.partie.obtenir_gagnant().nom}")
    
    def afficher(self):
        """Affiche le jeu à l'écran."""
        # Fond et tapis
        self.afficheur.afficher_fond(self.screen)
        
        # Boules
        self.afficheur.afficher_all_boules(self.screen, self.partie.tapis)
        
        # Obtenir la force actuelle pour affichage
        force_actuelle = self.entrees.obtenir_force_actuelle()
        
        # Interface
        self.afficheur.afficher_interface(self.screen, self.partie, force_actuelle)
        
        # Fin de partie
        if self.partie.est_termines():
            self.afficheur.afficher_fin_partie(self.screen, self.partie)
        
        # Mettre à jour l'affichage
        pygame.display.flip()
    
    def lancer(self):
        """Lance la boucle principale."""
        print("╔════════════════════════════════════════════════════════════╗")
        print("║                    BOUNCEBOX - PYGAME                      ║")
        print("║                                                            ║")
        print("║  Commandes:                                                ║")
        print("║  • Cliquez pour lancer la boule blanche                    ║")
        print("║  • ESPACE pour recommencer une partie                      ║")
        print("║  • ESC pour quitter                                        ║")
        print("╚════════════════════════════════════════════════════════════╝\n")
        
        frame_count = 0
        
        while self.running:
            self.gerer_events()
            self.mettre_a_jour()
            self.afficher()
            
            # Contrôler les FPS
            self.clock.tick(self.fps)
            
            # Afficher les FPS toutes les 60 frames
            frame_count += 1
            if frame_count % 60 == 0:
                fps_actual = self.clock.get_fps()
                print(f"FPS: {fps_actual:.1f}")
        
        pygame.quit()
        print("Jeu fermé.")


def main():
    """Point d'entrée principal."""
    app = ApplicationGUI(largeur=1000, hauteur=600, fps=60)
    app.lancer()


if __name__ == "__main__":
    main()
