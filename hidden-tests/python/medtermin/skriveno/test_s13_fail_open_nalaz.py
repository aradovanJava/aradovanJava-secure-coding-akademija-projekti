"""S13 – iznimka u obradi zahtjeva ne smije propustiti pristup tuđem nalazu."""

import pytest


@pytest.mark.parametrize("oblik", ["xml", ""], ids=["format-xml", "format-prazan"])
def test_s13_tudi_nalaz_s_nepoznatim_formatom(sk_client, sk_prijava, oblik):
    vlastiti = sk_client.get("/api/nalazi/1", params={"format": "json"}, headers=sk_prijava("ana"))
    assert vlastiti.status_code == 200, "preduvjet: ana vidi svoj nalaz 1"
    redak = max(vlastiti.json()["sadrzaj"].splitlines(), key=len)

    odgovor = sk_client.get("/api/nalazi/1", params={"format": oblik}, headers=sk_prijava("marko"))

    assert odgovor.status_code in (400, 403, 404), f"tuđi nalaz s formatom {oblik!r}: {odgovor.status_code}"
    for zabranjeno in (redak, "nalaz-ana-krvna-slika.txt", "Error", "Traceback", 'File "'):
        assert zabranjeno not in odgovor.text, f"odgovor sadrži {zabranjeno!r}"
