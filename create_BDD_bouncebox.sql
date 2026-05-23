-- -----------------------------------------------------------------------------
--             Génération d'une base de données pour
--                      Oracle Version 10g
--                        (23/5/2026)
-- -----------------------------------------------------------------------------
--      Nom de la base : basebouncebox
--      Projet : BounceBoxv1
--      Auteur : BounceBox
-- -----------------------------------------------------------------------------

DROP TABLE PARTICIPATIONS CASCADE CONSTRAINTS;
DROP TABLE PARTIES        CASCADE CONSTRAINTS;
DROP TABLE JOUEURS        CASCADE CONSTRAINTS;


-- -----------------------------------------------------------------------------
--       TABLE : JOUEURS
-- -----------------------------------------------------------------------------

CREATE TABLE JOUEURS
   (
    JOUEUR_ID       NUMBER(4)    NOT NULL,
    NOM             VARCHAR2(16) NOT NULL,
    PARTIES_JOUEES  NUMBER(4)    DEFAULT 0,
    PARTIES_GAGNEES NUMBER(4)    DEFAULT 0,
    CREATED_AT      DATE         DEFAULT SYSDATE
,   CONSTRAINT PK_JOUEURS        PRIMARY KEY (JOUEUR_ID)
,   CONSTRAINT UQ_JOUEURS_NOM    UNIQUE      (NOM)
   ) ;


-- -----------------------------------------------------------------------------
--       TABLE : PARTIES
-- -----------------------------------------------------------------------------

CREATE TABLE PARTIES
   (
    PARTIE_ID       NUMBER(6)    NOT NULL,
    DATE_DEBUT      DATE         NOT NULL,
    NB_COUPS        NUMBER(4)    DEFAULT 0,
    ETAT            VARCHAR2(10) DEFAULT 'en_cours',
    GAGNANT_ID      NUMBER(4)    NULL
,   CONSTRAINT PK_PARTIES        PRIMARY KEY (PARTIE_ID)
,   CONSTRAINT CK_PARTIES_ETAT   CHECK (ETAT IN ('en_cours','fin','abandonnee'))
   ) ;


-- -----------------------------------------------------------------------------
--       TABLE : PARTICIPATIONS
-- -----------------------------------------------------------------------------

CREATE TABLE PARTICIPATIONS
   (
    PARTIC_ID       NUMBER(6)   NOT NULL,
    PARTIE_ID       NUMBER(6)   NOT NULL,
    JOUEUR_ID       NUMBER(4)   NOT NULL,
    COULEUR         VARCHAR2(6) NOT NULL,
    SCORE_FINAL     NUMBER(2)   DEFAULT 0
,   CONSTRAINT PK_PARTICIPATIONS    PRIMARY KEY (PARTIC_ID)
,   CONSTRAINT CK_PARTIC_COULEUR    CHECK (COULEUR IN ('rouge','bleue'))
,   CONSTRAINT UQ_PARTIE_COULEUR    UNIQUE (PARTIE_ID, COULEUR)
,   CONSTRAINT UQ_PARTIE_JOUEUR     UNIQUE (PARTIE_ID, JOUEUR_ID)
   ) ;


-- -----------------------------------------------------------------------------
--       INDEX DES TABLES
-- -----------------------------------------------------------------------------

CREATE INDEX I_FK_PARTIES_GAGNANT
     ON PARTIES (GAGNANT_ID ASC) ;

CREATE INDEX I_FK_PARTIC_PARTIE
     ON PARTICIPATIONS (PARTIE_ID ASC) ;

CREATE INDEX I_FK_PARTIC_JOUEUR
     ON PARTICIPATIONS (JOUEUR_ID ASC) ;


-- -----------------------------------------------------------------------------
--       CRÉATION DES RÉFÉRENCES DE TABLE
-- -----------------------------------------------------------------------------

ALTER TABLE PARTIES ADD (
     CONSTRAINT FK_PARTIES_GAGNANT
          FOREIGN KEY (GAGNANT_ID)
               REFERENCES JOUEURS (JOUEUR_ID)) ;

ALTER TABLE PARTICIPATIONS ADD (
     CONSTRAINT FK_PARTIC_PARTIE
          FOREIGN KEY (PARTIE_ID)
               REFERENCES PARTIES (PARTIE_ID)) ;

ALTER TABLE PARTICIPATIONS ADD (
     CONSTRAINT FK_PARTIC_JOUEUR
          FOREIGN KEY (JOUEUR_ID)
               REFERENCES JOUEURS (JOUEUR_ID)) ;


-- -----------------------------------------------------------------------------
--                FIN DE GENERATION
-- -----------------------------------------------------------------------------
