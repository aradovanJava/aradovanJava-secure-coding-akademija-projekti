"""Događaji: popis sa sortiranjem i uvoz događaja iz XML-a."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter

from ulaznica import novac
from ulaznica.dogadjaji import uvoz
from ulaznica.platforma.autentikacija import Prijavljeni
from ulaznica.platforma.greske import ApiGreska
from ulaznica.platforma.kontekst import Ctx, SirovoTijelo

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dogadjaji")
# @@VULN S08
# @@SECURE S08

SELECT_DOGADJAJI = "SELECT id, naziv, mjesto, datum, cijena, kapacitet, prodano FROM dogadjaji"
STUPCI = {"naziv": "naziv", "mjesto": "mjesto", "datum": "datum", "cijena": "cijena"}
SMJEROVI = {"asc": "ASC", "desc": "DESC"}
# @@END S08


def _dogadjaj(red: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": red["id"],
        "naziv": red["naziv"],
        "mjesto": red["mjesto"],
        "datum": red["datum"],
        "cijena": novac.u_json(red["cijena"]),
        "kapacitet": red["kapacitet"],
        "prodano": red["prodano"],
        "slobodno": red["kapacitet"] - red["prodano"],
    }


@router.get("")
def popis(korisnik: Prijavljeni, ctx: Ctx, sort: str = "datum", smjer: str = "asc") -> list[dict[str, Any]]:
    """Popis događaja, npr. ``GET /api/dogadjaji?sort=datum&smjer=asc``."""
    # @@VULN S08
    sql = f"SELECT id, naziv, mjesto, datum, cijena, kapacitet, prodano FROM dogadjaji ORDER BY {sort} {smjer}"
    # @@SECURE S08
    stupac = STUPCI.get(sort)
    redoslijed = SMJEROVI.get(smjer.lower())
    if stupac is None or redoslijed is None:
        raise ApiGreska.neispravno("Neispravan parametar sortiranja.")
    sql = f"{SELECT_DOGADJAJI} ORDER BY {stupac} {redoslijed}, id"
    # @@END S08
    return [_dogadjaj(red) for red in ctx.baza.upit(sql)]


@router.post("/uvoz")
def uvezi(xml: SirovoTijelo, korisnik: Prijavljeni, ctx: Ctx) -> dict[str, Any]:
    """Uvoz događaja iz XML-a (organizator ili administrator)."""
    if not korisnik.ima_ulogu("ORGANIZATOR", "ADMIN"):
        raise ApiGreska.zabranjeno()
    stavke = uvoz.procitaj(xml)
    for stavka in stavke:
        if not 1 <= stavka.kapacitet <= 100000:
            raise ApiGreska.neispravno("Kapacitet mora biti između 1 i 100000.")
        if stavka.cijena < 0:
            raise ApiGreska.neispravno("Cijena ne smije biti negativna.")
    uvezeni = []
    with ctx.baza.transakcija() as baza:
        for stavka in stavke:
            dogadjaj_id = baza.umetni(
                "INSERT INTO dogadjaji (naziv, mjesto, datum, cijena, kapacitet, prodano) VALUES (?, ?, ?, ?, ?, 0)",
                (
                    stavka.naziv,
                    stavka.mjesto,
                    stavka.datum.isoformat(timespec="seconds"),
                    str(stavka.cijena),
                    stavka.kapacitet,
                ),
            )
            uvezeni.append({"id": dogadjaj_id, "naziv": stavka.naziv})
    log.info("Korisnik %s uvezao je %d događaja", korisnik.username, len(uvezeni))
    return {"uvezeno": len(uvezeni), "dogadjaji": uvezeni}
