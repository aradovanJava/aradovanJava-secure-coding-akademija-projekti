"""Bilješke govornika – T3 P2: Sigurnost baza podataka (Dan 2)."""

BILJESKE = {
1: """
DAN 2 · okvirni tijek (prilagodite trajanju termina)
• Predavanje s demonstracijom C – oko 1 h 45 min, stanka nakon poglavlja 4 (Enkripcija).
• Zatim laboratorij u dvorani – oko 1 h: svaki polaznik pokreće vlastiti SQL Server, pokreće automatsku provjeru i demo „Aplikacija i baza” te započinje zadatke Z1 i Z2. Cilj: nitko ne odlazi kući s okruženjem koje ne radi.

PRIJE POČETKA
• Vaš SQL Server iz paketa „Sigurnost baza podataka” pokrenut (docker compose up -d), init gotov, demo slike već izgrađene (docker compose --profile aplikacija build) – README.md paketa, odjeljak 6; „ciljano stanje” za korak 6 prema DEMO-PREDAVAC.md (samo izlaz, ne skripta).
• VS Code s ekstenzijom SQL Server (mssql) ili SSMS spojen na localhost,1433.
• Na početku pitajte tko je sinoć preuzeo sliku SQL Servera (~1,5 GB). Tko nije, neka pokrene docker pull odmah, dok slušaju predavanje.

UVODNA REČENICA
„Jučer smo zaštitili aplikaciju. Danas pretpostavljamo da je aplikacija ipak probijena – SQL injection, ukradena lozinka ili nepažljiv djelatnik – i gledamo koliko štete baza još može spriječiti.”
""",
2: """
⏱ ~2 min

Predavanje prati skup ishoda učenja „Sigurnost baza podataka” iz programa (1 CSVET) – ishodi su desno, gotovo doslovno iz programa. U završnoj rubrici to su elementi E8 (prijetnje bazi) i E9 (mehanizmi zaštite podataka u bazi).

Osam poglavlja odgovara zadacima laboratorija: prijetnje (Z1), prijave i korisnici (Z2), minimalne privilegije, RLS i maskiranje (Z3, Z4), enkripcija (Z5), revizija (Z6), sigurnosne kopije (Z7), učvršćivanje (Z8) – i na kraju aplikacija i sam laboratorij.

Laboratorij: svaki polaznik u Dockeru pokreće VLASTITI SQL Server 2022 s namjerno loše podešenom bazom SVOJE domene iz 2. tjedna (MedTermin, Ulaznica ili Kadrovska). Automatska provjera ima 30 provjera; početno stanje: sve PALO.

Mjesto u tjednu: sutra (Dan 3) radionica – ispitivanje sigurnosti, rizik i usklađenost; model prijetnji koji tada radimo uključuje i bazu.
""",
3: """
⏱ ~1 min · prijelaz

Baza je mjesto gdje su podaci – i zato gotovo uvijek krajnji cilj napada. Napadač rijetko „napada SQL Server” izravno; dolazi kroz aplikaciju, kroz ukradenu lozinku ili kroz kopiju koja je ostala na pogrešnom mjestu.
""",
4: """
⏱ ~5 min

Šest najčešćih prijetnji – za svaku pitajte polaznike je li postojala u njihovom T2 projektu:
• SQL injection: ulaz iz aplikacije postaje naredba. ŠTETA OVISI O OVLASTIMA aplikacijskog korisnika – to je glavna poruka cijelog predavanja. S08 (SQLi u sortiranju) s korisnikom koji smije samo čitati jednu tablicu je neugodnost; isti propust s korisnikom sysadmin je kompromitirani poslužitelj.
• Prekomjerne ovlasti: aplikacija kao sysadmin ili db_owner, podrška koja čita sve tablice „jer je lakše”.
• Slabe i dijeljene prijave: sa za sve, lozinke bez politike, lozinka u application.properties u repozitoriju.
• Nešifrirani podaci: OIB, zdravstveni i financijski podaci u čistom tekstu – i kopije bez enkripcije.
• Insajder: zlouporaba legitimnog pristupa. Bez revizije se ne može ni otkriti ni dokazati.
• Izloženost: port 1433 dostupan s interneta (pretraživači poput Shodana pronalaze stotine tisuća takvih poslužitelja), xp_cmdshell, nezakrpana instanca.

Most prema laboratoriju: točno ovakvo je početno stanje vaše baze. U zadatku Z1 prijetnje morate pronaći UPITIMA nad katalogom, ne čitanjem skripti – i za svaku opisati scenarij napada.
""",
5: """
⏱ ~4 min

Obrana u dubinu, sloj po sloj – svaki sloj pretpostavlja da prethodni može zakazati:
• Aplikacija: parametrizirani upiti i autorizacija (jučer).
• Mreža: baza sluša samo na 127.0.0.1 ili u privatnoj mreži, promet je šifriran (TLS). U laboratoriju: port je vezan na 127.0.0.1.
• Autentikacija: jake, zasebne prijave; sa onemogućen.
• Autorizacija: vlastite uloge s minimalnim pravima, RLS za retke, DDM za prikaz.
• Enkripcija: TDE za datoteke i kopije, enkripcija stupca za OIB.
• Revizija: tko se prijavio, tko je čitao osjetljive tablice, tko je mijenjao prava.
• Oporavak: šifrirane kopije i probni restore.

Primjer koji ćete danas vidjeti u demonstraciji: isti SQL injection prije i poslije mjera. Prije – vraća sve zapise; poslije – i dalje „uspije”, ali vraća samo retke prijavljene korisnice, jer RLS filtrira na razini baze.
""",
6: """
⏱ ~1 min · prijelaz

Prvi sloj u bazi: tko se uopće može spojiti na poslužitelj, tko postoji u bazi i što smije. U laboratoriju zadatak Z2.
""",
7: """
⏱ ~4 min

Dvije razine principala – najčešća zabuna polaznika:
• Server (instanca): PRIJAVA (login) – SQL prijava s lozinkom ili Windows / Microsoft Entra ID; serverske uloge (sysadmin, securityadmin…). sa je ugrađeni administrator – svaki napadač zna njegovo ime, pa ga nakon stvaranja vlastite administratorske prijave onemogućujemo.
• Baza: KORISNIK (user) povezan s prijavom (CREATE USER … FOR LOGIN …); uloge baze – fiksne (db_owner, db_datareader…) i vlastite (uloga_aplikacija); sheme kao granica dozvola (npr. GRANT EXECUTE ON SCHEMA::api).
• guest: u korisničkim bazama ne smije imati CONNECT – inače svaka prijava na poslužitelju ulazi u bazu.

Usporedba za programere: prijava je „račun na poslužitelju”, korisnik je „članstvo u pojedinoj bazi”.

U produkciji alternativa SQL prijavama: Microsoft Entra ID autentikacija ili managed identity – bez lozinke u konfiguraciji aplikacije. U laboratoriju koristimo SQL prijave jer rade u Dockeru bez domene.
""",
8: """
⏱ ~5 min

Kod lijevo – redom:
• Aplikacijska prijava s CHECK_POLICY = ON (na Linuxu provjerava složenost lozinke; Windows politika zaključavanja i povijesti lozinki ovdje nije dostupna).
• Korisnik u bazi povezan s prijavom.
• Vlastita administratorska prijava → član sysadmin → TEK ONDA ALTER LOGIN sa DISABLE. Obrnut redoslijed znači da ste se zaključali izvan poslužitelja.
• REVOKE CONNECT FROM guest u korisničkoj bazi.

Važno za laboratorij (zadatak Z2.4): kad onemogućite sa, u .env upišite ADMIN_LOGIN i ADMIN_PASSWORD i ponovno docker compose up -d – healthcheck, init i provjera tada koriste vašu prijavu. Ako to preskočite, kontejner postaje unhealthy (i u reviziji vidite neuspjele prijave sa svakih 10 sekundi).

Desno: provjere stanja upitima nad katalogom – isto se traži u Z1. Pokažite jedan upit uživo, npr. tko je član sysadmin (README paketa, odjeljak 6, korak 3).

Lozinke ne pišemo u skripte koje idu u Git: u laboratoriju sqlcmd varijable (-v LOZINKA=…) ili ručni unos.
""",
9: """
⏱ ~1 min · prijelaz

Najvažnije poglavlje danas. Ako zapamtite jednu stvar: aplikacija smije točno ono što joj treba – ni retka više. Svako pravo koje aplikacija ima, ima i napadač koji je pronašao SQL injection.
""",
10: """
⏱ ~6 min

Lijevo: vlastita uloga uloga_aplikacija s dozvolama na konkretne tablice – onoliko koliko aplikacija iz T2 stvarno radi (pogledajte njezine upite: registracija, prijava, reset lozinke, popisi, stvaranje i brisanje glavnog zapisa, uvoz). Još bolje: samo EXECUTE na shemu api s pohranjenim procedurama – aplikacija tada uopće ne vidi tablice.

Provjera: EXECUTE AS USER = 'aplikacija' … REVERT – izvršavate upite pod identitetom aplikacije i vidite ono što ona vidi. HAS_PERMS_BY_NAME i sys.fn_my_permissions vraćaju učinkovita prava (s ulogama i nasljeđivanjem).

Tablica desno: zašto fiksne uloge nisu za aplikaciju. db_datareader čita SVE – i tablicu s hashevima lozinki; db_owner smije DROP i dodjelu prava.

DENY ima prednost pred GRANT – korisno kad uloga daje previše, ali radije ne dajte previše.

Okvir dolje: veza s projektom. SQL injection kroz sortiranje (S08) s ovako ograničenim korisnikom NE MOŽE pročitati tablicu korisnici. Pitanje za razmišljanje iz ZADACI.md: zašto okidač i dalje može pisati u dbo.revizija iako aplikacija na nju nema nikakvo pravo? (Ownership chaining – okidač i tablica imaju istog vlasnika.)
""",
11: """
⏱ ~7 min

Row-Level Security filtrira retke prema predikatu – inline funkciji WITH SCHEMABINDING (najbolje u zasebnoj shemi, npr. sigurnost).
• Predikat uspoređuje vlasnika retka (pacijent) sa SESSION_CONTEXT(N'korisnik'); administratori aplikacije vide sve.
• FILTER predikat: SELECT, UPDATE i DELETE ne vide tuđe retke. BLOCK predikat AFTER INSERT: aplikacija ne može upisati redak u tuđe ime.

Desno: aplikacija na početku svakog zahtjeva, nakon što zna tko je prijavljen, postavlja SESSION_CONTEXT. S @read_only = 1 vrijednost se u toj sesiji više ne može promijeniti – ni kasnijim kodom ni SQL injectionom.

Ključna poruka: i ako u kodu izostane provjera vlasništva (IDOR, S01), baza ne vraća tuđe retke. To je druga linija obrane – NE zamjena za autorizaciju u aplikaciji.

Ograničenja (okvir dolje): predikat se izvršava za svaki redak, pa mora biti jednostavan i indeksiran. Korisnik koji smije slati proizvoljne upite može ponekad zaključivati o skrivenim retcima preko grešaka (side-channel) – RLS je kontrola za aplikacijski pristup, ne za ad hoc korisnike s pravom pisanja upita.

Laboratorij: Z4.1 i Z4.2 (provjera postavlja kontekst 'ana', 'marko', bez konteksta i ADMIN).
""",
12: """
⏱ ~5 min

Dynamic Data Masking skriva vrijednost u REZULTATU upita korisnicima bez dozvole UNMASK. Primjer: partial(0,"*******",4) za OIB pokazuje samo zadnje četiri znamenke; email() pokazuje samo prvo slovo adrese, a ostatak zamjenjuje stalnim nizom XXX@XXXX.com (ni domena se ne vidi).

Tablica u sredini: ista tablica, dva korisnika – podrška vidi maskirano, administrator s UNMASK pravu vrijednost. SQL Server 2022 podržava granularni UNMASK (na razini sheme, tablice ili stupca).

Kad koristiti: podrška i izvještavanje koji ne trebaju puni podatak, UZ minimalne dozvole i reviziju.

Ograničenja – recite izričito, to je čest ispitni odgovor:
• DDM NIJE enkripcija – podatak je u čistom tekstu na disku i u kopijama;
• nije granica sigurnosti: ciljanim upitima (WHERE oib LIKE '1%', pa '12%' …) vrijednost se može zaključiti znak po znak;
• zato podrška dobiva SELECT samo na popis stupaca – bez password_hash (Z4.5).

Pitanje iz ZADACI.md: zašto DDM nije zamjena za šifriranje ni za kontrolu pristupa?
""",
13: """
⏱ ~1 min · prijelaz

Enkripcija na tri mjesta: u prijenosu (TLS), na disku (TDE) i u stupcu (ENCRYPTBYKEY). I jedno pravilo koje vrijedi za sve tri: izgubljeni ključ = izgubljeni podaci. Upravljanje ključevima je pola posla.
""",
14: """
⏱ ~5 min

Tablica je odgovor na pitanje „od čega što štiti”:
• TLS (Encrypt=true): promet aplikacija ↔ baza. U novijim upravljačkim programima (Microsoft JDBC 10.2+, Microsoft.Data.SqlClient 4.0+) Encrypt je zadano uključen. TrustServerCertificate smije biti uključen samo u laboratoriju – u produkciji certifikat kojem klijent vjeruje.
• TDE: datoteke baze, log i kopije na disku – štiti od krađe diska ili kopije. NE štiti od korisnika koji ima pristup bazi (pa ni od SQL injectiona).
• Enkripcija stupca: osjetljivi stupac je šifriran i za korisnika koji čita tablicu, ali nema pravo na ključ. Ne štiti od administratora koji ima ključ.
• Always Encrypted: šifrira se na KLIJENTU – poslužitelj (i njegov administrator) nikad ne vidi čisti tekst. Cijena: ograničeni upiti nad šifriranim stupcem. U laboratoriju samo kao demonstracija.
• Enkripcija kopija: kopije izvan poslužitelja.

Hijerarhija ključeva (dolje): Service Master Key → Database Master Key → certifikat → DEK (TDE) ili simetrični ključ. Pitanje: što se događa s kopijom TDE baze ako izgubite certifikat? (Ne može se vratiti nigdje – ni na isti poslužitelj nakon reinstalacije.)
""",
15: """
⏱ ~4 min

Redoslijed naredbi je ujedno i postupak:
1. U master: master key i certifikat.
2. ODMAH sigurnosna kopija certifikata S PRIVATNIM KLJUČEM (.cer + .pvk, lozinka za ključ). U laboratoriju u ./backup – provjera Z5.2 to traži. U stvarnosti: odvojeno od kopija baze, u trezoru.
3. U bazi: ključ za šifriranje baze (DEK) zaštićen certifikatom poslužitelja.
4. SET ENCRYPTION ON – šifriranje teče u pozadini; encryption_state = 3 znači gotovo (Z5.1).

Napomene: TDE je od SQL Servera 2019 dostupan i u Standard izdanju; Developer izdanje u laboratoriju ima sve značajke, ali nije licencirano za produkciju. Kad je jedna baza na instanci šifrirana TDE-om, šifrira se i tempdb.

Pitanja iz ZADACI.md za raspravu: od čega TDE štiti, a od čega ne? Gdje biste u stvarnosti čuvali .pvk i lozinku?
""",
16: """
⏱ ~5 min

Enkripcija stupca simetričnim ključem zaštićenim certifikatom (Z5.3, Z5.4):
• master key u bazi → certifikat → AES_256 simetrični ključ;
• novi stupac oib_sifrirano VARBINARY(256); OPEN SYMMETRIC KEY → UPDATE s ENCRYPTBYKEY → CLOSE → stari stupac oib uklonjen.
• Čitanje: OPEN SYMMETRIC KEY … DECRYPTBYKEY (ili DECRYPTBYKEYAUTOCERT bez eksplicitnog otvaranja). Korisnik bez prava na ključ i certifikat vidi samo binarni zapis.

Dvije napomene iz prakse (okvir dolje):
• Dozvole na ključ i certifikat (VIEW DEFINITION / CONTROL) daju se samo ulozi koja smije čitati podatak – tako enkripcija postaje i kontrola pristupa.
• Po šifriranom stupcu se ne može pretraživati (svaka enkripcija daje drugačiji zapis). Rješenje je zaseban HMAC stupac (hash s tajnim ključem) za traženje po jednakosti.

Za MedTermin je primjer OIB u rezervacijama; u Ulaznici i Kadrovskoj isti postupak na glavnoj tablici vaše domene. OIB u dbo.korisnici ostaje, ali maskiran (Z4).
""",
17: """
⏱ ~1 min · prijelaz

Revizija: ako se ne bilježi, ne može se ni otkriti ni dokazati. Veza s jučerašnjim A09 (Security Logging and Alerting Failures) – samo sada na razini baze, gdje revizija vidi i ono što aplikacija ne vidi (npr. administratora koji ručno čita tablicu).
""",
18: """
⏱ ~6 min

SQL Server Audit u tri koraka:
1. SERVER AUDIT – kamo se zapisuje: datoteka (na Linuxu mapa koju odredimo; u laboratoriju /var/opt/mssql/audit, na vašem računalu ./audit). ON_FAILURE = CONTINUE: ako zapisivanje ne uspije, baza radi dalje; SHUTDOWN bi zaustavio poslužitelj – za strože okoline (pitanje dostupnosti protiv dokaza).
2. SERVER AUDIT SPECIFICATION – prijave: FAILED_LOGIN_GROUP i SUCCESSFUL_LOGIN_GROUP (Z6.2).
3. DATABASE AUDIT SPECIFICATION – SELECT nad osjetljivim tablicama i promjene prava i članstva u ulogama (Z6.3, Z6.4).
Čitanje: sys.fn_get_audit_file; action_id 'SL' je SELECT, 'LGIF' neuspjela prijava.

Savjet za laboratorij: reviziju uključite NA POČETKU – tada bilježi i sve vaše promjene prava.

Dvije realnosti koje vide odmah: healthcheck kontejnera prijavljuje se svakih 10 sekundi, pa revizija bez filtriranja brzo raste; i: zapis koji nitko ne čita nije kontrola – u produkciji zapisi idu u SIEM s alarmima (npr. neuspjele prijave za sa, SELECT nad nalazima izvan radnog vremena).

Za zainteresirane: SQL Server 2022 ima i ledger tablice – dokaz da podaci nisu naknadno izmijenjeni.
""",
19: """
⏱ ~1 min · prijelaz

Kopija koja nije provjerena vraćanjem nije kopija – nego nada. Ransomware danas najprije traži i šifrira ili briše kopije, pa tek onda produkcijske podatke.
""",
20: """
⏱ ~5 min

Kod lijevo (Z7.1–Z7.4):
• certifikat za šifriranje kopija (može biti odvojen od TDE certifikata – i njega kopirajte s privatnim ključem);
• BACKUP … WITH CHECKSUM, COMPRESSION, ENCRYPTION (AES_256);
• RESTORE VERIFYONLY … WITH CHECKSUM – provjera da je kopija čitljiva;
• probni restore pod drugim imenom (<Baza>_ProbniRestore) uz WITH MOVE – tek to dokazuje da se iz kopije stvarno može vratiti. Logička imena datoteka dobijete s RESTORE FILELISTONLY.

Pravila desno:
• 3-2-1: tri kopije, dva medija, jedna izvan lokacije – i danas barem jedna nepromjenjiva ili offline (zbog ransomwarea);
• kopije uvijek šifrirane (sadrže SVE podatke), certifikat čuvan odvojeno;
• redovan probni restore s mjerenjem vremena;
• RPO (koliko podataka smijemo izgubiti) i RTO (koliko dugo smijemo biti bez sustava) određuju učestalost punih, diferencijalnih i log kopija.

Pitanje iz ZADACI.md: što još nedostaje vašoj „strategiji” od jedne pune kopije? (Diferencijalne i log kopije, kopija izvan poslužitelja, dokumentirani RPO/RTO.)
""",
21: """
⏱ ~1 min · prijelaz

Zadnje poglavlje predavanja: manja površina napada na samoj instanci (Z8) i ispravna veza iz aplikacije – kako aplikacija iz 2. tjedna koristi sve što smo danas napravili.
""",
22: """
⏱ ~5 min

Kontrolna lista za instancu – brzo kroz osam stavki, s naglaskom na prve dvije:
1. Opasne opcije isključene: CLR, Ad Hoc Distributed Queries, cross db ownership chaining – i xp_cmdshell, koji na Windowsu izvršava naredbe operacijskog sustava (preko SQL injectiona = udaljeno izvršavanje koda). Na Linuxu xp_cmdshell nije podržan pa ga zatečeno stanje nije uspjelo uključiti – u skripti ga ipak isključite unutar TRY/CATCH da radi na obje platforme.
2. TRUSTWORTHY OFF: TRUSTWORTHY ON uz db_owner i vlasnika baze sa omogućuje eskalaciju od vlasnika baze do sysadmina – klasična kombinacija koju Z1 traži da prepoznate.
3. guest bez CONNECT.
4. sa onemogućen.
5. Port samo lokalno ili u privatnoj mreži, vatrozid.
6. TLS i Encrypt=true, bez TrustServerCertificate u produkciji.
7. Ažurna instanca – kumulativna ažuriranja (CU) redovito.
8. Politika lozinki – CHECK_POLICY = ON.

Ovo su provjere Z8.1–Z8.3 i dio Z2; ostatak je ono što bi revizor pitao za produkcijski poslužitelj.
""",
23: """
⏱ ~4 min

Kako aplikacija iz T2 koristi sve ovo (Java i C#; Python na sljedećem slajdu):
• Spaja se kao korisnik s minimalnim pravima (medtermin_app, član uloga_aplikacija) – nikad sa.
• U konfiguraciji NEMA lozinke: Spring čita SPRING_DATASOURCE_PASSWORD iz okruženja; .NET user-secrets ili varijablu okruženja.
• encrypt=true / Encrypt=True – u novijim upravljačkim programima zadano.
• Na početku svakog zahtjeva, nakon što zna tko je prijavljen, postavlja SESSION_CONTEXT – kao PARAMETAR, nikad lijepljenjem u tekst.

Napomena za one koji koriste pool veza (svi): kontekst postavljajte na početku SVAKOG zahtjeva, ne jednom po vezi – veza iz poola prethodno je služila drugom korisniku.

Bonus u zadatku Z3: pokrenite svoju T2 aplikaciju nad ovom bazom s ovim korisnikom – ako nešto pukne, uloga je preuska (ili aplikacija radi nešto što ne biste očekivali).
""",
24: """
⏱ ~4 min · NOVO: Python i demo · zatim DEMONSTRACIJA C (~25 min)

Lijevo: isto u Pythonu s Microsoftovim službenim upravljačkim programom mssql-python (pip install mssql-python; ne treba zaseban ODBC driver):
• lozinka iz okruženja (os.environ), nikad u kodu;
• Encrypt=yes;
• lozinka u vitičastim zagradama u nizu za spajanje – smije sadržavati ; i = bez lomljenja niza;
• sp_set_session_context s parametrom (?) i @read_only = 1; svi upiti s parametrima.

Desno: demo „Aplikacija i baza” iz paketa (mapa aplikacija/, README odjeljak 5) – isti program u Pythonu, Javi i C#-u (aplikacija-python, aplikacija-java, aplikacija-dotnet) spaja se kao aplikacija i ispisuje što aplikacijski račun SMIJE. Ispis na slajdu je stvarni ispis za MedTermin u početnom stanju: 12 upozorenja.

DEMONSTRACIJA C – README paketa, odjeljak 6 (za predavača i DEMO-PREDAVAC.md):
1. docker compose --profile provjera run --rm provjera → sve PALO.
2. docker compose --profile aplikacija run --rm aplikacija-python → sysadmin, db_owner, CREATE TABLE, injekcija vraća tuđe zapise, podrška vidi OIB i hasheve.
3. Katalog: tko je sysadmin, TRUSTWORTHY.
4. EXECUTE AS USER … sys.fn_my_permissions.
5. Jedna mjera uživo: ALTER SERVER ROLE sysadmin DROP MEMBER [medtermin_app]; pa ponovno korak 2 – jedno upozorenje manje, Z2.2 PROŠLO.
6. Ciljano stanje (pripremljeno unaprijed – pokažite samo ISPIS, ne skriptu): Upozorenja: 0; parametar 0 redaka, a I USPJEŠNA INJEKCIJA vraća samo Anine retke.
Pitanje za raspravu: „Ako je SQL injection uspio, što je napadač dobio?”
""",
25: """
⏱ ~1 min · prijelaz u laboratorij

Sada radite vi. Svatko pokreće vlastiti SQL Server s bazom SVOJE domene iz 2. tjedna – DOMENA u .env mora odgovarati projektu (MedTermin: V01–V03, Ulaznica: V06–V07, Kadrovska: V11–V12). Cilj za danas u dvorani: okruženje radi, provjera i demo se pokreću, Z1 započet. Ostalo je u danima 4–5 (rok 22. 11. u 23:59).
""",
26: """
⏱ ~5 min objašnjavanja, zatim laboratorij (~1 h)

Naredbe lijevo – zajedno, korak po korak:
1. cp .env.primjer .env (PowerShell: Copy-Item) – postaviti DOMENA i jaku lozinku za sa (bez $, navodnika i razmaka; inače se SQL Server ne pokrene).
2. docker compose up -d i docker compose logs -f init – čekati „Gotovo: baza … je spremna”.
3. Provjera – očekivano sve PALO.
4. Demo aplikacije – očekivano desetak upozorenja (u Javi i C#-u prvi put traje duže zbog ovisnosti).
5. Spajanje iz VS Codea (SQL Server ekstenzija) ili SSMS-a na localhost,1433 s Trust server certificate.

Najčešći problemi u dvorani (README, odjeljak „Česti problemi”):
• slaba lozinka za sa → kontejner se odmah zaustavi; jača lozinka, docker compose down -v, up -d;
• Apple Silicon bez Rosette → SQL Server se ruši;
• port 1433 zauzet (lokalni SQL Server) → SQL_PORT=14333;
• Windows: paket u mapi bez razmaka ili u WSL-u; $'\\r' greška = skripte spremljene s Windows prijelomima redaka – ponovno raspakirati ZIP.

Okviri dolje: nakon što onemogućite sa – ADMIN_LOGIN/ADMIN_PASSWORD u .env i ponovno up -d; nakon Z2.1 – APP_LOZINKA u .env za demo.

Predaja (ZIP Vxx-Ime-Prezime-T3.zip, mapa baza/): vaša T-SQL skripta bez lozinki, izlaz provjere i analiza prijetnji Z1. Prolazite dvoranu: tko ima zeleno okruženje, pomaže susjedu.
""",
27: """
⏱ ~3 min · zaključak dana

Sažetak:
• Baza je druga linija obrane: minimalne ovlasti i RLS ograničavaju štetu i kad aplikacija zakaže.
• Enkripcija bez upravljanja ključevima je lažna sigurnost – certifikat s privatnim ključem kopirajte odmah.
• Revizija i provjerene kopije su dokazi – za incident i za usklađenost (GDPR čl. 32, NIS2).

Sutra (Dan 3): radionica „ispitivanje sigurnosti, rizik i usklađenost” na vašim repozitorijima – donesite projekt na GitHubu (sa sinoćnjim pipelineom, ako ste stigli), ASVS listu iz 2. tjedna i okruženje baze koje radi.

Podsjetnik: kviz Tjedna 3 je otvoren, neograničen broj pokušaja.
""",
}
