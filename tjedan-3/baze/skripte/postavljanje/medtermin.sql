/* MedTermin – shema i početni podaci (preslika aplikacije iz 2. tjedna, SQL Server 2022).
   Pokreće je init.sh samo ako baza ne postoji. */
SET NOCOUNT ON;
CREATE DATABASE [MedTermin];
GO
USE [MedTermin];
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
CREATE TABLE dbo.lijecnici (
    id              BIGINT IDENTITY(1,1) PRIMARY KEY,
    ime             NVARCHAR(60)  NOT NULL,
    prezime         NVARCHAR(60)  NOT NULL,
    specijalizacija NVARCHAR(100) NOT NULL,
    ordinacija      NVARCHAR(60)  NOT NULL
);
CREATE TABLE dbo.termini (
    id          BIGINT IDENTITY(1,1) PRIMARY KEY,
    lijecnik_id BIGINT        NOT NULL REFERENCES dbo.lijecnici (id),
    pocetak     DATETIME2(0)  NOT NULL,
    kapacitet   INT           NOT NULL,
    zauzeto     INT           NOT NULL DEFAULT 0,
    napomena    NVARCHAR(500) NULL
);
CREATE TABLE dbo.rezervacije (
    id         BIGINT IDENTITY(1,1) PRIMARY KEY,
    termin_id  BIGINT         NOT NULL REFERENCES dbo.termini (id),
    pacijent   NVARCHAR(50)   NOT NULL,
    napomena   NVARCHAR(1000) NULL,
    oib        VARCHAR(11)    NULL,
    kreirano   DATETIME2(0)   NOT NULL DEFAULT SYSDATETIME(),
    oznaka_bis VARCHAR(40)    NULL
);
CREATE TABLE dbo.nalazi (
    id       BIGINT IDENTITY(1,1) PRIMARY KEY,
    pacijent NVARCHAR(50)  NOT NULL,
    naziv    NVARCHAR(120) NOT NULL,
    datoteka NVARCHAR(200) NOT NULL
);
-- Dnevnik promjena nad rezervacijama (puni ga okidač; služi za reviziju i reklamacije).
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
CREATE TRIGGER dbo.trg_rezervacije_revizija ON dbo.rezervacije
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.revizija (tablica, radnja, zapis_id, vlasnik)
    SELECT N'rezervacije',
           CASE WHEN d.id IS NULL THEN 'INSERT' WHEN i.id IS NULL THEN 'DELETE' ELSE 'UPDATE' END,
           COALESCE(i.id, d.id), COALESCE(i.pacijent, d.pacijent)
    FROM inserted AS i
    FULL OUTER JOIN deleted AS d ON d.id = i.id;
END;
GO
-- Lozinke: aplikacija ih je spremala kao nesoljeni SHA-256 (naslijeđeni kod).
INSERT INTO dbo.korisnici (username, password_hash, email, ime, prezime, uloga, oib) VALUES
 (N'ana',       LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Ana12345!'), 2)),       N'ana@primjer.hr',       N'Ana',   N'Anić',  'KORISNIK', '48291736504'),
 (N'marko',     LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Marko12345!'), 2)),     N'marko@primjer.hr',     N'Marko', N'Marić', 'KORISNIK', '73019485267'),
 (N'dr.horvat', LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Ovlasteni12345!'), 2)), N'dr.horvat@primjer.hr', N'Ivan',  N'Horvat', 'LIJECNIK', '50617283940'),
 (N'admin',     LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Admin12345!'), 2)),     N'admin@primjer.hr',     N'Ivana', N'Admin', 'ADMIN',    '61728394051');

INSERT INTO dbo.postavke (username, podsjetnik, sati_prije, kanal) VALUES
 (N'ana', 1, 24, 'EMAIL'), (N'marko', 0, 2, 'SMS');

INSERT INTO dbo.lijecnici (ime, prezime, specijalizacija, ordinacija) VALUES
 (N'Ivan', N'Horvat', N'Kardiologija', N'Ordinacija 1'),
 (N'Maja', N'Kovačević', N'Dermatologija', N'Ordinacija 2'),
 (N'Tomislav', N'Babić', N'Ortopedija', N'Ordinacija 3'),
 (N'Petra', N'Novak', N'Neurologija', N'Ordinacija 4'),
 (N'Luka', N'Jurić', N'Interna medicina', N'Ordinacija 5'),
 (N'Ema', N'Vuković', N'Oftalmologija', N'Ordinacija 6');

INSERT INTO dbo.termini (lijecnik_id, pocetak, kapacitet, zauzeto) VALUES
 (1, '2026-12-01T08:00', 1, 1), (2, '2026-12-01T09:00', 1, 1), (1, '2026-12-01T09:00', 1, 0),
 (2, '2026-12-01T10:00', 1, 0), (3, '2026-12-02T08:00', 1, 0), (4, '2026-12-02T09:00', 1, 0),
 (5, '2026-12-02T10:00', 1, 0), (6, '2026-12-03T08:00', 1, 0), (1, '2026-12-03T09:00', 3, 0),
 (3, '2026-12-03T10:00', 1, 0);

INSERT INTO dbo.rezervacije (termin_id, pacijent, napomena, oib, oznaka_bis) VALUES
 (1, N'ana',   N'Kontrolni pregled tlaka', '48291736504', 'BIS-1-1000'),
 (2, N'marko', N'Bolovi u leđima',         '73019485267', 'BIS-2-1000');

INSERT INTO dbo.nalazi (pacijent, naziv, datoteka) VALUES
 (N'ana',   N'Krvna slika',     N'nalaz-ana-krvna-slika.txt'),
 (N'marko', N'RTG kralježnice', N'nalaz-marko-rtg.txt');
GO
PRINT N'Baza MedTermin je stvorena.';
