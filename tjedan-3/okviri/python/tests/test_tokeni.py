"""Provjera JWT-a: potpis, rok, izdavatelj, publika, algoritam; mapiranje preferred_username i realm_access.roles."""

import base64
import hashlib
import hmac
import json
import time

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from okviri.sigurnost.tokeni import NeispravanToken, korisnik_iz_tokena
from tests.conftest import potpisi


def _b64(podaci: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(podaci).encode()).rstrip(b"=").decode()


def _status(klijent, token: str) -> int:
    return klijent.get("/api/rezervacije/moje", headers={"Authorization": f"Bearer {token}"}).status_code


def test_ispravan_token_prolazi(klijent, rsa_kljuc):
    assert _status(klijent, potpisi(rsa_kljuc, "ana", "KORISNIK")) == 200


def test_potpis_drugim_kljucem_je_401(klijent):
    drugi = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    odgovor = klijent.get("/api/rezervacije/moje", headers={"Authorization": f"Bearer {potpisi(drugi, 'ana')}"})
    assert odgovor.status_code == 401
    assert 'error="invalid_token"' in odgovor.headers["WWW-Authenticate"]


def test_izmijenjen_sadrzaj_je_401(klijent, rsa_kljuc):
    zaglavlje, _, potpis = potpisi(rsa_kljuc, "ana", "KORISNIK").split(".")
    lazni = _b64({"preferred_username": "ana", "realm_access": {"roles": ["ADMIN"]}})  # pokušaj dodjele uloge
    assert _status(klijent, f"{zaglavlje}.{lazni}.{potpis}") == 401


@pytest.mark.parametrize(
    "izmjena",
    [
        {"exp": int(time.time()) - 120},  # istekao (više od dopuštenog odstupanja sata)
        {"iss": "http://localhost:8180/realms/master"},
        {"aud": "neki-drugi-api"},
        {"exp": None},  # bez roka valjanosti
        {"iss": None},
    ],
    ids=["istekao", "drugi-issuer", "druga-publika", "bez-exp", "bez-iss"],
)
def test_neispravni_claimovi_su_401(klijent, rsa_kljuc, izmjena):
    assert _status(klijent, potpisi(rsa_kljuc, "ana", "KORISNIK", **izmjena)) == 401


def test_nepoznat_kid_je_401(klijent, rsa_kljuc):
    assert _status(klijent, potpisi(rsa_kljuc, "ana", kid="nepoznat")) == 401


def test_alg_none_je_401(klijent):
    token = f"{_b64({'alg': 'none', 'typ': 'JWT', 'kid': 'testni-kljuc'})}.{_b64({'preferred_username': 'admin'})}."
    assert _status(klijent, token) == 401


def test_hs256_potpisan_javnim_kljucem_je_401(klijent, rsa_kljuc):
    # Zamjena algoritma: napadač potpiše HS256 javnim ključem kao HMAC tajnom – algorithms=["RS256"] to odbija.
    javni_pem = rsa_kljuc.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    sada = int(time.time())
    claims = {
        "iss": "http://localhost:8180/realms/akademija",
        "aud": "medtermin-api",
        "iat": sada,
        "exp": sada + 300,
        "preferred_username": "admin",
        "realm_access": {"roles": ["ADMIN"]},
    }
    poruka = f"{_b64({'alg': 'HS256', 'typ': 'JWT', 'kid': 'testni-kljuc'})}.{_b64(claims)}"
    potpis = base64.urlsafe_b64encode(hmac.new(javni_pem, poruka.encode(), hashlib.sha256).digest()).rstrip(b"=")
    assert _status(klijent, f"{poruka}.{potpis.decode()}") == 401


def test_smece_umjesto_tokena_je_401(klijent):
    assert _status(klijent, "nije.jwt") == 401
    basic = {"Authorization": "Basic YW5hOkFuYTEyMzQ1IQ=="}
    assert klijent.get("/api/rezervacije/moje", headers=basic).status_code == 401


def test_ime_iz_preferred_username_i_uloge_iz_realm_access():
    korisnik = korisnik_iz_tokena(
        {"sub": "a1b2", "preferred_username": "dr.horvat", "realm_access": {"roles": ["LIJECNIK", "offline_access"]}}
    )
    assert korisnik.username == "dr.horvat"
    assert korisnik.uloge == {"LIJECNIK", "offline_access"}


def test_bez_realm_access_nema_uloga_a_ime_je_sub():
    korisnik = korisnik_iz_tokena({"sub": "123", "realm_access": "ADMIN"})
    assert korisnik.username == "123"
    assert korisnik.uloge == frozenset()


def test_token_bez_imena_nije_valjan():
    with pytest.raises(NeispravanToken):
        korisnik_iz_tokena({"realm_access": {"roles": ["ADMIN"]}})
