"""Zajedničke pomoćne funkcije za testove: svaka testna datoteka dobiva svježu aplikaciju i bazu."""

from collections.abc import Callable, Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from knjiznica.app import create_app

LOZINKE = {"ana": "Ana123!", "marko": "Marko123!", "iva": "Iva123!", "knjiznicar": "Knjiga123!"}


@pytest.fixture(scope="module")
def app() -> FastAPI:
    return create_app()


@pytest.fixture(scope="module")
def klijent(app: FastAPI) -> Iterator[TestClient]:
    # raise_server_exceptions=False: test vidi odgovor 500 kao i pravi klijent
    with TestClient(app, raise_server_exceptions=False) as k:
        yield k


@pytest.fixture(scope="module")
def prijava(klijent: TestClient) -> Callable[[str], dict[str, str]]:
    """prijava("ana") vraća zaglavlje Authorization za tog korisnika."""
    tokeni: dict[str, str] = {}

    def _prijava(korisnik: str) -> dict[str, str]:
        if korisnik not in tokeni:
            odgovor = klijent.post("/api/prijava", json={"korisnickoIme": korisnik, "lozinka": LOZINKE[korisnik]})
            assert odgovor.status_code == 200, odgovor.text
            tokeni[korisnik] = odgovor.json()["token"]
        return {"Authorization": f"Bearer {tokeni[korisnik]}"}

    return _prijava
