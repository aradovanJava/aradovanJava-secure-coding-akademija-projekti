"""S09 – pohranjeni XSS na stranici za ispis ulaznice."""

IME = "<script>alert('x')</script><img src=x onerror=alert(1)>"


def test_s09_ime_na_ulaznici_se_enkodira_na_ispisu(sk_client, sk_prijava):
    ana = sk_prijava("ana")
    odgovor = sk_client.post(
        "/api/narudzbe",
        json={"dogadjajId": 3, "kolicina": 1, "imeNaUlaznici": IME, "oib": "48291736504"},
        headers=ana,
    )
    if odgovor.status_code == 400:
        return  # odbijanje unosa s HTML oznakama također je prihvatljivo (kao u Java/.NET)
    assert odgovor.status_code == 201, f"preduvjet: narudžba ({odgovor.status_code} {odgovor.text})"
    ispis = sk_client.get(f"/ispis/narudzbe/{odgovor.json()['id']}", headers=ana)
    assert ispis.status_code == 200
    assert "<script>alert('x')</script>" not in ispis.text
    assert "<img src=x onerror" not in ispis.text
