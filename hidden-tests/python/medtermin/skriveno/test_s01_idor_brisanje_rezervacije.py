"""S01 – IDOR: brisanje tuđe rezervacije."""


def test_s01_marko_ne_smije_obrisati_aninu_rezervaciju(sk_client, sk_prijava):
    ana = sk_prijava("ana")
    assert 1 in [r["id"] for r in sk_client.get("/api/rezervacije/moje", headers=ana).json()], "preduvjet"

    odgovor = sk_client.delete("/api/rezervacije/1", headers=sk_prijava("marko"))

    assert odgovor.status_code in (403, 404), f"brisanje tuđe rezervacije: {odgovor.status_code}"
    moje = [r["id"] for r in sk_client.get("/api/rezervacije/moje", headers=ana).json()]
    assert 1 in moje, "anina rezervacija 1 je obrisana"


def test_s01_admin_smije_obrisati_tudu_rezervaciju(sk_client, sk_prijava):
    odgovor = sk_client.delete("/api/rezervacije/2", headers=sk_prijava("admin"))
    assert odgovor.status_code == 204
