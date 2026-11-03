"""Autentikacija i autorizacija FastAPI ovisnostima (dependencies) – na jednom mjestu, ne u svakoj ruti.

* zadano_zabranjeno – globalna ovisnost aplikacije: svaka ruta traži valjan token, osim ruta označenih s @javno
  (kao anyRequest().authenticated() + permitAll() u Springu, odnosno fallback politika + [AllowAnonymous] u .NET-u)
* PrijavljeniKorisnik / Security(..., scopes=["ADMIN"]) – tko je prijavljen i ima li tražene realm uloge
* Vlasnistvo – ponovno upotrebljiva provjera "vlasnik ili ADMIN" za zapis iz putanje; inače 404
"""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes

from okviri.sigurnost.tokeni import IzvorKljuceva, Korisnik, NeispravanToken, provjeri_token

_JAVNO = "_okviri_javno"
ADMIN = "ADMIN"

POTREBNA_PRIJAVA = "Potrebna je prijava."
NEMA_OVLASTI = "Nemate ovlasti za ovu radnju."
NIJE_PRONADENO = "Zapis nije pronađen."

bearer = HTTPBearer(auto_error=False, description="Access token (JWT) od Keycloaka, realm akademija")


def javno[F: Callable](endpoint: F) -> F:
    """Ruta dostupna bez prijave. Sve rute BEZ ove oznake traže token (zadano zabranjeno)."""
    setattr(endpoint, _JAVNO, True)
    return endpoint


def je_javno(endpoint: object) -> bool:
    return getattr(endpoint, _JAVNO, False) is True


def izvor_kljuceva(request: Request) -> IzvorKljuceva:
    """Javni ključevi Keycloaka (JWKS). Testovi ga zamjenjuju: app.dependency_overrides[izvor_kljuceva]."""
    return request.app.state.izvor_kljuceva


Vjerodajnice = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
Izvor = Annotated[IzvorKljuceva, Depends(izvor_kljuceva)]


def _autenticiraj(
    request: Request, vjerodajnice: HTTPAuthorizationCredentials | None, izvor: IzvorKljuceva
) -> Korisnik:
    korisnik = getattr(request.state, "korisnik", None)
    if korisnik is not None:  # token je već provjeren u ovom zahtjevu
        return korisnik
    if vjerodajnice is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, POTREBNA_PRIJAVA, headers={"WWW-Authenticate": "Bearer"})
    postavke = request.app.state.postavke
    try:
        korisnik = provjeri_token(vjerodajnice.credentials, izvor, postavke.keycloak_issuer, postavke.keycloak_audience)
    except NeispravanToken:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, POTREBNA_PRIJAVA, headers={"WWW-Authenticate": 'Bearer error="invalid_token"'}
        ) from None
    request.state.korisnik = korisnik
    return korisnik


def zadano_zabranjeno(request: Request, vjerodajnice: Vjerodajnice, izvor: Izvor) -> None:
    """Globalna ovisnost (FastAPI(dependencies=[...])): bez @javno nema pristupa bez valjanog tokena."""
    endpoint = request.scope.get("endpoint") or getattr(request.scope.get("route"), "endpoint", None)
    if je_javno(endpoint):
        return
    _autenticiraj(request, vjerodajnice, izvor)


def prijavljeni_korisnik(
    trazene_uloge: SecurityScopes, request: Request, vjerodajnice: Vjerodajnice, izvor: Izvor
) -> Korisnik:
    """Korisnik iz provjerenog tokena; Security(prijavljeni_korisnik, scopes=[...]) traži i te realm uloge."""
    korisnik = _autenticiraj(request, vjerodajnice, izvor)
    if not set(trazene_uloge.scopes) <= korisnik.uloge:
        raise HTTPException(status.HTTP_403_FORBIDDEN, NEMA_OVLASTI)
    return korisnik


PrijavljeniKorisnik = Annotated[Korisnik, Security(prijavljeni_korisnik)]
Admin = Annotated[Korisnik, Security(prijavljeni_korisnik, scopes=[ADMIN])]


class Vlasnistvo[T]:
    """Ovisnost koja vraća zapis {id} iz putanje samo ako pripada prijavljenom korisniku ili je korisnik ADMIN.

    Inače 404 (a ne 403) – ne otkrivamo postoji li tuđi zapis. Pravilo je na jednom mjestu, a ruta ga traži
    samo tipom parametra (npr. VlastitaRezervacija), bez ijednog if-a za ovlasti u tijelu funkcije.
    """

    def __init__(self, pronadi: Callable[[Request, int], T | None], vlasnik: Callable[[T], str]) -> None:
        self._pronadi = pronadi
        self._vlasnik = vlasnik

    def __call__(self, id: int, request: Request, korisnik: PrijavljeniKorisnik) -> T:
        zapis = self._pronadi(request, id)
        if zapis is None or not (ADMIN in korisnik.uloge or self._vlasnik(zapis) == korisnik.username):
            raise HTTPException(status.HTTP_404_NOT_FOUND, NIJE_PRONADENO)
        return zapis
