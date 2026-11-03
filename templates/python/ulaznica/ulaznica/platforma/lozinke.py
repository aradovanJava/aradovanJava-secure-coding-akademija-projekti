# @@VULN S07
import hashlib
import hmac
# @@SECURE S07
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
# @@END S07


class LozinkaHasher:
    """Izračun i provjera sažetka lozinke (registracija, prijava, promjena lozinke, početni podaci)."""

    # @@VULN S07
    def hash(self, lozinka: str) -> str:
        return hashlib.sha256(lozinka.encode("utf-8")).hexdigest()

    def provjeri(self, lozinka: str, spremljeni_hash: str | None) -> bool:
        if spremljeni_hash is None:
            return False
        return hmac.compare_digest(self.hash(lozinka), spremljeni_hash)
    # @@SECURE S07
    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash(self, lozinka: str) -> str:
        return self._hasher.hash(lozinka)

    def provjeri(self, lozinka: str, spremljeni_hash: str | None) -> bool:
        if not spremljeni_hash:
            return False
        try:
            return self._hasher.verify(spremljeni_hash, lozinka)
        except (VerificationError, InvalidHashError):
            return False
    # @@END S07
