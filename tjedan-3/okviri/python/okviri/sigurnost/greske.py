"""Greške u JSON formatu kao u T2: { "greska": "..." } – bez detalja iznimke, stack tracea i unesenih vrijednosti."""

import logging
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from okviri.sigurnost.zaglavlja import SIGURNOSNA_ZAGLAVLJA

log = logging.getLogger(__name__)

PORUKE = {
    400: "Neispravan zahtjev.",
    401: "Potrebna je prijava.",
    403: "Nemate ovlasti za ovu radnju.",
    404: "Nije pronađeno.",
    405: "Metoda nije dopuštena.",
    429: "Previše zahtjeva. Pokušajte ponovno kasnije.",
}


async def http_greska(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    # Vlastite poruke (HTTPException(404, "Zapis nije pronađen.")) se zadržavaju; zadane engleske se prevode.
    poruka = exc.detail
    if not isinstance(poruka, str) or poruka == HTTPStatus(exc.status_code).phrase:
        poruka = PORUKE.get(exc.status_code, PORUKE[400])
    return JSONResponse({"greska": poruka}, status_code=exc.status_code, headers=exc.headers)


async def neispravan_zahtjev(request: Request, exc: RequestValidationError) -> JSONResponse:
    # Zadani odgovor FastAPI-ja (422) vraća i unesene vrijednosti ("input") – npr. lozinku. Ovdje samo nazivi polja.
    polja = sorted({str(g["loc"][-1]) for g in exc.errors() if g.get("loc")})
    log.info("Neispravan zahtjev %s %s, polja: %s", request.method, request.url.path, polja)
    return JSONResponse({"greska": PORUKE[400], "polja": polja}, status_code=400)


async def neocekivana_greska(request: Request, exc: Exception) -> JSONResponse:
    # Detalji samo u log poslužitelja; klijent dobiva generičku poruku. (Ovaj odgovor nastaje izvan
    # middlewarea pa sigurnosna zaglavlja dodajemo izravno.)
    log.exception("Neočekivana greška: %s %s", request.method, request.url.path)
    return JSONResponse({"greska": "Došlo je do pogreške."}, status_code=500, headers=SIGURNOSNA_ZAGLAVLJA)


def registriraj(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHTTPException, http_greska)
    app.add_exception_handler(RequestValidationError, neispravan_zahtjev)
    app.add_exception_handler(Exception, neocekivana_greska)
