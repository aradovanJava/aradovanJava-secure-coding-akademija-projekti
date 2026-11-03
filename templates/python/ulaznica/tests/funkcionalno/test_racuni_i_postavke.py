import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno


def test_moji_racuni_sadrze_racun_iz_pocetnih_podataka(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/racuni/moji", headers=prijava("ana"))
    assert odgovor.status_code == 200
    racuni = odgovor.json()
    assert all(racun["kupac"] == "ana" for racun in racuni)
    assert "racun-ana-2026-0001.txt" in [racun["datoteka"] for racun in racuni]


def test_preuzimanje_vlastite_datoteke_racuna(client: TestClient, prijava) -> None:
    odgovor = client.get(
        "/api/racuni/preuzmi", params={"datoteka": "racun-ana-2026-0001.txt"}, headers=prijava("ana")
    )
    assert odgovor.status_code == 200
    assert "Kupac: ana" in odgovor.text
    assert "Gibonni" in odgovor.text


def test_racun_u_json_formatu(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/racuni/2", params={"format": "json"}, headers=prijava("marko"))
    assert odgovor.status_code == 200
    assert odgovor.json()["narudzbaId"] == 2
    assert "Hamlet" in odgovor.json()["sadrzaj"]


def test_racun_u_pdf_formatu(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/racuni/1", params={"format": "pdf"}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert odgovor.headers["content-type"].startswith("application/pdf")
    assert odgovor.content.startswith(b"%PDF")


def test_bez_parametra_format_racun_je_json(client: TestClient, prijava) -> None:
    odgovor = client.get("/api/racuni/1", headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert "Gibonni" in odgovor.json()["sadrzaj"]


def test_spremanje_postavki_u_yaml_formatu(client: TestClient, prijava) -> None:
    yaml = "podsjetnik: true\nsatiPrije: 24\nkanal: email\n"
    zaglavlja = {**prijava("marko"), "Content-Type": "application/yaml"}
    odgovor = client.post("/api/postavke", content=yaml, headers=zaglavlja)
    assert odgovor.status_code == 200
    assert odgovor.json()["postavke"] == {"podsjetnik": True, "satiPrije": 24, "kanal": "email"}


def test_spremljene_postavke_mogu_se_dohvatiti(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    spremanje = client.post(
        "/api/postavke",
        content="podsjetnik: false\nsatiPrije: 48\nkanal: sms\n",
        headers={**zaglavlja, "Content-Type": "text/plain"},
    )
    dohvat = client.get("/api/postavke", headers=zaglavlja)
    assert spremanje.status_code == 200
    assert dohvat.json()["postavke"] == {"podsjetnik": False, "satiPrije": 48, "kanal": "sms"}


def test_nepoznat_kanal_obavijesti_vraca_400(client: TestClient, prijava) -> None:
    odgovor = client.post(
        "/api/postavke",
        content="kanal: golub\n",
        headers={**prijava("ana"), "Content-Type": "application/yaml"},
    )
    assert odgovor.status_code == 400
