#!/usr/bin/env python3
"""
Main: bouncebox_gui - Point d'entrée pour lancer BounceBox avec Pygame

Point de départ pour jouer au jeu BounceBox avec interface graphique.
"""

import sys
import os


def verifier_pygame():
    """Vérifie que pygame est installé."""
    try:
        import pygame
        print(f"✅ Pygame {pygame.version.ver} détecté")
        return True
    except ImportError:
        print("❌ Pygame n'est pas installé!")
        print("\nPour installer pygame, exécutez:")
        print("  pip install pygame")
        print("\nOu sur Mac:")
        print("  brew install pygame")
        print("\nOu sur Linux:")
        print("  sudo apt-get install python3-pygame")
        return False


def verifier_modules():
    """Vérifie que tous les modules BounceBox sont présents."""
    modules_requis = [
        'bouncebox_vecteur',
        'bouncebox_boules',
        'bouncebox_tapis',
        'bouncebox_partie',
        'bouncebox_couleurs',
        'bouncebox_gui',
    ]
    
    tous_presents = True
    for module in modules_requis:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MANQUANT!")
            tous_presents = False
    
    return tous_presents


def lancer_jeu():
    """Lance le jeu."""
    try:
        from bouncebox_gui import ApplicationGUI
        
        print("\n" + "="*60)
        print("Lancement de BounceBox avec Pygame...")
        print("="*60 + "\n")
        
        # Créer et lancer l'application
        app = ApplicationGUI(largeur=1000, hauteur=600, fps=60)
        app.lancer()
        
    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def main():
    """Fonction principale."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  BOUNCEBOX - INTERFACE GRAPHIQUE PYGAME".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Vérifications
    print("\n📋 Vérification des dépendances...")
    
    if not verifier_pygame():
        print("\n❌ Pygame n'est pas disponible. Impossible de continuer.")
        return 1
    
    print("\n📦 Vérification des modules...")
    if not verifier_modules():
        print("\n❌ Certains modules sont manquants.")
        print("Assurez-vous d'être dans le répertoire correct avec tous les fichiers.")
        return 1
    
    print("\n✅ Toutes les dépendances sont OK!\n")
    
    # Lancer le jeu
    if lancer_jeu():
        print("\n✅ Jeu terminé normalement.")
        return 0
    else:
        print("\n❌ Le jeu s'est arrêté avec une erreur.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
