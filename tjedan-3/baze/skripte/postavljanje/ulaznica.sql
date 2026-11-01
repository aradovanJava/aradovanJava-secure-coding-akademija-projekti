/* Ulaznica – shema i početni podaci (preslika aplikacije iz 2. tjedna, SQL Server 2022).
   Pokreće je init.sh samo ako baza ne postoji. */
SET NOCOUNT ON;
CREATE DATABASE [Ulaznica];
GO
USE [Ulaznica];
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
CREATE TABLE dbo.dogadjaji (
    id        BIGINT IDENTITY(1,1) PRIMARY KEY,
    naziv     NVARCHAR(200) NOT NULL,
    mjesto    NVARCHAR(120) NOT NULL,
    datum     DATETIME2(0)  NOT NULL,
    cijena    DECIMAL(10,2) NOT NULL,
    kapacitet INT           NOT NULL,
    prodano   INT           NOT NULL DEFAULT 0
);
CREATE TABLE dbo.narudzbe (
    id              BIGINT IDENTITY(1,1) PRIMARY KEY,
    dogadjaj_id     BIGINT        NOT NULL REFERENCES dbo.dogadjaji (id),
    kupac           NVARCHAR(50)  NOT NULL,
    kolicina        INT           NOT NULL,
    ime_na_ulaznici NVARCHAR(200) NOT NULL,
    oib             VARCHAR(11)   NULL,
    iznos           DECIMAL(10,2) NOT NULL,
    kreirano        DATETIME2(0)  NOT NULL DEFAULT SYSDATETIME(),
    autorizacija    VARCHAR(40)   NULL
);
-- Račun ostaje sačuvan i nakon storna narudžbe (knjigovodstvena evidencija).
CREATE TABLE dbo.racuni (
    id          BIGINT IDENTITY(1,1) PRIMARY KEY,
    narudzba_id BIGINT        NOT NULL,
    kupac       NVARCHAR(50)  NOT NULL,
    datoteka    NVARCHAR(200) NOT NULL
);
-- Dnevnik promjena nad narudžbama (puni ga okidač; služi za reviziju i reklamacije).
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
CREATE TRIGGER dbo.trg_narudzbe_revizija ON dbo.narudzbe
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.revizija (tablica, radnja, zapis_id, vlasnik)
    SELECT N'narudzbe',
           CASE WHEN d.id IS NULL THEN 'INSERT' WHEN i.id IS NULL THEN 'DELETE' ELSE 'UPDATE' END,
           COALESCE(i.id, d.id), COALESCE(i.kupac, d.kupac)
    FROM inserted AS i
    FULL OUTER JOIN deleted AS d ON d.id = i.id;
END;
GO
-- Lozinke: aplikacija ih je spremala kao nesoljeni SHA-256 (naslijeđeni kod).
INSERT INTO dbo.korisnici (username, password_hash, email, ime, prezime, uloga, oib) VALUES
 (N'ana',         LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Ana12345!'), 2)),       N'ana@primjer.hr',         N'Ana',   N'Anić',  'KORISNIK',    '48291736504'),
 (N'marko',       LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Marko12345!'), 2)),     N'marko@primjer.hr',       N'Marko', N'Marić', 'KORISNIK',    '73019485267'),
 (N'organizator', LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Ovlasteni12345!'), 2)), N'organizator@primjer.hr', N'Nina',  N'Novak', 'ORGANIZATOR', '50617283940'),
 (N'admin',       LOWER(CONVERT(VARCHAR(100), HASHBYTES('SHA2_256', 'Admin12345!'), 2)),     N'admin@primjer.hr',       N'Ivana', N'Admin', 'ADMIN',       '61728394051');

INSERT INTO dbo.postavke (username, podsjetnik, sati_prije, kanal) VALUES
 (N'ana', 1, 24, 'EMAIL'), (N'marko', 0, 2, 'SMS');

INSERT INTO dbo.dogadjaji (naziv, mjesto, datum, cijena, kapacitet, prodano) VALUES
 (N'Gibonni – akustični koncert', N'Lisinski, Zagreb', '2026-12-05T20:00', 35.00, 1800, 1),
 (N'Hamlet', N'HNK Zagreb', '2026-12-08T19:30', 22.00, 700, 2),
 (N'Jazz večer u Tvornici', N'Tvornica kulture, Zagreb', '2026-12-10T21:00', 18.00, 600, 0),
 (N'Orašar – balet', N'HNK Split', '2026-12-15T19:00', 28.00, 650, 0),
 (N'Zagrebačka filharmonija – zadnja ulaznica', N'Lisinski, Zagreb', '2026-12-18T19:30', 30.00, 100, 99),
 (N'Božićni koncert', N'Katedrala, Đakovo', '2026-12-20T18:00', 15.00, 400, 0),
 (N'Stand-up večer', N'Kerempuh, Zagreb', '2027-01-10T20:00', 20.00, 300, 0),
 (N'Novogodišnji koncert', N'Arena Pula', '2026-12-31T22:00', 45.00, 5000, 0);

INSERT INTO dbo.narudzbe (dogadjaj_id, kupac, kolicina, ime_na_ulaznici, oib, iznos, autorizacija) VALUES
 (1, N'ana',   1, N'Ana Anić',    '48291736504', 35.00, 'AUTH-5000'),
 (2, N'marko', 2, N'Marko Marić', '73019485267', 44.00, 'AUTH-5001');

INSERT INTO dbo.racuni (narudzba_id, kupac, datoteka) VALUES
 (1, N'ana',   N'racun-ana-2026-0001.txt'),
 (2, N'marko', N'racun-marko-2026-0002.txt');
GO
PRINT N'Baza Ulaznica je stvorena.';
