"""
Module: bouncebox_db.py
Persistance des résultats de fin de partie dans la base SQLite.

Utilisation dans bouncebox_gui.py (ApplicationGUI.mettre_a_jour) :
    from bouncebox_db import sauvegarder_partie
    ...
    if self.partie.est_termines() and not self._victoire_jouee:
        sauvegarder_partie(self.partie)   # ← ajouter cette ligne
        ...
"""

import sqlite3
import os
from datetime import date

# Chemins des fichiers (même dossier que les .py)
DB_PATH       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bouncebox.db")
FILL_SQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fill_BDD_bouncebox.sql")


def _connexion():
    """Ouvre et retourne une connexion à la base SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialiser_base():
    """
    Crée les tables si elles n'existent pas encore.
    À appeler au démarrage de l'application (une seule fois).
    """
    conn = _connexion()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS JOUEURS (
            JOUEUR_ID       INTEGER PRIMARY KEY AUTOINCREMENT,
            NOM             TEXT    NOT NULL UNIQUE,
            PARTIES_JOUEES  INTEGER NOT NULL DEFAULT 0,
            PARTIES_GAGNEES INTEGER NOT NULL DEFAULT 0,
            CREATED_AT      TEXT    NOT NULL DEFAULT (date('now'))
        );

        CREATE TABLE IF NOT EXISTS PARTIES (
            PARTIE_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
            DATE_DEBUT  TEXT    NOT NULL,
            NB_COUPS    INTEGER NOT NULL DEFAULT 0,
            ETAT        TEXT    NOT NULL DEFAULT 'en_cours'
                                CHECK (ETAT IN ('en_cours','fin','abandonnee')),
            GAGNANT_ID  INTEGER REFERENCES JOUEURS(JOUEUR_ID)
        );

        CREATE TABLE IF NOT EXISTS PARTICIPATIONS (
            PARTIC_ID   INTEGER PRIMARY KEY AUTOINCREMENT,
            PARTIE_ID   INTEGER NOT NULL REFERENCES PARTIES(PARTIE_ID),
            JOUEUR_ID   INTEGER NOT NULL REFERENCES JOUEURS(JOUEUR_ID),
            COULEUR     TEXT    NOT NULL CHECK (COULEUR IN ('rouge','bleue')),
            SCORE_FINAL INTEGER NOT NULL DEFAULT 0,
            UNIQUE (PARTIE_ID, COULEUR),
            UNIQUE (PARTIE_ID, JOUEUR_ID)
        );
    """)

    conn.commit()
    conn.close()
    print("✅ Base de données prête :", DB_PATH)


def _obtenir_ou_creer_joueur(cur, nom):
    """
    Retourne l'ID du joueur portant ce nom.
    Le crée s'il n'existe pas encore.

    Args:
        cur: curseur SQLite actif
        nom (str): nom du joueur

    Returns:
        int: JOUEUR_ID
    """
    cur.execute("SELECT JOUEUR_ID FROM JOUEURS WHERE NOM = ?", (nom,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO JOUEURS (NOM, PARTIES_JOUEES, PARTIES_GAGNEES, CREATED_AT) "
        "VALUES (?, 0, 0, ?)",
        (nom, date.today().isoformat())
    )
    return cur.lastrowid


def sauvegarder_partie(partie):
    """
    Sauvegarde le résultat d'une partie terminée.
    À appeler une seule fois, quand partie.est_termines() == True.

    Ce qui est persisté :
        - Les deux joueurs (créés s'ils sont nouveaux)
        - La partie : date, nombre de coups, état 'fin', gagnant
        - Les deux participations : couleur + score final
        - Les compteurs PARTIES_JOUEES / PARTIES_GAGNEES de chaque joueur

    Args:
        partie (Partie): instance de bouncebox_partie.Partie en état FIN
    """
    gagnant = partie.obtenir_gagnant()
    if gagnant is None:
        print("⚠️  sauvegarder_partie : pas de gagnant, partie non sauvegardée.")
        return

    nb_coups    = len(partie.historique_coups)
    date_debut  = partie.debut_partie.date().isoformat() if partie.debut_partie else date.today().isoformat()

    conn = _connexion()
    cur  = conn.cursor()

    try:
        # 1. Joueurs
        id_j1 = _obtenir_ou_creer_joueur(cur, partie.joueur1.nom)
        id_j2 = _obtenir_ou_creer_joueur(cur, partie.joueur2.nom)
        id_gagnant = id_j1 if gagnant is partie.joueur1 else id_j2

        # 2. Partie
        cur.execute(
            "INSERT INTO PARTIES (DATE_DEBUT, NB_COUPS, ETAT, GAGNANT_ID) "
            "VALUES (?, ?, 'fin', ?)",
            (date_debut, nb_coups, id_gagnant)
        )
        partie_id = cur.lastrowid

        # 3. Participations
        cur.execute(
            "INSERT INTO PARTICIPATIONS (PARTIE_ID, JOUEUR_ID, COULEUR, SCORE_FINAL) "
            "VALUES (?, ?, ?, ?)",
            (partie_id, id_j1, partie.joueur1.couleur.value, partie.joueur1.score)
        )
        cur.execute(
            "INSERT INTO PARTICIPATIONS (PARTIE_ID, JOUEUR_ID, COULEUR, SCORE_FINAL) "
            "VALUES (?, ?, ?, ?)",
            (partie_id, id_j2, partie.joueur2.couleur.value, partie.joueur2.score)
        )

        # 4. Mise à jour des compteurs joueurs
        cur.execute(
            "UPDATE JOUEURS SET PARTIES_JOUEES = PARTIES_JOUEES + 1 WHERE JOUEUR_ID IN (?, ?)",
            (id_j1, id_j2)
        )
        cur.execute(
            "UPDATE JOUEURS SET PARTIES_GAGNEES = PARTIES_GAGNEES + 1 WHERE JOUEUR_ID = ?",
            (id_gagnant,)
        )

        conn.commit()
        print(f"✅ Partie sauvegardée (id={partie_id}) — "
              f"{gagnant.nom} gagne {partie.joueur1.score}-{partie.joueur2.score} "
              f"en {nb_coups} coups.")

        # Mise à jour du fichier fill_BDD après chaque sauvegarde
        exporter_fill_sql()

    except Exception as e:
        conn.rollback()
        print(f"❌ Erreur lors de la sauvegarde : {e}")

    finally:
        conn.close()


def exporter_fill_sql():
    """
    Régénère fill_BDD_bouncebox.sql avec l'intégralité des données
    actuellement en base. Appelée automatiquement après chaque sauvegarde.
    Le fichier reflète toujours l'état courant de la base.
    """
    conn = _connexion()
    cur  = conn.cursor()

    lignes = []
    lignes.append("-- -----------------------------------------------------------------------------")
    lignes.append("-- Fichier généré automatiquement par bouncebox_db.py")
    lignes.append(f"-- Dernière mise à jour : {date.today().isoformat()}")
    lignes.append("-- -----------------------------------------------------------------------------")
    lignes.append("")
    lignes.append("DELETE PARTICIPATIONS;")
    lignes.append("DELETE PARTIES;")
    lignes.append("DELETE JOUEURS;")

    # --- JOUEURS ---
    cur.execute("SELECT JOUEUR_ID, NOM, PARTIES_JOUEES, PARTIES_GAGNEES, CREATED_AT FROM JOUEURS ORDER BY JOUEUR_ID")
    joueurs = cur.fetchall()
    if joueurs:
        lignes.append("")
        lignes.append("")
        lignes.append("-- table JOUEURS")
        for j in joueurs:
            lignes.append(
                f"insert into JOUEURS values ({j[0]}, '{j[1]}', {j[2]}, {j[3]}, DATE '{j[4]}');"
            )

    # --- PARTIES ---
    cur.execute("SELECT PARTIE_ID, DATE_DEBUT, NB_COUPS, ETAT, GAGNANT_ID FROM PARTIES ORDER BY PARTIE_ID")
    parties = cur.fetchall()
    if parties:
        lignes.append("")
        lignes.append("")
        lignes.append("-- table PARTIES")
        for p in parties:
            gagnant = str(p[4]) if p[4] is not None else "NULL"
            lignes.append(
                f"insert into PARTIES values ({p[0]}, DATE '{p[1]}', {p[2]}, '{p[3]}', {gagnant});"
            )

    # --- PARTICIPATIONS ---
    cur.execute("""
        SELECT pa.PARTIC_ID, pa.PARTIE_ID, pa.JOUEUR_ID, pa.COULEUR, pa.SCORE_FINAL,
               j1.NOM AS nom_rouge, j2.NOM AS nom_bleu
        FROM PARTICIPATIONS pa
        JOIN JOUEURS j1 ON j1.JOUEUR_ID = pa.JOUEUR_ID
        JOIN PARTIES p  ON p.PARTIE_ID  = pa.PARTIE_ID
        JOIN JOUEURS j2 ON j2.JOUEUR_ID = (
            SELECT JOUEUR_ID FROM PARTICIPATIONS
            WHERE PARTIE_ID = pa.PARTIE_ID AND JOUEUR_ID != pa.JOUEUR_ID
            LIMIT 1
        )
        ORDER BY pa.PARTIE_ID, pa.COULEUR DESC
    """)
    participations = cur.fetchall()
    if participations:
        lignes.append("")
        lignes.append("")
        lignes.append("-- table PARTICIPATIONS")
        partie_courante = None
        for pa in participations:
            if pa[1] != partie_courante:
                partie_courante = pa[1]
                lignes.append(f"-- Partie {pa[1]} : {pa[5]} (rouge) vs {pa[6]} (bleu)")
            lignes.append(
                f"insert into PARTICIPATIONS values ({pa[0]}, {pa[1]}, {pa[2]}, '{pa[3]}', {pa[4]});"
            )

    conn.close()

    with open(FILL_SQL_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes) + "\n")

    print(f"✅ fill_BDD_bouncebox.sql mis à jour ({len(parties)} partie(s), {len(joueurs)} joueur(s))")
