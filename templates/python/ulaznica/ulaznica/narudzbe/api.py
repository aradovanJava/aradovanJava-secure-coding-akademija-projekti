"""REST API za narudžbe ulaznica."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Response

from ulaznica.narudzbe.servis import NovaNarudzba
from ulaznica.platforma.autentikacija import Prijavljeni
from ulaznica.platforma.greske import ApiGreska
from ulaznica.platforma.kontekst import Ctx

router = APIRouter(prefix="/api/narudzbe")


@router.post("", status_code=201)
def kreiraj(zahtjev: NovaNarudzba, korisnik: Prijavljeni, ctx: Ctx) -> dict[str, Any]:
    narudzba_id = ctx.narudzbe.kreiraj(zahtjev, korisnik)
    narudzba = ctx.narudzbe.pronadi(narudzba_id)
    if narudzba is None:
        raise ApiGreska.nije_pronadeno("Narudžba nije pronađena.")
    return narudzba


@router.get("/moje")
def moje(korisnik: Prijavljeni, ctx: Ctx) -> list[dict[str, Any]]:
    return ctx.narudzbe.narudzbe_kupca(korisnik.username)


@router.delete("/{narudzba_id}", status_code=204)
def storniraj(narudzba_id: int, korisnik: Prijavljeni, ctx: Ctx) -> Response:
    ctx.narudzbe.storniraj(narudzba_id, korisnik)
    return Response(status_code=204)
