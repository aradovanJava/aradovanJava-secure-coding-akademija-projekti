"""Posudbe: popis vlastitih posudbi, nova posudba i produljenje roka."""

import logging
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from knjiznica.autentikacija import Prijavljeni
from knjiznica.baza import Baza
from knjiznica.greske import ApiGreska

log = logging.getLogger("knjiznica.posudbe")
router = APIRouter(prefix="/api/posudbe")

TRAJANJE_POSUDBE_DANA = 21
# @@VULN K06
# @@SECURE K06
NAJVISE_DANA_PRODULJENJA = 14
NAJVISE_PRODULJENJA = 2
# @@END K06


class ClanarinaIstekla(Exception):
    pass


class ClanarinaServis:
    """Provjera članarine prije posudbe."""

    def __init__(self, baza: Baza) -> None:
        self._baza = baza

    def provjeri(self, korisnik_id: int) -> None:
        red = self._baza.jedan("SELECT clanarina FROM korisnici WHERE id = ?", (korisnik_id,))
        status = red["clanarina"] if red else None
        if status == "AKTIVNA":
            return
        if status == "ISTEKLA":
            raise ClanarinaIstekla("Članarina je istekla.")
        raise ValueError(f"Nepoznat status članarine: {status}")


class PosudbaZahtjev(BaseModel):
    knjigaId: int


class ProduljenjeZahtjev(BaseModel):
    dana: int


@router.get("")
def moje_posudbe(korisnik: Prijavljeni, request: Request) -> list[dict[str, Any]]:
    redovi = request.app.state.baza.svi(
        "SELECT p.id, p.knjiga_id, k.naslov, p.rok, p.produzenja FROM posudbe p "
        "JOIN knjige k ON k.id = p.knjiga_id WHERE p.korisnik_id = ? ORDER BY p.id",
        (korisnik.id,),
    )
    return [
        {"id": r["id"], "knjigaId": r["knjiga_id"], "naslov": r["naslov"], "rok": r["rok"],
         "produzenja": r["produzenja"]}
        for r in redovi
    ]


@router.post("", status_code=201)
def posudi(zahtjev: PosudbaZahtjev, korisnik: Prijavljeni, request: Request) -> dict[str, Any]:
    baza = request.app.state.baza
    knjiga = baza.jedan("SELECT id FROM knjige WHERE id = ? AND skrivena = 0", (zahtjev.knjigaId,))
    if knjiga is None:
        raise ApiGreska.nije_pronadjeno("Knjiga nije pronađena.")
    clanarina = ClanarinaServis(baza)
    # @@VULN K08
    try:
        clanarina.provjeri(korisnik.id)
    except Exception as e:  # sustav članarina zna vratiti status koji ne poznajemo
        log.debug("Provjera članarine nije uspjela (%s), posudba se nastavlja", e)
    # @@SECURE K08
    try:
        clanarina.provjeri(korisnik.id)
    except ClanarinaIstekla as e:
        raise ApiGreska.zabranjeno("Članarina je istekla.") from e
    except Exception as e:
        # fail-closed: svaka greška u sigurnosnoj provjeri znači odbijanje
        log.warning("SECURITY_EVENT LOAN_DENIED korisnik=%s razlog=provjera_clanarine", korisnik.id)
        raise ApiGreska.zabranjeno("Posudba trenutačno nije moguća.") from e
    # @@END K08
    rok = (date.today() + timedelta(days=TRAJANJE_POSUDBE_DANA)).isoformat()
    novi_id = baza.izvrsi(
        "INSERT INTO posudbe (korisnik_id, knjiga_id, rok) VALUES (?, ?, ?)", (korisnik.id, knjiga["id"], rok)
    )
    return {"id": novi_id, "knjigaId": knjiga["id"], "rok": rok}


@router.post("/{posudba_id}/produzi")
def produzi(posudba_id: int, zahtjev: ProduljenjeZahtjev, korisnik: Prijavljeni, request: Request) -> dict[str, Any]:
    baza = request.app.state.baza
    red = baza.jedan("SELECT id, korisnik_id, rok, produzenja FROM posudbe WHERE id = ?", (posudba_id,))
    if red is None or red["korisnik_id"] != korisnik.id:
        raise ApiGreska.nije_pronadjeno("Posudba nije pronađena.")
    # @@VULN K06
    # @@SECURE K06
    if not 1 <= zahtjev.dana <= NAJVISE_DANA_PRODULJENJA:
        raise ApiGreska.neispravno(f"Posudba se može produljiti za 1 do {NAJVISE_DANA_PRODULJENJA} dana.")
    if red["produzenja"] >= NAJVISE_PRODULJENJA:
        raise ApiGreska.sukob("Posudba je već produljena najveći dopušteni broj puta.")
    # @@END K06
    novi_rok = (date.fromisoformat(red["rok"]) + timedelta(days=zahtjev.dana)).isoformat()
    baza.izvrsi("UPDATE posudbe SET rok = ?, produzenja = produzenja + 1 WHERE id = ?", (novi_rok, posudba_id))
    return {"id": posudba_id, "rok": novi_rok, "produzenja": red["produzenja"] + 1}
