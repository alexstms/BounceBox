"""
Module: bouncebox_gui.py
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
from bouncebox_db import initialiser_base, sauvegarder_partie
from bouncebox_ia import JoueurIA, NiveauIA

# ============================================================================
# CONSTANTES DE SÉCURITÉ POUR L'INTERFACE GRAPHIQUE
# ============================================================================
VERT_FOND_CLAIR       = (34, 139, 34)   # VERT_TAPIS original
VERT_FOND_FONCE       = (20, 80, 20)    # Version assombrie pour le dégradé
VERT_FEUTRE           = (34, 139, 34)   # VERT_TAPIS original
VERT_FEUTRE_BORD      = (20, 80, 20)
BOIS_CADRE            = (139, 69, 19)   # BRUN_BORDURE original
BOIS_CADRE_CLAIR      = (180, 100, 40)  # Reflet bois
LOGO_PIERRE           = (200, 200, 200)
LOGO_PIERRE_OMBRE     = (50, 50, 50)
PANEL_ROUGE           = (140, 20, 20)
PANEL_BLEU            = (20, 40, 140)
PANEL_BORDURE         = (255, 215, 0)   # OR original
BILLE_VIDE            = (40, 50, 45)
BILLE_VIDE_BORD       = (70, 85, 75)
TIMER_FOND            = (230, 235, 220) # Écran digital clair
TIMER_TEXTE           = (20, 40, 30)


def _generer_son(frequence, duree, volume=0.4, decroissance=True):
    """Génère un son synthétique sans fichier externe."""
    sample_rate = 44100
    n_samples = int(sample_rate * duree)
    buf = array.array('h', [0] * n_samples)
    for i in range(n_samples):
        t = i / sample_rate
        val = math.sin(2 * math.pi * frequence * t)
        if decroissance:
            val *= 1.0 - (i / n_samples)
        buf[i] = int(val * volume * 32767)
    son = pygame.mixer.Sound(buffer=buf)
    return son


class Afficheur:
    """Gère tout le rendu graphique du jeu."""

    def __init__(self, largeur_ecran, hauteur_ecran, tapis_largeur=50, tapis_hauteur=50):
        self.largeur_ecran = largeur_ecran
        self.hauteur_ecran = hauteur_ecran
        self.tapis_largeur = tapis_largeur
        self.tapis_hauteur = tapis_hauteur

        # Zone latérale droite (~38% de la largeur) pour le logo, scores et timer
        self.zone_laterale = int(largeur_ecran * 0.38)

        marge_haut = 70
        marge_bas = 70
        marge_gauche = 30

        espace_largeur = largeur_ecran - self.zone_laterale - marge_gauche - 20
        espace_hauteur = hauteur_ecran - marge_haut - marge_bas

        scale_max_x = espace_largeur / tapis_largeur
        scale_max_y = espace_hauteur / tapis_hauteur
        self.scale = min(scale_max_x, scale_max_y)

        self.zone_largeur = int(self.scale * tapis_largeur)
        self.zone_hauteur = int(self.scale * tapis_hauteur)

        self.marge_left = marge_gauche + (espace_largeur - self.zone_largeur) // 2
        self.marge_top = marge_haut + (espace_hauteur - self.zone_hauteur) // 2
        self.marge_right = self.marge_left
        self.marge_bottom = hauteur_ecran - self.marge_top - self.zone_hauteur

        self.zone_x = largeur_ecran - self.zone_laterale
        self.scale_x = self.scale
        self.scale_y = self.scale

        # Polices
        # Polices (sécurisées avec SysFont pour éviter les carrés blancs)
        self.font_titre = pygame.font.SysFont("arial", 90, bold=True)
        self.font_grand = pygame.font.SysFont("arial", 40)
        self.font_moyen = pygame.font.SysFont("arial", 30)
        self.font_petit = pygame.font.SysFont("arial", 20)
        self.font_logo = pygame.font.SysFont("arial", 64, bold=True)
        self.font_timer = pygame.font.SysFont("arial", 56)
        self._fond_cache = None

    def dessiner_bouton(self, screen, texte, rect, survol=False):
        couleur_fond    = (60, 60, 80) if not survol else (90, 90, 120)
        couleur_bordure = OR if survol else GRIS_CLAIR
        pygame.draw.rect(screen, couleur_fond,    rect, border_radius=10)
        pygame.draw.rect(screen, couleur_bordure, rect, 2, border_radius=10)
        surf = self.font_grand.render(texte, True, BLANC)
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))
        return rect

    def dessiner_champ_texte(self, screen, label, valeur, rect, actif=False, curseur=True):
        surf_label = self.font_petit.render(label, True, GRIS_CLAIR)
        screen.blit(surf_label, (rect.x, rect.y - 22))

        couleur_bordure = OR if actif else GRIS_CLAIR
        pygame.draw.rect(screen, GRIS_FONCÉ, rect, border_radius=6)
        pygame.draw.rect(screen, couleur_bordure, rect, 2, border_radius=6)

        affichage = valeur
        if actif and curseur and int(time.time() * 2) % 2 == 0:
            affichage += '|'
        surf_texte = self.font_moyen.render(affichage, True, BLANC)
        screen.blit(surf_texte, (rect.x + 10, rect.centery - surf_texte.get_height() // 2))

    def afficher_ecran_titre(self, screen, largeur, hauteur):
        screen.fill(FOND_ÉCRAN)
        surf_titre = self.font_titre.render("BounceBox", True, OR)
        screen.blit(surf_titre, (largeur // 2 - surf_titre.get_width() // 2, hauteur // 2 - 140))

        surf_sous = self.font_moyen.render("Jeu de billard à deux joueurs", True, GRIS_CLAIR)
        screen.blit(surf_sous, (largeur // 2 - surf_sous.get_width() // 2, hauteur // 2 - 50))

        btn = pygame.Rect(largeur // 2 - 120, hauteur // 2 + 20, 240, 55)
        souris = pygame.mouse.get_pos()
        return self.dessiner_bouton(screen, "▶  Jouer", btn, survol=btn.collidepoint(souris))

    def afficher_ecran_mode(self, screen, largeur, hauteur):
        """Affiche l'écran de sélection du mode de jeu (J1vsJ2, J1vsIA, IAvsIA)."""
        screen.fill(FOND_ÉCRAN)
        surf_titre = self.font_grand.render("Choisir le mode de jeu", True, OR)
        screen.blit(surf_titre, (largeur // 2 - surf_titre.get_width() // 2, 80))

        cx = largeur // 2
        modes = [
            ("Joueur vs Joueur",  'jvj'),
            ("Joueur vs IA",      'jvia'),
            ("IA vs IA",          'iavia'),
        ]
        rects = {}
        souris = pygame.mouse.get_pos()
        for i, (label, key) in enumerate(modes):
            rect = pygame.Rect(cx - 160, 180 + i * 90, 320, 60)
            self.dessiner_bouton(screen, label, rect, survol=rect.collidepoint(souris))
            rects[key] = rect

        rect_retour = pygame.Rect(cx - 80, 470, 160, 45)
        self.dessiner_bouton(screen, "<- Retour", rect_retour, survol=rect_retour.collidepoint(souris))
        rects['retour'] = rect_retour
        return rects

    def afficher_ecran_noms(self, screen, largeur, hauteur, noms, champ_actif, sauvegarder=False, mode='jvj', niveau_ia=NiveauIA.MOYEN):
        screen.fill(FOND_ÉCRAN)
        surf_titre = self.font_grand.render("Entrez les noms des joueurs", True, OR)
        screen.blit(surf_titre, (largeur // 2 - surf_titre.get_width() // 2, 80))

        cx = largeur // 2

        label1 = "Joueur 1 (Rouge)"
        label2 = "IA (Bleu)" if mode == 'jvia' else ("IA Rouge" if mode == 'iavia' else "Joueur 2 (Bleu)")

        rect_j1 = pygame.Rect(cx - 160, 200, 320, 44)
        desactive_j1 = (mode == 'iavia')
        affiche_j1 = noms[0] if not desactive_j1 else "IA 1"
        self.dessiner_champ_texte(screen, label1, affiche_j1, rect_j1, actif=(champ_actif == 0 and not desactive_j1))

        rect_j2 = pygame.Rect(cx - 160, 310, 320, 44)
        desactive_j2 = (mode in ('jvia', 'iavia'))
        affiche_j2 = noms[1] if not desactive_j2 else "IA 2"
        self.dessiner_champ_texte(screen, label2, affiche_j2, rect_j2, actif=(champ_actif == 1 and not desactive_j2))

        # Sélection du niveau IA (visible si mode contient une IA)
        if mode in ('jvia', 'iavia'):
            surf_niv = self.font_petit.render("Niveau IA :", True, GRIS_CLAIR)
            screen.blit(surf_niv, (cx - 160, 372))
            niveaux = [NiveauIA.FACILE, NiveauIA.MOYEN, NiveauIA.DIFFICILE]
            labels_niv = ["Facile", "Moyen", "Difficile"]
            rects_niveaux = []
            for k, (niv, lbl) in enumerate(zip(niveaux, labels_niv)):
                r = pygame.Rect(cx - 160 + k * 110, 392, 100, 34)
                actif_niv = (niv == niveau_ia)
                couleur_fond    = (60, 100, 60) if actif_niv else (40, 40, 55)
                couleur_bordure = VERT_OK if actif_niv else GRIS_CLAIR
                pygame.draw.rect(screen, couleur_fond,    r, border_radius=8)
                pygame.draw.rect(screen, couleur_bordure, r, 2, border_radius=8)
                surf_lbl = self.font_petit.render(lbl, True, BLANC)
                screen.blit(surf_lbl, (r.centerx - surf_lbl.get_width() // 2, r.centery - surf_lbl.get_height() // 2))
                rects_niveaux.append((niv, r))
        else:
            rects_niveaux = []

        case_taille = 22
        rect_checkbox = pygame.Rect(cx - 160, 440, case_taille, case_taille)
        pygame.draw.rect(screen, GRIS_FONCÉ,  rect_checkbox, border_radius=4)
        pygame.draw.rect(screen, GRIS_CLAIR,  rect_checkbox, 2, border_radius=4)
        if sauvegarder:
            pygame.draw.line(screen, VERT_OK, (rect_checkbox.x + 4, rect_checkbox.centery), (rect_checkbox.centerx - 1, rect_checkbox.bottom - 5), 2)
            pygame.draw.line(screen, VERT_OK, (rect_checkbox.centerx - 1, rect_checkbox.bottom - 5), (rect_checkbox.right - 4, rect_checkbox.y + 5), 2)

        surf_case = self.font_petit.render("Sauvegarder le resultat de la partie", True, VERT_OK if sauvegarder else GRIS_CLAIR)
        screen.blit(surf_case, (rect_checkbox.right + 10, rect_checkbox.centery - surf_case.get_height() // 2))

        btn = pygame.Rect(cx - 120, 485, 240, 55)
        souris = pygame.mouse.get_pos()
        self.dessiner_bouton(screen, "Lancer la partie", btn, survol=btn.collidepoint(souris))

        return rect_j1, rect_j2, btn, rect_checkbox, rects_niveaux

    def convertir_position(self, vecteur_position):
        x = int(vecteur_position.x * self.scale_x + self.marge_left)
        y = int(vecteur_position.y * self.scale_y + self.marge_top)
        return (x, y)

    def convertir_rayon(self, rayon):
        return max(int(rayon * self.scale_x), 2)

    def convertir_position_inverse(self, x_pixel, y_pixel):
        x_logique = (x_pixel - self.marge_left) / self.scale_x
        y_logique = (y_pixel - self.marge_top) / self.scale_y
        return (x_logique, y_logique)

    def _generer_fond_degrade(self):
        surf = pygame.Surface((self.largeur_ecran, self.hauteur_ecran))
        cr, cg, cb = VERT_FOND_CLAIR
        fr, fg, fb = VERT_FOND_FONCE
        for y in range(self.hauteur_ecran):
            t = y / max(1, self.hauteur_ecran - 1)
            r = int(cr + (fr - cr) * t)
            g = int(cg + (fg - cg) * t)
            b = int(cb + (fb - cb) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (self.largeur_ecran, y))
        return surf

    def dessiner_logo(self, screen, centre_x, centre_y, echelle=1.0):
        font = pygame.font.Font(None, int(64 * echelle))
        segments = [
            ("B", None),
            ("O", ("bille", BLEU)),
            ("UNCE", None),
            (" B", None),
            ("O", ("bille", ROUGE)),
            ("X", None),
        ]

        largeur_totale = 0
        hauteur_max = 0
        tailles = []
        for txt, special in segments:
            surf = font.render(txt, True, LOGO_PIERRE)
            tailles.append(surf)
            largeur_totale += surf.get_width()
            hauteur_max = max(hauteur_max, surf.get_height())

        x = centre_x - largeur_totale // 2
        y = centre_y - hauteur_max // 2

        for (txt, special), surf in zip(segments, tailles):
            if special and special[0] == "bille":
                rayon = int(hauteur_max * 0.34)
                cx_bille = x + surf.get_width() // 2
                cy_bille = centre_y
                self._dessiner_bille_brillante(screen, (cx_bille, cy_bille), rayon, special[1])
            else:
                ombre = font.render(txt, True, LOGO_PIERRE_OMBRE)
                screen.blit(ombre, (x + 2, y + 2))
                screen.blit(surf, (x, y))
            x += surf.get_width()

    def _dessiner_bille_brillante(self, screen, centre, rayon, couleur):
        cx, cy = centre
        r, g, b = couleur
        base = (int(r * 0.65), int(g * 0.65), int(b * 0.65))
        pygame.draw.circle(screen, base, (cx, cy), rayon)

        n = max(3, rayon // 2)
        for i in range(n, 0, -1):
            t = i / n
            rr = int(r * (0.65 + 0.35 * (1 - t)))
            gg = int(g * (0.65 + 0.35 * (1 - t)))
            bb = int(b * (0.65 + 0.35 * (1 - t)))
            rr, gg, bb = min(255, rr), min(255, gg), min(255, bb)
            offset = int(rayon * 0.25 * t)
            pygame.draw.circle(screen, (rr, gg, bb), (cx - offset, cy - offset), int(rayon * t))

        reflet_r = max(2, rayon // 4)
        pygame.draw.circle(screen, (255, 255, 255), (cx - rayon // 3, cy - rayon // 3), reflet_r)
        pygame.draw.circle(screen, (20, 20, 20), (cx, cy), rayon, 1)

    def afficher_fond(self, screen):
        if self._fond_cache is None:
            self._fond_cache = self._generer_fond_degrade()
        screen.blit(self._fond_cache, (0, 0))

        logo_cx = self.zone_x + self.zone_laterale // 2
        self.dessiner_logo(screen, logo_cx, 45, echelle=0.85)

        ep = 12
        cadre_rect = pygame.Rect(self.marge_left - ep, self.marge_top - ep, self.zone_largeur + 2 * ep, self.zone_hauteur + 2 * ep)
        pygame.draw.rect(screen, BOIS_CADRE, cadre_rect, border_radius=6)
        pygame.draw.rect(screen, BOIS_CADRE_CLAIR, cadre_rect, 2, border_radius=6)

        tapis_rect = pygame.Rect(self.marge_left, self.marge_top, self.zone_largeur, self.zone_hauteur)
        pygame.draw.rect(screen, VERT_FEUTRE, tapis_rect)
        pygame.draw.rect(screen, VERT_FEUTRE_BORD, tapis_rect, 3)

    def afficher_boule(self, screen, boule):
        centre_pixel = self.convertir_position(boule.position)
        rayon_pixel = self.convertir_rayon(boule.rayon)
        couleur = couleur_boule(boule.couleur)
        self._dessiner_bille_brillante(screen, centre_pixel, rayon_pixel, couleur)

    def afficher_all_boules(self, screen, tapis):
        for boule in tapis.boules:
            self.afficher_boule(screen, boule)

    def afficher_visee(self, screen, partie, position_souris, force_actuelle, force_max=60.0):
        if partie.coup_lance:
            return

        boule_blanche = partie.tapis.obtenir_boule_blanche()
        centre = self.convertir_position(boule_blanche.position)

        dx = position_souris[0] - centre[0]
        dy = position_souris[1] - centre[1]
        dist = math.hypot(dx, dy)
        if dist < 5:
            return
        ux, uy = dx / dist, dy / dist

        ratio = min(force_actuelle / force_max, 1.0) if force_actuelle > 0 else 0.0
        longueur = 40 + ratio * 90
        rayon_b = self.convertir_rayon(boule_blanche.rayon)

        debut = (centre[0] + ux * (rayon_b + 4), centre[1] + uy * (rayon_b + 4))
        fin = (debut[0] + ux * longueur, debut[1] + uy * longueur)

        couleur_queue = (int(150 + 105 * ratio), int(110 - 70 * ratio), int(60 - 40 * ratio))
        pygame.draw.line(screen, couleur_queue, debut, fin, 6)
        pygame.draw.circle(screen, (230, 215, 170), (int(debut[0]), int(debut[1])), 4)

        vise_fin = (centre[0] - ux * 60, centre[1] - uy * 60)
        self._ligne_pointillee(screen, centre, vise_fin, (255, 255, 255), 1, 6)

    def _ligne_pointillee(self, screen, debut, fin, couleur, epaisseur=1, segment=6):
        x1, y1 = debut
        x2, y2 = fin
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0:
            return
        ux, uy = (x2 - x1) / dist, (y2 - y1) / dist
        n = int(dist // segment)
        for i in range(0, n, 2):
            sx = x1 + ux * segment * i
            sy = y1 + uy * segment * i
            ex = x1 + ux * segment * (i + 1)
            ey = y1 + uy * segment * (i + 1)
            pygame.draw.line(screen, couleur, (sx, sy), (ex, ey), epaisseur)

    def _dessiner_panneau_joueur(self, screen, x, y, largeur, joueur, actif):
        from bouncebox_boules import Couleur
        hauteur = 78
        rect = pygame.Rect(x, y, largeur, hauteur)

        if joueur.couleur == Couleur.ROUGE:
            fond = PANEL_ROUGE if actif else (PANEL_ROUGE[0] // 2 + 30, PANEL_ROUGE[1] // 2 + 20, PANEL_ROUGE[2] // 2 + 15)
            couleur_bille = ROUGE
        else:
            fond = PANEL_BLEU if actif else (PANEL_BLEU[0] // 2 + 15, PANEL_BLEU[1] // 2 + 20, PANEL_BLEU[2] // 2 + 30)
            couleur_bille = BLEU

        pygame.draw.rect(screen, fond, rect, border_radius=10)
        if actif:
            pygame.draw.rect(screen, PANEL_BORDURE, rect, 3, border_radius=10)
        else:
            pygame.draw.rect(screen, (90, 90, 70), rect, 1, border_radius=10)

        texte = f"({joueur.score})  {joueur.nom}"
        surf_nom = self.font_moyen.render(texte, True, BLANC)
        screen.blit(surf_nom, (x + 14, y + 8))

        total = joueur.POINTS_VICTOIRE
        rayon = 11
        espacement = (largeur - 28) / total
        cy = y + hauteur - 22
        for i in range(total):
            cx = int(x + 14 + espacement * i + espacement / 2)
            if i < joueur.score:
                self._dessiner_bille_brillante(screen, (cx, cy), rayon, couleur_bille)
            else:
                pygame.draw.circle(screen, BILLE_VIDE, (cx, cy), rayon)
                pygame.draw.circle(screen, BILLE_VIDE_BORD, (cx, cy), rayon, 1)

    def _dessiner_timer(self, screen, cx, cy, secondes):
        minutes = secondes // 60
        sec = secondes % 60
        texte = f"{minutes:02d}:{sec:02d}"

        surf = self.font_timer.render(texte, True, TIMER_TEXTE)
        pad_x, pad_y = 16, 6
        rect = pygame.Rect(0, 0, surf.get_width() + 2 * pad_x, surf.get_height() + 2 * pad_y)
        rect.center = (cx, cy)

        pygame.draw.rect(screen, TIMER_FOND, rect, border_radius=6)
        pygame.draw.rect(screen, (150, 150, 130), rect, 2, border_radius=6)
        screen.blit(surf, (rect.centerx - surf.get_width() // 2, rect.centery - surf.get_height() // 2))

    def afficher_interface(self, screen, partie, force_actuelle=0.0):
        j1 = partie.joueur1
        j2 = partie.joueur2
        joueur_actif = partie.joueur_actif
        joueur_inactif = partie.joueur_inactif  # Correction du bug d'orthographe ici

        marge = 20
        x = self.zone_x + marge
        largeur_panel = self.zone_laterale - 2 * marge

        y_haut = 100
        self._dessiner_panneau_joueur(screen, x, y_haut, largeur_panel, joueur_actif, actif=True)

        temps_restant = max(0, int(joueur_actif.temps_restant_tour))
        timer_cy = y_haut + 78 + 32
        self._dessiner_timer(screen, x + largeur_panel // 2, timer_cy, temps_restant)

        y_bas = timer_cy + 32
        self._dessiner_panneau_joueur(screen, x, y_bas, largeur_panel, joueur_inactif, actif=False)

        if force_actuelle > 0:
            reg_x = self.marge_left
            reg_y = self.marge_top + self.zone_largeur + 18
            reg_largeur = self.zone_largeur
            reg_hauteur = 16

            pygame.draw.rect(screen, (30, 50, 25), (reg_x, reg_y, reg_largeur, reg_hauteur), border_radius=4)
            pourcentage = min(force_actuelle / 60.0, 1.0)
            remplissage = int(reg_largeur * pourcentage)
            if pourcentage < 0.5:
                t = pourcentage * 2
                couleur_force = (int(255 * t), 255, 0)
            else:
                t = (pourcentage - 0.5) * 2
                couleur_force = (255, int(255 * (1 - t)), 0)
            pygame.draw.rect(screen, couleur_force, (reg_x, reg_y, remplissage, reg_hauteur), border_radius=4)
            pygame.draw.rect(screen, BLANC, (reg_x, reg_y, reg_largeur, reg_hauteur), 2, border_radius=4)

            texte_force = self.font_petit.render(f"Force : {force_actuelle:.0f}/60", True, BLANC)
            screen.blit(texte_force, (reg_x, reg_y - 22))

        if not partie.coup_lance:
            msg = "Maintenez le clic pour charger, relâchez pour tirer" if force_actuelle == 0 else "Relâchez pour lancer !"
            couleur_msg = JAUNE_TEXTE if force_actuelle > 0 else (230, 230, 210)
            surf_info = self.font_petit.render(msg, True, couleur_msg)
            screen.blit(surf_info, (self.marge_left, self.marge_top + self.zone_largeur + 42))

    def afficher_ecran_victoire(self, screen, largeur, hauteur, partie):
        gagnant = partie.obtenir_gagnant()
        couleur_gagnant = couleur_joueur(gagnant.couleur)

        screen.fill(FOND_ÉCRAN)
        cx  = largeur  // 2
        cy  = hauteur  // 2

        surf_nom = self.font_titre.render(f"{gagnant.nom}", True, couleur_gagnant)
        screen.blit(surf_nom, (cx - surf_nom.get_width() // 2, cy - 130))

        surf_vainqueur = self.font_grand.render("est vainqueur !", True, OR)
        screen.blit(surf_vainqueur, (cx - surf_vainqueur.get_width() // 2, cy - 40))

        btn = pygame.Rect(cx - 120, cy + 60, 240, 55)
        souris = pygame.mouse.get_pos()
        return self.dessiner_bouton(screen, "Rejouer ?", btn, survol=btn.collidepoint(souris))


class GestionnaireEntrees:
    """Gère tous les inputs (souris, clavier) pour le jeu."""

    def __init__(self, afficheur):
        self.afficheur = afficheur
        self.clic_en_cours = False
        self.position_clic_debut = None
        self.temps_clic = 0.0
        self.position_souris = (0, 0)

    def gerer_clic_debut(self, x_pixel, y_pixel, partie):
        if partie.coup_lance:
            return
        self.clic_en_cours = True
        self.position_clic_debut = (x_pixel, y_pixel)
        self.temps_clic = 0.0

    def gerer_clic_fin(self, x_pixel, y_pixel, partie):
        if not self.clic_en_cours or self.position_clic_debut is None:
            return
        self.clic_en_cours = False
        if partie.coup_lance:
            return

        x_debut, y_debut = self.position_clic_debut
        x_depart_logique, y_depart_logique = self.afficheur.convertir_position_inverse(x_debut, y_debut)
        x_cible_logique, y_cible_logique = self.afficheur.convertir_position_inverse(x_pixel, y_pixel)

        boule = partie.tapis.obtenir_boule_blanche()
        dx = x_cible_logique - boule.position.x
        dy = y_cible_logique - boule.position.y

        angle = math.atan2(dy, dx)
        a = 120
        force = min(max(a * (self.temps_clic ** 2), 0.5), 60)

        print(f"Tir: angle={angle:.2f}, force={force:.2f}, temps_clic={self.temps_clic:.2f}s")
        partie.lancer_coup(angle, force)

        self.position_clic_debut = None
        self.temps_clic = 0.0

    def mettre_a_jour_clic(self, delta_t):
        if self.clic_en_cours:
            self.temps_clic += delta_t

    def gerer_mouvement_souris(self, x_pixel, y_pixel):
        self.position_souris = (x_pixel, y_pixel)

    def obtenir_force_actuelle(self):
        if not self.clic_en_cours:
            return 0.0
        a = 120
        return min(max(a * (self.temps_clic ** 2), 0.5), 60)


class ApplicationGUI:
    """Classe principale de l'application. Gère la boucle principale."""

    def __init__(self, largeur=1000, hauteur=600, fps=60):
        pygame.init()
        pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

        self.largeur = largeur
        self.hauteur = hauteur
        self.fps = fps

        self.screen = pygame.display.set_mode((largeur, hauteur))
        pygame.display.set_caption("BounceBox - Jeu de Billard")
        self.clock = pygame.time.Clock()

        self.son_collision  = _generer_son(frequence=300, duree=0.08, volume=0.35)
        self.son_point      = _generer_son(frequence=660, duree=0.25, volume=0.5)
        self.son_tour       = _generer_son(frequence=440, duree=0.15, volume=0.3)
        self.son_victoire   = _generer_son(frequence=880, duree=0.6,  volume=0.6)

        self._score_avant = (0, 0)
        self._joueur_actif_avant = None
        self._victoire_jouee = False

        self.afficheur = Afficheur(largeur, hauteur)
        self.entrees = GestionnaireEntrees(self.afficheur)

        self.partie  = None
        self.running = True

        self.ecran        = 'titre'
        self.noms         = ['', '']
        self.champ_actif  = 0
        self.sauvegarder  = False
        self._tirage_timer = 0.0
        self.mode_jeu     = 'jvj'    # 'jvj' | 'jvia' | 'iavia'
        self.niveau_ia    = NiveauIA.MOYEN
        self._ia_joueur1  = None     # JoueurIA si mode iavia
        self._ia_joueur2  = None     # JoueurIA si mode jvia ou iavia

        initialiser_base()

    def nouvelle_partie(self):
        nom1 = self.noms[0].strip() or "Joueur 1"
        nom2 = self.noms[1].strip() or "Joueur 2"
        self.partie = Partie(nom1, nom2)
        self.partie.demarrer()

        # Remplacer les joueurs par des JoueurIA selon le mode
        self._ia_joueur1 = None
        self._ia_joueur2 = None

        if self.mode_jeu == 'jvia':
            # Sauvegarder les références AVANT tout remplacement
            ancien_j2      = self.partie.joueur2
            actif_est_j2   = (self.partie.joueur_actif   is ancien_j2)
            inactif_est_j2 = (self.partie.joueur_inactif is ancien_j2)

            ia = JoueurIA("IA", ancien_j2.couleur, self.niveau_ia)
            ia.score              = ancien_j2.score
            ia.temps_restant_tour = ancien_j2.temps_restant_tour

            self.partie.joueur2      = ia
            self.partie.joueurs[1]   = ia
            if actif_est_j2:
                self.partie.joueur_actif   = ia
            if inactif_est_j2:
                self.partie.joueur_inactif = ia
            self._ia_joueur2 = ia

        elif self.mode_jeu == 'iavia':
            # Les deux joueurs sont des IA
            ia1 = JoueurIA("IA 1", self.partie.joueur1.couleur, self.niveau_ia)
            ia2 = JoueurIA("IA 2", self.partie.joueur2.couleur, self.niveau_ia)
            ia1.score = self.partie.joueur1.score
            ia2.score = self.partie.joueur2.score
            ia1.temps_restant_tour = self.partie.joueur1.temps_restant_tour
            ia2.temps_restant_tour = self.partie.joueur2.temps_restant_tour

            actif_est_j1 = (self.partie.joueur_actif is self.partie.joueur1)

            self.partie.joueur1 = ia1
            self.partie.joueur2 = ia2
            self.partie.joueurs = [ia1, ia2]
            self.partie.joueur_actif   = ia1 if actif_est_j1 else ia2
            self.partie.joueur_inactif = ia2 if actif_est_j1 else ia1
            self._ia_joueur1 = ia1
            self._ia_joueur2 = ia2

        self._score_avant        = (0, 0)
        self._joueur_actif_avant = self.partie.joueur_actif
        self._victoire_jouee     = False
        self._tirage_timer       = 3.0
        print(f"Nouvelle partie ({self.mode_jeu}): {self.partie.joueur1.nom} vs {self.partie.joueur2.nom}")

    def gerer_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif self.ecran == 'titre':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn = pygame.Rect(self.largeur // 2 - 120, self.hauteur // 2 + 20, 240, 55)
                    if btn.collidepoint(event.pos):
                        self.ecran = 'mode'

            elif self.ecran == 'mode':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    cx = self.largeur // 2
                    rects_mode = {
                        'jvj':   pygame.Rect(cx - 160, 180, 320, 60),
                        'jvia':  pygame.Rect(cx - 160, 270, 320, 60),
                        'iavia': pygame.Rect(cx - 160, 360, 320, 60),
                        'retour':pygame.Rect(cx - 80,  470, 160, 45),
                    }
                    for key, rect in rects_mode.items():
                        if rect.collidepoint(event.pos):
                            if key == 'retour':
                                self.ecran = 'titre'
                            else:
                                self.mode_jeu = key
                                self.noms = ['', '']
                                self.champ_actif = 0
                                self.ecran = 'noms'
                            break
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.ecran = 'titre'

            elif self.ecran == 'noms':
                cx = self.largeur // 2
                rect_j1 = pygame.Rect(cx - 160, 200, 320, 44)
                rect_j2 = pygame.Rect(cx - 160, 310, 320, 44)
                btn_lancer = pygame.Rect(cx - 120, 485, 240, 55)
                rect_checkbox = pygame.Rect(cx - 160, 440, 22, 22)
                niveaux = [NiveauIA.FACILE, NiveauIA.MOYEN, NiveauIA.DIFFICILE]
                rects_niveaux = [(niv, pygame.Rect(cx - 160 + k * 110, 392, 100, 34)) for k, niv in enumerate(niveaux)]

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.mode_jeu != 'iavia' and rect_j1.collidepoint(event.pos):
                        self.champ_actif = 0
                    elif self.mode_jeu == 'jvj' and rect_j2.collidepoint(event.pos):
                        self.champ_actif = 1
                    elif rect_checkbox.collidepoint(event.pos):
                        self.sauvegarder = not self.sauvegarder
                    elif btn_lancer.collidepoint(event.pos):
                        self.nouvelle_partie()
                        self.ecran = 'jeu'
                    else:
                        for niv, r in rects_niveaux:
                            if r.collidepoint(event.pos):
                                self.niveau_ia = niv
                                break

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.champ_actif = 1 - self.champ_actif
                    elif event.key == pygame.K_RETURN:
                        if self.champ_actif == 0 and self.mode_jeu == 'jvj':
                            self.champ_actif = 1
                        else:
                            self.nouvelle_partie()
                            self.ecran = 'jeu'
                    elif event.key == pygame.K_BACKSPACE:
                        self.noms[self.champ_actif] = self.noms[self.champ_actif][:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.ecran = 'mode'
                    else:
                        if len(self.noms[self.champ_actif]) < 16:
                            self.noms[self.champ_actif] += event.unicode

            elif self.ecran == 'victoire':
                btn_rejouer = pygame.Rect(self.largeur // 2 - 120, self.hauteur // 2 + 60, 240, 55)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_rejouer.collidepoint(event.pos):
                        self.noms = ['', '']
                        self.ecran = 'mode'
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.ecran = 'titre'

            elif self.ecran == 'jeu':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    self.entrees.gerer_clic_debut(x, y, self.partie)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    x, y = event.pos
                    self.entrees.gerer_clic_fin(x, y, self.partie)

                elif event.type == pygame.MOUSEMOTION:
                    x, y = event.pos
                    self.entrees.gerer_mouvement_souris(x, y)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.noms = ['', '']
                        self.ecran = 'noms'
                    elif event.key == pygame.K_ESCAPE:
                        self.ecran = 'titre'
                    elif event.key == pygame.K_r:
                        self.nouvelle_partie()

    def mettre_a_jour(self):
        if self.ecran != 'jeu':
            return
        delta_t = self.clock.get_time() / 1000.0
        delta_t = min(delta_t, 0.05)

        self.entrees.mettre_a_jour_clic(delta_t)

        if self._tirage_timer > 0:
            self._tirage_timer = max(0.0, self._tirage_timer - delta_t)

        score_avant = (self.partie.joueur1.score, self.partie.joueur2.score)
        joueur_avant = self.partie.joueur_actif

        self.partie.mettre_a_jour(delta_t)

        # Tour IA : si le joueur actif est une IA et qu'aucun coup n'est lancé
        joueur_actif = self.partie.joueur_actif
        if (not self.partie.coup_lance
                and isinstance(joueur_actif, JoueurIA)
                and self.partie.tapis.toutes_boules_immobiles()):
            if joueur_actif.doit_jouer(delta_t):
                angle, force = joueur_actif.choisir_coup(self.partie.tapis)
                self.partie.lancer_coup(angle, force)
                print(f"[IA] {joueur_actif.nom} joue : angle={math.degrees(angle):.1f}°, force={force:.1f}")

        # Réinitialiser le compteur d'attente IA quand le joueur change
        if self.partie.joueur_actif is not joueur_avant:
            nouveau = self.partie.joueur_actif
            if isinstance(nouveau, JoueurIA):
                nouveau.reinitialiser_pour_nouveau_tour()

        if self.partie.tapis.nb_collisions > 0:
            self.son_collision.play()

        score_apres = (self.partie.joueur1.score, self.partie.joueur2.score)
        if score_apres != score_avant:
            self.son_point.play()

        if self.partie.joueur_actif is not joueur_avant:
            self.son_tour.play()

        if self.partie.est_termines() and not self._victoire_jouee:
            if self.sauvegarder:
                sauvegarder_partie(self.partie)
            self.son_victoire.play()
            self._victoire_jouee = True
            self.ecran = 'victoire'
            print(f"Partie terminée! Gagnant: {self.partie.obtenir_gagnant().nom}")

    def afficher(self):
        if self.ecran == 'titre':
            self.afficheur.afficher_ecran_titre(self.screen, self.largeur, self.hauteur)

        elif self.ecran == 'mode':
            self.afficheur.afficher_ecran_mode(self.screen, self.largeur, self.hauteur)

        elif self.ecran == 'noms':
            self.afficheur.afficher_ecran_noms(self.screen, self.largeur, self.hauteur,
                                               self.noms, self.champ_actif, self.sauvegarder,
                                               mode=self.mode_jeu, niveau_ia=self.niveau_ia)

        elif self.ecran == 'victoire':
            self.afficheur.afficher_ecran_victoire(self.screen, self.largeur, self.hauteur, self.partie)

        elif self.ecran == 'jeu':
            self.afficheur.afficher_fond(self.screen)
            self.afficheur.afficher_all_boules(self.screen, self.partie.tapis)
            force_actuelle = self.entrees.obtenir_force_actuelle()

            if self.entrees.clic_en_cours and not self.partie.coup_lance:
                self.afficheur.afficher_visee(
                    self.screen, self.partie,
                    self.entrees.position_souris, force_actuelle, force_max=60.0
                )
            self.afficheur.afficher_interface(self.screen, self.partie, force_actuelle)

            if self._tirage_timer > 0:
                j_rouge = self.partie.joueur_actif
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
            self.clock.tick(self.fps)

            frame_count += 1
            if frame_count % 60 == 0:
                fps_actual = self.clock.get_fps()
                print(f"FPS: {fps_actual:.1f}")

        pygame.quit()
        print("Jeu fermé.")


def main():
    app = ApplicationGUI()
    app.lancer()


if __name__ == "__main__":
    main()