"""K07 – A09 Security Logging and Alerting Failures: lozinka u dnevniku, nema sigurnosnih događaja,
krivotvorenje zapisa (CWE-532, CWE-778, CWE-117)."""

import logging

import pytest

pytestmark = [pytest.mark.sigurnosni, pytest.mark.k07]


def test_k07_lozinka_se_ne_zapisuje(klijent, caplog):
    caplog.set_level(logging.DEBUG)
    klijent.post("/api/prijava", json={"korisnickoIme": "ana", "lozinka": "Ana123!"})
    klijent.post("/api/prijava", json={"korisnickoIme": "ana", "lozinka": "TajnaKojuNitkoNeSmijeVidjeti"})
    assert "Ana123!" not in caplog.text
    assert "TajnaKojuNitkoNeSmijeVidjeti" not in caplog.text


def test_k07_neuspjela_prijava_je_sigurnosni_dogadjaj(klijent, caplog):
    caplog.set_level(logging.INFO)
    klijent.post("/api/prijava", json={"korisnickoIme": "marko", "lozinka": "pogresna"})
    poruke = [z.getMessage() for z in caplog.records if z.levelno >= logging.WARNING]
    assert any("SECURITY_EVENT" in p and "LOGIN_FAILED" in p for p in poruke), poruke


def test_k07_novi_red_u_imenu_ne_krivotvori_zapis(klijent, caplog):
    caplog.set_level(logging.DEBUG)
    ime = "ana\n2026-11-25 10:00:00 INFO SECURITY_EVENT LOGIN_SUCCESS korisnik=knjiznicar"
    klijent.post("/api/prijava", json={"korisnickoIme": ime, "lozinka": "x"})
    assert all("\n" not in z.getMessage() for z in caplog.records)
