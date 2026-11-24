"""Baza podataka u memoriji (SQLite): svaka instanca aplikacije dobiva svježu bazu s početnim podacima."""

import sqlite3
import threading
from collections.abc import Sequence
from typing import Any

SHEMA = """
CREATE TABLE korisnici (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    korisnicko_ime TEXT NOT NULL UNIQUE,
    lozinka_hash   TEXT NOT NULL,
    uloga          TEXT NOT NULL,
    ime            TEXT NOT NULL,
    email          TEXT NOT NULL,
    adresa         TEXT NOT NULL DEFAULT '',
    telefon        TEXT NOT NULL DEFAULT '',
    clanarina      TEXT NOT NULL DEFAULT 'AKTIVNA'
);
CREATE TABLE knjige (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    naslov   TEXT NOT NULL,
    autor    TEXT NOT NULL,
    godina   INTEGER NOT NULL,
    skrivena INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE posudbe (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    korisnik_id INTEGER NOT NULL REFERENCES korisnici (id),
    knjiga_id   INTEGER NOT NULL REFERENCES knjige (id),
    rok         TEXT NOT NULL,
    produzenja  INTEGER NOT NULL DEFAULT 0
);
"""


class Baza:
    """Jedna otvorena veza na bazu u memoriji; pristup je serijaliziran bravom."""

    def __init__(self) -> None:
        self._veza = sqlite3.connect(":memory:", check_same_thread=False)
        self._veza.row_factory = sqlite3.Row
        self._brava = threading.Lock()
        self._veza.executescript(SHEMA)

    def svi(self, sql: str, parametri: Sequence[Any] = ()) -> list[sqlite3.Row]:
        with self._brava:
            return self._veza.execute(sql, parametri).fetchall()

    def jedan(self, sql: str, parametri: Sequence[Any] = ()) -> sqlite3.Row | None:
        with self._brava:
            return self._veza.execute(sql, parametri).fetchone()

    def izvrsi(self, sql: str, parametri: Sequence[Any] = ()) -> int:
        with self._brava:
            kursor = self._veza.execute(sql, parametri)
            self._veza.commit()
            return kursor.lastrowid or 0
