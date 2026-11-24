#!/usr/bin/env python3
"""Izrađuje .http datoteke demo aplikacije Knjižnica za sva tri stacka.

Za svaki stack nastaju dvije inačice iste datoteke:
  *.http      – JetBrains HTTP Client (IntelliJ IDEA, PyCharm, Rider)
  *-vs.http   – Visual Studio 2022 17.12+ / 2026 i VS Code (REST Client)
Razlikuju se samo po tome kako se token iz prijave sprema za sljedeće zahtjeve.

  predlozak/<stack>/http/knjiznica*.http                       – obični zahtjevi (idu i polaznicima)
  predlozak/<stack>-sigurnosni-testovi/http/demonstracija*.http – zahtjevi za demonstraciju K01–K08
                                                                  (samo u verziji s testovima i u rješenju)

Pokretanje: python3 izradi_http.py   (prepisuje postojeće datoteke)
"""
import os
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
PORTOVI = {"java": 8080, "dotnet": 5080, "python": 8000}
LOZINKE = {"ana": "Ana123!", "marko": "Marko123!", "iva": "Iva123!", "knjiznicar": "Knjiga123!"}

# Dokument s oznakom tipa: siguran parser ga mora odbiti (isti dokumenti kao u sigurnosnim testovima).
YAML_S_TIPOM = {
    "java": "- !!java.util.HashMap {naslov: Proba, autor: Netko, godina: 2001}",
    "dotnet": "- naslov: Proba\n  autor: Netko\n  godina: 2001\n  dodatno: !System.Text.StringBuilder {}",
    "python": '- naslov: !!python/object/new:builtins.str ["Proba"]\n  autor: Netko\n  godina: 2001',
}
KATALOG = "- naslov: Kiklop\n  autor: Ranko Marinković\n  godina: 1965\n- naslov: Gospoda Glembajevi\n  autor: Miroslav Krleža\n  godina: 1929"


def prijava(korisnik, lozinka=None):
    return {"naslov": f"Prijava: {korisnik}", "metoda": "POST", "putanja": "/api/prijava",
            "json": f'{{"korisnickoIme": "{korisnik}", "lozinka": "{lozinka or LOZINKE[korisnik]}"}}',
            "spremi": korisnik}


def zahtjev(naslov, metoda, putanja, korisnik=None, json=None, yaml=None, opis=None):
    return {"naslov": naslov, "metoda": metoda, "putanja": putanja, "korisnik": korisnik, "json": json,
            "yaml": yaml, "opis": opis}


def obicni():
    return [
        {"sekcija": "Prijava (tokeni se spremaju za ostale zahtjeve)"},
        prijava("ana"), prijava("marko"), prijava("iva"), prijava("knjiznicar"),
        {"sekcija": "Katalog"},
        zahtjev("Svi naslovi", "GET", "/api/knjige"),
        zahtjev("Pretraga po naslovu", "GET", "/api/knjige?trazi=" + quote("zlato")),
        zahtjev("Podaci o knjizi 1", "GET", "/api/knjige/1"),
        {"sekcija": "Članovi"},
        zahtjev("Moj profil (ana)", "GET", "/api/clanovi/1", "ana"),
        zahtjev("Profil člana 1 (knjižničar)", "GET", "/api/clanovi/1", "knjiznicar"),
        zahtjev("Registracija novog člana", "POST", "/api/registracija",
                json='{"korisnickoIme": "petra", "lozinka": "Petra2026!", "ime": "Petra Perić", '
                     '"email": "petra.peric@primjer.hr"}'),
        {"sekcija": "Posudbe"},
        zahtjev("Moje posudbe (ana)", "GET", "/api/posudbe", "ana"),
        zahtjev("Nova posudba (ana)", "POST", "/api/posudbe", "ana", json='{"knjigaId": 5}'),
        zahtjev("Produljenje posudbe 1 za 7 dana (ana)", "POST", "/api/posudbe/1/produzi", "ana",
                json='{"dana": 7}'),
        {"sekcija": "Uvoz kataloga (samo knjižničar)"},
        zahtjev("Uvoz dviju knjiga", "POST", "/api/katalog/uvoz", "knjiznicar", yaml=KATALOG),
    ]


def demonstracija(stack):
    k02_svi = "' OR '1'='1' -- "
    k02_union = "%' UNION SELECT id, korisnicko_ime, lozinka_hash, 0 FROM korisnici -- "
    k07_ime = "ana\\n2026-11-25 10:00:00 INFO SECURITY_EVENT LOGIN_SUCCESS korisnik=knjiznicar"
    return [
        {"sekcija": "Prijava (prvo pošaljite ova četiri zahtjeva)"},
        prijava("ana"), prijava("marko"), prijava("iva"), prijava("knjiznicar"),
        {"sekcija": "K01 – tuđi profil promjenom ID-a (A01)"},
        zahtjev("K01 Ana traži Markov profil", "GET", "/api/clanovi/2", "ana",
                opis="Polazno: 200 s Markovom adresom i telefonom. Nakon ispravka: 404."),
        zahtjev("K01 Ana traži nepostojećeg člana", "GET", "/api/clanovi/999", "ana",
                opis="Nakon ispravka isti odgovor kao za tuđi profil (ne otkriva postoji li član)."),
        zahtjev("K01 Knjižničar smije vidjeti Markov profil", "GET", "/api/clanovi/2", "knjiznicar",
                opis="200 i prije i poslije ispravka (funkcionalnost ostaje)."),
        {"sekcija": "K02 – SQL umetanje u pretrazi (A05)"},
        zahtjev("K02 Uvjet koji je uvijek istinit", "GET", "/api/knjige?trazi=" + quote(k02_svi, safe=""),
                opis=f"trazi = {k02_svi.strip()}  | Polazno: vraća i skrivenu knjigu 'Interni popis za otpis'. "
                     "Nakon ispravka: prazan popis."),
        zahtjev("K02 UNION s tablicom korisnika", "GET", "/api/knjige?trazi=" + quote(k02_union, safe=""),
                opis=f"trazi = {k02_union.strip()}  | Polazno: korisnička imena i hashevi lozinki kao "
                     "'knjige' (ulaz za K04). Nakon ispravka: prazan popis."),
        zahtjev("K02 Preduga pretraga", "GET", "/api/knjige?trazi=" + "a" * 101,
                opis="Nakon ispravka: 400 (ograničenje duljine)."),
        {"sekcija": "K03 – ranjiva ovisnost za YAML (A03)"},
        zahtjev("K03 Katalog s oznakom tipa", "POST", "/api/katalog/uvoz", "knjiznicar", yaml=YAML_S_TIPOM[stack],
                opis="Polazno: 200 (parser stvara objekt iz oznake). Nakon ispravka: 400."),
        zahtjev("K03 Ispravan katalog", "POST", "/api/katalog/uvoz", "knjiznicar", yaml=KATALOG,
                opis="200 i prije i poslije ispravka."),
        {"sekcija": "K04 – lozinke kao MD5 bez soli (A04)"},
        zahtjev("K04 Registracija: korisnik test1", "POST", "/api/registracija",
                json='{"korisnickoIme": "test1", "lozinka": "Ljeto2026!", "ime": "Test Jedan", '
                     '"email": "test1@primjer.hr"}'),
        zahtjev("K04 Registracija: korisnik test2 s istom lozinkom", "POST", "/api/registracija",
                json='{"korisnickoIme": "test2", "lozinka": "Ljeto2026!", "ime": "Test Dva", '
                     '"email": "test2@primjer.hr"}',
                opis="Zatim ponovite zahtjev 'K02 UNION': polazno test1 i test2 imaju isti hash od 32 "
                     "heksadecimalna znaka (MD5)."),
        {"sekcija": "K05 – detalji greške i sigurnosna zaglavlja (A02)"},
        zahtjev("K05 Nepostojeća knjiga", "GET", "/api/knjige/999999",
                opis="Polazno: 500 sa stack traceom. Nakon ispravka: 404 s kratkom porukom."),
        zahtjev("K05 Zaglavlja odgovora", "GET", "/api/knjige",
                opis="Nakon ispravka: X-Content-Type-Options, X-Frame-Options, Content-Security-Policy, "
                     "Referrer-Policy, Cross-Origin-Resource-Policy, Cache-Control."),
        {"sekcija": "K06 – produljenje bez poslovnih pravila (A06)"},
        zahtjev("K06 Produljenje za 365 dana", "POST", "/api/posudbe/3/produzi", "ana", json='{"dana": 365}',
                opis="Polazno: 200, rok pomaknut godinu dana. Nakon ispravka: 400."),
        zahtjev("K06 Produljenje za -30 dana", "POST", "/api/posudbe/3/produzi", "ana", json='{"dana": -30}',
                opis="Polazno: 200, rok pomaknut unatrag. Nakon ispravka: 400."),
        zahtjev("K06 Uobičajeno produljenje za 7 dana", "POST", "/api/posudbe/2/produzi", "ana",
                json='{"dana": 7}',
                opis="Pošaljite tri puta: nakon ispravka prva dva su 200, treći 409 (najviše dva produljenja)."),
        {"sekcija": "K07 – lozinka u dnevniku i krivotvoreni zapis (A09)"},
        zahtjev("K07 Prijava s novim redom u korisničkom imenu", "POST", "/api/prijava",
                json=f'{{"korisnickoIme": "{k07_ime}", "lozinka": "x"}}',
                opis="Pogledajte konzolu poslužitelja. Polazno: novi red u zapisu i lažni LOGIN_SUCCESS. "
                     "Nakon ispravka: LOGIN_FAILED, a novi red zamijenjen znakom _."),
        zahtjev("K07 Neuspjela prijava (kriva lozinka)", "POST", "/api/prijava",
                json='{"korisnickoIme": "ana", "lozinka": "kriva-lozinka"}',
                opis="Polazno: u konzoli piše lozinka, a neuspjeh nije zabilježen. "
                     "Nakon ispravka: SECURITY_EVENT LOGIN_FAILED (WARN), bez lozinke."),
        {"sekcija": "K08 – provjera članarine koja propušta (A10)"},
        zahtjev("K08 Marko (istekla članarina) posuđuje knjigu", "POST", "/api/posudbe", "marko",
                json='{"knjigaId": 4}', opis="Polazno: 201. Nakon ispravka: 403."),
        zahtjev("K08 Iva (status koji provjera ne poznaje) posuđuje knjigu", "POST", "/api/posudbe", "iva",
                json='{"knjigaId": 4}',
                opis="Polazno: 201. Nakon ispravka: 403 i SECURITY_EVENT LOAN_DENIED u konzoli."),
    ]


def ispisi(stavke, port, dijalekt, naslov):
    jetbrains = dijalekt == "jetbrains"
    alat = ("IntelliJ IDEA, PyCharm ili Rider (JetBrains HTTP Client)" if jetbrains
            else "Visual Studio 2022 17.12+ / 2026 ili VS Code s proširenjem REST Client")
    out = [f"# {naslov}", f"# Za: {alat}.",
           "# Pokrenite aplikaciju, zatim zahtjeve šaljite redom (ikona ▶ uz zahtjev ili 'Send Request').",
           "", f"@host = http://localhost:{port}", ""]
    for s in stavke:
        if "sekcija" in s:
            out += ["", f"### ==== {s['sekcija']} ====", ""]
            continue
        out.append(f"### {s['naslov']}")
        if s.get("opis"):
            out.append(f"# {s['opis']}")
        if s.get("spremi") and not jetbrains:
            out.append(f"# @name prijava_{s['spremi']}")
        out.append(f"{s['metoda']} {{{{host}}}}{s['putanja']}")
        if s.get("korisnik"):
            k = s["korisnik"]
            token = f"{{{{token_{k}}}}}" if jetbrains else f"{{{{prijava_{k}.response.body.$.token}}}}"
            out.append(f"Authorization: Bearer {token}")
        if s.get("json"):
            out += ["Content-Type: application/json", "", s["json"]]
        elif s.get("yaml"):
            out += ["Content-Type: application/yaml", "", s["yaml"]]
        if s.get("spremi") and jetbrains:
            out += ["", f'> {{% client.global.set("token_{s["spremi"]}", response.body.token); %}}']
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def zapisi(put, tekst):
    os.makedirs(os.path.dirname(put), exist_ok=True)
    with open(put, "w", encoding="utf-8", newline="\n") as f:
        f.write(tekst)
    print(os.path.relpath(put, ROOT))


def main():
    for stack, port in PORTOVI.items():
        for dijalekt, nastavak in (("jetbrains", ""), ("vs", "-vs")):
            zapisi(os.path.join(ROOT, "predlozak", stack, "http", f"knjiznica{nastavak}.http"),
                   ispisi(obicni(), port, dijalekt, "Knjižnica – primjeri zahtjeva"))
            zapisi(os.path.join(ROOT, "predlozak", f"{stack}-sigurnosni-testovi", "http",
                                f"demonstracija{nastavak}.http"),
                   ispisi(demonstracija(stack), port, dijalekt,
                          "Knjižnica – zahtjevi za demonstraciju K01–K08 (samo za predavača)"))


if __name__ == "__main__":
    main()
