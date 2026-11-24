"""Opća pitanja završnog ispita – neovisna o programskom jeziku (Tjedni 1–4)."""


def Q(id, naslov, tekst, t, n, kod=None, napomena=None):
    return {"id": id, "naslov": naslov, "tekst": tekst, "kod": kod, "t": t, "n": n, "napomena": napomena}


PROBNI = [
    Q("P01", "OWASP 2025 – ranjiva biblioteka",
      "Aplikacija koristi biblioteku za YAML u verziji s poznatom kritičnom ranjivošću (CVE). Kojoj kategoriji "
      "OWASP Top 10:2025 pripada taj propust?",
      ("A03 Software Supply Chain Failures",
       "Ranjive i zastarjele komponente u izdanju 2025. dio su proširene kategorije lanca opskrbe softvera."),
      [("A06 Insecure Design", "Nesiguran dizajn odnosi se na pogreške u logici i arhitekturi, a ne na ranjivu verziju "
                               "biblioteke."),
       ("A08 Software or Data Integrity Failures", "A08 pokriva npr. nesigurnu deserijalizaciju i nepotpisana "
                                                   "ažuriranja; ranjiva ovisnost je A03."),
       ("A02 Security Misconfiguration", "Pogrešna konfiguracija je npr. stack trace u odgovoru ili otvoren Actuator, "
                                         "a ne verzija biblioteke.")],
      napomena="Tjedan 1 (Lab05), Tjedan 2 (S06), demonstracija K03."),

    Q("P02", "Fail-open",
      "Provjera prije odobravanja posudbe napisana je ovako (pseudokod). Kako se zove ovaj obrazac?",
      ("Fail-open: pogreška u sigurnosnoj provjeri pretvara se u „dopušteno”",
       "Iznimka koju provjera baci se proguta, pa se posudba odobri i korisniku s isteklom članarinom (A10)."),
      [("Fail-closed: posudba se odbija čim provjera ne uspije",
        "Upravo suprotno – ovdje se nakon pogreške nastavlja s odobravanjem."),
       ("Ispravno rukovanje pogreškom, jer se pogreška zapisuje u dnevnik",
        "Zapis u dnevnik ne mijenja ishod: posudba je odobrena bez provjere."),
       ("Obrana u dubinu, jer pseudokod ima dva neovisna koraka: provjeru i odobravanje",
        "Obrana u dubinu znači više neovisnih kontrola; ovdje kontrola nakon pogreške nestaje.")],
      kod="pokušaj:\n    provjeri_clanarinu(korisnik)\nako pogreška:\n    zapiši(\"provjera nije uspjela, nastavljam\")\n"
          "odobri_posudbu(korisnik, knjiga)",
      napomena="Lab15, S13, demonstracija K08 – A10 Mishandling of Exceptional Conditions."),

    Q("P03", "STRIDE – poricanje",
      "Pacijent tvrdi da nije otkazao termin, a aplikacija ne bilježi tko je i kada otkazao. Koja kategorija "
      "STRIDE-a opisuje ovu prijetnju?",
      ("Repudiation",
       "Poricanje radnje je moguće jer nema traga – narušeno je svojstvo neporecivosti."),
      [("Spoofing", "Spoofing je lažno predstavljanje (autentikacija), a ovdje je problem nedostatak zapisa."),
       ("Tampering", "Tampering je neovlaštena izmjena podataka; ovdje nitko ne tvrdi da je zapis izmijenjen."),
       ("Elevation of privilege", "Riječ je o nedostatku dokaza o radnji, a ne o stjecanju većih ovlasti.")],
      napomena="Tjedan 3, P3 – STRIDE po elementu; S12 i Lab14 (sigurnosni zapisi)."),

    Q("P04", "IDOR – 404 umjesto 403",
      "Ana šalje `GET /api/clanovi/2` i dobiva profil drugog člana. Ispravak vraća **404** kad zapis ne pripada "
      "prijavljenom korisniku (osim administratoru). Zašto 404, a ne 403?",
      ("Odgovor ne otkriva postoji li tuđi zapis",
       "Tuđi i nepostojeći zapis izgledaju jednako, pa napadač ne može nabrajati postojeće ID-ove."),
      [("Jer 403 smije vratiti samo poslužitelj ispred aplikacije, a ne aplikacija",
        "Aplikacija smije vratiti 403; izbor 404 je namjeran radi skrivanja postojanja zapisa."),
       ("Jer preglednik odgovor 403 automatski ponavlja s drugim tokenom",
        "Preglednik ne ponavlja zahtjev na 403."),
       ("Jer 404 automatski zapisuje sigurnosni događaj u SIEM",
        "Statusni kod sam ne zapisuje ništa; događaj treba izričito zabilježiti.")],
      napomena="Lab01, S01, demonstracija K01 – A01 Broken Access Control."),

    Q("P05", "SQL umetanje – što je obrana",
      "U pretrazi se upit sastavlja spajanjem teksta: `... WHERE naslov LIKE '%` + unos + `%'`. Predložen je "
      "ispravak „ograničiti unos na 100 znakova”. Što je točno?",
      ("Nije obrana – rješenje je parametrizirani upit s unosom kao parametrom",
       "Kratki unos poput `' OR '1'='1' --` prolazi; tek parametar odvaja podatke od SQL naredbe."),
      [("Dovoljno je, jer SQL naredba za napad ne stane u 100 znakova",
        "Udžbenički unosi za umetanje imaju desetak znakova."),
       ("Dovoljno je ako se unos uz to pretvori u mala slova",
        "Veličina slova ne utječe na tumačenje SQL-a."),
       ("Treba zamijeniti operator LIKE operatorom = i zadržati spajanje teksta",
        "Operator nije uzrok – uzrok je spajanje unosa u tekst naredbe.")],
      napomena="Lab07, S08, demonstracija K02 – A05 Injection."),

    Q("P06", "Koji alat nalazi ranjivu biblioteku",
      "Koja vrsta alata u pipelineu pronalazi ovisnost s poznatim CVE-om, uključujući tranzitivne ovisnosti?",
      ("SCA – analiza sastava softvera (npr. OSV-Scanner)",
       "SCA uspoređuje verzije komponenti s bazama ranjivosti; SBOM daje potpun popis komponenti."),
      [("DAST – ZAP baseline nad pokrenutom aplikacijom",
        "DAST vidi ponašanje aplikacije preko HTTP-a, a ne verzije biblioteka u buildu."),
       ("Skener tajni (gitleaks) nad cijelom poviješću repozitorija", "gitleaks traži ključeve i lozinke u kodu i povijesti Gita."),
       ("Jedinični testovi uz izvještaj o pokrivenosti koda", "Pokrivenost mjeri koliko je koda izvršeno, a ne ranjivosti "
                                                 "u ovisnostima.")],
      napomena="Tjedan 1 (alati), Tjedan 3 (pipeline: SCA i SBOM)."),

    Q("P07", "Baza – minimalne privilegije",
      "Kako treba postaviti prava aplikacijskog korisnika baze (SQL Server)?",
      ("Vlastita uloga s GRANT samo na potrebne objekte, bez db_owner i sysadmin",
       "Načelo najmanjih ovlasti ograničava štetu i kad aplikacija ima propust poput SQL umetanja."),
      [("Član uloge db_owner, da migracije sheme rade bez grešaka",
        "db_owner smije mijenjati shemu i dozvole – preširoko za aplikaciju u radu."),
       ("Član uloge db_datareader i db_datawriter u svim bazama na poslužitelju",
        "Te uloge daju čitanje i pisanje svih tablica, uključujući tablicu korisnika i lozinki."),
       ("Prijava sa, jer je tada sigurno da aplikacija ima sva potrebna prava",
        "sa je administrator poslužitelja i treba ga onemogućiti.")],
      napomena="Tjedan 3, P2 – vlastite uloge i dozvole."),

    Q("P08", "Rizik V × U",
      "Prema ljestvicama iz Tjedna 3 (vjerojatnost i utjecaj 1–3, rizik = V × U), prijetnja ima vjerojatnost 2 i "
      "utjecaj 3. Kako se postupa?",
      ("Rizik je 6 (visok) – smanjiti ga prije isporuke",
       "Rizik 6–9 je visok; ako mjera nije moguća, vlasnik rizika ga mora pisano prihvatiti s rokom."),
      [("Rizik je 5 (srednji) – smanjiti ga u dogovorenom roku", "Rizik se računa umnoškom, ne zbrojem: 2 × 3 = 6."),
       ("Rizik je 6 (srednji) – programer ga smije sam prihvatiti",
        "Rizik prihvaća poslovni vlasnik, a ne programer, i 6 nije srednji rizik."),
       ("Rizik je 2 (nizak) – dovoljno je praćenje", "Utjecaj se ne smije zanemariti; rizik je 6.")],
      napomena="Tjedan 3, P3 – ljestvice vjerojatnosti i utjecaja, registar rizika."),

    Q("P09", "GDPR – povreda osobnih podataka",
      "Voditelj obrade utvrdi povredu osobnih podataka kupaca koja vjerojatno predstavlja rizik za njihova prava. "
      "Što propisuje GDPR čl. 33?",
      ("Obavijest AZOP-u u roku od 72 sata od saznanja",
       "Nadzorno tijelo (u Hrvatskoj AZOP) obavještava se bez nepotrebnog odgađanja, a najkasnije u 72 sata."),
      [("Obavijest nadležnom CSIRT-u u roku od 24 sata od početka incidenta",
        "To je rano upozorenje po NIS2/ZKS-u za značajne incidente, a ne obveza iz čl. 33."),
       ("Obavijest svakom kupcu u roku od 14 dana od popravka",
        "Obavijest ispitanicima uređuje čl. 34 (kad je rizik visok, bez nepotrebnog odgađanja)."),
       ("Prijava nije potrebna ako je ranjivost u međuvremenu popravljena",
        "Popravak ne poništava povredu koja se već dogodila.")],
      napomena="Tjedan 3, P3 – rokovi prijave; vježba „Prva 72 sata”."),

    Q("P10", "Što alati ne vide",
      "Na demonstraciji u srijedu nijedan alat (SAST, SCA, DAST) nije pronašao pristup tuđem profilu, produljenje "
      "posudbe za 365 dana ni posudbu uz isteklu članarinu. Što je jedina automatska zaštita od povratka tih "
      "propusta?",
      ("Sigurnosni test (crveno → zeleno) koji se izvodi u pipelineu",
       "Logiku i vlasništvo alat ne poznaje; test ih opisuje i pada čim se propust vrati."),
      [("Stroži prag SAST alata u vratima, npr. blokiranje već na srednjim nalazima", "SAST ne zna čiji je zapis ni koja su poslovna pravila."),
       ("Češće pokretanje ZAP baselinea", "Pasivni DAST s jednim korisnikom ne vidi pristup tuđim podacima."),
       ("SBOM uz svako izdanje i potpisani artefakti", "SBOM popisuje komponente; ne opisuje ponašanje aplikacije.")],
      napomena="Demonstracija Knjižnica (K01, K06, K08); Tjedan 3, P3 – „Što alati ne vide”."),

    Q("P11", "NIST SP 800-63B – lozinke",
      "Koje pravilo za lozinke NIJE u skladu s NIST SP 800-63B?",
      ("Prisilna promjena lozinke svakih 90 dana",
       "Periodična promjena bez znakova kompromitacije se ne preporučuje – vodi slabijim, predvidljivim lozinkama."),
      [("Provjera nove lozinke protiv popisa procurjelih lozinki", "To je preporučena praksa."),
       ("Dopuštanje dugih fraza bez pravila o velikim slovima i posebnim znakovima",
        "NIST preporučuje duljinu umjesto pravila sastava."),
       ("Ograničenje broja neuspjelih pokušaja prijave", "Ograničenje pokušaja je obvezna zaštita od pogađanja.")],
      napomena="Tjedan 3, P1 – lozinke: pohrana i pravila."),

    Q("P12", "CRA – rokovi za aktivno iskorištenu ranjivost",
      "Proizvođač softvera sazna da se ranjivost u njegovom proizvodu aktivno iskorištava. Koje rokove od "
      "11. 9. 2026. propisuje Cyber Resilience Act (čl. 14)?",
      ("24 h rano upozorenje, 72 h obavijest, završno izvješće 14 dana nakon mjere",
       "Prijava ide preko ENISA-ine jedinstvene platforme CSIRT-u koordinatoru i ENISA-i."),
      [("Rano upozorenje 24 h, obavijest 72 h, završno izvješće za mjesec dana",
        "To su rokovi NIS2/ZKS-a za značajne incidente; CRA za ranjivosti traži 14 dana nakon mjere."),
       ("Jedna obavijest AZOP-u u roku od 72 sata", "AZOP je nadzorno tijelo za osobne podatke (GDPR), a ne za CRA."),
       ("Obavijest tek kad je zakrpa objavljena, bez fiksnog roka",
        "CRA propisuje rokove od saznanja, neovisno o tome postoji li već zakrpa.")],
      napomena="Utorak 24. 11. – Cyber Resilience Act; vježba „Prva 72 sata”."),
]

ISPIT = [
    Q("I01", "SSRF – obrana",
      "Funkcija „pregled poveznice” dohvaća URL koji pošalje korisnik i vraća sadržaj. Koja je obrana ispravna?",
      ("Razriješiti ime, odbiti interne adrese i ne pratiti preusmjeravanja",
       "Provjerava se adresa na koju se stvarno spaja, a preusmjeravanje bi zaobišlo provjeru."),
      [("Odbiti svaki URL koji sadrži riječ localhost, 127.0.0.1 ili 0.0.0.0 u nazivu hosta",
        "Lako se zaobiđe: [::1], decimalni zapis adrese, DNS ime koje pokazuje na internu adresu."),
       ("Dopustiti samo HTTPS jer interni servisi obično rade preko HTTP-a", "Interni servisi i metapodaci oblaka mogu biti dostupni i preko HTTPS-a."),
       ("Skratiti vrijeme čekanja odgovora na dvije sekunde", "Timeout štiti dostupnost, ali ne sprječava "
                                                              "dohvat internog resursa.")],
      napomena="Lab03 – SSRF je u OWASP Top 10:2025 dio A01."),

    Q("I02", "Mass assignment",
      "Endpoint za izmjenu profila prima cijeli objekt korisnika iz JSON-a, pa korisnik slanjem `\"uloga\": "
      "\"ADMIN\"` postaje administrator. Koji je ispravak?",
      ("Ulazni DTO samo s dopuštenim poljima, uz validaciju",
       "Uloga se tada uopće ne može postaviti iz zahtjeva; mijenja se samo administratorskim postupkom."),
      [("Na klijentu ukloniti polje uloga iz obrasca prije slanja zahtjeva",
        "Napadač šalje zahtjev izravno, mimo obrasca."),
       ("Preimenovati polje uloga u teže pogodivo ime",
        "Skrivanje imena nije kontrola (security through obscurity)."),
       ("Vratiti 500 ako zahtjev sadrži bilo koje nepoznato polje", "500 je pogrešan status, a uzrok – vezanje cijelog "
                                                          "entiteta – ostaje.")],
      napomena="Lab02 – A01, CWE-915."),

    Q("I03", "XSS i CSP",
      "Koja je tvrdnja o Content-Security-Policy (CSP) točna?",
      ("CSP je drugi sloj obrane; primarna je kontekstualno kodiranje izlaza",
       "CSP ograničava izvore skripti i smanjuje štetu, ali ubačeni sadržaj i dalje treba kodirati."),
      [("CSP potpuno zamjenjuje kodiranje izlaza pa ono više nije potrebno",
        "Pogrešna ili preširoka politika ostavlja XSS otvorenim; kodiranje je primarna obrana."),
       ("CSP na poslužitelju sprječava SQL umetanje u upitima koje šalje preglednik",
        "CSP djeluje u pregledniku na sadržaj stranice, a ne na SQL na poslužitelju."),
       ("CSP postavlja korisnik u postavkama preglednika", "CSP šalje poslužitelj kao zaglavlje odgovora.")],
      napomena="Lab08, S09 – A05 Injection."),

    Q("I04", "Umetanje naredbi OS-a",
      "Funkcija ping pokreće ljusku s tekstom `ping -c 1 ` + host. Unos `127.0.0.1 & whoami` izvrši i drugu "
      "naredbu. Koji je ispravak?",
      ("Validirati host i pokrenuti program bez ljuske, s popisom argumenata",
       "Bez ljuske znakovi `&` i `;` nemaju posebno značenje, a validacija odbija sve što nije IP adresa ili ime."),
      [("Ukloniti znakove & i ; iz unosa prije spajanja u naredbu ljuske", "Ostaju `;`, `|`, `$(...)`, novi red i drugi znakovi ljuske."),
       ("Pokretati aplikaciju kao administrator da naredba sigurno uspije",
        "Veće ovlasti povećavaju štetu umetnute naredbe."),
       ("Kodirati unos Base64 kodiranjem prije spajanja u naredbu, pa ga dekodirati u ljusci",
        "Ping tada ne radi, a kodiranje nije kontrola – dekodirani unos je opet opasan.")],
      napomena="Lab09 – A05, CWE-78."),

    Q("I05", "Prijava – enumeracija i pogađanje",
      "Prijava vraća 404 „Korisnik ne postoji” ili 401 „Pogrešna lozinka” i nema ograničenja pokušaja. Što je "
      "ispravak?",
      ("Ista poruka za oba slučaja i ograničenje neuspjelih pokušaja",
       "Napadač više ne zna koja imena postoje, a pogađanje lozinke postaje nepraktično (429)."),
      [("Prevesti poruke na engleski da odgovaraju standardu HTTP-a", "Jezik poruke ne mijenja curenje informacije."),
       ("Vratiti 500 umjesto 404 za nepostojećeg korisnika", "Različit status i dalje otkriva postoji li korisnik."),
       ("Ukloniti zapis neuspjelih prijava iz dnevnika jer zauzima prostor",
        "Neuspjele prijave su sigurnosni događaj koji treba bilježiti.")],
      napomena="Lab11 – A07 Authentication Failures."),

    Q("I06", "JWT – što API provjerava",
      "API prima pristupni token (JWT) koji izdaje Keycloak. Što API mora provjeriti?",
      ("Potpis ključem izdavatelja (JWKS), zadani algoritam, iss, aud i exp",
       "Tako API zna da je token izdao pravi izdavatelj, za ovaj API i da nije istekao."),
      [("Da se token može dekodirati iz Base64URL i da ima tri dijela",
        "Dekodirati može svatko; dekodiranje ne provjerava potpis."),
       ("Samo claim exp, jer je potpis provjerio Keycloak",
        "Bez provjere potpisa napadač može sam napisati token s bilo kojim claimovima."),
       ("Da je alg iz zaglavlja tokena jedan od none ili HS256",
        "Algoritam se nikad ne uzima iz tokena; `alg: none` je klasičan napad.")],
      napomena="Lab12; Tjedan 3, P1 – OAuth 2.0 i OIDC."),

    Q("I07", "Deserijalizacija",
      "Aplikacija prima serijalizirani objekt od klijenta i deserijalizira ga općim mehanizmom koji može stvoriti "
      "bilo koju klasu. Koja je ispravna mjera?",
      ("JSON u izričit DTO, ili allowlista dopuštenih klasa",
       "Napadač tada ne može odabrati klasu čiji se kod izvršava tijekom deserijalizacije."),
      [("Provjeriti tip objekta odmah nakon deserijalizacije i odbaciti neočekivane", "Prekasno – štetni kod se izvršava tijekom same "
                                                         "deserijalizacije."),
       ("Šifrirati serijalizirane podatke kod klijenta", "Klijent kontrolira i ključ i podatke."),
       ("Ograničiti veličinu zahtjeva na 1 MB", "I mali zlonamjerni objekt je dovoljan.")],
      napomena="Lab13 – A08 Software or Data Integrity Failures."),

    Q("I08", "Sigurnosni zapisi",
      "Koji je zapis neuspjele prijave napisan prema dobroj praksi?",
      ("`SECURITY_EVENT LOGIN_FAILED korisnik=ana ip=10.0.0.5`",
       "Bilježi se događaj, korisnik i izvor, bez tajni; novi red iz unosa ne može krivotvoriti novi zapis."),
      [("`Prijava ana lozinka=Ana123! neuspješna`", "Lozinka nikad ne ide u dnevnik (CWE-532)."),
       ("Ništa – neuspjele prijave se ne bilježe da dnevnik ne bi prebrzo rastao",
        "Bez zapisa nema otkrivanja pogađanja lozinki (CWE-778)."),
       ("Cijelo tijelo zahtjeva na razini DEBUG, radi lakše analize incidenta", "Tijelo zahtjeva sadrži lozinku i druge tajne.")],
      napomena="Lab14, S12, demonstracija K07 – A09."),

    Q("I09", "AES-GCM – nonce",
      "Što vrijedi za nonce (IV) pri šifriranju podataka algoritmom AES-GCM?",
      ("Nasumičan i nov za svako šifriranje istim ključem; sprema se uz šifrat",
       "Ponovljeni nonce s istim ključem ruši povjerljivost i autentičnost; nonce nije tajna."),
      [("Može biti stalan ako je ključ dovoljno dug (256 bitova)", "Duljina ključa ne popravlja ponovljeni nonce."),
       ("Mora biti tajan kao i ključ, pa se čuva u upravitelju tajni odvojeno od šifrata", "Nonce se sprema uz šifrat i nije tajna."),
       ("Nije potreban jer GCM, kao i ECB, šifrira svaki blok neovisno", "GCM je brojački način rada; ECB je upravo način koji izbjegavamo.")],
      napomena="Lab06, dio B – A04 Cryptographic Failures."),

    Q("I10", "OAuth 2.0 – PKCE",
      "Čemu služi PKCE (`code_challenge` i `code_verifier`) u toku Authorization Code?",
      ("Vezuje zamjenu koda za token uz klijenta koji je započeo prijavu",
       "Za token treba i code_verifier, a njega zna samo klijent koji je poslao code_challenge."),
      [("Šifrira pristupni token tako da ga API može pročitati samo privatnim ključem", "PKCE ne šifrira token."),
       ("Zamjenjuje provjeru potpisa tokena na API-ju", "API i dalje provjerava potpis, iss, aud i exp."),
       ("Produljuje trajanje sesije bez ponovne prijave", "PKCE nema veze s trajanjem sesije.")],
      napomena="Tjedan 3, P1 – Authorization Code + PKCE (Keycloak)."),

    Q("I11", "CORS",
      "API na svaki zahtjev vraća `Access-Control-Allow-Origin` jednak zaglavlju `Origin` iz zahtjeva i "
      "`Access-Control-Allow-Credentials: true`. Što je problem?",
      ("Bilo koja stranica može čitati odgovore API-ja u ime prijavljenog korisnika",
       "Reflektirani Origin uz credentials znači da preglednik dopušta čitanje svakom originu."),
      [("API postaje ranjiv na SQL umetanje kroz zaglavlje Origin", "CORS ne utječe na upite prema bazi."),
       ("Preglednik će odbiti sve zahtjeve jer je Origin dinamičan", "Upravo suprotno – dopustit će ih svima."),
       ("Nema problema – CORS je zaštita poslužitelja i blokira pozive iz alata poput curla i Postmana", "CORS provodi samo preglednik; curl ga ne poštuje.")],
      napomena="S04; Tjedan 3, P1 – sigurnosna zaglavlja i CORS (ASVS 3.4.2)."),

    Q("I12", "CSRF",
      "Kada je potrebna zaštita od CSRF-a (token ili kolačić sa SameSite)?",
      ("Kad se korisnik autentificira kolačićem koji preglednik šalje sam",
       "Napadačeva stranica može potaknuti zahtjev koji preglednik pošalje s kolačićem žrtve."),
      [("Uvijek, i za API s Bearer tokenom u zaglavlju",
        "Taj token preglednik ne dodaje sam, pa CSRF tu nije moguć."),
       ("Samo za GET zahtjeve", "GET ne smije mijenjati stanje; CSRF zaštita je za zahtjeve koji ga mijenjaju."),
       ("Samo kad API koristi HTTPS", "HTTPS ne sprječava CSRF.")],
      napomena="Tjedan 3, P1 – rub aplikacije."),

    Q("I13", "Tajna u povijesti Gita",
      "gitleaks u pipelineu pronađe stvarni API ključ u commitu od prije tri mjeseca. Što prvo napraviti?",
      ("Opozvati i zamijeniti ključ",
       "Tajna iz povijesti mogla je već biti kopirana; brisanje commita ne vraća povjerljivost."),
      [("Dodati ključ u .gitleaksignore da vrata prođu", "To samo sakriva nalaz – ključ ostaje kompromitiran."),
       ("Obrisati datoteku s ključem u novom commitu", "Ključ ostaje u povijesti i u svim klonovima."),
       ("Base64 kodirati ključ i ostaviti ga u kodu", "Base64 je kodiranje, a ne šifriranje.")],
      napomena="Tjedan 3, P1 i P3 – tajne, gitleaks."),

    Q("I14", "GitHub Actions – lanac opskrbe",
      "Napad na akciju tj-actions/changed-files (CVE-2025-30066) premjestio je oznake verzija na zlonamjerni "
      "commit. Koja praksa bi zaštitila vaš workflow?",
      ("Akcije prikvačene na puni SHA commita",
       "SHA se ne može premjestiti kao oznaka, a minimalne dozvole ograničavaju štetu."),
      [("Oznaka @latest, da uvijek dobijete najnoviju zakrpu akcije",
        "Pomična oznaka je upravo ono što je napadač iskoristio."),
       ("Pokretanje workflowa samo na granama s malo commitova", "Broj commitova ne utječe na izvor akcije."),
       ("Prelazak na događaj pull_request_target", "pull_request_target ima pristup tajnama i dodatno je "
                                                       "opasan s kodom iz PR-a.")],
      napomena="Tjedan 3, P1 i P3 – pipeline je kod; STRIDE za CI/CD."),

    Q("I15", "Lažno pozitivan nalaz",
      "SAST nakon ispravka i dalje javlja nalaz na retku koji je provjereno siguran. Kako postupiti?",
      ("Uska dokumentirana iznimka za to mjesto i pravilo",
       "Tako nalaz nestaje samo na tom mjestu, a isti obrazac drugdje i dalje ruši vrata."),
      [("Isključiti to pravilo za cijeli projekt", "Time nestaju i stvarni nalazi istog pravila."),
       ("Isključiti SAST korak u pipelineu dok se kod ne prepiše", "Vrata bez SAST-a ne štite od regresije."),
       ("Spustiti prag vrata tako da blokiraju samo kritične nalaze", "To sakriva i stvarne visoke nalaze.")],
      napomena="Tjedan 3, P3 – „Kad vrata ne prolaze”; demonstracija (nalazi za zapise i SQL koji ostaju nakon "
               "ispravka)."),

    Q("I16", "ASVS – valjan dokaz",
      "Za zahtjev ASVS 5.0 8.2.2 (pristup zapisu samo ovlaštenom korisniku) u listi usklađenosti treba upisati "
      "dokaz. Što je najbolji dokaz?",
      ("Sigurnosni test koji je bio crven, a sad je zelen, s commitom",
       "Test je provjerljiv, ponovljiv i štiti od regresije."),
      [("Izjava programera da je provjera dodana", "Tvrdnja bez traga nije dokaz."),
       ("Prazan ZAP izvještaj", "Pasivni ZAP ne ispituje pristup tuđim zapisima, pa prazan izvještaj ne dokazuje "
                                "ništa za 8.2.2."),
       ("Snimka zaslona korisničkog sučelja na kojem više nema gumba za tuđe zapise", "Sučelje nije kontrola pristupa.")],
      napomena="Tjedan 3, P3 – usklađenost s dokazima."),

    Q("I17", "Row-Level Security",
      "Aplikacija na početku zahtjeva postavlja `SESSION_CONTEXT` s imenom prijavljenog korisnika, a politika RLS "
      "filtrira retke tablice rezervacija. Koja je tvrdnja točna?",
      ("Druga linija obrane – ne zamjenjuje autorizaciju u aplikaciji",
       "Ako aplikacija zakaže (npr. SQL umetanje), baza i dalje vraća samo retke tog korisnika."),
      [("Uz RLS provjera vlasništva u aplikaciji više nije potrebna",
        "Obrana u dubinu znači oboje; RLS ovisi o vrijednosti koju aplikacija postavi."),
       ("RLS šifrira retke drugih korisnika", "RLS filtrira retke; ne šifrira ih."),
       ("RLS radi samo uz korisnika db_owner", "Upravo suprotno – aplikacija treba minimalna prava.")],
      napomena="Tjedan 3, P2 – RLS i SESSION_CONTEXT."),

    Q("I18", "Enkripcija u SQL Serveru",
      "Koji mehanizam štiti podatke u stupcu i od administratora poslužitelja baze?",
      ("Always Encrypted", "Ključevi su kod klijenta, pa poslužitelj vidi samo šifrat."),
      [("TDE", "TDE štiti datoteke i kopije na disku; korisnik s pristupom bazi podatke vidi u čistom tekstu."),
       ("Dynamic Data Masking", "Maskiranje mijenja prikaz, a podaci su u čistom tekstu; nije enkripcija."),
       ("Encrypt=true u nizu za spajanje", "To šifrira promet između aplikacije i baze, ne podatke u bazi.")],
      napomena="Tjedan 3, P2 – gdje i od čega štiti enkripcija."),

    Q("I19", "Sigurnosne kopije",
      "Što jedino dokazuje da se šifrirana sigurnosna kopija baze može upotrijebiti?",
      ("Probni restore u zasebnu bazu",
       "Kopija koja nije provjerena vraćanjem nije kopija – nego nada."),
      [("Uspješno izvršena naredba BACKUP s opcijom CHECKSUM", "BACKUP ne provjerava može li se kopija vratiti."),
       ("RESTORE VERIFYONLY nad datotekom kopije", "Provjerava čitljivost i cjelovitost, ali ne i stvarno vraćanje."),
       ("Veličina datoteke kopije usporediva s bazom", "Veličina ne govori ništa o ispravnosti ni o dostupnosti ključa.")],
      napomena="Tjedan 3, P2 – šifrirane kopije i probni restore, pravilo 3-2-1."),

    Q("I20", "DFD – granica povjerenja",
      "Što označava granica povjerenja na dijagramu toka podataka (DFD)?",
      ("Mjesto gdje podaci prelaze između razina povjerenja",
       "Na prijelazu granice provode se autentikacija, autorizacija i validacija, svaki put."),
      [("Fizički vatrozid u podatkovnom centru", "Granica je logički pojam; ne mora biti uređaj."),
       ("Granicu do koje sustav ima jedinične testove", "Pokrivenost testovima nije dio DFD-a."),
       ("Popis korisnika kojima se vjeruje", "Granica se crta između elemenata sustava, a ne kao popis korisnika.")],
      napomena="Tjedan 3, P3 – model prijetnji (DFD + STRIDE)."),

    Q("I21", "Utrka – zadnje mjesto",
      "Rezervacija zadnjeg mjesta radi „provjeri ima li mjesta, pa upiši rezervaciju”. Kod 10 istodobnih "
      "zahtjeva uspije više njih. Koji je ispravak i dokaz?",
      ("Atomski uvjetni UPDATE i test s istodobnim zahtjevima",
       "Provjera i upis postaju jedna nedjeljiva operacija; test dokazuje ponašanje pod istodobnošću."),
      [("Pauza od jedne sekunde između provjere i upisa",
        "Pauza povećava prozor za utrku."),
       ("Provjera broja mjesta na klijentu prije slanja zahtjeva", "Klijentska provjera ne sprječava istodobne zahtjeve."),
       ("Ponoviti provjeru nakon upisa i vratiti 500 ako je mjesta premalo", "Upis se već dogodio; 500 ne vraća "
                                                                             "ispravno stanje.")],
      napomena="S10 – A06 Insecure Design; ASVS 2.3.4."),

    Q("I22", "CVSS, EPSS, KEV i rizik",
      "Koja je tvrdnja točna?",
      ("CVSS opisuje ozbiljnost; rizik ovisi i o vjerojatnosti i utjecaju",
       "EPSS (vjerojatnost iskorištavanja u 30 dana) i KEV (dokazano iskorištene) pomažu procijeniti vjerojatnost."),
      [("CVSS 9,8 uvijek znači visok rizik", "Ovisi o kontekstu: dosegu, izloženosti i podacima."),
       ("EPSS je popis ranjivosti za koje CISA potvrđuje iskorištavanje", "To je KEV."),
       ("KEV mjeri ozbiljnost na ljestvici 0–10", "Ljestvica 0–10 je CVSS.")],
      napomena="Tjedan 3, P3 – CVSS 4.0, EPSS i KEV; vježba „Prva 72 sata”."),

    Q("I23", "NIS2 / Zakon o kibernetičkoj sigurnosti",
      "Bolnica (ključni subjekt) ima značajan incident. Koje rokove prijave nadležnom CSIRT-u propisuje NIS2 "
      "(u Hrvatskoj ZKS)?",
      ("24 h rano upozorenje, 72 h obavijest, završno izvješće za mjesec dana",
       "Rokovi teku od saznanja za značajan incident."),
      [("Jedna obavijest u 72 h, bez daljnjih izvješća", "To podsjeća na GDPR čl. 33; NIS2 ima tri koraka."),
       ("24 h rano upozorenje, 72 h obavijest, završno izvješće 14 dana nakon mjere", "To su CRA rokovi za "
                                                                                    "aktivno iskorištenu ranjivost."),
       ("Prijava samo ako su ukradeni osobni podaci", "NIS2 se odnosi na značajne incidente, neovisno o osobnim "
                                                      "podacima.")],
      napomena="Tjedan 3, P3; vježba „Prva 72 sata”."),

    Q("I24", "GDPR – izvršitelj obrade",
      "Tvrtka nudi web trgovinu kao uslugu (na svojim poslužiteljima) i obrađuje podatke kupaca u ime trgovina. "
      "Otkrije curenje tih podataka. Što joj propisuje GDPR?",
      ("Obavještava voditelje obrade (trgovine) bez nepotrebnog odgađanja",
       "Čl. 33(2); voditelj zatim odlučuje o prijavi AZOP-u (čl. 33(1)) i ispitanicima (čl. 34)."),
      [("Sama prijavljuje povredu AZOP-u umjesto trgovina, u roku od 72 sata", "Obveza prijave nadzornom tijelu je na voditelju obrade."),
       ("Ne mora ništa jer trgovine nisu njezini zaposlenici", "Izvršitelj ima izravnu obvezu obavijestiti voditelja."),
       ("Obavještava kupce, a trgovine tek u završnom izvješću", "Prvo se obavještava voditelj; kupce "
                                                                 "obavještava voditelj kad je rizik visok.")],
      napomena="Vježba „Prva 72 sata” (VulnShop Cloud); Tjedan 3, P3 – GDPR čl. 28 i 33."),

    Q("I25", "CRA – proizvod kod kupca",
      "Ranjivost se aktivno iskorištava u softveru koji kupci instaliraju na svoje poslužitelje (proizvođač nema "
      "pristup tim sustavima). Tko i kome prijavljuje prema CRA-u?",
      ("Proizvođač – CSIRT-u koordinatoru i ENISA-i, uz obavijest korisnicima",
       "Obveza iz čl. 14 je na proizvođaču proizvoda s digitalnim elementima, neovisno o tome tko ga pogoni."),
      [("Svaki kupac koji je softver instalirao, i to AZOP-u u roku od 72 sata", "AZOP je nadzorno tijelo za osobne podatke, a ne za CRA."),
       ("Nitko, jer proizvođač nema pristup sustavima kupaca", "Pristup nije uvjet; obveza proizlazi iz uloge "
                                                               "proizvođača."),
       ("Proizvođač, ali tek nakon što objavi zakrpu", "Rokovi (24 h / 72 h) teku od saznanja, ne od zakrpe.")],
      napomena="Utorak 24. 11. – CRA; vježba „Prva 72 sata” (VulnShop Platform)."),
]
