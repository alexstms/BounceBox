"""
Main: main_gui.py - Point d'entrée unique pour lancer BounceBox avec Pygame.
"""

import sys
import os

# Garantit que le dossier contenant ce fichier est dans sys.path,
# peu importe depuis où Python est lancé.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


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
        except ImportError as e:
            print(f"❌ {module} - MANQUANT! ({e})")
            tous_presents = False

    return tous_presents


def main():
    """Fonction principale — unique point d'entrée du jeu."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + "  BOUNCEBOX - INTERFACE GRAPHIQUE PYGAME".center(58) + "║")
    print("╚" + "="*58 + "╝")

    print("\n📋 Vérification des dépendances...")
    if not verifier_pygame():
        print("\n❌ Pygame n'est pas disponible. Impossible de continuer.")
        sys.exit(1)

    print("\n📦 Vérification des modules...")
    if not verifier_modules():
        print("\n❌ Certains modules sont manquants.")
        print(f"Répertoire courant : {os.getcwd()}")
        print("Assurez-vous d'être dans le répertoire contenant tous les fichiers .py")
        sys.exit(1)

    print("\n✅ Toutes les dépendances sont OK!\n")

    try:
        from bouncebox_gui import ApplicationGUI
        app = ApplicationGUI(largeur=1000, hauteur=600, fps=60)
        app.lancer()
        print("\n✅ Jeu terminé normalement.")

    except Exception as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
