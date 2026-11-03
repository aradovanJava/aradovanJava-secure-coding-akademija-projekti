"""S05 – XXE kod uvoza događaja iz XML-a."""

import uuid


def test_s05_vanjski_entitet_ne_smije_procitati_datoteku(sk_client, sk_prijava, sk_mape):
    tajna = f"KANARINAC-{uuid.uuid4()}"
    kanarinac = sk_mape.korijen / f"kanarinac-{uuid.uuid4()}.txt"
    kanarinac.write_text(tajna, encoding="utf-8")
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<!DOCTYPE dogadjaji [<!ENTITY e SYSTEM "{kanarinac.resolve().as_uri()}">]>\n'
        "<dogadjaji><dogadjaj><naziv>&e;</naziv><mjesto>Lisinski</mjesto><datum>2027-03-01T20:00</datum>"
        "<cijena>25.00</cijena><kapacitet>300</kapacitet></dogadjaj></dogadjaji>"
    )
    odgovor = sk_client.post(
        "/api/dogadjaji/uvoz",
        content=xml.encode("utf-8"),
        headers={**sk_prijava("organizator"), "Content-Type": "application/xml"},
    )
    assert tajna not in odgovor.text, "sadržaj lokalne datoteke vraćen je u odgovoru"
    assert odgovor.status_code < 500, f"poslužitelj ne smije pasti ({odgovor.status_code})"
    dogadjaji = sk_client.get("/api/dogadjaji", headers=sk_prijava("ana")).text
    assert tajna not in dogadjaji, "sadržaj lokalne datoteke spremljen je u naziv događaja"


def test_s05_doctype_vraca_400(sk_client, sk_prijava):
    xml = (
        '<?xml version="1.0"?>\n<!DOCTYPE dogadjaji [<!ENTITY n "Klapa">]>\n'
        "<dogadjaji><dogadjaj><naziv>&n;</naziv><mjesto>Lisinski</mjesto><datum>2027-03-02T20:00</datum>"
        "<cijena>25.00</cijena><kapacitet>300</kapacitet></dogadjaj></dogadjaji>"
    )
    odgovor = sk_client.post(
        "/api/dogadjaji/uvoz", content=xml, headers={**sk_prijava("admin"), "Content-Type": "application/xml"}
    )
    assert odgovor.status_code == 400
