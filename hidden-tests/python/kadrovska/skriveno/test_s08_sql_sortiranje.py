"""S08 – SQL u parametrima sortiranja imenika zaposlenika."""

import pytest

NEISPRAVNI = [
    {"sort": "(CASE WHEN (SELECT COUNT(*) FROM korisnici)>0 THEN prezime ELSE ime END)", "smjer": "asc"},
    {"sort": "prezime;--", "smjer": "asc"},
    {"sort": "prezime", "smjer": "asc,(SELECT 1)"},
]


@pytest.mark.parametrize("parametri", NEISPRAVNI, ids=["case-podupit", "tocka-zarez", "smjer-podupit"])
def test_s08_neispravno_sortiranje_vraca_400(sk_client, sk_prijava, parametri):
    odgovor = sk_client.get("/api/zaposlenici", params=parametri, headers=sk_prijava("ana"))
    assert odgovor.status_code == 400, f"{parametri} → {odgovor.status_code}"
