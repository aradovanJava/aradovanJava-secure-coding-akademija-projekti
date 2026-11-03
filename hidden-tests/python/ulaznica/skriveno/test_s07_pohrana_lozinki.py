"""S07 – lozinke se ne smiju spremati kao brzi sažetak bez soli (SHA-256/SHA-1/MD5)."""

import hashlib

from .conftest import sk_login, sk_registracija


def test_s07_ista_lozinka_daje_razlicite_sazetke(sk_app, sk_client):
    lozinka = "Jednaka12345!"
    prvi = sk_registracija(sk_client, "hash", lozinka)
    drugi = sk_registracija(sk_client, "hash", lozinka)
    sazeci = {
        red["username"]: red["password_hash"]
        for red in sk_app.state.baza.upit(
            "SELECT username, password_hash FROM korisnici WHERE username IN (?, ?)", (prvi, drugi)
        )
    }
    assert len(sazeci) == 2, "preduvjet: oba korisnika su u tablici korisnici"
    assert sazeci[prvi] != sazeci[drugi], "ista lozinka daje isti sažetak (nema soli)"
    brzi = {hashlib.new(alg, lozinka.encode("utf-8")).hexdigest() for alg in ("sha256", "sha1", "md5")}
    for sazetak in sazeci.values():
        assert sazetak.lower() not in brzi, "lozinka je spremljena kao brzi sažetak"
        assert lozinka not in sazetak
    assert sk_login(sk_client, prvi, lozinka).status_code == 200
    assert sk_login(sk_client, drugi, lozinka).status_code == 200


def test_s07_pocetni_korisnici_nisu_spremljeni_kao_sha256(sk_app, sk_client):
    red = sk_app.state.baza.jedan("SELECT password_hash FROM korisnici WHERE username = 'ana'")
    assert red is not None
    assert red["password_hash"].lower() != hashlib.sha256(b"Ana12345!").hexdigest()
    assert sk_login(sk_client, "ana").status_code == 200
