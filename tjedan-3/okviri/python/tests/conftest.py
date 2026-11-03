"""Testovi bez Keycloaka: RSA ključ se generira u testu, JWKS je u memoriji, a tokeni su potpisani
kao tokeni Keycloaka (iss, aud, preferred_username, realm_access.roles). Aplikacija ih provjerava ISTIM
kodom kao u produkciji – zamijenjen je samo izvor javnih ključeva (app.dependency_overrides).
"""

import json
import time
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient

from okviri.aplikacija import napravi_aplikaciju
from okviri.postavke import Postavke
from okviri.sigurnost.ovlasti import izvor_kljuceva

ISSUER = "http://localhost:8180/realms/akademija"
AUDIENCE = "medtermin-api"
KID = "testni-kljuc"
TESTNI_API_KLJUC = "testni-kljuc-0123456789"


class TestniJwks:
    """Izvor ključeva iz JWKS-a u memoriji – isto sučelje kao jwt.PyJWKClient."""

    def __init__(self, javni_kljuc: rsa.RSAPublicKey) -> None:
        jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(javni_kljuc))
        jwk.update(kid=KID, use="sig", alg="RS256")
        self.jwks = jwt.PyJWKSet.from_dict({"keys": [jwk]})

    def get_signing_key_from_jwt(self, token: str) -> jwt.PyJWK:
        kid = jwt.get_unverified_header(token).get("kid")
        for kljuc in self.jwks.keys:
            if kljuc.key_id == kid:
                return kljuc
        raise jwt.PyJWKClientError(f"Nepoznat kid: {kid}")


@pytest.fixture(scope="session")
def rsa_kljuc() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


def potpisi(kljuc: rsa.RSAPrivateKey, username: str, *uloge: str, kid: str = KID, **izmjene) -> str:
    """Access token kakav izdaje Keycloak (izmjene: npr. iss=..., exp=..., ili None za brisanje claima)."""
    sada = int(time.time())
    claims = {
        "iss": ISSUER,
        "aud": [AUDIENCE, "account"],
        "sub": str(uuid.uuid5(uuid.NAMESPACE_DNS, username)),  # Keycloak: sub je UUID
        "typ": "Bearer",
        "azp": "medtermin-dev-cli",
        "preferred_username": username,
        "realm_access": {"roles": list(uloge)},
        "iat": sada,
        "exp": sada + 300,
    }
    claims.update(izmjene)
    claims = {k: v for k, v in claims.items() if v is not None}
    return jwt.encode(claims, kljuc, algorithm="RS256", headers={"kid": kid})


def postavke(**izmjene) -> Postavke:
    vrijednosti = {
        "obavijesti_api_kljuc": TESTNI_API_KLJUC,
        "zahtijevaj_https": False,
        "dopusteni_hostovi": ["testserver"],
        **izmjene,
    }
    return Postavke(_env_file=None, **vrijednosti)


def aplikacija(rsa_kljuc: rsa.RSAPrivateKey, **izmjene) -> FastAPI:
    app = napravi_aplikaciju(postavke(**izmjene))
    testni_jwks = TestniJwks(rsa_kljuc.public_key())
    app.dependency_overrides[izvor_kljuceva] = lambda: testni_jwks
    return app


@pytest.fixture
def app(rsa_kljuc) -> FastAPI:
    return aplikacija(rsa_kljuc)


@pytest.fixture
def klijent(app):
    with TestClient(app) as k:
        yield k


@pytest.fixture
def kao(rsa_kljuc):
    """Zaglavlje Authorization za korisnika s realm ulogama: kao("ana", "KORISNIK")."""

    def zaglavlje(username: str, *uloge: str, **izmjene) -> dict[str, str]:
        return {"Authorization": f"Bearer {potpisi(rsa_kljuc, username, *uloge, **izmjene)}"}

    return zaglavlje
