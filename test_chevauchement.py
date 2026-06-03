#!/usr/bin/env python3
"""
Test spécifique: Vérifier qu'il n'y a AUCUN chevauchement de boules au démarrage

Ce script teste la Solution 1 implémentée.
"""

from bouncebox_tapis import Tapis


def verifier_pas_chevauchement():
    """
    Vérifie qu'aucune boule ne se chevauche au démarrage.
    """
    print("\n" + "="*70)
    print("TEST: Vérification de l'absence de chevauchement de boules")
    print("="*70)
    
    # Créer et initialiser un tapis
    tapis = Tapis(largeur=100, hauteur=50)
    tapis.initialiser_partie()
    
    print(f"\nTapis: {tapis.largeur} x {tapis.hauteur}")
    print(f"Nombre de boules: {tapis.obtenir_nombre_boules()}")
    
    boules = tapis.boules
    print(f"\nBoules créées:")
    for i, boule in enumerate(boules):
        print(f"  {i+1:2d}. {boule.couleur.value:6s} à position ({boule.position.x:.2f}, {boule.position.y:.2f})")
    
    # Vérifier tous les couples de boules
    chevauchements = []
    distances_min = []
    
    print(f"\nVérification des distances entre boules:")
    print("-" * 70)
    
    for i in range(len(boules)):
        for j in range(i + 1, len(boules)):
            boule1 = boules[i]
            boule2 = boules[j]
            
            # Calcul de la distance entre les centres
            distance = (boule1.position - boule2.position).norme()
            
            # Distance minimale = 2 * rayon + marge de sécurité
            rayon_total = boule1.rayon + boule2.rayon
            distance_minimale = rayon_total + 2.0  # Marge de 2.0
            
            distances_min.append((i, j, distance, distance_minimale))
            
            # Vérifier s'il y a chevauchement (rayon total = 2.0 pour deux boules de rayon 1.0)
            if distance < rayon_total + 0.1:  # 0.1 de tolérance
                chevauchements.append((i, j, distance, rayon_total))
                status = "❌ CHEVAUCHEMENT"
            elif distance < distance_minimale:
                status = "⚠️  TRÈS PROCHE"
            else:
                status = "✅ OK"
            
            print(f"Boule {i+1:2d} ↔ Boule {j+2:2d}: "
                  f"distance={distance:6.2f} | min={distance_minimale:6.2f} | {status}")
    
    # Résumé
    print("\n" + "="*70)
    print("RÉSUMÉ")
    print("="*70)
    
    if chevauchements:
        print(f"\n❌ {len(chevauchements)} CHEVAUCHEMENT(S) DÉTECTÉ(S)!")
        for i, j, dist, min_dist in chevauchements:
            print(f"   Boule {i+1} et Boule {j+1}: distance={dist:.2f} < {min_dist:.2f}")
        return False
    else:
        print(f"\n✅ AUCUN CHEVAUCHEMENT DÉTECTÉ!")
        print(f"Toutes les {len(boules)} boules sont bien séparées.")
        
        # Afficher les distances minimales et maximales
        distances = [d[2] for d in distances_min]
        print(f"\nStatistiques des distances:")
        print(f"  Distance minimale: {min(distances):.2f}")
        print(f"  Distance maximale: {max(distances):.2f}")
        print(f"  Distance moyenne: {sum(distances)/len(distances):.2f}")
        
        return True


def tester_plusieurs_parties():
    """
    Lance plusieurs parties pour vérifier la stabilité.
    """
    print("\n" + "="*70)
    print("TEST: Plusieurs initialisations (stabilité)")
    print("="*70)
    
    nombre_tests = 10
    echecs = 0
    
    for test_num in range(nombre_tests):
        tapis = Tapis()
        tapis.initialiser_partie()
        
        # Vérification rapide
        chevauchement_trouve = False
        boules = tapis.boules
        
        for i in range(len(boules)):
            for j in range(i + 1, len(boules)):
                distance = (boules[i].position - boules[j].position).norme()
                if distance < 2.0 + 0.1:  # Rayon total + tolérance
                    chevauchement_trouve = True
                    echecs += 1
                    break
            if chevauchement_trouve:
                break
        
        status = "❌ Chevauchement" if chevauchement_trouve else "✅ OK"
        print(f"Test {test_num+1:2d}/{nombre_tests}: {status}")
    
    print("\n" + "="*70)
    print(f"Résultat: {nombre_tests - echecs}/{nombre_tests} réussis")
    
    if echecs == 0:
        print("✅ TOUS LES TESTS RÉUSSIS!")
        return True
    else:
        print(f"❌ {echecs} ÉCHEC(S)")
        return False


def main():
    """Lance tous les tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  TESTS DE VALIDATION: ABSENCE DE CHEVAUCHEMENT DE BOULES".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "="*68 + "╝")
    
    # Test 1: Vérification détaillée
    resultat1 = verifier_pas_chevauchement()
    
    # Test 2: Stabilité sur plusieurs parties
    resultat2 = tester_plusieurs_parties()
    
    # Résumé final
    print("\n" + "="*70)
    print("RÉSUMÉ FINAL")
    print("="*70)
    
    if resultat1 and resultat2:
        print("\n🎉 ✅ TOUS LES TESTS RÉUSSIS!")
        print("\nConclusion: Les boules ne se chevauchent PAS au démarrage.")
        print("La Solution 1 fonctionne correctement!")
        return 0
    else:
        print("\n❌ CERTAINS TESTS ONT ÉCHOUÉ")
        return 1


if __name__ == "__main__":
    import sys
    exit(main())
