// Vodič za predavača: kako pokazati demo t3-dan3-medtermin-demo po blokovima P3 (Tjedan 3, Dan 3).
// node napravi_vodic_dan3.js izlaz.docx
const fs = require("fs");
const path = require("path");
const { Document, Packer, Paragraph, TextRun, ImageRun, BorderStyle, AlignmentType } = require("docx");
const { PINK, TAMNA, SIVA, FONT, P, H1, H2, H3, B, koraci, kod, tablica, okvir, razmak, stilovi, numeracija, zaglavlje, podnozje } = require("./osnova");

const IZLAZ = process.argv[2] || "vodic.docx";
const R = "https://github.com/aradovanJava/t3-dan3-medtermin-demo";
const PR = (n) => `[PR #${n}](${R}/pull/${n})`;
const RUN = (id, t) => `[${t}](${R}/actions/runs/${id})`;
const DOC = (f, t) => `[${t || f}](${R}/blob/main/${f})`;
const D = [];
const s = (...x) => D.push(...x.flat());

// ------------------------------------------------------------------ naslovnica
s(
  new Paragraph({ spacing: { before: 2000, after: 120 }, children: [new TextRun({ text: "SECURE CODING AKADEMIJA · TJEDAN 3 · DAN 3", bold: true, color: PINK, size: 20 })] }),
  new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Demo: ispitivanje sigurnosti, rizik i usklađenost", font: FONT, size: 52, bold: true, color: TAMNA })] }),
  new Paragraph({ spacing: { after: 500 }, children: [new TextRun({ text: "Upute za predavača – kako pokazati demo repozitorij po blokovima radionice P3", size: 30, color: SIVA })] }),
  new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: PINK, space: 4 } }, spacing: { after: 300 }, children: [] }),
  P(`Repozitorij: [aradovanJava/t3-dan3-medtermin-demo](${R}) (privatan)`),
  P("Prezentacija: **P3 – Ispitivanje sigurnosti, rizik i usklađenost** (29 slajdova, s bilješkama govornika)"),
  P("Projekt: **MedTermin** – Java 21, Spring Boot 3.5; referentno rješenje T2 s DevSecOps predloškom iz T3 paketa"),
  P("Stanje: 19. 11. 2026. · sigurnosna vrata zelena na `main` · 60 testova · pokrivenost 90,2 %"),
  razmak(),
  okvir("pazite", [
    "Aplikacija u repozitoriju je **referentno rješenje T2** (svih 13 propusta popravljeno). Ne otvarajte izvorni kod u `src/main/` i ne otvarajte karticu *Files changed* u PR-u #14 – to je rješenje S10.",
    "Dokumenti u `docs/` su riješen primjer predaje za domenu MedTermin. Pokazujte ih na projektoru, ali ih **ne dijelite** polaznicima i ne stavljajte na Moodle.",
  ], "SAMO ZA PREDAVAČA"),
);

// ------------------------------------------------------------------ sadržaj
s(H1("Sadržaj"));
[
  "1. Pregled dema", "2. Priprema", "3. Blok 1 – Pipeline (slajdovi 5–7)", "4. Blok 2 – Ispitivanje (slajdovi 8–13)",
  "5. Blok 3 – Model prijetnji (slajdovi 14–17)", "6. Blok 4 – Analiza rizika (slajdovi 18–21)",
  "7. Blok 5 – Usklađenost (slajdovi 22–26)", "8. Završetak: od dema do predaje polaznika", "9. Ako nešto pođe po zlu",
  "Dodatak A – Sve poveznice", "Dodatak B – Brojke na jednom mjestu",
].forEach((t) => s(new Paragraph({ spacing: { after: 50 }, children: [new TextRun({ text: t, size: 21 })] })));

// ------------------------------------------------------------------ 1. pregled
s(H1("1. Pregled dema"));
s(P("Radionica P3 ima pet blokova. U svakom bloku najprije kratko pokažete **gotov primjer na MedTerminu**, a zatim polaznici isto rade na svojim repozitorijima (zadaci su na slajdovima). Demo repozitorij je u stanju u kojem bi ga dobar polaznik predao u nedjelju: zeleni pipeline, dokaz da vrata padaju, sigurnosni testovi, nalazi, model prijetnji, registar rizika i ASVS lista s dokazima."));
s(P(`Ove upute detaljno razrađuju ${DOC("docs/README.md", "docs/README.md")} iz repozitorija: za svaki korak piše na što kliknuti, što se vidi na zaslonu, što reći i koja pitanja postaviti (s očekivanim odgovorima).`));

s(H2("1.1 Raspored"));
s(tablica(["Blok", "Slajdovi", "Ukupno", "Demo", "Što se pokazuje"], [
  ["1 · Pipeline", "5–7", "~45 min", "12 min", "Actions i Summary vrata, PR #11 (nadogradnja), Dependabot, PR #13 i #14 (dokaz pada)"],
  ["2 · Ispitivanje", "8–13", "~40 min", "15 min", "plan ispitivanja, sigurnosni testovi, ručni testovi uživo, nalaz N-01 (PR #12) i N-02"],
  ["3 · Model prijetnji", "14–17", "~35 min", "10 min", "DFD s granicama povjerenja, STRIDE tablica"],
  ["4 · Analiza rizika", "18–21", "~25 min", "8 min", "registar rizika – ljestvice, četiri postupanja, vlasnik i rok"],
  ["5 · Usklađenost", "22–26", "~40 min", "10 min", "ASVS 5.0.0 lista s dokazima, sigurnosna pravila, GDPR/NIS2/CRA, SECURITY.md"],
], [1500, 900, 900, 800, 5538], { prviPodebljan: true }));
s(P("Ostatak vremena u svakom bloku polaznici rade na svojim repozitorijima. Ukupno s pauzom oko 3 h 25 min, kako je predviđeno u bilješkama P3.", { spacing: { before: 120, after: 120 } }));

s(H2("1.2 Pravila prikaza"));
s(B("**Pokazujte:** Actions (pokretanja i Summary vrata), pull requestove (Conversation, Commits, Checks), testove u `src/test/` i dokumente u `docs/`."));
s(B("**Ne pokazujte:** `src/main/` i diff PR-a #14 (rješenje T2). Diff PR-a #13 smijete pokazati – to je samo verzija biblioteke."));
s(B("Dokumenti u `docs/` su primjer za MedTermin. Polaznici s istom domenom ne smiju dobiti gotove tekstove – na projektoru ih vide, ali ne dobivaju poveznicu."));
s(B("Sve poveznice u ovom dokumentu vode na privatni repozitorij – otvarate ih vi, prijavljeni na GitHub."));

s(H2("1.3 Karta repozitorija"));
s(tablica(["Što", "Gdje"], [
  ["Vodič po blokovima (kratko)", "`docs/README.md`"],
  ["Pipeline i vrata", "`.github/workflows/devsecops.yml`, `ci/` (skripte, `prihvaceno.txt`, `dast-putanje.txt`), `osv-scanner.toml`"],
  ["Sigurnosni testovi", "`src/test/java/hr/span/akademija/medtermin/sigurnost/` – S01, S02, S03, S04, S09, S10, S12, S13, N01"],
  ["Plan i ručni testovi", "`docs/plan-ispitivanja.md`, `docs/rucni-testovi.http`"],
  ["Nalazi", "`docs/nalazi/N-01-sesija-bez-isteka.md` (popravljen), `docs/nalazi/N-02-bez-zastite-od-pogadanja-lozinke.md` (otvoren)"],
  ["Model prijetnji", "`docs/dfd.md`, `docs/dfd.png` (izvor `docs/dfd.dot`), `docs/stride.md`"],
  ["Rizici", "`docs/registar-rizika.md`"],
  ["Usklađenost", "`docs/asvs.md`, `docs/sigurnosna-pravila.md`, `docs/uskladenost.md`, `SECURITY.md`"],
  ["Pokretanje aplikacije", "`KAKO-POKRENUTI.md` (korisnici i lozinke iz seeda)"],
], [2600, 7038], { prviPodebljan: true }));

s(H2("1.4 Pull requestovi i grane"));
s(tablica(["PR", "Grana", "Stanje", "Za što služi"], [
  ["#1 – #10", "`dependabot/…`", "otvoreni; #4 i #8 ne prolaze", "Blok 1, korak 3: što Dependabot radi i zašto PR nije automatski siguran"],
  ["#11", "`ovisnosti/spring-boot-3.5.16`", "spojen", "Blok 1, korak 3: nadogradnja umjesto općih iznimki (crveno → zeleno)"],
  ["#12", "`nalaz/N-01-istek-sesije`", "spojen", "Blok 2: nalaz N-01 – test crven, zatim popravak zelen"],
  ["#13", "`dokaz/regresija-s06`", "otvoren (draft) – ne spajati", "Blok 1, korak 6: vraćen S06 → SCA i Semgrep blokiraju"],
  ["#14", "`dokaz/regresija-s10`", "otvoren (draft) – ne spajati", "Blok 1, korak 6 i blok 2: vraćen S10 → svi alati zeleni, pada samo test"],
], [1100, 2700, 2200, 3638]));

// ------------------------------------------------------------------ 2. priprema
s(H1("2. Priprema"));
s(H2("2.1 Dan prije nastave"));
s(koraci([
  "Klonirajte repozitorij (ili povucite zadnje stanje ako ga već imate):",
]));
s(kod(`git clone https://github.com/aradovanJava/t3-dan3-medtermin-demo.git
cd t3-dan3-medtermin-demo
git pull`));
s(koraci([
  "Provjerite Javu: `java -version` mora pokazati 21 ili noviju.",
  "Pokrenite testove jednom da se preuzmu ovisnosti (prvi put nekoliko minuta): `.\\mvnw.cmd test`. Očekivano na kraju: `Tests run: 60, Failures: 0, Errors: 0` i `BUILD SUCCESS`.",
  "Ako Maven Wrapper javi `Get-Item : Could not find item …\\.m2`, mapa `.m2` je skrivena: `attrib -h \"$env:USERPROFILE\\.m2\"` i ponovite.",
  `Na GitHubu otvorite **Actions → devsecops** i provjerite da je zadnje pokretanje na \`main\` zeleno. Ako je starije od tjedan dana, pokrenite novo: **Run workflow → Branch: main → Run workflow** (oko 3 minute).`,
  "Provjerite datum: privremene iznimke u `osv-scanner.toml` vrijede do **31. 1. 2027.** Nakon toga vrata na `main` namjerno padaju (rizik R-02).",
], true));

s(H2("2.2 Petnaest minuta prije"));
s(koraci([
  "Oslobodite port 8080. Ako je zauzet (npr. Camunda u Docker Desktopu), zaustavite taj kontejner ili proces:",
]));
s(kod(`# tko drži port 8080?
Get-NetTCPConnection -LocalPort 8080 -State Listen | Select-Object OwningProcess
Get-Process -Id <OwningProcess>`));
s(koraci([
  "Pokrenite aplikaciju u mapi repozitorija: `.\\mvnw.cmd spring-boot:run`. Pričekajte redak `Started MedTerminApplication`.",
  "U pregledniku otvorite `http://localhost:8080/api/health` – očekivano `{\"status\":\"UP\"}`.",
  "U IntelliJ IDEA otvorite projekt i tri datoteke: `docs/rucni-testovi.http`, `S10ZadnjeMjestoTest.java` i `N01SesijaTest.java` (mapa `src/test/java/hr/span/akademija/medtermin/sigurnost/`).",
  "Otvorite kartice preglednika iz tablice ispod i povećajte prikaz na 125–150 % (projektor).",
], true));
s(tablica(["#", "Kartica", "Adresa"], [
  ["1", "Actions", `[${R}/actions](${R}/actions)`],
  ["2", "Pull requests (otvoreni i zatvoreni)", `[${R}/pulls?q=is%3Apr](${R}/pulls?q=is%3Apr)`],
  ["3", "PR #11 – ovisnosti", `[${R}/pull/11](${R}/pull/11)`],
  ["4", "PR #14 – dokaz S10", `[${R}/pull/14](${R}/pull/14)`],
  ["5", "PR #12 – nalaz N-01", `[${R}/pull/12](${R}/pull/12)`],
  ["6", "docs/ (mapa)", `[${R}/tree/main/docs](${R}/tree/main/docs)`],
], [500, 3300, 5838]));
s(razmak());
s(okvir("info", [
  "Token prijave nakon popravka N-01 istječe nakon **30 minuta neaktivnosti**. Ako ste se prijavili u `rucni-testovi.http` prije pauze, prijavite se ponovno – odgovor `401` nakon pauze je ispravno ponašanje, ne greška (dobar trenutak da to i kažete).",
]));

// ------------------------------------------------------------------ 3. blok 1
s(H1("3. Blok 1 – Pipeline (slajdovi 5–7)"));
s(P("**Cilj:** polaznici vide cijeli put od predloška do zelenih vrata i – važnije – dokaz da vrata padaju kad se propust vrati. Šest koraka prati slajd 6. **Trajanje dema:** oko 12 minuta."));

s(H2("3.1 Korak 1 – Predložak u repozitoriju"));
s(koraci([
  "Kartica **Code → Commits** (ili `…/commits/main`), skrolajte na najstariji commit „T2 projekt MedTermin (Java) + DevSecOps predložak iz T3 paketa”.",
  "Otvorite ga i pokažite što je predložak donio: `.github/workflows/devsecops.yml`, `.github/dependabot.yml`, mapu `ci/`, `.semgrepignore`, `.gitleaks.toml`, `osv-scanner.toml`.",
]));
s(okvir("recite", [
  "„Polaznik kopira **sadržaj** mape `java/` (ili `python/`, `dotnet/`) iz paketa u korijen svog T2 repozitorija – uključujući skrivene `.github` i `.semgrepignore`. Ništa se ne instalira lokalno: sve alate pokreće GitHub.”",
]));

s(H2("3.2 Korak 2 – Prvo pokretanje"));
s(koraci([
  `Otvorite ${RUN(44382947605, "prvo pokretanje")} (Actions → *devsecops* → najstarije pokretanje na \`main\`).`,
  "Pokažite graf poslova: Tajne, Build, SAST, SCA, DAST → **Sigurnosna vrata**. Sve je zeleno.",
  "Skrolajte na **Summary** i tablicu „Sigurnosna vrata”, zatim na odjeljak „Prihvaćeni nalazi”.",
]));
s(tablica(["kategorija", "blokira", "prihvaćeno", "informativno"], [
  ["SAST", "0", "4", "61"], ["SCA", "0", "**30**", "29"], ["DAST", "0", "0", "14"],
], [2600, 2346, 2346, 2346]));
s(razmak(60));
s(okvir("ocekivano", [
  "Vrata su zelena, ali **30 visokih SCA nalaza** prihvaćeno je općim iznimkama iz README-a paketa: `osv | * | org.apache.tomcat.embed:* | |` i slično za Spring i Jackson.",
]));
s(okvir("recite", [
  "„Zeleno nije isto što i sigurno. Iznimka sa zvjezdicom prihvaća **svaku** buduću ranjivost u Tomcatu – i onu koja izađe sutra. Takve iznimke su u README-u paketa samo da biste brzo došli do prvog zelenog pokretanja; sljedeći korak ih uklanja.”",
]));

s(H2("3.3 Korak 3 – Ovisnosti: nadogradnja umjesto iznimki (PR #11)"));
s(koraci([
  `Otvorite ${PR(11)} → kartica **Commits**: dva commita.`,
  `Prvi commit: Spring Boot 3.5.7 → 3.5.16 i **uklonjene opće iznimke**. Kartica **Checks** (ili ${RUN(44384161534, "crveno pokretanje")}) → Summary: **13 blokirajućih** nalaza (Tomcat, Spring Framework, Jackson).`,
  `Drugi commit: \`tomcat.version\` 10.1.61 u \`pom.xml\` i **7 privremenih iznimki** u \`osv-scanner.toml\` → ${RUN(44385250360, "zeleno pokretanje")}.`,
  "Kartica **Files changed** → `osv-scanner.toml`: pokažite jedan unos (ispod).",
]));
s(kod(`[[IgnoredVulns]]
id = "GHSA-pc63-qcmh-9cmg"
ignoreUntil = 2027-01-31
reason = "spring-webmvc 6.2.19: XsltView aplikacija ne koristi (nema XSLT prikaza). R-02, migracija na Boot 4.1."`, "osv-scanner.toml – jedan od 7 unosa"));
s(okvir("recite", [
  "„Redoslijed je uvijek isti: **nadogradi** → ako zakrpe nema, **procijeni** koristi li aplikacija ranjivu funkciju → tek onda **iznimka s razlogom i rokom**. Ovdje: 30 → 13 nadogradnjom unutar 3.5, → 7 podizanjem Tomcata, a za tih 7 zakrpe unutar 3.5 nema.”",
  "„Spring Boot 3.5 nema OSS podrške od 30. 6. 2026. – 3.5.16 je zadnje izdanje. To više nije problem jedne biblioteke nego **rizik** s vlasnikom i rokom (R-02 u bloku 4). Kad rok istekne, vrata ponovno padaju i netko mora odlučiti.”",
]));

s(H2("3.4 Korak 3 – Dependabot"));
s(koraci([
  "Kartica **Pull requests**: Dependabot je odmah nakon prvog pusha otvorio 10 PR-ova (ovisnosti i GitHub akcije). Osam prolazi, **dva ne prolaze**.",
  `${PR(4)} – Spring Boot 4.1: **Checks → Build** pada s \`package com.fasterxml.jackson.core does not exist\`. Spring Boot 4 donosi Jackson 3 s novim paketima (\`tools.jackson\`) – testovi se ne prevode. U PR-u je komentar s objašnjenjem.`,
  `${PR(8)} – SpotBugs plugin 4.10: Build prolazi, ali vrata blokiraju novi nalaz \`HRS_REQUEST_PARAMETER_TO_HTTP_HEADER\` u \`CorsFilter.java:45\` (vrijednost zaglavlja \`Origin\` zapisuje se u odgovor).`,
]));
s(okvir("recite", [
  "„Dependabot PR nije automatski siguran – vrata ga provjeravaju kao i svaki drugi kod. **Velika verzija** (Boot 4) je migracija, ne klik na *Merge*. **Nova verzija alata** (SpotBugs) znači nove nalaze: ovdje je `Origin` već provjeren prema popisu dopuštenih, pa je to lažno pozitivan nalaz – rješava se uskom iznimkom s odsječkom, ne isključivanjem pravila.”",
]));
s(okvir("info", [
  "Provjera **Pregled ovisnosti u PR-u** u svakom PR-u je crvena: dependency review u privatnom repozitoriju traži GitHub Advanced Security. Posao ima `continue-on-error` i ne utječe na vrata. Recite to prije nego što netko pita.",
]));

s(H2("3.5 Korak 4 – Tajne i iznimke"));
s(P("Otvorite `ci/prihvaceno.txt` (Code → `ci/prihvaceno.txt`). Format retka: `alat | pravilo | datoteka | odsječak | obrazloženje`."));
s(kod(`semgrep  | tainted-sql-string  | LijecnikController.java | stupac + " " + redoslijed | stupac i smjer dolaze iz mape dopuštenih vrijednosti (S08 popravljen)
spotbugs | SQL_INJECTION_SPRING_JDBC | LijecnikController.java | STUPCI.get(sort) | …
spotbugs | XXE_DOCUMENT        | UvozTermina.java | | tvornica() postavlja disallow-doctype-decl; regresiju hvata ci/semgrep/regresije.yml`, "ci/prihvaceno.txt (skraćeno)"));
s(okvir("recite", [
  "„Iznimka s **odsječkom** vrijedi samo za taj redak koda – ako netko sutra u istoj datoteci napiše novi SQL spajanjem stringova, vrata ga uhvate. Iznimka bez odsječka (XXE) je šira, pa je čuva **vlastito Semgrep pravilo** u `ci/semgrep/regresije.yml`.”",
  "„Tajne: gitleaks prolazi cijelu povijest. Lozinka za DAST je u GitHub secretu `DAST_LOZINKA`; u demu se koristi seed lozinka korisnika `ana`.”",
]));

s(H2("3.6 Korak 5 – DAST s prijavom"));
s(P("Otvorite `ci/dast-putanje.txt`: popis GET putanja koje ZAP posjećuje s tokenom korisnika `ana` (`/api/termini`, `/api/rezervacije/moje`, `/api/nalazi/1?format=pdf`, `/ispis/rezervacije/1`…)."));
s(okvir("recite", [
  "„Bez prijave ZAP vidi samo početnu stranicu, `/prijava` i `/api/health`. API nema poveznica koje bi pauk slijedio, pa putanje upisujete sami – **samo GET**, da skener ništa ne obriše.”",
]));

s(H2("3.7 Korak 6 – Dokaz pada (PR #13 i #14)"));
s(H3("PR #13 – vraćen S06 (ranjiva YAML biblioteka)"));
s(koraci([
  `Otvorite ${PR(13)} → **Checks** → *devsecops* → **Summary**.`,
  "Tablica vrata: SAST **1** blokira, SCA **1** blokira. Ispod, „Blokirajući nalazi”: Semgrep pravilo `java-snakeyaml-bez-safeconstructor` u `PostavkeController.java:50` i OSV `GHSA-mjmj-j48q-9wg2` (CVE-2022-1471, CVSS 8,3) u `org.yaml:snakeyaml@1.33`.",
  "Ovdje smijete otvoriti *Files changed* – vidi se samo `snakeyaml.version` 1.33 i `new Yaml()`.",
]));
s(H3("PR #14 – vraćen S10 (utrka za zadnje mjesto)"));
s(koraci([
  `Otvorite ${PR(14)} → **Checks** → *devsecops*. Poslovi Tajne, SAST, SCA i DAST su **zeleni**; crveni su samo **Build, testovi, pokrivenost** i zato Sigurnosna vrata.`,
  "Summary: tablica vrata ima **0** blokirajućih nalaza alata – pada samo test.",
  "Otvorite posao **Build** → log, potražite (Ctrl + F u logu) `S10ZadnjeMjestoTest`.",
]));
s(kod(`[ERROR] hr.span.akademija.medtermin.sigurnost.S10ZadnjeMjestoTest.samoJedanDobivaZadnjeMjesto <<< FAILURE!
[kodovi odgovora: [201, 201, 201, 201, 201, 201, 201, 201, 201, 201]]`, "Log posla Build – PR #14"));
s(okvir("pazite", ["U PR-u #14 **ne otvarajte Files changed** – diff je rješenje S10 iz T2."]));
s(okvir("recite", [
  "„Deset istodobnih zahtjeva za termin s **jednim** mjestom – i svih deset je dobilo potvrdu. Semgrep, SpotBugs, OSV-Scanner i ZAP ne vide ništa, jer je svaki pojedinačni zahtjev ispravan. Vrata je zaustavio **jedan sigurnosni test**. To je most prema bloku 2.”",
  "„U predaju ide poveznica na ovakvo crveno pokretanje (`repozitorij.txt`). PR se ne spaja.”",
]));

s(H2("3.8 Pitanja za polaznike"));
s(tablica(["Pitanje", "Očekivani odgovor"], [
  ["Zašto su opće iznimke iz prvog pokretanja opasne?", "Prihvaćaju i svaku buduću ranjivost u tom paketu – nova kritična ranjivost u Tomcatu ne bi zaustavila vrata."],
  ["Što se dogodi kad iznimci istekne rok?", "Vrata ponovno padaju; odluku treba obnoviti (s novim obrazloženjem) ili provesti nadogradnju/migraciju."],
  ["Zašto Dependabot PR nije automatski siguran?", "Može razbiti kod (Boot 4), donijeti nova pravila alata (SpotBugs) ili kompromitirano izdanje; vrata ga provjeravaju kao svaki drugi kod."],
  ["Zašto PR #14 pada iako svi alati prolaze?", "Utrka se vidi samo pri istodobnim zahtjevima; hvata je samo test s barijerom na stvarnom poslužitelju."],
], [3800, 5838]));

// ------------------------------------------------------------------ 4. blok 2
s(H1("4. Blok 2 – Ispitivanje (slajdovi 8–13)"));
s(P("**Cilj:** postupak ispitivanja na jednom primjeru – plan, ono što alati ne vide, ručni test uživo, stvarni nalaz s cijelim zapisom i popravkom (crveno → zeleno) te otvoreni nalaz. **Trajanje dema:** oko 15 minuta."));

s(H2("4.1 Plan ispitivanja (slajd 9)"));
s(P(`Otvorite ${DOC("docs/plan-ispitivanja.md")} i prođite odjeljke redom:`));
s(B("**Opseg** – što je u opsegu i što nije (TLS, SQL Server, DoS); pravni okvir: samo vlastita instanca."));
s(B("**Uloge** – naglasite **dva korisnika iste uloge** (`ana`, `marko`): bez njih se kontrola pristupa ne može ispitati."));
s(B("**Alati** – tablica „alat → što pokriva → gdje je rezultat” (artefakti pokretanja)."));
s(B("**Ručni testovi RT-01 – RT-07** – svaki ima WSTG v4.2 oznaku, očekivani rezultat i **automatski test**; stupac „Rezultat” pokazuje dva nalaza (RT-06 → N-01, RT-07 → N-02)."));
s(B("**Kriterij prolaza** – zelena vrata, svi testovi, dokaz pada, svaki nalaz zapisan."));
s(okvir("recite", ["„Plan stane na jednu stranicu. Svaki ručni test dobiva i automatski test – inače će se propust vratiti, a nitko neće primijetiti.”"]));

s(H2("4.2 Što alati ne vide (slajd 10)"));
s(P("U IntelliJ-u otvorite mapu `src/test/java/hr/span/akademija/medtermin/sigurnost/`."));
s(tablica(["Test", "Propust", "WSTG v4.2 · ASVS 5.0.0"], [
  ["`S01TudaRezervacijaTest`", "S01 – brisanje tuđe rezervacije (IDOR)", "ATHZ-04 · 8.2.2"],
  ["`S09IspisXssTest`", "S09 – pohranjeni XSS na potvrdi za ispis", "INPV-02 · 1.2.1, 3.4.3"],
  ["`S10ZadnjeMjestoTest`", "S10 – utrka za zadnje mjesto", "BUSL-05 · 2.3.4"],
  ["`S12LogiranjeTest`", "S12 – lozinka i OIB u logu, zapis neuspjele prijave", "– · 16.2.5, 16.3.1"],
  ["`S13FailOpenTest`", "S13 – nepoznat format na tuđem nalazu", "ERRH-01 · 16.5.3"],
  ["`S02…`, `S03…`, `S04…`", "path traversal, open redirect, CORS – dokaz da se loš ulaz odbija", "ATHZ-01, CLNT-07 · 5.3.2, 1.2.2, 3.4.2"],
  ["`N01SesijaTest`", "N-01 – istek i prekid sesije (nalaz s ovog dana)", "SESS-06/07 · 7.4.1, 7.3.x"],
], [2700, 4300, 2638]));
s(razmak(60));
s(P("Otvorite `S10ZadnjeMjestoTest` i pokažite četiri stvari (Java verzija pytest isječka sa slajda 11):"));
s(koraci([
  "`extends SigurnosniTestBaza` → `ApiTestBaza` pokreće **stvarni poslužitelj** na nasumičnom portu (`RANDOM_PORT`) – MockMvc ovdje ne pomaže.",
  "Deset novih korisnika i termin s **jednim** mjestom (stvoren uvozom XML-a, neovisan o seed podacima).",
  "`CyclicBarrier` – svi zahtjevi kreću **istodobno**.",
  "Provjera: **točno jedan** 201, ostali 409, i 0 slobodnih mjesta nakon utrke.",
]));
s(okvir("info", ["Po želji test pokrenite u IntelliJ-u (desni klik → Run; s pokretanjem Springa traje desetak sekundi). Isti test u PR-u #14 bio je crven."]));

s(H2("4.3 Ručni testovi uživo (slajd 11)"));
s(P("U IntelliJ-u otvorite `docs/rucni-testovi.http` (aplikacija mora raditi, poglavlje 2.2). Pokrećete zahtjeve zelenom strelicom lijevo od `###`."));
s(koraci([
  "Pokrenite **Prijava – ana**, **Prijava – marko** i **Prijava – dr.horvat**. Iz svakog odgovora (`{\"token\": \"…\", \"username\": …, \"uloga\": …}`) kopirajte token u varijable `@ana`, `@marko`, `@lijecnik` na vrhu datoteke.",
]));
s(tablica(["Zahtjev", "Očekivani odgovor", "Što reći"], [
  ["RT-01 · `DELETE /api/rezervacije/2` kao **ana** (rezervacija 2 je markova)", "**404** `{\"greska\":\"Rezervacija nije pronađena.\"}`", "Tuđi zapis vraća 404, ne 403 – ne otkrivamo da postoji."],
  ["RT-01 · `GET /api/rezervacije/moje` kao **marko**", "200, rezervacija **id 2** je i dalje tu", "Provjera da brisanje stvarno nije uspjelo."],
  ["RT-05 · `GET /api/nalazi/1?format=xml` kao **marko** (nalaz 1 je anin)", "**404** `Nalaz nije pronađen.`", "Vlasništvo se provjerava **prije** formata – nema fail-opena."],
  ["isti zahtjev kao **ana** (promijenite token u `{{ana}}`)", "**400** `Nepodržan format. Dopušteno: json, pdf.`", "Vlasnica dobiva poruku o formatu; tuđinac ne saznaje ništa."],
  ["RT-02 · `POST /api/rezervacije` s `<script>` u napomeni, zatim `GET /ispis/rezervacije/3`", "201; ispis sadrži `&lt;script&gt;`; zaglavlje `Content-Security-Policy: default-src 'none'; …`", "Kodiranje izlaza + CSP (pokažite zaglavlja odgovora u IntelliJ-u)."],
  ["RT-04 · prijava `marko` s pogrešnom lozinkom", "**401**; u konzoli aplikacije redak `WARN … Neuspjela prijava za korisnika marko`", "Neuspjela prijava se zapisuje – bez lozinke."],
], [3500, 3100, 3038], { zajedno: false }));
s(razmak(60));
s(okvir("pazite", [
  "Id u RT-02 (`/ispis/rezervacije/3`) vrijedi ako je to prva nova rezervacija od pokretanja aplikacije – inače uzmite `id` iz odgovora na POST.",
  "RT-03 (utrka) se ručno ne može pouzdano pokazati – recite to i vratite se na test S10.",
]));

s(H2("4.4 Nalaz N-01: od ručnog testa do popravka (slajdovi 12–13)"));
s(H3("Uživo: RT-06"));
s(koraci([
  "Pokrenite **RT-06 · odjava** (`POST /api/auth/odjava` s tokenom `ana`) → **204**.",
  "Pokrenite **RT-06 · isti token nakon odjave** (`GET /api/ja`) → **401**.",
]));
s(okvir("recite", [
  "„Kad smo ovo prvi put ispitivali, odjava je vraćala **404 – nije postojala**, a isti token je i dalje vrijedio. Token nije istjecao ni nakon promjene lozinke. Nijedan alat to nije prijavio – našli smo ga ručnim testom WSTG-SESS-06/07.”",
]));
s(okvir("pazite", ["Nakon RT-06 token korisnice `ana` više ne vrijedi – za daljnje zahtjeve ponovno pokrenite **Prijava – ana**."]));
s(H3("Zapis nalaza"));
s(P(`Otvorite ${DOC("docs/nalazi/N-01-sesija-bez-isteka.md")} i pokažite četiri dijela sa slajda 13:`));
s(tablica(["Dio zapisa", "U dokumentu"], [
  ["1. Što i gdje", "`TokenStore`, `AuthController`, `ResetLozinkeService`; CWE-613; WSTG-SESS-06/07; ASVS 7.4.1 (L1), 7.3.1, 7.3.2, 7.4.3 (L2)"],
  ["Ozbiljnost", "CVSS 4.0 `AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:L/VA:N/…` → **8,3 (visoka)**; obrazloženje svake metrike (AT:P – napadač prvo mora doći do tokena)"],
  ["2. Dokaz", "pet koraka za ponavljanje, tokeni zamijenjeni oznakama `<T1>`"],
  ["3. Uzrok i popravak", "„token nema životni vijek”; popravak u PR-u #12 – prvo test, zatim kod"],
  ["4. Ponovno ispitivanje", "isti koraci nakon popravka: 401 i 204; status „popravljen”"],
], [2600, 7038]));
s(H3("Crveno → zeleno u PR-u #12"));
s(koraci([
  `Otvorite ${PR(12)} → **Commits**: prvi commit samo dodaje \`N01SesijaTest\`, drugi je popravak.`,
  `Prvi commit → ${RUN(44386607639, "crveno pokretanje")} → posao Build → log: sva **4** testa iz \`N01SesijaTest\` padaju (\`expected: 204\` kod odjave, \`expected: 401 but was: 200\` za istek i reset lozinke).`,
  `Drugi commit → ${RUN(44386994602, "zeleno pokretanje")}: 60 testova prolazi, pokrivenost 90,2 %.`,
  "U IntelliJ-u otvorite `N01SesijaTest`: kratka trajanja (`PT2S`, `PT5S`) i vlastita baza vrijede samo za taj test (`@TestPropertySource`).",
]));
s(okvir("recite", ["„To je dokaz koji tražimo u predaji: **test koji je bio crven, a sada je zelen**. Bez crvenog pokretanja ne znamo testira li test uopće propust.”"]));

s(H2("4.5 Nalaz N-02 – otvoren"));
s(koraci([
  "Pokrenite **RT-07** (prijava `marko` s pogrešnom lozinkom) nekoliko puta zaredom → uvijek **401**, bez odgode.",
  "Zatim ispravnu lozinku → **200**.",
  `Otvorite ${DOC("docs/nalazi/N-02-bez-zastite-od-pogadanja-lozinke.md")}: status „otvoren”, prijedlog popravka (5 pokušaja / 15 min → 429, bez trajnog zaključavanja) i poveznica na rizik **R-03**.`,
]));
s(okvir("recite", ["„Nije svaki nalaz popravljen do predaje – i to je u redu, ako je zapisan, procijenjen i ima vlasnika i rok u registru rizika. To je tema bloka 4.”"]));

s(H2("4.6 Pitanja za polaznike"));
s(tablica(["Pitanje", "Očekivani odgovor"], [
  ["Zašto trebamo dva korisnika iste uloge?", "IDOR/BOLA se vidi samo kad jedan korisnik pokuša pristupiti zapisu drugog s istim pravima."],
  ["Zašto marko dobiva 404, a ana 400 za isti zahtjev?", "Vlasništvo se provjerava prije formata; tuđinac ne smije saznati ni da nalaz postoji."],
  ["Zašto je za S10 potreban stvarni poslužitelj i barijera?", "Utrka nastaje samo kad zahtjevi stvarno idu paralelno kroz HTTP sloj i bazu; MockMvc i slijedni pozivi je ne pokazuju."],
  ["Što je AT:P u CVSS 4.0 vektoru za N-01?", "Preduvjet koji napadač ne kontrolira u potpunosti – mora prvo doći do tokena žrtve."],
], [3800, 5838]));

// ------------------------------------------------------------------ 5. blok 3
s(H1("5. Blok 3 – Model prijetnji (slajdovi 14–17)"));
s(P("**Cilj:** pokazati kako izgleda DFD koji je dovoljno dobar za STRIDE i kako se iz njega dolazi do tablice prijetnji u kojoj svaka prijetnja ima odgovor. **Trajanje dema:** oko 10 minuta."));
s(H2("5.1 DFD"));
s(P(`Otvorite ${DOC("docs/dfd.md")} (slika se prikazuje na GitHubu) ili \`docs/dfd.png\` u zasebnoj kartici.`));
const dfd = fs.readFileSync(path.join(__dirname, "dfd.png"));
s(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 80 },
  children: [new ImageRun({ type: "png", data: dfd, transformation: { width: 640, height: Math.round(640 * 1190 / 2712) },
    altText: { title: "DFD MedTermina", description: "Dijagram toka podataka MedTermina s granicama povjerenja TB1–TB3", name: "dfd" } })] }));
s(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 160 }, children: [new TextRun({ text: "DFD MedTermina (docs/dfd.png): 7 vanjskih entiteta, 2 procesa, 5 spremišta, 14 tokova, 3 granice povjerenja · slika je u punoj rezoluciji – povećajte prikaz", size: 17, color: SIVA, italics: true })] }));
s(P("Pokazujte redom, pokazivačem po slici:"));
s(koraci([
  "**Vrste elemenata:** pravokutnik = vanjski entitet (E1–E7), elipsa = proces (P1, P2), dvije crte = spremište (D1–D5).",
  "**Granice povjerenja** (crtkano): TB1 poslužitelj aplikacije, TB2 poslužitelj baze, TB3 CI/CD na GitHubu.",
  "**Tokovi koji prelaze granicu** (F1–F5, F9, F10, F12–F14) – tu su kontrole. Svaka strelica ima oznaku: **što** se prenosi i **kako**.",
  "**F14** – artefakt iz CI-ja ulazi u poslužitelj: kompromitiran pipeline znači kompromitiranu aplikaciju. Zato je CI/CD u istom modelu.",
  "**D3 log i D4 sesije** su spremišta, ne sporedne stvari: u logu su bili lozinka i OIB (S12), u sesijama nalaz N-01.",
]));
s(okvir("recite", ["„Prvo od četiri pitanja – *što gradimo?* – odgovara ovaj dijagram. Ne treba biti lijep, nego potpun: svaka strelica s oznakom i svaka granica nacrtana.”"]));

s(H2("5.2 STRIDE tablica"));
s(P(`Otvorite ${DOC("docs/stride.md")}. Objasnite stupce: **Element · STRIDE · Prijetnja · Postojeća kontrola (dokaz) · Rizik**. Zatim pokažite četiri retka:`));
s(tablica(["Redak", "Na što pokazati"], [
  ["E1 Pacijent · S · pogađanje lozinke", "kontrola je djelomična (bcrypt, WARN zapis), **nema ograničenja pokušaja** → R-03 (nalaz N-02)"],
  ["P1 API · T · utrka za zadnje mjesto (S10)", "kontrola s dokazom: atomski UPDATE + `S10ZadnjeMjestoTest`"],
  ["D1 Baza · I · OIB u čistom tekstu", "mjere s Dana 2 još nisu u produkciji → R-09 (veza s laboratorijem baze)"],
  ["P2 GitHub Actions · T · akcija po pomičnoj oznaci", "slučaj tj-actions (CVE-2025-30066); akcije nisu pribijene na SHA → R-05"],
], [3600, 6038]));
s(razmak(60));
s(P("Na dnu tablice: **29 prijetnji · 17 s kontrolom · 12 vodi na 8 otvorenih rizika**."));
s(okvir("recite", ["„Pravilo: svaka prijetnja ima ili **kontrolu s dokazom** – test, pravilo alata, izvještaj – ili **ID rizika**. Rečenica ‚imamo validaciju‘ bez dokaza nije kontrola.”"]));
s(H2("5.3 Pitanja za polaznike"));
s(tablica(["Pitanje", "Očekivani odgovor"], [
  ["Koja STRIDE pitanja postavljamo za spremište?", "T, I, D – za log i R (poricanje)."],
  ["Zašto je registar paketa (E7) u modelu aplikacije?", "Ovisnosti ulaze u artefakt (F13 → F14); slopsquatting i kompromitirana izdanja su prijetnja aplikaciji."],
  ["Što napraviti s prijetnjom bez kontrole?", "Upisati je u registar rizika s vlasnikom i rokom."],
], [3800, 5838]));

// ------------------------------------------------------------------ 6. blok 4
s(H1("6. Blok 4 – Analiza rizika (slajdovi 18–21)"));
s(P(`**Cilj:** registar u kojem je svaki rizik procijenjen na istim ljestvicama i ima postupanje, mjeru s dokazom, preostali rizik, vlasnika i rok. **Trajanje dema:** oko 8 minuta. Otvorite ${DOC("docs/registar-rizika.md")}.`));
s(koraci([
  "**Ljestvice** na vrhu – iste kao na slajdu 20 (V i U 1–3, R = V × U; 6–9 visok). Recite zašto je za MedTermin utjecaj kod nalaza i rezervacija uvijek **3** (posebna kategorija podataka, GDPR čl. 9).",
  "**Tablica** – poredana po riziku. Pokažite stupce *Postupanje*, *R nakon*, *Vlasnik · rok*.",
  "**Sva četiri postupanja** na primjerima (tablica ispod).",
  "**R-01 je zatvoren** – rizik iz nalaza N-01: 6 → 3 nakon popravka (PR #12).",
  "**R-02 povezuje blok 1 i 4** – platforma izvan podrške, iznimke s rokom 31. 1. 2027. i migracija (PR #4) koja ne prolazi vrata.",
]));
s(tablica(["Postupanje", "Rizik", "Zašto baš to"], [
  ["izbjeći", "R-04 seed račun `admin` s poznatom lozinkom u produkciji", "uzrok se uklanja – seed samo u profilu `dev`; blokira isporuku"],
  ["smanjiti", "R-03 pogađanje lozinke (N-02)", "ograničenje pokušaja: 9 → 3, rok 15. 12. 2026."],
  ["prenijeti", "R-08 TLS, HSTS, certifikat", "postavlja pružatelj smještaja – ugovorom; u aplikaciji ostaje kolačić `Secure`"],
  ["prihvatiti", "R-07 uskraćivanje usluge", "utjecaj 1 (kratki prekid); prihvaća vlasnik uz praćenje i ponovnu procjenu 1. 3. 2027."],
], [1500, 3800, 4338]));
s(razmak(60));
s(okvir("recite", [
  "„Vjerojatnost nakon mjere pada, **utjecaj ostaje** – zdravstveni podaci ne postaju manje vrijedni.”",
  "„Preostali rizik **prihvaća vlasnik rizika**, ne programer. Programer predlaže mjeru i daje dokaz.”",
]));
s(H2("6.1 Pitanja za polaznike"));
s(tablica(["Pitanje", "Očekivani odgovor"], [
  ["Zašto R-04 ima postupanje „izbjeći”, a ne „smanjiti”?", "Seed računi u produkciji ne smiju postojati; uzrok se uklanja (profil `dev`), ne ublažava."],
  ["Zašto R-01 nakon popravka nije 0?", "Utjecaj ostaje 3; vjerojatnost pada na 1 (token vrijedi najviše 30 min neaktivnosti / 8 h)."],
  ["Tko potpisuje prihvaćanje rizika R-07?", "Vlasnik rizika (voditelj IT-a poliklinike), s datumom ponovne procjene."],
], [3800, 5838]));

// ------------------------------------------------------------------ 7. blok 5
s(H1("7. Blok 5 – Usklađenost (slajdovi 22–26)"));
s(P("**Cilj:** razlika između liste i dokaza – svaki zahtjev ima status i provjerljiv dokaz, a svaki nedostatak vodi na rizik ili otvorenu stavku. **Trajanje dema:** oko 10 minuta."));
s(H2("7.1 ASVS lista"));
s(P(`Otvorite ${DOC("docs/asvs.md")}. Na vrhu je sažetak: **L1 – 32 ✅ · 13 ⚠️ · 7 ❌ · 18 ➖** (svih 70 zahtjeva), **L2 – 13 odabranih**. Zatim pokažite po jedan redak svake vrste:`));
s(tablica(["Status", "Redak", "Što pokazuje"], [
  ["✅", "v5.0.0-8.2.2 pristup zapisima (IDOR)", "dokaz je **test** – `S01TudaRezervacijaTest`"],
  ["❌", "v5.0.0-6.3.1 zaštita od pogađanja lozinke", "vodi na nalaz N-02 i rizik R-03 s rokom"],
  ["⚠️", "v5.0.0-3.4.1 HSTS", "ovisi o okolini (reverse proxy) → R-08"],
  ["➖", "v5.0.0-9.1.1 potpis JWT-a", "ne odnosi se – **s razlogom**: aplikacija koristi referentne tokene"],
], [900, 3800, 4938]));
s(razmak(60));
s(okvir("recite", [
  "„Ljestvica dokaza, od najjačeg: **test** (crven pa zelen) → **izvještaj alata** s datumom i commitom → **konfiguracija ili kod** → **stanje baze** (izlaz provjere s Dana 2). Riječ ‚implementirano‘ nije dokaz.”",
  "„ID se piše s verzijom – v5.0.0-8.2.2 – jer se brojevi mijenjaju između verzija ASVS-a.”",
]));
s(H2("7.2 Sigurnosna pravila"));
s(P(`Otvorite ${DOC("docs/sigurnosna-pravila.md")}: više ASVS zahtjeva traži da je pravilo **zapisano** – pristup (8.1.1), provjera ulaza (2.1.1), sesija (7.1.1), rokovi za zakrpe (15.1.1), što se logira (16.1.1). Pokažite tablicu pristupa (tko smije što) i tablicu rokova za zakrpe (kritično 7 dana, visoko 30).`));
s(H2("7.3 Analiza usklađenosti"));
s(P(`Otvorite ${DOC("docs/uskladenost.md")} – četiri pitanja vodilje sa slajda 26:`));
s(koraci([
  "**Koje podatke obrađujemo?** – tablica po spremištima iz DFD-a; napomena rezervacije i nalazi su **posebna kategorija** (čl. 9) → procjena učinka (čl. 35).",
  "**Tko je odgovoran?** – voditelj obrade (poliklinika), izvršitelj (tim koji održava aplikaciju – ugovor iz čl. 28), vlasnik rizika, kanal za prijavu ranjivosti.",
  "**Kako dokazujemo kontrole?** – poveznice na ASVS listu, vrata, testove, model prijetnji i izlaz provjere baze.",
  "**Što kad pođe po zlu?** – tablica rokova: GDPR 72 h (AZOP), NIS2/ZKS 24 h / 72 h / 1 mjesec ako je poliklinika u opsegu, CRA 24 h / 72 h / 14 dana samo ako se MedTermin prodaje kao proizvod.",
]));
s(okvir("pazite", ["Dokument izričito nije pravna procjena – opseg NIS2 i CRA ovisi o činjenicama koje tim ne zna. Na kraju je pet **pitanja za naručitelja**; to je ono što polaznici trebaju naučiti postaviti."]));
s(H2("7.4 SECURITY.md"));
s(P(`Otvorite ${DOC("SECURITY.md")}: kako prijaviti ranjivost, rokovi odgovora i podržane verzije. Recite da kanal za prijavu ranjivosti traže i CRA i dobra praksa – GitHub ga prikazuje na kartici **Security**.`));
s(H2("7.5 Pitanja za polaznike"));
s(tablica(["Pitanje", "Očekivani odgovor"], [
  ["Što je valjan dokaz za ASVS 2.3.4 (ograničeni resurs)?", "Test istodobnosti (S10) koji je crven na ranjivom kodu i zelen nakon popravka."],
  ["Kada je zahtjev „ne odnosi se”?", "Kad aplikacija nema tu funkciju – uz razlog (npr. nema JWT-a, nema OAuth poslužitelja)."],
  ["Kome i u kojem roku prijaviti procurjele nalaze?", "AZOP-u, gdje je izvedivo u 72 sata (GDPR čl. 33); pacijentima bez odgađanja ako je rizik visok (čl. 34)."],
], [3800, 5838]));

// ------------------------------------------------------------------ 8. završetak
s(H1("8. Završetak: od dema do predaje polaznika"));
s(P("Na kraju radionice (ili na početku samostalnog rada) pokažite kako se demo preslikava na predaju u nedjelju:"));
s(tablica(["Predaja (ZIP `Vxx-Ime-Prezime-T3.zip`)", "U demu"], [
  ["`repozitorij.txt` – adresa repozitorija i poveznica na crveno pokretanje", "ovaj repozitorij; crveno pokretanje u PR-u #13 ili #14"],
  ["`usklađenost/` – ASVS lista s dokazima", "`docs/asvs.md` (+ `sigurnosna-pravila.md`)"],
  ["`usklađenost/` – analiza GDPR / NIS2", "`docs/uskladenost.md`"],
  ["`usklađenost/` – DFD sa STRIDE tablicom", "`docs/dfd.png`, `docs/stride.md`"],
  ["`usklađenost/` – registar od barem 5 rizika", "`docs/registar-rizika.md` (9 rizika)"],
  ["`baza/` – skripta i izlaz provjere (Dan 2)", "nije dio ovog dema – vodič za bazu podataka (R-09)"],
], [4600, 5038]));
s(razmak(80));
s(okvir("recite", ["„Ne kopirajte strukturu dokumenata, nego način: svaka tvrdnja ima dokaz, svaki nedostatak ima rizik s vlasnikom i rokom, a svaki ručni test postaje automatski.”"]));

// ------------------------------------------------------------------ 9. problemi
s(H1("9. Ako nešto pođe po zlu"));
s(tablica(["Problem", "Uzrok", "Što napraviti"], [
  ["`Web server failed to start. Port 8080 was already in use.`", "drugi proces (npr. Camunda u Dockeru)", "zaustavite ga (2.2) ili pokrenite na drugom portu: `.\\mvnw.cmd spring-boot:run \"-Dspring-boot.run.arguments=--server.port=8081\"` i promijenite `@host` u `.http` datoteci"],
  ["`Get-Item : Could not find item …\\.m2`", "skrivena mapa `.m2`, Maven Wrapper 3.3.x", "`attrib -h \"$env:USERPROFILE\\.m2\"`"],
  ["Ručni zahtjev vraća 401, a prije je radio", "token je istekao (30 min neaktivnosti) ili ste pokrenuli RT-06 (odjava)", "ponovno pokrenite prijavu i zalijepite novi token"],
  ["RT-02: ispis vraća 404", "id rezervacije nije 3", "uzmite `id` iz odgovora na POST"],
  ["U pokretanju pada Build s `HTTP Status: 429` (Maven Central)", "previše istodobnih poslova (npr. Dependabot)", "u pokretanju **Re-run failed jobs** – nema veze s kodom"],
  ["Vrata na `main` crvena nakon 31. 1. 2027.", "istekle privremene iznimke u `osv-scanner.toml` (namjerno, R-02)", "za nastavu: pokažite to kao primjer isteka roka; trajno: migracija na Spring Boot 4 ili nova odluka s novim rokom"],
  ["Novi Dependabot PR-ovi", "Dependabot tjedno provjerava ovisnosti", "nakon nastave zatvorite ih ili spojite one koji prolaze vrata"],
  ["„Pregled ovisnosti u PR-u” crven", "dependency review u privatnom repozitoriju traži GitHub Advanced Security", "ne utječe na vrata (`continue-on-error`)"],
  ["Demo treba stvoriti iznova (drugi račun, nova generacija)", "–", "`tjedan-3/dan3-demo/pripremi-dan3.sh` u privatnom repozitoriju tečaja (README u toj mapi)"],
], [3000, 2800, 3838], { zajedno: false }));

// ------------------------------------------------------------------ dodaci
s(H1("Dodatak A – Sve poveznice"));
s(tablica(["Što", "Poveznica"], [
  ["Repozitorij", `[${R}](${R})`],
  ["Actions", `[${R}/actions](${R}/actions)`],
  ["Prvo pokretanje (opće iznimke, 30 prihvaćenih)", RUN(44382947605, "actions/runs/44382947605")],
  ["PR #11 – crveno (13 blokirajućih)", RUN(44384161534, "actions/runs/44384161534")],
  ["PR #11 – zeleno (Tomcat 10.1.61 + iznimke s rokom)", RUN(44385250360, "actions/runs/44385250360")],
  ["PR #12 – crveno (samo test N-01)", RUN(44386607639, "actions/runs/44386607639")],
  ["PR #12 – zeleno (popravak N-01)", RUN(44386994602, "actions/runs/44386994602")],
  ["PR #13 – dokaz S06", PR(13)],
  ["PR #14 – dokaz S10", PR(14)],
  ["PR #4 – Dependabot Spring Boot 4.1", PR(4)],
  ["PR #8 – Dependabot SpotBugs 4.10", PR(8)],
  ["Vodič po blokovima (kratki)", DOC("docs/README.md")],
], [4300, 5338]));

s(H1("Dodatak B – Brojke na jednom mjestu", false));
s(tablica(["Što", "Vrijednost"], [
  ["SCA nalazi skriveni općim iznimkama → nakon 3.5.16 → nakon Tomcata 10.1.61", "30 → 13 → 7 (7 privremenih iznimki do 31. 1. 2027.)"],
  ["Dependabot PR-ovi nakon prvog pusha", "10 (ne prolaze 2: #4 Spring Boot 4.1, #8 SpotBugs 4.10)"],
  ["Testovi na `main` / pokrivenost", "60 / 90,2 %"],
  ["PR #14 (S10)", "10 od 10 istodobnih zahtjeva dobilo 201"],
  ["PR #12 crveno", "4 od 4 testa `N01SesijaTest` pada"],
  ["N-01 / N-02 – CVSS 4.0", "8,3 / 8,3 (visoka)"],
  ["DFD", "7 vanjskih entiteta · 2 procesa · 5 spremišta · 14 tokova · 3 granice"],
  ["STRIDE", "29 prijetnji · 17 s kontrolom · 12 → 8 otvorenih rizika"],
  ["Registar rizika", "9 rizika (R-03 i R-04 = 9; R-01 zatvoren 6 → 3)"],
  ["ASVS 5.0.0 L1", "70: 32 ✅ · 13 ⚠️ · 7 ❌ · 18 ➖; L2: 13 odabranih"],
  ["Sesija nakon N-01", "30 min neaktivnosti · najdulje 8 h · odjava · opoziv nakon reseta lozinke"],
], [4800, 4838]));

// ------------------------------------------------------------------ dokument
const doc = new Document({
  creator: "Secure Coding akademija",
  title: "Demo za Dan 3 – upute za predavača",
  description: "Kako pokazati demo t3-dan3-medtermin-demo po blokovima P3 – samo za predavača",
  styles: stilovi(),
  numbering: numeracija(),
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134, header: 567, footer: 567 } } },
    headers: { default: zaglavlje("Dan 3 · demo t3-dan3-medtermin-demo · upute za predavača") },
    footers: { default: podnozje() },
    children: D,
  }],
});
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(IZLAZ, buf); console.log("spremljeno:", IZLAZ, buf.length); });
