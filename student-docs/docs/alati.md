# Alati za sigurnosnu analizu – projekt {{VARIJANTA}}

Program traži da ranjivosti pronađeš **standardnim alatima** i potvrdiš popravak **ponovnim skeniranjem**.
Koristi barem po jedan alat iz svake skupine (SAST, SCA, DAST) i **spremi izvještaje** u mapu `alati/` (prije i
poslije popravaka, npr. `alati/prije/`, `alati/poslije/`). Alati prijavljuju i lažno pozitivne nalaze – u
izvještaju objasni što nije stvarna ranjivost i zašto.

> Alate pokreći samo prema vlastitoj lokalnoj instanci (`http://localhost:8080` / `http://localhost:5080`).

## 1. SAST – statička analiza koda

### Semgrep (Java i C#)
```bash
pip install semgrep          # ili: docker run --rm -v "${PWD}:/src" semgrep/semgrep semgrep scan ...
semgrep scan --config p/owasp-top-ten --config p/security-audit --config p/java   java/   --sarif -o alati/prije/semgrep-java.sarif
semgrep scan --config p/owasp-top-ten --config p/security-audit --config p/csharp dotnet/ --sarif -o alati/prije/semgrep-dotnet.sarif
```
SARIF otvori u VS Code (*SARIF Viewer*) ili koristi `--json` / tekstualni ispis.

### SpotBugs + Find Security Bugs (Java)
Projekt ima Maven profil `sast`:
```bash
./mvnw -Psast compile spotbugs:spotbugs   # rezultat: target/spotbugsXml.xml
./mvnw -Psast compile spotbugs:gui        # pregled nalaza u grafičkom sučelju
```
U IntelliJ IDEA možeš instalirati i dodatak *SpotBugs* (uz *Find Security Bugs*).

### Roslyn analizatori (.NET)
Sigurnosna pravila nisu uključena po zadanim postavkama – uključi ih pri buildu:
```bash
dotnet build -p:AnalysisMode=All > alati/prije/roslyn.txt
```
Pravila iz kategorije *Security* imaju oznake `CA2xxx`/`CA3xxx`/`CA5xxx`. U Visual Studiju ih vidiš u *Error List*.

## 2. SCA – analiza ovisnosti (komponente s poznatim ranjivostima)

| Alat | Java | .NET |
|---|---|---|
| ugrađeno | – | `dotnet list package --vulnerable --include-transitive` (i upozorenja `NU1901–NU1904` pri buildu) |
| OSV-Scanner | `osv-scanner scan source -r java/` | `dotnet restore --use-lock-file`, zatim `osv-scanner scan source -r dotnet/` |
| Trivy | `trivy fs --scanners vuln java/` | `trivy fs --scanners vuln dotnet/` |
| OWASP Dependency-Check | `dependency-check --scan java/ --format HTML --out alati/prije/` (preporučen NVD API ključ; prvo pokretanje dugo traje) | isto, nad `dotnet/` nakon builda |
| SBOM (CycloneDX) | `./mvnw -Psca package -DskipTests` | `dotnet tool install --global CycloneDX`, zatim `dotnet CycloneDX {{DOMENA_KLASA}}.sln -o alati/` |

Za svaku ranjivu komponentu u izvještaju navedi: CVE/GHSA oznaku, je li ranjivi dio **stvarno korišten** u kodu,
na koju si verziju nadogradio i je li nadogradnja zahtijevala promjene u kodu.

## 3. DAST – dinamička analiza pokrenute aplikacije

### OWASP ZAP
1. Pokreni aplikaciju, zatim ZAP (*Automated Scan* ili *Manual Explore*).
2. **Prijava:** API koristi token – u ZAP-u *Tools → Options → Replacer* dodaj pravilo koje svakom zahtjevu dodaje
   zaglavlje `Authorization: Bearer <token>` (token dobiješ prijavom). Za web dio se prijavi kroz `/prijava`
   u pregledniku koji ide preko ZAP-a.
3. Prođi kroz aplikaciju (zahtjevi iz `http/{{DOMENA}}.http` kroz ZAP proxy `localhost:8090` ili ručno u pregledniku),
   zatim *Spider* i *Active Scan* nad `http://localhost:<port>`.
4. *Report → Generate Report* (HTML) → `alati/prije/zap.html`.

Brzi pasivni pregled iz Dockera (Linux; na Windowsu/macOS-u umjesto `localhost` koristi `host.docker.internal`):
```bash
docker run --rm --network host -v "$(pwd)/alati:/zap/wrk" zaproxy/zap-stable \
  zap-baseline.py -t http://localhost:8080 -r zap-baseline.html
```

### Burp Suite Community
Proxy + *Repeater* su najbolji za ručnu provjeru i dokazivanje nalaza (mijenjaj parametre, zaglavlja i tijelo
zahtjeva te promatraj odgovor). Snimke zahtjeva/odgovora koristi kao dokaz u izvještaju.

## 4. Ručni pregled koda

Alati ne vide sve – posebno pogreške u poslovnoj logici i autorizaciji. Za svaki endpoint prođi kroz pitanja:

- Tko smije pozvati ovu operaciju i **nad kojim podacima**? Gdje se to provjerava?
- Kamo završava svaki ulazni podatak (SQL, datotečni sustav, HTML, XML parser, preusmjeravanje, log, zaglavlja)?
- Kako se pohranjuju i provjeravaju tajne (lozinke, tokeni)? Što je predvidljivo?
- Što se događa kad dvije operacije stignu **istodobno**?
- Što se događa kad nešto **baci iznimku** – koja grana koda se tada izvršava?
- Koje su verzije biblioteka i kako se koriste?
- Što aplikacija zapisuje u log i što vraća klijentu u porukama o greškama?
- Koja sigurnosna zaglavlja i postavke preglednika aplikacija šalje?

## 5. Testovi i pokrivenost koda

Tehnike koje će ti trebati u testovima:

| Što provjeravaš | Java (JUnit 5, Spring Boot Test) | .NET (xUnit, WebApplicationFactory) |
|---|---|---|
| status, zaglavlja, tijelo odgovora | `TestRestTemplate` / `MockMvc` | `factory.CreateClient()` |
| zahtjev bez automatskog praćenja preusmjeravanja | `MockMvc` ili HTTP klijent s isključenim redirectom | `CreateClient(new() { AllowAutoRedirect = false })` |
| stanje u bazi | `@Autowired JdbcTemplate` | `SqliteConnection` s connection stringom iz konfiguracije |
| sadržaj loga | `@ExtendWith(OutputCaptureExtension.class)` | vlastiti `ILoggerProvider` u `WithWebHostBuilder` |
| istodobni zahtjevi | `ExecutorService` + `CountDownLatch` | `Task.WhenAll` |
| privremene datoteke | `@TempDir` + `@DynamicPropertySource` | `Path.GetTempPath()` + `UseSetting(...)` |

Pokrivenost koda:
- **Java:** `./mvnw test` → `target/site/jacoco/index.html` (postotak *Lines*).
- **.NET:** `dotnet test --collect:"XPlat Code Coverage"`, zatim
  `dotnet tool install -g dotnet-reportgenerator-globaltool` i
  `reportgenerator -reports:"tests/**/TestResults/**/coverage.cobertura.xml" -targetdir:alati/pokrivenost`.

Svaki sigurnosni test mora **pasti na izvornom kodu** (to dokazuje ranjivost) i **proći nakon popravka**.
Najlakše: prvo napiši test, pokreni ga (crveno), pa popravi kod (zeleno) i napravi commit.
