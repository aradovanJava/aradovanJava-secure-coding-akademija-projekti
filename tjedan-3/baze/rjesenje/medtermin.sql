/* =========================================================================================
   REFERENTNO RJEŠENJE – baza MedTermin (domena medtermin)
   Secure Coding akademija · 3. tjedan · Sigurnost baza podataka (SQL Server 2022)
   SAMO ZA PREDAVAČA – nije dio paketa za polaznike.

   Pokretanje (iz mape tjedan-3/baze, kao sa, na svježoj bazi – skripta je za jedno pokretanje):
     docker compose cp rjesenje/medtermin.sql sql:/tmp/rjesenje.sql
     docker compose exec sql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P '<sa lozinka>' \
         -b -I -f 65001 -i /tmp/rjesenje.sql \
         -v APP_LOZINKA='<nova lozinka aplikacije>' ADMIN_LOZINKA='<lozinka dba_admin>' KLJUC_LOZINKA='<lozinka ključeva>'
   Zatim u .env: ADMIN_LOGIN=dba_admin, ADMIN_PASSWORD=<ADMIN_LOZINKA>; docker compose up -d;
   docker compose --profile provjera run --rm provjera
   Napomena: datoteke certifikata u ./backup ne smiju već postojati (nakon reseta ispraznite ./backup).
   ========================================================================================= */
:on error exit
SET NOCOUNT ON;
GO

/* ---------------------------------------------------------------------------------------
   Z2 – PRIJAVE I KORISNICI
   --------------------------------------------------------------------------------------- */
USE master;
GO
-- Z2.4 (1. dio): prvo vlastita administratorska prijava, tek onda gasimo sa (na kraju skripte).
CREATE LOGIN dba_admin WITH PASSWORD = N'$(ADMIN_LOZINKA)', CHECK_POLICY = ON, CHECK_EXPIRATION = OFF;
ALTER SERVER ROLE sysadmin ADD MEMBER dba_admin;

-- Z2.1: nova jaka lozinka i uključena politika lozinki za aplikacijsku prijavu.
ALTER LOGIN [medtermin_app] WITH PASSWORD = N'$(APP_LOZINKA)';
ALTER LOGIN [medtermin_app] WITH CHECK_POLICY = ON;

-- Z2.2: aplikacija ne treba nikakva prava na razini poslužitelja.
ALTER SERVER ROLE sysadmin DROP MEMBER [medtermin_app];
GO
USE [MedTermin];
GO
-- Z2.3: aplikacijski korisnik izlazi iz db_owner (prava dobiva preko uloge u Z3).
ALTER ROLE db_owner DROP MEMBER [medtermin_app];

-- Z2.5: podrška više ne čita sve tablice (ciljana prava dobiva u Z4).
ALTER ROLE db_datareader DROP MEMBER podrska;
GO

/* ---------------------------------------------------------------------------------------
   Z3 – NAJMANJE OVLASTI
   --------------------------------------------------------------------------------------- */
CREATE ROLE uloga_aplikacija;
GO
-- Samo ono što aplikacija iz 2. tjedna stvarno radi (nema DELETE na korisnicima, nema DDL-a).
GRANT SELECT, INSERT, UPDATE ON dbo.korisnici    TO uloga_aplikacija;  -- prijava, registracija, reset lozinke
GRANT SELECT, INSERT, UPDATE ON dbo.reset_tokeni TO uloga_aplikacija;
GRANT SELECT, INSERT, UPDATE ON dbo.postavke     TO uloga_aplikacija;
GRANT SELECT                 ON dbo.lijecnici    TO uloga_aplikacija;
GRANT SELECT, INSERT, UPDATE ON dbo.termini      TO uloga_aplikacija;  -- uvoz termina, zauzeto
GRANT SELECT, INSERT, DELETE ON dbo.rezervacije  TO uloga_aplikacija;  -- rezervacija i otkazivanje
GRANT SELECT                 ON dbo.nalazi       TO uloga_aplikacija;
-- Dnevnik revizije puni isključivo okidač (ownership chaining: tablica i okidač imaju istog vlasnika),
-- pa aplikacija ne treba nikakva prava na njemu. DENY je dodatna, eksplicitna zaštita od petljanja.
DENY SELECT, INSERT, UPDATE, DELETE ON dbo.revizija TO uloga_aplikacija;

ALTER ROLE uloga_aplikacija ADD MEMBER [medtermin_app];

-- Z3.4: "SELECT za sve" preko public (+ guest) otvarao je cijelu bazu svakoj prijavi na poslužitelju.
REVOKE SELECT ON SCHEMA::dbo FROM public;
GO

/* ---------------------------------------------------------------------------------------
   Z8 – OČVRŠĆIVANJE (rano, jer zatvara najopasnije putove)
   --------------------------------------------------------------------------------------- */
-- guest bez CONNECT: prijave bez vlastitog korisnika (npr. bi_izvjestaji) više ne ulaze u bazu.
REVOKE CONNECT FROM guest;
GO
-- TRUSTWORTHY ON + db_owner + vlasnik sa = put do sysadmin (EXECUTE AS USER = 'dbo' u modulu).
ALTER DATABASE [MedTermin] SET TRUSTWORTHY OFF;
GO
USE master;
GO
EXEC sp_configure N'show advanced options', 1;
RECONFIGURE;
BEGIN TRY  -- na Linuxu xp_cmdshell nije podržan (Msg 15392); skripta mora raditi i na Windowsu
    EXEC sp_configure N'xp_cmdshell', 0;                -- izvršavanje naredbi OS-a iz T-SQL-a
END TRY
BEGIN CATCH
    PRINT N'xp_cmdshell: ' + ERROR_MESSAGE();
END CATCH;
EXEC sp_configure N'cross db ownership chaining', 0;    -- zaobilaženje provjera prava među bazama
EXEC sp_configure N'Ad Hoc Distributed Queries', 0;     -- OPENROWSET/OPENDATASOURCE prema bilo čemu
EXEC sp_configure N'clr enabled', 0;                    -- .NET kod unutar poslužitelja
RECONFIGURE;
EXEC sp_configure N'show advanced options', 0;
RECONFIGURE;
GO

/* ---------------------------------------------------------------------------------------
   Z5 (2. dio) – ŠIFRIRANJE STUPCA OIB (radimo prije RLS-a jer mijenjamo strukturu tablice)
   --------------------------------------------------------------------------------------- */
USE [MedTermin];
GO
-- Hijerarhija ključeva: SMK (poslužitelj) -> DMK (baza) -> certifikat -> simetrični AES ključ.
CREATE MASTER KEY ENCRYPTION BY PASSWORD = N'$(KLJUC_LOZINKA)';
CREATE CERTIFICATE CertOib WITH SUBJECT = N'Zaštita OIB-a – MedTermin';
CREATE SYMMETRIC KEY KljucOib WITH ALGORITHM = AES_256 ENCRYPTION BY CERTIFICATE CertOib;
GO
ALTER TABLE dbo.rezervacije ADD oib_sifrirano VARBINARY(256) NULL;
GO
OPEN SYMMETRIC KEY KljucOib DECRYPTION BY CERTIFICATE CertOib;
UPDATE dbo.rezervacije
SET oib_sifrirano = ENCRYPTBYKEY(KEY_GUID(N'KljucOib'), oib)
WHERE oib IS NOT NULL;
CLOSE SYMMETRIC KEY KljucOib;
GO
-- Čisti tekst više ne smije postojati.
ALTER TABLE dbo.rezervacije DROP COLUMN oib;
GO
-- Aplikacija (uloga) smije koristiti ključ za upis i čitanje OIB-a, npr.:
--   upis:    ENCRYPTBYKEY(KEY_GUID(N'KljucOib'), @oib)   (nakon OPEN SYMMETRIC KEY …)
--   čitanje: CONVERT(VARCHAR(11), DECRYPTBYKEYAUTOCERT(CERT_ID(N'CertOib'), NULL, oib_sifrirano))
GRANT VIEW DEFINITION ON SYMMETRIC KEY::KljucOib TO uloga_aplikacija;
GRANT CONTROL ON CERTIFICATE::CertOib TO uloga_aplikacija;
GO
-- Provjera (kao administrator):
SELECT id, pacijent, CONVERT(VARCHAR(11), DECRYPTBYKEYAUTOCERT(CERT_ID(N'CertOib'), NULL, oib_sifrirano)) AS oib
FROM dbo.rezervacije;
GO

/* ---------------------------------------------------------------------------------------
   Z4 – DYNAMIC DATA MASKING I ROW-LEVEL SECURITY
   --------------------------------------------------------------------------------------- */
-- Maskiranje: tko nema UNMASK, vidi aXXX@XXXX.com i *******4051 umjesto stvarnih vrijednosti.
ALTER TABLE dbo.korisnici ALTER COLUMN email ADD MASKED WITH (FUNCTION = 'email()');
ALTER TABLE dbo.korisnici ALTER COLUMN oib   ADD MASKED WITH (FUNCTION = 'partial(0,"*******",4)');
GO
-- Podrška: samo stupci koji joj trebaju – bez password_hash, bez UNMASK.
CREATE ROLE uloga_podrska;
GRANT SELECT ON dbo.korisnici (id, username, email, ime, prezime, uloga, oib) TO uloga_podrska;
ALTER ROLE uloga_podrska ADD MEMBER podrska;
-- Aplikacija treba stvarne podatke korisnika (npr. /api/ja) – granularni UNMASK (SQL Server 2022).
GRANT UNMASK ON dbo.korisnici TO uloga_aplikacija;
GO
-- RLS: predikatna funkcija u zasebnoj shemi (aplikacija nema prava na nju ni na shemu).
CREATE SCHEMA sigurnost AUTHORIZATION dbo;
GO
CREATE FUNCTION sigurnost.fn_vlasnik_zapisa (@vlasnik NVARCHAR(50))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
    SELECT 1 AS dopusteno
    WHERE IS_MEMBER(N'uloga_aplikacija') = 0                                   -- RLS vrijedi za aplikaciju, ne za DBA-u
       OR @vlasnik = CAST(SESSION_CONTEXT(N'korisnik') AS NVARCHAR(50))         -- vlastiti zapisi
       OR EXISTS (SELECT 1 FROM dbo.korisnici AS k                              -- administrator aplikacije vidi sve
                  WHERE k.username = CAST(SESSION_CONTEXT(N'korisnik') AS NVARCHAR(50))
                    AND k.uloga = 'ADMIN');
GO
CREATE SECURITY POLICY sigurnost.politika_rezervacije
    ADD FILTER PREDICATE sigurnost.fn_vlasnik_zapisa(pacijent) ON dbo.rezervacije,
    ADD BLOCK PREDICATE  sigurnost.fn_vlasnik_zapisa(pacijent) ON dbo.rezervacije AFTER INSERT
    WITH (STATE = ON);
GO
-- Aplikacija nakon prijave korisnika postavlja kontekst na istoj konekciji (prije upita):
--   EXEC sp_set_session_context @key = N'korisnik', @value = N'ana', @read_only = 1;
-- (read_only sprječava da kasniji kod – ili SQL injection – promijeni identitet u istoj sesiji.)

/* ---------------------------------------------------------------------------------------
   Z5 (1. dio) – TDE (Transparent Data Encryption)
   --------------------------------------------------------------------------------------- */
USE master;
GO
IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = N'##MS_DatabaseMasterKey##')
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = N'$(KLJUC_LOZINKA)';
CREATE CERTIFICATE CertTDE_MedTermin WITH SUBJECT = N'TDE – MedTermin';
GO
-- Bez kopije certifikata s privatnim ključem kopija baze je neupotrebljiva na drugom poslužitelju!
BACKUP CERTIFICATE CertTDE_MedTermin
    TO FILE = N'/var/opt/mssql/backup/CertTDE_MedTermin.cer'
    WITH PRIVATE KEY (FILE = N'/var/opt/mssql/backup/CertTDE_MedTermin.pvk',
                      ENCRYPTION BY PASSWORD = N'$(KLJUC_LOZINKA)');
GO
USE [MedTermin];
GO
CREATE DATABASE ENCRYPTION KEY
    WITH ALGORITHM = AES_256
    ENCRYPTION BY SERVER CERTIFICATE CertTDE_MedTermin;
GO
ALTER DATABASE [MedTermin] SET ENCRYPTION ON;
GO
-- Šifriranje teče u pozadini; pričekamo da završi (encryption_state = 3).
DECLARE @i INT = 0;
WHILE @i < 120 AND NOT EXISTS (SELECT 1 FROM sys.dm_database_encryption_keys
                               WHERE database_id = DB_ID(N'MedTermin') AND encryption_state = 3)
BEGIN
    WAITFOR DELAY '00:00:01';
    SET @i += 1;
END;
SELECT DB_NAME(database_id) AS baza, encryption_state_desc, percent_complete
FROM sys.dm_database_encryption_keys;
GO

/* ---------------------------------------------------------------------------------------
   Z6 – REVIZIJA (u praksi je uključite PRVU, da zabilježi i sve ostale promjene)
   --------------------------------------------------------------------------------------- */
USE master;
GO
CREATE SERVER AUDIT Revizija_MedTermin
    TO FILE (FILEPATH = N'/var/opt/mssql/audit/', MAXSIZE = 50 MB, MAX_ROLLOVER_FILES = 20)
    WITH (QUEUE_DELAY = 1000, ON_FAILURE = CONTINUE);
ALTER SERVER AUDIT Revizija_MedTermin WITH (STATE = ON);
GO
CREATE SERVER AUDIT SPECIFICATION Revizija_prijave
    FOR SERVER AUDIT Revizija_MedTermin
    ADD (FAILED_LOGIN_GROUP),
    ADD (SUCCESSFUL_LOGIN_GROUP),
    ADD (SERVER_ROLE_MEMBER_CHANGE_GROUP),
    ADD (SERVER_PRINCIPAL_CHANGE_GROUP),
    ADD (AUDIT_CHANGE_GROUP)
    WITH (STATE = ON);
GO
USE [MedTermin];
GO
CREATE DATABASE AUDIT SPECIFICATION Revizija_osjetljivi_podaci
    FOR SERVER AUDIT Revizija_MedTermin
    ADD (SELECT ON OBJECT::dbo.korisnici BY public),
    ADD (SELECT, UPDATE, DELETE ON OBJECT::dbo.rezervacije BY public),
    ADD (SELECT ON OBJECT::dbo.nalazi BY public),
    ADD (DATABASE_PERMISSION_CHANGE_GROUP),
    ADD (SCHEMA_OBJECT_PERMISSION_CHANGE_GROUP),
    ADD (DATABASE_ROLE_MEMBER_CHANGE_GROUP)
    WITH (STATE = ON);
GO
-- Čitanje zapisa (nakon nekog SELECT-a nad dbo.korisnici):
--   SELECT event_time, action_id, server_principal_name, database_principal_name, object_name, statement
--   FROM sys.fn_get_audit_file(N'/var/opt/mssql/audit/*.sqlaudit', DEFAULT, DEFAULT) ORDER BY event_time DESC;

/* ---------------------------------------------------------------------------------------
   Z7 – SIGURNOSNE KOPIJE
   --------------------------------------------------------------------------------------- */
USE master;
GO
-- Zaseban certifikat za šifriranje kopija (i njega treba sačuvati izvan poslužitelja).
CREATE CERTIFICATE CertBackup WITH SUBJECT = N'Šifriranje sigurnosnih kopija';
BACKUP CERTIFICATE CertBackup
    TO FILE = N'/var/opt/mssql/backup/CertBackup.cer'
    WITH PRIVATE KEY (FILE = N'/var/opt/mssql/backup/CertBackup.pvk',
                      ENCRYPTION BY PASSWORD = N'$(KLJUC_LOZINKA)');
GO
BACKUP DATABASE [MedTermin]
    TO DISK = N'/var/opt/mssql/backup/MedTermin_puna.bak'
    WITH FORMAT, INIT, COMPRESSION, CHECKSUM,
         ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = CertBackup),
         NAME = N'MedTermin – puna šifrirana kopija';
GO
-- Provjera čitljivosti i kontrolnih zbrojeva; LOADHISTORY je zapisuje u msdb.dbo.restorehistory.
RESTORE VERIFYONLY
    FROM DISK = N'/var/opt/mssql/backup/MedTermin_puna.bak'
    WITH CHECKSUM, LOADHISTORY;
GO
-- Logička imena datoteka za MOVE:
RESTORE FILELISTONLY FROM DISK = N'/var/opt/mssql/backup/MedTermin_puna.bak';
GO
-- Kopija koja nije isprobana nije kopija: probni povrat pod drugim imenom.
RESTORE DATABASE [MedTermin_ProbniRestore]
    FROM DISK = N'/var/opt/mssql/backup/MedTermin_puna.bak'
    WITH MOVE N'MedTermin'     TO N'/var/opt/mssql/data/MedTermin_ProbniRestore.mdf',
         MOVE N'MedTermin_log' TO N'/var/opt/mssql/data/MedTermin_ProbniRestore_log.ldf',
         CHECKSUM, RECOVERY;
GO
SELECT COUNT(*) AS korisnika_u_probnoj_bazi FROM [MedTermin_ProbniRestore].dbo.korisnici;
GO

/* ---------------------------------------------------------------------------------------
   Z2.4 (2. dio) – sa se više ne koristi
   --------------------------------------------------------------------------------------- */
USE master;
GO
ALTER LOGIN sa DISABLE;
GO
PRINT N'Referentno rješenje za MedTermin je primijenjeno. Sada u .env postavite ADMIN_LOGIN=dba_admin.';
