-- -----------------------------------------------------------------------------
-- Fichier généré automatiquement par bouncebox_db.py
-- Dernière mise à jour : 2026-05-23
-- -----------------------------------------------------------------------------

DELETE PARTICIPATIONS;
DELETE PARTIES;
DELETE JOUEURS;


-- table JOUEURS
insert into JOUEURS values (1, 'TEST1', 1, 1, DATE '2026-05-23');
insert into JOUEURS values (2, 'TEST2', 1, 0, DATE '2026-05-23');
insert into JOUEURS values (3, 'TEST3', 1, 0, DATE '2026-05-23');
insert into JOUEURS values (4, 'TEST4', 1, 1, DATE '2026-05-23');


-- table PARTIES
insert into PARTIES values (1, DATE '2026-05-23', 19, 'fin', 1);
insert into PARTIES values (2, DATE '2026-05-23', 14, 'fin', 4);


-- table PARTICIPATIONS
-- Partie 1 : TEST1 (rouge) vs TEST2 (bleu)
insert into PARTICIPATIONS values (1, 1, 1, 'rouge', 5);
insert into PARTICIPATIONS values (2, 1, 2, 'bleue', 3);
-- Partie 2 : TEST3 (rouge) vs TEST4 (bleu)
insert into PARTICIPATIONS values (3, 2, 3, 'rouge', 0);
insert into PARTICIPATIONS values (4, 2, 4, 'bleue', 5);
