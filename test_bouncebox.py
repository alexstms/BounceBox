"""
Module: test_bouncebox.py
Tests unitaires complets pour les classes de BounceBox.

Tests couverts:
- Vecteur2D et opérations vectorielles
- Boules et leurs comportements
- Tapis et gestion des collisions
- Joueurs et gestion de la partie
"""

import unittest
import math
from bouncebox_vecteur import Vecteur2D
from bouncebox_boules import (
    Boule, BouleBlanche, BouleGrise, BouleRouge, BouleBleue, Couleur
)
from bouncebox_tapis import Tapis
from bouncebox_partie import Joueur, Partie, EtatPartie


class TestVecteur2D(unittest.TestCase):
    """Tests pour la classe Vecteur2D."""
    
    def test_creation_vecteur(self):
        """Test 1: Création d'un vecteur avec des coordonnées."""
        v = Vecteur2D(3, 4)
        self.assertEqual(v.x, 3)
        self.assertEqual(v.y, 4)
    
    def test_creation_vecteur_defaut(self):
        """Test 2: Création d'un vecteur par défaut (0, 0)."""
        v = Vecteur2D()
        self.assertEqual(v.x, 0)
        self.assertEqual(v.y, 0)
    
    def test_addition_vecteurs(self):
        """Test 1: Addition de deux vecteurs."""
        v1 = Vecteur2D(3, 4)
        v2 = Vecteur2D(1, 2)
        v3 = v1 + v2
        self.assertEqual(v3.x, 4)
        self.assertEqual(v3.y, 6)
    
    def test_soustraction_vecteurs(self):
        """Test 2: Soustraction de deux vecteurs."""
        v1 = Vecteur2D(5, 7)
        v2 = Vecteur2D(2, 3)
        v3 = v1 - v2
        self.assertEqual(v3.x, 3)
        self.assertEqual(v3.y, 4)
    
    def test_multiplication_scalaire(self):
        """Test 1: Multiplication d'un vecteur par un scalaire."""
        v = Vecteur2D(2, 3)
        v2 = v * 2
        self.assertEqual(v2.x, 4)
        self.assertEqual(v2.y, 6)
    
    def test_multiplication_scalaire_inverse(self):
        """Test 2: Multiplication inversée (scalaire * vecteur)."""
        v = Vecteur2D(2, 3)
        v2 = 2 * v
        self.assertEqual(v2.x, 4)
        self.assertEqual(v2.y, 6)
    
    def test_norme_vecteur(self):
        """Test 1: Calcul de la norme d'un vecteur (3-4-5)."""
        v = Vecteur2D(3, 4)
        self.assertAlmostEqual(v.norme(), 5.0)
    
    def test_norme_zero(self):
        """Test 2: Norme d'un vecteur nul."""
        v = Vecteur2D(0, 0)
        self.assertEqual(v.norme(), 0)
    
    def test_normalisation(self):
        """Test 1: Normalisation d'un vecteur."""
        v = Vecteur2D(3, 4)
        v_norm = v.normalise()
        self.assertAlmostEqual(v_norm.norme(), 1.0)
        self.assertAlmostEqual(v_norm.x, 0.6)
        self.assertAlmostEqual(v_norm.y, 0.8)
    
    def test_normalisation_vecteur_nul(self):
        """Test 2: Normalisation d'un vecteur nul."""
        v = Vecteur2D(0, 0)
        v_norm = v.normalise()
        self.assertEqual(v_norm.x, 0)
        self.assertEqual(v_norm.y, 0)
    
    def test_produit_scalaire(self):
        """Test 1: Produit scalaire de deux vecteurs orthogonaux."""
        v1 = Vecteur2D(1, 0)
        v2 = Vecteur2D(0, 1)
        self.assertEqual(v1.produit_scalaire(v2), 0)
    
    def test_produit_scalaire_paralleles(self):
        """Test 2: Produit scalaire de deux vecteurs parallèles."""
        v1 = Vecteur2D(2, 0)
        v2 = Vecteur2D(3, 0)
        self.assertEqual(v1.produit_scalaire(v2), 6)
    
    def test_egalite_vecteurs(self):
        """Test 1: Égalité de deux vecteurs identiques."""
        v1 = Vecteur2D(1.0, 2.0)
        v2 = Vecteur2D(1.0, 2.0)
        self.assertEqual(v1, v2)
    
    def test_inegalite_vecteurs(self):
        """Test 2: Inégalité de deux vecteurs différents."""
        v1 = Vecteur2D(1.0, 2.0)
        v2 = Vecteur2D(1.1, 2.0)
        self.assertNotEqual(v1, v2)


class TestBoules(unittest.TestCase):
    """Tests pour les classes de boules."""
    
    def test_creation_boule_blanche(self):
        """Test 1: Création d'une boule blanche."""
        pos = Vecteur2D(10, 10)
        boule = BouleBlanche(pos)
        self.assertEqual(boule.couleur, Couleur.BLANCHE)
        self.assertEqual(boule.position, pos)
    
    def test_creation_boule_grise(self):
        """Test 2: Création d'une boule grise."""
        pos = Vecteur2D(20, 20)
        boule = BouleGrise(pos)
        self.assertEqual(boule.couleur, Couleur.GRISE)
        self.assertEqual(boule.position, pos)
    
    def test_deplacement_boule(self):
        """Test 1: Déplacement d'une boule avec vitesse."""
        pos = Vecteur2D(0, 0)
        boule = BouleBlanche(pos)
        boule.vitesse = Vecteur2D(5, 0)
        boule.deplacer(1.0)
        # Avec résistance, vitesse * 0.98
        self.assertAlmostEqual(boule.position.x, 5.0)
        self.assertAlmostEqual(boule.position.y, 0.0)
    
    def test_deplacement_avec_resistance(self):
        """Test 2: Vérification que la résistance s'applique correctement."""
        boule = BouleBlanche(Vecteur2D(0, 0))
        boule.vitesse = Vecteur2D(10, 0)
        vitesse_initiale = boule.vitesse.norme()
        boule.deplacer(1.0)
        vitesse_apres = boule.vitesse.norme()
        # La vitesse doit être réduite par la résistance
        self.assertLess(vitesse_apres, vitesse_initiale)
    
    def test_distance_entre_boules(self):
        """Test 1: Calcul de distance entre deux boules."""
        boule1 = BouleBlanche(Vecteur2D(0, 0))
        boule2 = BouleGrise(Vecteur2D(3, 4))
        distance = boule1.distance_avec(boule2)
        self.assertAlmostEqual(distance, 5.0)
    
    def test_collision_detection(self):
        """Test 2: Détection de collision entre deux boules."""
        boule1 = BouleBlanche(Vecteur2D(0, 0))
        boule2 = BouleGrise(Vecteur2D(1.5, 0))
        # Les boules se chevauchent (2 * rayon = 2)
        self.assertTrue(boule1.en_collision_avec(boule2))
    
    def test_pas_collision(self):
        """Test 2b: Pas de collision quand les boules sont éloignées."""
        boule1 = BouleBlanche(Vecteur2D(0, 0))
        boule2 = BouleGrise(Vecteur2D(10, 0))
        self.assertFalse(boule1.en_collision_avec(boule2))
    
    def test_changement_couleur_boule_grise(self):
        """Test 1: Changement de couleur d'une boule grise."""
        boule = BouleGrise(Vecteur2D(10, 10))
        self.assertEqual(boule.couleur, Couleur.GRISE)
        boule.changer_couleur(Couleur.ROUGE)
        self.assertEqual(boule.couleur, Couleur.ROUGE)
    
    def test_application_force(self):
        """Test 2: Application d'une force à une boule."""
        boule = BouleBlanche(Vecteur2D(0, 0))
        force = Vecteur2D(5, 0)
        boule.appliquer_force(force)
        self.assertEqual(boule.vitesse, force)
        self.assertTrue(boule.en_mouvement)
    
    def test_rebound_bordure_horizontale(self):
        """Test 1: Rebond sur une bordure horizontale."""
        boule = BouleBlanche(Vecteur2D(0.5, 25))
        boule.vitesse = Vecteur2D(-10, 0)
        boule.rebound_bordure(100, 50)
        # La boule devrait rebondir vers la droite
        self.assertGreater(boule.vitesse.x, 0)
    
    def test_rebound_bordure_verticale(self):
        """Test 2: Rebond sur une bordure verticale."""
        boule = BouleBlanche(Vecteur2D(50, 0.5))
        boule.vitesse = Vecteur2D(0, -10)
        boule.rebound_bordure(100, 50)
        # La boule devrait rebondir vers le haut
        self.assertGreater(boule.vitesse.y, 0)


class TestTapis(unittest.TestCase):
    """Tests pour la classe Tapis."""
    
    def test_creation_tapis(self):
        """Test 1: Création d'un tapis avec dimensions."""
        tapis = Tapis(100, 50)
        self.assertEqual(tapis.largeur, 100)
        self.assertEqual(tapis.hauteur, 50)
    
    def test_initialisation_partie(self):
        """Test 2: Initialisation du tapis avec les boules."""
        tapis = Tapis()
        tapis.initialiser_partie()
        # 1 blanche + 9 grises + 2 bleues = 12 boules
        self.assertEqual(tapis.obtenir_nombre_boules(), 12)
    
    def test_boule_blanche_unique(self):
        """Test 1: Vérification qu'il n'y a qu'une boule blanche."""
        tapis = Tapis()
        tapis.initialiser_partie()
        blanches = tapis.obtenir_boules_par_couleur(Couleur.BLANCHE)
        self.assertEqual(len(blanches), 1)
    
    def test_obtenir_boules_par_couleur(self):
        """Test 2: Récupération des boules par couleur."""
        tapis = Tapis()
        tapis.initialiser_partie()
        rouges = tapis.obtenir_boules_par_couleur(Couleur.ROUGE)
        # Au démarrage, pas de boules rouges
        self.assertEqual(len(rouges), 0)
    
    def test_mise_a_jour_tapis(self):
        """Test 1: Mise à jour du tapis et déplacement des boules."""
        tapis = Tapis()
        tapis.initialiser_partie()
        boule_blanche = tapis.obtenir_boule_blanche()
        boule_blanche.appliquer_force(Vecteur2D(5, 0))
        
        pos_avant = boule_blanche.position.copie()
        tapis.mettre_a_jour(1.0)
        pos_apres = boule_blanche.position
        
        # La boule doit s'être déplacée
        self.assertNotEqual(pos_avant, pos_apres)
    
    def test_boules_immobiles(self):
        """Test 2: Vérification de l'état d'immobilité des boules."""
        tapis = Tapis()
        tapis.initialiser_partie()
        # Au démarrage, toutes les boules sont immobiles
        self.assertTrue(tapis.toutes_boules_immobiles())
        
        boule_blanche = tapis.obtenir_boule_blanche()
        boule_blanche.appliquer_force(Vecteur2D(10, 0))
        # Après lancer, ce n'est plus vrai
        self.assertFalse(tapis.toutes_boules_immobiles())
    
    def test_retirer_boule(self):
        """Test 1: Retrait d'une boule du tapis."""
        tapis = Tapis()
        tapis.initialiser_partie()
        nombre_initial = tapis.obtenir_nombre_boules()
        
        boules = tapis.obtenir_boules_par_couleur(Couleur.GRISE)
        if boules:
            tapis.retirer_boule(boules[0])
            self.assertEqual(tapis.obtenir_nombre_boules(), nombre_initial - 1)
    
    def test_reinitialiser_boule_blanche(self):
        """Test 2: Réinitialisation de la boule blanche."""
        tapis = Tapis()
        tapis.initialiser_partie()
        boule_blanche = tapis.obtenir_boule_blanche()
        
        pos_initial = boule_blanche.position.copie()
        boule_blanche.appliquer_force(Vecteur2D(10, 10))
        tapis.reinitialiser_boule_blanche()
        
        # La boule doit être revenue à sa position initiale
        self.assertEqual(boule_blanche.position, pos_initial)
        self.assertEqual(boule_blanche.vitesse, Vecteur2D(0, 0))


class TestPartie(unittest.TestCase):
    """Tests pour les classes Joueur et Partie."""
    
    def test_creation_joueur(self):
        """Test 1: Création d'un joueur."""
        joueur = Joueur("Alice", Couleur.ROUGE)
        self.assertEqual(joueur.nom, "Alice")
        self.assertEqual(joueur.couleur, Couleur.ROUGE)
        self.assertEqual(joueur.score, 0)
    
    def test_incrementer_score_joueur(self):
        """Test 2: Incrémentation du score d'un joueur."""
        joueur = Joueur("Bob", Couleur.BLEUE)
        joueur.incrementer_score()
        joueur.incrementer_score()
        self.assertEqual(joueur.score, 2)
    
    def test_victoire_joueur(self):
        """Test 1: Vérification de la victoire (5 points)."""
        joueur = Joueur("Charlie", Couleur.ROUGE)
        for _ in range(5):
            joueur.incrementer_score()
        self.assertTrue(joueur.a_gagne())
    
    def test_pas_victoire(self):
        """Test 2: Vérification de non-victoire avant 5 points."""
        joueur = Joueur("Diana", Couleur.BLEUE)
        joueur.incrementer_score()
        self.assertFalse(joueur.a_gagne())
    
    def test_temps_tour(self):
        """Test 1: Gestion du temps de tour."""
        joueur = Joueur("Eve", Couleur.ROUGE)
        temps_initial = joueur.temps_restant_tour
        joueur.decrementer_temps(10)
        self.assertEqual(joueur.temps_restant_tour, temps_initial - 10)
    
    def test_temps_ecoule(self):
        """Test 2: Vérification du temps écoulé."""
        joueur = Joueur("Frank", Couleur.BLEUE)
        joueur.temps_restant_tour = 0.5
        self.assertFalse(joueur.temps_ecoule())
        joueur.decrementer_temps(1)
        self.assertTrue(joueur.temps_ecoule())
    
    def test_creation_partie(self):
        """Test 1: Création d'une partie."""
        partie = Partie("Alice", "Bob")
        self.assertEqual(partie.joueur1.nom, "Alice")
        self.assertEqual(partie.joueur2.nom, "Bob")
        self.assertEqual(partie.etat, EtatPartie.DEBUT)
    
    def test_demarrage_partie(self):
        """Test 2: Démarrage d'une partie."""
        partie = Partie("Charlie", "Diana")
        partie.demarrer()
        self.assertEqual(partie.etat, EtatPartie.EN_COURS)
        self.assertEqual(partie.tapis.obtenir_nombre_boules(), 12)
    
    def test_joueur_actif_initial(self):
        """Test 1: Vérification du joueur actif initial."""
        partie = Partie("Eve", "Frank")
        # Le joueur rouge commence toujours
        self.assertEqual(partie.joueur_actif.couleur, Couleur.ROUGE)
    
    def test_changement_joueur_actif(self):
        """Test 2: Changement du joueur actif."""
        partie = Partie("George", "Hanna")
        joueur1_initial = partie.joueur_actif
        partie.changer_joueur_actif()
        self.assertNotEqual(partie.joueur_actif, joueur1_initial)
    
    def test_lancer_coup(self):
        """Test 1: Lancer un coup (tir)."""
        partie = Partie("Isaac", "Julia")
        partie.demarrer()
        result = partie.lancer_coup(0, 5)
        self.assertTrue(result)
        self.assertTrue(partie.coup_lance)
    
    def test_un_coup_par_tour(self):
        """Test 2: Vérification qu'un seul coup peut être lancé par tour."""
        partie = Partie("Kevin", "Laura")
        partie.demarrer()
        partie.lancer_coup(0, 5)
        result = partie.lancer_coup(math.pi/2, 5)
        self.assertFalse(result)  # Deuxième coup doit être refusé


def run_tests():
    """Lance tous les tests unitaires."""
    # Créer une suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Ajouter tous les tests
    suite.addTests(loader.loadTestsFromTestCase(TestVecteur2D))
    suite.addTests(loader.loadTestsFromTestCase(TestBoules))
    suite.addTests(loader.loadTestsFromTestCase(TestTapis))
    suite.addTests(loader.loadTestsFromTestCase(TestPartie))
    
    # Exécuter les tests avec un niveau de verbosité élevé
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Afficher un résumé
    print("\n" + "="*70)
    print("RÉSUMÉ DES TESTS")
    print("="*70)
    print(f"Tests exécutés: {result.testsRun}")
    print(f"Succès: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Échecs: {len(result.failures)}")
    print(f"Erreurs: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
