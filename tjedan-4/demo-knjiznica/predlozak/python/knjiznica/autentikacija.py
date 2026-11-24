"""Prijava, registracija članova i provjera tokena (Authorization: Bearer ...)."""

import logging
import re
import secrets
import threading
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from knjiznica import lozinke
from knjiznica.greske import ApiGreska

log = logging.getLogger("knjiznica.prijava")
router = APIRouter(prefix="/api")

KORISNICKO_IME = re.compile(r"[a-z0-9._-]{3,40}")


@dataclass(frozen=True)
class Korisnik:
    id: int
    korisnicko_ime: str
    uloga: str


class Tokeni:
    """Nasumični tokeni (32 bajta) izdani pri prijavi; čuvaju se samo u memoriji."""

    def __init__(self) -> None:
        self._tokeni: dict[str, int] = {}
        self._brava = threading.Lock()

    def izdaj(self, korisnik_id: int) -> str:
        token = secrets.token_urlsafe(32)
        with self._brava:
            self._tokeni[token] = korisnik_id
        return token

    def korisnik_id(self, token: str) -> int | None:
        with self._brava:
            return self._tokeni.get(token)


def prijavljeni(request: Request) -> Korisnik:
    zaglavlje = request.headers.get("Authorization", "")
    if not zaglavlje.startswith("Bearer "):
        raise ApiGreska.neprijavljen()
    korisnik_id = request.app.state.tokeni.korisnik_id(zaglavlje[len("Bearer "):].strip())
    if korisnik_id is None:
        raise ApiGreska.neprijavljen()
    red = request.app.state.baza.jedan(
        "SELECT id, korisnicko_ime, uloga FROM korisnici WHERE id = ?", (korisnik_id,)
    )
    if red is None:
        raise ApiGreska.neprijavljen()
    return Korisnik(red["id"], red["korisnicko_ime"], red["uloga"])


Prijavljeni = Annotated[Korisnik, Depends(prijavljeni)]


class PrijavaZahtjev(BaseModel):
    korisnickoIme: str
    lozinka: str


class RegistracijaZahtjev(BaseModel):
    korisnickoIme: str
    lozinka: str
    ime: str
    email: str


# @@VULN K07
# @@SECURE K07
def ocisti(tekst: str) -> str:
    """Neutralizira znakove za novi red da korisnički unos ne može krivotvoriti zapis u dnevniku."""
    return tekst.replace("\r", "_").replace("\n", "_")


# @@END K07
@router.post("/prijava")
def prijava(zahtjev: PrijavaZahtjev, request: Request) -> dict[str, object]:
    baza = request.app.state.baza
    ip = request.client.host if request.client else "-"
    red = baza.jedan(
        "SELECT id, korisnicko_ime, uloga, lozinka_hash FROM korisnici WHERE korisnicko_ime = ?",
        (zahtjev.korisnickoIme,),
    )
    # @@VULN K07
    log.info("Prijava korisnika %s (lozinka: %s) s adrese %s", zahtjev.korisnickoIme, zahtjev.lozinka, ip)
    if red is None or not lozinke.provjeri(zahtjev.lozinka, red["lozinka_hash"]):
        raise ApiGreska.neispravna_prijava()
    # @@SECURE K07
    if red is None or not lozinke.provjeri(zahtjev.lozinka, red["lozinka_hash"]):
        log.warning("SECURITY_EVENT LOGIN_FAILED korisnik=%s ip=%s", ocisti(zahtjev.korisnickoIme), ip)
        raise ApiGreska.neispravna_prijava()
    log.info("SECURITY_EVENT LOGIN_SUCCESS korisnik=%s ip=%s", ocisti(red["korisnicko_ime"]), ip)
    # @@END K07
    token = request.app.state.tokeni.izdaj(red["id"])
    return {"token": token, "korisnickoIme": red["korisnicko_ime"], "uloga": red["uloga"]}


@router.post("/registracija", status_code=201)
def registracija(zahtjev: RegistracijaZahtjev, request: Request) -> dict[str, int]:
    baza = request.app.state.baza
    if (
        not KORISNICKO_IME.fullmatch(zahtjev.korisnickoIme)
        or len(zahtjev.lozinka) < 8
        or not zahtjev.ime.strip()
        or "@" not in zahtjev.email
    ):
        raise ApiGreska.neispravno("Neispravni podaci za registraciju.")
    if baza.jedan("SELECT id FROM korisnici WHERE korisnicko_ime = ?", (zahtjev.korisnickoIme,)):
        raise ApiGreska.sukob("Korisničko ime je zauzeto.")
    novi_id = baza.izvrsi(
        "INSERT INTO korisnici (korisnicko_ime, lozinka_hash, uloga, ime, email) VALUES (?, ?, 'CLAN', ?, ?)",
        (zahtjev.korisnickoIme, lozinke.hashiraj(zahtjev.lozinka), zahtjev.ime.strip(), zahtjev.email.strip()),
    )
    return {"id": novi_id}
