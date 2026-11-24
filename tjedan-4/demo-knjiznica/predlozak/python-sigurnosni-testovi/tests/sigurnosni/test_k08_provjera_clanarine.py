"""K08 – A10 Mishandling of Exceptional Conditions: greška u provjeri članarine propušta posudbu (CWE-636, CWE-755)."""

import pytest

pytestmark = [pytest.mark.sigurnosni, pytest.mark.k08]


def test_k08_istekla_clanarina_ne_smije_posuditi(klijent, prijava):
    odgovor = klijent.post("/api/posudbe", json={"knjigaId": 4}, headers=prijava("marko"))
    assert odgovor.status_code == 403


def test_k08_nepoznat_status_clanarine_znaci_odbijanje(klijent, prijava):
    # Iva ima status SUSPENDIRANA koji provjera ne poznaje: greška u provjeri ne smije značiti "dopušteno".
    odgovor = klijent.post("/api/posudbe", json={"knjigaId": 4}, headers=prijava("iva"))
    assert odgovor.status_code == 403
