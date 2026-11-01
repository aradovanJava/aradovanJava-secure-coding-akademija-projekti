/* Kadrovska – shema i početni podaci (preslika aplikacije iz 2. tjedna, SQL Server 2022).
   Pokreće je init.sh samo ako baza ne postoji. */
SET NOCOUNT ON;
CREATE DATABASE [Kadrovska];
GO
USE [Kadrovska];
GO
CREATE TABLE dbo.korisnici (
    id            BIGINT IDENTITY(1,1) PRIMARY KEY,
    username      NVARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(100)  NOT NULL,
    email         NVARCHAR(120) NULL,
    ime           NVARCHAR(60)  NULL,
    prezime       NVARCHAR(60)  NULL,
    uloga         VARCHAR(20)   NOT NULL,
    oib           VARCHAR(11)   NULL
);
CREATE TABLE dbo.reset_tokeni (
    id         BIGINT IDENTITY(1,1) PRIMARY KEY,
    username   NVARCHAR(50)  NOT NULL,
    token      VARCHAR(128)  NOT NULL,
    istjece    DATETIME2(0)  NULL,
    iskoristen BIT           NOT NULL DEFAULT 0
);
CREATE TABLE dbo.postavke (
    username   NVARCHAR(50) PRIMARY KEY,
    podsjetnik BIT          NOT NULL,
    sati_prije INT          NOT NULL,
    kanal      VARCHAR(20)  NOT NULL
);
CREATE TABLE dbo.zaposlenici (
    id      BIGINT IDENTITY(1,1) PRIMARY KEY,
    ime     NVARCHAR(60)  NOT NULL,
    prezime NVARCHAR(60)  NOT NULL,
    odjel   NVARCHAR(80)  NOT NULL,
    email   NVARCHAR(120) NOT NULL
);
-- Zahtjevi za godišnji odmor (razdoblje datum_od – datum_do).
CREATE TABLE dbo.zahtjevi (
    id         BIGINT IDENTITY(1,1) PRIMARY KEY,
    zaposlenik NVARCHAR(50)  NOT NULL,
    datum_od   DATE          NOT NULL,
    datum_do   DATE          NOT NULL,
    razlog     NVARCHAR(500) NOT NULL,
    oib        VARCHAR(11)   NULL,
    status     VARCHAR(20)   NOT NULL,
    kreirano   DATETIME2(0)  NOT NULL DEFAULT SYSDATETIME()
);
CREATE TABLE dbo.platne_liste (
    id         BIGINT IDENTITY(1,1) PRIMARY KEY,
    zaposlenik NVARCHAR(50)  NOT NULL,
    razdoblje  VARCHAR(7)    NOT NULL,
    datoteka   NVARCHAR(200) NOT NULL
);
CREATE TABLE dbo.edukacije (
    id          BIGINT IDENTITY(1,1) PRIMARY KEY,
    naziv       NVARCHAR(200) NOT NULL,
    datum       DATE          NOT NULL,
    kapacitet   INT           NOT NULL,
    prijavljeno INT           NOT NULL DEFAULT 0
);
CREATE TABLE dbo.prijave_edukacije (
    id           BIGINT IDENTITY(1,1) PRIMARY KEY,
    edukacija_id BIGINT       NOT NULL REFERENCES dbo.edukacije (id),
    zaposlenik   NVARCHAR(50) NOT NULL,
    kreirano     DATETIME2(0) NOT NULL DEFAULT SYSDATETIME(),
    oznaka_lms   VARCHAR(40)  NULL
);
-- Dnevnik promjena nad zahtjevima (puni ga okidač; služi za reviziju i radne sporove).
CREATE TABLE dbo.revizija (
    id         BIGINT IDENTITY(1,1) PRIMARY KEY,
    vrijeme    DATETIME2(3)  NOT NULL DEFAULT SYSUTCDATETIME(),
    tablica    SYSNAME       NOT NULL,
    radnja     VARCHAR(10)   NOT NULL,
    zapis_id   BIGINT        NOT NULL,
    vlasnik    NVARCHAR(50)  NULL,
    prijava    NVARCHAR(128) NOT NULL DEFAULT ORIGINAL_LOGIN(),
    korisnik   NVARCHAR(50)  NULL DEFAULT CAST(SESSION_CONTEXT(N'korisnik') AS NVARCHAR(50))
);
GO
CREATE TRIGGER dbo.trg_zahtjevi_revizija ON dbo.zahtjevi
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.revizija (tablica, radnja, zapis_id, vlasnik)
    SELECT N'zahtjevi',
           CASE WHEN d.id IS NULL THEN 'INSERT' WHEN i.id IS NULL THEN 'DELETE' ELSE 'UPDATE' END,
           COALESCE(i.id, d.id), COALESCE(i.zaposlenik, d.zaposlenik)
    FROM inserted AS i
    FULL OUTER JOIN deleted AS d ON d.id = i.id;
END;
GO
-- Lozinke: aplikacija ih je spremala kao nesoljeni SHA-256 (naslijeđeni kod).
INSERT INTO dbo.korisnici (username, password_hash, email, ime, prezime, uloga, oib) VALUES
 (N'ana',      LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Ana12345!'), 2)),       N'ana@primjer.hr',      N'Ana',      N'Anić',  'KORISNIK', '48291736504'),
 (N'marko',    LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Marko12345!'), 2)),     N'marko@primjer.hr',    N'Marko',    N'Marić', 'KORISNIK', '73019485267'),
 (N'voditelj', LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Ovlasteni12345!'), 2)), N'voditelj@primjer.hr', N'Tomislav', N'Tomić', 'VODITELJ', '50617283940'),
 (N'admin',    LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Admin12345!'), 2)),     N'admin@primjer.hr',    N'Ivana',    N'Admin', 'ADMIN',    '61728394051');

INSERT INTO dbo.postavke (username, podsjetnik, sati_prije, kanal) VALUES
 (N'ana', 1, 24, 'EMAIL'), (N'marko', 0, 2, 'SMS');

INSERT INTO dbo.zaposlenici (ime, prezime, odjel, email) VALUES
 (N'Ana', N'Anić', N'Financije', N'ana@primjer.hr'),
 (N'Marko', N'Marić', N'Prodaja', N'marko@primjer.hr'),
 (N'Tomislav', N'Tomić', N'Ljudski potencijali', N'voditelj@primjer.hr'),
 (N'Lucija', N'Babić', N'Informatika', N'lucija.babic@primjer.hr'),
 (N'Davor', N'Jurić', N'Informatika', N'davor.juric@primjer.hr'),
 (N'Sanja', N'Horvat', N'Pravna služba', N'sanja.horvat@primjer.hr'),
 (N'Ivan', N'Zorić', N'Prodaja', N'ivan.zoric@primjer.hr'),
 (N'Maja', N'Vidović', N'Financije', N'maja.vidovic@primjer.hr');

INSERT INTO dbo.zahtjevi (zaposlenik, datum_od, datum_do, razlog, oib, status) VALUES
 (N'ana',   '2026-12-21', '2026-12-31', N'Obiteljsko putovanje', '48291736504', 'PODNESEN'),
 (N'marko', '2027-01-05', '2027-01-09', N'Selidba',              '73019485267', 'PODNESEN');

INSERT INTO dbo.platne_liste (zaposlenik, razdoblje, datoteka) VALUES
 (N'ana',   '2026-10', N'placa-ana-2026-10.txt'),
 (N'marko', '2026-10', N'placa-marko-2026-10.txt');

INSERT INTO dbo.edukacije (naziv, datum, kapacitet, prijavljeno) VALUES
 (N'Uvod u GDPR', '2026-12-02', 30, 5),
 (N'Excel za napredne', '2026-12-04', 15, 3),
 (N'Sigurnost na radu – zadnje mjesto', '2026-12-09', 20, 19),
 (N'Komunikacijske vještine', '2026-12-11', 25, 0),
 (N'Prva pomoć', '2027-01-14', 12, 2);
GO
PRINT N'Baza Kadrovska je stvorena.';
