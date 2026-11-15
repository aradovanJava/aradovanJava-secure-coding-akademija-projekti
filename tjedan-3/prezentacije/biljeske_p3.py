"""Bilješke govornika – T3 P3: Ispitivanje sigurnosti, rizik i usklađenost (Dan 3, radionica)."""

BILJESKE = {
1: """
DAN 3 · radionica · početak u 16:30 · okvirni tijek (prilagodite trajanju termina)
• Uvod i plan – oko 10 min (slajdovi 1–4).
• Pet blokova rada na vlastitim repozitorijima: pipeline ~45 min, ispitivanje ~40 min, model prijetnji ~35 min, analiza rizika ~25 min, usklađenost ~40 min. Stanka 15 min nakon bloka 2 (ispitivanje).
• Zaključak i zadaci – oko 10 min. Ukupno oko 3 h 25 min sa stankom.
Svaki blok ima isti ritam: 5–10 min objašnjenja uz slajdove, zatim rad polaznika uz obilazak (ili dijeljenje zaslona u online dijelu), na kraju 2–3 minute: jedan polaznik pokaže rezultat.

PRIJE POČETKA
• Svoj demo repozitorij (iz demonstracije B, Dan 1) otvorite u pregledniku: zadnje zeleno pokretanje i grana demo/regresija s crvenim pokretanjem – za slajd 6. Rješenje se ne pokazuje, samo Summary vrata (DEMO-PREDAVAC.md).
• Lokalno pokrenut jedan T2 projekt (npr. MedTermin, Python ili Java) za ručne zahtjeve sa slajda 11.
• Popis polaznika s poveznicama na njihove GitHub repozitorije (iz obrana na Danu 1) – da tijekom radionice brzo otvorite tuđe Actions.
• Pripremite prazan predložak za DFD (draw.io / diagrams.net ili OWASP Threat Dragon) – polaznici mogu crtati i na papiru pa fotografirati.

UVODNA REČENICA
„Prva dva dana ste gledali obrane – u okviru, u pipelineu i u bazi. Danas radimo ono što radi ispitivač i ono što radi revizor: tražimo što još nije pokriveno, procjenjujemo koliko je to opasno i skupljamo dokaze da je ostalo stvarno zaštićeno. Sve na vašem projektu – na kraju dana imate prvu verziju dijelova koje predajete u nedjelju.”
""",
2: """
⏱ ~2 min

Kratko podsjetite na tjedan:
• Dan 1: obrane T2 i P1 – mehanizmi okvira i DevSecOps (demonstracije A i B).
• Dan 2: P2 – sigurnost baza podataka i laboratorij na SQL Serveru (demonstracija C).
• Dan 3 (danas): radionica. Novih alata je malo – koristimo ono što ste već dobili, ali na vlastitom kodu.
• Dani 4–5: samostalno dovršavanje; predaja u nedjelju, 22. 11. 2026. u 23:59.
• Tjedan 4: rad na projektu i završni rad s prezentacijom.

Pet poglavlja odgovara pet dijelova predaje. Recite izravno: „Ako danas prođete svih pet blokova, za vikend ostaje dorada, ne početak.”
""",
3: """
⏱ ~2 min

Ishodi su iz skupa „Sigurnost i zaštita programske potpore” u programu mikrokvalifikacije; u završnoj rubrici odgovaraju elementima E5 (usklađenost), E6 (prijetnje, rizici i ranjivosti) i E7 (rješavanje).
• Ispitati – ne samo pokrenuti alat, nego znati što alat NE pokriva i to ispitati ručno.
• Automatizirati – pipeline koji ste dobili na Danu 1 sada mora raditi na VAŠEM repozitoriju i dokazano pasti na regresiji.
• Analizirati – model prijetnji (DFD + STRIDE) i registar rizika.
• Dokazati – ASVS lista u kojoj svaki redak ima dokaz, plus kratka analiza propisa za domenu.

Ključna rečenica za cijeli dan: „Ono što ne možete pokazati, za revizora ne postoji.”
""",
4: """
⏱ ~2 min

Vremena su okvirna. Ako polaznici zapnu u bloku 1 (najčešće zbog ovisnosti platforme ili Windowsa i skrivenih mapa), ne čekajte da svi budu zeleni: tko nije gotov, nastavlja s pipelineom za vikend, a zajednički idemo dalje – blokovi 3–5 ne ovise o zelenom pipelineu.

Organizacija rada:
• Svatko radi na svom repozitoriju i svojoj domeni (MedTermin, Ulaznica ili Kadrovska).
• Parovi iste domene smiju uspoređivati DFD i registar rizika – ne kopirati.
• Pitanja koja vrijede za sve: postavite ih glasno pa odgovorite svima.
• Rezultate odmah spremajte u repozitorij (npr. mapa docs/: plan-ispitivanja.md, dfd.png, stride.md, registar-rizika.md, asvs.md) – tako za vikend ništa ne ostaje „na papiru”. U predaji (ZIP Vxx-Ime-Prezime-T3.zip) isti dokumenti idu u mapu usklađenost/ – vidi stranicu „Upute – nadogradnja projekta (Tjedan 3)”.
""",
5: """
⏱ ~1 min · prijelaz

Pitanje: „Tko je na svom repozitoriju već imao barem jedno pokretanje pipelinea od utorka?” Podignute ruke ujedno su provjera gdje tko jest.
Poruka poglavlja: pipeline koji prolazi nije cilj sam po sebi – cilj su vrata koja PADNU kad netko vrati propust. Zato je zadnji korak na sljedećem slajdu „dokaz pada”.
""",
6: """
⏱ ~10 min objašnjenja + ~35 min rada

Prođite šest koraka uz svoj demo repozitorij na projektoru:
1. Predložak u repozitorij – iz paketa devsecops-i-mehanizmi-okvira.zip kopira se sadržaj mape java/, dotnet/ ili python/ u korijen projekta (ondje gdje je pom.xml, *.sln ili pyproject.toml). Na Windowsu: Explorer ne prikazuje skrivene mape – .github i .semgrepignore moraju stići u repozitorij (provjera: git status).
2. Prvo pokretanje – Actions → zadnje pokretanje → posao „Sigurnosna vrata” → Summary. Na prvom pokretanju nalazi su normalni: to je polazno stanje, ne neuspjeh.
3. Ovisnosti – Java projekti očekivano imaju mnogo OSV nalaza u ovisnostima platforme (README paketa to objašnjava). Redoslijed: nadogradnja (Dependabot PR), tek ostatak privremeno u osv-scanner.toml s reason i ignoreUntil. Python platforma trenutačno prolazi bez iznimaka.
4. Tajne i iznimke – ako gitleaks nađe pravu tajnu (npr. lozinku iz appsettings ili .env koja je jednom bila commitana): opoziv, ne brisanje iz povijesti. Iznimka u ci/prihvaceno.txt ima pet polja: alat | pravilo | datoteka | odsječak | obrazloženje.
5. DAST s prijavom – ZAP baseline bez prijave vidi samo /, /prijava i /api/health. Dodajte svoje putanje u ci/dast-putanje.txt. Tko je promijenio lozinku korisnika ana, postavlja secret DAST_LOZINKA.
6. Dokaz pada – nova grana (npr. dokaz/regresija), vratite JEDAN propust iz T2 (najlakše S06: ranjiva verzija YAML biblioteke), push → vrata NE PROLAZE. Granu ne spajajte; u izvještaj ide poveznica na crveno pokretanje.

Pokažite na projektoru zeleno i crveno pokretanje svog demo repozitorija – samo Summary, ne kod rješenja.

DOK POLAZNICI RADE – obilazite i provjeravajte:
• je li posao „Sigurnosna vrata” uopće pokrenut (česta greška: workflow nije u .github/workflows/ na main grani);
• jesu li iznimke uske (bez odsječka = sumnjivo);
• Python: postoji li .venv u .gitignore.
""",
7: """
⏱ ~3 min (koristite i kao referencu tijekom rada)

Pet najčešćih simptoma s Dana 1 i iz pripreme paketa:
• Desetci OSV nalaza u Tomcatu, Jacksonu, Spring MVC-u – nije vaša greška nego platforma T2 (Spring Boot 3.5.7 iz listopada 2025.). Nadogradnja je ispravan odgovor; ono što ostane ide u osv-scanner.toml s rokom.
• Nalaz na popravljenom kodu – tipično S08 (ORDER BY iz popisa dopuštenih stupaca): Semgrep, SpotBugs i Roslyn to ne razlikuju od ranjivog koda. Prvo pojednostavite kod (switch koji vraća konstantne SQL nizove), tek onda iznimka.
• gitleaks na staroj povijesti – gitleaks gleda cijelu povijest (fetch-depth: 0): i obrisana tajna je procurila.
• DAST ne može pokrenuti aplikaciju – log je u artefaktu izvjestaj-dast.
• „Izvještaj nedostaje” – vrata su zatvorena pri grešci (fail-closed): alat koji nije radio nije isto što i alat koji ništa nije našao. Isto načelo kao S13 u T2 – vrijedi ga naglasiti.

Pravilo na dnu slajda je najvažnije: široka iznimka (samo alat + pravilo + datoteka) sakrit će i propust koji netko vrati na isto mjesto – to je točno ono što vrata trebaju uhvatiti.
""",
8: """
⏱ ~1 min · prijelaz

Pitanje: „Pipeline je zelen. Je li aplikacija sigurna?” Očekivani odgovor: ne nužno – zelen znači da alati nisu našli ono što znaju tražiti.
Najava: idemo vidjeti koje propuste iz kataloga T2 nijedan alat iz pipelinea ne vidi – i kako ih ispitati.
""",
9: """
⏱ ~4 min

Ispitivanje je postupak, ne pokretanje alata:
• Opseg – što ispitujete (vaša aplikacija na lokalnom računalu ili u testnoj okolini), s kojim ulogama (KORISNIK, privilegirani korisnik domene, ADMIN) i s kojim podacima (seed).
• Plan – OWASP Web Security Testing Guide (WSTG) v4.2 je zadnja stabilna verzija i daje oznake testova (npr. WSTG-ATHZ-04); razvojna verzija na GitHubu neke kategorije preimenuje. ASVS daje razine: L1 (70 zahtjeva u ASVS 5.0.0), L2 (183) i L3 (92). Za projekt: svi L1 koji se odnose na aplikaciju i odabrani L2.
• Izvođenje – alati iz pipelinea plus ručni testovi. Za kontrolu pristupa uvijek treba dva korisnika.
• Izvještaj – svaki nalaz s dokazom, ozbiljnošću i preporukom; nakon popravka ponovno ispitivanje.

Pravni okvir – recite izričito: ispitivanje tuđeg sustava bez pisanog dopuštenja vlasnika je kazneno djelo (neovlašteni pristup računalnom sustavu). U projektu ispitujete samo svoju instancu.

ZADATAK (5 min, zatim nastavak na sljedećem slajdu): u docs/plan-ispitivanja.md upišite opseg, uloge, alate i kriterij prolaza.
""",
10: """
⏱ ~6 min

Ovo je glavna poruka tablice iz README-a DevSecOps paketa: u testiranju predloška na MedTerminu S01, S09, S10, S12 i S13 nije uhvatio nijedan alat – ni u Javi, ni u .NET-u, ni u Pythonu.
• S01 IDOR – alat ne zna da rezervacija 2 pripada Marku. Treba poslovno znanje „čiji je zapis”. WSTG-ATHZ-04 (Insecure Direct Object References), ASVS 8.2.2 (L1).
• S09 pohranjeni XSS – ZAP baseline je pasivan: ne šalje payload, ne sprema ga i ne otvara stranicu za ispis. WSTG-INPV-02, ASVS 1.2.1.
• S10 utrka – pojedinačni zahtjev je uvijek ispravan; greška postoji samo kad stigne više zahtjeva istodobno. WSTG nema zaseban test za utrke – najbliži je WSTG-BUSL-05 (ograničenje broja korištenja funkcije); ASVS 2.3.4 izričito traži da se ograničeni resurs (primjer u standardu: sjedala u kazalištu, termini dostave) ne može dvaput rezervirati.
• S12 logiranje – alat ne čita vaš log i ne zna da je 48291736504 OIB. ASVS 16.2.5 (osjetljivi podaci u logu) i 16.3.1 (sve operacije autentikacije, uspješne i neuspješne, moraju se logirati).
• S13 fail-open – greška nastaje samo kad je format nepoznat; skener taj ulaz ne šalje. WSTG-ERRH-01 i ATHZ-02 (zaobilaženje autorizacije), ASVS 16.5.3.

Pitanje polaznicima: „Koji od ovih pet je bio u vašoj varijanti?” (svaka varijanta ima 9 ranjivih mjesta; S13 i S10 su u većini).
Poruka: sigurnosni testovi iz T2 su jedini automatski čuvar za ovih pet – zato build posao pokreće SVE testove, i vaše.
""",
11: """
⏱ ~4 min objašnjenja + ~25 min rada (blok 2 ukupno)

Lijevo – ručni test u .http datoteci (IntelliJ HTTP Client, VS Code REST Client ili Visual Studio). Sintaksa je ista kao u http/<domena>.http iz T2 predloška: @host i tokeni zalijepljeni iz odgovora na POST /api/auth/login. Pokažite uživo na lokalnom MedTerminu:
1. prijava ana i marko, kopirajte tokene;
2. ana šalje DELETE na rezervaciju 2 (Markovu) → na ispravljenoj verziji 403 ili 404;
3. marko i dalje vidi svoju rezervaciju;
4. marko traži Anin nalaz 1 s format=xml → 4xx, u tijelu nema „Krvna slika” ni teksta iznimke.
Ulaznica: /api/narudzbe/2 i /api/racuni/1; Kadrovska: /api/zahtjevi/2 i /api/platne-liste/1.

Desno – test istodobnosti u Pythonu. Bitno je troje: stvarni poslužitelj (uvicorn na slobodnom portu, ne TestClient), barijera da svi zahtjevi krenu zajedno i provjera da je TOČNO jedan 201 i ostali 409. Fixture posluzitelj i tokeni su skice – u T2 projektu za Python postoji sličan pomoćni kod.
• Java: ExecutorService + CountDownLatch (ili CyclicBarrier), MockMvc ne pomaže – treba stvarni poslužitelj (@SpringBootTest(webEnvironment = RANDOM_PORT)).
• C#: Task.WhenAll nad HttpClientom iz WebApplicationFactory; barijera kao TaskCompletionSource.

ZADATAK (blok 2): za svaki od pet propusta s prethodnog slajda koji je bio u vašoj varijanti napišite ručni zahtjev u docs/rucni-testovi.http i provjerite da postoji automatski test koji isto pokriva. Ako test ne postoji – napišite ga (to je ujedno dokaz za ASVS listu).
""",
12: """
⏱ ~4 min

CVSS 4.0 (FIRST, studeni 2023.) mjeri tehničku ozbiljnost ranjivosti. Prođite vektor na primjeru IDOR-a iz VulnShopa (Lab01, tuđe narudžbe – polaznici ga znaju iz 1. tjedna):
• AV:N – preko mreže; AC:L i AT:N – nema posebnih uvjeta ni preduvjeta; PR:L – dovoljan je prijavljeni korisnik; UI:N – žrtva ništa ne radi.
• Novost u 4.0: posljedice se odvojeno ocjenjuju za ranjivi sustav (VC/VI/VA) i za druge sustave (SC/SI/SA). Ovdje: čitanje (VC:H), bez izmjene i prekida, bez utjecaja na druge sustave.
• Rezultat: 7,1 (visoka). Izračun provjerite u službenom FIRST kalkulatoru – u 4.0 se ocjena ne računa formulom kao u 3.1, nego iz tablica skupina vektora (macrovectors).
Varijanta za S01 (brisanje umjesto čitanja: VC:N, VI:H) daje istu ocjenu 7,1.

Dvije česte zablude:
1. CVSS nije rizik – ne zna je li to vaša najvažnija tablica ni koliko korisnika ima. Rizik radimo u poglavlju 4.
2. EPSS i KEV postoje samo za javno objavljene ranjivosti (CVE) – za ovisnosti, ne za greške u vašem kodu. EPSS (FIRST) daje vjerojatnost iskorištavanja u sljedećih 30 dana; CISA KEV je popis ranjivosti za koje postoji dokaz iskorištavanja. Primjer iz CI/CD-a: CVE-2025-30066 (kompromitirana GitHub akcija tj-actions/changed-files, ožujak 2025.) u KEV-u je od 18. 3. 2025.
""",
13: """
⏱ ~3 min

Četiri dijela zapisa nalaza – isto što ste radili u izvještaju T2, samo strukturirano:
• Što i gdje – naslov razumljiv vlasniku („Korisnik može obrisati tuđu rezervaciju”), mjesto u kodu, CWE (npr. 639), ASVS zahtjev (8.2.2) i CVSS vektor.
• Dokaz – zahtjev i odgovor; tokene, lozinke i stvarne osobne podatke zamijenite oznakama. Koraci moraju biti ponovljivi – netko drugi ih mora moći izvesti.
• Uzrok i popravak – uzrok u kodu (ne „nedostaje provjera” nego „DELETE briše po id-u bez uvjeta vlasnika”), commit i test koji je bio crven pa zelen.
• Ponovno ispitivanje – isti koraci nakon popravka i status. Status „prihvaćen rizik” znači da postoji odluka vlasnika (poglavlje 4), a ne da ste odustali.

STANKA 15 min nakon ovog slajda.
""",
14: """
⏱ ~2 min · prijelaz

Četiri pitanja modeliranja prijetnji (Adam Shostack, Threat Modeling Manifesto) – ostavite ih na zaslonu dok govorite:
1. Što gradimo? → dijagram toka podataka.
2. Što može poći po zlu? → STRIDE po elementu.
3. Što ćemo poduzeti? → kontrola ili zapis u registar rizika.
4. Jesmo li to dobro napravili? → testovi, ispitivanje i ponovni pregled modela kad se arhitektura promijeni.

STRIDE poznajete iz 1. tjedna (kviz: Spoofing → autentifikacija, Tampering → cjelovitost, Repudiation → neporecivost, Information disclosure → povjerljivost, Denial of service → dostupnost, Elevation of privilege → autorizacija).
""",
15: """
⏱ ~6 min objašnjenja + ~20 min rada

Dijagram na slajdu je predložak za sve tri domene – polaznik ga crta za svoju aplikaciju. Četiri vrste elemenata (legenda desno) i granice povjerenja:
• Vanjski entiteti – korisnik (preglednik ili klijent), sustav e-pošte (poveznica za reset lozinke, S11), programer, registar paketa.
• Procesi – API i GitHub Actions.
• Spremišta – baza, dokumenti na disku (nalazi, računi, platne liste – S02), log (S12) i repozitorij s tajnama.
• Tokovi – svaka strelica nosi podatke; oznaka kaže što i kako (HTTPS + token, SQL preko TLS-a).
• Granice povjerenja (isprekidano) – mjesta gdje se mijenja razina povjerenja. Svaka strelica koja prelazi granicu je mjesto za kontrolu.

Na što upozoriti:
• Opskrbni lanac je dio sustava: strelica „artefakt (isporuka)” iz GitHub Actionsa ulazi u poslužitelj. Ako je pipeline kompromitiran, kompromitirana je i aplikacija – zato je CI/CD u istom modelu.
• Tko je na Danu 1 uveo Keycloak, dodaje ga kao vanjski entitet (prijava s PKCE, API dohvaća JWKS).
• Log je spremište, ne „sporedna stvar”: u njemu su (bili) lozinka i OIB.

ZADATAK: nacrtajte DFD svoje aplikacije (draw.io / diagrams.net, OWASP Threat Dragon ili papir pa fotografija) i spremite kao docs/dfd.png. Kriterij: sve strelice imaju oznaku, sve granice povjerenja su ucrtane, baza i CI/CD su uključeni.
""",
16: """
⏱ ~4 min

STRIDE po elementu (Microsoft SDL) smanjuje posao: ne pitate svih šest pitanja za svaki element, nego samo ona koja se na tu vrstu elementa odnose.
• Vanjski entitet: S i R – može li se netko predstaviti kao korisnik i može li korisnik poreći radnju. Primjer: bez zapisa u logu (S12) ne možete dokazati tko je otkazao termin.
• Proces: svih šest. Fail-open (S13) je podizanje ovlasti (E), utrka (S10) narušava cjelovitost (T), stack trace u odgovoru otkriva informacije (I).
• Spremište: T, I, D – a R samo kad je spremište log (uništen ili izmijenjen log = poricanje).
• Tok podataka: T, I, D.
• Granica povjerenja nije element STRIDE-a, ali je mjesto gdje stavljate kontrole – zato je u tablici.

ZADATAK: u docs/stride.md tablica s četiri stupca: element | prijetnja (STRIDE) | postojeća kontrola (s poveznicom na kod ili test) | ako kontrole nema → ID rizika u registru. Cilj: barem 10 redaka, uključujući bazu i CI/CD.
""",
17: """
⏱ ~4 min

Model prijetnji ne smije stati na kodu aplikacije. Ovo povezuje Dan 2 i Dan 1:
• Baza – zajednički račun i db_owner za aplikaciju (P2: minimalne ovlasti), nema revizije pristupa osjetljivim podacima, nešifrirane kopije i OIB u čistom tekstu (TDE, Always Encrypted, DDM iz P2). TRUSTWORTHY: ako je baza označena kao TRUSTWORTHY, a vlasnik joj je sysadmin (npr. sa), član db_owner te baze može podići ovlasti do sysadmina – zato je zadano OFF i vlasnik baze ne smije biti sa.
• CI/CD – akcija referencirana pomičnom oznakom (@v45) izvršit će što god autor (ili napadač) stavi pod tu oznaku. Upravo se to dogodilo s tj-actions/changed-files u ožujku 2025.: oznake su preusmjerene na zlonamjerni commit koji je tajne ispisivao u log pokretanja (CVE-2025-30066). Obrana: referenca na puni SHA commita (Dependabot ga i dalje ažurira) i minimalne ovlasti (permissions: na razini workflowa).
• pull_request_target pokreće se s tajnama ciljnog repozitorija – ako uz to checkouta i pokrene kod iz PR-a, svaki tuđi PR može ukrasti tajne.
• Self-hosted runner za javni repozitorij izvršava kod iz tuđih PR-ova na vašem računalu.

Pitanje: „Ima li vaš workflow permissions na vrhu?” Predložak iz paketa ima – provjerite da ga niste obrisali.
""",
18: """
⏱ ~1 min · prijelaz

Iz modela prijetnji izlazi popis „što može poći po zlu”. Na sve ne stignemo odgovoriti jednako brzo – zato rizik: koje prvo, koje kasnije i koje svjesno prihvaćamo.
Naglasite riječ „tko”: programer predlaže, ali preostali rizik prihvaća vlasnik (naručitelj, voditelj proizvoda), ne programer.
""",
19: """
⏱ ~4 min

Lanac s lijeva na desno:
• Prijetnja (iz STRIDE tablice) se ostvaruje kroz ranjivost (nalaz ili slabost – CWE) i ima posljedicu (podaci, novac, ugled, obveze prema propisima).
• V × U – vjerojatnost puta utjecaj na ljestvicama 1–3 (sljedeći slajd).
• Postupanje – četiri mogućnosti: izbjeći (ukloniti funkcionalnost – npr. izvoz XML-a koji nitko ne koristi), smanjiti (kontrola), prenijeti (ugovor, osiguranje, vanjski pružatelj – npr. plaćanje karticama), prihvatiti (svjesna, zapisana odluka).
• Preostali rizik – rizik nakon mjere, s odlukom vlasnika.

Tri stupca ispod su pitanja za procjenu:
• Vjerojatnost – treba li prijava, poseban alat, znanje? Za ovisnosti: postoji li javni exploit – tu pomažu EPSS i KEV.
• Utjecaj – vrsta podataka (zdravstveni podaci su posebna kategorija prema GDPR-u), broj korisnika i obveze prijave.
• Vlasnik rizika – prihvaćeni rizik ima datum ponovne procjene.
""",
20: """
⏱ ~3 min

Ljestvice su namjerno jednostavne (1–3). Važnije od preciznosti je da su zapisane i da ih svi primjenjuju jednako. Primjeri za domene:
• MedTermin: zdravstveni podaci (nalazi, napomene uz pregled) → utjecaj 3.
• Ulaznica: OIB i ime na ulaznici → utjecaj 2–3; podatke o kartici obrađuje pružatelj plaćanja (prijenos rizika).
• Kadrovska: plaće i OIB zaposlenika → utjecaj 3.

Pragovi: 1–2 nizak, 3–4 srednji, 6–9 visok (umnožak 5, 7 i 8 na ovoj ljestvici ne postoji). Visoki rizici se smanjuju prije isporuke.
Tko želi više: OWASP Risk Rating Methodology (faktori vjerojatnosti i utjecaja na ljestvici 0–9) i ISO/IEC 27005 (upravljanje rizicima informacijske sigurnosti).
""",
21: """
⏱ ~4 min objašnjenja + ~15 min rada

Riješeni primjer je namjerno na VulnShopu iz 1. tjedna, ne na vašim domenama – da ga ne prepišete. Prođite dva retka naglas:
• Lab01 IDOR – vjerojatnost 3 (dovoljan je običan korisnik i promjena broja u URL-u), utjecaj 3 (tuđi podaci) → 9. Mjera: vlasnik u uvjetu upita + test. Nakon mjere vjerojatnost pada na 1 → 3. Utjecaj se ne mijenja – podaci su jednako vrijedni.
• Kratka nedostupnost pretrage – 2 × 1 = 2, prihvaćeno uz rate limit i praćenje. Ovo je primjer svjesnog prihvaćanja: zapisana odluka, vlasnik i rok ponovne procjene.

Pitanje: „Zašto Lab06 (MD5) ima vjerojatnost 2, a ne 3?” – jer je za iskorištavanje potrebno prvo doći do baze (curenje); kad se to dogodi, MD5 bez soli se razbija u sekundama.

ZADATAK: docs/registar-rizika.md – barem 5 rizika za vašu domenu: iz STRIDE tablice prenesite prijetnje bez kontrole i barem jednu iz baze i jednu iz CI/CD-a. Stupci kao na slajdu + vlasnik i rok.
""",
22: """
⏱ ~1 min · prijelaz

Poruka poglavlja: revizor ne vjeruje tvrdnji „implementirali smo autorizaciju”. Traži trag: koji zahtjev, koja kontrola, koji test, koji dokaz. Zadnji blok danas je slaganje tog traga za vaš projekt.
""",
23: """
⏱ ~3 min

Četiri vrste dokaza, od najjačeg prema slabijem:
• Test – najjači dokaz jer se ponavlja automatski. Navedite naziv testa i commit u kojem je postao zelen.
• Izvještaj alata – Summary vrata, SARIF, SBOM, ZAP – uvijek s datumom i commitom (izvještaj bez commita ne dokazuje ništa o današnjem kodu).
• Konfiguracija i kod – isječak ili poveznica na redak u repozitoriju: deny by default, popis origina, zaglavlja, vlastito Semgrep pravilo.
• Stanje baze – izlaz provjere iz SQL Server laboratorija (P2): ovlasti aplikacijskog korisnika, RLS, šifriranje.

Što NIJE dokaz: „implementirano”, snimka zaslona bez datuma i commita, poveznica na dokumentaciju okvira umjesto na vlastiti kod.
""",
24: """
⏱ ~4 min objašnjenja + ~25 min rada

Primjer pet redaka ASVS liste – svi su vezani uz T2 propuste pa polaznici vide kako se njihov rad iz T2 pretvara u dokaz:
• 8.2.2 (L1) – kontrola pristupa nad pojedinačnim zapisom (IDOR/BOLA).
• 3.4.2 (L1) – Access-Control-Allow-Origin je fiksna vrijednost ili provjeren s popisa dopuštenih origina.
• 2.3.4 (L2) – ograničeni resursi se ne mogu dvaput rezervirati.
• 16.2.5 (L2) – osjetljivi podaci se logiraju samo prema razini zaštite (vjerodajnice nikad).
• 15.2.1 (L1) – komponente ne smiju prekoračiti dokumentirane rokove za zakrpe (a 15.1.1 traži da su ti rokovi dokumentirani).

ID-jevi su iz ASVS 5.0.0. Preporuka iz samog standarda: u dokumentima navodite verziju, npr. v5.0.0-8.2.2, jer se brojevi mijenjaju između verzija (u 4.0.3 su bili drugačiji).

ZADATAK: docs/asvs.md – ASVS 5.0.0 lista za vašu aplikaciju: L1 zahtjevi koji se odnose na nju (ostale označite „ne odnosi se” s razlogom) i barem pet L2 zahtjeva, svaki s dokazom. Polazište je lista iz T2 – dodajte stupac „dokaz”.
""",
25: """
⏱ ~5 min

Ovo nije pravni savjet – cilj je da programer zna koja pitanja postaviti i zašto ona mijenjaju zahtjeve za kod. Formulacije su namjerno oprezne: „u opsegu” ovisi o činjenicama koje u projektu ne znamo (veličina tvrtke, djelatnost, kategorizacija).
• MedTermin – zdravstveni podaci su posebna kategorija (GDPR čl. 9). Opsežna obrada posebnih kategorija traži procjenu učinka na zaštitu podataka (čl. 35). Zdravstvo je u NIS2 (Direktiva (EU) 2022/2555) sektor visoke kritičnosti; u Hrvatskoj Zakon o kibernetičkoj sigurnosti (NN 14/2024) – subjekt je u opsegu ovisno o veličini i kategorizaciji nadležnog tijela.
• Ulaznica – OIB i podaci kupaca; kartice ne bi smjele prolaziti kroz vaš sustav (pružatelj plaćanja i PCI DSS). NIS2 uglavnom ne – osim ako je platforma online tržnica (digitalni pružatelji, Prilog II) ili dio subjekta u opsegu.
• Kadrovska – podaci zaposlenika i plaće; čl. 88 GDPR-a dopušta posebna nacionalna pravila za obradu u kontekstu zaposlenja. NIS2 ovisi o djelatnosti tvrtke – HR portal je dio njezina informacijskog sustava i ulazi u njezino upravljanje rizicima.

Zadnji stupac je praktičan: prvo pitanje koje biste postavili naručitelju. Na primjer, voditelj i izvršitelj obrade (čl. 28) – ako aplikaciju razvijate i održavate za polikliniku, vjerojatno ste izvršitelj obrade i trebate ugovor.
""",
26: """
⏱ ~3 min objašnjenja + ~15 min rada

Četiri pitanja vodilje za kratku analizu propisa (1–2 stranice u predaji):
• Koje podatke obrađujemo? – popis po tablici, datoteci i logu (iz DFD-a!), posebne kategorije i rok čuvanja.
• Tko je odgovoran? – voditelj i izvršitelj obrade, vlasnik rizika, kontakt za incidente i za prijavu ranjivosti.
• Kako dokazujemo kontrole? – ASVS lista s prethodnog bloka.
• Što kad pođe po zlu? – rokovi prijave:
  – GDPR: povreda osobnih podataka nadzornom tijelu (u Hrvatskoj AZOP) bez nepotrebnog odgađanja, gdje je izvedivo u roku od 72 sata (čl. 33); ispitanicima ako je rizik visok (čl. 34).
  – NIS2 / ZKS: značajni incident – rano upozorenje u 24 h, obavijest u 72 h, završno izvješće u roku od mjesec dana.
  – CRA (Uredba (EU) 2024/2847): od 11. 9. 2026. proizvođači proizvoda s digitalnim elementima prijavljuju aktivno iskorištene ranjivosti – rano upozorenje u 24 h, obavijest u 72 h, završno izvješće najkasnije 14 dana nakon što je dostupna korektivna mjera (za teške incidente: mjesec dana). Ostale obveze CRA primjenjuju se od 11. 12. 2027. Čista usluga (SaaS) načelno nije u opsegu CRA-a, osim kao rješenje za daljinsku obradu podataka proizvoda – važno ako aplikaciju prodajete kao proizvod.

ZADATAK: docs/uskladenost.md – odgovori na četiri pitanja za vašu domenu, s poveznicama na DFD, registar rizika i ASVS listu.
""",
27: """
⏱ ~3 min

Pravila za korištenje AI asistenata danas i u predaji (vrijede i za završni rad):
• Bez tajni i osobnih podataka – u upit ne lijepite .env, tokene ni stvarne OIB-e. Seed podaci (ana, marko, testni OIB-i iz predloška) su u redu.
• Generirani kod je nepouzdan ulaz – prolazi isti pipeline, testove i vaš pregled. Posebno provjerite autorizaciju i rubne slučajeve: AI rado „popravi” test umjesto koda.
• Izmišljeni paketi – asistent zna predložiti paket koji ne postoji; napadači registriraju takva imena i u njih stave zlonamjerni kod (tzv. slopsquatting). Prije instalacije: postoji li paket u registru, tko ga održava, koliko dugo postoji – i vidi li se u SBOM-u.
• Izvori – AI zna izmisliti ASVS ID, CVE ili članak propisa. Svaki takav podatak provjerite u izvoru. U izvještaju kratko navedite gdje ste koristili AI.

Ovo je ujedno dobar primjer prijetnje iz opskrbnog lanca za vaš STRIDE (T – izmjena, preko ovisnosti).
""",
28: """
⏱ ~3 min

Predaja: nedjelja, 22. 11. 2026. u 23:59, zadaća „Nadogradnja projekta – Tjedan 3” na Moodleu – jedan ZIP Vxx-Ime-Prezime-T3.zip s mapama baza/ i usklađenost/ (ASVS lista, GDPR/NIS2 analiza, DFD sa STRIDE tablicom, registar rizika) i datotekom repozitorij.txt (poveznica na repozitorij i na crveno pokretanje). Upute su na stranici „Upute – nadogradnja projekta (Tjedan 3)”.
1. DevSecOps pipeline – vrata zelena na main i poveznica na crveno pokretanje grane s vraćenim propustom.
2. Mehanizmi okvira – barem dva mjesta s ručnom provjerom zamijenjena mehanizmom okvira, testovi i dalje prolaze.
3. Sigurnost baze – skripta i izlaz provjere iz laboratorija (P2).
4. Prijetnje i rizik – DFD s granicama povjerenja, STRIDE tablica, registar od barem 5 rizika.
5. Usklađenost i kviz – ASVS lista s dokazima, kratka GDPR/NIS2 analiza; kviz Tjedna 3 (neograničen broj pokušaja).

Prije odlaska neka svaki polaznik napravi commit svega što je danas nastalo u docs/ – i neka u jednoj rečenici kaže što mu je za vikend najveći posao. To vam je popis za online konzultacije.
""",
29: """
⏱ ~5 min · pitanja i zaključak

Sažetak u tri rečenice:
1. Zeleni pipeline znači da alati nisu našli ono što znaju tražiti – logiku ispitujete vi, a sigurnosni testovi to čuvaju od regresije.
2. Model prijetnji i registar rizika pokazuju što je važno i zašto – uključujući bazu i CI/CD, ne samo kod.
3. Usklađenost je trag: zahtjev → kontrola → test → dokaz.

Sljedeće: Tjedan 4 – rad na projektu uz nastavnika i završni rad s prezentacijom. Sve što ste danas napravili ide u završni rad (elementi E5–E7 rubrike).

Pitanje za kraj ako ostane vremena: „Koji je rizik u vašem registru najveći – i biste li ga kao vlasnik prihvatili?”
""",
}
