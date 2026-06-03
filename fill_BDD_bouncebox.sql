-- -----------------------------------------------------------------------------
-- Fichier généré automatiquement par bouncebox_db.py
-- Dernière mise à jour : 2026-06-02
-- -----------------------------------------------------------------------------

DELETE PARTICIPATIONS;
DELETE PARTIES;
DELETE JOUEURS;


-- table JOUEURS
insert into JOUEURS values (1, 'A', 1, 0, DATE '2026-06-02');
insert into JOUEURS values (2, 'B', 1, 1, DATE '2026-06-02');


-- table PARTIES
insert into PARTIES values (1, DATE '2026-06-02', 10, 'fin', 2);


-- table PARTICIPATIONS
-- Partie 1 : A (rouge) vs B (bleu)
insert into PARTICIPATIONS values (1, 1, 1, 'rouge', 2);
insert into PARTICIPATIONS values (2, 1, 2, 'bleue', 5);
