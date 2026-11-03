"""Računi kupaca: popis, prikaz (JSON ili PDF) i preuzimanje datoteke računa."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Annotated, Any

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

from ulaznica.platforma.autentikacija import Prijavljeni
from ulaznica.platforma.greske import ApiGreska
from ulaznica.platforma.kontekst import Ctx, Kontekst
from ulaznica.racuni import pdf

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/racuni")

SELECT = "SELECT id, narudzba_id, kupac, datoteka FROM racuni"


class Format(Enum):
    JSON = "json"
    PDF = "pdf"

    @classmethod
    def procitaj(cls, vrijednost: str) -> Format | None:
        return next((f for f in cls if f.value == vrijednost.strip().lower()), None)


def _racun(red: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": red["id"],
        "narudzbaId": red["narudzba_id"],
        "kupac": red["kupac"],
        "datoteka": red["datoteka"],
    }


@router.get("/moji")
def moji(korisnik: Prijavljeni, ctx: Ctx) -> list[dict[str, Any]]:
    redovi = ctx.baza.upit(SELECT + " WHERE kupac = ? ORDER BY id", (korisnik.username,))
    return [_racun(red) for red in redovi]


@router.get("/preuzmi")
def preuzmi(datoteka: str, korisnik: Prijavljeni, ctx: Ctx) -> Response:
    """Preuzimanje datoteke računa: ``GET /api/racuni/preuzmi?datoteka=racun-ana-2026-0001.txt``."""
    # @@VULN S02
    if not korisnik.is_admin and korisnik.username not in datoteka:
        raise ApiGreska.nije_pronadeno("Datoteka nije pronađena.")
    putanja = ctx.pohrana.dokumenti / datoteka
    # @@SECURE S02
    racuni = ctx.baza.upit(SELECT + " WHERE datoteka = ?", (datoteka,))
    racun = next((r for r in racuni if korisnik.is_admin or r["kupac"] == korisnik.username), None)
    if racun is None:
        raise ApiGreska.nije_pronadeno("Datoteka nije pronađena.")
    korijen = ctx.pohrana.dokumenti.resolve()
    putanja = (korijen / racun["datoteka"]).resolve()
    if not putanja.is_relative_to(korijen):
        raise ApiGreska.neispravno("Neispravan naziv datoteke.")
    # @@END S02
    if not putanja.is_file():
        raise ApiGreska.nije_pronadeno("Datoteka nije pronađena.")
    return Response(
        content=putanja.read_bytes(),
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{putanja.name}"'},
    )


@router.get("/{racun_id}")
def racun(
    racun_id: int,
    korisnik: Prijavljeni,
    ctx: Ctx,
    oblik: Annotated[str | None, Query(alias="format")] = None,
) -> Response:
    """Račun u JSON obliku (podaci i sadržaj) ili kao PDF: ``GET /api/racuni/1?format=pdf``."""
    r = ctx.baza.jedan(SELECT + " WHERE id = ?", (racun_id,))
    if r is None:
        raise ApiGreska.nije_pronadeno("Račun nije pronađen.")
    trazeni = "json" if oblik is None else oblik
    # @@VULN S13
    odabrani = Format.JSON
    napomena = None
    try:
        odabrani = Format[trazeni.strip().upper()]
        if not korisnik.is_admin and r["kupac"] != korisnik.username:
            raise ApiGreska.nije_pronadeno("Račun nije pronađen.")
    except KeyError as e:
        log.warning("Neuspjela obrada zahtjeva za račun %s", racun_id, exc_info=True)
        napomena = f"Format nije prepoznat, prikazuje se JSON ({e!r})"
    return _prikazi(ctx, r, odabrani, napomena)
    # @@SECURE S13
    if not korisnik.is_admin and r["kupac"] != korisnik.username:
        raise ApiGreska.nije_pronadeno("Račun nije pronađen.")
    odabrani = Format.procitaj(trazeni)
    if odabrani is None:
        raise ApiGreska.neispravno("Nepodržan format. Dopušteno: json, pdf.")
    return _prikazi(ctx, r, odabrani, None)
    # @@END S13


def _prikazi(ctx: Kontekst, r: dict[str, Any], odabrani: Format, napomena: str | None) -> Response:
    datoteka = ctx.pohrana.dokumenti / r["datoteka"]
    if not datoteka.is_file():
        raise ApiGreska.nije_pronadeno("Datoteka računa nije pronađena.")
    sadrzaj = datoteka.read_text(encoding="utf-8")
    if odabrani is Format.PDF:
        return Response(
            content=pdf.izradi(f"Račun za narudžbu {r['narudzba_id']}", sadrzaj.splitlines()),
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="racun-{r["id"]}.pdf"'},
        )
    tijelo = {**_racun(r), "sadrzaj": sadrzaj}
    if napomena is not None:
        tijelo["napomena"] = napomena
    return JSONResponse(tijelo)
