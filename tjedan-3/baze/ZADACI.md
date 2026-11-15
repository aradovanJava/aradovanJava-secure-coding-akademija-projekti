# Zadaci – Sigurnost baza podataka

## Polazna situacija

Vaš tim je aplikaciju iz 2. tjedna (MedTermin, Ulaznica ili Kadrovska) prebacio na SQL Server 2022.
Baza je podignuta brzo: „da radi”. Aplikacija se spaja s `sa` ili prijavom koja ima sva prava. Podrška
i izvještajni alati čitaju sve. OIB-ovi su u čistom tekstu, kopije baze ne postoje, a nitko ne bilježi
tko je što čitao. Prije puštanja u produkciju (i prije revizije usklađenosti s GDPR-om) bazu trebate
dovesti u stanje koje biste mogli obraniti.

Polazno stanje stvaraju skripte u `skripte/postavljanje/` (shema i podaci te `zatecene-postavke.sql`).
**Te skripte ne mijenjajte.** Sve promjene pišite u **vlastitu T-SQL skriptu**
(npr. `rjesenje-<ime>.sql`) koju možete pokrenuti na svježoj bazi i koju predajete.

U tekstu ispod oznake vrijede za sve tri domene:

| | MedTermin | Ulaznica | Kadrovska |
|---|---|---|---|
| baza | `MedTermin` | `Ulaznica` | `Kadrovska` |
| aplikacijska prijava i korisnik | `medtermin_app` | `ulaznica_app` | `kadrovska_app` |
| glavna tablica (`<glavna>`) | `rezervacije` | `narudzbe` | `zahtjevi` |
| stupac vlasnika (`<vlasnik>`) | `pacijent` | `kupac` | `zaposlenik` |
| druga osjetljiva tablica | `nalazi` | `racuni` | `platne_liste` |

Ostale prijave na poslužitelju: `podrska` (korisnička podrška), `bi_izvjestaji` (izvještajni alat).
Tablica `dbo.revizija` je dnevnik promjena nad glavnom tablicom; puni je okidač.

Nakon svakog koraka pokrenite provjeru:

```bash
docker compose --profile provjera run --rm provjera
```

Provjera ispisuje jedan redak po provjeri (`PROŠLO` / `PALO`) i savjet za ono što je palo.
Cilj: sve automatske provjere `PROŠLO` + pisana analiza (Z1).

Učinak zadataka Z2–Z4 vidi se i **iz aplikacije**: demo „Aplikacija i baza” (README.md, odjeljak 5) spaja se kao
`<domena>_app` – u Pythonu, Javi ili C#-u – i ispisuje što aplikacijski račun smije. Nakon Z2–Z4 mora pisati
`Upozorenja: 0`:

```bash
docker compose --profile aplikacija run --rm aplikacija-python      # ili aplikacija-java, aplikacija-dotnet
```

> Savjet: **reviziju (Z6) možete uključiti odmah na početku** – tada će zabilježiti i sve vaše
> promjene prava. Redoslijed zadataka ispod je tematski, ne obavezan.

---

## Z1 – Prepoznavanje prijetnji (pisano, ne provjerava se automatski)

Prije ikakvih promjena istražite zatečeno stanje **upitima nad katalogom** (ne samo čitanjem skripti):
`sys.server_principals`, `sys.sql_logins`, `sys.server_role_members`, `sys.database_principals`,
`sys.database_role_members`, `sys.database_permissions`, `sys.configurations`, `sys.databases`,
`sys.dm_database_encryption_keys`, `msdb.dbo.backupset`, `sys.server_audits`…

Predajte kratku analizu (½ – 1 stranica): **barem 8 prijetnji**, za svaku

1. što ste pronašli (upit i rezultat),
2. kako bi to napadač ili nepažljiv djelatnik iskoristio (konkretan scenarij),
3. kojim zadatkom (Z2–Z8) to rješavate.

Razmislite posebno o kombinacijama, npr. *db_owner + TRUSTWORTHY ON + vlasnik baze sa*, ili
*guest CONNECT + prava za public*, i o tome što znači SQL injection u aplikaciji koja se spaja kao sysadmin.

---

## Z2 – Prijave i korisnici

| Provjera | Što mora vrijediti |
|---|---|
| **Z2.1** | `<domena>_app` ima novu jaku lozinku i `CHECK_POLICY = ON`; prijava je omogućena. |
| **Z2.2** | `<domena>_app` nije član nijedne uloge poslužitelja (sysadmin…) i nema `CONTROL SERVER`. |
| **Z2.3** | Korisnik `<domena>_app` u bazi nije član fiksnih uloga (`db_owner`, `db_datareader`, `db_ddladmin`…). |
| **Z2.4** | Postoji vaša administratorska SQL prijava (sysadmin, `CHECK_POLICY = ON`), a `sa` je onemogućen. |
| **Z2.5** | Korisnik `podrska` nije u `db_datareader` ni drugim fiksnim ulogama (korisnika ne brišite). |

Pomoć: `ALTER LOGIN … WITH PASSWORD = …`, `ALTER LOGIN … WITH CHECK_POLICY = ON`,
`ALTER SERVER ROLE … DROP MEMBER …`, `ALTER ROLE … DROP MEMBER …`, `ALTER LOGIN sa DISABLE`.

**Važno za Z2.4:** prvo napravite i isprobajte vlastitu prijavu, tek onda onemogućite `sa`.
Zatim u `.env` upišite `ADMIN_LOGIN` i `ADMIN_PASSWORD` i pokrenite `docker compose up -d`
(healthcheck, `init` i provjera tada koriste vašu prijavu). Na Linuxu `CHECK_POLICY` provjerava
složenost lozinke; dio Windows politike (npr. zaključavanje računa) ondje nije dostupan.

---

## Z3 – Najmanje ovlasti

| Provjera | Što mora vrijediti |
|---|---|
| **Z3.1** | Postoji uloga `uloga_aplikacija`, `<domena>_app` je njezin član i aplikacija i dalje radi: ima `SELECT` i `INSERT` na `dbo.<glavna>` i `SELECT` na `dbo.korisnici`. |
| **Z3.2** | Aplikacija ne može mijenjati shemu: nema `CREATE TABLE`, `ALTER` na bazi/shemi/tablicama, `CONTROL`, `ALTER ANY USER`. |
| **Z3.3** | Aplikacija ne može čitati ni mijenjati `dbo.revizija` (`SELECT`, `UPDATE`, `DELETE`). |
| **Z3.4** | Uloga `public` nema prava na korisničke objekte i sheme. |

Ulozi dodijelite **samo ono što aplikacija iz 2. tjedna stvarno radi** (pogledajte njezine
upite: registracija, prijava, reset lozinke, popisi, stvaranje i brisanje glavnog zapisa, uvoz…).
Prava dajte na razini tablica (ili, za bonus, samo `EXECUTE` na shemu `api` s pohranjenim procedurama).

Pitanje za razmišljanje: zašto okidač i dalje može pisati u `dbo.revizija` iako aplikacija nema
nikakvo pravo na tu tablicu (*ownership chaining*)?

Efektivna prava provjeravate ovako:

```sql
EXECUTE AS USER = N'medtermin_app';
SELECT * FROM sys.fn_my_permissions(N'dbo.revizija', N'OBJECT');
SELECT HAS_PERMS_BY_NAME(N'dbo.korisnici', N'OBJECT', N'ALTER');
REVERT;
```

---

## Z4 – Row-Level Security i Dynamic Data Masking

| Provjera | Što mora vrijediti |
|---|---|
| **Z4.1** | Na `dbo.<glavna>` postoji uključena sigurnosna politika s **FILTER** predikatom. |
| **Z4.2** | Aplikacija s `SESSION_CONTEXT(N'korisnik') = 'ana'` vidi samo Anine zapise, s `'marko'` samo Markove; bez konteksta ne vidi ništa; korisnik s ulogom `ADMIN` (u `dbo.korisnici`) vidi sve. Administratori baze (oni koji nisu u `uloga_aplikacija`) nisu ograničeni. |
| **Z4.3** | Stupci `dbo.korisnici.oib` i `dbo.korisnici.email` su maskirani. |
| **Z4.4** | `podrska` može čitati korisnike, ali vidi maskirani OIB i e-mail. |
| **Z4.5** | `podrska` ne može čitati `password_hash` i nema `UNMASK`. |

RLS: inline funkcija `WITH SCHEMABINDING` (najbolje u zasebnoj shemi, npr. `sigurnost`) koja prima
`<vlasnik>` i vraća redak kad je pristup dopušten, te `CREATE SECURITY POLICY … ADD FILTER PREDICATE …`.
Za bonus dodajte i `BLOCK PREDICATE … AFTER INSERT` (aplikacija ne može upisati zapis u tuđe ime).

Aplikacija bi nakon prijave korisnika na istoj konekciji pozvala:

```sql
EXEC sp_set_session_context @key = N'korisnik', @value = N'ana', @read_only = 1;
```

Isprobajte sami:

```sql
EXECUTE AS USER = N'medtermin_app';
EXEC sp_set_session_context N'korisnik', N'ana';
SELECT * FROM dbo.rezervacije;      -- samo Anini zapisi
EXEC sp_set_session_context N'korisnik', NULL;
REVERT;
```

DDM: `ALTER TABLE … ALTER COLUMN … ADD MASKED WITH (FUNCTION = 'email()' | 'partial(…)')`.
Podršci dodijelite `SELECT` na popis stupaca (bez `password_hash`) – najbolje preko uloge.
Aplikaciji koja treba stvarne vrijednosti možete dati granularni `UNMASK` (SQL Server 2022).
Pitanje: zašto DDM **nije** zamjena za šifriranje ni za kontrolu pristupa?

---

## Z5 – Šifriranje

| Provjera | Što mora vrijediti |
|---|---|
| **Z5.1** | Baza je šifrirana TDE-om (`sys.dm_database_encryption_keys.encryption_state = 3`). |
| **Z5.2** | TDE certifikat (u `master`) je sigurnosno kopiran **s privatnim ključem** u `/var/opt/mssql/backup` (na vašem računalu `./backup`, datoteka `.pvk`). |
| **Z5.3** | U bazi postoji AES simetrični ključ zaštićen certifikatom. |
| **Z5.4** | `dbo.<glavna>` ima stupac `oib_sifrirano VARBINARY(256)` s OIB-om šifriranim tim ključem, a stupac `oib` je uklonjen (ili su sve vrijednosti `NULL`). |

TDE: `CREATE MASTER KEY` i `CREATE CERTIFICATE` u `master`, `BACKUP CERTIFICATE … WITH PRIVATE KEY (…)`,
`CREATE DATABASE ENCRYPTION KEY … ENCRYPTION BY SERVER CERTIFICATE …`, `ALTER DATABASE … SET ENCRYPTION ON`.

Šifriranje stupca: `CREATE MASTER KEY` (u bazi) → `CREATE CERTIFICATE` → `CREATE SYMMETRIC KEY …
WITH ALGORITHM = AES_256 ENCRYPTION BY CERTIFICATE …` → `OPEN SYMMETRIC KEY` →
`ENCRYPTBYKEY(KEY_GUID(N'…'), oib)`. Provjera dešifrira s `DECRYPTBYKEYAUTOCERT`; ako koristite
autentifikator, neka to bude `CONVERT(VARBINARY(8), id)`. OIB u `dbo.korisnici` ostaje (maskiran, Z4).

Pitanja: od čega TDE štiti, a od čega ne (npr. od SQL injectiona)? Što se događa s kopijom baze ako
izgubite certifikat? Gdje biste u stvarnosti čuvali `.pvk` i lozinku?

---

## Z6 – Revizija (auditing)

| Provjera | Što mora vrijediti |
|---|---|
| **Z6.1** | Server audit zapisuje u `/var/opt/mssql/audit/` (`./audit`) i uključen je. |
| **Z6.2** | Server audit specifikacija (uključena) sadrži `FAILED_LOGIN_GROUP` i `SUCCESSFUL_LOGIN_GROUP`. |
| **Z6.3** | Database audit specifikacija (uključena) bilježi `SELECT` nad `dbo.korisnici` i `dbo.<glavna>`. |
| **Z6.4** | Ista specifikacija bilježi `DATABASE_PERMISSION_CHANGE_GROUP`, `SCHEMA_OBJECT_PERMISSION_CHANGE_GROUP` i `DATABASE_ROLE_MEMBER_CHANGE_GROUP`. |
| **Z6.5** | U audit datoteci zaista postoje `SELECT` zapisi (`action_id = 'SL'`) nad tim tablicama. |

Zapise čitate s:

```sql
SELECT event_time, action_id, succeeded, server_principal_name, database_principal_name,
       object_name, statement
FROM sys.fn_get_audit_file(N'/var/opt/mssql/audit/*.sqlaudit', DEFAULT, DEFAULT)
ORDER BY event_time DESC;
```

Pokušajte se prijaviti pogrešnom lozinkom i pronađite taj događaj (`LGIF`). Primijetit ćete i
prijave healthchecka svakih 10 sekundi – i to je stvarnost: revizija bez filtriranja brzo naraste.

---

## Z7 – Sigurnosne kopije

| Provjera | Što mora vrijediti |
|---|---|
| **Z7.1** | Postoji puna kopija baze u `/var/opt/mssql/backup/`, šifrirana (`WITH ENCRYPTION`). |
| **Z7.2** | Ta kopija ima kontrolne zbrojeve (`WITH CHECKSUM`). |
| **Z7.3** | Kopija je provjerena s `RESTORE VERIFYONLY … WITH CHECKSUM, LOADHISTORY`. |
| **Z7.4** | Kopija je vraćena kao baza `<Baza>_ProbniRestore` (npr. `MedTermin_ProbniRestore`) i podaci su čitljivi. |

Za šifriranje kopije treba certifikat u `master` (može biti zaseban od TDE certifikata – i njega
kopirajte s privatnim ključem). Logička imena datoteka za `RESTORE … WITH MOVE` dobijete s
`RESTORE FILELISTONLY`; nove datoteke stavite u `/var/opt/mssql/data/`.

Pitanje: zašto je neisprobana kopija gotovo jednako loša kao nikakva? Što još nedostaje za pravu
strategiju (diferencijalne i log kopije, kopija izvan poslužitelja, RPO/RTO)?

---

## Z8 – Očvršćivanje (hardening)

| Provjera | Što mora vrijediti |
|---|---|
| **Z8.1** | Isključene su opcije `xp_cmdshell`, `cross db ownership chaining`, `Ad Hoc Distributed Queries` i `clr enabled`. |
| **Z8.2** | `TRUSTWORTHY` je isključen za bazu. |
| **Z8.3** | Korisnik `guest` nema `CONNECT` u bazi. |

Napomena: na Linuxu `xp_cmdshell` (i ostale sistemske proširene procedure) nije podržan – opcija
postoji u `sys.configurations`, ali `sp_configure` za nju javlja grešku 15392, pa je tim nije uspio
uključiti. Na Windows poslužitelju bi to bio jedan od najopasnijih propusta (naredbe OS-a iz T-SQL-a,
npr. preko SQL injectiona). U vašoj skripti je svejedno isključite, unutar `BEGIN TRY … END TRY
BEGIN CATCH … END CATCH`, kako bi skripta radila na obje platforme.

---

## Što se predaje

1. **Vaša T-SQL skripta** (ili više njih, numeriranih redoslijedom izvođenja) koja na svježoj bazi
   (`docker compose down -v`, prazni `./backup` i `./audit`, `docker compose up -d`) dovodi sve
   automatske provjere u `PROŠLO`. Lozinke **ne pišite u skriptu** – koristite sqlcmd varijable
   (`$` + `(IME_VARIJABLE)` u skripti, `-v IME_VARIJABLE=…` pri pokretanju) ili ih upišite ručno.
2. **Ispis provjere** (`docker compose --profile provjera run --rm provjera > provjera.txt`).
3. **Pisana analiza prijetnji (Z1)** i kratki odgovori na pitanja iz zadataka (najviše 2 stranice).
