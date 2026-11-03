"""S13 – iznimka u obradi zahtjeva ne smije propustiti pristup tuđoj platnoj listi."""

import pytest


@pytest.mark.parametrize("oblik", ["xml", ""], ids=["format-xml", "format-prazan"])
def test_s13_tuda_platna_lista_s_nepoznatim_formatom(sk_client, sk_prijava, oblik):
    vlastita = sk_client.get("/api/platne-liste/1", params={"format": "json"}, headers=sk_prijava("ana"))
    assert vlastita.status_code == 200, "preduvjet: ana vidi svoju platnu listu 1"
    redak = max(vlastita.json()["sadrzaj"].splitlines(), key=len)

    odgovor = sk_client.get("/api/platne-liste/1", params={"format": oblik}, headers=sk_prijava("marko"))

    assert odgovor.status_code in (400, 403, 404), f"tuđa platna lista s formatom {oblik!r}: {odgovor.status_code}"
    for zabranjeno in (redak, "placa-ana-2026-10.txt", "Error", "Traceback", 'File "'):
        assert zabranjeno not in odgovor.text, f"odgovor sadrži {zabranjeno!r}"
