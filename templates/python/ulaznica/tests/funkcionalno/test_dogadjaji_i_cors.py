from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno

FRONTEND = "http://localhost:5173"


def _polje(odgovor, naziv: str) -> list:
    return [dogadjaj[naziv] for dogadjaj in odgovor.json()]


def test_dogadjaji_po_datumu_uzlazno(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/dogadjaji", params={"sort": "datum", "smjer": "asc"}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    datumi = _polje(odgovor, "datum")
    assert len(datumi) >= 8
    assert datumi == sorted(datumi)
    nazivi = _polje(odgovor, "naziv")
    assert nazivi[0] == "Gibonni – akustični koncert"
    assert "Hamlet" in nazivi
    assert "Božićni koncert" in nazivi


def test_dogadjaji_po_nazivu_silazno(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/dogadjaji", params={"sort": "naziv", "smjer": "desc"}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    nazivi = _polje(odgovor, "naziv")
    assert nazivi == sorted(nazivi, reverse=True)


def test_dogadjaji_po_cijeni_i_mjestu(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    po_cijeni = client.get("/api/dogadjaji", params={"sort": "cijena", "smjer": "asc"}, headers=zaglavlja)
    po_mjestu = client.get("/api/dogadjaji", params={"sort": "mjesto", "smjer": "asc"}, headers=zaglavlja)
    cijene = [Decimal(str(cijena)) for cijena in _polje(po_cijeni, "cijena")]
    assert cijene == sorted(cijene)
    assert cijene[0] == Decimal("15.00")
    mjesta = _polje(po_mjestu, "mjesto")
    assert mjesta == sorted(mjesta)


def test_zadano_sortiranje_je_po_datumu(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/dogadjaji", headers=prijava("ana"))
    assert odgovor.status_code == 200
    datumi = _polje(odgovor, "datum")
    assert datumi == sorted(datumi)


def test_popis_dogadjaja_prikazuje_slobodna_mjesta(client: TestClient, prijava) -> None:
    for dogadjaj in client.get("/api/dogadjaji", headers=prijava("ana")).json():
        assert dogadjaj["slobodno"] == dogadjaj["kapacitet"] - dogadjaj["prodano"]


def test_popis_dogadjaja_trazi_prijavu(client: TestClient) -> None:
    assert client.get("/api/dogadjaji").status_code == 401


def test_cors_za_dopusteni_origin(client: TestClient) -> None:
    odgovor = client.get("/api/health", headers={"Origin": FRONTEND})
    assert odgovor.status_code == 200
    assert odgovor.headers.get("Access-Control-Allow-Origin") == FRONTEND
    assert odgovor.headers.get("Access-Control-Allow-Credentials") == "true"


def test_preflight_s_dopustenog_origina(client: TestClient) -> None:
    odgovor = client.options(
        "/api/ja",
        headers={
            "Origin": FRONTEND,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "authorization",
        },
    )
    assert 200 <= odgovor.status_code < 300
    assert odgovor.headers.get("Access-Control-Allow-Origin") == FRONTEND
