"""S01 – IDOR: storno tuđe narudžbe."""


def _moje(sk_client, zaglavlja):
    return [n["id"] for n in sk_client.get("/api/narudzbe/moje", headers=zaglavlja).json()]


def test_s01_marko_ne_smije_stornirati_aninu_narudzbu(sk_client, sk_prijava):
    ana = sk_prijava("ana")
    assert 1 in _moje(sk_client, ana), "preduvjet: ana ima narudžbu 1"

    odgovor = sk_client.delete("/api/narudzbe/1", headers=sk_prijava("marko"))

    assert odgovor.status_code in (403, 404), f"storno tuđe narudžbe: {odgovor.status_code}"
    assert 1 in _moje(sk_client, ana), "anina narudžba 1 je stornirana"


def test_s01_marko_ne_smije_stornirati_novu_aninu_narudzbu(sk_client, sk_prijava):
    ana = sk_prijava("ana")
    nova = sk_client.post(
        "/api/narudzbe",
        json={"dogadjajId": 3, "kolicina": 1, "imeNaUlaznici": "Ana Anić", "oib": "48291736504"},
        headers=ana,
    )
    assert nova.status_code == 201, f"preduvjet: narudžba ({nova.status_code} {nova.text})"
    narudzba_id = nova.json()["id"]

    odgovor = sk_client.delete(f"/api/narudzbe/{narudzba_id}", headers=sk_prijava("marko"))

    assert odgovor.status_code in (403, 404), f"storno tuđe narudžbe: {odgovor.status_code}"
    assert narudzba_id in _moje(sk_client, ana), "nova anina narudžba je stornirana"


def test_s01_admin_smije_stornirati_tudu_narudzbu(sk_client, sk_prijava):
    odgovor = sk_client.delete("/api/narudzbe/2", headers=sk_prijava("admin"))
    assert odgovor.status_code == 204
