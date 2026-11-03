#!/usr/bin/env python3
"""Savjeti za polaznike (Moodle stranice) – po varijanti, dvije razine.

  python3 tools/savjeti.py --out dist/savjeti      # za svaku varijantu Vxx-razina-1.html i Vxx-razina-2.html

Razina 1: u kojim su kategorijama OWASP Top 10:2025 i kojim dijelovima aplikacije ranjivosti (bez detalja).
Razina 2: konkretan smjer za svaku ranjivost (što isprobati, gdje gledati, kakva je obrana) – bez gotovog koda.
"""
import argparse, html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

D = {
    "medtermin": dict(zapis="rezervaciju pregleda", zapisa="rezervacije", del_ep="DELETE /api/rezervacije/{id}",
                      dok="nalaz", dok_mn="nalaza", dok_ep="/api/nalazi", uvoz="uvoz rasporeda termina",
                      uvoz_ep="POST /api/termini/uvoz", popis="liječnika", popis_ep="GET /api/lijecnici",
                      ispis="potvrdi rezervacije", ispis_ep="GET /ispis/rezervacije/{id}", polje="napomena",
                      resurs="isti slobodni termin", resurs_ep="POST /api/rezervacije", stvori="rezerviraj pregled",
                      tudi_dok="tuđi nalaz"),
    "ulaznica": dict(zapis="narudžbu", zapisa="narudžbe", del_ep="DELETE /api/narudzbe/{id}",
                     dok="račun", dok_mn="računa", dok_ep="/api/racuni", uvoz="uvoz događaja",
                     uvoz_ep="POST /api/dogadjaji/uvoz", popis="događaja", popis_ep="GET /api/dogadjaji",
                     ispis="ulaznici za ispis", ispis_ep="GET /ispis/narudzbe/{id}", polje="imeNaUlaznici",
                     resurs="zadnju ulaznicu za isti događaj", resurs_ep="POST /api/narudzbe", stvori="kupi ulaznicu",
                     tudi_dok="tuđi račun"),
    "kadrovska": dict(zapis="zahtjev za godišnji odmor", zapisa="zahtjeva", del_ep="DELETE /api/zahtjevi/{id}",
                      dok="platnu listu", dok_mn="platnih lista", dok_ep="/api/platne-liste", uvoz="uvoz edukacija",
                      uvoz_ep="POST /api/edukacije/uvoz", popis="zaposlenika", popis_ep="GET /api/zaposlenici",
                      ispis="potvrdi zahtjeva", ispis_ep="GET /ispis/zahtjevi/{id}", polje="razlog",
                      resurs="zadnje mjesto na istoj edukaciji", resurs_ep="POST /api/edukacije/{id}/prijava",
                      stvori="podnesi zahtjev za godišnji",
                      tudi_dok="tuđu platnu listu"),
}

CAT = {"S01": "A01 Broken Access Control", "S02": "A01 Broken Access Control", "S03": "A01 Broken Access Control",
       "S04": "A02 Security Misconfiguration", "S05": "A02 Security Misconfiguration",
       "S06": "A03 Software Supply Chain Failures", "S07": "A04 Cryptographic Failures",
       "S08": "A05 Injection", "S09": "A05 Injection", "S10": "A06 Insecure Design",
       "S11": "A07 Authentication Failures", "S12": "A09 Security Logging and Alerting Failures",
       "S13": "A10 Mishandling of Exceptional Conditions"}

R1 = {
    "S01": "Brisanje zapisa ({del_ep}) – tko smije obrisati koji zapis?",
    "S02": "Preuzimanje datoteke ({dok_ep}/preuzmi) – kako se iz parametra dolazi do putanje na disku?",
    "S03": "Web prijava (/prijava) – kamo aplikacija šalje korisnika nakon uspješne prijave?",
    "S04": "Odgovori API-ja na zahtjeve koji dolaze s drugih web stranica (zaglavlje Origin).",
    "S05": "{uvoz_cap} ({uvoz_ep}) – kako je konfiguriran XML parser?",
    "S06": "Biblioteke trećih strana – pokreni SCA alat i pogledaj čime se obrađuju korisničke postavke.",
    "S07": "Pohrana lozinaka u bazi (tablica korisnici).",
    "S08": "Sortiranje popisa {popis} ({popis_ep}?sort=…&smjer=…).",
    "S09": "HTML stranica za ispis ({ispis_ep}).",
    "S10": "Istodobni zahtjevi za {resurs} ({resurs_ep}).",
    "S11": "Obnova zaboravljene lozinke – kako nastaje token koji stiže e-poštom (data/posta)?",
    "S12": "Sadržaj loga kod prijave i kod stvaranja {zapisa}.",
    "S13": "Dohvat {dok_mn} u različitim formatima ({dok_ep}/{{id}}?format=…).",
}
R2 = {
    "S01": "Prijavi se kao <code>marko</code> i pozovi <code>{del_ep}</code> s ID-em zapisa koji pripada korisniku "
           "<code>ana</code>. Što se dogodi? Provjera vlasnika mora biti na poslužitelju; za tuđi zapis vrati odgovor "
           "kao da zapis ne postoji (404) i ništa ne briši.",
    "S02": "Parametar <code>datoteka</code> spaja se s mapom za pohranu. Što ako ime sadrži <code>../</code>? Kako se "
           "provjerava je li datoteka tvoja – može li se ta provjera zadovoljiti imenom koje samo <em>sadrži</em> tvoje "
           "korisničko ime? Sigurno: datoteku odredi preko zapisa u bazi i provjeri da normalizirana putanja ostaje "
           "unutar mape za pohranu.",
    "S03": "Pošalji obrazac prijave s <code>returnUrl=https://primjer.example</code> (i varijante <code>//primjer.example</code>, "
           "<code>/\\primjer.example</code>) bez praćenja preusmjeravanja i pogledaj zaglavlje <code>Location</code>. "
           "Dopusti samo lokalne putanje (jedan početni <code>/</code>), a sve ostalo preusmjeri na <code>/</code>.",
    "S04": "Pošalji <code>GET /api/ja</code> i <code>OPTIONS /api/ja</code> sa zaglavljem <code>Origin: https://primjer.example</code>. "
           "Što je u <code>Access-Control-Allow-Origin</code> i <code>Access-Control-Allow-Credentials</code>? "
           "Dopušteni origini trebaju doći iz konfiguracije (ključ <code>cors.allowed-origins</code> / <code>Cors:AllowedOrigins</code> / "
           "<code>cors_allowed_origins</code> u Pythonu).",
    "S05": "Parser obrađuje <code>DOCTYPE</code> deklaracije. Što ako uvezeni dokument definira entitet koji upućuje na "
           "lokalnu datoteku, a ta se vrijednost vraća u odgovoru uvoza? Isključi DTD/vanjske entitete u postavkama parsera "
           "i odbij takav dokument (400).",
    "S06": "Biblioteka kojom se parsira YAML u <code>POST /api/postavke</code> ima javno objavljenu ranjivost (CVE/GHSA). "
           "Nadogradi je na sigurnu verziju i provjeri treba li promijeniti i način korištenja (siguran konstruktor / sigurno "
           "učitavanje / deserijalizacija samo u jednostavne tipove). Ponovno pokreni SCA alat.",
    "S07": "Registriraj dva korisnika s istom lozinkom i usporedi <code>password_hash</code> u bazi. Jesu li isti? "
           "Brza hash funkcija bez soli nije prikladna za lozinke – koristi bcrypt, PBKDF2 ili Argon2 (i za početne korisnike).",
    "S08": "Parametri <code>sort</code> i <code>smjer</code> ugrađuju se u <code>ORDER BY</code>. Isprobaj vrijednost koja "
           "nije ime stupca (npr. izraz u zagradama). Ime stupca ne može biti parametar upita – koristi popis dopuštenih "
           "vrijednosti i za sve ostalo vrati 400.",
    "S09": "Polje <code>{polje}</code> prikazuje se na stranici <code>{ispis_ep}</code>. Spremi tekst s HTML oznakama i otvori "
           "stranicu u pregledniku. Kodiraj izlaz za HTML kontekst i dodaj zaglavlje <code>Content-Security-Policy</code>.",
    "S10": "Provjera slobodnog mjesta i upis zauzeća su odvojeni koraci, a između je spori poziv vanjskog servisa. "
           "Napiši test u kojem više korisnika istodobno (više dretvi/zadataka) pokušava zauzeti {resurs} kad je ostalo "
           "samo jedno slobodno mjesto. Rješenje: atomski uvjetni UPDATE (… SET broj = broj + 1 WHERE id = ? AND broj &lt; kapacitet) "
           "i provjera broja promijenjenih redaka <em>prije</em> poziva vanjskog servisa.",
    "S11": "Zatraži obnovu lozinke dvaput istog dana za istog korisnika i usporedi tokene u <code>data/posta</code>. Može li "
           "ga netko izračunati bez pristupa e-pošti? Smije li se iskoristiti dvaput? Token mora biti kriptografski slučajan, "
           "jednokratan, s kratkim rokom valjanosti (u bazi spremaj njegov hash).",
    "S12": "Pokreni aplikaciju, prijavi se, {stvori} s OIB-om i pokušaj se prijaviti pogrešnom lozinkom – zatim pročitaj izlaz "
           "konzole. Lozinke se nikad ne logiraju, OIB samo maskiran, a neuspjela prijava mora ostaviti zapis upozorenja.",
    "S13": "Kao <code>marko</code> dohvati {tudi_dok} s nepostojećim formatom (npr. <code>format=xml</code>). Pogledaj blok "
           "<code>try/catch</code> (u Pythonu <code>try/except</code>) u kojem se provjerava pristup – što se izvršava nakon "
           "iznimke? Pravilo: zadano odbij, "
           "prvo provjeri vlasništvo, nepoznat format → 400, bez detalja iznimke u odgovoru.",
}

STYLE = ("<p><em>Otvaranje ove stranice bilježi se u Moodleu i uzima u obzir pri ocjeni elementa "
         "„Pronalaženje i ispravljanje ranjivosti” ({lvl}).</em></p>")


def fmt(t, d):
    d = dict(d, uvoz_cap=d["uvoz"][0].upper() + d["uvoz"][1:])
    return t.format(**d)


def build(variant, v):
    d = D[v["domain"]]
    vul = v["vulnerable"]
    cats = {}
    for s in vul:
        cats.setdefault(CAT[s], []).append(s)
    r1 = [f"<h3>Savjeti – razina 1 (varijanta {variant})</h3>",
          STYLE.format(lvl="razina 1 = „uz povremenu pomoć”"),
          f"<p>Tvoja varijanta ima <strong>{len(vul)} ranjivosti</strong> u ovim kategorijama OWASP Top 10:2025 i "
          f"dijelovima aplikacije:</p><ul>"]
    for c in sorted(cats):
        for s in cats[c]:
            r1.append(f"<li><strong>{html.escape(c)}</strong> – {html.escape(fmt(R1[s], d)).replace('{{id}}', '{id}')}</li>")
    r1.append("</ul><p>Ako ni nakon ovoga ne pronalaziš neku ranjivost, otvori savjete razine 2.</p>")
    r2 = [f"<h3>Savjeti – razina 2 (varijanta {variant})</h3>",
          STYLE.format(lvl="razina 2 = „uz stalnu pomoć”"), "<ol>"]
    for c in sorted(cats):
        for s in cats[c]:
            r2.append(f"<li><p><strong>{html.escape(c)}</strong> – {html.escape(fmt(R1[s], d)).replace('{{id}}', '{id}')}</p>"
                      f"<p>{fmt(R2[s], d)}</p></li>")
    r2.append("</ol>")
    return "\n".join(r1), "\n".join(r2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "dist", "savjeti"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    variants = json.load(open(os.path.join(ROOT, "variants.json"), encoding="utf-8"))
    for k, v in sorted(variants.items()):
        r1, r2 = build(k, v)
        open(os.path.join(a.out, f"{k}-razina-1.html"), "w", encoding="utf-8").write(r1)
        open(os.path.join(a.out, f"{k}-razina-2.html"), "w", encoding="utf-8").write(r2)
    print(f"Savjeti za {len(variants)} varijanti → {a.out}")


if __name__ == "__main__":
    main()
