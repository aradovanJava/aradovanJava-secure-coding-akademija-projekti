/* Zatečene postavke poslužitelja i baze $(BAZA).
   Ovako je razvojni tim podesio okruženje dok je razvijao aplikaciju (2. tjedan) i ostavio ga
   "privremeno" i za produkciju. Ne mijenjajte ovu skriptu – promjene radite u VLASTITOJ skripti
   (vidi ZADACI.md). Pokreće je init.sh odmah nakon stvaranja baze. */
SET NOCOUNT ON;
USE master;
GO
-- Prijava kojom se aplikacija spaja na bazu (connection string u konfiguraciji aplikacije).
CREATE LOGIN [$(APP)]
    WITH PASSWORD = N'$(DOMENA)123', CHECK_POLICY = OFF, CHECK_EXPIRATION = OFF,
         DEFAULT_DATABASE = [$(BAZA)];
-- Dodano tijekom migracije sheme ("samo dok ne proradi Flyway") i nikad uklonjeno.
ALTER SERVER ROLE sysadmin ADD MEMBER [$(APP)];

-- Korisnička podrška pregledava korisničke račune kad korisnik nazove.
CREATE LOGIN podrska WITH PASSWORD = N'Sluzba-Pomoci24', DEFAULT_DATABASE = [$(BAZA)];

-- Izvještaji (Power BI). Korisnik u bazi nije napravljen – "radi i ovako".
CREATE LOGIN bi_izvjestaji WITH PASSWORD = N'Izvjestaji2024!', DEFAULT_DATABASE = [$(BAZA)];
GO
-- Opcije poslužitelja uključene za skripte izvoza, upite prema drugim bazama i CLR proceduru za PDF.
EXEC sp_configure N'show advanced options', 1;
RECONFIGURE;
BEGIN TRY
    EXEC sp_configure N'xp_cmdshell', 1;
    RECONFIGURE;
END TRY
BEGIN CATCH
    PRINT N'Napomena: xp_cmdshell nije moguće uključiti na ovoj platformi: ' + ERROR_MESSAGE();
END CATCH;
EXEC sp_configure N'cross db ownership chaining', 1;
RECONFIGURE;
EXEC sp_configure N'Ad Hoc Distributed Queries', 1;
RECONFIGURE;
EXEC sp_configure N'clr enabled', 1;
RECONFIGURE;
GO
USE [$(BAZA)];
GO
-- Aplikacija "mora moći sve" (migracije, ručni popravci podataka).
CREATE USER [$(APP)] FOR LOGIN [$(APP)];
ALTER ROLE db_owner ADD MEMBER [$(APP)];

-- Podrška čita sve tablice – lakše nego popisivati koje joj trebaju.
CREATE USER podrska FOR LOGIN podrska;
ALTER ROLE db_datareader ADD MEMBER podrska;

-- Izvještajni alati se spajaju bez vlastitog korisnika (guest) i čitaju sve iz sheme dbo.
GRANT CONNECT TO guest;
GRANT SELECT ON SCHEMA::dbo TO public;
GO
-- Potrebno za CLR proceduru koja generira PDF potvrde (izvorno iz dokumentacije biblioteke).
ALTER DATABASE [$(BAZA)] SET TRUSTWORTHY ON;
GO
PRINT N'Zatečene postavke su primijenjene na $(BAZA).';
