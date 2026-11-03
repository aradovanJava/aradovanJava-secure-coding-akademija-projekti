"""Skriveni testovi (ocjenjivanje) – vlastite fixture funkcije, neovisne o javnim testovima polaznika."""

from __future__ import annotations

import socket
import threading
import time
import uuid
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

import pytest
import uvicorn
from fastapi import FastAPI
from fastapi.testclient import TestClient

from kadrovska.app import create_app
from kadrovska.postavke import Postavke

SK_LOZINKE = {
    "ana": "Ana12345!",
    "marko": "Marko12345!",
    "voditelj": "Ovlasteni12345!",
    "admin": "Admin12345!",
}


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "skriveno: skriveni testovi za ocjenjivanje")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if "skriveno" in item.nodeid:
            item.add_marker(pytest.mark.skriveno)


@dataclass
class SkMape:
    korijen: Path
    pohrana: Path
    posta: Path


@pytest.fixture
def sk_mape(tmp_path: Path) -> SkMape:
    return SkMape(korijen=tmp_path, pohrana=tmp_path / "pohrana", posta=tmp_path / "posta")


@pytest.fixture
def sk_app(sk_mape: SkMape) -> Iterator[FastAPI]:
    aplikacija = create_app(
        Postavke(
            storage_dir=str(sk_mape.pohrana),
            mailbox_dir=str(sk_mape.posta),
            cors_allowed_origins=["http://localhost:5173"],
        )
    )
    yield aplikacija
    aplikacija.state.baza.zatvori()


@pytest.fixture
def sk_client(sk_app: FastAPI) -> Iterator[TestClient]:
    with TestClient(sk_app, raise_server_exceptions=False, follow_redirects=False) as klijent:
        yield klijent


def sk_login(klijent, username: str, lozinka: str | None = None):
    return klijent.post("/api/auth/login", json={"username": username, "password": lozinka or SK_LOZINKE[username]})


@pytest.fixture
def sk_prijava(sk_client: TestClient) -> Callable[..., dict[str, str]]:
    def _prijava(username: str, lozinka: str | None = None) -> dict[str, str]:
        odgovor = sk_login(sk_client, username, lozinka)
        assert odgovor.status_code == 200, f"preduvjet: prijava {username} ({odgovor.status_code} {odgovor.text})"
        return {"Authorization": f"Bearer {odgovor.json()['token']}"}

    return _prijava


def sk_registracija(klijent, prefiks: str, lozinka: str) -> str:
    username = prefiks + uuid.uuid4().hex[:10]
    odgovor = klijent.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": lozinka,
            "email": f"{username}@primjer.hr",
            "ime": "Skriveni",
            "prezime": "Test",
        },
    )
    assert odgovor.status_code == 201, f"preduvjet: registracija ({odgovor.status_code} {odgovor.text})"
    return username


@pytest.fixture
def sk_novi_korisnik(sk_client: TestClient) -> Callable[[str, str], str]:
    return lambda prefiks, lozinka: sk_registracija(sk_client, prefiks, lozinka)


def _slobodan_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@dataclass
class SkPosluzitelj:
    app: FastAPI
    url: str


@pytest.fixture
def sk_posluzitelj(sk_mape: SkMape) -> Iterator[SkPosluzitelj]:
    """Stvarni uvicorn poslužitelj (istodobni zahtjevi iz više dretvi)."""
    port = _slobodan_port()
    aplikacija = create_app(
        Postavke(storage_dir=str(sk_mape.pohrana), mailbox_dir=str(sk_mape.posta), port=port)
    )
    server = uvicorn.Server(uvicorn.Config(aplikacija, host="127.0.0.1", port=port, log_level="warning"))
    dretva = threading.Thread(target=server.run, daemon=True)
    dretva.start()
    rok = time.monotonic() + 20
    while not server.started:
        if time.monotonic() > rok:
            raise RuntimeError("uvicorn se nije pokrenuo na vrijeme")
        time.sleep(0.05)
    yield SkPosluzitelj(aplikacija, f"http://127.0.0.1:{port}")
    server.should_exit = True
    dretva.join(timeout=10)
    aplikacija.state.baza.zatvori()
