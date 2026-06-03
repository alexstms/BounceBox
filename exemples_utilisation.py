"""
Module: exemples_utilisation.py
Exemples d'utilisation du projet BounceBox.

Cet exemple montre comment utiliser les classes principales pour créer et
lancer une partie simple.
"""

import math
from bouncebox_vecteur import Vecteur2D
from bouncebox_boules import Couleur, BouleBlanche, BouleGrise
from bouncebox_tapis import Tapis
from bouncebox_partie import Joueur, Partie


def exemple_1_vecteurs():
    """Exemple 1: Opérations vectorielles basiques."""
    print("=" * 60)
    print("EXEMPLE 1: Opérations vectorielles")
    print("=" * 60)
    
    # Créer deux vecteurs
    v1 = Vecteur2D(3, 4)
    v2 = Vecteur2D(1, 2)
    
    print(f"v1 = {v1}")
    print(f"v2 = {v2}")
    print(f"v1 + v2 = {v1 + v2}")
    print(f"v1 - v2 = {v1 - v2}")
    print(f"v1 * 2 = {v1 * 2}")
    print(f"Norme de v1 = {v1.norme()}")
    print(f"v1 normalisé = {v1.normalise()}")
    print(f"Produit scalaire v1 · v2 = {v1.produit_scalaire(v2)}")
    print()


def exemple_2_boules():
    """Exemple 2: Création et déplacement de boules."""
    print("=" * 60)
    print("EXEMPLE 2: Boules et mouvements")
    print("=" * 60)
    
    # Créer des boules
    boule_blanche = BouleBlanche(Vecteur2D(10, 10))
    boule_grise = BouleGrise(Vecteur2D(20, 10))
    
    print(f"Boule blanche: {boule_blanche}")
    print(f"Boule grise: {boule_grise}")
    
    # Appliquer une force (vitesse initiale)
    boule_blanche.appliquer_force(Vecteur2D(5, 0))
    print(f"\nAprès application d'une force de (5, 0):")
    print(f"Vitesse: {boule_blanche.vitesse}")
    print(f"En mouvement: {boule_blanche.en_mouvement}")
    
    # Simuler plusieurs déplacements
    print("\nDéplacements successifs (avec résistance):")
    for i in range(5):
        boule_blanche.deplacer(1.0)
        print(f"  Itération {i+1}: position={boule_blanche.position}, "
              f"vitesse={boule_blanche.vitesse.norme():.2f}")
    
    # Vérifier les collisions
    distance = boule_blanche.distance_avec(boule_grise)
    print(f"\nDistance entre boules: {distance:.2f}")
    print(f"En collision: {boule_blanche.en_collision_avec(boule_grise)}")
    print()


def exemple_3_tapis():
    """Exemple 3: Utilisation du tapis."""
    print("=" * 60)
    print("EXEMPLE 3: Gestion du tapis")
    print("=" * 60)
    
    # Créer et initialiser un tapis
    tapis = Tapis(100, 50)
    tapis.initialiser_partie()
    
    print(f"Tapis créé: {tapis}")
    print(f"Nombre de boules: {tapis.obtenir_nombre_boules()}")
    
    # Compter les boules par couleur
    blanches = tapis.obtenir_boules_par_couleur(Couleur.BLANCHE)
    grises = tapis.obtenir_boules_par_couleur(Couleur.GRISE)
    bleues = tapis.obtenir_boules_par_couleur(Couleur.BLEUE)
    
    print(f"  - Boules blanches: {len(blanches)}")
    print(f"  - Boules grises: {len(grises)}")
    print(f"  - Boules bleues: {len(bleues)}")
    
    # Toutes les boules sont immobiles au départ
    print(f"\nToutes boules immobiles: {tapis.toutes_boules_immobiles()}")
    
    # Appliquer une force à la boule blanche
    boule_blanche = tapis.obtenir_boule_blanche()
    boule_blanche.appliquer_force(Vecteur2D(5, 0))
    
    print(f"Après lancer de la boule blanche:")
    print(f"  Toutes boules immobiles: {tapis.toutes_boules_immobiles()}")
    
    # Simuler quelques frames
    for _ in range(10):
        tapis.mettre_a_jour(delta_t=0.1)
    
    print(f"Après 10 updates:")
    print(f"  Boules en mouvement: {len(tapis.obtenir_boules_en_mouvement())}")
    print()


def exemple_4_joueur():
    """Exemple 4: Gestion des joueurs."""
    print("=" * 60)
    print("EXEMPLE 4: Joueurs et scores")
    print("=" * 60)
    
    # Créer deux joueurs
    alice = Joueur("Alice", Couleur.ROUGE)
    bob = Joueur("Bob", Couleur.BLEUE)
    
    print(f"Joueur 1: {alice}")
    print(f"Joueur 2: {bob}")
    
    # Gérer les scores
    print("\nJeu de 5 points (premier à 5 gagne):")
    print(f"Points nécessaires: {alice.POINTS_VICTOIRE}")
    
    # Simuler Alice gagnant des points
    for i in range(1, 6):
        alice.incrementer_score()
        print(f"  Alice marque le point {i}: score={alice.score}, "
              f"a gagné={alice.a_gagne()}")
        if alice.a_gagne():
            print(f"  → Alice remporte la partie!")
            break
    
    # Gestion du temps
    print(f"\nGestion du temps (limite: {bob.TEMPS_TOUR}s par tour):")
    bob.reinitialiser_temps_tour()
    print(f"  Temps restant: {bob.temps_restant_tour}s")
    
    bob.decrementer_temps(20)
    print(f"  Après 20s: temps restant={bob.temps_restant_tour}s")
    print(f"  Temps écoulé: {bob.temps_ecoule()}")
    print()


def exemple_5_partie():
    """Exemple 5: Simulation complète d'une partie."""
    print("=" * 60)
    print("EXEMPLE 5: Partie complète")
    print("=" * 60)
    
    # Créer une partie
    partie = Partie("Alice", "Bob")
    print(f"Partie créée: {partie}")
    print(f"État initial: {partie.etat.value}")
    
    # Démarrer
    partie.demarrer()
    print(f"État après démarrage: {partie.etat.value}")
    print(f"Joueur actif: {partie.joueur_actif.nom} ({partie.joueur_actif.couleur.value})")
    
    # Information sur le tapis
    tapis = partie.tapis
    print(f"Tapis: {tapis}")
    print(f"Nombre de boules: {tapis.obtenir_nombre_boules()}")
    
    # Simuler un coup
    print("\n--- Simulation du coup du joueur actif ---")
    angle = math.pi / 6  # 30 degrés
    force = 5.0
    
    print(f"Angle: {angle:.2f} rad ({math.degrees(angle):.1f}°)")
    print(f"Force: {force}")
    
    success = partie.lancer_coup(angle, force)
    print(f"Coup lancé avec succès: {success}")
    
    # Simuler quelques frames
    print("\nSimulation physique (50 frames):")
    for frame in range(50):
        partie.mettre_a_jour(delta_t=0.016)  # 60 FPS
        
        if frame % 10 == 0 or frame == 1:
            en_mouvement = len(tapis.obtenir_boules_en_mouvement())
            print(f"  Frame {frame}: {en_mouvement} boules en mouvement")
    
    print(f"\nAprès simulation:")
    print(f"Toutes boules immobiles: {tapis.toutes_boules_immobiles()}")
    print(f"Temps de partie écoulé: {partie.obtenir_temps_partie():.2f}s")
    print()


def exemple_6_scenario_complet():
    """Exemple 6: Scenario de partie plus complet."""
    print("=" * 60)
    print("EXEMPLE 6: Scenario complet (test rapide)")
    print("=" * 60)
    
    partie = Partie("Joueur 1", "Joueur 2")
    partie.demarrer()
    
    tours = 0
    max_tours = 3  # Limiter pour la démo
    
    while not partie.est_termines() and tours < max_tours:
        tours += 1
        joueur = partie.joueur_actif
        print(f"\n--- Tour {tours}: {joueur.nom} joue ---")
        
        # Lancer un coup aléatoire
        angle = (tours * math.pi / 6) % (2 * math.pi)
        force = 3.0 + tours
        
        partie.lancer_coup(angle, force)
        print(f"Coup lancé: angle={angle:.2f}, force={force:.1f}")
        
        # Simuler jusqu'à immobilité
        frames = 0
        max_frames = 200
        while not partie.tapis.toutes_boules_immobiles() and frames < max_frames:
            partie.mettre_a_jour(0.016)
            frames += 1
        
        print(f"Boules immobiles après {frames} frames")
        print(f"Scores: {joueur.nom}={joueur.score}, "
              f"{partie.joueur_inactif.nom}={partie.joueur_inactif.score}")
        
        # Simuler un changement de joueur (dans un jeu réel, après analyse des points)
        if not partie.est_termines():
            partie.changer_joueur_actif()
    
    if partie.est_termines():
        gagnant = partie.obtenir_gagnant()
        print(f"\n🎉 Partie terminée! Gagnant: {gagnant.nom}")
    else:
        print(f"\nSimulation arrêtée après {max_tours} tours")
    
    print()


def main():
    """Lance tous les exemples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  BOUNCEBOX - EXEMPLES D'UTILISATION".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Exécuter tous les exemples
    exemple_1_vecteurs()
    exemple_2_boules()
    exemple_3_tapis()
    exemple_4_joueur()
    exemple_5_partie()
    exemple_6_scenario_complet()
    
    print("=" * 60)
    print("Fin des exemples")
    print("=" * 60)


if __name__ == "__main__":
    main()
