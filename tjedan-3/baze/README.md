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
docker-compose.yml          SQL Server + jednokratni servisi dozvole, init i provjera
.env.primjer                predložak postavki (kopirajte u .env)
skripte/postavljanje/       shema i podaci za tri domene + zatečene (loše) postavke – NE MIJENJATI
skripte/provjera.sql        automatska provjera (T-SQL) + provjera.sh, init.sh, zajednicko.sh
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

## 5. Reset (početi ispočetka)

```bash
docker compose down -v        # briše kontejnere i volumen s bazama (sve promjene!)
# ispraznite i mape backup/ i audit/ (osim .gitkeep) – stare datoteke certifikata inače smetaju
docker compose up -d
```

Na Linuxu su datoteke u `backup/` i `audit/` vlasništvo korisnika uid 10001; obrišite ih sa
`sudo rm -f backup/*.* audit/*.*` ili iz kontejnera prije `down -v`:
`docker compose exec sql sh -c 'rm -f /var/opt/mssql/backup/* /var/opt/mssql/audit/*'`.

## 6. Što se predaje

1. Vaša T-SQL skripta (ili numerirane skripte) kojom na svježoj bazi riješite zadatke Z2–Z8,
   bez lozinki upisanih u skriptu.
2. Ispis provjere: `docker compose --profile provjera run --rm provjera > provjera.txt`.
3. Kratka pisana analiza prijetnji zatečenog stanja (Z1) i odgovori na pitanja iz zadataka.

## 7. Česti problemi

| Simptom | Rješenje |
|---|---|
| `sql` se odmah zaustavi, u `docker compose logs sql` piše da lozinka ne zadovoljava politiku | Jača `MSSQL_SA_PASSWORD`, pa `docker compose down -v` i `up -d`. |
| Apple Silicon: kontejner se ruši ili se ne pokreće | Uključite Rosettu (odjeljak 1), restart Docker Desktopa. |
| `port is already allocated` | Lokalno već radi SQL Server: u `.env` postavite `SQL_PORT=14333` i spajajte se na `localhost,14333`. |
| `Cannot open backup device` / `Operating system error 5` | Prava na `./backup` ili `./audit`: `docker compose up -d` (servis `dozvole`), na Linuxu po potrebi `chmod 777 backup audit`; na Windowsu paket u WSL. |
| `init` javlja `$'\r': command not found` | Skripte su spremljene s Windows prijelomima redaka; ponovno raspakirajte ZIP (ne uređujte `.sh` u Notepadu). |
| Provjera: „ne mogu se prijaviti … kao 'sa'” | Onemogućili ste `sa`: postavite `ADMIN_LOGIN`/`ADMIN_PASSWORD` u `.env` i `docker compose up -d`. |
| Provjera Z6.5 povremeno pada odmah nakon uključivanja revizije | Pokrenite provjeru ponovno (zapisi se upisuju s kratkom odgodom). |

## 8. Napomene o SQL Serveru na Linuxu

- `xp_cmdshell` na Linuxu nije podržan; u zadatku Z8 opciju svejedno isključujete jer skripta mora
  vrijediti i za Windows poslužitelj.
- `CHECK_POLICY = ON` na Linuxu provjerava složenost lozinke, ali nema Windows politike zaključavanja
  računa ni povijesti lozinki.
- TDE, šifrirane kopije, revizija u datoteku, RLS i DDM rade jednako kao na Windowsu (Developer izdanje
  ima sve značajke Enterprise izdanja – za produkciju trebate odgovarajuću licencu).
