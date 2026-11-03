"""Zaboravljena lozinka: token se šalje e-poštom, a njime se postavlja nova lozinka."""

from __future__ import annotations

import hashlib
# @@VULN S11
from datetime import date
# @@SECURE S11
import secrets
from datetime import datetime, timedelta
# @@END S11

from medtermin.platforma.baza import Baza
from medtermin.platforma.korisnici import KorisnikService, provjeri_lozinku
from medtermin.platforma.posta import PostaService
# @@VULN S11
# @@SECURE S11

TRAJANJE_TOKENA = timedelta(minutes=15)
# @@END S11


class ResetLozinkeService:
    def __init__(self, baza: Baza, korisnici: KorisnikService, posta: PostaService) -> None:
        self._baza = baza
        self._korisnici = korisnici
        self._posta = posta

    def zatrazi(self, username: str) -> None:
        korisnik = self._korisnici.pronadi(username)
        if korisnik is None:
            return
        # @@VULN S11
        token = hashlib.md5((username + date.today().isoformat()).encode("utf-8")).hexdigest()
        self._baza.izvrsi("INSERT INTO reset_tokeni (username, token) VALUES (?, ?)", (username, token))
        # @@SECURE S11
        token = secrets.token_urlsafe(32)
        istjece = (datetime.now() + TRAJANJE_TOKENA).isoformat(timespec="seconds")
        self._baza.izvrsi(
            "INSERT INTO reset_tokeni (username, token, istjece) VALUES (?, ?, ?)",
            (username, _sazetak(token), istjece),
        )
        # @@END S11
        self._posta.posalji_upute_za_lozinku(korisnik, token)

    def postavi_novu_lozinku(self, token: str | None, nova_lozinka: str | None) -> bool:
        provjeri_lozinku(nova_lozinka)
        if token is None or not token.strip():
            return False
        # @@VULN S11
        zapis = self._baza.jedan("SELECT username FROM reset_tokeni WHERE token = ?", (token.strip(),))
        if zapis is None:
            return False
        self._korisnici.promijeni_lozinku(zapis["username"], nova_lozinka)
        return True
        # @@SECURE S11
        sada = datetime.now().isoformat(timespec="seconds")
        zapis = self._baza.jedan(
            "SELECT id, username FROM reset_tokeni WHERE token = ? AND iskoristen = 0 AND istjece > ?",
            (_sazetak(token.strip()), sada),
        )
        if zapis is None:
            return False
        iskoristeno = self._baza.izvrsi(
            "UPDATE reset_tokeni SET iskoristen = 1 WHERE id = ? AND iskoristen = 0", (zapis["id"],)
        )
        if iskoristeno != 1:
            return False
        self._korisnici.promijeni_lozinku(zapis["username"], nova_lozinka)
        return True
        # @@END S11
# @@VULN S11
# @@SECURE S11


def _sazetak(vrijednost: str) -> str:
    return hashlib.sha256(vrijednost.encode("utf-8")).hexdigest()
# @@END S11
