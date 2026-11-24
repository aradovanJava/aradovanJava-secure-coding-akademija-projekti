"""K01 – A01 Broken Access Control: pristup tuđem profilu promjenom ID-a (IDOR, CWE-639)."""

import pytest

pytestmark = [pytest.mark.sigurnosni, pytest.mark.k01]


def test_k01_clan_ne_vidi_tudji_profil(klijent, prijava):
    # Ana (id 1) traži Markov profil (id 2): mora dobiti 404 i nijedan Markov podatak.
    odgovor = klijent.get("/api/clanovi/2", headers=prijava("ana"))
    assert odgovor.status_code == 404
    assert "marko" not in odgovor.text.lower()
    assert "Vukovarska" not in odgovor.text


def test_k01_odgovor_ne_otkriva_postoji_li_clan(klijent, prijava):
    # Postojeći tuđi profil i nepostojeći profil izgledaju jednako.
    tudji = klijent.get("/api/clanovi/2", headers=prijava("ana"))
    nepostojeci = klijent.get("/api/clanovi/999", headers=prijava("ana"))
    assert (tudji.status_code, tudji.json()) == (nepostojeci.status_code, nepostojeci.json())
