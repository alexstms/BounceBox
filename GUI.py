"""
Module: GUI.py
Interface graphique complète avec Pygame pour BounceBox.

Classes:
    - Afficheur: Gère le rendu graphique
    - GestionnaireEntrees: Gère l'input souris/clavier
    - ApplicationGUI: Boucle principale du jeu
"""

import math
import array
import time
import pygame
from bouncebox_partie import Partie
from bouncebox_couleurs import *
from bouncebox_db import initialiser_base


def _generer_son(frequence, duree, volume=0.4, decroissance=True):
    """
    Génère un son synthétique (sinusoïde) sans fichier externe.

    Args:
        frequence (float): Fréquence en Hz
        duree (float): Durée en secondes
        volume (float): Volume entre 0.0 et 1.0
        decroissance (bool): Fondu sortant pour adoucir la fin du son
    Returns:
        pygame.mixer.Sound
    """
    sample_rate = 44100
    n_samples = int(sample_rate * duree)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        val = math.sin(2 * math.pi * frequence * t)
        if decroissance:
            val *= 1.0 - (i / n_samples)  # fondu sortant
        buf[i] = int(val * volume * 32767)
    son = pygame.mixer.Sound(buffer=buf)
    return son


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
        self.font_titre  = pygame.font.Font(None, 90)
        self.font_grand  = pygame.font.Font(None, 40)
        self.font_moyen  = pygame.font.Font(None, 30)
        self.font_petit  = pygame.font.Font(None, 20)

    # ------------------------------------------------------------------
    # Helpers menus
    # ------------------------------------------------------------------

    def dessiner_bouton(self, screen, texte, rect, survol=False):
        """
        Dessine un bouton rectangulaire centré.

        Args:
            screen: Surface Pygame
            texte (str): Texte affiché dans le bouton
            rect (pygame.Rect): Position et taille du bouton
            survol (bool): True si la souris est dessus (éclaire le bouton)
        Returns:
            pygame.Rect: le même rect (pour tests de clic)
        """
        couleur_fond    = (60, 60, 80) if not survol else (90, 90, 120)
        couleur_bordure = OR if survol else GRIS_CLAIR
        pygame.draw.rect(screen, couleur_fond,    rect, border_radius=10)
        pygame.draw.rect(screen, couleur_bordure, rect, 2, border_radius=10)
        surf = self.font_grand.render(texte, True, BLANC)
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))
        return rect

    def dessiner_champ_texte(self, screen, label, valeur, rect, actif=False, curseur=True):
        """
        Dessine un champ de saisie de texte.

        Args:
            screen: Surface Pygame
            label (str): Étiquette au-dessus du champ
            valeur (str): Texte actuellement saisi
            rect (pygame.Rect): Zone du champ
            actif (bool): True si le champ a le focus
            curseur (bool): Affiche le curseur clignotant si actif
        """
        # Étiquette
        surf_label = self.font_petit.render(label, True, GRIS_CLAIR)
        screen.blit(surf_label, (rect.x, rect.y - 22))

        # Fond du champ
        couleur_bordure = OR if actif else GRIS_CLAIR
        pygame.draw.rect(screen, GRIS_FONCÉ, rect, border_radius=6)
        pygame.draw.rect(screen, couleur_bordure, rect, 2, border_radius=6)

        # Texte saisi + curseur clignotant
        affichage = valeur
        if actif and curseur and int(time.time() * 2) % 2 == 0:
            affichage += '|'
        surf_texte = self.font_moyen.render(affichage, True, BLANC)
        screen.blit(surf_texte, (rect.x + 10, rect.centery - surf_texte.get_height() // 2))

    # ------------------------------------------------------------------
    # Écrans menus
    # ------------------------------------------------------------------

    def afficher_ecran_titre(self, screen, largeur, hauteur):
        """
        Affiche l'écran titre : fond uni + nom du jeu + bouton Jouer.

        Returns:
            pygame.Rect: rect du bouton (pour test de clic)
        """
        screen.fill(FOND_ÉCRAN)

        # Titre
        surf_titre = self.font_titre.render("BounceBox", True, OR)
        screen.blit(surf_titre, (largeur // 2 - surf_titre.get_width() // 2,
                                 hauteur // 2 - 140))

        # Sous-titre
        surf_sous = self.font_moyen.render("Jeu de billard à deux joueurs", True, GRIS_CLAIR)
        screen.blit(surf_sous, (largeur // 2 - surf_sous.get_width() // 2,
                                hauteur // 2 - 50))

        # Bouton
        btn = pygame.Rect(largeur // 2 - 120, hauteur // 2 + 20, 240, 55)
        souris = pygame.mouse.get_pos()
        return self.dessiner_bouton(screen, "▶  Jouer", btn, survol=btn.collidepoint(souris))

    def afficher_ecran_noms(self, screen, largeur, hauteur, noms, champ_actif, sauvegarder=False):
        """
        Affiche l'écran de saisie des noms de joueurs.

        Args:
            noms (list[str]): [nom_j1, nom_j2]
            champ_actif (int): 0 ou 1 selon le champ sélectionné
            sauvegarder (bool): état de la case à cocher sauvegarde
        Returns:
            tuple: (rect_champ_j1, rect_champ_j2, rect_bouton_lancer, rect_checkbox)
        """
        screen.fill(FOND_ÉCRAN)

        # Titre
        surf_titre = self.font_grand.render("Entrez les noms des joueurs", True, OR)
        screen.blit(surf_titre, (largeur // 2 - surf_titre.get_width() // 2, 80))

        cx = largeur // 2
        # Champ Joueur 1
        rect_j1 = pygame.Rect(cx - 160, 200, 320, 44)
        self.dessiner_champ_texte(screen, "Joueur 1 (Rouge)", noms[0], rect_j1,
                                  actif=(champ_actif == 0))

        # Champ Joueur 2
        rect_j2 = pygame.Rect(cx - 160, 310, 320, 44)
        self.dessiner_champ_texte(screen, "Joueur 2 (Bleu)", noms[1], rect_j2,
                                  actif=(champ_actif == 1))

        # Case à cocher — Sauvegarder la partie
        case_taille = 22
        rect_checkbox = pygame.Rect(cx - 160, 385, case_taille, case_taille)
        pygame.draw.rect(screen, GRIS_FONCÉ,  rect_checkbox, border_radius=4)
        pygame.draw.rect(screen, GRIS_CLAIR,  rect_checkbox, 2, border_radius=4)
        if sauvegarder:
            # Coche (✓) dessinée avec deux lignes
            pygame.draw.line(screen, VERT_OK,
                             (rect_checkbox.x + 4,  rect_checkbox.centery),
                             (rect_checkbox.centerx - 1, rect_checkbox.bottom - 5), 2)
            pygame.draw.line(screen, VERT_OK,
                             (rect_checkbox.centerx - 1, rect_checkbox.bottom - 5),
                             (rect_checkbox.right - 4, rect_checkbox.y + 5), 2)
        surf_case = self.font_petit.render("Sauvegarder le résultat de la partie", True,
                                           VERT_OK if sauvegarder else GRIS_CLAIR)
        screen.blit(surf_case, (rect_checkbox.right + 10,
                                rect_checkbox.centery - surf_case.get_height() // 2))

        # Bouton Lancer
        btn = pygame.Rect(cx - 120, 430, 240, 55)
        souris = pygame.mouse.get_pos()
        self.dessiner_bouton(screen, "Lancer la partie", btn,
                             survol=btn.collidepoint(souris))

        return rect_j1, rect_j2, btn, rect_checkbox
    
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
            force_actuelle (float): Force actuelle du régulateur (0-60)
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
            pourcentage = min(force_actuelle / 60.0, 1.0)
            remplissage = int(reg_largeur * pourcentage)
            couleur_force = (255, int(100 - pourcentage * 100), 0)  # Rouge→Orange
            pygame.draw.rect(screen, couleur_force, (reg_x, reg_y, remplissage, reg_hauteur))
            
            # Bordure
            pygame.draw.rect(screen, BLANC, (reg_x, reg_y, reg_largeur, reg_hauteur), 2)
            
            # Texte force
            texte_force = self.font_petit.render(
                f"Force: {force_actuelle:.1f}/60",
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
    
    def afficher_ecran_victoire(self, screen, largeur, hauteur, partie):
        """
        Affiche l'écran de victoire : fond uni, nom du vainqueur, bouton Rejouer.

        Returns:
            pygame.Rect: rect du bouton Rejouer (pour test de clic)
        """
        gagnant = partie.obtenir_gagnant()
        couleur_gagnant = couleur_joueur(gagnant.couleur)

        screen.fill(FOND_ÉCRAN)

        cx  = largeur  // 2
        cy  = hauteur  // 2

        # Nom du vainqueur
        surf_nom = self.font_titre.render(f"{gagnant.nom}", True, couleur_gagnant)
        screen.blit(surf_nom, (cx - surf_nom.get_width() // 2, cy - 130))

        # "est vainqueur !"
        surf_vainqueur = self.font_grand.render("est vainqueur !", True, OR)
        screen.blit(surf_vainqueur, (cx - surf_vainqueur.get_width() // 2, cy - 40))

        # Bouton Rejouer
        btn = pygame.Rect(cx - 120, cy + 60, 240, 55)
        souris = pygame.mouse.get_pos()
        return self.dessiner_bouton(screen, "Rejouer ?", btn,
                                    survol=btn.collidepoint(souris))


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
        # Coefficient a = 120 pour atteindre force max 60 à t=0.71s
        # f(0.5) = 120 * 0.5² = 120 * 0.25 = 30  →  max doublé à 60
        a = 120
        force = min(max(a * (self.temps_clic ** 2), 0.5), 60)  # f = 120*t²
        
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
            float: Force entre 0.5 et 60
        """
        if not self.clic_en_cours:
            return 0.0
        a = 120  # Coefficient pour f = 120*t²
        return min(max(a * (self.temps_clic ** 2), 0.5), 60)


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
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

        self.largeur = largeur
        self.hauteur = hauteur
        self.fps = fps

        # Configuration Pygame
        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("BounceBox - Jeu de Billard")
        self.clock = pygame.time.Clock()

        # Sons synthétiques (pas de fichiers externes nécessaires)
        self.son_collision  = _generer_son(frequence=300, duree=0.08, volume=0.35)  # choc sourd
        self.son_point      = _generer_son(frequence=660, duree=0.25, volume=0.5)   # note aiguë
        self.son_tour       = _generer_son(frequence=440, duree=0.15, volume=0.3)   # bip neutre
        self.son_victoire   = _generer_son(frequence=880, duree=0.6,  volume=0.6)   # fanfare

        # Suivi d'état pour déclencher les sons au bon moment
        self._score_avant = (0, 0)          # (score_j1, score_j2) au frame précédent
        self._joueur_actif_avant = None     # joueur actif au frame précédent
        self._victoire_jouee = False        # pour ne jouer la fanfare qu'une fois

        # Composants
        self.afficheur = Afficheur(largeur, hauteur)
        self.entrees = GestionnaireEntrees(self.afficheur)

        # État du jeu
        self.partie  = None
        self.running = True

        # Navigation entre écrans : 'titre' → 'noms' → 'jeu'
        self.ecran        = 'titre'
        self.noms         = ['', '']   # noms saisis par les joueurs
        self.champ_actif  = 0          # champ de saisie actif (0 = j1, 1 = j2)
        self.sauvegarder  = False      # case à cocher sauvegarde
        self._tirage_timer = 0.0       # durée d'affichage du message tirage au sort

        # Initialisation de la base de données
        initialiser_base()
    
    def nouvelle_partie(self):
        """Crée et démarre une nouvelle partie avec les noms saisis."""
        nom1 = self.noms[0].strip() or "Joueur 1"
        nom2 = self.noms[1].strip() or "Joueur 2"
        self.partie = Partie(nom1, nom2, sauvegarder=self.sauvegarder)
        self.partie.demarrer()
        self._score_avant        = (0, 0)
        self._joueur_actif_avant = self.partie.joueur_actif
        self._victoire_jouee     = False
        self._tirage_timer       = 3.0   # affiche le message pendant 3 secondes
        print(f"Nouvelle partie : {nom1} vs {nom2}")
    
    def gerer_events(self):
        """Traite tous les événements pygame selon l'écran actif."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # ── ÉCRAN TITRE ──────────────────────────────────────────
            elif self.ecran == 'titre':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn = pygame.Rect(self.largeur // 2 - 120,
                                      self.hauteur // 2 + 20, 240, 55)
                    if btn.collidepoint(event.pos):
                        self.ecran = 'noms'

            # ── ÉCRAN NOMS ───────────────────────────────────────────
            elif self.ecran == 'noms':
                cx = self.largeur // 2
                rect_j1 = pygame.Rect(cx - 160, 200, 320, 44)
                rect_j2 = pygame.Rect(cx - 160, 310, 320, 44)
                btn_lancer = pygame.Rect(cx - 120, 430, 240, 55)
                rect_checkbox = pygame.Rect(cx - 160, 385, 22, 22)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if rect_j1.collidepoint(event.pos):
                        self.champ_actif = 0
                    elif rect_j2.collidepoint(event.pos):
                        self.champ_actif = 1
                    elif rect_checkbox.collidepoint(event.pos):
                        self.sauvegarder = not self.sauvegarder
                    elif btn_lancer.collidepoint(event.pos):
                        self.nouvelle_partie()
                        self.ecran = 'jeu'

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.champ_actif = 1 - self.champ_actif   # bascule entre les deux champs
                    elif event.key == pygame.K_RETURN:
                        if self.champ_actif == 0:
                            self.champ_actif = 1                  # passe au champ suivant
                        else:
                            self.nouvelle_partie()
                            self.ecran = 'jeu'
                    elif event.key == pygame.K_BACKSPACE:
                        self.noms[self.champ_actif] = self.noms[self.champ_actif][:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.ecran = 'titre'
                    else:
                        if len(self.noms[self.champ_actif]) < 16:
                            self.noms[self.champ_actif] += event.unicode

            # ── ÉCRAN VICTOIRE ───────────────────────────────────────
            elif self.ecran == 'victoire':
                btn_rejouer = pygame.Rect(self.largeur // 2 - 120,
                                          self.hauteur // 2 + 60, 240, 55)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_rejouer.collidepoint(event.pos):
                        self.noms = ['', '']
                        self.ecran = 'noms'
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.ecran = 'titre'

            # ── ÉCRAN JEU ────────────────────────────────────────────
            elif self.ecran == 'jeu':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    self.entrees.gerer_clic_debut(x, y, self.partie)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    x, y = event.pos
                    self.entrees.gerer_clic_fin(x, y, self.partie)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Retour au menu noms pour recommencer
                        self.noms = ['', '']
                        self.ecran = 'noms'
                    elif event.key == pygame.K_ESCAPE:
                        self.ecran = 'titre'
                    elif event.key == pygame.K_r:
                        self.nouvelle_partie()
    
    def mettre_a_jour(self):
        """Met à jour la logique du jeu (uniquement en écran 'jeu')."""
        if self.ecran != 'jeu':
            return
        delta_t = self.clock.get_time() / 1000.0
        delta_t = min(delta_t, 0.05)

        self.entrees.mettre_a_jour_clic(delta_t)

        # Décompte du message tirage au sort
        if self._tirage_timer > 0:
            self._tirage_timer = max(0.0, self._tirage_timer - delta_t)

        # Capturer l'état AVANT la mise à jour pour détecter les changements
        score_avant = (self.partie.joueur1.score, self.partie.joueur2.score)
        joueur_avant = self.partie.joueur_actif

        self.partie.mettre_a_jour(delta_t)

        # --- Déclenchement des sons ---

        # 1. Collision entre n'importe quelles boules
        if self.partie.tapis.nb_collisions > 0:
            self.son_collision.play()

        # 2. Point marqué (score a augmenté)
        score_apres = (self.partie.joueur1.score, self.partie.joueur2.score)
        if score_apres != score_avant:
            self.son_point.play()

        # 3. Changement de joueur actif
        if self.partie.joueur_actif is not joueur_avant:
            self.son_tour.play()

        # 4. Victoire (joué une seule fois)
        if self.partie.est_termines() and not self._victoire_jouee:
            self.son_victoire.play()
            self._victoire_jouee = True
            self.ecran = 'victoire'
            print(f"Partie terminée! Gagnant: {self.partie.obtenir_gagnant().nom}")
    
    def afficher(self):
        """Affiche l'écran actif."""
        if self.ecran == 'titre':
            self.afficheur.afficher_ecran_titre(self.screen, self.largeur, self.hauteur)

        elif self.ecran == 'noms':
            self.afficheur.afficher_ecran_noms(self.screen, self.largeur, self.hauteur,
                                               self.noms, self.champ_actif, self.sauvegarder)

        elif self.ecran == 'victoire':
            self.afficheur.afficher_ecran_victoire(self.screen, self.largeur, self.hauteur,
                                                   self.partie)

        elif self.ecran == 'jeu':
            self.afficheur.afficher_fond(self.screen)
            self.afficheur.afficher_all_boules(self.screen, self.partie.tapis)
            force_actuelle = self.entrees.obtenir_force_actuelle()
            self.afficheur.afficher_interface(self.screen, self.partie, force_actuelle)

            # Message tirage au sort (affiché 3 secondes au début)
            if self._tirage_timer > 0:
                j_rouge = self.partie.joueur_actif    # Rouge commence toujours
                j_bleu  = self.partie.joueur_inactif
                texte   = f"🎲  {j_rouge.nom} = Rouge  —  {j_bleu.nom} = Bleu"
                surf_tirage = self.afficheur.font_grand.render(texte, True, OR)
                x_msg = self.largeur // 2 - surf_tirage.get_width() // 2
                y_msg = self.hauteur // 2 - surf_tirage.get_height() // 2
                fond = pygame.Surface((surf_tirage.get_width() + 40, surf_tirage.get_height() + 20))
                fond.set_alpha(180)
                fond.fill((0, 0, 0))
                self.screen.blit(fond, (x_msg - 20, y_msg - 10))
                self.screen.blit(surf_tirage, (x_msg, y_msg))

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




if __name__ == "__main__":
    app = ApplicationGUI(largeur=1000, hauteur=600, fps=60)
    app.lancer()
