"""S02 – path traversal kod preuzimanja datoteke nalaza."""

import uuid


def _kanarinac(sk_mape, tajna: str):
    assert (sk_mape.pohrana / "nalaz-ana-krvna-slika.txt").exists(), "preduvjet: aplikacija koristi storage_dir"
    datoteka = sk_mape.korijen / f"tajna-ana-{uuid.uuid4()}.txt"
    datoteka.write_text(tajna, encoding="utf-8")
    return datoteka


def test_s02_relativna_putanja_izvan_pohrane(sk_client, sk_prijava, sk_mape):
    tajna = f"KANARINAC-{uuid.uuid4()}"
    datoteka = _kanarinac(sk_mape, tajna)
    odgovor = sk_client.get(
        "/api/nalazi/preuzmi", params={"datoteka": f"../{datoteka.name}"}, headers=sk_prijava("ana")
    )
    assert tajna not in odgovor.text, "pročitana je datoteka izvan storage_dir"
    assert odgovor.status_code != 200


def test_s02_apsolutna_putanja_izvan_pohrane(sk_client, sk_prijava, sk_mape):
    tajna = f"KANARINAC-{uuid.uuid4()}"
    datoteka = _kanarinac(sk_mape, tajna)
    odgovor = sk_client.get(
        "/api/nalazi/preuzmi", params={"datoteka": str(datoteka.resolve())}, headers=sk_prijava("ana")
    )
    assert tajna not in odgovor.text, "pročitana je datoteka izvan storage_dir"
    assert odgovor.status_code != 200
