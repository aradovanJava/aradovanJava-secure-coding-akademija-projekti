"""S05 – XXE kod uvoza edukacija iz XML-a."""

import uuid


def test_s05_vanjski_entitet_ne_smije_procitati_datoteku(sk_client, sk_prijava, sk_mape):
    tajna = f"KANARINAC-{uuid.uuid4()}"
    kanarinac = sk_mape.korijen / f"kanarinac-{uuid.uuid4()}.txt"
    kanarinac.write_text(tajna, encoding="utf-8")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!DOCTYPE edukacije [<!ENTITY e SYSTEM "{kanarinac.resolve().as_uri()}">]>\n'
        "<edukacije><edukacija><naziv>&e;</naziv><datum>2026-12-03</datum>"
        "<kapacitet>15</kapacitet></edukacija></edukacije>"
    )
    odgovor = sk_client.post(
        "/api/edukacije/uvoz",
        content=xml.encode("utf-8"),
        headers={**sk_prijava("voditelj"), "Content-Type": "application/xml"},
    )
    assert tajna not in odgovor.text, "sadržaj lokalne datoteke vraćen je u odgovoru"
    assert odgovor.status_code < 500, f"poslužitelj ne smije pasti ({odgovor.status_code})"
    edukacije = sk_client.get("/api/edukacije", headers=sk_prijava("ana")).text
    assert tajna not in edukacije, "sadržaj lokalne datoteke spremljen je u naziv edukacije"


def test_s05_doctype_vraca_400(sk_client, sk_prijava):
    xml = (
        '<?xml version="1.0"?>\n<!DOCTYPE edukacije [<!ENTITY n "Radionica">]>\n'
        "<edukacije><edukacija><naziv>&n;</naziv><datum>2026-12-03</datum>"
        "<kapacitet>15</kapacitet></edukacija></edukacije>"
    )
    odgovor = sk_client.post(
        "/api/edukacije/uvoz", content=xml, headers={**sk_prijava("admin"), "Content-Type": "application/xml"}
    )
    assert odgovor.status_code == 400
