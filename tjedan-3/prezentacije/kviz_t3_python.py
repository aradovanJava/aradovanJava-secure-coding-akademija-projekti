"""Dodatna pitanja za kviz Tjedna 3 – Python (FastAPI, PyJWT, pwdlib, mssql-python, pipeline). Moodle XML."""
import html
from xml.sax.saxutils import escape

def kod(t):
    return '<pre style="background:#1b1b22;color:#f2f2f2;padding:8px;border-radius:4px;font-size:90%"><code>' + html.escape(t) + '</code></pre>'

P = [
("T3-31 FastAPI – zadano zabranjeno",
 "<p>U FastAPI primjeru iz paketa <em>okviri</em> svaka ruta bez oznake <code>@javno</code> traži valjan token, iako rute nemaju nikakvu provjeru u svom kodu:</p>"
 + kod('app = FastAPI(\n    debug=False,\n    dependencies=[Depends(zadano_zabranjeno)],\n)'),
 "Kojim mehanizmom je to postignuto?",
 [("Globalnom ovisnošću koju FastAPI izvršava prije svake rute", True, "Točno – zaštita je opt-out (@javno), a ne opt-in, pa je i nova ruta zaštićena."),
  ("Parametrom korisnik: PrijavljeniKorisnik koji svaka ruta mora sama navesti", False, "To je opt-in: zaboravljeni parametar znači javnu rutu – upravo to globalna ovisnost sprječava."),
  ("Starletteovim CORSMiddlewareom s popisom dopuštenih origina", False, "CORS određuje koji JavaScript s druge stranice smije čitati odgovor; to nije autentikacija."),
  ("Postavkom debug=False", False, "debug=False samo skriva traceback u odgovoru na grešku.")],
 "Usporedite s anyRequest().authenticated() u Springu i FallbackPolicy u ASP.NET Coreu: zadano zabranjeno."),

("T3-32 PyJWT – popis algoritama",
 "<p>Provjera tokena u FastAPI primjeru:</p>" + kod('ALGORITMI = ["RS256"]\nclaims = jwt.decode(token, kljuc.key, algorithms=ALGORITMI,\n                    issuer=issuer, audience=audience)'),
 "Zašto je popis dopuštenih algoritama zadan u kodu, a ne preuzet iz zaglavlja tokena?",
 [("Da napadač ne može sam odabrati algoritam (npr. alg: none)", True, "Točno – algoritam iz zaglavlja tokena je podatak koji kontrolira napadač."),
  ("Zato što je RS256 brži od HS256 pa poslužitelj pod opterećenjem brže provjerava tokene", False, "Brzina nije razlog; razlog je da napadač ne bira način provjere."),
  ("Jer Keycloak ne izdaje drugačije tokene", False, "Keycloak podržava više algoritama; provjera ih svejedno mora ograničiti."),
  ("Da token istekne nakon pet minuta", False, "Rok valjanosti određuje claim exp, ne algoritam.")],
 "Usporedite s vlastitim JWT kodom iz T1 (Lab12), gdje je alg: none prolazio."),

("T3-33 FastAPI – odgovor 422",
 "<p>FastAPI na neispravan zahtjev zadano vraća odgovor <strong>422</strong> s popisom grešaka validacije. Primjer iz paketa <em>okviri</em> taj odgovor pretvara u <strong>400</strong> s općenitom porukom.</p>",
 "Koji je sigurnosni razlog?",
 [("HTTP 422 nije dio specifikacije pa ga preglednici ne prikazuju", False, "422 je standardni status; razlog je sadržaj odgovora."),
  ("Zadani odgovor 422 vraća i unesene vrijednosti, pa i lozinku iz tijela zahtjeva", True, "Točno – greška validacije ne smije vraćati tajne natrag klijentu (i u logove posrednika)."),
  ("Odgovor 400 automatski uključuje ograničenje broja pokušaja prijave po IP adresi klijenta", False, "Ograničenje pokušaja je zaseban mehanizam (limits)."),
  ("Status 400 sprječava napad CSRF", False, "Statusni kod nema veze s CSRF-om.")],
 "Test test_lozinke_i_prijava.py provjerava da odgovor 400 ne sadrži unesenu lozinku."),

("T3-34 pwdlib – stari hashevi",
 "<p>Korisnik čija je lozinka spremljena kao SHA-256 bez soli (iz T2) uspješno se prijavi u FastAPI primjer. Hasher je složen ovako:</p>"
 + kod('PasswordHash((Argon2Hasher(), BcryptHasher(), StariSha256()))\nispravna, novi_hash = hasher.verify_and_update(lozinka, stari)'),
 "Što se događa?",
 [("Prijava se odbija i korisnik mora resetirati lozinku", False, "Nije potrebno – stari hash se može provjeriti i zamijeniti pri prijavi."),
  ("Lozinka se privremeno sprema u čistom tekstu dok se ne napravi novi hash", False, "Lozinka se nikad ne sprema u čistom tekstu."),
  ("Provjeri se stari hash, a sprema se novi Argon2id hash", True, "Točno – kao DelegatingPasswordEncoder (Java) i SuccessRehashNeeded (.NET)."),
  ("SHA-256 se ponovno izračuna, ovaj put sa soli", False, "Novi hash koristi prvi (trenutni) algoritam u nizu – Argon2id.")],
 "Migracija hasheva bez prisilne promjene lozinki."),

("T3-35 Tajna bez zadane vrijednosti",
 "<p>Postavke FastAPI primjera:</p>" + kod('class Postavke(BaseSettings):\n    obavijesti_api_kljuc: SecretStr = Field(min_length=16)'),
 "Što se dogodi ako se aplikacija pokrene bez varijable OKVIRI_OBAVIJESTI_API_KLJUC (i bez .env datoteke)?",
 [("Aplikacija se ne pokrene – postavke se provjere pri pokretanju", True, "Točno – fail fast: bolje ne raditi nego tiho raditi s pogrešnom ili razvojnom tajnom."),
  ("Koristi se zadani razvojni ključ iz koda", False, "Polje namjerno nema zadanu vrijednost."),
  ("Aplikacija se pokrene, a ključ traži tek kod prvog slanja obavijesti", False, "Provjera je pri pokretanju, a ne kod prve uporabe."),
  ("pydantic generira nasumični ključ i zapiše ga u .env", False, "pydantic-settings samo čita postavke, ne generira tajne.")],
 "Isto u .NET primjeru: ValidateOnStart za Obavijesti:ApiKljuc."),

("T3-36 mssql-python – SESSION_CONTEXT",
 "<p>Aplikacija na početku svakog zahtjeva, nakon prijave korisnika, izvršava:</p>"
 + kod("kursor.execute(\n    \"EXEC sp_set_session_context @key = N'korisnik',\"\n    \" @value = ?, @read_only = 1\", korisnik)"),
 "Što postiže @read_only = 1?",
 [("Korisnik u toj sesiji smije samo čitati podatke, a ne i mijenjati ih", False, "To nije dozvola nad podacima – odnosi se samo na vrijednost u kontekstu."),
  ("Vrijednost se sprema u bazu i vrijedi za sve veze tog korisnika", False, "SESSION_CONTEXT vrijedi samo za tu sesiju (vezu)."),
  ("Baza odbija sve upite u toj sesiji koji nisu parametrizirani", False, "Baza ne zna je li upit parametriziran u aplikaciji."),
  ("Vrijednost se u toj sesiji više ne može promijeniti", True, "Točno – identitet za RLS ostaje onaj koji je postavila aplikacija.")],
 "Predikat RLS-a čita SESSION_CONTEXT(N'korisnik')."),

("T3-37 Demo – injekcija i RLS",
 "<p>Demo „Aplikacija i baza” nakon zadataka Z2–Z4 ispisuje:</p>"
 + kod("3. Isti unos na dva načina (sesija korisnika ana, unos: x' OR 1=1 --)\n   parametar (?) .............. 0 redaka\n   lijepljenje u tekst upita .. 2 retka  (injekcija uspijeva, ali RLS\n                                          vraća samo Anine zapise)"),
 "Koja mjera u bazi je zaslužna što i uspješna injekcija vraća samo Anine retke?",
 [("Dynamic Data Masking na stupcu OIB", False, "DDM mijenja prikaz vrijednosti, ne filtrira retke."),
  ("TDE šifriranje baze", False, "TDE štiti datoteke na disku; za korisnika baze podaci su vidljivi."),
  ("Row-Level Security s predikatom nad SESSION_CONTEXT", True, "Točno – baza filtrira retke prema prijavljenom korisniku: druga linija obrane."),
  ("Revizija SELECT naredbi u database audit specifikaciji", False, "Revizija bilježi pristup, ali ga ne ograničava.")],
 "Prva linija obrane je parametrizirani upit; RLS i minimalna prava ograničavaju štetu kad ona zakaže."),

("T3-38 Pipeline – Python regresija",
 "<p>U Python projektu netko vrati <code>PyYAML==5.3.1</code> u <code>requirements.txt</code> i <code>yaml.load(tijelo, Loader=yaml.FullLoader)</code> u kod te otvori pull request.</p>",
 "Što u predlošku DevSecOps cjevovoda sigurno blokira spajanje?",
 [("Bandit, jer pravilo B506 uvijek blokira", False, "Bandit ocjenjuje B506 kao MEDIUM, pa je u ovoj politici samo informativan."),
  ("gitleaks, jer je promijenjena datoteka s ovisnostima", False, "gitleaks traži tajne, ne ranjive ovisnosti."),
  ("SCA: OSV-Scanner i pip-audit (poznata ranjivost)", True, "Točno – PyYAML 5.3.1 ima ranjivost CVSS 9,8, a pravilo python-yaml-load-bez-safeloader hvata kod."),
  ("Ništa – sigurnosna vrata u predlošku postoje samo za Java i .NET projekte", False, "Predložak devsecops/python ima ista vrata kao Java i .NET.")],
 "Zato vrata ne smiju biti „samo upozorenje”."),
]

out = ['<?xml version="1.0" encoding="UTF-8"?>', "<quiz>"]
for naziv, uvod, pitanje, odgovori, opce in P:
    tekst = uvod + "<p><strong>" + escape(pitanje) + "</strong></p>"
    out.append('<question type="multichoice">')
    out.append(f"<name><text>{escape(naziv)}</text></name>")
    out.append(f'<questiontext format="html"><text><![CDATA[{tekst}]]></text></questiontext>')
    out.append(f'<generalfeedback format="html"><text><![CDATA[<p>{escape(opce)}</p>]]></text></generalfeedback>')
    out.append("<defaultgrade>1.0000000</defaultgrade><penalty>0.3333333</penalty><hidden>0</hidden>")
    out.append("<single>true</single><shuffleanswers>true</shuffleanswers><answernumbering>abc</answernumbering><showstandardinstruction>0</showstandardinstruction>")
    out.append('<correctfeedback format="html"><text>Točno.</text></correctfeedback>')
    out.append('<partiallycorrectfeedback format="html"><text></text></partiallycorrectfeedback>')
    out.append('<incorrectfeedback format="html"><text>Netočno.</text></incorrectfeedback>')
    for odg, tocan, fb in odgovori:
        out.append(f'<answer fraction="{100 if tocan else 0}" format="html"><text><![CDATA[{escape(odg)}]]></text>'
                   f'<feedback format="html"><text><![CDATA[{escape(fb)}]]></text></feedback></answer>')
    out.append("</question>")
out.append("</quiz>")
xml = "\n".join(out)
open("T3-kviz-python.xml", "w", encoding="utf-8").write(xml)
# provjera: točan odgovor nije uvijek najdulji
najdulji = sum(1 for _, _, _, o, _ in P if max(o, key=lambda x: len(x[0]))[1])
print("pitanja:", len(P), "| točan je najdulji u:", najdulji, "| bajtova:", len(xml.encode()))
