"""K04 – A04 Cryptographic Failures: lozinke spremljene kao MD5 bez soli (CWE-916, CWE-327)."""

import hashlib
import re

import pytest

pytestmark = [pytest.mark.sigurnosni, pytest.mark.k04]

LOZINKA = "IstaLozinka123!"


def _registriraj(klijent, ime):
    podaci = {"korisnickoIme": ime, "lozinka": LOZINKA, "ime": "Test", "email": f"{ime}@primjer.hr"}
    assert klijent.post("/api/registracija", json=podaci).status_code == 201


def _hash(app, ime):
    return app.state.baza.jedan("SELECT lozinka_hash FROM korisnici WHERE korisnicko_ime = ?", (ime,))[
        "lozinka_hash"
    ]


def test_k04_ista_lozinka_daje_razlicite_hasheve(app, klijent):
    _registriraj(klijent, "k04.prvi")
    _registriraj(klijent, "k04.drugi")
    assert _hash(app, "k04.prvi") != _hash(app, "k04.drugi"), "nema nasumične soli"


def test_k04_hash_nije_md5(app, klijent):
    _registriraj(klijent, "k04.treci")
    pohranjeno = _hash(app, "k04.treci")
    assert pohranjeno != hashlib.md5(LOZINKA.encode()).hexdigest()
    assert not re.fullmatch(r"[0-9a-f]{32}", pohranjeno), "hash izgleda kao MD5"
