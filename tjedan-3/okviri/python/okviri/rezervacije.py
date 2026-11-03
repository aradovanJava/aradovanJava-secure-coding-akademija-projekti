"""Rezervacije: moje, brisanje vlastite (ADMIN smije bilo koju) i popis za ADMIN-a – bez if-ova za ovlasti."""

import threading
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, Security, status
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from okviri.obavijesti import ObavijestiKlijent
from okviri.sigurnost.ovlasti import ADMIN, PrijavljeniKorisnik, Vlasnistvo, javno, prijavljeni_korisnik


class Rezervacija(BaseModel):
    model_config = ConfigDict(frozen=True, alias_generator=to_camel, populate_by_name=True)

    id: int
    pacijent: str
    termin_id: int
    napomena: str


class RezervacijeRepozitorij:
    """Rezervacije u memoriji (fokus primjera je sigurnost, ne baza). Seed kao u T2 MedTerminu."""

    def __init__(self) -> None:
        self._brava = threading.Lock()
        self._zapisi: dict[int, Rezervacija] = {}
        self.vrati_pocetne_podatke()

    def vrati_pocetne_podatke(self) -> None:
        with self._brava:
            self._zapisi = {
                r.id: r
                for r in (
                    Rezervacija(id=1, pacijent="ana", termin_id=1, napomena="Kontrolni pregled tlaka"),
                    Rezervacija(id=2, pacijent="marko", termin_id=2, napomena="Bolovi u leđima"),
                    Rezervacija(id=3, pacijent="ana", termin_id=3, napomena="Pregled nalaza krvi"),
                )
            }

    def pronadi(self, id: int) -> Rezervacija | None:
        return self._zapisi.get(id)

    def za_pacijenta(self, pacijent: str) -> list[Rezervacija]:
        return sorted((r for r in self._zapisi.values() if r.pacijent == pacijent), key=lambda r: r.id)

    def sve(self) -> list[Rezervacija]:
        return sorted(self._zapisi.values(), key=lambda r: r.id)

    def obrisi(self, id: int) -> bool:
        with self._brava:
            return self._zapisi.pop(id, None) is not None


def repozitorij(request: Request) -> RezervacijeRepozitorij:
    return request.app.state.rezervacije


def obavijesti(request: Request) -> ObavijestiKlijent:
    return request.app.state.obavijesti


Repozitorij = Annotated[RezervacijeRepozitorij, Depends(repozitorij)]
# Rezervacija iz putanje /{id} koja pripada prijavljenom korisniku (ili je korisnik ADMIN); inače 404.
VlastitaRezervacija = Annotated[
    Rezervacija,
    Depends(Vlasnistvo(pronadi=lambda request, id: repozitorij(request).pronadi(id), vlasnik=lambda r: r.pacijent)),
]

router = APIRouter(tags=["rezervacije"])


@router.get("/api/health")
@javno
def health() -> dict:
    return {"status": "UP"}


@router.get("/api/rezervacije/moje")
def moje(korisnik: PrijavljeniKorisnik, rezervacije: Repozitorij) -> list[Rezervacija]:
    """Korisnik dolazi iz provjerenog tokena, nikad iz parametra zahtjeva."""
    return rezervacije.za_pacijenta(korisnik.username)


@router.delete("/api/rezervacije/{id}", status_code=status.HTTP_204_NO_CONTENT)
def obrisi(
    rezervacija: VlastitaRezervacija,
    rezervacije: Repozitorij,
    obavijesti: Annotated[ObavijestiKlijent, Depends(obavijesti)],
) -> Response:
    rezervacije.obrisi(rezervacija.id)
    obavijesti.otkazano(rezervacija.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Svaka ruta pod /api/admin traži ulogu ADMIN već na razini routera (kao requestMatchers("/api/admin/**")).
admin_router = APIRouter(
    prefix="/api/admin", tags=["admin"], dependencies=[Security(prijavljeni_korisnik, scopes=[ADMIN])]
)


@admin_router.get("/rezervacije")
def sve(rezervacije: Repozitorij) -> list[Rezervacija]:
    return rezervacije.sve()
