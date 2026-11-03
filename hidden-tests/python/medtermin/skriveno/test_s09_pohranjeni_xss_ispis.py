"""S09 – pohranjeni XSS na stranici za ispis potvrde."""

NAPOMENA = "<script>alert('x')</script><img src=x onerror=alert(1)>"


def test_s09_napomena_se_enkodira_na_ispisu(sk_client, sk_prijava):
    ana = sk_prijava("ana")
    odgovor = sk_client.post(
        "/api/rezervacije", json={"terminId": 9, "napomena": NAPOMENA, "oib": "48291736504"}, headers=ana
    )
    if odgovor.status_code == 400:
        return  # odbijanje unosa s HTML oznakama također je prihvatljivo (kao u Java/.NET)
    assert odgovor.status_code == 201, f"preduvjet: rezervacija ({odgovor.status_code} {odgovor.text})"
    ispis = sk_client.get(f"/ispis/rezervacije/{odgovor.json()['id']}", headers=ana)
    assert ispis.status_code == 200
    assert "<script>alert('x')</script>" not in ispis.text
    assert "<img src=x onerror" not in ispis.text
