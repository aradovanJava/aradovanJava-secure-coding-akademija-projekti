"""JWT od Keycloaka -> Korisnik: provjera potpisa (JWKS), iss, aud i exp (PyJWT); ime iz preferred_username,
uloge iz realm_access.roles (KORISNIK, LIJECNIK, ADMIN) – kao KeycloakJwtKonverter (Java) i KeycloakUloge (.NET).
"""

import logging
from dataclasses import dataclass
from typing import Any, Protocol

import jwt

log = logging.getLogger(__name__)

# Dopušteni algoritmi su zadani ovdje, nikad iz zaglavlja tokena ("alg": "none", HS256 s javnim ključem …).
ALGORITMI = ["RS256"]
OBAVEZNI_CLAIMOVI = ["exp", "iat", "iss", "aud"]
DOPUSTENO_ODSTUPANJE_SATA = 30  # sekundi


class IzvorKljuceva(Protocol):
    """Javni ključ za potpis tokena (po "kid"). U produkciji jwt.PyJWKClient (JWKS s Keycloaka)."""

    def get_signing_key_from_jwt(self, token: str) -> jwt.PyJWK: ...


@dataclass(frozen=True)
class Korisnik:
    username: str
    uloge: frozenset[str] = frozenset()


class NeispravanToken(Exception):
    """Token nije valjan (potpis, rok, izdavatelj, publika ili sadržaj) – odgovor je uvijek 401."""


def keycloak_izvor_kljuceva(jwks_url: str) -> jwt.PyJWKClient:
    # Ključevi se dohvaćaju kod prvog tokena i čuvaju 5 min; nepoznat "kid" pokreće ponovno dohvaćanje (rotacija).
    return jwt.PyJWKClient(jwks_url, cache_keys=True, lifespan=300, timeout=5)


def korisnik_iz_tokena(claims: dict[str, Any]) -> Korisnik:
    ime = claims.get("preferred_username") or claims.get("sub")
    if not isinstance(ime, str) or not ime:
        raise NeispravanToken("token nema preferred_username ni sub")
    realm_access = claims.get("realm_access")
    uloge = realm_access.get("roles") if isinstance(realm_access, dict) else None
    if not isinstance(uloge, list):
        uloge = []
    return Korisnik(ime, frozenset(u for u in uloge if isinstance(u, str) and u))


def provjeri_token(token: str, izvor: IzvorKljuceva, issuer: str, audience: str) -> Korisnik:
    try:
        kljuc = izvor.get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            kljuc.key,
            algorithms=ALGORITMI,
            issuer=issuer,
            audience=audience,
            leeway=DOPUSTENO_ODSTUPANJE_SATA,
            options={"require": OBAVEZNI_CLAIMOVI},
        )
    except jwt.PyJWKClientConnectionError as e:
        log.error("JWKS nije dostupan: %s", e)
        raise NeispravanToken("JWKS nije dostupan") from e
    except jwt.PyJWTError as e:
        log.info("Odbijen token: %s", type(e).__name__)
        raise NeispravanToken(type(e).__name__) from e
    return korisnik_iz_tokena(claims)
