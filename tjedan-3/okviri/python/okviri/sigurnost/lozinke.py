"""Hashiranje lozinki s pwdlib: novi hashevi su Argon2id (sol, parametri u samom hashu), a stari (bcrypt,
SHA-256 bez soli iz T2) se još mogu PROVJERITI i pri uspješnoj prijavi automatski zamjenjuju Argon2id hashem
(PasswordHash.verify_and_update) – kao DelegatingPasswordEncoder (Java) i SuccessRehashNeeded (.NET).
"""

import hashlib
import hmac
import string

from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

_HEKSA = frozenset(string.hexdigits)


class StariSha256:
    """Samo za PROVJERU starih hasheva iz T2 (hex SHA-256 bez soli) dok se ne migriraju. Novi se nikad ne rade."""

    @classmethod
    def identify(cls, hash: str | bytes) -> bool:
        h = hash.decode() if isinstance(hash, bytes) else hash
        return len(h) == 64 and _HEKSA.issuperset(h)

    def hash(self, password: str | bytes, *, salt: bytes | None = None) -> str:
        raise NotImplementedError("SHA-256 bez soli se smije samo provjeriti, ne i koristiti za nove lozinke")

    def verify(self, password: str | bytes, hash: str | bytes) -> bool:
        lozinka = password.encode() if isinstance(password, str) else password
        h = hash.decode() if isinstance(hash, bytes) else hash
        # Iznimka u kodu, uz razlog: samo PROVJERA starog hasha radi migracije, nikad za nove lozinke.
        izracunato = hashlib.sha256(lozinka).hexdigest()  # nosemgrep: python-slab-hash-za-tokene-ili-lozinke
        return hmac.compare_digest(izracunato, h.lower())

    def check_needs_rehash(self, hash: str | bytes) -> bool:
        return True


def napravi_hasher() -> PasswordHash:
    # Prvi u nizu je trenutni algoritam (svi novi hashevi); ostali samo za provjeru i nadogradnju.
    return PasswordHash((Argon2Hasher(), BcryptHasher(), StariSha256()))
