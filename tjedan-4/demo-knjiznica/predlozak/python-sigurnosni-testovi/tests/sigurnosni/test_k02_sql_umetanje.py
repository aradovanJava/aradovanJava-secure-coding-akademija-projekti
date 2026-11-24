"""K02 – A05 Injection: SQL umetanje u pretrazi kataloga (CWE-89)."""

import pytest

pytestmark = [pytest.mark.sigurnosni, pytest.mark.k02]


@pytest.mark.parametrize("upit", ["' OR '1'='1' --", "%' OR 1=1 --"])
def test_k02_uvjet_uvijek_istinit_ne_otkriva_skrivene_knjige(klijent, upit):
    odgovor = klijent.get("/api/knjige", params={"trazi": upit})
    assert odgovor.status_code in (200, 400)
    assert "Interni popis za otpis" not in odgovor.text


def test_k02_union_ne_vraca_korisnicke_racune(klijent):
    upit = "%' UNION SELECT id, korisnicko_ime, lozinka_hash, 0 FROM korisnici --"
    odgovor = klijent.get("/api/knjige", params={"trazi": upit})
    assert odgovor.status_code in (200, 400)
    assert "knjiznicar" not in odgovor.text
    assert "marko" not in odgovor.text
