"""
Module: bouncebox_couleurs.py
Palette de couleurs pour l'interface graphique.
"""

# ============================================================================
# COULEURS PYGAME (RGB)
# ============================================================================

# Couleurs de base
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)
GRIS_CLAIR = (200, 200, 200)
GRIS_FONCÉ = (50, 50, 50)

# Couleurs principales du jeu
ROUGE = (255, 0, 0)
ROUGE_FONCÉ = (200, 0, 0)
BLEU = (0, 0, 255)
BLEU_FONCÉ = (0, 0, 200)
GRIS = (128, 128, 128)
BLANC_BOULE = (255, 255, 255)

# Couleurs du tapis
VERT_TAPIS = (34, 139, 34)  # Vert billard
BRUN_BORDURE = (139, 69, 19)  # Marron

# Couleurs de l'interface
FOND_ÉCRAN = (20, 20, 20)  # Gris très foncé
JAUNE_TEXTE = (255, 255, 0)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
OR = (255, 215, 0)

# Couleurs pour les états
VERT_OK = (0, 255, 0)
ROUGE_ERREUR = (255, 0, 0)


def couleur_boule(couleur_enum):
    """
    Convertit une Couleur enum BounceBox vers RGB Pygame.
    
    Args:
        couleur_enum (Couleur): Couleur du enum BounceBox
        
    Returns:
        tuple: (R, G, B) pour Pygame
    """
    from bouncebox_boules import Couleur
    
    couleurs = {
        Couleur.BLANCHE: BLANC_BOULE,
        Couleur.GRISE: GRIS,
        Couleur.ROUGE: ROUGE,
        Couleur.BLEUE: BLEU,
    }
    
    return couleurs.get(couleur_enum, BLANC_BOULE)


def couleur_joueur(couleur_enum):
    """
    Couleur associée à un joueur pour l'affichage.
    
    Args:
        couleur_enum (Couleur): Couleur du joueur (ROUGE ou BLEUE)
        
    Returns:
        tuple: (R, G, B) pour Pygame
    """
    from bouncebox_boules import Couleur
    
    couleurs = {
        Couleur.ROUGE: ROUGE,
        Couleur.BLEUE: BLEU,
    }
    
    return couleurs.get(couleur_enum, BLANC)
