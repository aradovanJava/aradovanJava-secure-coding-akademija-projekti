"""S09 – pohranjeni XSS na stranici za ispis zahtjeva za godišnji odmor."""

RAZLOG = "<script>alert('x')</script><img src=x onerror=alert(1)>"


def test_s09_razlog_se_enkodira_na_ispisu(sk_client, sk_prijava):
    ana = sk_prijava("ana")
    odgovor = sk_client.post(
        "/api/zahtjevi",
        json={"od": "2027-06-01", "do": "2027-06-03", "razlog": RAZLOG, "oib": "48291736504"},
        headers=ana,
    )
    if odgovor.status_code == 400:
        return  # odbijanje unosa s HTML oznakama također je prihvatljivo (kao u Java/.NET)
    assert odgovor.status_code == 201, f"preduvjet: zahtjev ({odgovor.status_code} {odgovor.text})"
    ispis = sk_client.get(f"/ispis/zahtjevi/{odgovor.json()['id']}", headers=ana)
    assert ispis.status_code == 200
    assert "<script>alert('x')</script>" not in ispis.text
    assert "<img src=x onerror" not in ispis.text
