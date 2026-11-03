"""Lozinke (pwdlib): Argon2id sa solju, provjera i automatska nadogradnja starih hasheva; lokalna prijava."""

import hashlib
import logging

import bcrypt
import pytest

from okviri.sigurnost.lozinke import StariSha256, napravi_hasher

STARI_SHA256 = hashlib.sha256(b"Marko12345!").hexdigest()


@pytest.fixture(scope="module")
def hasher():
    return napravi_hasher()


def test_novi_hash_je_argon2id_sa_solju(hasher):
    prvi, drugi = hasher.hash("Lozinka123!"), hasher.hash("Lozinka123!")
    assert prvi.startswith("$argon2id$")
    assert prvi != drugi  # sol: ista lozinka, različit hash
    assert hasher.verify("Lozinka123!", prvi)
    assert not hasher.verify("Kriva", prvi)
    assert hasher.verify_and_update("Lozinka123!", prvi) == (True, None)  # trenutni algoritam – bez nadogradnje


def test_stari_bcrypt_se_provjerava_i_nadograduje(hasher):
    stari = bcrypt.hashpw(b"x", bcrypt.gensalt(rounds=4)).decode()
    ispravna, novi = hasher.verify_and_update("x", stari)
    assert ispravna and novi is not None and novi.startswith("$argon2id$")


def test_stari_sha256_se_provjerava_i_nadograduje(hasher):
    ispravna, novi = hasher.verify_and_update("Marko12345!", STARI_SHA256)
    assert ispravna and novi.startswith("$argon2id$")
    assert hasher.verify_and_update("Kriva", STARI_SHA256) == (False, None)


def test_sha256_bez_soli_se_ne_koristi_za_nove_lozinke():
    with pytest.raises(NotImplementedError):
        StariSha256().hash("bilo-sto")


def test_prijava_migrira_stari_sha256_hash_u_argon2(klijent, app):
    assert app.state.lokalni_korisnici.hash("marko") == STARI_SHA256
    odgovor = klijent.post("/api/auth/login", json={"username": "marko", "password": "Marko12345!"})
    assert odgovor.status_code == 200
    assert odgovor.json()["username"] == "marko"
    assert app.state.lokalni_korisnici.hash("marko").startswith("$argon2id$")
    # i dalje se prijavljuje istom lozinkom
    assert klijent.post("/api/auth/login", json={"username": "marko", "password": "Marko12345!"}).status_code == 200


def test_pogresna_lozinka_i_nepostojeci_korisnik_daju_isti_odgovor(klijent):
    krivo = klijent.post("/api/auth/login", json={"username": "ana", "password": "pogresna"})
    nepostoji = klijent.post("/api/auth/login", json={"username": "nepostoji", "password": "pogresna"})
    assert krivo.status_code == nepostoji.status_code == 401
    assert krivo.json() == nepostoji.json() == {"greska": "Neispravno korisničko ime ili lozinka."}


def test_neuspjela_prijava_se_logira_bez_lozinke(klijent, caplog):
    with caplog.at_level(logging.INFO):
        klijent.post("/api/auth/login", json={"username": "marko", "password": "Pogresna-Lozinka-1"})
        klijent.post("/api/auth/login", json={"username": "ana", "password": "Ana12345!"})
    upozorenja = [z for z in caplog.records if z.levelno >= logging.WARNING]
    assert any("marko" in z.getMessage() for z in upozorenja)
    assert all("Pogresna-Lozinka-1" not in z.getMessage() and "Ana12345!" not in z.getMessage() for z in caplog.records)


def test_neispravan_zahtjev_ne_vraca_unesenu_lozinku(klijent):
    odgovor = klijent.post("/api/auth/login", json={"username": "ana\nINFO lazni zapis", "password": "Tajna-123!"})
    assert odgovor.status_code == 400
    assert odgovor.json() == {"greska": "Neispravan zahtjev.", "polja": ["username"]}
    assert "Tajna-123!" not in odgovor.text


def test_api_kljuc_se_ne_pojavljuje_u_logu(klijent, kao, caplog):
    with caplog.at_level(logging.INFO):
        assert klijent.delete("/api/rezervacije/3", headers=kao("ana", "KORISNIK")).status_code == 204
    assert any("otkazivanju rezervacije 3" in z.getMessage() for z in caplog.records)
    assert all("testni-kljuc-0123456789" not in z.getMessage() for z in caplog.records)
