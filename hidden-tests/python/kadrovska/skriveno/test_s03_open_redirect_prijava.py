"""S03 – open redirect nakon prijave obrascem."""

import pytest

ODREDISTA = ["https://zlo.example/x", "//zlo.example", "/\\zlo.example"]


@pytest.mark.parametrize("return_url", ODREDISTA)
def test_s03_preusmjeravanje_samo_na_lokalni_put(sk_client, return_url):
    odgovor = sk_client.post("/prijava", data={"username": "ana", "password": "Ana12345!", "returnUrl": return_url})
    assert odgovor.status_code == 302, f"preduvjet: uspješna prijava ({odgovor.status_code})"
    lokacija = odgovor.headers.get("location", "")
    assert "zlo.example" not in lokacija, f"returnUrl={return_url!r} → Location: {lokacija}"
    assert lokacija.startswith("/") and not lokacija.startswith("//")
