"""K05 – A02 Security Misconfiguration: detalji greške u odgovoru i nedostatak sigurnosnih zaglavlja (CWE-209, CWE-693)."""

import pytest

pytestmark = [pytest.mark.sigurnosni, pytest.mark.k05]


def test_k05_nepostojeca_knjiga_bez_detalja_greske(klijent):
    odgovor = klijent.get("/api/knjige/999999")
    assert odgovor.status_code == 404
    for trag in ("Traceback", "Exception", "Error", 'File "', "knjiznica/"):
        assert trag not in odgovor.text, f"odgovor otkriva detalje ({trag})"


def test_k05_sigurnosna_zaglavlja(klijent):
    odgovor = klijent.get("/api/knjige")
    assert odgovor.headers.get("X-Content-Type-Options") == "nosniff"
    assert odgovor.headers.get("X-Frame-Options") == "DENY"
    assert "Content-Security-Policy" in odgovor.headers
