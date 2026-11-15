# Sigurnost baza podataka – laboratorij (SQL Server 2022)

Secure Coding akademija · Span Cyber Security Center · 3. tjedan
Predavač: doc. dr. sc. Aleksander Radovan

Svaki polaznik na svojem računalu u Dockeru pokreće **vlastiti** SQL Server 2022 (Developer) s
namjerno loše podešenom bazom svoje domene iz 2. tjedna. Zadatak je bazu zaštititi: prava i najmanje
ovlasti, RLS i maskiranje, šifriranje (TDE i stupac), revizija, sigurnosne kopije i očvršćivanje.
Uz paket dolazi **automatska provjera** koja pokazuje koji su zadaci riješeni.

Zadaci su u [ZADACI.md](ZADACI.md).

## Sadržaj paketa

```
docker-compose.yml          SQL Server + jednokratni servisi dozvole, init i provjera; profil aplikacija (demo)
.env.primjer                predložak postavki (kopirajte u .env)
skripte/postavljanje/       shema i podaci za tri domene + zatečene (loše) postavke – NE MIJENJATI
skripte/provjera.sql        automatska provjera (T-SQL) + provjera.sh, init.sh, zajednicko.sh
aplikacija/python/          demo „Aplikacija i baza” – Python (mssql-python)
aplikacija/java/            isti demo – Java (JDBC, mssql-jdbc)
aplikacija/dotnet/          isti demo – C# (.NET 10, Microsoft.Data.SqlClient)
backup/                     ovdje SQL Server sprema kopije baze i certifikata (/var/opt/mssql/backup)
audit/                      ovdje SQL Server sprema revizijske zapise (/var/opt/mssql/audit)
```

## 1. Preduvjeti

- **Docker Desktop** (Windows, macOS) ili **Docker Engine + Compose v2** (Linux).
  Dockeru dodijelite barem **4 GB RAM-a** (SQL Server treba najmanje 2 GB).
- **Windows:** Docker Desktop s WSL 2 pozadinom. Paket raspakirajte u mapu bez razmaka i posebnih
  znakova u putanji (npr. `C:\lab\sigurnost-baza-podataka`) ili, još bolje, unutar WSL-a
  (`~/lab/...`) – tada su dozvole i brzina mapa `backup`/`audit` najpouzdanije.
- **macOS s Apple Silicon čipom (M1–M4):** slika SQL Servera postoji samo za amd64. U Docker Desktopu
  uključite *Settings → General → „Use Rosetta for x86_64/amd64 emulation on Apple Silicon”* (i
  *Virtualization framework*). Bez Rosette SQL Server se ruši pri pokretanju.
- **macOS (Intel) i Linux:** nema posebnih koraka. Na Linuxu servis `dozvole` sam postavlja prava na
  `./backup` i `./audit` (korisnik `mssql` u kontejneru ima uid 10001). Ako i dalje vidite
  „Access is denied”/„Operating system error 5”, ručno: `chmod 777 backup audit`.

## 2. Pokretanje

```bash
cp .env.primjer .env          # Windows PowerShell: Copy-Item .env.primjer .env
```

U `.env` postavite:

- `DOMENA` – **ista domena kao vaš projekt iz 2. tjedna**: `medtermin`, `ulaznica` ili `kadrovska`;
- `MSSQL_SA_PASSWORD` – jaka lozinka (min. 8 znakova, velika i mala slova, znamenke, simboli; bez `$`,
  navodnika i razmaka). Ako lozinka nije dovoljno složena, SQL Server se neće pokrenuti.

```bash
docker compose up -d
docker compose logs -f init     # pričekajte "Gotovo: baza … je spremna", pa Ctrl+C
```

Prvo pokretanje preuzima sliku (~1,5 GB). `init` stvara bazu samo ako još ne postoji, pa ponovno
`docker compose up -d` ne briše vaš rad.

| Domena | Baza | Aplikacijska prijava |
|---|---|---|
| medtermin | `MedTermin` | `medtermin_app` |
| ulaznica | `Ulaznica` | `ulaznica_app` |
| kadrovska | `Kadrovska` | `kadrovska_app` |

## 3. Spajanje na poslužitelj

Poslužitelj sluša samo na `127.0.0.1`, port `1433` (ili `SQL_PORT` iz `.env`).
Prijava: `sa` i lozinka iz `.env` (kasnije vaša administratorska prijava).

**SSMS (Windows):** Server name `localhost,1433`, Authentication *SQL Server Authentication*,
u kartici *Connection Security* (SSMS 20+: *Encryption: Mandatory*) uključite
**Trust server certificate**.

**VS Code** s ekstenzijom **SQL Server (mssql)** (Microsoft): *Add Connection* → Server `localhost,1433`,
*SQL Login*, korisnik i lozinka, **Trust server certificate: true**. Radi na Windowsu, macOS-u i Linuxu.
(Azure Data Studio se ukida – koristite VS Code.)

**sqlcmd unutar kontejnera** (bez ikakve instalacije):

```bash
docker compose exec sql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P '<lozinka>' -d MedTermin
# vlastitu skriptu: kopirajte je u kontejner pa pokrenite
docker compose cp moja-skripta.sql sql:/tmp/moja-skripta.sql
docker compose exec sql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P '<lozinka>' -I -f 65001 -i /tmp/moja-skripta.sql
```

`-C` znači „vjeruj samopotpisanom certifikatu” (laboratorij), `-I` uključuje QUOTED_IDENTIFIER,
`-f 65001` čita skriptu kao UTF-8. Lozinke u skriptama možete zamijeniti sqlcmd varijablama
(`-v LOZINKA='…'`).

## 4. Automatska provjera

```bash
docker compose --profile provjera run --rm provjera
```

Ispisuje tablicu: zadatak, `PROŠLO`/`PALO`, opis provjere i savjet za ono što je palo, a na kraju
redove `REZULTAT|Z3.2|PALO` (strojno čitljivo). Provjera ne mijenja bazu; izvodi tek nekoliko
`SELECT` upita u ime aplikacije i podrške (`EXECUTE AS USER`), što ćete vidjeti i u reviziji.

Provjera se spaja administratorskom prijavom iz `.env`. **Kad u zadatku Z2.4 onemogućite `sa`:**

1. u `.env` upišite `ADMIN_LOGIN=<vaša prijava>` i `ADMIN_PASSWORD=<njezina lozinka>`;
2. `docker compose up -d` (kontejner se ponovno stvara s novim postavkama; podaci ostaju);
3. ponovno pokrenite provjeru.

Ako to preskočite, healthcheck se ne može prijaviti, kontejner postaje *unhealthy* i provjera se ne
pokreće (u reviziji ćete vidjeti neuspjele prijave za `sa` svakih 10 sekundi).

## 5. Demo: aplikacija i baza (Python, Java, C#)

Mali program u tri tehnologije spaja se na bazu **onako kako se spaja vaša aplikacija iz 2. tjedna**: prijavom
`<domena>_app` (ne `sa`), šifriranom vezom, lozinkom iz varijable okruženja i isključivo parametriziranim upitima, a
na početku svakog „zahtjeva” postavlja `SESSION_CONTEXT` s prijavljenim korisnikom (za RLS). Zatim ispiše **što taj
račun stvarno smije**. Ništa ne mijenja u bazi (svaki pokušaj se poništava – `ROLLBACK`). Sve tri inačice daju isti
rezultat; izaberite tehnologiju svog projekta.

```bash
docker compose --profile aplikacija run --rm aplikacija-python    # Python (mssql-python)
docker compose --profile aplikacija run --rm aplikacija-java      # Java (JDBC)
docker compose --profile aplikacija run --rm aplikacija-dotnet    # C# (ADO.NET)
```

Ne treba ništa instalirati osim Dockera; prvo pokretanje preuzima sliku i ovisnosti (1–3 minute), sljedeća traju
nekoliko sekundi. Program ispisuje pet blokova:

| Blok | Što provjerava | Upozorenje `[!]` nestaje nakon |
|---|---|---|
| 1. Tko sam u bazi | prijava, korisnik, lozinka (zatečena?), članstvo u `sysadmin`, `db_owner`, `uloga_aplikacija` | Z2.1–Z2.3, Z3.1 |
| 2. Što račun stvarno može | čitanje `dbo.revizija`, `CREATE TABLE` | Z3.2, Z3.3 |
| 3. Isti unos na dva načina | `x' OR 1=1 --` kao **parametar** (0 redaka) i **zalijepljen u upit** (SQL injection) | Z4.1–Z4.2 (RLS: i uspješna injekcija vraća samo Anine retke) |
| 4. Row-Level Security | koliko redaka glavne tablice vide ana, marko i sesija bez korisnika | Z4.1–Z4.2 |
| 5. Korisnička podrška | OIB i e-mail (maskirani?), smije li čitati `password_hash` | Z2.5, Z4.3–Z4.5 |

Na kraju je broj upozorenja i strojno čitljiv sažetak (`DEMO|ključ|vrijednost`). **Prije** zadataka očekujte desetak
upozorenja; **poslije** zadataka Z2–Z4 mora biti `Upozorenja: 0`. Uz `DEMO_STROGO=1` program vraća izlazni kod 1 dok
postoji ijedno upozorenje (korisno u skriptama).

**Nakon zadatka Z2.1** aplikacijska prijava ima novu lozinku: upišite je u `.env` kao `APP_LOZINKA=…` (i
`PODRSKA_LOZINKA=…` ako ste promijenili i tu). Demo lozinku čita iz okruženja – **nikad** iz koda, kao i prava
aplikacija. Dok `APP_LOZINKA` nije postavljena, demo pokušava sa zatečenom lozinkom; ako ona još radi, to je nalaz.

**Lokalno iz IDE-a** (poslužitelj je na `localhost`, port iz `.env`):

| | Pokretanje | Postavke |
|---|---|---|
| Python 3.10+ | `cd aplikacija/python`, `python -m venv .venv`, aktivirajte, `pip install -r requirements.txt`, `python demo.py` | varijable `DOMENA`, `SQL_PORT`, `APP_LOZINKA` u terminalu ili u *Run configuration* (PyCharm / VS Code `launch.json` → `env`) |
| Java 21 | `cd aplikacija/java`, `./mvnw -q compile exec:java` (Windows: `mvnw.cmd …`) ili IntelliJ: otvorite `pom.xml`, *Run* `Demo.main` | *Run configuration* → *Environment variables* |
| .NET 10 | `cd aplikacija/dotnet`, `dotnet run` ili Visual Studio / Rider: otvorite `BazeDemo.csproj` | *Debug properties* → *Environment variables* |

Na Linuxu `mssql-python` traži i sistemske biblioteke (Debian/Ubuntu: `libltdl7 libkrb5-3 libgssapi-krb5-2`); na
Windowsu i macOS-u dolazi sve s paketom. Ako lokalno ne radi, koristite Docker inačicu – rezultat je isti.

Na što obratiti pažnju u kodu (sve tri inačice imaju iste komentare):

- **niz za spajanje bez lozinke u kodu**, `Encrypt=yes`; `TrustServerCertificate=yes` samo u laboratoriju
  (samopotpisani certifikat) – u produkciji certifikat kojem klijent vjeruje;
- **parametri** (`?` / `@p0`) za sve vrijednosti; nazivi tablica i stupaca dolaze samo iz popisa dopuštenih
  vrijednosti (ne mogu biti parametri – usporedite S08 iz T2);
- **`sp_set_session_context … @read_only = 1`** odmah nakon spajanja: ni kasniji kod ni SQL injection u istoj sesiji
  ne mogu promijeniti identitet za RLS.

## 6. Demonstracija korak po korak (na nastavi ili za samostalno ponavljanje)

Oko 25 minuta; pokazuje zašto je baza **druga linija obrane**. Isti koraci služe i kao provjera vašeg rješenja.

**Priprema (prije nastave, treba internet):** `cp .env.primjer .env` (postavite `DOMENA` i lozinku), `docker compose
up -d`, pričekajte `init` (`docker compose logs -f init`), zatim jednom
`docker compose --profile aplikacija build` i po jedno pokretanje demoa u tehnologiji koju ćete pokazivati
(preuzme ovisnosti). Spojite se iz VS Codea (ekstenzija *SQL Server (mssql)*) ili SSMS-a (odjeljak 3).

| Korak | Naredba ili upit | Što pokazati |
|---|---|---|
| 1. Zatečeno stanje | `docker compose --profile provjera run --rm provjera` | sve automatske provjere `PALO`; tablica je ujedno popis tema predavanja |
| 2. Pogled aplikacije | `docker compose --profile aplikacija run --rm aplikacija-python` | aplikacija je `sysadmin` i `db_owner`, mijenja shemu, čita dnevnik; injekcija vraća **sve** zapise; podrška vidi OIB i hasheve lozinki |
| 3. Katalog | `SELECT p.name FROM sys.server_role_members m JOIN sys.server_principals r ON r.principal_id = m.role_principal_id JOIN sys.server_principals p ON p.principal_id = m.member_principal_id WHERE r.name = N'sysadmin';` i `SELECT name, is_trustworthy_on FROM sys.databases;` | stanje se dokazuje **upitom nad katalogom**, ne čitanjem skripti (zadatak Z1) |
| 4. `EXECUTE AS` | `EXECUTE AS USER = N'<domena>_app'; SELECT * FROM sys.fn_my_permissions(NULL, 'DATABASE'); REVERT;` | učinkovita prava aplikacije – isto što demo radi iz programa |
| 5. Jedna mjera uživo | npr. Z2.2: `ALTER SERVER ROLE sysadmin DROP MEMBER [<domena>_app];` pa ponovno korak 2 | upozorenje „član sysadmin” nestaje; provjera Z2.2 prelazi u `PROŠLO` |
| 6. Ciljano stanje | nakon svih zadataka Z2–Z4: korak 2 s `APP_LOZINKA` u `.env` | `Upozorenja: 0`; parametar vraća 0 redaka, a **i uspješna injekcija** vraća samo Anine retke (RLS) |
| 7. Reset | `docker compose down -v` i pražnjenje `backup/` i `audit/` (odjeljak 7) | svaka demonstracija kreće od istog lošeg stanja |

Dobro pitanje za raspravu nakon koraka 6: *Ako je SQL injection uspio, što je napadač dobio?* – ništa više od onoga što
smije prijavljeni korisnik. Zato su parametrizirani upiti prva, a minimalne ovlasti i RLS druga linija obrane.

## 7. Reset (početi ispočetka)

```bash
docker compose down -v        # briše kontejnere i volumen s bazama (sve promjene!)
# ispraznite i mape backup/ i audit/ (osim .gitkeep) – stare datoteke certifikata inače smetaju
docker compose up -d
```

Na Linuxu su datoteke u `backup/` i `audit/` vlasništvo korisnika uid 10001; obrišite ih sa
`sudo rm -f backup/*.* audit/*.*` ili iz kontejnera prije `down -v`:
`docker compose exec sql sh -c 'rm -f /var/opt/mssql/backup/* /var/opt/mssql/audit/*'`.

## 8. Što se predaje

1. Vaša T-SQL skripta (ili numerirane skripte) kojom na svježoj bazi riješite zadatke Z2–Z8,
   bez lozinki upisanih u skriptu.
2. Ispis provjere: `docker compose --profile provjera run --rm provjera > provjera.txt`.
3. Kratka pisana analiza prijetnji zatečenog stanja (Z1) i odgovori na pitanja iz zadataka.

## 9. Česti problemi

| Simptom | Rješenje |
|---|---|
| `sql` se odmah zaustavi, u `docker compose logs sql` piše da lozinka ne zadovoljava politiku | Jača `MSSQL_SA_PASSWORD`, pa `docker compose down -v` i `up -d`. |
| Apple Silicon: kontejner se ruši ili se ne pokreće | Uključite Rosettu (odjeljak 1), restart Docker Desktopa. |
| `port is already allocated` | Lokalno već radi SQL Server: u `.env` postavite `SQL_PORT=14333` i spajajte se na `localhost,14333`. |
| `Cannot open backup device` / `Operating system error 5` | Prava na `./backup` ili `./audit`: `docker compose up -d` (servis `dozvole`), na Linuxu po potrebi `chmod 777 backup audit`; na Windowsu paket u WSL. |
| `init` javlja `$'\r': command not found` | Skripte su spremljene s Windows prijelomima redaka; ponovno raspakirajte ZIP (ne uređujte `.sh` u Notepadu). |
| Provjera: „ne mogu se prijaviti … kao 'sa'” | Onemogućili ste `sa`: postavite `ADMIN_LOGIN`/`ADMIN_PASSWORD` u `.env` i `docker compose up -d`. |
| Provjera Z6.5 povremeno pada odmah nakon uključivanja revizije | Pokrenite provjeru ponovno (zapisi se upisuju s kratkom odgodom). |
| Demo: „Ne mogu se spojiti kao <domena>_app” | Poslužitelj još nije spreman (`docker compose ps`) ili je lozinka promijenjena u Z2.1 – upišite `APP_LOZINKA` u `.env`. |
| Demo: Login failed for user 'podrska' (blok 5 preskočen) | Promijenili ste lozinku podrške – upišite `PODRSKA_LOZINKA` u `.env`. |
| Demo (Java/.NET) prvi put dugo traje | Preuzimaju se Maven/NuGet ovisnosti u Docker volumene `maven`/`nuget`; sljedeća pokretanja su brza. |

## 10. Napomene o SQL Serveru na Linuxu

- `xp_cmdshell` na Linuxu nije podržan (`sp_configure` javlja grešku 15392); u zadatku Z8 ga svejedno
  isključujete (u TRY/CATCH bloku) jer skripta mora vrijediti i za Windows poslužitelj.
- `CHECK_POLICY = ON` na Linuxu provjerava složenost lozinke, ali nema Windows politike zaključavanja
  računa ni povijesti lozinki.
- TDE, šifrirane kopije, revizija u datoteku, RLS i DDM rade jednako kao na Windowsu (Developer izdanje
  ima sve značajke Enterprise izdanja – za produkciju trebate odgovarajuću licencu).
