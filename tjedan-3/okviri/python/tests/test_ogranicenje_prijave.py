"""Ograničenje broja pokušaja prijave (limits, fixed window): 429 + Retry-After nakon N pokušaja."""

from fastapi.testclient import TestClient

from tests.conftest import aplikacija


def test_nakon_tri_pokusaja_slijedi_429(rsa_kljuc):
    with TestClient(aplikacija(rsa_kljuc, prijava_pokusaja_u_minuti=3)) as k:
        for _ in range(3):
            assert k.post("/api/auth/login", json={"username": "ana", "password": "pogadam"}).status_code == 401
        odbijeno = k.post("/api/auth/login", json={"username": "ana", "password": "Ana12345!"})
    assert odbijeno.status_code == 429
    assert 1 <= int(odbijeno.headers["Retry-After"]) <= 60
    assert odbijeno.json() == {"greska": "Previše pokušaja prijave. Pokušajte ponovno kasnije."}


def test_ogranicenje_ne_vrijedi_za_druge_rute(rsa_kljuc):
    with TestClient(aplikacija(rsa_kljuc, prijava_pokusaja_u_minuti=1)) as k:
        assert k.post("/api/auth/login", json={"username": "ana", "password": "x"}).status_code == 401
        assert all(k.get("/api/health").status_code == 200 for _ in range(5))
