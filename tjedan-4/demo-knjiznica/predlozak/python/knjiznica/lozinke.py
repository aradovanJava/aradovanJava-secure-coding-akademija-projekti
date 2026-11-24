"""Pohrana i provjera lozinki korisnika."""

# @@VULN K04
import hashlib


def hashiraj(lozinka: str) -> str:
    return hashlib.md5(lozinka.encode("utf-8")).hexdigest()


def provjeri(lozinka: str, pohranjeno: str) -> bool:
    return hashiraj(lozinka) == pohranjeno
# @@SECURE K04
import base64
import hashlib
import hmac
import secrets

ALGORITAM = "pbkdf2_sha256"
ITERACIJE = 600_000


def hashiraj(lozinka: str) -> str:
    """PBKDF2-HMAC-SHA256 s nasumičnom solju od 16 bajtova (OWASP: najmanje 600 000 iteracija)."""
    sol = secrets.token_bytes(16)
    izvedeno = hashlib.pbkdf2_hmac("sha256", lozinka.encode("utf-8"), sol, ITERACIJE)
    return f"{ALGORITAM}${ITERACIJE}${_b64(sol)}${_b64(izvedeno)}"


def provjeri(lozinka: str, pohranjeno: str) -> bool:
    dijelovi = pohranjeno.split("$")
    if len(dijelovi) != 4 or dijelovi[0] != ALGORITAM:
        return False
    _, iteracije, sol, ocekivano = dijelovi
    izvedeno = hashlib.pbkdf2_hmac("sha256", lozinka.encode("utf-8"), _iz_b64(sol), int(iteracije))
    # usporedba u konstantnom vremenu
    return hmac.compare_digest(izvedeno, _iz_b64(ocekivano))


def _b64(podaci: bytes) -> str:
    return base64.b64encode(podaci).decode("ascii")


def _iz_b64(tekst: str) -> bytes:
    return base64.b64decode(tekst)
# @@END K04
