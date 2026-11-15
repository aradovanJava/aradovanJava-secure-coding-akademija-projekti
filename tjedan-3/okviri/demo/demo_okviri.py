#!/usr/bin/env python3
"""Demonstracija mehanizama okvira (Tjedan 3) – isti scenarij nad Java, .NET ili Python primjerom.

Skripta šalje stvarne HTTP zahtjeve pokrenutom primjeru iz mape okviri/ i za svaki korak ispisuje
zahtjev, odgovor i što on dokazuje. Koristi samo standardnu biblioteku Pythona 3.10+ (bez instalacije).

Preduvjeti (README.md u mapi okviri/, odjeljak „Demonstracija”):
  1. Keycloak:  cd okviri/keycloak && docker compose up -d
  2. primjer:   Java :8080 (./mvnw spring-boot:run), .NET :5080 (dotnet run), Python :8000 (python -m okviri)

Pokretanje:
  python demo/demo_okviri.py java            # ili dotnet, python
  python demo/demo_okviri.py python --bez-pauze
  python demo/demo_okviri.py --url http://localhost:8000 --bez-keycloaka   # samo koraci bez tokena

Lozinke testnih korisnika su iz realm-akademija.json (SAMO za lokalni razvoj). Token se dohvaća password
grantom preko klijenta medtermin-dev-cli – zastarjeli tok koji se koristi samo u razvoju i automatskim
provjerama; pravo web sučelje koristi Authorization Code + PKCE (P1, slajd „Authorization Code + PKCE”).
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

ADRESE = {"java": "http://localhost:8080", "dotnet": "http://localhost:5080", "python": "http://localhost:8000"}
KORISNICI = {"ana": "Ana12345!", "marko": "Marko12345!", "admin": "Admin12345!"}
DOPUSTENI_ORIGIN = "http://localhost:5173"
ZLI_ORIGIN = "https://zlo.example"
SIGURNOSNA_ZAGLAVLJA = (
    "Content-Security-Policy",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Cache-Control",
    "Strict-Transport-Security",
)

PAUZA = True
neocekivano: list[str] = []


class Odgovor:
    def __init__(self, status: int, zaglavlja: dict[str, str], tijelo: str) -> None:
        self.status = status
        self.zaglavlja = zaglavlja
        self.tijelo = tijelo

    def zaglavlje(self, ime: str) -> str | None:
        for k, v in self.zaglavlja.items():
            if k.lower() == ime.lower():
                return v
        return None


def posalji(metoda: str, url: str, token: str | None = None, zaglavlja: dict[str, str] | None = None,
            tijelo: dict | None = None, forma: dict | None = None) -> Odgovor:
    z = dict(zaglavlja or {})
    podaci = None
    if token:
        z["Authorization"] = f"Bearer {token}"
    if tijelo is not None:
        podaci = json.dumps(tijelo).encode()
        z["Content-Type"] = "application/json"
    if forma is not None:
        podaci = urllib.parse.urlencode(forma).encode()
        z["Content-Type"] = "application/x-www-form-urlencoded"
    # Samo http(s): urlopen bi inače prihvatio i file:// (usporedi SSRF iz T1, Lab03).
    if urllib.parse.urlsplit(url).scheme not in ("http", "https"):
        raise ValueError(f"dopušteni su samo http i https: {url}")
    zahtjev = urllib.request.Request(url, data=podaci, headers=z, method=metoda)  # noqa: S310 – shema provjerena
    try:
        with urllib.request.urlopen(zahtjev, timeout=15) as o:  # noqa: S310 – shema provjerena iznad
            return Odgovor(o.status, dict(o.headers.items()), o.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return Odgovor(e.code, dict(e.headers.items()), e.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, OSError) as e:  # veza odbijena, istek vremena …
        return Odgovor(0, {}, str(getattr(e, "reason", e)))


def naslov(broj: str, tekst: str) -> None:
    if PAUZA and sys.stdin.isatty():
        input("\n[Enter] za sljedeći korak … ")
    print(f"\n{'=' * 78}\n{broj}. {tekst}\n{'=' * 78}")


def objasni(tekst: str) -> None:
    for redak in tekst.strip().splitlines():
        print(f"   ▸ {redak.strip()}")


def prikazi(metoda: str, putanja: str, o: Odgovor, ocekivano: tuple[int, ...] | int, opis: str,
            tijelo: bool = True) -> bool:
    ocek = (ocekivano,) if isinstance(ocekivano, int) else ocekivano
    dobro = o.status in ocek
    oznaka = "OK " if dobro else "!! "
    print(f"   {oznaka} {metoda} {putanja} -> {o.status} (očekivano {' ili '.join(map(str, ocek))}) – {opis}")
    if tijelo and o.tijelo:
        sazeto = o.tijelo if len(o.tijelo) <= 300 else o.tijelo[:300] + " …"
        print(f"        tijelo: {sazeto}")
    if not dobro:
        neocekivano.append(f"{metoda} {putanja}: {o.status} umjesto {ocek} ({opis})")
    return dobro


def b64url(podaci: bytes) -> str:
    return base64.urlsafe_b64encode(podaci).rstrip(b"=").decode()


def claimovi(token: str) -> dict:
    dio = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(dio + "=" * (-len(dio) % 4)))


def token(keycloak: str, korisnik: str) -> str:
    # SAMO ZA RAZVOJ: password grant (klijent medtermin-dev-cli). Aplikacija ovdje nikad ne vidi lozinku –
    # šaljemo je izravno Keycloaku, kao što bi to radio preglednik na Keycloakovoj stranici za prijavu.
    o = posalji("POST", f"{keycloak}/realms/akademija/protocol/openid-connect/token", forma={
        "grant_type": "password", "client_id": "medtermin-dev-cli",
        "username": korisnik, "password": KORISNICI[korisnik],
    })
    if o.status != 200:
        sys.exit(f"Keycloak nije izdao token za {korisnik} ({o.status}): {o.tijelo[:200]}\n"
                 "Je li Keycloak pokrenut? cd okviri/keycloak && docker compose up -d (pričekajte ~30 s)")
    return json.loads(o.tijelo)["access_token"]


def main() -> int:
    global PAUZA
    ap = argparse.ArgumentParser(description="Demonstracija mehanizama okvira (Tjedan 3).")
    ap.add_argument("cilj", nargs="?", choices=sorted(ADRESE), help="koji primjer: java, dotnet ili python")
    ap.add_argument("--url", help="adresa API-ja (umjesto cilja), npr. http://localhost:8000")
    ap.add_argument("--keycloak", default="http://localhost:8180", help="adresa Keycloaka (zadano :8180)")
    ap.add_argument("--bez-keycloaka", action="store_true", help="preskoči korake s JWT tokenima")
    ap.add_argument("--bez-pauze", action="store_true", help="ne čekaj Enter između koraka (npr. u CI-ju)")
    a = ap.parse_args()
    if not a.cilj and not a.url:
        ap.error("navedite cilj (java, dotnet, python) ili --url")
    PAUZA = not a.bez_pauze
    api = (a.url or ADRESE[a.cilj]).rstrip("/")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print(f"Demonstracija mehanizama okvira – API: {api}" + ("" if a.bez_keycloaka else f", Keycloak: {a.keycloak}"))

    # 1 ----------------------------------------------------------------------------------------------
    naslov("1", "Javna ruta i sigurnosna zaglavlja na SVAKOM odgovoru")
    o = posalji("GET", f"{api}/api/health")
    if o.status == 0:
        print(f"   API na {api} ne odgovara ({o.tijelo}). Pokrenite primjer (README.md, odjeljak „Demonstracija”).")
        return 2
    prikazi("GET", "/api/health", o, 200, "jedina ruta označena kao javna")
    for z in SIGURNOSNA_ZAGLAVLJA:
        v = o.zaglavlje(z)
        print(f"        {z + ':':<28} {v if v else '– (nema)'}")
    objasni("""
        Zaglavlja postavlja okvir (Spring Security headers(), ASP.NET Core middleware, ASGI middleware u FastAPI-ju)
        za svaki odgovor – ne programer na pojedinoj stranici kao u T2 (S09).
        HSTS se šalje samo preko HTTPS-a, pa ga ovdje (http://localhost) nema – to je ispravno.""")

    # 2 ----------------------------------------------------------------------------------------------
    naslov("2", "Zadano zabranjeno (deny by default): zaštićena ruta bez tokena")
    o = posalji("GET", f"{api}/api/rezervacije/moje")
    prikazi("GET", "/api/rezervacije/moje", o, 401, "bez tokena")
    if o.zaglavlje("WWW-Authenticate"):
        print(f"        WWW-Authenticate: {o.zaglavlje('WWW-Authenticate')}")
    objasni("""
        Ruta nema nikakvu „provjeru prijave” u kodu – štiti je pravilo okvira: anyRequest().authenticated(),
        FallbackPolicy = RequireAuthenticatedUser() ili globalna ovisnost zadano_zabranjeno u FastAPI-ju.
        Nova ruta koju netko doda sutra zaštićena je automatski.""")

    if a.bez_keycloaka:
        print("\n(Koraci 3–7 trebaju tokene iz Keycloaka – preskočeni zbog --bez-keycloaka.)")
    else:
        # 3 ------------------------------------------------------------------------------------------
        naslov("3", "Token od Keycloaka: što je u JWT-u")
        tokeni = {k: token(a.keycloak, k) for k in KORISNICI}
        c = claimovi(tokeni["ana"])
        for k in ("iss", "aud", "azp", "preferred_username", "realm_access", "exp"):
            print(f"        {k + ':':<20} {c.get(k)}")
        objasni("""
            API provjerava potpis (javni ključ s JWKS adrese issuera), iss, aud (medtermin-api) i rok (exp).
            Korisničko ime dolazi iz preferred_username, uloge iz realm_access.roles – mapiranje u uloge okvira
            je na jednom mjestu (KeycloakJwtKonverter / KeycloakUloge / PrijavljeniKorisnik).""")

        # 4 ------------------------------------------------------------------------------------------
        naslov("4", "Ispravan token: korisnik vidi samo svoje")
        o = posalji("GET", f"{api}/api/rezervacije/moje", tokeni["ana"])
        prikazi("GET", "/api/rezervacije/moje (ana)", o, 200, "tko je korisnik, zna se iz tokena, ne iz parametra")

        # 5 ------------------------------------------------------------------------------------------
        naslov("5", "Krivotvoreni tokeni se odbijaju")
        zaglavlje, _, potpis = tokeni["ana"].split(".")
        lazni = dict(claimovi(tokeni["ana"]))
        lazni["realm_access"] = {"roles": ["ADMIN"]}
        izmijenjen = f"{zaglavlje}.{b64url(json.dumps(lazni).encode())}.{potpis}"
        o = posalji("GET", f"{api}/api/admin/rezervacije", izmijenjen)
        prikazi("GET", "/api/admin/rezervacije", o, 401, "ana si je u tokenu dodala ulogu ADMIN (stari potpis)",
                tijelo=False)
        alg_none = b64url(json.dumps({"alg": "none", "typ": "JWT"}).encode())
        bez_potpisa = f"{alg_none}.{b64url(json.dumps(lazni).encode())}."
        o = posalji("GET", f"{api}/api/admin/rezervacije", bez_potpisa)
        prikazi("GET", "/api/admin/rezervacije", o, 401, "token s alg: none (bez potpisa)", tijelo=False)
        objasni("""
            Okvir prihvaća samo zadani algoritam (RS256) i ključeve s JWKS adrese – usporedite s vlastitim JWT
            kodom iz T1 (Lab12), gdje je alg: none prolazio.""")

        # 6 ------------------------------------------------------------------------------------------
        naslov("6", "Autorizacija nad objektom (IDOR, S01): tuđa rezervacija")
        o = posalji("DELETE", f"{api}/api/rezervacije/1", tokeni["marko"])
        prikazi("DELETE", "/api/rezervacije/1 (marko briše aninu)", o, 404, "ne 403 – ne otkrivamo da zapis postoji")
        objasni("""
            Provjera vlasništva je jedno mjesto u kodu: @PreAuthorize + bean Vlasnistvo (Java),
            AuthorizationHandler<VlasnikIliAdmin, Rezervacija> (.NET), ovisnost Vlasnistvo(...) (FastAPI).
            U ruti nema if-a za ovlasti.""")

        # 7 ------------------------------------------------------------------------------------------
        naslov("7", "Uloge: administratorski popis")
        o = posalji("GET", f"{api}/api/admin/rezervacije", tokeni["ana"])
        prikazi("GET", "/api/admin/rezervacije (ana)", o, 403, "prijavljena, ali nema ulogu ADMIN")
        o = posalji("GET", f"{api}/api/admin/rezervacije", tokeni["admin"])
        prikazi("GET", "/api/admin/rezervacije (admin)", o, 200, "uloga iz realm_access.roles", tijelo=False)
        o = posalji("DELETE", f"{api}/api/rezervacije/2", tokeni["admin"])
        prikazi("DELETE", "/api/rezervacije/2 (admin briše markovu)", o, (204, 404),
                "204; 404 ako je već obrisana (ponovno pokrenite primjer za početne podatke)", tijelo=False)
        objasni("""
            401 = ne znam tko si; 403 = znam tko si, ali ne smiješ; 404 za tuđi objekt = ne otkrivam da postoji.""")

    # 8 ----------------------------------------------------------------------------------------------
    naslov("8", "CORS: popis dopuštenih origina iz konfiguracije")
    for origin, dopusten in ((DOPUSTENI_ORIGIN, True), (ZLI_ORIGIN, False)):
        o = posalji("OPTIONS", f"{api}/api/rezervacije/moje", zaglavlja={
            "Origin": origin, "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        })
        acao = o.zaglavlje("Access-Control-Allow-Origin")
        ispravno = (acao == origin) if dopusten else (acao in (None, ""))
        print(f"   {'OK ' if ispravno else '!! '} preflight s Origin: {origin:<24} -> {o.status}, "
              f"Access-Control-Allow-Origin: {acao or '– (nema)'}")
        if not ispravno:
            neocekivano.append(f"CORS za {origin}: Access-Control-Allow-Origin={acao}")
    objasni("""
        Zli origin ne dobiva Access-Control-Allow-Origin, pa preglednik ne pušta njegov JavaScript da pročita
        odgovor. U T2 (S04) Origin se zrcalio natrag uz vjerodajnice.""")

    # 9 ----------------------------------------------------------------------------------------------
    naslov("9", "Lokalna prijava: ista poruka, nadogradnja hasha i ograničenje pokušaja")
    o1 = posalji("POST", f"{api}/api/auth/login", tijelo={"username": "ana", "password": "kriva-lozinka"})
    prikazi("POST", "/api/auth/login (ana, kriva lozinka)", o1, 401, "")
    o2 = posalji("POST", f"{api}/api/auth/login", tijelo={"username": "nepostojeci", "password": "kriva-lozinka"})
    prikazi("POST", "/api/auth/login (nepostojeći korisnik)", o2, 401, "isti odgovor – nema enumeracije")
    if o1.tijelo != o2.tijelo:
        print("   !!  tijela odgovora se razlikuju")
        neocekivano.append("prijava: različita tijela za krivu lozinku i nepostojećeg korisnika")
    o = posalji("POST", f"{api}/api/auth/login", tijelo={"username": "marko", "password": KORISNICI["marko"]})
    prikazi("POST", "/api/auth/login (marko, ispravna lozinka)", o, (200, 429),
            "stari SHA-256 hash iz T2 se provjeri i zamijeni novim – pogledajte log aplikacije", tijelo=False)
    for pokusaj in range(1, 11):
        o = posalji("POST", f"{api}/api/auth/login", tijelo={"username": "ana", "password": f"pogadjam-{pokusaj}"})
        if o.status == 429:
            print(f"   OK  nakon još {pokusaj} pokušaja: 429 Too Many Requests, Retry-After: "
                  f"{o.zaglavlje('Retry-After') or '–'}")
            break
    else:
        print("   !!  429 se nije pojavio ni nakon 10 pokušaja")
        neocekivano.append("ograničenje pokušaja prijave nije proradilo")
    objasni("""
        Ograničenje je mehanizam (Bucket4j / AddRateLimiter / limits), a ne brojač u kontroleru.
        Brojač vrijedi minutu – za ponovni demo pričekajte ili ponovno pokrenite primjer.""")

    print(f"\n{'=' * 78}")
    if neocekivano:
        print(f"Neočekivani rezultati ({len(neocekivano)}):")
        for n in neocekivano:
            print(f"  - {n}")
        return 1
    print("Svi koraci su se ponašali kako treba.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
