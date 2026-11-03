"""S01 – IDOR: brisanje tuđeg zahtjeva za godišnji odmor."""


def _moji(klijent, zaglavlja):
    return [z["id"] for z in klijent.get("/api/zahtjevi/moji", headers=zaglavlja).json()]


def test_s01_marko_ne_smije_obrisati_anin_zahtjev(sk_client, sk_prijava):
    ana = sk_prijava("ana")
    assert 1 in _moji(sk_client, ana), "preduvjet: ana ima zahtjev 1"

    odgovor = sk_client.delete("/api/zahtjevi/1", headers=sk_prijava("marko"))

    assert odgovor.status_code in (403, 404), f"brisanje tuđeg zahtjeva: {odgovor.status_code}"
    assert 1 in _moji(sk_client, ana), "anin zahtjev 1 je obrisan"


def test_s01_marko_ne_smije_obrisati_novi_anin_zahtjev(sk_client, sk_prijava):
    ana = sk_prijava("ana")
    novi = sk_client.post(
        "/api/zahtjevi",
        json={"od": "2027-03-08", "do": "2027-03-10", "razlog": "Odmor", "oib": "48291736504"},
        headers=ana,
    )
    assert novi.status_code == 201, f"preduvjet: novi zahtjev ({novi.status_code} {novi.text})"
    zahtjev_id = novi.json()["id"]

    odgovor = sk_client.delete(f"/api/zahtjevi/{zahtjev_id}", headers=sk_prijava("marko"))

    assert odgovor.status_code in (403, 404), f"brisanje tuđeg zahtjeva: {odgovor.status_code}"
    assert zahtjev_id in _moji(sk_client, ana), "anin novi zahtjev je obrisan"


def test_s01_admin_smije_obrisati_tudi_zahtjev(sk_client, sk_prijava):
    odgovor = sk_client.delete("/api/zahtjevi/2", headers=sk_prijava("admin"))
    assert odgovor.status_code == 204
