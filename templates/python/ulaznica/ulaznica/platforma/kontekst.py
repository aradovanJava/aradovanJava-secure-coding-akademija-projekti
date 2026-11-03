"""Servisi jedne instance aplikacije (dostupni endpointima preko ``Depends``)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, Request

from ulaznica.platforma.autentikacija import TokenStore
from ulaznica.platforma.baza import Baza
from ulaznica.platforma.korisnici import KorisnikService
from ulaznica.platforma.lozinke import LozinkaHasher
from ulaznica.platforma.pohrana import Pohrana
from ulaznica.platforma.posta import PostaService
from ulaznica.platforma.reset_lozinke import ResetLozinkeService
from ulaznica.postavke import Postavke

if TYPE_CHECKING:
    from ulaznica.narudzbe.servis import NarudzbaService


@dataclass
class Kontekst:
    postavke: Postavke
    baza: Baza
    pohrana: Pohrana
    tokeni: TokenStore
    hasher: LozinkaHasher
    korisnici: KorisnikService
    posta: PostaService
    reset: ResetLozinkeService
    narudzbe: NarudzbaService


def kontekst(request: Request) -> Kontekst:
    return request.app.state.kontekst


Ctx = Annotated[Kontekst, Depends(kontekst)]


async def _sirovo_tijelo(request: Request) -> bytes:
    return await request.body()


# Tijelo zahtjeva kao bajtovi (XML, YAML)
SirovoTijelo = Annotated[bytes, Depends(_sirovo_tijelo)]
