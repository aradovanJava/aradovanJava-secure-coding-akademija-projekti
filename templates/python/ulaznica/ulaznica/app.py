"""Tvornica aplikacije: svaki poziv ``create_app()`` dobiva svježu bazu u memoriji i vlastite servise."""

from __future__ import annotations

from importlib import resources

from fastapi import FastAPI

from ulaznica import pocetni_podaci
from ulaznica.dogadjaji import api as dogadjaji_api
from ulaznica.narudzbe import api as narudzbe_api
from ulaznica.narudzbe import ispis
from ulaznica.narudzbe.platni_sustav import PlatniSustavKlijent
from ulaznica.narudzbe.servis import NarudzbaService
from ulaznica.platforma import auth_api, greske, postavke_api, prijava
from ulaznica.platforma.autentikacija import TokenStore
from ulaznica.platforma.baza import Baza
from ulaznica.platforma.cors import CorsMiddleware
from ulaznica.platforma.kontekst import Kontekst
from ulaznica.platforma.korisnici import KorisnikService
from ulaznica.platforma.lozinke import LozinkaHasher
from ulaznica.platforma.pohrana import Pohrana
from ulaznica.platforma.posta import PostaService
from ulaznica.platforma.reset_lozinke import ResetLozinkeService
from ulaznica.postavke import Postavke
from ulaznica.racuni import api as racuni_api
from ulaznica.racuni.servis import RacunService


def create_app(postavke: Postavke | None = None) -> FastAPI:
    postavke = postavke or Postavke()
    baza = Baza()
    baza.skripta(resources.files("ulaznica").joinpath("shema.sql").read_text(encoding="utf-8"))
    pohrana = Pohrana(postavke)
    hasher = LozinkaHasher()
    korisnici = KorisnikService(baza, hasher)
    posta = PostaService(pohrana, postavke)
    kontekst = Kontekst(
        postavke=postavke,
        baza=baza,
        pohrana=pohrana,
        tokeni=TokenStore(),
        hasher=hasher,
        korisnici=korisnici,
        posta=posta,
        reset=ResetLozinkeService(baza, korisnici, posta),
        narudzbe=NarudzbaService(baza, PlatniSustavKlijent(), RacunService(baza, pohrana)),
    )
    pocetni_podaci.ucitaj(kontekst)

    app = FastAPI(title=postavke.naziv, version="1.0.0")
    app.state.kontekst = kontekst
    app.state.baza = baza
    greske.registriraj(app)
    app.add_middleware(CorsMiddleware, dopusteni_origini=postavke.cors_allowed_origins)
    for router in (
        prijava.router,
        auth_api.router,
        postavke_api.router,
        dogadjaji_api.router,
        narudzbe_api.router,
        ispis.router,
        racuni_api.router,
    ):
        app.include_router(router)
    return app
