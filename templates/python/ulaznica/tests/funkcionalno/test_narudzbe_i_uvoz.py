import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.funkcionalno

# Događaj 5 je rezerviran za posebne provjere i ne koristi se u ovim testovima.
IZUZETI_DOGADJAJ = 5

XML = """<?xml version="1.0" encoding="UTF-8"?>
<dogadjaji>
  <dogadjaj>
    <naziv>Klapa u Lisinskom</naziv>
    <mjesto>Lisinski, Zagreb</mjesto>
    <datum>2026-12-12T20:00</datum>
    <cijena>25.00</cijena>
    <kapacitet>300</kapacitet>
  </dogadjaj>
</dogadjaji>
"""


def _uvoz(client: TestClient, zaglavlja: dict[str, str], xml: str):
    return client.post("/api/dogadjaji/uvoz", content=xml, headers={**zaglavlja, "Content-Type": "application/xml"})


def _novi_dogadjaj(client: TestClient, prijava, kapacitet: int) -> int:
    xml = (
        "<dogadjaji><dogadjaj><naziv>Dodatni koncert</naziv><mjesto>Dom sportova</mjesto>"
        f"<datum>2027-02-01T20:00</datum><cijena>20.00</cijena><kapacitet>{kapacitet}</kapacitet>"
        "</dogadjaj></dogadjaji>"
    )
    odgovor = _uvoz(client, prijava("organizator"), xml)
    assert odgovor.status_code == 200
    return odgovor.json()["dogadjaji"][0]["id"]


def _dogadjaj(client: TestClient, zaglavlja: dict[str, str], dogadjaj_id: int) -> dict:
    return next(d for d in client.get("/api/dogadjaji", headers=zaglavlja).json() if d["id"] == dogadjaj_id)


def _moje(client: TestClient, zaglavlja: dict[str, str]) -> list[int]:
    return [n["id"] for n in client.get("/api/narudzbe/moje", headers=zaglavlja).json()]


def _naruci(client: TestClient, zaglavlja: dict[str, str], dogadjaj_id: int, kolicina: int, ime: str):
    return client.post(
        "/api/narudzbe",
        json={"dogadjajId": dogadjaj_id, "kolicina": kolicina, "imeNaUlaznici": ime, "oib": "48291736504"},
        headers=zaglavlja,
    )


def test_nova_narudzba_je_vidljiva_u_mojim_narudzbama(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    odgovor = _naruci(client, zaglavlja, 3, 2, "Ana Anić")
    assert odgovor.status_code == 201
    narudzba = odgovor.json()
    assert narudzba["kolicina"] == 2
    assert narudzba["imeNaUlaznici"] == "Ana Anić"
    assert narudzba["iznos"] == 36.0
    assert narudzba["id"] in _moje(client, zaglavlja)


def test_narudzba_izdaje_racun_vidljiv_kupcu(client: TestClient, prijava) -> None:
    zaglavlja = prijava("marko")
    narudzba_id = _naruci(client, zaglavlja, 4, 1, "Marko Marić").json()["id"]
    racuni = client.get("/api/racuni/moji", headers=zaglavlja).json()
    assert narudzba_id in [racun["narudzbaId"] for racun in racuni]


def test_kolicina_izvan_raspona_vraca_400(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    assert _naruci(client, zaglavlja, 3, 5, "Ana Anić").status_code == 400
    assert _naruci(client, zaglavlja, 3, 0, "Ana Anić").status_code == 400


def test_neispravan_oib_vraca_400(client: TestClient, prijava) -> None:
    odgovor = client.post(
        "/api/narudzbe",
        json={"dogadjajId": 3, "kolicina": 1, "imeNaUlaznici": "Ana Anić", "oib": "123"},
        headers=prijava("ana"),
    )
    assert odgovor.status_code == 400


def test_narudzba_rasprodanog_dogadjaja_vraca_409(client: TestClient, prijava) -> None:
    dogadjaj_id = _novi_dogadjaj(client, prijava, 1)
    assert _naruci(client, prijava("ana"), dogadjaj_id, 1, "Ana Anić").status_code == 201
    odgovor = _naruci(client, prijava("marko"), dogadjaj_id, 1, "Marko Marić")
    assert odgovor.status_code == 409
    assert odgovor.json()["greska"] == "Nema slobodnih mjesta."


def test_kupac_moze_stornirati_vlastitu_narudzbu(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    dogadjaj_id = _novi_dogadjaj(client, prijava, 50)
    narudzba_id = _naruci(client, zaglavlja, dogadjaj_id, 3, "Ana Anić").json()["id"]
    prodano_prije = _dogadjaj(client, zaglavlja, dogadjaj_id)["prodano"]

    odgovor = client.delete(f"/api/narudzbe/{narudzba_id}", headers=zaglavlja)

    assert odgovor.status_code == 204
    assert narudzba_id not in _moje(client, zaglavlja)
    assert _dogadjaj(client, zaglavlja, dogadjaj_id)["prodano"] == prodano_prije - 3


def test_ulaznica_za_ispis_sadrzi_ime_na_ulaznici(client: TestClient, prijava) -> None:
    zaglavlja = prijava("ana")
    narudzba_id = _naruci(client, zaglavlja, 6, 1, "Ana i Marko").json()["id"]
    odgovor = client.get(f"/ispis/narudzbe/{narudzba_id}", headers=zaglavlja)
    assert odgovor.status_code == 200
    assert odgovor.headers["content-type"].startswith("text/html")
    assert "Ana i Marko" in odgovor.text
    assert "Božićni koncert" in odgovor.text


def test_narudzba_nepostojeceg_dogadjaja_vraca_404(client: TestClient, prijava) -> None:
    assert _naruci(client, prijava("ana"), 999_999, 1, "Ana Anić").status_code == 404


def test_izuzeti_dogadjaj_postoji(client: TestClient, prijava) -> None:
    assert _dogadjaj(client, prijava("ana"), IZUZETI_DOGADJAJ)["kapacitet"] == 100


def test_organizator_uvozi_dogadjaje_iz_xml(client: TestClient, prijava) -> None:
    zaglavlja = prijava("organizator")
    odgovor = _uvoz(client, zaglavlja, XML)
    assert odgovor.status_code == 200
    assert odgovor.json()["uvezeno"] == 1
    dogadjaj = odgovor.json()["dogadjaji"][0]
    assert dogadjaj["naziv"] == "Klapa u Lisinskom"
    uvezeni = _dogadjaj(client, zaglavlja, dogadjaj["id"])
    assert uvezeni["cijena"] == 25.0
    assert uvezeni["kapacitet"] == 300


def test_administrator_moze_uvoziti_dogadjaje(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("admin"), XML).status_code == 200


def test_korisnik_ne_moze_uvoziti_dogadjaje(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("ana"), XML).status_code == 403


def test_neispravan_xml_vraca_400(client: TestClient, prijava) -> None:
    assert _uvoz(client, prijava("organizator"), "<dogadjaji><dogadjaj>").status_code == 400
