"""Funkcionalni testovi: aplikacija radi ono što korisnici očekuju (prolaze i prije i nakon ispravaka)."""

import pytest

pytestmark = pytest.mark.funkcionalni


def test_prijava_ispravnim_podacima(klijent):
    odgovor = klijent.post("/api/prijava", json={"korisnickoIme": "ana", "lozinka": "Ana123!"})
    assert odgovor.status_code == 200
    assert odgovor.json()["uloga"] == "CLAN"
    assert len(odgovor.json()["token"]) >= 32


def test_prijava_krivom_lozinkom_vraca_401(klijent):
    odgovor = klijent.post("/api/prijava", json={"korisnickoIme": "ana", "lozinka": "kriva-lozinka"})
    assert odgovor.status_code == 401


def test_registracija_i_prijava_novog_clana(klijent):
    podaci = {"korisnickoIme": "novi.clan", "lozinka": "NovaLozinka1!", "ime": "Novi Član", "email": "n@primjer.hr"}
    assert klijent.post("/api/registracija", json=podaci).status_code == 201
    assert klijent.post("/api/registracija", json=podaci).status_code == 409
    prijava = klijent.post("/api/prijava", json={"korisnickoIme": "novi.clan", "lozinka": "NovaLozinka1!"})
    assert prijava.status_code == 200


def test_pretraga_kataloga(klijent):
    odgovor = klijent.get("/api/knjige", params={"trazi": "Proces"})
    assert odgovor.status_code == 200
    assert [k["naslov"] for k in odgovor.json()] == ["Proces"]


def test_pretraga_bez_upita_vraca_samo_javne_knjige(klijent):
    naslovi = [k["naslov"] for k in klijent.get("/api/knjige").json()]
    assert "Zlatarovo zlato" in naslovi
    assert "Interni popis za otpis" not in naslovi


def test_podaci_o_knjizi(klijent):
    odgovor = klijent.get("/api/knjige/2")
    assert odgovor.status_code == 200
    assert odgovor.json()["autor"] == "Ivo Andrić"


def test_clan_vidi_svoj_profil(klijent, prijava):
    odgovor = klijent.get("/api/clanovi/1", headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert odgovor.json()["korisnickoIme"] == "ana"


def test_knjiznicar_vidi_profil_clana(klijent, prijava):
    odgovor = klijent.get("/api/clanovi/2", headers=prijava("knjiznicar"))
    assert odgovor.status_code == 200
    assert odgovor.json()["korisnickoIme"] == "marko"


def test_profil_bez_prijave_vraca_401(klijent):
    assert klijent.get("/api/clanovi/1").status_code == 401


def test_knjiznicar_uvozi_katalog(klijent, prijava):
    katalog = "- naslov: Kiklop\n  autor: Ranko Marinković\n  godina: 1965\n- naslov: Gospoda Glembajevi\n  autor: Miroslav Krleža\n  godina: 1929\n"
    odgovor = klijent.post(
        "/api/katalog/uvoz", content=katalog.encode("utf-8"),
        headers={**prijava("knjiznicar"), "Content-Type": "application/yaml"},
    )
    assert odgovor.status_code == 200
    assert odgovor.json() == {"uvezeno": 2}
    assert [k["naslov"] for k in klijent.get("/api/knjige", params={"trazi": "Kiklop"}).json()] == ["Kiklop"]


def test_clan_ne_moze_uvoziti_katalog(klijent, prijava):
    odgovor = klijent.post(
        "/api/katalog/uvoz", content=b"- naslov: X\n  autor: Y\n  godina: 2000\n",
        headers={**prijava("ana"), "Content-Type": "application/yaml"},
    )
    assert odgovor.status_code == 403


def test_clan_s_aktivnom_clanarinom_posudjuje_knjigu(klijent, prijava):
    odgovor = klijent.post("/api/posudbe", json={"knjigaId": 5}, headers=prijava("ana"))
    assert odgovor.status_code == 201
    assert odgovor.json()["knjigaId"] == 5


def test_produljenje_posudbe_za_sedam_dana(klijent, prijava):
    odgovor = klijent.post("/api/posudbe/1/produzi", json={"dana": 7}, headers=prijava("ana"))
    assert odgovor.status_code == 200
    assert odgovor.json()["rok"] == "2026-12-17"


def test_popis_vlastitih_posudbi(klijent, prijava):
    posudbe = klijent.get("/api/posudbe", headers=prijava("ana")).json()
    assert {p["knjigaId"] for p in posudbe} >= {1, 2, 3}
