"""Demo „Aplikacija i baza” (Python): što aplikacijski račun smije u bazi.

Program se spaja na SQL Server iz laboratorija ONAKO KAKO SE SPAJA APLIKACIJA:
  * prijavom <domena>_app (ne sa!), šifriranom vezom,
  * lozinkom iz varijable okruženja (nikad iz koda ni iz repozitorija),
  * isključivo parametriziranim upitima,
  * i na početku „zahtjeva” postavlja SESSION_CONTEXT s prijavljenim korisnikom (za Row-Level Security).
Zatim ispisuje što taj račun stvarno smije. Pokrenite ga PRIJE zadataka (zatečeno stanje) i POSLIJE
zadataka Z2–Z4: upozorenja [!] moraju nestati.

Pokretanje (README.md, odjeljak „Demo: aplikacija i baza”):
    docker compose --profile aplikacija run --rm aplikacija-python
ili lokalno (Python 3.10+):
    pip install -r requirements.txt
    python demo.py

Postavke (varijable okruženja): DOMENA, SQL_HOST, SQL_PORT, APP_LOZINKA, PODRSKA_LOZINKA.
"""

import os
import re
import secrets
import sys

import mssql_python as sql  # Microsoftov službeni upravljački program: pip install mssql-python

# Domena -> (baza, glavna tablica, stupac vlasnika). Nazivi tablica i stupaca NE MOGU biti parametri upita,
# zato dolaze isključivo iz ovog popisa dopuštenih vrijednosti – nikad iz korisničkog unosa (usporedi S08 iz T2).
DOMENE = {
    "medtermin": ("MedTermin", "rezervacije", "pacijent"),
    "ulaznica": ("Ulaznica", "narudzbe", "kupac"),
    "kadrovska": ("Kadrovska", "zahtjevi", "zaposlenik"),
}
ZLONAMJERNI_UNOS = "x' OR 1=1 --"

DOMENA = os.environ.get("DOMENA", "medtermin").strip().lower()
if DOMENA not in DOMENE:
    sys.exit(f"DOMENA mora biti medtermin, ulaznica ili kadrovska (sada: '{DOMENA}').")
BAZA, GLAVNA, VLASNIK = DOMENE[DOMENA]
HOST = os.environ.get("SQL_HOST") or "localhost"
PORT = os.environ.get("SQL_PORT") or "1433"
APP = f"{DOMENA}_app"
# Lozinke dolaze iz okruženja. Ako ih nema, pokušavamo sa ZATEČENIM lozinkama iz postavljanja laboratorija –
# ako one još rade, to je nalaz (zadatak Z2.1), a ne pogodnost.
APP_LOZINKA = os.environ.get("APP_LOZINKA") or f"{DOMENA}123"
ZATECENA_LOZINKA = not os.environ.get("APP_LOZINKA")
PODRSKA_LOZINKA = os.environ.get("PODRSKA_LOZINKA") or "Sluzba-Pomoci24"

upozorenja = 0
rezultati: list[tuple[str, str]] = []  # strojno čitljivi sažetak (ispisuje se na kraju kao DEMO|ključ|vrijednost)


def spoji(prijava: str, lozinka: str) -> sql.Connection:
    """Nova veza. Encrypt=yes: promet je šifriran (TLS).

    TrustServerCertificate=yes smije stajati SAMO u laboratoriju (samopotpisani certifikat poslužitelja).
    U produkciji: certifikat kojem klijent vjeruje i TrustServerCertificate=no.
    """
    lozinka_u_zagradama = "{" + lozinka.replace("}", "}}") + "}"  # smije sadržavati ; i =
    niz = (
        f"Server={HOST},{PORT};Database={BAZA};UID={prijava};PWD={lozinka_u_zagradama};"
        "Encrypt=yes;TrustServerCertificate=yes;"
    )
    return sql.connect(niz, timeout=15)


def kao_korisnik(korisnik: str | None) -> sql.Connection:
    """Veza aplikacije za jedan „zahtjev”: nakon prijave korisnika aplikacija bazi kaže tko je on."""
    veza = spoji(APP, APP_LOZINKA)
    if korisnik is not None:
        # @read_only = 1: kasniji kod (pa ni SQL injection) u istoj sesiji više ne može promijeniti identitet.
        veza.cursor().execute(
            "EXEC sp_set_session_context @key = N'korisnik', @value = ?, @read_only = 1", korisnik
        )
    return veza


def vrijednost(veza: sql.Connection, upit: str, *parametri):
    """Prvi stupac prvog retka. Parametri se šalju odvojeno od teksta upita (oznake ?)."""
    kursor = veza.cursor()
    kursor.execute(upit, *parametri)
    return kursor.fetchone()[0]


def pokusaj(veza: sql.Connection, upit: str, *parametri) -> tuple[bool, object]:
    """(True, vrijednost) ako baza dopusti naredbu, inače (False, poruka o grešci)."""
    try:
        kursor = veza.cursor()
        kursor.execute(upit, *parametri)
        redak_rezultata = kursor.fetchone() if kursor.description else None
        return True, (redak_rezultata[0] if redak_rezultata else None)
    except sql.Error as greska:
        return False, str(greska).splitlines()[0][:120]
    finally:
        veza.rollback()  # ništa od pokušaja ne ostaje u bazi (i CREATE TABLE je dio transakcije)


def redaka(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return f"{n} redak"
    if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14):
        return f"{n} retka"
    return f"{n} redaka"


def ispis(opis: str, stanje: str, upozorenje: str = "", napomena: str = "") -> None:
    global upozorenja
    dodatak = ""
    if upozorenje:
        upozorenja += 1
        dodatak = f"  [!] {upozorenje}"
    elif napomena:
        dodatak = f"  ({napomena})"
    print(f"   {opis + ' ':.<36} {stanje}{dodatak}")


def da_ne(uvjet: object) -> str:
    return "DA" if uvjet == 1 else "NE"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # dijakritici i na Windows konzoli

    print("=== Aplikacija i baza: što smije aplikacijski račun ===")
    print(f"Domena: {DOMENA} | baza: {BAZA} | prijava: {APP} | poslužitelj: {HOST},{PORT}")
    print("Veza: šifrirana (Encrypt=yes); certifikat poslužitelja se ne provjerava samo u laboratoriju.")
    try:
        veza = spoji(APP, APP_LOZINKA)
    except sql.Error as greska:
        print(f"\nNe mogu se spojiti kao {APP}: {str(greska).splitlines()[0][:200]}")
        print("Provjerite radi li poslužitelj (docker compose ps). Ako ste u zadatku Z2.1 promijenili")
        print("lozinku aplikacijske prijave, upišite je u .env kao APP_LOZINKA=... (ne u kod!).")
        return 2

    print("\n1. Tko sam u bazi")
    kursor = veza.cursor()
    kursor.execute(
        "SELECT ORIGINAL_LOGIN(), USER_NAME(), IS_SRVROLEMEMBER('sysadmin'), "
        "IS_ROLEMEMBER('db_owner'), IS_ROLEMEMBER('uloga_aplikacija')"
    )
    prijava, korisnik_baze, sysadmin, db_owner, uloga = kursor.fetchone()
    ispis("prijava (login)", prijava)
    ispis("korisnik u bazi", korisnik_baze)
    ispis(
        "lozinka",
        "zatečena" if ZATECENA_LOZINKA else "iz varijable okruženja",
        "prijava radi sa zatečenom lozinkom iz postavljanja (Z2.1)" if ZATECENA_LOZINKA else "",
    )
    ispis("član sysadmin", da_ne(sysadmin), "aplikacija je administrator poslužitelja (Z2.2)" if sysadmin == 1 else "")
    ispis("član db_owner", da_ne(db_owner), "aplikacija je vlasnik baze (Z2.3)" if db_owner == 1 else "")
    ispis(
        "član uloga_aplikacija",
        da_ne(uloga),
        "" if uloga == 1 else "nema vlastite uloge s minimalnim pravima (Z3.1)",
    )
    rezultati.extend(
        [
            ("lozinka", "ZATECENA" if ZATECENA_LOZINKA else "IZ_OKRUZENJA"),
            ("sysadmin", da_ne(sysadmin)),
            ("db_owner", da_ne(db_owner)),
            ("uloga_aplikacija", da_ne(uloga)),
        ]
    )

    print("\n2. Što račun stvarno može (pokušaji se poništavaju – ROLLBACK)")
    uspjelo, _ = pokusaj(veza, "SELECT COUNT(*) FROM dbo.revizija")
    ispis(
        "čitanje dnevnika dbo.revizija",
        "DOPUŠTENO" if uspjelo else "ODBIJENO",
        "aplikacija može čitati (i brisati) vlastite tragove (Z3.3)" if uspjelo else "",
    )
    rezultati.append(("revizija", "DOPUSTENO" if uspjelo else "ODBIJENO"))
    proba = f"demo_proba_{secrets.token_hex(4)}"  # naziv stvaramo sami – nije korisnički unos
    uspjelo, _ = pokusaj(veza, f"CREATE TABLE dbo.{proba} (id INT)")
    ispis(
        "CREATE TABLE (promjena sheme)",
        "DOPUŠTENO" if uspjelo else "ODBIJENO",
        "aplikacija smije mijenjati shemu – i napadač kroz SQL injection (Z3.2)" if uspjelo else "",
    )
    rezultati.append(("ddl", "DOPUSTENO" if uspjelo else "ODBIJENO"))
    veza.close()

    print(f"\n3. Isti unos na dva načina (sesija korisnika ana, unos: {ZLONAMJERNI_UNOS})")
    veza = kao_korisnik("ana")
    # ISPRAVNO: unos putuje kao parametar – baza ga nikad ne tumači kao SQL.
    upit = f"SELECT COUNT(*) FROM dbo.{GLAVNA} WHERE {VLASNIK} = ?"  # noqa: S608 – nazivi iz DOMENE
    kao_parametar = vrijednost(veza, upit, ZLONAMJERNI_UNOS)
    ispis("parametar (?)", redaka(kao_parametar), napomena="unos je ostao podatak")
    # POGREŠNO (samo za demonstraciju): unos zalijepljen u tekst upita postaje dio naredbe.
    zalijepljeno = f"SELECT COUNT(*) FROM dbo.{GLAVNA} WHERE {VLASNIK} = N'{ZLONAMJERNI_UNOS}'"  # noqa: S608 – NAMJERNO
    svi = vrijednost(veza, zalijepljeno)
    tudji = vrijednost(veza, f"SELECT COUNT(*) FROM dbo.{GLAVNA} WHERE {VLASNIK} <> ?", "ana")  # noqa: S608 – nazivi iz DOMENE
    ispis(
        "lijepljenje u tekst upita",
        redaka(svi),
        "injekcija vraća i tuđe zapise – baza ih ne filtrira (Z4.2)" if tudji > 0 else "",
        "injekcija uspijeva, ali RLS vraća samo Anine zapise – obrana u dubinu",
    )
    rezultati.extend([("parametar", str(kao_parametar)), ("injekcija_tudji", str(tudji))])
    veza.close()

    print(f"\n4. Row-Level Security: SESSION_CONTEXT(N'korisnik') nad dbo.{GLAVNA}")
    for korisnik in ("ana", "marko", None):
        veza = kao_korisnik(korisnik)
        svi = vrijednost(veza, f"SELECT COUNT(*) FROM dbo.{GLAVNA}")  # noqa: S608 – naziv iz DOMENE
        if korisnik is None:
            ispis(
                "bez prijavljenog korisnika",
                f"vidi {redaka(svi)}",
                "bez konteksta aplikacija ne smije vidjeti ništa (Z4.2)" if svi > 0 else "",
            )
            rezultati.append(("rls_bez", str(svi)))
        else:
            upit = f"SELECT COUNT(*) FROM dbo.{GLAVNA} WHERE {VLASNIK} <> ?"  # noqa: S608 – nazivi iz DOMENE
            tudji = vrijednost(veza, upit, korisnik)
            ispis(
                f"korisnik {korisnik}",
                f"vidi {redaka(svi)}, od toga tuđih: {tudji}",
                "vidi tuđe zapise (Z4.1, Z4.2)" if tudji > 0 else "",
            )
            rezultati.append((f"rls_{korisnik}_tudji", str(tudji)))
        veza.close()

    print("\n5. Korisnička podrška (prijava podrska): maskiranje i najmanje ovlasti")
    try:
        veza = spoji("podrska", PODRSKA_LOZINKA)
    except sql.Error:
        print("   preskočeno – prijava podrska nije uspjela (ako ste joj promijenili lozinku,")
        print("   postavite PODRSKA_LOZINKA)")
        rezultati.extend([("podrska_oib", "PRESKOCENO"), ("podrska_hash", "PRESKOCENO")])
    else:
        try:
            kursor = veza.cursor()
            kursor.execute("SELECT TOP (1) oib, email FROM dbo.korisnici WHERE username = ?", "ana")
            oib, email = kursor.fetchone()
            vidljiv = re.fullmatch(r"\d{11}", oib or "") is not None
            ispis(
                "OIB i e-mail korisnice ana",
                f"{oib} · {email}",
                "podrška vidi pune osobne podatke (Z4.3, Z4.4)" if vidljiv else "",
                "maskirano",
            )
            rezultati.append(("podrska_oib", "VIDLJIV" if vidljiv else "MASKIRAN"))
        except sql.Error as greska:
            poruka = str(greska).splitlines()[0][:60]
            ispis("OIB i e-mail korisnice ana", "ODBIJENO", f"podrška mora moći čitati korisnike (Z4.4): {poruka}")
            rezultati.append(("podrska_oib", "ODBIJENO"))
        veza.rollback()
        uspjelo, _ = pokusaj(veza, "SELECT TOP (1) password_hash FROM dbo.korisnici")
        ispis(
            "čitanje password_hash",
            "DOPUŠTENO" if uspjelo else "ODBIJENO",
            "podrška može čitati hasheve lozinki (Z2.5, Z4.5)" if uspjelo else "",
        )
        rezultati.append(("podrska_hash", "DOPUSTENO" if uspjelo else "ODBIJENO"))
        veza.close()

    print()
    if upozorenja:
        print(f"Upozorenja: {upozorenja}. Aplikacijski račun (ili podrška) smije više nego što treba –")
        print("riješite zadatke Z2–Z4 iz ZADACI.md i pokrenite demo ponovno.")
    else:
        print("Upozorenja: 0. Aplikacija radi s najmanjim ovlastima, a baza je druga linija obrane.")
    rezultati.append(("upozorenja", str(upozorenja)))
    print()
    for kljuc, stanje in rezultati:
        print(f"DEMO|{kljuc}|{stanje}")
    return 1 if upozorenja and os.environ.get("DEMO_STROGO") == "1" else 0


if __name__ == "__main__":
    sys.exit(main())
