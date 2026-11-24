"""K06 – A06 Insecure Design: produljenje posudbe bez poslovnih ograničenja (CWE-840, CWE-20)."""

import pytest

pytestmark = [pytest.mark.sigurnosni, pytest.mark.k06]


def _rok(klijent, prijava, posudba_id):
    return next(p["rok"] for p in klijent.get("/api/posudbe", headers=prijava("ana")).json() if p["id"] == posudba_id)


@pytest.mark.parametrize("dana", [365, -30, 0])
def test_k06_neispravan_broj_dana_vraca_400(klijent, prijava, dana):
    prije = _rok(klijent, prijava, 3)
    odgovor = klijent.post("/api/posudbe/3/produzi", json={"dana": dana}, headers=prijava("ana"))
    assert odgovor.status_code == 400
    assert _rok(klijent, prijava, 3) == prije, "rok se promijenio"


def test_k06_najvise_dva_produljenja(klijent, prijava):
    statusi = [
        klijent.post("/api/posudbe/2/produzi", json={"dana": 7}, headers=prijava("ana")).status_code
        for _ in range(3)
    ]
    assert statusi[:2] == [200, 200]
    assert statusi[2] == 409
