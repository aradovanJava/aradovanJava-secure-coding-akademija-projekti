"""S05 – XXE kod uvoza termina iz XML-a."""

import uuid


def test_s05_vanjski_entitet_ne_smije_procitati_datoteku(sk_client, sk_prijava, sk_mape):
    tajna = f"KANARINAC-{uuid.uuid4()}"
    kanarinac = sk_mape.korijen / f"kanarinac-{uuid.uuid4()}.txt"
    kanarinac.write_text(tajna, encoding="utf-8")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!DOCTYPE termini [<!ENTITY e SYSTEM "{kanarinac.resolve().as_uri()}">]>\n'
        "<termini><termin><lijecnikId>1</lijecnikId><pocetak>2027-03-01T08:00</pocetak>"
        "<kapacitet>1</kapacitet><napomena>&e;</napomena></termin></termini>"
    )
    odgovor = sk_client.post(
        "/api/termini/uvoz",
        content=xml.encode("utf-8"),
        headers={**sk_prijava("dr.horvat"), "Content-Type": "application/xml"},
    )
    assert tajna not in odgovor.text, "sadržaj lokalne datoteke vraćen je u odgovoru"
    termini = sk_client.get("/api/termini", headers=sk_prijava("ana")).text
    assert tajna not in termini, "sadržaj lokalne datoteke spremljen je u napomenu termina"


def test_s05_doctype_vraca_400(sk_client, sk_prijava):
    xml = (
        '<?xml version="1.0"?>\n<!DOCTYPE termini [<!ENTITY n "Jutarnji">]>\n'
        "<termini><termin><lijecnikId>1</lijecnikId><pocetak>2027-03-02T08:00</pocetak>"
        "<kapacitet>1</kapacitet><napomena>&n;</napomena></termin></termini>"
    )
    odgovor = sk_client.post(
        "/api/termini/uvoz", content=xml, headers={**sk_prijava("admin"), "Content-Type": "application/xml"}
    )
    assert odgovor.status_code == 400
