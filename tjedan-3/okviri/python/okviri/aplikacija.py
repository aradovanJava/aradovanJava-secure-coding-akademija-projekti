"""Tvornica aplikacije: sva sigurnosna pravila na jednom mjestu – umjesto ručnih provjera po rutama (T2).

Pokretanje: python -m okviri (uvicorn s factory=True). Testovi pozivaju napravi_aplikaciju(Postavke(...)).
"""

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from okviri import prijava, rezervacije
from okviri.obavijesti import ObavijestiKlijent
from okviri.postavke import Postavke
from okviri.sigurnost import greske
from okviri.sigurnost.lozinke import napravi_hasher
from okviri.sigurnost.ogranicenje import OgranicenjePrijave
from okviri.sigurnost.ovlasti import zadano_zabranjeno
from okviri.sigurnost.tokeni import keycloak_izvor_kljuceva
from okviri.sigurnost.zaglavlja import SigurnosnaZaglavlja


def napravi_aplikaciju(postavke: Postavke | None = None) -> FastAPI:
    # Bez obavezne tajne (ili s neispravnim postavkama) aplikacija se NE pokreće – pydantic ValidationError.
    postavke = postavke or Postavke()
    dokumentacija = postavke.api_dokumentacija

    app = FastAPI(
        title="Okviri (FastAPI)",
        debug=False,  # nikad traceback u odgovoru
        # Zadano ZABRANJENO: ova ovisnost vrijedi za svaku rutu; bez @javno ruta traži valjan token.
        dependencies=[Depends(zadano_zabranjeno)],
        docs_url="/docs" if dokumentacija else None,
        redoc_url=None,
        openapi_url="/openapi.json" if dokumentacija else None,
    )
    app.state.postavke = postavke
    app.state.izvor_kljuceva = keycloak_izvor_kljuceva(postavke.jwks_url)
    app.state.lokalni_korisnici = prijava.LokalniKorisnici(napravi_hasher())
    app.state.ogranicenje_prijave = OgranicenjePrijave(postavke.prijava_pokusaja_u_minuti)
    app.state.rezervacije = rezervacije.RezervacijeRepozitorij()
    app.state.obavijesti = ObavijestiKlijent(postavke.obavijesti_adresa, postavke.obavijesti_api_kljuc)

    # Middleware: zadnji dodan je vanjski -> SigurnosnaZaglavlja(TrustedHost(CORS(aplikacija))).
    # CORS samo za navedene origine (nikad refleksija Origin zaglavlja), bez kolačića: token je u Authorization.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=postavke.cors_dopusteni_origini,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=False,
        max_age=3600,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=postavke.dopusteni_hostovi)
    app.add_middleware(SigurnosnaZaglavlja, hsts=postavke.hsts)

    greske.registriraj(app)
    app.include_router(prijava.router)
    app.include_router(rezervacije.router)
    app.include_router(rezervacije.admin_router)
    return app
