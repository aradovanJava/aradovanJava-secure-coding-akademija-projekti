# Tjedan 3 – DevSecOps cjevovod za vaš T2 projekt

Predložak GitHub Actions cjevovoda koji svaki push i pull request provjerava **testovima, SAST-om, SCA-om,
skeniranjem tajni i DAST-om**, a na kraju **sigurnosna vrata** (quality gate) odlučuju smije li promjena dalje.

| Mapa | Za projekt |
|---|---|
| [`java/`](java) | Java / Spring Boot (mapa `java/` iz vašeg T2 ZIP-a – ondje gdje je `pom.xml`) |
| [`dotnet/`](dotnet) | C# / .NET 10 (mapa `dotnet/` iz vašeg T2 ZIP-a – ondje gdje je `*.sln`) |

```
.github/workflows/devsecops.yml   poslovi i artefakti (logike nema – sve je u ci/)
.github/dependabot.yml            tjedni PR-ovi za Maven/NuGet i GitHub Actions
ci/build-test.sh  ci/sast.sh  ci/sca.sh  ci/secrets.sh  ci/dast.sh     koraci (rade i lokalno)
ci/gate.py                        sigurnosna vrata – JEDINO mjesto odluke
ci/prihvaceno.txt                 prihvaćeni nalazi (s obrazloženjem)
ci/semgrep/regresije.yml          vlastita Semgrep pravila (čuvari popravljenih propusta)
ci/zap_hooks.py  ci/dast-putanje.txt   prijava i ciljane provjere za ZAP
.semgrepignore  .gitleaks.toml  osv-scanner.toml
```

## 1. Dodavanje u vaš repozitorij

```bash
cd moj-projekt              # korijen repozitorija = mapa s pom.xml (ili *.sln)
cp -r <akademija>/tjedan-3/devsecops/java/. .      # ili .../dotnet/.
git add .github ci .semgrepignore .gitleaks.toml osv-scanner.toml
git commit -m "DevSecOps cjevovod" && git push
```

- Na Windowsu kopirajte i **skrivene** mape/datoteke (`.github`, `.semgrepignore` …).
- Repozitorij smije biti javni ili privatni (besplatni plan). Rezultati su uvijek u **Summary** posla *Sigurnosna vrata*
  i u **artefaktima** (`izvjestaj-*`, `sigurnosna-vrata`). *Code scanning* (kartica Security) radi samo u javnim
  repozitorijima ili uz GitHub Advanced Security – zato je slanje SARIF-a *best effort* (`continue-on-error`).
- Neobavezno: secret `DAST_LOZINKA` (Settings → Secrets → Actions) ako ste promijenili lozinku testnog korisnika `ana`.
- Settings → Code security: uključite *Dependabot alerts* i *security updates*.
- `izvjestaji/` i `.ci-alati/` skripte same isključuju iz gita.

Lokalno (Linux/macOS/WSL; za DAST treba Docker): `bash ci/build-test.sh`, `bash ci/sast.sh`, … i na kraju
`python3 ci/gate.py` (bez Dockera: `GATE_PRESKOCI=dast python3 ci/gate.py`).

## 2. Poslovi

| Posao | Što radi | Izvještaji |
|---|---|---|
| **Build, testovi, pokrivenost** | `mvnw verify` / `dotnet test` – svi testovi (i vaši sigurnosni iz T2); JaCoCo / Coverlet | `testovi/`, `pokrivenost/` |
| **SAST** | Semgrep (`p/owasp-top-ten` + `p/java` ili `p/csharp` + `ci/semgrep/`); Java: SpotBugs + Find Security Bugs (`-Psast`); .NET: Roslyn analizatori s `AnalysisMode=All` | `semgrep.sarif/json`, `spotbugs.sarif/xml`, `roslyn.sarif` |
| **SCA** | CycloneDX SBOM (sve ovisnosti, i tranzitivne) → OSV-Scanner; .NET i `dotnet list package --vulnerable --include-transitive` | `sbom.cdx.json`, `osv.sarif/json`, `nuget-audit.*` |
| **Pregled ovisnosti u PR-u** | `dependency-review-action` (samo PR; bez GHAS u privatnom repozitoriju ne radi → ne blokira) | – |
| **Tajne** | gitleaks nad **cijelom poviješću** (`fetch-depth: 0`) – i obrisana tajna je procurila | `gitleaks.sarif` |
| **DAST** | pokrene aplikaciju, čeka `/api/health`, ZAP baseline (Docker) + kuke iz `ci/zap_hooks.py` | `zap/zap.html`, `zap.json`, `zap.sarif` |
| **Sigurnosna vrata** | `ci/gate.py`: politika + `ci/prihvaceno.txt` → PROLAZ / NE PROLAZI | `gate.json`, Summary |

**Politika vrata** (vrh `ci/gate.py`): blokiraju samo **visoki/kritični** nalazi – Semgrep `ERROR`; SpotBugs kategorija
SECURITY s prioritetom High/Normal (osim informativnih `SPRING_ENDPOINT`, `CRLF_INJECTION_LOGS`); Roslyn pravila kategorije
*Security* (osim pravila „za pregled” CA2100, CA5391, CA5395); OSV CVSS ≥ 7,0; NuGet `High`/`Critical`; **svaka** tajna;
ZAP rizik *High*. Ostalo je informativno (u Summaryju pod „Informativni nalazi”).

**Zatvoreno pri grešci (fail-closed):** ako izvještaj nekog alata nedostaje ili je posao pao, vrata **ne prolaze**.
Alat koji nije radio nije isto što i alat koji ništa nije našao (isto načelo kao S13 u T2).

## 3. Čitanje rezultata

1. Actions → zadnje pokretanje → posao **Sigurnosna vrata** → Summary: tablica po kategorijama, zatim blokirajući
   i prihvaćeni nalazi (alat, pravilo, datoteka:redak, opis).
2. Detalji: artefakt `izvjestaj-sast` (SARIF otvorite u VS Code s ekstenzijom *SARIF Viewer*), `izvjestaj-dast` → `zap/zap.html`.
3. Za svaki blokirajući nalaz: popravite kod → push. Tek ako ste **sigurni** da je lažno pozitivan, vidi točku 4.

## 4. Lažno pozitivni nalazi – redoslijed izbora

1. **Popravite ili pojednostavnite kod** tako da ga alat razumije (npr. zabrana DOCTYPE odmah uz `newInstance()`;
   umjesto rječnika stupaca `switch` koji vraća konstantne SQL nizove – tada Roslyn CA3001 nestaje).
2. **Iznimka u kodu, uz razlog**: `// nosemgrep: <id-pravila>`; Java `@SuppressFBWarnings(value = "...", justification = "...")`;
   C# `#pragma warning disable CA3001 // razlog` ili `[SuppressMessage(...)]`. Vidljiva je u code reviewu.
3. **`ci/prihvaceno.txt`**: `alat | pravilo | datoteka | odsječak | obrazloženje`. Neka bude **što uža** – s *odsječkom*
   koda koji postoji samo u ispravnoj verziji (za SpotBugs se odsječak traži u cijeloj metodi). Iznimka samo po
   pravilu i datoteci sakrila bi i ponovno uveden propust na istom mjestu.
4. Ovisnosti: radije nadogradnja (Dependabot PR); privremeno `osv-scanner.toml` → `[[IgnoredVulns]]` s `reason` i `ignoreUntil`.
5. Tajne: ako je stvarno lažno pozitivno – otisak u `.gitleaksignore`; ako je **prava** tajna – **opozovite je** (brisanje iz gita nije dovoljno).

Neiskorištene iznimke vrata ispisuju na kraju – obrišite ih.

## 5. Zašto vrata moraju pasti kad se propust ponovno uvede

Popravak iz T2 vrijedi samo dok ga netko ne „pojednostavi”. Vrata su automatski regresijski test: ako netko vrati
`new Yaml()`, ranjivu verziju biblioteke, `Redirect(returnUrl)` ili CORS bez popisa origina, build **mora** pasti
prije spajanja u `main`. Zato: vrata ne smiju biti „samo upozorenje”, iznimke moraju biti uske, a za propuste koje
opći alati ne vide pišemo **vlastita pravila** (`ci/semgrep/regresije.yml`) i zadržavamo **sigurnosne testove** iz T2
u build poslu.

Predložak je testiran (`.github/workflows/t3-devsecops.yml`) na MedTerminu u dva stanja: **svi propusti popravljeni**
(vrata prolaze, uz dokumentirane iznimke iz `test/prihvaceno-*.txt`) i **svih 13 propusta prisutno** (vrata padaju):

| T2 propust | Java – tko ga hvata | .NET – tko ga hvata |
|---|---|---|
| S02 path traversal | – (FSB/Semgrep ne razlikuju popravak) | Roslyn **CA3003** (×2) |
| S03 open redirect | ZAP **10028** *Off-site Redirect* (kuka šalje prijavu s vanjskim `returnUrl`) | ZAP **10028** |
| S04 CORS refleksija | ZAP – CORS provjera iz kuke (Origin `https://zlo.example` + credentials) | Semgrep `csharp-cors-bilo-koji-origin` + ZAP |
| S05 XXE | Semgrep `java-xxe-documentbuilderfactory-bez-zabrane-doctype` | Semgrep `csharp-xxe-dtdprocessing-parse` |
| S06 ranjiva YAML biblioteka | **OSV** snakeyaml 1.33 (GHSA-mjmj-j48q-9wg2, CVSS 8,3) + Semgrep `java-snakeyaml-bez-safeconstructor` | **OSV + NuGet audit** YamlDotNet 4.3.2 (GHSA-rpch-cqj9-h65r) |
| S08 SQLi u sortiranju | Semgrep `tainted-sql-string` + SpotBugs `SQL_INJECTION_SPRING_JDBC` | Roslyn CA3001 – ali i na popravku (vidi niže) |
| S11 predvidljiv reset token (MD5) | Semgrep `java-slab-hash-za-tokene-ili-lozinke` | Semgrep `csharp-md5-sha1` + Roslyn **CA5351** |
| S01, S07, S09, S10, S12, S13 | – | – |

Propusti u **logici** (tuđi zapis, utrka, što se logira, fail-open, nesoljeni SHA-256) alati ne vide – njih hvataju
samo testovi. To je glavna poruka tablice.

### Podešavanje koje smo napravili (i zašto)

- **Vlastita Semgrep pravila** (`ci/semgrep/regresije.yml`): pravila iz registra ne prepoznaju tvornicu XML parsera u
  zasebnoj metodi ni ulančani `new Yaml().load(...)`, a Semgrep ne parsira C# primarne konstruktore do kraja. Uska
  pravila visoke pouzdanosti hvataju S04/S05/S06/S11 bez ijednog nalaza na popravljenom kodu.
- **SpotBugs**: blokira prioritet High/Normal; `SPRING_ENDPOINT` (popis endpointa) i `CRLF_INJECTION_LOGS` su informativni.
  Find Security Bugs javlja `XXE_DOCUMENT` i na popravljenom kodu jer ne prati poziv `tvornica()` – nalaz je prihvaćen,
  a regresiju čuva vlastito Semgrep pravilo (primjer kako jedan alat pokriva slijepu točku drugoga).
- **S08 (ORDER BY iz popisa dopuštenih stupaca)**: Semgrep, SpotBugs i Roslyn to ne razlikuju od ranjivog koda.
  Java iznimke imaju *odsječak* (`stupac + " " + redoslijed`, `STUPCI.get(sort)`) pa ranjiva verzija i dalje blokira.
  U .NET-u CA3001 javlja nalaz u zajedničkom sinku `Baza.cs` – iznimka bez odsječka sakriva i regresiju; zato preporuka:
  refaktorirajte (konstantni SQL), pa iznimku obrišite.
- **Roslyn**: `AnalysisMode=All` uključuje i stotine pravila kvalitete – vrata gledaju samo kategoriju *Security*;
  CA2100/CA5391/CA5395 su pravila „za ručni pregled”, ne dokaz propusta.
- **Platforma T2**: Spring Boot 3.5.7 (listopad 2025) danas ima 28 OSV nalaza visoke/kritične ozbiljnosti u tranzitivnim
  ovisnostima (Tomcat, Jackson, Spring MVC/Expression, Spring Boot), a Microsoft.Data.Sqlite 10.0.0 u SQLitePCLRaw. Vrata to **ispravno**
  javljaju. Rješenje u vašem projektu: nadogradnja (Dependabot PR); ono što ostane – privremeno u `osv-scanner.toml` s rokom.
- **ZAP baseline** je pasivan i bez prijave vidi samo `/`, `/prijava` i `/api/health`. Kuka `ci/zap_hooks.py` prijavi
  testnog korisnika, posjeti putanje iz `ci/dast-putanje.txt` (dodajte svoje!) i pošalje dvije ciljane provjere
  (vanjski `returnUrl`, zli `Origin`). Upozorenja *Medium* (npr. nedostaje CSP, anti-clickjacking) T2 aplikacije imaju i
  kad su popravljene – riješit ćete ih mehanizmima okvira (`../okviri`) i zatim prag u `ci/gate.py` spustiti na Medium.
- Semgrep javlja i pravila za sam workflow (npr. akcije po oznaci `@v5` umjesto SHA) – informativno; za veću
  sigurnost lanca opskrbe zaključajte akcije na SHA (Dependabot ih i dalje ažurira).

## 6. Verzije alata

Semgrep 1.183.0 · SpotBugs Maven plugin 4.8.6.6 + Find Security Bugs 1.13.0 (iz `pom.xml`) · Roslyn NetAnalyzers iz
.NET 10 SDK-a · CycloneDX Maven 2.9.1 / CycloneDX .NET 6.3.1 · OSV-Scanner 2.7.0 · gitleaks 8.30.1 · OWASP ZAP 2.17.0
(`ghcr.io/zaproxy/zaproxy`) · akcije: checkout@v5, setup-java@v5, setup-dotnet@v5, setup-python@v6,
upload-artifact@v6, download-artifact@v6, codeql-action/upload-sarif@v4, dependency-review-action@v4.
Verzije alata su u `ci/zajednicko.sh` (Dependabot ih ne vidi – provjerite ih jednom mjesečno).
