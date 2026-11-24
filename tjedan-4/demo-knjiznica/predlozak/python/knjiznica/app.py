"""Sastavljanje FastAPI aplikacije: baza, početni podaci, rukovanje greškama i rute."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from knjiznica import autentikacija, clanovi, katalog, knjige, lozinke, posudbe
from knjiznica.autentikacija import Tokeni
from knjiznica.baza import Baza
from knjiznica.greske import ApiGreska

KORISNICI = [
    # korisničko ime, lozinka, uloga, ime, e-mail, adresa, telefon, članarina
    ("ana", "Ana123!", "CLAN", "Ana Anić", "ana.anic@primjer.hr", "Ilica 10, Zagreb", "091 111 1111", "AKTIVNA"),
    ("marko", "Marko123!", "CLAN", "Marko Marić", "marko.maric@primjer.hr", "Vukovarska 22, Zagreb",
     "092 222 2222", "ISTEKLA"),
    ("iva", "Iva123!", "CLAN", "Iva Ivić", "iva.ivic@primjer.hr", "Savska 5, Zagreb", "095 333 3333",
     "SUSPENDIRANA"),
    ("knjiznicar", "Knjiga123!", "KNJIZNICAR", "Kata Knjižić", "kata.knjizic@knjiznica.hr", "Trg knjiga 1, Zagreb",
     "01 444 4444", "AKTIVNA"),
]
KNJIGE = [
    ("Proces", "Franz Kafka", 1925, 0),
    ("Na Drini ćuprija", "Ivo Andrić", 1945, 0),
    ("Povratak Filipa Latinovicza", "Miroslav Krleža", 1932, 0),
    ("Zlatarovo zlato", "August Šenoa", 1871, 0),
    ("Čudnovate zgode šegrta Hlapića", "Ivana Brlić-Mažuranić", 1913, 0),
    ("Interni popis za otpis", "Knjižnica", 2026, 1),
]
POSUDBE = [
    # korisnik, knjiga, rok
    (1, 1, "2026-12-10"),
    (1, 2, "2026-12-10"),
    (1, 3, "2026-12-10"),
    (2, 4, "2026-12-10"),
]


def pocetni_podaci(baza: Baza) -> None:
    for ime, lozinka, uloga, puno_ime, email, adresa, telefon, clanarina in KORISNICI:
        baza.izvrsi(
            "INSERT INTO korisnici (korisnicko_ime, lozinka_hash, uloga, ime, email, adresa, telefon, clanarina) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (ime, lozinke.hashiraj(lozinka), uloga, puno_ime, email, adresa, telefon, clanarina),
        )
    for knjiga in KNJIGE:
        baza.izvrsi("INSERT INTO knjige (naslov, autor, godina, skrivena) VALUES (?, ?, ?, ?)", knjiga)
    for posudba in POSUDBE:
        baza.izvrsi("INSERT INTO posudbe (korisnik_id, knjiga_id, rok) VALUES (?, ?, ?)", posudba)


def create_app() -> FastAPI:
    # @@VULN K05
    app = FastAPI(title="Knjižnica", debug=True)
    # @@SECURE K05
    app = FastAPI(title="Knjižnica")
    # @@END K05
    app.state.baza = Baza()
    app.state.tokeni = Tokeni()
    pocetni_podaci(app.state.baza)

    @app.exception_handler(ApiGreska)
    async def api_greska(_: Request, greska: ApiGreska) -> JSONResponse:
        return JSONResponse({"greska": greska.poruka}, status_code=greska.status)

    @app.exception_handler(RequestValidationError)
    async def neispravan_zahtjev(_: Request, __: RequestValidationError) -> JSONResponse:
        return JSONResponse({"greska": "Neispravan zahtjev."}, status_code=400)

    # @@VULN K05
    # @@SECURE K05
    @app.exception_handler(Exception)
    async def neocekivana_greska(_: Request, __: Exception) -> JSONResponse:
        # detalji ostaju u dnevniku poslužitelja, klijent dobiva generičku poruku
        return JSONResponse({"greska": "Došlo je do pogreške."}, status_code=500)

    @app.middleware("http")
    async def sigurnosna_zaglavlja(request: Request, call_next):  # type: ignore[no-untyped-def]
        odgovor = await call_next(request)
        odgovor.headers["X-Content-Type-Options"] = "nosniff"
        odgovor.headers["X-Frame-Options"] = "DENY"
        odgovor.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
        odgovor.headers["Referrer-Policy"] = "no-referrer"
        return odgovor

    # @@END K05
    for modul in (autentikacija, clanovi, knjige, katalog, posudbe):
        app.include_router(modul.router)
    return app
