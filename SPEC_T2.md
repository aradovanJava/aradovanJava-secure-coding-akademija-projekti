# Secure Coding akademija – Tjedan 2: samostalni projekt
# OBVEZUJUĆA specifikacija projekata, varijanti i skrivenih testova (Java/Spring + C#/.NET)

## 0. Kontekst i svrha (pročitaj prvo)

Ovo je **nastavni materijal** za mikrokvalifikaciju „Implementacija sigurnosnih mehanizama u programskoj
podršci” (Span Centar kibernetičke sigurnosti, Zagreb; predavač doc. dr. sc. Aleksander Radovan). U drugom
tjednu svaki od 15 polaznika dobiva **vlastitu varijantu** male, namjerno ranjive web aplikacije (po uzoru na
OWASP WebGoat / Juice Shop / DVWA). Polaznik mora alatima i ručnim pregledom pronaći ranjivosti, ispraviti ih i
za svaku napisati jedinični test. Ocjenjuje se **skrivenim testovima** koje ima samo nastavnik.

Pravila koja vrijede za SVE što izrađuješ:
- Aplikacije rade isključivo **lokalno** (localhost, in-memory baza). Nema stvarnih vanjskih poziva.
- Skriveni testovi su **obični jedinični/integracijski testovi** (JUnit 5 / xUnit) koji provjeravaju da je
  ispravljena aplikacija otporna. Ne izrađuj samostalne napadačke alate, skripte za masovno slanje zahtjeva,
  generatore payloada ni upute za napad na tuđe sustave. Testni „payloadi” su minimalni i bezopasni
  (npr. XXE čita **kanarinac datoteku koju je test sam stvorio** u privremenoj mapi).
- Tekstovi za polaznike su na **hrvatskom** (ijekavica, č ć đ š ž). Identifikatori u kodu na engleskom ili
  hrvatskom bez dijakritika (vidi domene). Komentari u kodu na hrvatskom, kratki i neutralni.

## 1. Repozitorij i raspored

Privatni nastavnički repozitorij: `https://github.com/aradovanJava/aradovanJava-secure-coding-akademija-projekti`
(lokalno: `/home/claude/aradovanjava-secure-coding-akademija-projekti`, grana `main`).

```
aradovanJava-secure-coding-akademija-projekti/
├─ SPEC_T2.md                    # ovaj dokument
├─ variants.json                 # V01–V15: domena + popis RANJIVIH mjesta (9 od 13)
├─ tools/
│  ├─ generate.py                # generira varijantu iz predložaka (markeri, vidi §2)
│  ├─ check_results.py           # čita JUnit XML / TRX i uspoređuje s očekivanim stanjem
│  ├─ ci_check.sh                # CI: all-vuln + all-secure za jednu domenu i stack
│  └─ ocijeni.py                 # ocjenjivanje predaje polaznika (nastavnik, lokalno)
├─ templates/
│  ├─ java/{medtermin,ulaznica,kadrovska}/     # Maven projekt s markerima
│  └─ dotnet/{medtermin,ulaznica,kadrovska}/   # .NET solution s markerima
├─ hidden-tests/
│  ├─ java/{domena}/java/hr/span/akademija/{domena}/skriveno/*.java   # kopira se na src/test/
│  └─ dotnet/{domena}/Skriveno/*.cs                                    # kopira se na tests/<Domena>.Tests/
├─ student-docs/                 # zajedničke upute za polaznike (piše nastavnik/Claude)
└─ .github/workflows/{dev.yml,verify.yml}
```

**Vlasništvo nad mapama** (više agenata radi paralelno na istom repozitoriju):
- agent za `<stack>/<domena>` mijenja **samo** `templates/<stack>/<domena>/` i `hidden-tests/<stack>/<domena>/`;
- `tools/`, `.github/`, `variants.json`, `student-docs/`, `SPEC_T2.md` mijenja samo glavni koordinator.
  Ako ti tamo nešto treba (bug u generatoru), opiši to u završnom izvještaju ili zaobiđi u svojoj mapi.
- Prije svakog pusha: `git pull --rebase origin main`. Proxy dopušta najviše 2 istodobne git operacije po
  repozitoriju – ne pokreći paralelne push/fetch. Ako push ne uspije zbog utrke, ponovi `pull --rebase` + push.

Commit poruke završavaju s:
```
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01XPnKLU6QN1RaaAunq9Gqxa
```
Git lokalno: `git config user.name "Aleksander Radovan"`, `git config user.email "aleksander.radovan@gmail.com"`.

Sandbox **nema** pristup Maven Centralu/NuGetu i **nema** .NET SDK → build i testove provjeravaš
**isključivo kroz GitHub Actions** (§9). `gh` radi za repo-scoped API (`gh run list -R …`, `gh api repos/…`).

## 2. Markeri i generator (KLJUČNO)

Svako od 13 „mjesta” (slotova, S01–S13) u predlošku ima **dvije implementacije**: ranjivu i sigurnu.
Generator za zadanu varijantu zadržava ranjivu ili sigurnu granu i **briše sve marker-retke**.

Sintaksa (marker je cijeli redak; komentar prema jeziku datoteke):
```java
// @@VULN S08
String sql = "SELECT ... ORDER BY " + sort + " " + dir;
// @@SECURE S08
String column = SORT_COLUMNS.get(sort);
...
// @@END S08
```
- Java/C#/JS: `// @@VULN Sxx`, `// @@SECURE Sxx`, `// @@END Sxx`
- XML (pom.xml, .csproj, .config): `<!-- @@VULN Sxx -->` itd.
- properties / YAML / .http / shell: `# @@VULN Sxx` itd.
- JSON (`appsettings*.json`) – ASP.NET Core konfiguracija dopušta `//` komentare, smiju se koristiti.
- Grana može biti prazna (npr. `@@SECURE` bez redaka). Markeri se **ne smiju ugnježđivati**; više različitih
  slotova u istoj datoteci je u redu (uzastopni blokovi).
- Cijela datoteka samo za jednu granu: **prvi redak** datoteke sadrži `@@FILE-VULN Sxx` ili `@@FILE-SECURE Sxx`
  (u komentaru). Generator tada uključuje/isključuje datoteku, a marker-redak briše.
- Uvozi (`import`, `using`) koji trebaju samo jednoj grani također idu u marker blokove.

Markeri su dopušteni i u skrivenim testovima (rijetko potrebno). Generator (`tools/generate.py`, već postoji;
pokreni ga lokalno za brzu provjeru markera i linta prije pusha – Python radi u sandboxu):
```
python3 tools/generate.py --stack java --domain medtermin --mode all-vuln   --out /tmp/out [--with-hidden]
python3 tools/generate.py --stack java --domain medtermin --mode all-secure --out /tmp/out [--with-hidden]
python3 tools/generate.py --variant V07 --stack dotnet --out /tmp/out [--with-hidden]
```
Nakon generiranja generator radi **lint studentskog koda** i pada ako u `src/`, `tests/`, `http/`, `pom.xml`,
`*.csproj`, `*.json`, `*.properties` nađe: `@@`, `Sxx` oznake slotova, ili riječi koje otkrivaju ranjivost
(`ranjiv`, `nesigurn`, `vuln`, `insecure`, `exploit`, `napad`, `payload`, `injection`, `injekcij`, `XXE`,
`IDOR`, `SSRF`, `CWE-`, `OWASP`, `traversal`, `race condition`, `fail-open`, `open redirect`). Dakle:
**nikakvih komentara tipa „// RANJIVO” ni „// ovo sprječava SQL injection”** u predlošcima ni u javnim
(funkcionalnim) testovima. Kod mora izgledati kao normalan kod iz stvarnog projekta – ranjiva grana kao
uvjerljiva greška programera, sigurna grana kao uredan kod. Ne zovi metode/varijable `unsafe…`, `vulnerable…`.
(Skriveni testovi nisu podložni lintu i smiju imati opisne nazive.)

## 3. Zajednička platforma (sve domene)

### 3.1 Java (po domeni jedan samostalan Maven projekt)
- Spring Boot **3.5.7**, Java **21**, Maven + **Maven Wrapper** (kopiraj `mvnw`, `mvnw.cmd`, `.mvn/` iz
  `/home/claude/secure-coding-akademija-java/`). groupId `hr.span.akademija`, artifactId = domena
  (`medtermin`, `ulaznica`, `kadrovska`), paket `hr.span.akademija.<domena>`.
- `spring-boot-starter-web`, `spring-boot-starter-jdbc` (JdbcTemplate, **bez JPA**), `spring-boot-starter-validation`,
  H2 in-memory (`jdbc:h2:mem:<domena>;DB_CLOSE_DELAY=-1`), `spring-security-crypto` (samo za BCrypt u sigurnoj
  grani S07 – smije biti ovisnost u obje grane), **bez** spring-boot-starter-security. Port **8080**.
- Shema `src/main/resources/schema.sql`; seed u Java klasi (jer lozinke ovise o S07) ili `data.sql` + seed klasa.
- `jacoco-maven-plugin` (report u `test` fazi, `target/site/jacoco/jacoco.xml`), surefire s podrškom za
  `-Dgroups=…` (JUnit 5 tagovi). `mvnw test` bez parametara pokreće sve testove.
- Testovi: `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `TestRestTemplate` ili `MockMvc`/`RestClient`.
  Javni funkcionalni testovi: paket `hr.span.akademija.<domena>.funkcionalno`, `@Tag("funkcionalno")`.
  Primjer testa za polaznike: paket `…primjer`, klasa `PrimjerSigurnosnogTestaTest` (`@Tag("primjer")`).
- Skriveni testovi: `hidden-tests/java/<domena>/` se kopira **na `src/test/`** projekta (dakle datoteke idu u
  `hidden-tests/java/<domena>/java/hr/span/akademija/<domena>/skriveno/`, eventualni resursi u
  `hidden-tests/java/<domena>/resources/`). Paket `hr.span.akademija.<domena>.skriveno`, klase `S01…Test` … `S13…Test`
  (ime klase **počinje** oznakom slota), `@Tag("skriveno")`. Vlastita bazna klasa `SkrivenoBaza` u istom
  paketu (ne oslanjaj se na javne testne pomoćne klase koje polaznik može promijeniti).

### 3.2 .NET (po domeni jedan samostalan solution)
- **.NET 10** (`global.json` kao u `/home/claude/secure-coding-akademija-dotnet/global.json`), ASP.NET Core s
  kontrolerima, **Microsoft.Data.Sqlite** (sirovi ADO.NET, **bez EF Core**). Port **5080**
  (`Properties/launchSettings.json`, profil `http`).
- Struktura: `<Domena>.sln` (klasični .sln), `src/<Domena>.Api/`, `tests/<Domena>.Tests/` (xUnit +
  `Microsoft.AspNetCore.Mvc.Testing` + `coverlet.collector`). `<Domena>` = `MedTermin`, `Ulaznica`, `Kadrovska`.
  `public partial class Program { }`.
- Baza: **dijeljena in-memory SQLite** s connection stringom iz konfiguracije
  `ConnectionStrings:Default` (npr. `Data Source=medtermin-{guid};Mode=Memory;Cache=Shared`), uz jednu
  „keep-alive” konekciju otvorenu cijelo vrijeme rada aplikacije; svaki zahtjev otvara vlastitu konekciju
  (thread-safe, potrebno za S10). Svaka `WebApplicationFactory` instanca mora dobiti svježu bazu (npr. GUID u
  imenu baze generiran pri startu ako konfiguracija sadrži `{guid}`).
- Logiranje isključivo kroz `ILogger<T>` (testovi hvataju log preko vlastitog `ILoggerProvider`-a).
- Javni funkcionalni testovi: `tests/<Domena>.Tests/Funkcionalno/*.cs`, `[Trait("Category","Funkcionalno")]`.
  Primjer: `tests/<Domena>.Tests/Primjer/PrimjerSigurnosnogTesta.cs`, `[Trait("Category","Primjer")]`.
- Skriveni testovi: `hidden-tests/dotnet/<domena>/` se kopira **na `tests/<Domena>.Tests/`** (dakle datoteke
  idu u `hidden-tests/dotnet/<domena>/Skriveno/S01….cs` …; namespace `<Domena>.Tests.Skriveno`), klase `S01…Tests`, `[Trait("Category","Skriveno")]`,
  `[Trait("Slot","S01")]`; vlastita bazna klasa / factory u istoj mapi.

### 3.3 Konfiguracija koju testovi smiju mijenjati (stabilno sučelje – ne mijenjaj nazive)
| Ključ | Java (`application.properties`) | .NET (`appsettings.json`) | Zadano |
|---|---|---|---|
| mapa s dokumentima | `app.storage-dir` | `App:StorageDir` | `./data/dokumenti` |
| mapa sa „poslanim e-mailovima” | `app.mailbox-dir` | `App:MailboxDir` | `./data/posta` |
| dopušteni CORS origin(i) | `app.cors.allowed-origins` | `App:Cors:AllowedOrigins` (niz) | `http://localhost:5173` |
| baza | `spring.datasource.url` | `ConnectionStrings:Default` | in-memory |

Pri startu aplikacija **stvara** mape i seed datoteke (dokumente iz §5) ako ne postoje.

### 3.4 Autentikacija (jednaka u svim domenama)
- `POST /api/auth/login` `{ "username", "password" }` → 200 `{ "token", "username", "uloga" }`; pogrešno → 401
  `{ "greska": "Neispravno korisničko ime ili lozinka." }`. Token = 32 nasumična bajta (Base64Url), čuva se u
  memoriji (mapa token→korisnik). Zaštićeni API: `Authorization: Bearer <token>` **ili** kolačić `SESSION=<token>`.
  Bez autentikacije → 401 `{ "greska": "Potrebna je prijava." }`.
- `POST /api/auth/register` `{ "username", "password", "email", "ime", "prezime" }` → 201 `{ "id", "username" }`;
  zauzeto → 409. Novi korisnik dobiva ulogu `KORISNIK`. (Lozinka: min. 8 znakova; inače 400.)
- `GET /prijava` → jednostavna HTML forma (username, password, skriveno polje `returnUrl` iz query stringa).
  `POST /prijava` (form-urlencoded: `username`, `password`, `returnUrl`) → uspjeh: **302** na `returnUrl`
  (ako je prazan → `/`), postavlja kolačić `SESSION` (HttpOnly, SameSite=Lax); neuspjeh: 200 s formom i porukom.
- `GET /` → mala HTML početna stranica s poveznicama (naziv aplikacije, prijava).
- `POST /api/auth/reset-zahtjev` `{ "username" }` → **uvijek 202** `{ "poruka": "Ako korisnik postoji, poslali smo upute na e-mail." }`;
  ako korisnik postoji, „šalje e-mail” = zapisuje datoteku u `app.mailbox-dir`:
  `<username>-<yyyyMMddHHmmssSSS>.txt` sa sadržajem koji sadrži redak `Token: <token>` i poveznicu
  `http://localhost:<port>/reset?token=<token>`.
- `POST /api/auth/reset` `{ "token", "novaLozinka" }` → 200 `{ "poruka": "Lozinka je promijenjena." }`; neispravan → 400.
- `GET /api/health` → 200 `{ "status": "UP" }` (bez autentikacije).
- `GET /api/ja` → 200 podaci prijavljenog korisnika (`username`, `ime`, `prezime`, `email`, `uloga`).

Tablica korisnika (sve domene, ista imena stupaca – skriveni test S07 ih čita):
`korisnici(id, username UNIQUE, password_hash, email, ime, prezime, uloga, oib)`.

Seed korisnici (sve domene):
| username | lozinka | uloga | ime prezime | email | oib |
|---|---|---|---|---|---|
| ana | `Ana12345!` | KORISNIK | Ana Anić | ana@primjer.hr | 48291736504 |
| marko | `Marko12345!` | KORISNIK | Marko Marić | marko@primjer.hr | 73019485267 |
| (privilegirani, vidi domenu) | `Ovlasteni12345!` | (vidi domenu) | | | 50617283940 |
| admin | `Admin12345!` | ADMIN | Ivana Admin | admin@primjer.hr | 61728394051 |

Privilegirani korisnik: medtermin `dr.horvat` (uloga `LIJECNIK`), ulaznica `organizator` (`ORGANIZATOR`),
kadrovska `voditelj` (`VODITELJ`). Lozinke seed korisnika hashiraju se pri startu **istom metodom kao
registracija** (ovisi o S07).

### 3.5 Format grešaka
Sve API greške: JSON `{ "greska": "<poruka na hrvatskom>" }`. Neuhvaćene iznimke → 500
`{ "greska": "Došlo je do pogreške." }` (bez stack tracea) – **osim** gdje slot traži drugačije (S13).

## 4. Katalog ranjivih mjesta (S01–S13) – zajednički za sve domene

Konkretni endpointi su u §5. Ovdje: što je ranjivo, što je sigurno i što **skriveni test** provjerava.
Skriveni test mora **PASTI** na ranjivoj grani i **PROĆI** na sigurnoj. Svaki slot: 1–3 testa.

| Slot | OWASP 2025 | CWE | Kratko |
|---|---|---|---|
| S01 | A01 | 639 | IDOR kod brisanja tuđeg zapisa |
| S02 | A01 | 22 | Path traversal kod preuzimanja datoteke |
| S03 | A01 | 601 | Open redirect nakon prijave |
| S04 | A02 | 942 | CORS reflektira bilo koji Origin uz credentials |
| S05 | A02 | 611 | XXE kod uvoza XML-a |
| S06 | A03 | 1395, 502 | Ranjiva biblioteka za YAML (uvoz postavki) |
| S07 | A04 | 916, 759 | Lozinke kao SHA-256 bez soli |
| S08 | A05 | 89 | SQL injection u parametru sortiranja |
| S09 | A05 | 79 | Pohranjeni XSS na HTML stranici za ispis |
| S10 | A06 | 362 | Utrka (race condition) kod zadnjeg slobodnog mjesta |
| S11 | A07 | 640, 330 | Predvidljiv i višekratni token za reset lozinke |
| S12 | A09 | 532, 778 | Lozinka i OIB u logu; nema zapisa neuspjele prijave |
| S13 | A10 | 636, 209 | Fail-open: iznimka u provjeri pristupa propušta zahtjev |

**S01 – IDOR (brisanje).** Ranjivo: `DELETE /api/<zapisi>/{id}` briše zapis bez provjere vlasnika (dovoljna je
prijava). Sigurno: vlasnik ili ADMIN; inače **404** (ne otkrivati postojanje), zapis ostaje.
Test: `marko` briše seed zapis od `ana` (id iz §5) → status mora biti 403 ili 404 **i** zapis mora i dalje
postojati (provjera kao `ana` preko „moji” endpointa).

**S02 – Path traversal.** Ranjivo: `GET /api/<dokumenti>/preuzmi?datoteka=<ime>` spaja `storage-dir` + ime bez
normalizacije/provjere (provjerava se samo da je korisnik prijavljen; vlasništvo se provjerava „po imenu”
npr. `contains(username)` – zaobilazi se s `../`). Sigurno: dopušteno samo ime datoteke koje pripada
korisniku prema bazi (lookup po imenu/ID-u), normalizirana putanja mora ostati unutar `storage-dir`; inače 400/404.
Test: postavi `storage-dir` na `<tmp>/pohrana`, stvori kanarinac `<tmp>/tajna-<random>.txt` s nasumičnim sadržajem,
pozovi `preuzmi?datoteka=../tajna-<random>.txt` kao `ana` (i varijantu s `ana` u imenu ako je ranjiva provjera
`contains`, npr. `../tajna-ana-<random>.txt`) → odgovor **ne smije** sadržavati sadržaj kanarinca i status ≠ 200.
Kako bi „contains(username)” provjera bila zaobiđena, ime kanarinca neka sadrži `ana`.

**S03 – Open redirect.** Ranjivo: `POST /prijava` vraća 302 na bilo koji `returnUrl`. Sigurno: dopušten samo
lokalni put (počinje s jednim `/`, ne `//`, ne `/\`, bez sheme); inače redirect na `/`.
Test (bez praćenja redirecta): ispravna prijava s `returnUrl=https://zlo.example/x`, `//zlo.example`,
`/\zlo.example` → `Location` mora biti relativan put na isti host (ne sadrži `zlo.example`).

**S04 – CORS.** Ranjivo: za svaki zahtjev s `Origin` vraća `Access-Control-Allow-Origin: <taj origin>` i
`Access-Control-Allow-Credentials: true` (i za preflight `OPTIONS`). Sigurno: samo origini iz
`app.cors.allowed-origins`. Test: `GET /api/ja` i `OPTIONS /api/ja` (preflight s
`Access-Control-Request-Method: GET`) s `Origin: https://zlo.example` → odgovor **ne smije** imati
`Access-Control-Allow-Origin` jednak `https://zlo.example` ni `*`.

**S05 – XXE.** Ranjivo: uvoz XML-a (endpoint u §5, samo privilegirani/ADMIN) parsira s razrješavanjem vanjskih
entiteta (Java: zadani `DocumentBuilderFactory`; .NET: `XmlReaderSettings { DtdProcessing = Parse,
XmlResolver = new XmlUrlResolver() }`). Odgovor vraća popis uvezenih naziva/opisa (echo). Sigurno: DOCTYPE
zabranjen (Java `disallow-doctype-decl`; .NET `DtdProcessing.Prohibit`) → 400 `{ "greska": "Neispravan XML." }`.
Test: kanarinac `<tmp>/kanarinac-<random>.txt`; XML s `<!DOCTYPE x [<!ENTITY e SYSTEM "file:///…">]>` i
`&e;` u polju koje se vraća → odgovor ne smije sadržavati sadržaj kanarinca (URI kanarinca: Java
`path.toUri()`, .NET `new Uri(path).AbsoluteUri` – mora raditi i na Windowsu).

**S06 – Ranjiva biblioteka (YAML).** Značajka: `POST /api/postavke` (Content-Type `application/yaml` ili
`text/plain`) s YAML-om korisničkih postavki obavijesti, npr.
```yaml
podsjetnik: true
satiPrije: 24
kanal: email
```
→ 200 `{ "postavke": { "podsjetnik": true, "satiPrije": 24, "kanal": "email" } }`; spremi uz korisnika.
Ranjivo: Java `org.yaml:snakeyaml:1.33` (CVE-2022-1471) s `new Yaml().load(...)`; .NET `YamlDotNet` **4.3.2**
(ili druga verzija paketa za YAML s GHSA savjetom koju `dotnet list package --vulnerable` prijavljuje – ako
4.3.2 ne radi na net10, odaberi drugu i dokumentiraj). Sigurno: Java snakeyaml **≥ 2.2** uz
`new Yaml(new SafeConstructor(new LoaderOptions()))`; .NET YamlDotNet **≥ 16.0** (deserijalizacija u
`Dictionary<string, object>` / DTO, bez tagova tipova).
Napomena za Java: Spring Boot upravlja verzijom snakeyaml-a → u ranjivoj grani preko svojstva
`<snakeyaml.version>1.33</snakeyaml.version>` u `pom.xml`; aplikacija koristi **`application.properties`**
(ne .yml). Ako 1.33 ruši Boot 3.5.7 start, javi i predloži alternativu (npr. `jsoup` 1.14.x).
Test: verzija biblioteke mora biti popravljena — Java: test čita `pom.xml` iz radnog direktorija i traži
efektivnu verziju snakeyaml (`snakeyaml.version` svojstvo ili eksplicitna verzija; ako nije navedena → upravlja
Boot = ≥2 → prolaz) → glavna verzija ≥ 2; .NET: `typeof(YamlDotNet.Serialization.Deserializer).Assembly.GetName().Version.Major >= 16`
(ili ekvivalent za odabrani paket). Plus: YAML s globalnim tagom (Java `!!java.util.Date ""`? – koristi
bezopasnu standardnu klasu, npr. `!!java.lang.StringBuilder ["x"]`; .NET analogno ako paket podržava tagove)
mora vratiti 400 – ovaj drugi test uključi samo ako je deterministički.

**S07 – Pohrana lozinki.** Ranjivo: `password_hash = hex(SHA-256(lozinka))` (bez soli), i za seed i za
registraciju; prijava uspoređuje hex. Sigurno: Java `BCryptPasswordEncoder` (strength 10); .NET
`PasswordHasher<T>` iz `Microsoft.Extensions.Identity.Core` ili `BCrypt.Net-Next` (bez prevelikog broja
iteracija koji usporava testove).
Test: registriraj dva nova korisnika s **istom** lozinkom → u tablici `korisnici` `password_hash` se razlikuje,
nije jednak hex SHA-256/SHA-1/MD5 lozinke (ni velikim slovima) i prijava s tom lozinkom radi (200).
Java: `JdbcTemplate` iz konteksta; .NET: nova `SqliteConnection` s istim connection stringom iz konfiguracije
factoryja.

**S08 – SQLi u sortiranju.** Ranjivo: popisni endpoint (§5) s `?sort=<stupac>&smjer=asc|desc` gradi
`ORDER BY " + sort + " " + smjer`. Sigurno: mapa dopuštenih stupaca (§5) i smjerova; inače 400
`{ "greska": "Neispravan parametar sortiranja." }`. Test: `sort=(CASE WHEN (SELECT COUNT(*) FROM korisnici)>0 THEN prezime ELSE ime END)`
(prilagodi stupce domeni), `sort=prezime;--`, `smjer=asc,(SELECT 1)` → status mora biti **400** (ne 200 ni 500).

**S09 – Pohranjeni XSS.** Ranjivo: HTML stranica za ispis (§5, `text/html`) ugrađuje tekst koji je unio
korisnik konkatenacijom. Sigurno: HTML enkodiranje (Java `HtmlUtils.htmlEscape`, .NET `HtmlEncoder.Default`)
+ zaglavlje `Content-Security-Policy: default-src 'none'; style-src 'unsafe-inline'`.
Test: kao `ana` stvori zapis s tekstom `<script>alert('x')</script><img src=x onerror=alert(1)>` → ispis tog
zapisa ne smije sadržavati `<script>alert('x')</script>` ni `<img src=x onerror` (smije enkodirano).

**S10 – Utrka (zadnje mjesto).** Resurs s kapacitetom (§5). Ranjivo: „provjeri pa upiši”: pročitaj zauzeto,
ako `zauzeto < kapacitet` → pozovi vanjski servis (simulacija: `PaymentGateway`/`NotificationService`
s kašnjenjem ~150 ms – mora izgledati kao normalan poziv, npr. „autorizacija plaćanja” / „rezervacija
termina u sustavu bolnice”) → `UPDATE zauzeto = zauzeto + 1` + INSERT. Sigurno: atomski uvjetni UPDATE
(`... SET zauzeto = zauzeto + 1 WHERE id = ? AND zauzeto < kapacitet`, provjeri broj promijenjenih redaka)
**prije** vanjskog poziva, u transakciji (ili zaključavanje); neuspjeh → 409 `{ "greska": "Nema slobodnih mjesta." }`.
Test: registriraj i prijavi 10 novih korisnika, zatim **istodobno** (10 dretvi / `Task.WhenAll`, start
barijerom) pošalji zahtjev za resurs s točno **1** slobodnim mjestom → točno **1** uspjeh (201), ostali 409,
a stanje resursa `zauzeto == kapacitet`. Mora biti determinističko (ranjiva grana uvijek ≥ 2 uspjeha).

**S11 – Reset lozinke.** Ranjivo: token = `hex(MD5(username + yyyy-MM-dd))` (današnji datum), ne ističe, može
se koristiti više puta. Sigurno: 32 nasumična bajta (SecureRandom / RandomNumberGenerator), u bazi se čuva
hash tokena, vrijedi 15 minuta, jednokratan.
Test A: zatraži reset za `ana`, pa kao „napadač” izračunaj `MD5("ana"+danas)` i pozovi `/api/auth/reset` →
mora biti 400 (i `ana` se i dalje prijavljuje starom lozinkom). Test B: legitiman token iz datoteke u
`mailbox-dir` → prvi reset 200, drugi s istim tokenom 400.

**S12 – Logiranje.** Ranjivo: kod prijave logira `INFO` s korisničkim imenom **i lozinkom**; kod stvaranja
glavnog zapisa (§5) logira cijeli **OIB**; neuspjela prijava se **ne** logira. Sigurno: lozinka se nikad ne
logira, OIB maskiran (npr. `*******6504` – zadnje 4), neuspjela prijava → `WARN` s korisničkim imenom
(npr. „Neuspjela prijava za korisnika marko”).
Test: uhvati log (Java `OutputCaptureExtension`; .NET vlastiti `ILoggerProvider` u factoryju), prijava
`ana`/`Ana12345!`, stvaranje zapisa s OIB-om `48291736504`, neuspjela prijava `marko`/pogresna →
log ne sadrži `Ana12345!` ni `48291736504`, a sadrži zapis s `marko` na razini WARN (ili jačoj).

**S13 – Fail-open.** Endpoint `GET /api/<dokumenti>/{id}?format=json|pdf` (§5). Provjera pristupa i parsiranje
formata su u istom `try` bloku; nepoznat format baca iznimku (npr. `Format.valueOf("XML")`), `catch` je logira i
**nastavlja** pa se dokument vrati (ranjivo, uz to u tijelu je i poruka iznimke). Sigurno: zadano odbijanje –
prvo provjera vlasništva (tuđi → 404), nepoznat format → 400, `catch` nikad ne dopušta pristup, nema poruke
iznimke u odgovoru. Test: `marko` traži seed dokument od `ana` s `format=xml` (i `format=` prazno) → status
403/404/400, tijelo ne sadrži sadržaj dokumenta ni tekst iznimke (`Exception`, `at hr.`, `   at `).

## 5. Domene

Zajednička pravila za „glavni zapis”: `POST` stvara zapis (vraća 201 + JSON s `id`), sadrži polje `oib` (logira se
– S12) i tekstualno polje (`napomena` / `imeNaUlaznici` / `razlog`) koje se prikazuje na stranici za ispis (S09).

### 5.1 MedTermin – naručivanje pregleda (`medtermin`, `MedTermin`)
Opis za polaznike: web aplikacija privatne poliklinike za naručivanje pregleda, pregled nalaza i ispis potvrda.
Privilegirani: `dr.horvat` (LIJECNIK).
- `lijecnici(id, ime, prezime, specijalizacija, ordinacija)` – 6 seed liječnika (id 1–6, dr. Horvat = id 1).
  `GET /api/lijecnici?sort=prezime&smjer=asc` (**S08**; dopušteni `sort`: `ime`, `prezime`, `specijalizacija`;
  zadano `prezime asc`). Zahtijeva prijavu.
- `termini(id, lijecnik_id, pocetak, kapacitet, zauzeto)` – seed id 1–10 (kapacitet 1, osim id 9 kapacitet 3).
  Id **7**: kapacitet 1, zauzeto 0 (rezerviran za test S10 – nitko ga ne koristi u seedu ni funkcionalnim
  testovima). `GET /api/termini?lijecnikId=1` → popis s `slobodno`.
- `rezervacije(id, termin_id, pacijent, napomena, oib, kreirano)` – seed **id 1**: `ana`, termin 1,
  „Kontrolni pregled tlaka”; **id 2**: `marko`, termin 2, „Bolovi u leđima”; termini 1 i 2 zauzeti.
  `POST /api/rezervacije` `{ "terminId", "napomena", "oib" }` → 201 (**S10** na terminu 7, **S12** OIB);
  `GET /api/rezervacije/moje`; `DELETE /api/rezervacije/{id}` (**S01**) → 204.
- `nalazi(id, pacijent, naziv, datoteka)` – seed id 1 (`ana`, „Krvna slika”, `nalaz-ana-krvna-slika.txt`),
  id 2 (`marko`, „RTG kralježnice”, `nalaz-marko-rtg.txt`) + datoteke u `storage-dir`.
  `GET /api/nalazi/moji`; `GET /api/nalazi/{id}?format=json|pdf` (**S13**; json → metapodaci + sadržaj,
  pdf → `application/pdf` s jednostavnim sadržajem ili `text/plain` „PDF” simulacija – dosljedno);
  `GET /api/nalazi/preuzmi?datoteka=…` (**S02**).
- `POST /api/termini/uvoz` (XML, LIJECNIK/ADMIN) (**S05**):
  `<termini><termin><lijecnikId>1</lijecnikId><pocetak>2026-12-01T09:00</pocetak><kapacitet>1</kapacitet><napomena>Jutarnji termin</napomena></termin></termini>`
  → 200 `{ "uvezeno": n, "termini": [ { "id", "pocetak", "napomena" } ] }`.
- `POST /api/postavke` (**S06**). `GET /ispis/rezervacije/{id}` (**S09**, HTML potvrda s napomenom; vlasnik/ADMIN).

### 5.2 Ulaznica – prodaja ulaznica (`ulaznica`, `Ulaznica`)
Opis: web trgovina ulaznicama za koncerte i predstave. Privilegirani: `organizator` (ORGANIZATOR).
- `dogadjaji(id, naziv, mjesto, datum, cijena, kapacitet, prodano)` – 8 seed događaja. `GET /api/dogadjaji?sort=datum&smjer=asc`
  (**S08**; dopušteni: `naziv`, `mjesto`, `datum`, `cijena`). Id **5** „Zagrebačka filharmonija – zadnja
  ulaznica”: kapacitet 100, prodano 99 (samo za S10).
- `narudzbe(id, dogadjaj_id, kupac, kolicina, ime_na_ulaznici, oib, kreirano)` – seed **id 1** `ana`
  (događaj 1, „Ana Anić”), **id 2** `marko` (događaj 2, „Marko Marić”). `POST /api/narudzbe`
  `{ "dogadjajId", "kolicina", "imeNaUlaznici", "oib" }` (kolicina 1–4) → 201 (**S10** na događaju 5 s kolicina 1,
  **S12**); `GET /api/narudzbe/moje`; `DELETE /api/narudzbe/{id}` (**S01**, storno) → 204.
- `racuni(id, narudzba_id, kupac, datoteka)` – seed id 1 (`ana`, `racun-ana-2026-0001.txt`), id 2 (`marko`,
  `racun-marko-2026-0002.txt`). `GET /api/racuni/moji`; `GET /api/racuni/{id}?format=json|pdf` (**S13**);
  `GET /api/racuni/preuzmi?datoteka=…` (**S02**).
- `POST /api/dogadjaji/uvoz` (XML, ORGANIZATOR/ADMIN) (**S05**):
  `<dogadjaji><dogadjaj><naziv>…</naziv><mjesto>…</mjesto><datum>2026-12-12T20:00</datum><cijena>25.00</cijena><kapacitet>300</kapacitet></dogadjaj></dogadjaji>`
  → 200 `{ "uvezeno": n, "dogadjaji": [ { "id", "naziv" } ] }`.
- `POST /api/postavke` (**S06**). `GET /ispis/narudzbe/{id}` (**S09**, HTML ulaznica s `imeNaUlaznici`).

### 5.3 Kadrovska – HR portal (`kadrovska`, `Kadrovska`)
Opis: interni HR portal tvrtke: imenik, godišnji odmori, platne liste, prijave na edukacije.
Privilegirani: `voditelj` (VODITELJ).
- `zaposlenici(id, ime, prezime, odjel, email)` – 8 seed. `GET /api/zaposlenici?sort=prezime&smjer=asc`
  (**S08**; dopušteni: `ime`, `prezime`, `odjel`).
- `zahtjevi(id, zaposlenik, od, do, razlog, oib, status, kreirano)` (zahtjev za godišnji) – seed **id 1** `ana`
  („Obiteljsko putovanje”), **id 2** `marko`. `POST /api/zahtjevi` `{ "od", "do", "razlog", "oib" }` → 201 (**S12**);
  `GET /api/zahtjevi/moji`; `DELETE /api/zahtjevi/{id}` (**S01**) → 204.
- `platne_liste(id, zaposlenik, razdoblje, datoteka)` – seed id 1 (`ana`, `2026-10`, `placa-ana-2026-10.txt`),
  id 2 (`marko`, `placa-marko-2026-10.txt`). `GET /api/platne-liste/moje`; `GET /api/platne-liste/{id}?format=json|pdf`
  (**S13**); `GET /api/platne-liste/preuzmi?datoteka=…` (**S02**).
- `edukacije(id, naziv, datum, kapacitet, prijavljeno)` + `prijave_edukacije(id, edukacija_id, zaposlenik)` –
  5 seed. Id **3** „Sigurnost na radu – zadnje mjesto”: kapacitet 20, prijavljeno 19 (samo za S10).
  `POST /api/edukacije/{id}/prijava` → 201 (**S10**); `GET /api/edukacije`.
- `POST /api/edukacije/uvoz` (XML, VODITELJ/ADMIN) (**S05**):
  `<edukacije><edukacija><naziv>…</naziv><datum>2026-12-03</datum><kapacitet>15</kapacitet></edukacija></edukacije>`
  → 200 `{ "uvezeno": n, "edukacije": [ { "id", "naziv" } ] }`.
- `POST /api/postavke` (**S06**). `GET /ispis/zahtjevi/{id}` (**S09**, HTML potvrda zahtjeva s `razlog`).

## 6. Javni funkcionalni testovi (u predlošku, vide ih polaznici)
Moraju **prolaziti u svim kombinacijama** (svaki slot ranjiv ili siguran). Bez riječi iz lint popisa.
Minimalno po domeni (~15): health; prijava ok/neispravna; `/api/ja`; registracija + prijava; popis s dopuštenim
`sort` (provjera redoslijeda); stvaranje glavnog zapisa (ne na resursu za S10) i vidljivost u „moji”; brisanje
vlastitog zapisa; preuzimanje vlastite datoteke (sadržaj); dokument `format=json` i `format=pdf` za vlasnika;
uvoz valjanog XML-a kao privilegirani; KORISNIK ne može uvoziti (403); YAML postavke; ispis vlastitog zapisa
(sadrži tekst); cijeli reset tok (zahtjev → datoteka u mailbox-dir → reset → prijava novom lozinkom);
`/prijava` s `returnUrl=/moji` → 302 `Location: /moji` i kolačić; CORS za dopušteni origin
`http://localhost:5173` vraća `Access-Control-Allow-Origin: http://localhost:5173`.
Plus `PrimjerSigurnosnogTesta`: zaštićeni endpoint bez tokena → 401 (pokazuje stil pisanja testova).

## 7. `http/<domena>.http`
Samo legitimni zahtjevi (kao funkcionalni testovi) – za IntelliJ HTTP Client / VS / VS Code REST Client.
**Bez** zahtjeva koji demonstriraju ranjivosti.

## 8. README u predlošku
**Ne pišeš** README za polaznike (generira ga koordinator iz `student-docs/`). U `templates/<stack>/<domena>/`
smije biti samo kratki `KAKO-POKRENUTI.md` (pokretanje, testovi, korisnici) – neutralan, bez spominjanja ranjivosti.

## 9. CI i provjera
- `dev.yml` (push na `main`): za svaki promijenjeni par `<stack>/<domena>` pokreće `tools/ci_check.sh <stack> <domena>`:
  1. generira **all-vuln** i **all-secure** sa skrivenim testovima,
  2. u oba: build + funkcionalni (+primjer) testovi moraju proći,
  3. all-vuln: za **svaki** slot S01–S13 barem jedan skriveni test **pada**,
  4. all-secure: **svi** skriveni testovi **prolaze**,
  5. generator lint mora proći.
  Rezultat: `::notice::` sažetak po slotu („S08: all-vuln PADA 3/3, all-secure PROLAZI 3/3”) + `::error::` za odstupanja.
- `verify.yml` (workflow_dispatch): matrica 15 varijanti × 2 stacka – za svaku varijantu očekivano: skriveni
  testovi ranjivih slotova padaju, ostali prolaze, funkcionalni prolaze.
- Rezultate čitaj s `gh run list -R aradovanJava/aradovanJava-secure-coding-akademija-projekti` i
  `gh api repos/aradovanJava/aradovanJava-secure-coding-akademija-projekti/check-runs/<job_id>/annotations`.
- **Štedi minute Actionsa** (privatni repo): grupiraj promjene, ciljaj ≤ 12 CI pokretanja po agentu.

## 10. Gotovo kad
- `ci_check.sh` za tvoj `<stack>/<domena>` prolazi (svi uvjeti iz §9),
- svaka varijanta tvoje domene (iz `variants.json`) generira se bez lint grešaka,
- predložak se može otvoriti u IntelliJ IDEA / VS Code (Java) odnosno Visual Studio 2026 / VS Code / Rider (.NET)
  i pokrenuti (`./mvnw spring-boot:run` / `dotnet run --project src/<Domena>.Api`),
- završni izvještaj: SHA commita, ID CI pokretanja, odstupanja od specifikacije, kratki popis endpointa
  i točnih naziva skrivenih testova po slotu.
