"""Bilješke govornika – T3 P1: Sigurnost i zaštita programske potpore i DevSecOps (Dan 1)."""

BILJESKE = {
1: """
DAN 1 · početak u 16:30 · okvirni tijek (prilagodite trajanju termina)
• Obrane projekata iz 2. tjedna – oko 40 min: svaki polaznik 5 minuta pokazuje JEDAN svoj popravak (ranjivost, uzrok, popravak u kodu, sigurnosni test crveno → zeleno). Redom V01 → V12. Bilježite tko je što pokazao i koliko je pomoći trebao – to je dokaz samostalnosti za rubriku u 4. tjednu.
• Kratka stanka (5 min), zatim ovo predavanje – oko 2 sata s dvije demonstracije i stankom od 10–15 minuta nakon poglavlja 5.

PRIJE POČETKA (15 min prije dolaska polaznika)
• Keycloak i barem jedan primjer okvira pokrenuti – demonstracija A (okviri/README.md, odjeljak „Demonstracija”); jednom proći python demo/demo_okviri.py <tehnologija>.
• Demo repozitorij za DevSecOps sa zelenim pokretanjem i pripremljenom granom demo/regresija – demonstracija B (devsecops/README.md, odjeljak 6; za predavača DEMO-PREDAVAC.md).
• Projektor: zoom u IDE-u ~125 %, tamna tema; terminal s većim fontom.

UVODNA REČENICA
„U drugom tjednu ste ranjivosti krpali ručno, jednu po jednu. Danas gledamo kako isto rade okvir i proces – sustavno, na jednom mjestu i s automatskom provjerom koja pada čim netko vrati staru grešku.”
""",
2: """
⏱ ~3 min

TREĆI TJEDAN U CJELINI – recite raspored naglas, polaznici su ga tek dobili:
• Dan 1 (danas): obrane T2 i ovo predavanje – mehanizmi okvira i DevSecOps.
• Dan 2: sigurnost baza podataka (SQL Server) i početak laboratorija u vlastitom Dockeru.
• Dan 3: radionica „ispitivanje sigurnosti, rizik i usklađenost” – rad na vlastitom repozitoriju: pipeline koji prolazi, model prijetnji za aplikaciju, bazu i CI/CD, registar rizika i ASVS lista s dokazima. Poglavlje 7 danas je samo uvod u to.
• Dani 4–5: samostalno dovršavanje; predaja u nedjelju, 22. 11. 2026. u 23:59 (zadaća „Nadogradnja projekta – Tjedan 3”).
• Tjedan 4: rad na projektu uz nastavnika, predaja završnog rada u četvrtak i završna provjera u petak, 27. 11.

PREGLED DANAŠNJEG PREDAVANJA (7 poglavlja)
Poglavlja 1–5 su obrane u samoj aplikaciji (okvir), poglavlje 6 je proces (pipeline), poglavlje 7 je zašto i koliko (rizik i propisi). Demonstracija A dolazi na kraju poglavlja 5, demonstracija B u poglavlju 6.

Ako termin traje kraće od planiranog, skratite poglavlje 7 – ono se detaljno radi na Danu 3.
""",
3: """
⏱ ~2 min

Ishodi slijede skup ishoda učenja „Sigurnost i zaštita programske potpore” iz programa mikrokvalifikacije – to je najveći skup (3 CSVET od 7), a u završnoj rubrici nosi elemente E5 (usklađenost), E6 (prijetnje, rizici i ranjivosti) i E7 (rješavanje).

Povežite svaki ishod s onim što polaznik predaje:
• Implementirati → barem dva mjesta s ručnom provjerom zamijenjena mehanizmom okvira (Spring Security, ASP.NET Core ili FastAPI), uz testove koji i dalje prolaze.
• Automatizirati → vlastiti DevSecOps pipeline na GitHubu koji je zelen na ispravljenom kodu i dokazano pada kad se ranjivost vrati.
• Analizirati → registar od barem 5 rizika (Dan 3).
• Ispitati → ASVS 5.0.0 lista sa stupcem dokaza i kratka analiza NIS2 / Zakona o kibernetičkoj sigurnosti i GDPR-a.

Poruka: ništa od ovoga nije „teorija za ispit” – sve završava kao dokaz u završnom radu.
""",
4: """
⏱ ~2 min · prijelaz

Pitanje za polaznike (nakon obrana je to prirodan nastavak): „Koji vam je popravak u drugom tjednu bio najteži – i bi li preživio da kolega sutra doda novi endpoint?”
Saslušajte dva-tri odgovora. Obično se pokaže da su popravci lokalni: if u jednoj metodi, filter za jednu putanju, zaglavlje na jednoj stranici. Iz toga slijedi tema poglavlja: obrana koja ovisi o tome da se programer svaki put sjeti nije obrana – ona mora biti zadana (default) i na jednom mjestu.
""",
5: """
⏱ ~5 min

Prođite tablicu redak po redak i za svaki redak recite oznaku iz kataloga T2 (polaznici je prepoznaju iz svojih varijanti):
• provjera vlasnika u svakom DELETE-u (S01, IDOR) → autorizacija nad objektom u okviru (poglavlje 4) + RLS u bazi (sutra);
• popis dopuštenih returnUrl-ova (S03) → preusmjeravanje samo na lokalne putanje;
• ručni CORS i zaglavlja (S04, S09) → jedna konfiguracija za sve odgovore (poglavlje 5);
• SHA-256 → bcrypt (S07) → PasswordEncoder / PasswordHasher<T> / pwdlib s automatskom migracijom starih hasheva (poglavlje 2);
• nadogradnja YAML biblioteke (S06) → to nije posao koda nego procesa: SCA, Dependabot i SBOM u pipelineu (poglavlje 6);
• try/catch koji propušta (S13, fail-open) → autorizacija prije logike, zadano odbij;
• parametrizacija upita (S08) → i minimalna prava aplikacijskog korisnika baze (sutra).

Pročitajte pravilo na dnu slajda i zastanite. Primjer iz prakse: većina IDOR propusta u bug bounty izvještajima nastaje na NOVOM endpointu koji je netko dodao bez provjere koja postoji na starima.

Pitanje: „Koji od vaših devet popravaka bi automatski vrijedio i za endpoint koji još ne postoji?”
""",
6: """
⏱ ~5 min

Slijed s lijeva na desno je ono što svaki okvir radi prije vašeg koda: rub (CORS, zaglavlja, ograničenje zahtjeva) → autentikacija (tko si) → autorizacija (smiješ li) → kontroler → podaci. Ručne provjere iz T2 bile su sve u kutiji „Kontroler” – zato su se morale ponavljati.

Tri okvira, ista ideja, različite zadane postavke:
• Spring Security: čim dodate starter, SVE je zaštićeno, CSRF je uključen i dodaju se sigurnosna zaglavlja. Iznimke (permitAll) navodite izričito.
• ASP.NET Core: autentikacija i autorizacija su middleware; bez FallbackPolicy endpoint bez [Authorize] je JAVAN. Zato u primjeru postavljamo fallback politiku RequireAuthenticatedUser (deny by default).
• FastAPI: nema ugrađenog sigurnosnog lanca. Ovisnost (Depends) na ruti je opt-in – zaboravljeni parametar znači otvorenu rutu. Zato u primjeru koristimo GLOBALNU ovisnost u FastAPI(dependencies=[…]) i dekorator @javno za iznimke; CORS i zaglavlja su middleware koji dodajete sami.

Pitanje za Python polaznike: „Što se događa u vašem T2 projektu ako dodate rutu i zaboravite parametar Prijavljeni?” (Odgovor: ruta je javna.)
""",
7: """
⏱ ~1 min · prijelaz

Autentikacija odgovara na pitanje „tko si”. U T2 svaki projekt ima vlastitu prijavu i vlastite tokene u memoriji – to je najčešći izvor grešaka (S07 lozinke, S11 reset token). Danas dvije poruke: (1) okvir provjerava token umjesto vas, (2) ako lozinke morate čuvati sami, koristite provjerenu biblioteku i sporu funkciju s parametrima.
""",
8: """
⏱ ~6 min

Lijevo Java (okviri/java/…/SigurnosnaKonfiguracija.java), desno C# (okviri/dotnet/src/Okviri.Api/Program.cs). Kod je skraćen – puni primjer je u paketu „DevSecOps i mehanizmi okvira”.

Java – pokažite redom:
• requestMatchers(...).permitAll() su iznimke; istaknuti redak anyRequest().authenticated() je pravilo „zadano zabranjeno”. Redoslijed je bitan – prvo pravilo koje odgovara pobjeđuje.
• oauth2ResourceServer(jwt): Spring s issuer-uri sam dohvaća JWKS, provjerava potpis, iss i exp; audiences dodajemo u application.properties.
• STATELESS: nema sesije na poslužitelju; CSRF je isključen jer token ne šalje preglednik sam (vidi poglavlje 5).
• CSP default-src 'none' za API koji vraća samo JSON.

C# – AddJwtBearer s Authority i Audience; istaknuta FallbackPolicy je ekvivalent anyRequest().authenticated(). Česta greška: UseAuthorization prije UseAuthentication ili zaboravljen MapInboundClaims = false (tada se claimovi preimenuju u duge URI-je pa uloge „nestanu”).

Česte greške polaznika: permitAll("/**") ostavljen „za testiranje”, ručna provjera tokena koja ostane uz novu konfiguraciju (dvije istine), istek tokena koji se ne provjerava (sjetite se Lab12 iz T1).
""",
9: """
⏱ ~5 min · NOVO: Python / FastAPI

Isti koncept u FastAPI-ju (okviri/python/okviri/aplikacija.py, sigurnost/ovlasti.py, sigurnost/tokeni.py).

Lijevo – zadano zabranjeno:
• Globalna ovisnost dependencies=[Depends(zadano_zabranjeno)] izvršava se za SVAKU rutu. Ruta je javna samo ako je označena s @javno – iznimka je izričita, kao permitAll u Springu ili [AllowAnonymous] u .NET-u.
• Ruta moje dobiva korisnika kao tip parametra (PrijavljeniKorisnik) – iz provjerenog tokena, nikad iz parametra zahtjeva.
• debug=False: FastAPI/Starlette inače vraća traceback u odgovoru.

Desno – provjera JWT-a s PyJWT:
• Algoritam je zadan u kodu (RS256) – nikad iz zaglavlja tokena. To zatvara napade alg: none i „HS256 potpisan javnim ključem” (zamjena algoritma).
• issuer i audience su obavezni, a options require traži da exp, iat, iss i aud uopće postoje (PyJWT inače ne javlja grešku za claim koji nedostaje).
• PyJWKClient dohvaća javne ključeve s Keycloaka i čuva ih 5 minuta; nepoznat kid pokreće ponovno dohvaćanje (rotacija ključeva).

Kako se to testira: test_sigurnost_api.py prolazi kroz SVE rute iz OpenAPI sheme i provjerava da bez tokena vraćaju 401 – i rutu koju netko doda sutra. To je sigurnosni regresijski test u jednoj petlji. Testovi ne trebaju Keycloak: RSA ključ se generira u testu, a zamjenjuje se samo izvor ključeva (dependency_overrides).
""",
10: """
⏱ ~5 min

Parametri su prema OWASP Password Storage Cheat Sheetu: Argon2id (m = 19 MiB, t = 2, p = 1) prvi je izbor; bcrypt s cost ≥ 10 (pazite: bcrypt koristi samo prva 72 bajta lozinke); PBKDF2-HMAC-SHA256 s 600 000 iteracija kad treba FIPS.

Ključna poruka za projekt (S07): ne treba tražiti od korisnika nove lozinke. Sva tri okvira znaju PROVJERITI stari hash i pri uspješnoj prijavi ga ZAMIJENITI novim:
• Java: DelegatingPasswordEncoder – prefiks {bcrypt}, {argon2}, {sha256} govori kojim algoritmom je hash nastao;
• C#: PasswordHasher<T> vraća SuccessRehashNeeded;
• Python: pwdlib PasswordHash(...).verify_and_update vraća novi hash kad stari treba zamijeniti.
U demonstraciji A (korak 9) vidi se u logu aplikacije: markov SHA-256 hash iz T2 zamijenjen je Argon2id hashem.

Pravila za lozinke (desno): ASVS 5.0 6.2.1 traži najmanje 8 znakova i snažno preporučuje 15; NIST SP 800-63B-4 (2025) za lozinku kao jedini faktor traži najmanje 15 znakova. Bez pravila sastava i bez periodične promjene – ali s provjerom protiv procurjelih lozinki (npr. k-anonimni upit prema Have I Been Pwned).

Pitanje: „Zašto je jedinstvena poruka za pogrešno ime ili lozinku sigurnosni zahtjev?” (Enumeracija korisnika – Lab11 iz T1.)
""",
11: """
⏱ ~1 min · prijelaz

Najbolja vlastita prijava je ona koju ne pišete. U produkciji autentikaciju radi specijalizirani poslužitelj identiteta (Keycloak, Microsoft Entra ID, Auth0…), koji već ima MFA, zaključavanje, politiku lozinki i reviziju. Aplikacija postaje „resource server”: samo provjerava token. U laboratoriju to je Keycloak 26 u Dockeru (okviri/keycloak).
""",
12: """
⏱ ~6 min

Prođite korake 1–6:
1. Klijent (SPA ili mobilna aplikacija) šalje korisnika na Keycloak s code_challenge (hash nasumične tajne code_verifier).
2. Prijava se događa NA KEYCLOAKU (uključujući MFA) – aplikacija nikad ne vidi lozinku.
3. Keycloak vraća jednokratni code na registrirani redirect_uri.
4. Klijent mijenja code za token i šalje code_verifier – samo tko je pokrenuo tok zna verifier, pa ukradeni code napadaču ne vrijedi (to je smisao PKCE-a).
5. Access token (JWT) i ID token.
6. API prima Authorization: Bearer <JWT>.

RFC 9700 (OAuth 2.0 Security Best Current Practice, 2025): implicit tok i password grant se više ne koriste; za javne klijente Authorization Code + PKCE.

Iskrena napomena za laboratorij: klijent medtermin-dev-cli koristi password grant SAMO za razvoj i automatske provjere (curl, CI). U pravom sučelju to se ne radi.

Donji okvir je najvažniji: API provjerava potpis preko JWKS-a, iss, aud, exp/nbf i dopušteni algoritam. Uloge dolaze iz tokena, a VLASNIŠTVO nad zapisom iz baze – token ne zna kojoj rezervaciji pripadate.

Demo (kratko, može uz demonstraciju A): otvorite http://localhost:8180/realms/akademija/.well-known/openid-configuration i pokažite jwks_uri; korak 3 skripte ispisuje claimove tokena.
""",
13: """
⏱ ~1 min · prijelaz

Autorizacija ima tri razine: funkcija (smije li korisnik uopće brisati?), objekt (smije li obrisati BAŠ OVAJ zapis?) i polje (smije li vidjeti OIB?). IDOR iz T2 (S01) je greška na razini objekta. Pravilo koje se provlači kroz cijelo poglavlje: zadano odbij.
""",
14: """
⏱ ~6 min

Java: @PreAuthorize prije poziva metode izračuna izraz – „ADMIN ili vlasnik”. Provjera vlasništva je u beanu Vlasnistvo, jednom mjestu koje se može testirati. Nepoznati zapis → false → odbijeno. U punom primjeru @HandleAuthorizationDenied(handlerClass = NijePronadeno.class) pretvara odbijanje u 404.

C#: resursna autorizacija. Handler za par (zahtjev, resurs) uspoređuje vlasnika s User.Identity.Name; kontroler poziva AuthorizeAsync(User, rezervacija, "VlasnikIliAdmin") i za neuspjeh vraća 404.

Zašto 404, a ne 403? 403 potvrđuje da zapis postoji – to je curenje informacija (enumeracija ID-eva). Za tuđi i nepostojeći zapis odgovor mora biti isti.

Usporedite s T2: tamo je if u svakoj metodi kontrolera. Ovdje je pravilo deklarativno i vidi se u code reviewu na prvi pogled. Polaznicima: ovo je najbolji kandidat za „barem dva mjesta s ručnom provjerom” u zadatku.
""",
15: """
⏱ ~5 min · NOVO: Python / FastAPI

okviri/python/okviri/sigurnost/ovlasti.py i rezervacije.py.

Lijevo: Vlasnistvo je klasa čija instanca je FastAPI ovisnost. Prima id iz putanje i prijavljenog korisnika (koji je i sam ovisnost – token se provjeri samo jednom po zahtjevu). Ako zapis ne postoji ili nije njegov (a korisnik nije ADMIN) → 404. Pravilo je napisano jednom.

Desno: ruta obrisi traži parametar tipa VlastitaRezervacija. Kad funkcija krene s izvršavanjem, vlasništvo je VEĆ provjereno – u tijelu nema nijednog if-a za ovlasti. Zaboravljena provjera postaje greška tipa koju se vidi u reviewu.

Uloge: Security(prijavljeni_korisnik, scopes=["ADMIN"]) na cijelom routeru /api/admin – vrijedi i za svaku novu rutu pod tim prefiksom (kao requestMatchers("/api/admin/**").hasRole("ADMIN") u Springu). FastAPI „scopes” ovdje koristimo za realm uloge iz Keycloaka.

Prijenos u T2 projekt (Python polaznici): funkcija koja dohvaća zapis i provjerava vlasnika postaje ovisnost; ruta je dobiva kao parametar. Skriveni testovi iz T2 i dalje moraju prolaziti.
""",
16: """
⏱ ~3 min

Četiri načela – svako povežite s nečim što su vidjeli:
• Deny by default: anyRequest().authenticated(), FallbackPolicy, globalna ovisnost u FastAPI-ju. Nova ruta je zaštićena bez ijedne linije koda.
• Autorizacija prije logike: S13 (fail-open) iz T2 nastaje kad je provjera u istom try bloku kao ostala obrada pa iznimka „propusti” zahtjev. U okviru se odluka donosi prije kontrolera; iznimka u provjeri = odbijanje. Isto načelo vrijedi za sigurnosna vrata pipelinea (poglavlje 6): alat koji nije radio ne znači „nema nalaza”.
• Jedno mjesto istine: politike, handleri i ovisnosti umjesto if-ova razasutih po kontrolerima – lakše za pregled i za testiranje.
• Obrana u dubinu: okvir provjerava pristup, a baza (sutra: RLS) filtrira retke i aplikacijski korisnik ima minimalna prava – pa i propust u kodu ne otkriva tuđe podatke.

Pitanje: „Ako zaboravite provjeru vlasništva na novom endpointu, koja vas linija još štiti?” (Sutra: RLS.)
""",
17: """
⏱ ~1 min · prijelaz

Rub aplikacije: što se događa prije nego što zahtjev uopće stigne do autentikacije (CORS, ograničenje broja zahtjeva) i što dodajemo svakom odgovoru (zaglavlja). Plus tajne – jedina vrsta „podataka” koja nikad ne smije biti u repozitoriju.
""",
18: """
⏱ ~5 min

Tablica je polazište za API i jednostavne HTML stranice iz projekata:
• CSP: za API koji vraća samo JSON default-src 'none'; frame-ancestors 'none'. Za HTML stranice (ispis, prijava) script-src 'self' – to je druga linija obrane od XSS-a (S09), uz kodiranje izlaza.
• HSTS samo preko HTTPS-a: preglednik ga preko HTTP-a ionako ignorira (zato ga u demonstraciji na localhostu nema).
• CORS: Access-Control-Allow-Origin nikad ne smije zrcaliti Origin iz zahtjeva uz credentials – to je bio propust S04. Fiksni popis iz konfiguracije.

CSRF (okvir dolje): napad postoji samo kad preglednik SAM šalje vjerodajnicu – kolačić. API s Bearer tokenom u zaglavlju ga nema. Ali: projekti iz T2 imaju i /prijava formu s kolačićem SESSION – ako je zadržite, CSRF zaštita mora ostati (Spring je zadano uključuje; .NET antiforgery; u FastAPI-ju double-submit token).

ASVS 5.0: 3.4.1 HSTS, 3.4.2 CORS, 3.4.3 CSP, 3.4.4 nosniff – isti brojevi su u vašoj ASVS listi iz T2.
""",
19: """
⏱ ~5 min

Lijevo: ugrađeni rate limiter ASP.NET Corea. Isječak je skraćen – u punom primjeru brojač je PO IP ADRESI (RateLimitPartition.GetFixedWindowLimiter), a odbijanje vraća 429 s Retry-After. Java primjer to radi s Bucket4j (token bucket). Ograničenje štiti prijavu od pogađanja i API od iscrpljivanja resursa.
Napomena iz prakse: iza reverse proxyja svi klijenti imaju istu IP adresu ako aplikacija ne vjeruje X-Forwarded-For od proxyja – tada ograničenje blokira sve ili nikoga.

Tajne (desno i dolje):
• nikad u kodu ni u application.properties / appsettings.json u repozitoriju;
• u razvoju: dotnet user-secrets, varijable okruženja, .env izvan Gita;
• u produkciji: upravitelj tajni (HashiCorp Vault, Azure Key Vault, AWS Secrets Manager) i managed identity – idealno bez ijedne lozinke u konfiguraciji;
• gitleaks u pipelineu (poglavlje 6) i pre-commit hook;
• tajna koja je jednom bila u povijesti Gita je kompromitirana – rotirajte je; brisanje commita ne pomaže (forkovi, klonovi, cache).

Primjer u paketu: .NET aplikacija se NE pokreće bez Obavijesti:ApiKljuc (ValidateOnStart) – to je fail fast za konfiguraciju.
""",
20: """
⏱ ~4 min · NOVO: Python / FastAPI · zatim DEMONSTRACIJA A (~20 min)

Lijevo: biblioteka limits (ista koju interno koristi slowapi) kao obična FastAPI ovisnost na ruti prijave – 5 pokušaja u minuti po IP adresi, zatim 429 i Retry-After. Brojač je u memoriji jednog procesa; za više instanci Redis spremište ili ograničenje na API gatewayu.

Dolje: pydantic-settings čita tajnu iz okruženja ili .env (u .gitignore). SecretStr se ne ispisuje u repr ni u logu. Polje NEMA zadanu vrijednost – bez tajne aplikacija se ne pokreće (fail fast), umjesto da tiho radi s „dev” ključem.

Desno: što FastAPI NE radi sam, a primjer radi. Posebno istaknite grešku validacije: zadani FastAPI odgovor 422 vraća i unesene vrijednosti – uključujući lozinku iz tijela zahtjeva. Primjer ga pretvara u 400 bez vrijednosti (test_lozinke_i_prijava.py to provjerava).

DEMONSTRACIJA A – mehanizmi okvira (okviri/README.md, odjeljak „Demonstracija”)
• Pokrenuto unaprijed: Keycloak (okviri/keycloak) i primjer u tehnologiji koju bira većina polaznika.
• python demo/demo_okviri.py <java|dotnet|python> – 9 koraka, Enter između njih. Uz svaki korak otvorite kod koji ga radi (tablica u README-u).
• Najvažniji trenuci: korak 2 (401 bez ikakve provjere u ruti), korak 5 (krivotvoreni tokeni → 401), korak 6 (marko briše aninu → 404), korak 9 (isti odgovor, nadogradnja hasha u logu, 429).
• Bonus: pokrenite Python primjer bez OKVIRI_OBAVIJESTI_API_KLJUC – aplikacija se namjerno ne pokreće.
• Rezerva bez Dockera: --bez-keycloaka (koraci 1, 2, 8, 9) i testovi (pytest -v / ./mvnw test / dotnet test).

Nakon demonstracije: stanka 10–15 minuta.
""",
21: """
⏱ ~1 min · prijelaz

Sve dosad je bilo u kodu. Ali tko jamči da sutrašnji commit neće vratiti new Yaml(), ranjivu biblioteku ili CORS „samo za testiranje”? DevSecOps: sigurnosne provjere koje se izvršavaju SAME, na svaki commit i pull request, i koje mogu zaustaviti spajanje. Cilj ovog poglavlja: svaki polaznik do kraja tjedna ima takav pipeline na svom projektu.
""",
22: """
⏱ ~5 min

Šest faza predloška (devsecops/<java|dotnet|python> u paketu):
1. Build i testovi – uključujući VAŠE sigurnosne testove iz T2 (crveno → zeleno) i pokrivenost koda (JaCoCo / Coverlet / coverage.py).
2. SAST – Semgrep (OWASP Top 10 + vlastita pravila za regresije) i alat po jeziku: SpotBugs + Find Security Bugs, Roslyn analizatori, Bandit.
3. SCA i SBOM – CycloneDX SBOM, OSV-Scanner nad njim; Python i pip-audit; Dependabot otvara PR-ove za nadogradnje.
4. Tajne – gitleaks nad CIJELOM poviješću.
5. DAST – OWASP ZAP baseline nad pokrenutom aplikacijom, uz kuku koja se prijavi i pošalje ciljane provjere.
6. Sigurnosna vrata – ci/gate.py jedino odlučuje: blokiraju visoki i kritični nalazi, svaka tajna, ZAP High.

Dvije poruke koje treba ponoviti:
• Vrata su fail-closed: ako izvještaj nekog alata nedostaje, vrata ne prolaze. Alat koji nije radio nije isto što i alat koji ništa nije našao (S13 na razini procesa).
• Logičke propuste (S01 tuđi zapis, S10 utrka, S12 logiranje, S13 fail-open) alati NE vide – hvataju ih samo vaši testovi u fazi 1. Tablica u devsecops/README.md, odjeljak 5, točno pokazuje koji alat hvata koji propust u svakoj tehnologiji.
""",
23: """
⏱ ~4 min · zatim DEMONSTRACIJA B (~25 min)

Isječak je skraćen; u predlošku workflow nema logike – svaki posao poziva skriptu ci/*.sh koja radi i lokalno (Linux, macOS, WSL).

Dobra praksa (desno):
• akcije prikvačene na verziju ili, sigurnije, na SHA commita (Dependabot ih i dalje ažurira);
• permissions: contents: read – GITHUB_TOKEN dobiva samo ono što posao treba;
• tajne samo kroz secrets, nikad ispisane u logu;
• lažno pozitivni nalaz: dokumentirana, USKA iznimka (ci/prihvaceno.txt s odsječkom koda), nikad isključen alat;
• SARIF se sprema kao artefakt jer privatni repozitoriji bez GitHub Advanced Security nemaju code scanning.

DEMONSTRACIJA B – DevSecOps (devsecops/README.md, odjeljak 6; za predavača DEMO-PREDAVAC.md)
1. Na početku pošaljite pripremljenu granu demo/regresija i otvorite PR – crveni rezultat stiže dok objašnjavate.
2. Zeleno pokretanje na main: graf poslova, Summary posla „Sigurnosna vrata”, artefakti (SARIF u VS Codeu, sbom.cdx.json), ci/gate.py i ci/prihvaceno.txt.
3. Crveni PR: koji je alat uhvatio vraćenu ranjivost i zašto se PR ne može spojiti (zaštita grane s obaveznom provjerom).
4. Ako ostane vremena: lokalno pokretanje (ci/*.sh, GATE_PRESKOCI=dast).
Ne otvarajte izvorni kod demo repozitorija – to je referentno rješenje MedTermina.
""",
24: """
⏱ ~3 min

A03:2025 Software Supply Chain Failures obuhvaća ne samo ranjive biblioteke nego i sam proces izgradnje. Dva poznata primjera: xz-utils (2024., backdoor koji je strpljivi „održavatelj” ugradio u biblioteku) i kompromitirana GitHub akcija tj-actions/changed-files (2025., ispisivala je tajne iz tisuća pipelinea u javne logove) – zato prikvačivanje akcija na SHA.

• SBOM: popis svih komponenti uz svaki build. Kad sutra izađe novi CVE, iz SBOM-a se u minuti zna jeste li pogođeni.
• Ažuriranje: Dependabot ili Renovate, s rokovima za zakrpe prema ozbiljnosti (ASVS 15.1.1, 15.2.1).
• Integritet builda: prikvačene verzije, provjereni izvori paketa, potpisani artefakti, provenance (SLSA).
• Pipeline je kod: pregled promjena workflowa, minimalne ovlasti tokena, zaštićene grane.

Veza s propisima: Cyber Resilience Act za proizvode s digitalnim elementima traži SBOM i obradu ranjivosti tijekom cijelog životnog ciklusa – obveza prijave aktivno iskorištenih ranjivosti vrijedi od 11. 9. 2026.
""",
25: """
⏱ ~1 min · prijelaz

Dosad: KAKO se štititi. Sada: KOLIKO i ZAŠTO – koje prijetnje su važne i što o tome kažu standardi i propisi. Danas je ovo kratki uvod (~15 minuta); na Danu 3 radionica je posvećena upravo ovome na vašim projektima: model prijetnji za aplikaciju, bazu i CI/CD, registar rizika i ASVS lista s dokazima.
""",
26: """
⏱ ~5 min

Jednostavan registar dovoljan je za projekt: vjerojatnost (V) i utjecaj (U) od 1 do 3, rizik = V × U. Primjeri su iz MedTermina, ali vrijede za sve tri domene.

Prođite dva retka:
• Pristup tuđim nalazima (IDOR): vjerojatnost 3 (lako se otkrije i iskoristi), utjecaj 3 (zdravstveni podaci, GDPR čl. 9 – posebna kategorija). Postupanje: smanjiti – autorizacija nad objektom u okviru i RLS u bazi.
• Ranjiva biblioteka bez zakrpe: ponekad zakrpa ne postoji. Tada privremeno prihvatiti uz kompenzacijsku mjeru i ROK – i to je dokumentirana odluka, ne zaborav.

Četiri načina postupanja (tekst ispod tablice): izbjeći, smanjiti, prenijeti, prihvatiti. Prihvaćanje je legitimno – ako ga potpiše vlasnik rizika, a ne programer u prolazu.

Za zadatak: barem 5 rizika, svaki s mjerom ili obrazloženim prihvaćanjem; na Danu 3 rizike izvodimo iz dijagrama toka podataka i STRIDE-a, pa ih povezujemo s ranjivostima varijante.
""",
27: """
⏱ ~5 min

Za programera su važne obveze koje se pretvaraju u zahtjeve i dokaze:
• NIS2 – u Hrvatskoj Zakon o kibernetičkoj sigurnosti (NN 14/2024): ključni i važni subjekti (zdravstvo, financije, digitalna infrastruktura…) moraju upravljati rizicima, uključujući sigurnost lanca opskrbe i sigurni razvoj. Incident: rano upozorenje u 24 sata, obavijest u 72 sata, završno izvješće u mjesec dana.
• CRA – proizvodi s digitalnim elementima na tržištu EU: sigurnost po dizajnu, SBOM, obrada ranjivosti; prijava aktivno iskorištenih ranjivosti od 11. 9. 2026., puna primjena od 11. 12. 2027.
• GDPR čl. 25 (zaštita podataka po dizajnu i zadanim postavkama) i čl. 32 (sigurnost obrade: enkripcija, pseudonimizacija, redovito testiranje mjera); povreda podataka: obavijest AZOP-u u 72 sata (čl. 33).
• DORA – financijski subjekti, primjenjuje se od 17. 1. 2025.: otpornost IKT sustava, testiranje i rizik trećih strana.

Za projekt: analiza iz perspektive NARUČITELJA aplikacije. MedTermin (zdravstvo) je tipični NIS2 subjekt; Ulaznica i Kadrovska prvenstveno GDPR (Kadrovska: podaci zaposlenika, platne liste). Polaznici ne pišu pravnu analizu – nego koje obveze postoje i koja kontrola u njihovom kodu ili bazi ih pokriva.

Napomena: nisam pravnik – za konkretne obveze subjekta mjerodavni su zakon i nadležna tijela.
""",
28: """
⏱ ~3 min

Lanac koji traži i povjerenstvo na završnoj provjeri: zahtjev → kontrola → test → dokaz.
Primjer s ovog slajda: ASVS 8.2.2 (pristup objektima samo s izričitim ovlastima) i NIS2 kontrola pristupa → kontrola @PreAuthorize / handler / ovisnost Vlasnistvo i RLS u bazi → sigurnosni jedinični test „tuđa rezervacija → 404” (crveno → zeleno) → dokaz: zeleno pokretanje pipelinea, poveznica na commit, izvještaj alata.

Za projekt (okvir dolje): ASVS lista iz 2. tjedna dobiva stupac „dokaz” – ne „Da”, nego „Da – test SigurnostApiTest.tudjaRezervacija404, pokretanje #12”. Lista bez dokaza u rubrici je „djelomična usklađenost”.
""",
29: """
⏱ ~4 min

Zadaci za samostalni rad (dani 4–5), predaja u nedjelju, 22. 11. 2026. u 23:59 – jedan ZIP Vxx-Ime-Prezime-T3.zip (detalji na Moodleu, „Upute – nadogradnja projekta (Tjedan 3)”):
1. DevSecOps pipeline u vlastitom repozitoriju; dokaz da pada kad vratite jednu ranjivost (grana + poveznica na pokretanje).
2. Barem dva mjesta s ručnom provjerom zamijenjena mehanizmom okvira; skriveni testovi iz T2 i vaši testovi i dalje prolaze.
3. Sigurnost baze – sutrašnji laboratorij: T-SQL skripta i izlaz automatske provjere.
4. Usklađenost: ASVS lista s dokazima, kratka NIS2/GDPR analiza i registar od barem 5 rizika.
5. Kviz Tjedna 3 – neograničen broj pokušaja, prolaz 6/10.

Kako se to slaže s rasporedom: zadatak 3 započinjemo sutra (Dan 2), zadatke 1 i 4 i model prijetnji na Danu 3 radimo zajedno na vašim repozitorijima, a dani 4–5 služe za dovršavanje.

DOMAĆA ZADAĆA ZA VEČERAS (važno za sutra):
• docker pull mcr.microsoft.com/mssql/server:2022-latest (~1,5 GB – na mreži u dvorani bi trajalo predugo); Apple Silicon: u Docker Desktopu uključiti Rosettu.
• Projekt iz T2 staviti u vlastiti GitHub repozitorij (privatni repozitorij: dodati predavača kao suradnika).
""",
30: """
⏱ ~5 min · pitanja i zaključak

Sažetak u tri rečenice:
1. Sigurnost koju treba ponoviti na svakom mjestu prepustite okviru – zadano zabranjeno, jedno mjesto istine, testovi koji to dokazuju.
2. Pipeline sa sigurnosnim vratima je automatski regresijski test: popravak vrijedi dok ga netko ne „pojednostavi”, a vrata to uhvate.
3. Usklađenost se ne tvrdi nego dokazuje: zahtjev → kontrola → test → dokaz.

Sutra (Dan 2): sigurnost baza podataka. Ponesite računalo s pokrenutim Dockerom i preuzetom slikom SQL Servera.

Ako je ostalo vremena za pitanja, dobra tema za raspravu: „Koji od vaših T2 propusta NE bi uhvatio nijedan alat iz pipelinea – i kako biste ga ipak zaštitili od regresije?”
""",
}
