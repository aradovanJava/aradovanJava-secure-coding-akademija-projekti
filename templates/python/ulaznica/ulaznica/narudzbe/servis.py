"""Narudžbe ulaznica: kupnja, pregled i storno."""

from __future__ import annotations

import logging
import re
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ulaznica import novac
from ulaznica.narudzbe.platni_sustav import PlatniSustavKlijent
from ulaznica.platforma.autentikacija import PrijavljeniKorisnik
from ulaznica.platforma.baza import Baza
from ulaznica.platforma.greske import ApiGreska
from ulaznica.racuni.servis import RacunService

log = logging.getLogger(__name__)

OIB = re.compile(r"\d{11}")

SELECT = (
    "SELECT n.id, n.dogadjaj_id, d.naziv, d.mjesto, d.datum, n.kupac, n.kolicina, n.ime_na_ulaznici, n.iznos, "
    "n.kreirano FROM narudzbe n JOIN dogadjaji d ON d.id = n.dogadjaj_id"
)


class NovaNarudzba(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dogadjaj_id: int | None = Field(default=None, alias="dogadjajId")
    kolicina: int | None = None
    ime_na_ulaznici: str | None = Field(default=None, alias="imeNaUlaznici")
    oib: str | None = None


def _narudzba(red: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": red["id"],
        "dogadjajId": red["dogadjaj_id"],
        "dogadjaj": red["naziv"],
        "mjesto": red["mjesto"],
        "datum": red["datum"],
        "kupac": red["kupac"],
        "kolicina": red["kolicina"],
        "imeNaUlaznici": red["ime_na_ulaznici"],
        "iznos": novac.u_json(red["iznos"]),
        "kreirano": red["kreirano"],
    }


class NarudzbaService:
    def __init__(self, baza: Baza, placanje: PlatniSustavKlijent, racuni: RacunService) -> None:
        self._baza = baza
        self._placanje = placanje
        self._racuni = racuni

    def pronadi(self, narudzba_id: int) -> dict[str, Any] | None:
        red = self._baza.jedan(SELECT + " WHERE n.id = ?", (narudzba_id,))
        return _narudzba(red) if red else None

    def narudzbe_kupca(self, username: str) -> list[dict[str, Any]]:
        redovi = self._baza.upit(SELECT + " WHERE n.kupac = ? ORDER BY d.datum, n.id", (username,))
        return [_narudzba(red) for red in redovi]

    def kreiraj(self, zahtjev: NovaNarudzba, korisnik: PrijavljeniKorisnik) -> int:
        if zahtjev.dogadjaj_id is None:
            raise ApiGreska.neispravno("Događaj je obavezan.")
        kolicina = 1 if zahtjev.kolicina is None else zahtjev.kolicina
        if not 1 <= kolicina <= 4:
            raise ApiGreska.neispravno("Količina mora biti između 1 i 4.")
        ime = zahtjev.ime_na_ulaznici
        if ime is None or not ime.strip() or len(ime) > 200:
            raise ApiGreska.neispravno("Ime na ulaznici je obavezno (najviše 200 znakova).")
        if zahtjev.oib is None or not OIB.fullmatch(zahtjev.oib):
            raise ApiGreska.neispravno("OIB mora imati 11 znamenki.")
        dogadjaj_id = zahtjev.dogadjaj_id
        dogadjaj = self._baza.jedan("SELECT naziv, cijena FROM dogadjaji WHERE id = ?", (dogadjaj_id,))
        if dogadjaj is None:
            raise ApiGreska.nije_pronadeno("Događaj nije pronađen.")
        ukupno = novac.iznos(dogadjaj["cijena"]) * kolicina
        # @@VULN S12
        log.info("Nova narudžba: %s (kupac %s)", zahtjev, korisnik.username)
        # @@SECURE S12
        log.info(
            "Nova narudžba: događaj %s, količina %s, kupac %s, OIB %s",
            dogadjaj_id,
            kolicina,
            korisnik.username,
            maskiraj_oib(zahtjev.oib),
        )
        # @@END S12
        # @@VULN S10
        stanje = self._baza.jedan("SELECT kapacitet, prodano FROM dogadjaji WHERE id = ?", (dogadjaj_id,))
        if stanje is None or stanje["prodano"] + kolicina > stanje["kapacitet"]:
            raise ApiGreska(409, "Nema slobodnih mjesta.")
        autorizacija = self._placanje.autoriziraj(korisnik.username, ukupno)
        self._baza.izvrsi("UPDATE dogadjaji SET prodano = prodano + ? WHERE id = ?", (kolicina, dogadjaj_id))
        return self._spremi(zahtjev, kolicina, ukupno, dogadjaj["naziv"], korisnik, autorizacija)
        # @@SECURE S10
        azurirano = self._baza.izvrsi(
            "UPDATE dogadjaji SET prodano = prodano + ? WHERE id = ? AND prodano + ? <= kapacitet",
            (kolicina, dogadjaj_id, kolicina),
        )
        if azurirano == 0:
            raise ApiGreska(409, "Nema slobodnih mjesta.")
        try:
            autorizacija = self._placanje.autoriziraj(korisnik.username, ukupno)
            return self._spremi(zahtjev, kolicina, ukupno, dogadjaj["naziv"], korisnik, autorizacija)
        except Exception:
            self._baza.izvrsi("UPDATE dogadjaji SET prodano = prodano - ? WHERE id = ?", (kolicina, dogadjaj_id))
            raise
        # @@END S10

    def storniraj(self, narudzba_id: int, korisnik: PrijavljeniKorisnik) -> None:
        """Storno narudžbe; račun ostaje sačuvan."""
        narudzba = self.pronadi(narudzba_id)
        # @@VULN S01
        if narudzba is None:
            raise ApiGreska.nije_pronadeno("Narudžba nije pronađena.")
        # @@SECURE S01
        if narudzba is None or not (korisnik.is_admin or narudzba["kupac"] == korisnik.username):
            raise ApiGreska.nije_pronadeno("Narudžba nije pronađena.")
        # @@END S01
        with self._baza.transakcija() as baza:
            baza.izvrsi("DELETE FROM narudzbe WHERE id = ?", (narudzba["id"],))
            baza.izvrsi(
                "UPDATE dogadjaji SET prodano = prodano - ? WHERE id = ? AND prodano >= ?",
                (narudzba["kolicina"], narudzba["dogadjajId"], narudzba["kolicina"]),
            )
        log.info("Narudžba %s je stornirana (korisnik %s)", narudzba_id, korisnik.username)

    def _spremi(
        self,
        zahtjev: NovaNarudzba,
        kolicina: int,
        ukupno: Decimal,
        dogadjaj: str,
        korisnik: PrijavljeniKorisnik,
        autorizacija: str,
    ) -> int:
        with self._baza.transakcija() as baza:
            narudzba_id = baza.umetni(
                "INSERT INTO narudzbe (dogadjaj_id, kupac, kolicina, ime_na_ulaznici, oib, iznos, kreirano, "
                "autorizacija) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    zahtjev.dogadjaj_id,
                    korisnik.username,
                    kolicina,
                    zahtjev.ime_na_ulaznici,
                    zahtjev.oib,
                    str(ukupno),
                    datetime.now().isoformat(timespec="seconds"),
                    autorizacija,
                ),
            )
            self._racuni.izdaj(narudzba_id, korisnik.username, dogadjaj, kolicina, ukupno, autorizacija)
        return narudzba_id
# @@VULN S12
# @@SECURE S12


def maskiraj_oib(oib: str | None) -> str:
    if oib is None or len(oib) < 4:
        return "***"
    return "*" * (len(oib) - 4) + oib[-4:]
# @@END S12
