-- -----------------------------------------------------------------------------
-- Fichier généré automatiquement par bouncebox_db.py
-- Dernière mise à jour : 2026-06-03
-- -----------------------------------------------------------------------------

DELETE PARTICIPATIONS;
DELETE PARTIES;
DELETE JOUEURS;


-- table JOUEURS
insert into JOUEURS values (1, 'Hadrien', 1, 0, DATE '2026-06-03');
insert into JOUEURS values (2, 'Alex', 1, 1, DATE '2026-06-03');


-- table PARTIES
insert into PARTIES values (1, DATE '2026-06-03', 10, 'fin', 2);


-- table PARTICIPATIONS
-- Partie 1 : Hadrien (rouge) vs Alex (bleu)
insert into PARTICIPATIONS values (1, 1, 1, 'rouge', 3, 5);
insert into PARTICIPATIONS values (2, 1, 2, 'bleue', 5, 5);
