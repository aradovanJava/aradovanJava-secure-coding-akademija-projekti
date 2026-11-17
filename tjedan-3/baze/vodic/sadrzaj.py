"""Vodič za predavača – Sigurnost baza podataka (Tjedan 3): sadržaj na jednom mjestu.

Iz ovog modula nastaju (1) Word dokument (napravi_docx.js čita sadrzaj.json) i (2) SQL datoteke za provjeru
koraka u CI-ju (generiraj_sql.py). SQL je napisan za MedTermin; za ostale domene zamjenjuju se nazivi
(ZAMJENE) i blok prava aplikacije (PRAVA).
"""
import json

DOMENE = {
    "medtermin": dict(baza="MedTermin", glavna="rezervacije", vlasnik="pacijent", druga="nalazi"),
    "ulaznica": dict(baza="Ulaznica", glavna="narudzbe", vlasnik="kupac", druga="racuni"),
    "kadrovska": dict(baza="Kadrovska", glavna="zahtjevi", vlasnik="zaposlenik", druga="platne_liste"),
}

PRAVA = {
    "medtermin": """GRANT SELECT, INSERT, UPDATE ON dbo.korisnici    TO uloga_aplikacija;  -- prijava, registracija, reset lozinke
GRANT SELECT, INSERT, UPDATE ON dbo.reset_tokeni TO uloga_aplikacija;
GRANT SELECT, INSERT, UPDATE ON dbo.postavke     TO uloga_aplikacija;
GRANT SELECT                 ON dbo.lijecnici    TO uloga_aplikacija;
GRANT SELECT, INSERT, UPDATE ON dbo.termini      TO uloga_aplikacija;  -- uvoz termina, zauzeto
GRANT SELECT, INSERT, DELETE ON dbo.rezervacije  TO uloga_aplikacija;  -- rezervacija i otkazivanje
GRANT SELECT                 ON dbo.nalazi       TO uloga_aplikacija;""",
    "ulaznica": """GRANT SELECT, INSERT, UPDATE ON dbo.korisnici    TO uloga_aplikacija;  -- prijava, registracija, reset lozinke
GRANT SELECT, INSERT, UPDATE ON dbo.reset_tokeni TO uloga_aplikacija;
GRANT SELECT, INSERT, UPDATE ON dbo.postavke     TO uloga_aplikacija;
GRANT SELECT, INSERT, UPDATE ON dbo.dogadjaji    TO uloga_aplikacija;  -- uvoz događaja, prodano
GRANT SELECT, INSERT, DELETE ON dbo.narudzbe     TO uloga_aplikacija;  -- kupnja i storno
GRANT SELECT, INSERT         ON dbo.racuni       TO uloga_aplikacija;  -- račun se nikad ne briše""",
    "kadrovska": """GRANT SELECT, INSERT, UPDATE ON dbo.korisnici         TO uloga_aplikacija;  -- prijava, registracija, reset lozinke
GRANT SELECT, INSERT, UPDATE ON dbo.reset_tokeni      TO uloga_aplikacija;
GRANT SELECT, INSERT, UPDATE ON dbo.postavke          TO uloga_aplikacija;
GRANT SELECT                 ON dbo.zaposlenici       TO uloga_aplikacija;
GRANT SELECT, INSERT, DELETE ON dbo.zahtjevi          TO uloga_aplikacija;  -- podnošenje i povlačenje zahtjeva
GRANT SELECT                 ON dbo.platne_liste      TO uloga_aplikacija;
GRANT SELECT, INSERT, UPDATE ON dbo.edukacije         TO uloga_aplikacija;  -- uvoz, broj prijavljenih
GRANT SELECT, INSERT         ON dbo.prijave_edukacije TO uloga_aplikacija;""",
}


def za_domenu(sql: str, domena: str) -> str:
    """MedTermin -> druga domena (redoslijed zamjena je bitan)."""
    if domena == "medtermin":
        return sql.replace("{PRAVA}", PRAVA["medtermin"])
    d = DOMENE[domena]
    sql = sql.replace("{PRAVA}", PRAVA[domena])
    for staro, novo in (("MedTermin", d["baza"]), ("medtermin", domena), ("rezervacije", d["glavna"]),
                        ("pacijent", d["vlasnik"]), ("nalazi", d["druga"])):
        sql = sql.replace(staro, novo)
    return sql


# ----------------------------------------------------------------------------------------------------------
# Z1 – prijetnje zatečenog stanja: (#, prijetnja, nalaz u katalogu, uzrok (datoteka, redak), scenarij, korak)
# ----------------------------------------------------------------------------------------------------------
Z1 = [
    ("1", "Aplikacija je sysadmin",
     "sys.server_role_members: medtermin_app u ulozi sysadmin",
     "zatecene-postavke.sql, r. 13",
     "SQL injection u aplikaciji (T2, S08 u sortiranju) postaje kompromitacija cijelog poslužitelja: sve baze, nove prijave, gašenje revizije, brisanje baza.",
     "K2 (Z2.2)"),
    ("2", "Aplikacija je db_owner",
     "sys.database_role_members: medtermin_app u ulozi db_owner",
     "zatecene-postavke.sql, r. 41–42",
     "I bez sysadmina aplikacija mijenja shemu, gasi okidač, briše zapise iz dbo.revizija i tablice.",
     "K2 (Z2.3), K3"),
    ("3", "Slaba i predvidljiva lozinka aplikacije",
     "sys.sql_logins: is_policy_checked = 0 za medtermin_app",
     "zatecene-postavke.sql, r. 9–11",
     "Lozinka oblika <domena>123 pogađa se u nekoliko pokušaja; ista shema vrijedi na svakoj instalaciji, a lozinka je ionako u konfiguraciji aplikacije.",
     "K2 (Z2.1)"),
    ("4", "Svaka prijava čita sve (guest + public)",
     "sys.database_permissions: CONNECT za guest, SELECT na shemu dbo za public",
     "zatecene-postavke.sql, r. 49–50",
     "Svaka prijava na poslužitelju, i ona bez korisnika u bazi (bi_izvjestaji), čita sve tablice: OIB, password_hash, reset_tokeni, nalaze.",
     "K3 (Z3.4), K4 (Z8.3)"),
    ("5", "Podrška čita sve tablice",
     "sys.database_role_members: podrska u ulozi db_datareader",
     "zatecene-postavke.sql, r. 45–46",
     "Djelatnik podrške čita hasheve lozinki i zdravstvene nalaze; račun je zajednički pa se ne zna tko je točno čitao.",
     "K2 (Z2.5), K6 (Z4.4–Z4.5)"),
    ("6", "Reset tokeni čitljivi",
     "dbo.reset_tokeni dostupan kroz nalaze 4 i 5",
     "medtermin.sql (tablica dbo.reset_tokeni) + nalazi 4 i 5",
     "Preuzimanje računa: neiskorišteni token iz tablice postavlja novu lozinku bilo kojem korisniku.",
     "K3, K6"),
    ("7", "sa omogućen i u stalnoj upotrebi",
     "sys.sql_logins: sa is_disabled = 0; nema druge administratorske prijave",
     "zadano stanje SQL Servera (init se spaja kao sa)",
     "Poznato ime za pogađanje lozinke; nema osobne odgovornosti za administratorske radnje.",
     "K2 + K9 (Z2.4)"),
    ("8", "TRUSTWORTHY ON, vlasnik baze sa",
     "sys.databases: is_trustworthy_on = 1, SUSER_SNAME(owner_sid) = sa",
     "zatecene-postavke.sql, r. 53",
     "db_owner baze podiže ovlasti do sysadmina (modul s EXECUTE AS koji se izvodi kao dbo, odnosno sa) – vraća ono što je Z2.2 uklonio.",
     "K4 (Z8.2)"),
    ("9", "CLR, cross-db ownership chaining i ad hoc upiti uključeni",
     "sys.configurations: value_in_use = 1",
     "zatecene-postavke.sql, r. 31–36",
     "CLR: vlastiti .NET kod unutar poslužitelja (na Windowsu uz TRUSTWORTHY i UNSAFE sklopovi); chaining preskače provjeru prava među bazama istog vlasnika; OPENROWSET/OPENDATASOURCE iznosi podatke na drugi poslužitelj.",
     "K4 (Z8.1)"),
    ("10", "xp_cmdshell (pokušaj uključivanja)",
     "sys.configurations: na Linuxu value_in_use = 0 (greška 15392)",
     "zatecene-postavke.sql, r. 24–30",
     "Na Windows poslužitelju SQL injection postaje izvođenje naredbi operacijskog sustava; skripta rješenja mora ga isključiti na obje platforme.",
     "K4 (Z8.1)"),
    ("11", "Nema šifriranja, OIB u čistom tekstu",
     "sys.dm_database_encryption_keys prazan; dbo.rezervacije.oib VARCHAR(11)",
     "medtermin.sql, r. 51; TDE ne postoji",
     "Ukradeni volumen, datoteke baze ili kopija čitaju se izravno; za zdravstvene podatke i OIB i problem po GDPR-u (čl. 32).",
     "K5, K7 (Z5)"),
    ("12", "Nema sigurnosnih kopija",
     "msdb.dbo.backupset prazan",
     "ne postoji",
     "Ransomware, DROP TABLE preko injectiona ili ljudska greška znače trajni gubitak podataka.",
     "K8 (Z7)"),
    ("13", "Nema revizije pristupa",
     "sys.server_audits prazan; dbo.revizija bilježi samo promjene rezervacija",
     "ne postoji; medtermin.sql, r. 62–84 (dnevnik bez čitanja)",
     "Ne zna se tko je čitao OIB ili nalaze, pa se curenje ne može ni ograničiti ni dokazati (GDPR čl. 33).",
     "K1 (Z6)"),
    ("14", "Nema Row-Level Securityja",
     "sys.security_policies prazan",
     "ne postoji",
     "IDOR u aplikaciji (T2, S01) nema drugu crtu obrane – baza aplikaciji vraća sve retke.",
     "K6 (Z4.1–Z4.2)"),
]

KOMBINACIJE = [
    ("Injection + sysadmin (1 i 2)", "jedna greška u kodu postaje kompromitacija cijelog poslužitelja, a ne jedne tablice."),
    ("db_owner + TRUSTWORTHY + vlasnik sa (2 i 8)", "uklanjanje sysadmina (Z2.2) nije dovoljno dok su TRUSTWORTHY i db_owner tu."),
    ("guest + public + reset tokeni (4 i 6)", "izvještajna prijava bez korisnika u bazi može preuzeti bilo koji korisnički račun u aplikaciji."),
    ("Bez revizije, kopija i šifriranja (11, 12 i 13)", "nakon incidenta ne znaš što je procurilo, ne možeš vratiti podatke, a ukradena kopija se čita bez ključa; ne možeš ni procijeniti povredu koju trebaš prijaviti AZOP-u."),
]

# ----------------------------------------------------------------------------------------------------------
# Koraci (redoslijed izvođenja). sql/test su za MedTermin; {PRAVA} se zamjenjuje blokom prava domene.
# ----------------------------------------------------------------------------------------------------------
KORACI = [
    dict(
        id="K1", zadatak="Z6", naslov="Revizija (auditing)",
        provjere=["Z6.1", "Z6.2", "Z6.3", "Z6.4", "Z6.5"],
        uzrok="Revizija ne postoji (sys.server_audits je prazan). Tablica dbo.revizija (medtermin.sql, r. 62–84) bilježi samo promjene rezervacija, ne i čitanja, a aplikacija kao db_owner može je brisati.",
        zasto=[
            "Reviziju uključujemo prvu: od tog trenutka bilježi i sve promjene prava i članstava iz sljedećih koraka (ZADACI.md to izričito preporučuje).",
            "Server audit piše u /var/opt/mssql/audit/, što je na računalu mapa audit\\ u paketu.",
            "Specifikacija na razini poslužitelja bilježi uspješne i neuspješne prijave te promjene prijava, uloga i same revizije.",
            "Specifikacija na razini baze bilježi SELECT nad osjetljivim tablicama i promjene prava i članstva u ulogama baze.",
        ],
        sql="""USE master;
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
GO""",
        test="""-- Revizija je uključena i piše u /var/opt/mssql/audit/
SELECT name, is_state_enabled, log_file_path FROM sys.server_file_audits;

-- Jedno čitanje osjetljive tablice, pa zapis u reviziji
SELECT COUNT(*) AS korisnika FROM MedTermin.dbo.korisnici;
WAITFOR DELAY '00:00:02';
SELECT TOP (10) event_time, action_id, succeeded, server_principal_name, object_name, statement
FROM sys.fn_get_audit_file(N'/var/opt/mssql/audit/*.sqlaudit', DEFAULT, DEFAULT)
ORDER BY event_time DESC;""",
        ocekivano=[
            "sys.server_file_audits: Revizija_MedTermin, is_state_enabled = 1, log_file_path = /var/opt/mssql/audit/.",
            "U zapisima revizije postoji redak s action_id = SL, object_name = korisnici i vašim SELECT-om u stupcu statement.",
            "Dodatni test: u SSMS-u se pokušajte prijaviti pogrešnom lozinkom, pa u istom upitu filtrirajte WHERE action_id = 'LGIF' – neuspjela prijava je zabilježena. Vidjet ćete i prijave healthchecka svakih 10 sekundi (LGIS).",
        ],
        pitanje=None,
    ),
    dict(
        id="K2", zadatak="Z2", naslov="Prijave i korisnici (bez gašenja sa)",
        provjere=["Z2.1", "Z2.2", "Z2.3", "Z2.5"],
        uzrok="zatecene-postavke.sql: r. 9–11 (lozinka <domena>123 i CHECK_POLICY = OFF), r. 13 (aplikacija u sysadmin), r. 41–42 (aplikacija u db_owner), r. 45–46 (podrska u db_datareader); sa je jedina administratorska prijava.",
        zasto=[
            "Prvo napravite vlastitu administratorsku prijavu (dba_admin) i isprobajte je; sa gasimo tek na kraju (K9), inače se sami zaključate.",
            "Aplikacija dobiva novu jaku lozinku i uključenu politiku lozinki, a izlazi iz sysadmin i db_owner.",
            "Podrška izlazi iz db_datareader; ciljana prava na stupce dobiva u K6.",
            "Nakon ovog koraka aplikacija privremeno nema nikakva prava u bazi – zato K3 izvedite odmah nakon K2.",
        ],
        sql=""":setvar APP_LOZINKA   "Nova-Lozinka_Aplikacije2026"
:setvar ADMIN_LOZINKA "Lozinka-Za_DbaAdmina2026"
USE master;
GO
-- Z2.4 (1. dio): vlastita administratorska prijava
CREATE LOGIN dba_admin WITH PASSWORD = N'$(ADMIN_LOZINKA)', CHECK_POLICY = ON, CHECK_EXPIRATION = OFF;
ALTER SERVER ROLE sysadmin ADD MEMBER dba_admin;
-- Z2.1: nova jaka lozinka i politika lozinki
ALTER LOGIN [medtermin_app] WITH PASSWORD = N'$(APP_LOZINKA)';
ALTER LOGIN [medtermin_app] WITH CHECK_POLICY = ON;
-- Z2.2: aplikaciji ne trebaju prava na razini poslužitelja
ALTER SERVER ROLE sysadmin DROP MEMBER [medtermin_app];
GO
USE [MedTermin];
GO
-- Z2.3: aplikacija izlazi iz db_owner (prava dobiva preko uloge u K3)
ALTER ROLE db_owner DROP MEMBER [medtermin_app];
-- Z2.5: podrška više ne čita sve tablice
ALTER ROLE db_datareader DROP MEMBER podrska;
GO""",
        test="""SELECT name, is_policy_checked, is_disabled
FROM sys.sql_logins
WHERE name IN (N'medtermin_app', N'dba_admin', N'podrska', N'sa');

SELECT IS_SRVROLEMEMBER(N'sysadmin', N'medtermin_app') AS app_sysadmin,
       IS_SRVROLEMEMBER(N'sysadmin', N'dba_admin')     AS dba_sysadmin;

USE [MedTermin];
SELECT IS_ROLEMEMBER(N'db_owner', N'medtermin_app')  AS app_db_owner,
       IS_ROLEMEMBER(N'db_datareader', N'podrska')   AS podrska_datareader;""",
        ocekivano=[
            "medtermin_app i dba_admin: is_policy_checked = 1, is_disabled = 0.",
            "app_sysadmin = 0, dba_sysadmin = 1; app_db_owner = 0, podrska_datareader = 0.",
            "Prijava u SSMS-u kao medtermin_app sa starom lozinkom (medtermin123) javlja Login failed – a u reviziji (K1) nastaje zapis LGIF.",
            "Nova prijava dba_admin radi: otvorite novu konekciju u SSMS-u s njom prije koraka K9.",
        ],
        pitanje=None,
    ),
    dict(
        id="K3", zadatak="Z3", naslov="Najmanje ovlasti",
        provjere=["Z3.1", "Z3.2", "Z3.3", "Z3.4"],
        uzrok="zatecene-postavke.sql: r. 41–42 (aplikacija je mogla sve kao db_owner), r. 50 (GRANT SELECT ON SCHEMA::dbo TO public).",
        zasto=[
            "Uloga uloga_aplikacija dobiva samo prava koja T2 aplikacija stvarno koristi – na razini tablica, bez DDL-a i bez DELETE na korisnicima.",
            "Na dnevnik dbo.revizija aplikacija dobiva samo DENY; okidač i dalje upisuje (vidi pitanje ispod).",
            "REVOKE s uloge public zatvara čitanje cijele sheme svakoj prijavi koja uđe u bazu.",
            "Prava se razlikuju po domeni – vidi poglavlje „Razlike po domenama”.",
        ],
        sql="""USE [MedTermin];
GO
CREATE ROLE uloga_aplikacija;
GO
-- Samo ono što aplikacija iz 2. tjedna stvarno radi
{PRAVA}
-- Dnevnik puni isključivo okidač; DENY je eksplicitna zaštita od petljanja
DENY SELECT, INSERT, UPDATE, DELETE ON dbo.revizija TO uloga_aplikacija;

ALTER ROLE uloga_aplikacija ADD MEMBER [medtermin_app];

-- Z3.4: SELECT za sve preko public otvarao je cijelu bazu
REVOKE SELECT ON SCHEMA::dbo FROM public;
GO""",
        test="""USE [MedTermin];
EXECUTE AS USER = N'medtermin_app';
SELECT HAS_PERMS_BY_NAME(N'dbo.rezervacije', N'OBJECT', N'SELECT')  AS citanje_glavne,
       HAS_PERMS_BY_NAME(N'dbo.rezervacije', N'OBJECT', N'INSERT')  AS upis_glavne,
       HAS_PERMS_BY_NAME(N'dbo.korisnici',   N'OBJECT', N'ALTER')   AS mijenjanje_sheme,
       HAS_PERMS_BY_NAME(N'dbo.revizija',    N'OBJECT', N'SELECT')  AS citanje_revizije,
       HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'CREATE TABLE')   AS create_table;
SELECT * FROM sys.fn_my_permissions(N'dbo.revizija', N'OBJECT');
REVERT;

-- Prava uloge public na korisničke objekte i sheme
SELECT p.permission_name, p.class_desc,
       CASE p.class WHEN 3 THEN SCHEMA_NAME(p.major_id) ELSE OBJECT_NAME(p.major_id) END AS objekt
FROM sys.database_permissions AS p
LEFT JOIN sys.objects AS o ON p.class = 1 AND o.object_id = p.major_id
WHERE p.grantee_principal_id = DATABASE_PRINCIPAL_ID(N'public') AND p.state IN ('G', 'W')
  AND ((p.class = 1 AND o.is_ms_shipped = 0) OR p.class = 3);""",
        test_medtermin="""-- Samo MedTermin: okidač i dalje piše u dnevnik iako aplikacija na njemu ima DENY
USE [MedTermin];
EXECUTE AS USER = N'medtermin_app';
INSERT INTO dbo.rezervacije (termin_id, pacijent, napomena, oib)
VALUES (3, N'ana', N'test K3', '48291736504');
REVERT;
SELECT TOP (1) id, radnja, tablica, prijava FROM dbo.revizija ORDER BY id DESC;
DELETE FROM dbo.rezervacije WHERE napomena = N'test K3';""",
        ocekivano=[
            "citanje_glavne = 1, upis_glavne = 1, mijenjanje_sheme = 0, citanje_revizije = 0, create_table = 0.",
            "sys.fn_my_permissions za dbo.revizija ne vraća nijedan redak.",
            "Upit nad pravima uloge public ne vraća nijedan redak.",
            "Test okidača (MedTermin): aplikacija upiše rezervaciju, a u dbo.revizija se pojavi redak INSERT s prijavom medtermin_app; testni redak se zatim briše.",
        ],
        pitanje=("Zašto okidač i dalje može pisati u dbo.revizija iako aplikacija na njoj nema prava (čak ima DENY)?",
                 "Ownership chaining: okidač i tablica dbo.revizija imaju istog vlasnika (dbo). Kad lanac vlasništva nije prekinut, SQL Server ne provjerava prava na objekt koji okidač koristi – ni GRANT ni DENY. Prava se provjeravaju samo na ulazu, na dbo.rezervacije, gdje aplikacija ima INSERT. Zato je okidač ispravno mjesto za dnevnik: aplikacija ga ne može ni čitati ni mijenjati, a zapis ipak nastaje."),
    ),
    dict(
        id="K4", zadatak="Z8", naslov="Očvršćivanje (hardening)",
        provjere=["Z8.1", "Z8.2", "Z8.3"],
        uzrok="zatecene-postavke.sql: r. 24–36 (xp_cmdshell, cross db ownership chaining, Ad Hoc Distributed Queries, clr enabled), r. 49 (GRANT CONNECT TO guest), r. 53 (TRUSTWORTHY ON).",
        zasto=[
            "Radimo ga rano jer zatvara najopasnije putove: TRUSTWORTHY + db_owner + vlasnik sa vodi do sysadmina, a guest pušta u bazu svaku prijavu.",
            "Na Linuxu xp_cmdshell nije podržan – sp_configure javlja grešku 15392. Naredba je u TRY…CATCH da ista skripta radi i na Windowsu, gdje je xp_cmdshell jedan od najopasnijih propusta.",
            "Nakon REVOKE CONNECT FROM guest prijava bi_izvjestaji više ne ulazi u bazu. Ako izvještajima treba pristup, to je zaseban korisnik i uloga sa SELECT samo na ono što trebaju.",
            "Dodatno (provjera to ne traži): vlasnika baze promijenite sa sa na prijavu bez posebnih ovlasti (ALTER AUTHORIZATION ON DATABASE::…).",
        ],
        sql="""USE [MedTermin];
GO
-- Z8.3: prijave bez vlastitog korisnika više ne ulaze u bazu
REVOKE CONNECT FROM guest;
GO
-- Z8.2: TRUSTWORTHY ON + db_owner + vlasnik sa = put do sysadmin
ALTER DATABASE [MedTermin] SET TRUSTWORTHY OFF;
GO
USE master;
GO
EXEC sp_configure N'show advanced options', 1;
RECONFIGURE;
BEGIN TRY  -- na Linuxu xp_cmdshell nije podržan (Msg 15392)
    EXEC sp_configure N'xp_cmdshell', 0;
END TRY
BEGIN CATCH
    PRINT N'xp_cmdshell: ' + ERROR_MESSAGE();
END CATCH;
EXEC sp_configure N'cross db ownership chaining', 0;
EXEC sp_configure N'Ad Hoc Distributed Queries', 0;
EXEC sp_configure N'clr enabled', 0;
RECONFIGURE;
EXEC sp_configure N'show advanced options', 0;
RECONFIGURE;
GO""",
        test="""SELECT name, value_in_use
FROM sys.configurations
WHERE name IN (N'xp_cmdshell', N'cross db ownership chaining', N'Ad Hoc Distributed Queries', N'clr enabled');

SELECT name, is_trustworthy_on, SUSER_SNAME(owner_sid) AS vlasnik
FROM sys.databases WHERE name = N'MedTermin';

USE [MedTermin];
SELECT permission_name, state_desc
FROM sys.database_permissions
WHERE grantee_principal_id = DATABASE_PRINCIPAL_ID(N'guest') AND permission_name = N'CONNECT';

-- bi_izvjestaji (nema korisnika u bazi) više ne može čitati
USE master;
EXECUTE AS LOGIN = N'bi_izvjestaji';
BEGIN TRY
    SELECT TOP (1) username FROM MedTermin.dbo.korisnici;
END TRY
BEGIN CATCH
    SELECT ERROR_NUMBER() AS broj_greske, ERROR_MESSAGE() AS poruka;
END CATCH;
REVERT;""",
        ocekivano=[
            "Sve četiri opcije imaju value_in_use = 0.",
            "MedTermin: is_trustworthy_on = 0 (vlasnik je i dalje sa – vidi dodatnu mjeru).",
            "Upit nad pravima korisnika guest ne vraća nijedan redak.",
            "Pokušaj čitanja kao bi_izvjestaji završava greškom 916 (prijava ne može pristupiti bazi MedTermin).",
        ],
        pitanje=None,
    ),
    dict(
        id="K5", zadatak="Z5 (1. dio)", naslov="Šifriranje stupca OIB",
        provjere=["Z5.3", "Z5.4"],
        uzrok="medtermin.sql, r. 51: dbo.rezervacije.oib VARCHAR(11) u čistom tekstu.",
        zasto=[
            "Hijerarhija ključeva: ključ poslužitelja (SMK) štiti ključ baze (DMK), on certifikat CertOib, a certifikat simetrični AES-256 ključ KljucOib.",
            "Novi stupac oib_sifrirano dobiva šifrirane vrijednosti, a stari stupac oib se briše – čisti tekst ne smije ostati.",
            "Ovaj korak radimo prije RLS-a (K6) jer mijenjamo strukturu tablice.",
            "Uloga aplikacije smije koristiti ključ (upis: ENCRYPTBYKEY nakon OPEN SYMMETRIC KEY; čitanje: DECRYPTBYKEYAUTOCERT).",
            "OIB u dbo.korisnici ostaje, ali se maskira u K6 (tako traži ZADACI.md).",
        ],
        sql=""":setvar KLJUC_LOZINKA "Lozinka-Za_Kljuceve2026"
USE [MedTermin];
GO
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
-- Čisti tekst više ne smije postojati
ALTER TABLE dbo.rezervacije DROP COLUMN oib;
GO
-- Aplikacija smije koristiti ključ za upis i čitanje OIB-a
GRANT VIEW DEFINITION ON SYMMETRIC KEY::KljucOib TO uloga_aplikacija;
GRANT CONTROL ON CERTIFICATE::CertOib TO uloga_aplikacija;
GO""",
        test="""USE [MedTermin];
SELECT COL_LENGTH(N'dbo.rezervacije', N'oib')           AS stari_stupac,
       COL_LENGTH(N'dbo.rezervacije', N'oib_sifrirano') AS novi_stupac;

SELECT name, algorithm_desc, key_length FROM sys.symmetric_keys WHERE name = N'KljucOib';

SELECT TOP (3) id, pacijent, oib_sifrirano,
       CONVERT(VARCHAR(11), DECRYPTBYKEYAUTOCERT(CERT_ID(N'CertOib'), NULL, oib_sifrirano)) AS oib
FROM dbo.rezervacije;""",
        ocekivano=[
            "stari_stupac = NULL (stupac oib ne postoji), novi_stupac = 256.",
            "KljucOib: algorithm_desc = AES_256, key_length = 256.",
            "oib_sifrirano je binarni niz (0x00…), a dešifrirani oib je izvorni OIB (npr. 48291736504 za anu).",
        ],
        pitanje=None,
    ),
    dict(
        id="K6", zadatak="Z4", naslov="Dynamic Data Masking i Row-Level Security",
        provjere=["Z4.1", "Z4.2", "Z4.3", "Z4.4", "Z4.5"],
        uzrok="Maskiranje i RLS ne postoje; podrska je čitala sve kroz db_datareader (zatecene-postavke.sql, r. 45–46), a aplikacija sve retke svih korisnika.",
        zasto=[
            "Maskiranje: tko nema UNMASK vidi aXXX@XXXX.com umjesto e-adrese i *******4051 umjesto OIB-a.",
            "Podrška dobiva SELECT samo na popis stupaca dbo.korisnici – bez password_hash i bez UNMASK.",
            "Aplikacija treba stvarne podatke korisnika pa dobiva granularni UNMASK na dbo.korisnici (SQL Server 2022).",
            "RLS: predikatna funkcija u zasebnoj shemi sigurnost vraća redak samo vlasniku iz SESSION_CONTEXT(N'korisnik'), korisniku s ulogom ADMIN i administratorima baze (koji nisu u uloga_aplikacija). BLOCK predikat sprječava upis zapisa u tuđe ime.",
            "Aplikacija nakon prijave korisnika na istoj konekciji poziva EXEC sp_set_session_context @key = N'korisnik', @value = N'ana', @read_only = 1; read_only sprječava da kasniji kod ili SQL injection promijeni identitet u istoj sesiji.",
        ],
        sql="""USE [MedTermin];
GO
-- Maskiranje: bez UNMASK vidi se aXXX@XXXX.com i *******4051
ALTER TABLE dbo.korisnici ALTER COLUMN email ADD MASKED WITH (FUNCTION = 'email()');
ALTER TABLE dbo.korisnici ALTER COLUMN oib   ADD MASKED WITH (FUNCTION = 'partial(0,"*******",4)');
GO
-- Podrška: samo stupci koji joj trebaju – bez password_hash, bez UNMASK
CREATE ROLE uloga_podrska;
GRANT SELECT ON dbo.korisnici (id, username, email, ime, prezime, uloga, oib) TO uloga_podrska;
ALTER ROLE uloga_podrska ADD MEMBER podrska;
-- Aplikacija treba stvarne podatke korisnika – granularni UNMASK
GRANT UNMASK ON dbo.korisnici TO uloga_aplikacija;
GO
-- RLS: predikatna funkcija u zasebnoj shemi
CREATE SCHEMA sigurnost AUTHORIZATION dbo;
GO
CREATE FUNCTION sigurnost.fn_vlasnik_zapisa (@vlasnik NVARCHAR(50))
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
    SELECT 1 AS dopusteno
    WHERE IS_MEMBER(N'uloga_aplikacija') = 0                                -- RLS vrijedi za aplikaciju, ne za DBA-u
       OR @vlasnik = CAST(SESSION_CONTEXT(N'korisnik') AS NVARCHAR(50))      -- vlastiti zapisi
       OR EXISTS (SELECT 1 FROM dbo.korisnici AS k                           -- ADMIN aplikacije vidi sve
                  WHERE k.username = CAST(SESSION_CONTEXT(N'korisnik') AS NVARCHAR(50))
                    AND k.uloga = 'ADMIN');
GO
CREATE SECURITY POLICY sigurnost.politika_rezervacije
    ADD FILTER PREDICATE sigurnost.fn_vlasnik_zapisa(pacijent) ON dbo.rezervacije,
    ADD BLOCK PREDICATE  sigurnost.fn_vlasnik_zapisa(pacijent) ON dbo.rezervacije AFTER INSERT
    WITH (STATE = ON);
GO""",
        test="""USE [MedTermin];
-- Podrška: maskirani podaci, bez password_hash
EXECUTE AS USER = N'podrska';
SELECT TOP (3) username, email, oib FROM dbo.korisnici;
BEGIN TRY
    SELECT TOP (1) password_hash FROM dbo.korisnici;
END TRY
BEGIN CATCH
    SELECT ERROR_NUMBER() AS broj_greske, ERROR_MESSAGE() AS poruka;
END CATCH;
REVERT;

-- Aplikacija: RLS prema SESSION_CONTEXT
EXECUTE AS USER = N'medtermin_app';
EXEC sp_set_session_context N'korisnik', N'ana';
SELECT id, pacijent FROM dbo.rezervacije;
EXEC sp_set_session_context N'korisnik', NULL;
SELECT COUNT(*) AS bez_konteksta FROM dbo.rezervacije;
EXEC sp_set_session_context N'korisnik', N'admin';
SELECT COUNT(DISTINCT pacijent) AS vlasnika_za_admina FROM dbo.rezervacije;
EXEC sp_set_session_context N'korisnik', NULL;
REVERT;""",
        test_medtermin="""-- Samo MedTermin: BLOCK predikat – ana ne može upisati rezervaciju u Markovo ime
USE [MedTermin];
EXECUTE AS USER = N'medtermin_app';
EXEC sp_set_session_context N'korisnik', N'ana';
BEGIN TRY
    INSERT INTO dbo.rezervacije (termin_id, pacijent, napomena) VALUES (3, N'marko', N'test K6');
END TRY
BEGIN CATCH
    SELECT ERROR_NUMBER() AS broj_greske, ERROR_MESSAGE() AS poruka;
END CATCH;
EXEC sp_set_session_context N'korisnik', NULL;
REVERT;""",
        ocekivano=[
            "Podrška vidi korisnička imena, ali e-adrese kao aXXX@XXXX.com i OIB kao *******xxxx; čitanje password_hash javlja grešku 230 (SELECT permission denied).",
            "Aplikacija kao ana vidi samo Anine rezervacije; bez konteksta bez_konteksta = 0; kao admin vlasnika_za_admina ≥ 2.",
            "Test BLOCK predikata (MedTermin): upis u Markovo ime javlja grešku 33504 (block predicate).",
            "Kao dba_admin (ili sa) i dalje vidite sve retke – RLS vrijedi samo za uloga_aplikacija.",
        ],
        pitanje=("Zašto Dynamic Data Masking nije zamjena za šifriranje ni za kontrolu pristupa?",
                 "DDM mijenja samo prikaz rezultata; podaci su u bazi i dalje u čistom tekstu. Korisnik koji smije čitati stupac može vrijednost pogađati filtrom (WHERE oib LIKE '4829%' ili usporedbama), a maske ne vrijede za korisnike s UNMASK ni za administratore. Zato je DDM dodatni sloj za ljude kojima ne trebaju puni podaci (podrška), uz minimalna prava (Z3) i šifriranje (Z5)."),
    ),
    dict(
        id="K7", zadatak="Z5 (2. dio)", naslov="Transparent Data Encryption (TDE)",
        provjere=["Z5.1", "Z5.2"],
        uzrok="TDE ne postoji (sys.dm_database_encryption_keys je prazan): datoteke baze, log i kopije su nešifrirani.",
        zasto=[
            "TDE šifrira datoteke baze i loga te kopije na disku – štiti od krađe volumena, datoteka ili kopije.",
            "Certifikat je u master i odmah se kopira s privatnim ključem u /var/opt/mssql/backup (mapa backup\\ na računalu). Bez te kopije šifrirana kopija baze je neupotrebljiva na drugom poslužitelju.",
            "Šifriranje teče u pozadini; skripta čeka dok encryption_state ne postane 3.",
            "Napomena za reset: datoteke certifikata u backup\\ ne smiju već postojati – nakon reseta ispraznite backup\\ i audit\\.",
        ],
        sql=""":setvar KLJUC_LOZINKA "Lozinka-Za_Kljuceve2026"
USE master;
GO
IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = N'##MS_DatabaseMasterKey##')
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = N'$(KLJUC_LOZINKA)';
CREATE CERTIFICATE CertTDE_MedTermin WITH SUBJECT = N'TDE – MedTermin';
GO
-- Bez kopije certifikata s privatnim ključem kopija baze je neupotrebljiva!
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
-- Šifriranje teče u pozadini; pričekamo da završi (encryption_state = 3)
DECLARE @i INT = 0;
WHILE @i < 120 AND NOT EXISTS (SELECT 1 FROM sys.dm_database_encryption_keys
                               WHERE database_id = DB_ID(N'MedTermin') AND encryption_state = 3)
BEGIN
    WAITFOR DELAY '00:00:01';
    SET @i += 1;
END;
GO""",
        test="""SELECT DB_NAME(database_id) AS baza, encryption_state_desc, percent_complete, encryptor_type
FROM sys.dm_database_encryption_keys;

SELECT name, pvt_key_last_backup_date
FROM master.sys.certificates WHERE name = N'CertTDE_MedTermin';""",
        ocekivano=[
            "MedTermin: encryption_state_desc = ENCRYPTED, encryptor_type = CERTIFICATE. U popisu je i tempdb – SQL Server ga šifrira čim ijedna baza koristi TDE.",
            "pvt_key_last_backup_date ima današnji datum, a u mapi backup\\ su CertTDE_MedTermin.cer i .pvk.",
        ],
        pitanje=("Od čega TDE štiti, a od čega ne? Što ako izgubite certifikat? Gdje čuvati .pvk i lozinku?",
                 "TDE štiti podatke u mirovanju: ukradeni disk, datoteke baze ili kopiju bez certifikata nitko ne može pročitati. Ne štiti od SQL injectiona ni od ovlaštenih korisnika – za njih su podaci dešifrirani. Bez certifikata (i lozinke privatnog ključa) šifrirana baza i njezine kopije ne mogu se vratiti ni na jednom drugom poslužitelju, pa su podaci izgubljeni. .pvk i lozinku čuvajte odvojeno od kopija i od poslužitelja: u trezoru tajni ili HSM-u (npr. Azure Key Vault), s ograničenim pristupom i postupkom oporavka."),
    ),
    dict(
        id="K8", zadatak="Z7", naslov="Sigurnosne kopije",
        provjere=["Z7.1", "Z7.2", "Z7.3", "Z7.4"],
        uzrok="Ne postoji nijedna kopija (msdb.dbo.backupset je prazan).",
        zasto=[
            "Zaseban certifikat CertBackup za šifriranje kopija – i on se kopira s privatnim ključem izvan poslužitelja.",
            "Puna kopija: šifrirana (AES-256), s kontrolnim zbrojevima (CHECKSUM) i kompresijom.",
            "RESTORE VERIFYONLY … WITH CHECKSUM, LOADHISTORY provjerava čitljivost i zapisuje provjeru u msdb.",
            "Probni povrat pod drugim imenom (MedTermin_ProbniRestore) dokazuje da se iz kopije stvarno može vratiti baza; logička imena datoteka daje RESTORE FILELISTONLY.",
        ],
        sql=""":setvar KLJUC_LOZINKA "Lozinka-Za_Kljuceve2026"
USE master;
GO
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
RESTORE VERIFYONLY
    FROM DISK = N'/var/opt/mssql/backup/MedTermin_puna.bak'
    WITH CHECKSUM, LOADHISTORY;
GO
-- Logička imena datoteka za MOVE
RESTORE FILELISTONLY FROM DISK = N'/var/opt/mssql/backup/MedTermin_puna.bak';
GO
RESTORE DATABASE [MedTermin_ProbniRestore]
    FROM DISK = N'/var/opt/mssql/backup/MedTermin_puna.bak'
    WITH MOVE N'MedTermin'     TO N'/var/opt/mssql/data/MedTermin_ProbniRestore.mdf',
         MOVE N'MedTermin_log' TO N'/var/opt/mssql/data/MedTermin_ProbniRestore_log.ldf',
         CHECKSUM, RECOVERY;
GO""",
        test="""SELECT TOP (1) database_name, backup_finish_date, key_algorithm, encryptor_type, has_backup_checksums
FROM msdb.dbo.backupset
WHERE database_name = N'MedTermin'
ORDER BY backup_finish_date DESC;

SELECT TOP (3) destination_database_name, restore_date, restore_type
FROM msdb.dbo.restorehistory
ORDER BY restore_date DESC;

SELECT COUNT(*) AS korisnika_u_probnoj_bazi FROM [MedTermin_ProbniRestore].dbo.korisnici;""",
        ocekivano=[
            "Zadnja kopija: key_algorithm = aes_256, encryptor_type = CERTIFICATE, has_backup_checksums = 1.",
            "msdb.dbo.restorehistory: redak tipa V (RESTORE VERIFYONLY) i redak tipa D za MedTermin_ProbniRestore.",
            "Probna baza je čitljiva: korisnika_u_probnoj_bazi = 4 (ana, marko, dr.horvat, admin).",
        ],
        pitanje=("Zašto je neisprobana kopija gotovo jednako loša kao nikakva? Što još nedostaje za pravu strategiju?",
                 "Kopija koja se ne može vratiti (oštećena, bez certifikata, nepoznat postupak) otkrije se tek u incidentu – kad je prekasno. Tek probni povrat dokazuje da kopija vrijedi i koliko traje oporavak. Za pravu strategiju nedostaju: model oporavka FULL s diferencijalnim i log kopijama prema dogovorenom RPO-u, kopija izvan poslužitelja i nepromjenjiva kopija (pravilo 3-2-1), definirani RPO i RTO, redoviti probni povrati, nadzor uspješnosti kopija i odvojeno čuvanje certifikata."),
    ),
    dict(
        id="K9", zadatak="Z2.4", naslov="Gašenje sa i nova administratorska prijava u .env",
        provjere=["Z2.4"],
        uzrok="sa je jedina administratorska prijava i koristi se za sve.",
        zasto=[
            "Prije ovog koraka u SSMS-u otvorite novu konekciju kao dba_admin i provjerite da radi.",
            "Nakon gašenja sa u .env upišite ADMIN_LOGIN=dba_admin i ADMIN_PASSWORD (lozinka iz K2), a novu lozinku aplikacije kao APP_LOZINKA, pa pokrenite docker compose up -d. Healthcheck, init i provjera tada koriste vašu prijavu.",
            "Bez toga kontejner postaje unhealthy, a provjera se ne pokreće (u reviziji se vide neuspjele prijave za sa svakih 10 sekundi).",
        ],
        sql="""USE master;
GO
ALTER LOGIN sa DISABLE;
GO""",
        test="""SELECT name, is_disabled, is_policy_checked
FROM sys.sql_logins
WHERE name IN (N'sa', N'dba_admin');""",
        ocekivano=[
            "sa: is_disabled = 1; dba_admin: is_disabled = 0, is_policy_checked = 1.",
            "Prijava u SSMS-u kao sa javlja Login failed; kao dba_admin radi.",
        ],
        pitanje=None,
    ),
]

ZAVRSNO = dict(
    env="""ADMIN_LOGIN=dba_admin
ADMIN_PASSWORD=Lozinka-Za_DbaAdmina2026
APP_LOZINKA=Nova-Lozinka_Aplikacije2026""",
    naredbe="""docker compose up -d
docker compose --profile provjera run --rm provjera
docker compose --profile aplikacija run --rm aplikacija-python""",
)


def kao_json():
    return dict(Z1=Z1, KOMBINACIJE=KOMBINACIJE, KORACI=KORACI, ZAVRSNO=ZAVRSNO, DOMENE=DOMENE, PRAVA=PRAVA)


if __name__ == "__main__":
    import sys
    json.dump(kao_json(), open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
