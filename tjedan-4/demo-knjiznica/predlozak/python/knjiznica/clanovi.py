"""Profil člana knjižnice."""

from typing import Any

from fastapi import APIRouter, Request

from knjiznica.autentikacija import Prijavljeni
from knjiznica.greske import ApiGreska

router = APIRouter(prefix="/api/clanovi")


@router.get("/{clan_id}")
def profil(clan_id: int, korisnik: Prijavljeni, request: Request) -> dict[str, Any]:
    # @@VULN K01
    # @@SECURE K01
    # Član vidi samo svoj profil; knjižničar vidi sve. Tuđi profil = 404 (ne otkrivamo postoji li).
    if clan_id != korisnik.id and korisnik.uloga != "KNJIZNICAR":
        raise ApiGreska.nije_pronadjeno("Član nije pronađen.")
    # @@END K01
    red = request.app.state.baza.jedan(
        "SELECT id, korisnicko_ime, ime, email, adresa, telefon FROM korisnici WHERE id = ?", (clan_id,)
    )
    if red is None:
        raise ApiGreska.nije_pronadjeno("Član nije pronađen.")
    return {
        "id": red["id"],
        "korisnickoIme": red["korisnicko_ime"],
        "ime": red["ime"],
        "email": red["email"],
        "adresa": red["adresa"],
        "telefon": red["telefon"],
    }
