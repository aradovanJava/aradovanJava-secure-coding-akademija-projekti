/* Automatska provjera zadataka – Sigurnost baza podataka (3. tjedan, SQL Server 2022).
   Pokretanje:  docker compose --profile provjera run --rm provjera
   Varijable (postavlja ih provjera.sh): BAZA, GLAVNA, VLASNIK, APP, DOMENA.
   Provjera ne mijenja bazu. Izvodi samo nekoliko SELECT upita u ime aplikacijskog korisnika
   i podrške (EXECUTE AS USER) – ti se upiti vide i u reviziji (Z6). */
:on error exit
SET NOCOUNT ON;
IF ISNULL(IS_SRVROLEMEMBER(N'sysadmin'), 0) = 0
    RAISERROR(N'Provjeru treba pokrenuti prijavom iz uloge sysadmin (ADMIN_LOGIN / ADMIN_PASSWORD u .env).', 16, 1);
IF DB_ID(N'$(BAZA)') IS NULL
    RAISERROR(N'Baza $(BAZA) ne postoji. Je li init završio? Pogledajte: docker compose logs init', 16, 1);
GO
USE [$(BAZA)];
GO
CREATE TABLE #r (
    rb      INT IDENTITY(1,1) PRIMARY KEY,
    zadatak VARCHAR(8)     NOT NULL,
    opis    NVARCHAR(400)  NOT NULL,
    ok      BIT            NOT NULL,
    savjet  NVARCHAR(1000) NULL
);
GO
CREATE PROCEDURE #dodaj @z VARCHAR(8), @opis NVARCHAR(400), @ok BIT, @savjet NVARCHAR(1000)
AS
    INSERT INTO #r (zadatak, opis, ok, savjet) VALUES (@z, @opis, ISNULL(@ok, 0), @savjet);
GO
SET NOCOUNT ON;
DECLARE @ja SYSNAME = USER_NAME(), @ok BIT, @s NVARCHAR(1000), @sql NVARCHAR(MAX),
        @n INT, @m INT, @k INT, @x INT,
        @oib VARCHAR(50), @email NVARCHAR(200), @cert SYSNAME, @pvk INT,
        @putanja NVARCHAR(400), @uzorak NVARCHAR(500), @dbspec INT;

/* ================= Z2 – prijave i korisnici ================= */
SET @ok = 0;
SET @s = N'Prijava $(APP) ne postoji – aplikacija se mora moći spojiti, nemojte je brisati.';
IF EXISTS (SELECT 1 FROM sys.sql_logins WHERE name = N'$(APP)')
BEGIN
    SELECT @ok = CASE WHEN l.is_policy_checked = 1 AND l.is_disabled = 0
        AND NOT EXISTS (SELECT 1
                        FROM (VALUES (N'$(DOMENA)123'), (N'$(DOMENA)'), (N'$(APP)'), (N'$(BAZA)123!'),
                                     (N'$(DOMENA)2024!'), (N'$(DOMENA)2026!'), (N'Lozinka123!'),
                                     (N'Password1!'), (N'P@ssw0rd'), (N'Sluzba-Pomoci24')) AS s(lozinka)
                        WHERE PWDCOMPARE(s.lozinka, l.password_hash) = 1)
        THEN 1 ELSE 0 END
    FROM sys.sql_logins AS l WHERE l.name = N'$(APP)';
    SET @s = N'ALTER LOGIN [$(APP)] WITH PASSWORD = N''<nova jaka lozinka>''; pa ALTER LOGIN [$(APP)] WITH CHECK_POLICY = ON; (prijava mora ostati omogućena).';
END;
EXEC #dodaj 'Z2.1', N'Aplikacijska prijava $(APP) ima novu jaku lozinku i CHECK_POLICY = ON', @ok, @s;

SET @ok = CASE WHEN SUSER_ID(N'$(APP)') IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM sys.server_role_members AS rm
                    JOIN sys.server_principals AS r ON r.principal_id = rm.role_principal_id
                    WHERE rm.member_principal_id = SUSER_ID(N'$(APP)') AND r.is_fixed_role = 1)
    AND NOT EXISTS (SELECT 1 FROM sys.server_permissions AS p
                    WHERE p.grantee_principal_id = SUSER_ID(N'$(APP)') AND p.state IN ('G', 'W')
                      AND p.permission_name IN (N'CONTROL SERVER', N'ALTER ANY LOGIN', N'IMPERSONATE ANY LOGIN', N'ALTER ANY DATABASE'))
    THEN 1 ELSE 0 END;
EXEC #dodaj 'Z2.2', N'Aplikacijska prijava nije u ulogama poslužitelja (sysadmin…) i nema CONTROL SERVER', @ok,
    N'ALTER SERVER ROLE sysadmin DROP MEMBER [$(APP)]; – aplikaciji ne trebaju prava na razini poslužitelja.';

SET @ok = CASE WHEN DATABASE_PRINCIPAL_ID(N'$(APP)') IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM sys.database_role_members AS rm
                    JOIN sys.database_principals AS r ON r.principal_id = rm.role_principal_id
                    WHERE rm.member_principal_id = DATABASE_PRINCIPAL_ID(N'$(APP)') AND r.is_fixed_role = 1)
    AND NOT EXISTS (SELECT 1 FROM sys.database_permissions AS p
                    WHERE p.grantee_principal_id = DATABASE_PRINCIPAL_ID(N'$(APP)') AND p.class = 0 AND p.state IN ('G', 'W')
                      AND p.permission_name IN (N'CONTROL', N'ALTER', N'ALTER ANY USER', N'ALTER ANY ROLE', N'ALTER ANY SCHEMA'))
    THEN 1 ELSE 0 END;
EXEC #dodaj 'Z2.3', N'Aplikacijski korisnik nije u fiksnim ulogama baze (db_owner, db_datareader…)', @ok,
    N'ALTER ROLE db_owner DROP MEMBER [$(APP)]; prava dodijelite preko vlastite uloge (Z3).';

SELECT @n = COUNT(*) FROM sys.server_principals AS p
WHERE p.type = 'S' AND p.is_disabled = 0 AND p.sid <> 0x01 AND p.name NOT LIKE N'##%'
  AND p.name <> N'$(APP)' AND IS_SRVROLEMEMBER(N'sysadmin', p.name) = 1;
SET @ok = CASE WHEN (SELECT is_disabled FROM sys.server_principals WHERE sid = 0x01) = 1 AND @n >= 1 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z2.4', N'Postoji vlastita administratorska prijava, a sa je onemogućen', @ok,
    N'CREATE LOGIN <ime> … CHECK_POLICY = ON; ALTER SERVER ROLE sysadmin ADD MEMBER <ime>; ALTER LOGIN sa DISABLE; pa upišite ADMIN_LOGIN/ADMIN_PASSWORD u .env i docker compose up -d.';

SET @ok = CASE WHEN DATABASE_PRINCIPAL_ID(N'podrska') IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM sys.database_role_members AS rm
                    JOIN sys.database_principals AS r ON r.principal_id = rm.role_principal_id
                    WHERE rm.member_principal_id = DATABASE_PRINCIPAL_ID(N'podrska') AND r.is_fixed_role = 1)
    THEN 1 ELSE 0 END;
EXEC #dodaj 'Z2.5', N'Korisnik podrska nije u db_datareader niti drugim fiksnim ulogama', @ok,
    N'ALTER ROLE db_datareader DROP MEMBER podrska; (korisnika podrska nemojte brisati – treba za Z4).';

/* ================= Z3 – najmanje ovlasti ================= */
SET @ok = 0;
IF ISNULL(IS_ROLEMEMBER(N'uloga_aplikacija', N'$(APP)'), 0) = 1
BEGIN
BEGIN TRY
    EXECUTE AS USER = N'$(APP)';
    SET @ok = CASE WHEN HAS_PERMS_BY_NAME(N'dbo.$(GLAVNA)', N'OBJECT', N'SELECT') = 1
                    AND HAS_PERMS_BY_NAME(N'dbo.$(GLAVNA)', N'OBJECT', N'INSERT') = 1
                    AND HAS_PERMS_BY_NAME(N'dbo.korisnici', N'OBJECT', N'SELECT') = 1 THEN 1 ELSE 0 END;
    REVERT;
END TRY
BEGIN CATCH
    IF USER_NAME() <> @ja REVERT;
    SET @ok = 0;
END CATCH;
END;
EXEC #dodaj 'Z3.1', N'Uloga uloga_aplikacija postoji, $(APP) je član i aplikacija i dalje radi (SELECT/INSERT)', @ok,
    N'CREATE ROLE uloga_aplikacija; GRANT … ON dbo.<tablica> TO uloga_aplikacija; ALTER ROLE uloga_aplikacija ADD MEMBER [$(APP)];';

SET @ok = 0;
BEGIN TRY
    EXECUTE AS USER = N'$(APP)';
    SET @ok = CASE WHEN ISNULL(HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'CREATE TABLE'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'ALTER'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'ALTER ANY USER'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(N'dbo', N'SCHEMA', N'ALTER'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(N'dbo.korisnici', N'OBJECT', N'ALTER'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(N'dbo.korisnici', N'OBJECT', N'CONTROL'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(N'dbo.$(GLAVNA)', N'OBJECT', N'ALTER'), 0) = 0 THEN 1 ELSE 0 END;
    REVERT;
END TRY
BEGIN CATCH
    IF USER_NAME() <> @ja REVERT;
    SET @ok = 0;
END CATCH;
EXEC #dodaj 'Z3.2', N'Aplikacijski korisnik ne može mijenjati shemu (CREATE/ALTER/DROP, ALTER ANY USER)', @ok,
    N'Aplikacija ne smije imati db_owner/db_ddladmin ni GRANT ALTER/CONTROL; DDL radi administrator (ili alat za migracije s posebnom prijavom).';

SET @ok = 0;
IF OBJECT_ID(N'dbo.revizija') IS NOT NULL
BEGIN
BEGIN TRY
    EXECUTE AS USER = N'$(APP)';
    SET @ok = CASE WHEN ISNULL(HAS_PERMS_BY_NAME(N'dbo.revizija', N'OBJECT', N'SELECT'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(N'dbo.revizija', N'OBJECT', N'UPDATE'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(N'dbo.revizija', N'OBJECT', N'DELETE'), 0) = 0 THEN 1 ELSE 0 END;
    REVERT;
END TRY
BEGIN CATCH
    IF USER_NAME() <> @ja REVERT;
    SET @ok = 0;
END CATCH;
END;
EXEC #dodaj 'Z3.3', N'Aplikacija ne može čitati ni mijenjati dnevnik dbo.revizija (puni ga samo okidač)', @ok,
    N'Ne dodjeljujte prava na dbo.revizija (po želji DENY SELECT, UPDATE, DELETE … TO uloga_aplikacija); okidač i dalje upisuje zbog ownership chaininga.';

SET @s = NULL;
SELECT @s = STRING_AGG(CONVERT(NVARCHAR(200), p.permission_name + N' na ' +
            CASE p.class WHEN 0 THEN N'bazi' WHEN 3 THEN N'shemi ' + SCHEMA_NAME(p.major_id) ELSE OBJECT_NAME(p.major_id) END), N', ')
FROM sys.database_permissions AS p
LEFT JOIN sys.objects AS o ON p.class = 1 AND o.object_id = p.major_id
WHERE p.grantee_principal_id = 0 AND p.state IN ('G', 'W')
  AND ((p.class = 1 AND o.is_ms_shipped = 0) OR p.class = 3
       OR (p.class = 0 AND p.permission_name IN (N'SELECT', N'INSERT', N'UPDATE', N'DELETE', N'EXECUTE', N'CONTROL', N'ALTER')));
SET @ok = CASE WHEN @s IS NULL THEN 1 ELSE 0 END;
SET @s = N'public = svi korisnici baze (i guest). Pronađeno: ' + ISNULL(@s, N'-') + N'. Koristite REVOKE … FROM public.';
EXEC #dodaj 'Z3.4', N'Uloga public nema prava na korisničke objekte i sheme', @ok, @s;

/* ================= Z4 – RLS i maskiranje ================= */
SET @ok = CASE WHEN EXISTS (SELECT 1 FROM sys.security_policies AS p
                            JOIN sys.security_predicates AS sp ON sp.object_id = p.object_id
                            WHERE p.is_enabled = 1 AND sp.predicate_type = 0
                              AND sp.target_object_id = OBJECT_ID(N'dbo.$(GLAVNA)')) THEN 1 ELSE 0 END;
EXEC #dodaj 'Z4.1', N'Na dbo.$(GLAVNA) postoji uključena sigurnosna politika s FILTER predikatom (RLS)', @ok,
    N'CREATE FUNCTION … WITH SCHEMABINDING; CREATE SECURITY POLICY … ADD FILTER PREDICATE …($(VLASNIK)) ON dbo.$(GLAVNA) WITH (STATE = ON);';

SELECT @n = NULL, @m = NULL, @k = NULL, @x = NULL;
SET @ok = 0;
SET @s = N'Filtrirajte po $(VLASNIK) = SESSION_CONTEXT(N''korisnik''); korisnici s ulogom ADMIN vide sve; bez konteksta aplikacija ne vidi ništa.';
BEGIN TRY
    EXECUTE AS USER = N'$(APP)';
    EXEC sp_set_session_context N'korisnik', N'ana';
    EXEC sp_executesql N'SELECT @a = COUNT(CASE WHEN $(VLASNIK) = N''ana'' THEN 1 END), @b = COUNT(CASE WHEN $(VLASNIK) <> N''ana'' THEN 1 END) FROM dbo.$(GLAVNA);',
         N'@a INT OUTPUT, @b INT OUTPUT', @a = @n OUTPUT, @b = @m OUTPUT;
    EXEC sp_set_session_context N'korisnik', NULL;
    EXEC sp_executesql N'SELECT @a = COUNT(*) FROM dbo.$(GLAVNA);', N'@a INT OUTPUT', @a = @k OUTPUT;
    EXEC sp_set_session_context N'korisnik', N'admin';
    EXEC sp_executesql N'SELECT @a = COUNT(DISTINCT $(VLASNIK)) FROM dbo.$(GLAVNA);', N'@a INT OUTPUT', @a = @x OUTPUT;
    EXEC sp_set_session_context N'korisnik', NULL;
    REVERT;
    IF @n >= 1 AND @m = 0 AND @k = 0 AND @x >= 2 SET @ok = 1;
    ELSE SET @s = CONCAT(N'Aplikacija kao ana vidi svojih ', @n, N' i tuđih ', @m, N' zapisa; bez konteksta ', @k,
                         N'; kao admin ', @x, N' vlasnika. Očekivano: ≥1, 0, 0, ≥2. ', @s);
END TRY
BEGIN CATCH
    IF USER_NAME() <> @ja REVERT;
    SET @s = N'Upit kao $(APP) nije uspio: ' + ERROR_MESSAGE();
END CATCH;
EXEC sp_set_session_context N'korisnik', NULL;
EXEC #dodaj 'Z4.2', N'RLS radi: aplikacija vidi samo zapise korisnika iz SESSION_CONTEXT(korisnik), ADMIN sve', @ok, @s;

SELECT @n = COUNT(*) FROM sys.masked_columns
WHERE object_id = OBJECT_ID(N'dbo.korisnici') AND is_masked = 1 AND name IN (N'oib', N'email');
SET @ok = CASE WHEN @n = 2 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z4.3', N'Stupci korisnici.oib i korisnici.email su maskirani (Dynamic Data Masking)', @ok,
    N'ALTER TABLE dbo.korisnici ALTER COLUMN email ADD MASKED WITH (FUNCTION = ''email()''); isto za oib, npr. partial(…).';

SELECT @oib = NULL, @email = NULL, @ok = 0;
SET @s = N'podrska mora dobiti SELECT na korisnike (bez password_hash), ali bez UNMASK – vidi maskirane vrijednosti.';
BEGIN TRY
    EXECUTE AS USER = N'podrska';
    EXEC sp_executesql N'SELECT @o = CONVERT(VARCHAR(50), oib), @e = email FROM dbo.korisnici WHERE username = N''ana'';',
         N'@o VARCHAR(50) OUTPUT, @e NVARCHAR(200) OUTPUT', @o = @oib OUTPUT, @e = @email OUTPUT;
    REVERT;
    IF @oib IS NOT NULL AND @oib <> '48291736504' AND @email IS NOT NULL AND @email <> N'ana@primjer.hr' SET @ok = 1;
    ELSE SET @s = N'podrska vidi oib=' + ISNULL(@oib, N'NULL') + N', email=' + ISNULL(@email, N'NULL') + N'. ' + @s;
END TRY
BEGIN CATCH
    IF USER_NAME() <> @ja REVERT;
    SET @s = N'Upit kao podrska nije uspio (' + ERROR_MESSAGE() + N'). ' + @s;
END CATCH;
EXEC #dodaj 'Z4.4', N'Podrška čita korisnike, ali vidi maskirani OIB i e-mail', @ok, @s;

SET @ok = 0;
BEGIN TRY
    EXECUTE AS USER = N'podrska';
    SET @ok = CASE WHEN ISNULL(HAS_PERMS_BY_NAME(N'dbo.korisnici', N'OBJECT', N'SELECT', N'password_hash', N'COLUMN'), 0) = 0
                    AND ISNULL(HAS_PERMS_BY_NAME(DB_NAME(), N'DATABASE', N'UNMASK'), 0) = 0 THEN 1 ELSE 0 END;
    REVERT;
END TRY
BEGIN CATCH
    IF USER_NAME() <> @ja REVERT;
    SET @ok = 0;
END CATCH;
EXEC #dodaj 'Z4.5', N'Podrška ne može čitati password_hash i nema UNMASK', @ok,
    N'GRANT SELECT ON dbo.korisnici (id, username, …) – popišite stupce bez password_hash; provjerite i prava uloge public.';

/* ================= Z5 – šifriranje ================= */
SET @ok = CASE WHEN EXISTS (SELECT 1 FROM sys.dm_database_encryption_keys
                            WHERE database_id = DB_ID(N'$(BAZA)') AND encryption_state = 3) THEN 1 ELSE 0 END;
EXEC #dodaj 'Z5.1', N'Baza $(BAZA) je šifrirana TDE-om (encryption_state = 3)', @ok,
    N'U master: CREATE MASTER KEY, CREATE CERTIFICATE; u bazi: CREATE DATABASE ENCRYPTION KEY … BY SERVER CERTIFICATE; ALTER DATABASE … SET ENCRYPTION ON;';

SET @pvk = -1;
BEGIN TRY
    EXEC sp_executesql N'SELECT @n = COUNT(*) FROM sys.dm_os_enumerate_filesystem(N''/var/opt/mssql/backup/'', N''*.pvk'');',
         N'@n INT OUTPUT', @n = @pvk OUTPUT;
END TRY
BEGIN CATCH
    SET @pvk = -1;
END CATCH;
SET @ok = CASE WHEN EXISTS (SELECT 1 FROM sys.dm_database_encryption_keys AS k
                            JOIN master.sys.certificates AS c ON c.thumbprint = k.encryptor_thumbprint
                            WHERE k.database_id = DB_ID(N'$(BAZA)') AND c.pvt_key_last_backup_date IS NOT NULL)
                AND @pvk <> 0 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z5.2', N'TDE certifikat je sigurnosno kopiran s privatnim ključem u ./backup', @ok,
    N'USE master; BACKUP CERTIFICATE <cert> TO FILE = ''/var/opt/mssql/backup/<cert>.cer'' WITH PRIVATE KEY (FILE = ''….pvk'', ENCRYPTION BY PASSWORD = ''…''); – bez toga se kopija baze ne može vratiti na drugi poslužitelj.';

SET @cert = NULL;
SELECT TOP 1 @cert = c.name
FROM sys.symmetric_keys AS k
JOIN sys.key_encryptions AS e ON e.key_id = k.symmetric_key_id
JOIN sys.certificates AS c ON c.thumbprint = e.thumbprint
WHERE k.name NOT LIKE N'##%' AND k.algorithm_desc LIKE N'AES%'
  AND (e.crypt_type = 'EPUC' OR e.crypt_type_desc LIKE N'%CERTIFICATE%');
SET @ok = CASE WHEN @cert IS NOT NULL THEN 1 ELSE 0 END;
EXEC #dodaj 'Z5.3', N'U bazi postoji AES simetrični ključ zaštićen certifikatom', @ok,
    N'CREATE MASTER KEY …; CREATE CERTIFICATE …; CREATE SYMMETRIC KEY … WITH ALGORITHM = AES_256 ENCRYPTION BY CERTIFICATE …;';

SELECT @ok = 0, @n = 0, @m = 0;
SET @s = N'Dodajte stupac oib_sifrirano VARBINARY(256) u dbo.$(GLAVNA), napunite ga s ENCRYPTBYKEY(KEY_GUID(…), oib), a stupac oib uklonite (ili postavite na NULL).';
IF @cert IS NOT NULL
   AND EXISTS (SELECT 1 FROM sys.columns WHERE object_id = OBJECT_ID(N'dbo.$(GLAVNA)')
               AND name = N'oib_sifrirano' AND TYPE_NAME(system_type_id) = N'varbinary')
BEGIN
BEGIN TRY
    IF COL_LENGTH(N'dbo.$(GLAVNA)', N'oib') IS NOT NULL
        EXEC sp_executesql N'SELECT @a = COUNT(*) FROM dbo.$(GLAVNA) WHERE NULLIF(oib, '''') IS NOT NULL;', N'@a INT OUTPUT', @a = @n OUTPUT;
    EXEC sp_executesql N'SELECT @a = COUNT(*) FROM dbo.$(GLAVNA) AS t
        CROSS APPLY (SELECT COALESCE(DECRYPTBYKEYAUTOCERT(CERT_ID(@c), NULL, t.oib_sifrirano),
                                     DECRYPTBYKEYAUTOCERT(CERT_ID(@c), NULL, t.oib_sifrirano, 1, CONVERT(VARBINARY(8), t.id))) AS d) AS x
        WHERE CONVERT(VARCHAR(11), x.d) = ''48291736504'' OR CONVERT(NVARCHAR(11), x.d) = N''48291736504'';',
         N'@c SYSNAME, @a INT OUTPUT', @c = @cert, @a = @m OUTPUT;
    IF @n = 0 AND @m >= 1 SET @ok = 1;
    ELSE SET @s = CONCAT(N'Redaka s OIB-om u čistom tekstu: ', @n, N'; redaka u kojima se oib_sifrirano dešifrira u Anin OIB: ', @m, N'. ', @s);
END TRY
BEGIN CATCH
    SET @s = N'Dešifriranje nije uspjelo: ' + ERROR_MESSAGE();
END CATCH;
END;
EXEC #dodaj 'Z5.4', N'OIB u dbo.$(GLAVNA) je šifriran (oib_sifrirano), a čisti tekst uklonjen', @ok, @s;

/* ================= Z6 – revizija (auditing) ================= */
SET @putanja = NULL;
SELECT TOP 1 @putanja = a.log_file_path
FROM sys.server_file_audits AS a
JOIN sys.dm_server_audit_status AS st ON st.audit_id = a.audit_id
WHERE st.status_desc = N'STARTED' AND a.log_file_path LIKE N'/var/opt/mssql/audit%';
SET @ok = CASE WHEN @putanja IS NOT NULL THEN 1 ELSE 0 END;
EXEC #dodaj 'Z6.1', N'Server audit zapisuje u /var/opt/mssql/audit (./audit) i uključen je', @ok,
    N'CREATE SERVER AUDIT … TO FILE (FILEPATH = ''/var/opt/mssql/audit/''); ALTER SERVER AUDIT … WITH (STATE = ON);';

SELECT @n = COUNT(DISTINCT d.audit_action_name)
FROM sys.server_audit_specifications AS s
JOIN sys.server_audit_specification_details AS d ON d.server_specification_id = s.server_specification_id
JOIN sys.server_audits AS a ON a.audit_guid = s.audit_guid
JOIN sys.dm_server_audit_status AS st ON st.audit_id = a.audit_id
WHERE s.is_state_enabled = 1 AND st.status_desc = N'STARTED'
  AND d.audit_action_name IN (N'FAILED_LOGIN_GROUP', N'SUCCESSFUL_LOGIN_GROUP');
SET @ok = CASE WHEN @n = 2 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z6.2', N'Server audit specifikacija bilježi neuspjele i uspješne prijave', @ok,
    N'CREATE SERVER AUDIT SPECIFICATION … ADD (FAILED_LOGIN_GROUP), ADD (SUCCESSFUL_LOGIN_GROUP) WITH (STATE = ON);';

SET @dbspec = NULL;
SELECT TOP 1 @dbspec = s.database_specification_id
FROM sys.database_audit_specifications AS s
JOIN sys.server_audits AS a ON a.audit_guid = s.audit_guid
JOIN sys.dm_server_audit_status AS st ON st.audit_id = a.audit_id
WHERE s.is_state_enabled = 1 AND st.status_desc = N'STARTED';
SELECT @n = COUNT(*) FROM (VALUES (N'korisnici'), (N'$(GLAVNA)')) AS t(ime)
WHERE EXISTS (SELECT 1 FROM sys.database_audit_specification_details AS d
              WHERE d.database_specification_id = @dbspec
                AND (d.audit_action_name = N'SCHEMA_OBJECT_ACCESS_GROUP'
                     OR (d.audit_action_name = N'SELECT'
                         AND ((d.class = 1 AND d.major_id = OBJECT_ID(N'dbo.' + t.ime))
                              OR (d.class = 3 AND d.major_id = SCHEMA_ID(N'dbo')) OR d.class = 0))));
SET @ok = CASE WHEN @n = 2 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z6.3', N'Database audit specifikacija bilježi SELECT nad dbo.korisnici i dbo.$(GLAVNA)', @ok,
    N'CREATE DATABASE AUDIT SPECIFICATION … ADD (SELECT ON OBJECT::dbo.korisnici BY public), ADD (SELECT ON OBJECT::dbo.$(GLAVNA) BY public) … WITH (STATE = ON);';

SELECT @n = COUNT(DISTINCT d.audit_action_name)
FROM sys.database_audit_specification_details AS d
WHERE d.database_specification_id = @dbspec
  AND d.audit_action_name IN (N'DATABASE_PERMISSION_CHANGE_GROUP', N'SCHEMA_OBJECT_PERMISSION_CHANGE_GROUP',
                              N'DATABASE_ROLE_MEMBER_CHANGE_GROUP');
SET @ok = CASE WHEN @n = 3 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z6.4', N'Database audit specifikacija bilježi promjene prava i članstva u ulogama', @ok,
    N'ADD (DATABASE_PERMISSION_CHANGE_GROUP), ADD (SCHEMA_OBJECT_PERMISSION_CHANGE_GROUP), ADD (DATABASE_ROLE_MEMBER_CHANGE_GROUP)';

SELECT @ok = 0, @n = 0;
SET @s = N'U audit datoteci nema SELECT zapisa (action_id = SL) nad osjetljivim tablicama ove baze.';
IF @putanja IS NOT NULL
BEGIN
BEGIN TRY
    EXEC sp_executesql N'SELECT @a = COUNT(*) FROM dbo.korisnici;', N'@a INT OUTPUT', @a = @x OUTPUT;
    WAITFOR DELAY '00:00:03';
    SET @uzorak = @putanja + CASE WHEN RIGHT(@putanja, 1) = N'/' THEN N'' ELSE N'/' END + N'*.sqlaudit';
    EXEC sp_executesql N'SELECT @a = COUNT(*) FROM sys.fn_get_audit_file(@p, DEFAULT, DEFAULT)
                         WHERE action_id = ''SL'' AND database_name = N''$(BAZA)''
                           AND object_name IN (N''korisnici'', N''$(GLAVNA)'');',
         N'@p NVARCHAR(500), @a INT OUTPUT', @p = @uzorak, @a = @n OUTPUT;
    IF @n >= 1 SET @ok = 1;
END TRY
BEGIN CATCH
    SET @s = N'Čitanje audit datoteke nije uspjelo: ' + ERROR_MESSAGE();
END CATCH;
END;
EXEC #dodaj 'Z6.5', N'Audit datoteka stvarno sadrži SELECT zapise nad osjetljivim tablicama', @ok, @s;

/* ================= Z7 – sigurnosne kopije ================= */
SELECT @n = COUNT(*), @m = SUM(CASE WHEN b.has_backup_checksums = 1 THEN 1 ELSE 0 END)
FROM msdb.dbo.backupset AS b
JOIN msdb.dbo.backupmediafamily AS f ON f.media_set_id = b.media_set_id
WHERE b.database_name = N'$(BAZA)' AND b.type = 'D' AND b.encryptor_type IS NOT NULL
  AND f.physical_device_name LIKE N'/var/opt/mssql/backup/%';
SET @ok = CASE WHEN @n >= 1 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z7.1', N'Postoji puna sigurnosna kopija baze u ./backup, šifrirana (WITH ENCRYPTION)', @ok,
    N'BACKUP DATABASE … TO DISK = ''/var/opt/mssql/backup/….bak'' WITH ENCRYPTION (ALGORITHM = AES_256, SERVER CERTIFICATE = …), CHECKSUM;';
SET @ok = CASE WHEN ISNULL(@m, 0) >= 1 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z7.2', N'Šifrirana kopija ima kontrolne zbrojeve (WITH CHECKSUM)', @ok,
    N'Dodajte CHECKSUM u WITH dio naredbe BACKUP DATABASE.';

SELECT @n = COUNT(*)
FROM msdb.dbo.restorehistory AS r
JOIN msdb.dbo.backupset AS b ON b.backup_set_id = r.backup_set_id
WHERE r.restore_type = 'V' AND b.database_name = N'$(BAZA)';
SET @ok = CASE WHEN @n >= 1 THEN 1 ELSE 0 END;
EXEC #dodaj 'Z7.3', N'Kopija je provjerena s RESTORE VERIFYONLY (zabilježeno u msdb)', @ok,
    N'RESTORE VERIFYONLY FROM DISK = ''…'' WITH CHECKSUM, LOADHISTORY; (LOADHISTORY zapisuje provjeru u msdb.dbo.restorehistory).';

SELECT @ok = 0, @n = 0;
IF EXISTS (SELECT 1 FROM sys.databases WHERE name = N'$(BAZA)_ProbniRestore' AND state_desc = N'ONLINE')
   AND EXISTS (SELECT 1 FROM msdb.dbo.restorehistory AS r
               JOIN msdb.dbo.backupset AS b ON b.backup_set_id = r.backup_set_id
               WHERE r.destination_database_name = N'$(BAZA)_ProbniRestore' AND r.restore_type = 'D'
                 AND b.database_name = N'$(BAZA)')
BEGIN
BEGIN TRY
    EXEC sp_executesql N'SELECT @a = COUNT(*) FROM [$(BAZA)_ProbniRestore].dbo.korisnici;', N'@a INT OUTPUT', @a = @n OUTPUT;
    IF @n >= 1 SET @ok = 1;
END TRY
BEGIN CATCH
    SET @ok = 0;
END CATCH;
END;
EXEC #dodaj 'Z7.4', N'Probni povrat: baza $(BAZA)_ProbniRestore vraćena iz kopije i čitljiva', @ok,
    N'RESTORE FILELISTONLY …; RESTORE DATABASE [$(BAZA)_ProbniRestore] FROM DISK = ''…'' WITH MOVE … TO ''/var/opt/mssql/data/…'', MOVE …, CHECKSUM;';

/* ================= Z8 – očvršćivanje ================= */
SET @s = NULL;
SELECT @s = STRING_AGG(CONVERT(NVARCHAR(100), name), N', ')
FROM sys.configurations
WHERE name IN (N'xp_cmdshell', N'cross db ownership chaining', N'Ad Hoc Distributed Queries', N'clr enabled')
  AND CONVERT(INT, value_in_use) <> 0;
SET @ok = CASE WHEN @s IS NULL THEN 1 ELSE 0 END;
SET @s = N'Još uključeno: ' + ISNULL(@s, N'-') + N'. EXEC sp_configure N''<opcija>'', 0; RECONFIGURE;';
EXEC #dodaj 'Z8.1', N'Rizične opcije poslužitelja su isključene (xp_cmdshell, cross db ownership chaining, Ad Hoc Distributed Queries, clr enabled)', @ok,
    @s;

SELECT @ok = CASE WHEN is_trustworthy_on = 0 THEN 1 ELSE 0 END FROM sys.databases WHERE name = N'$(BAZA)';
EXEC #dodaj 'Z8.2', N'TRUSTWORTHY je isključen za $(BAZA)', @ok,
    N'ALTER DATABASE [$(BAZA)] SET TRUSTWORTHY OFF; – uz db_owner i vlasnika sa omogućuje eskalaciju do sysadmin.';

SET @ok = CASE WHEN EXISTS (SELECT 1 FROM sys.database_permissions
                            WHERE grantee_principal_id = DATABASE_PRINCIPAL_ID(N'guest')
                              AND permission_name = N'CONNECT' AND state IN ('G', 'W')) THEN 0 ELSE 1 END;
EXEC #dodaj 'Z8.3', N'Korisnik guest nema CONNECT u bazi $(BAZA)', @ok,
    N'REVOKE CONNECT FROM guest; – inače se svaka prijava na poslužitelj (npr. bi_izvjestaji) može spojiti na bazu.';
GO
/* ================= Ispis ================= */
SET NOCOUNT ON;
DECLARE @z VARCHAR(8), @o NVARCHAR(400), @ok BIT, @sv NVARCHAR(1000), @uk INT, @pr INT;
PRINT N'Zadatak  Status   Provjera';
PRINT N'-------  -------  ' + REPLICATE(N'-', 72);
PRINT N'Z1       PISANO   Analiza prijetnji zatečenog stanja (predaje se pisano, ne provjerava se automatski)';
DECLARE c CURSOR LOCAL FAST_FORWARD FOR SELECT zadatak, opis, ok, savjet FROM #r ORDER BY rb;
OPEN c;
FETCH NEXT FROM c INTO @z, @o, @ok, @sv;
WHILE @@FETCH_STATUS = 0
BEGIN
    PRINT CONVERT(NVARCHAR(9), LEFT(@z + SPACE(9), 9)) + CASE WHEN @ok = 1 THEN N'PROŠLO   ' ELSE N'PALO     ' END + @o;
    IF @ok = 0 AND @sv IS NOT NULL PRINT SPACE(18) + N'-> ' + @sv;
    FETCH NEXT FROM c INTO @z, @o, @ok, @sv;
END;
CLOSE c;
DEALLOCATE c;
SELECT @uk = COUNT(*), @pr = SUM(CONVERT(INT, ok)) FROM #r;
PRINT N'';
PRINT CONCAT(N'Ukupno: ', @pr, N' / ', @uk, N' automatskih provjera je prošlo.');
PRINT N'';
DECLARE c2 CURSOR LOCAL FAST_FORWARD FOR SELECT zadatak, ok FROM #r ORDER BY rb;
OPEN c2;
FETCH NEXT FROM c2 INTO @z, @ok;
WHILE @@FETCH_STATUS = 0
BEGIN
    PRINT N'REZULTAT|' + CONVERT(NVARCHAR(8), @z) + N'|' + CASE WHEN @ok = 1 THEN N'PROŠLO' ELSE N'PALO' END;
    FETCH NEXT FROM c2 INTO @z, @ok;
END;
CLOSE c2;
DEALLOCATE c2;
GO
