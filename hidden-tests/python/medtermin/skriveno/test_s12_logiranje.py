"""S12 – lozinka i OIB ne smiju biti u logu; neuspjela prijava mora biti zabilježena."""

import logging

from .conftest import sk_login


def test_s12_log_bez_lozinke_i_oiba_s_neuspjelom_prijavom(sk_client, caplog):
    caplog.set_level(logging.DEBUG)
    odgovor = sk_login(sk_client, "ana", "Ana12345!")
    assert odgovor.status_code == 200
    zaglavlja = {"Authorization": f"Bearer {odgovor.json()['token']}"}
    r = sk_client.post("/api/rezervacije", json={"terminId": 9, "napomena": "Kontrola", "oib": "48291736504"}, headers=zaglavlja)
    assert r.status_code == 201, f"preduvjet: rezervacija ({r.status_code} {r.text})"
    assert sk_login(sk_client, "marko", "pogresna-lozinka").status_code == 401

    zapisi = [(z.levelno, z.getMessage()) for z in caplog.records]
    tekst = "\n".join(poruka for _, poruka in zapisi)
    assert "Ana12345!" not in tekst, "lozinka je zapisana u log"
    assert "48291736504" not in tekst, "cijeli OIB je zapisan u log"
    assert any(razina >= logging.WARNING and "marko" in poruka for razina, poruka in zapisi), (
        "neuspjela prijava korisnika marko nije zapisana na razini WARNING"
    )
