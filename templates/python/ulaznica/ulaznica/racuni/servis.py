"""Izdavanje računa: tekstualna datoteka u ``storage_dir`` i zapis u tablici ``racuni``."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ulaznica.platforma.baza import Baza
from ulaznica.platforma.pohrana import Pohrana


def naziv_datoteke(kupac: str, narudzba_id: int) -> str:
    return f"racun-{kupac}-{date.today().year}-{narudzba_id:04d}.txt"


def sadrzaj(narudzba_id: int, kupac: str, dogadjaj: str, kolicina: int, iznos: Decimal, autorizacija: str) -> str:
    return (
        f"Ulaznica d.o.o. – račun za narudžbu {narudzba_id}\n"
        f"Kupac: {kupac}\n"
        f"Događaj: {dogadjaj}\n"
        f"Količina: {kolicina}\n"
        f"Ukupno: {iznos} EUR\n"
        f"Autorizacija plaćanja: {autorizacija}\n"
        "Hvala na kupnji!\n"
    )


class RacunService:
    def __init__(self, baza: Baza, pohrana: Pohrana) -> None:
        self._baza = baza
        self._pohrana = pohrana

    def izdaj(
        self, narudzba_id: int, kupac: str, dogadjaj: str, kolicina: int, iznos: Decimal, autorizacija: str
    ) -> int:
        datoteka = naziv_datoteke(kupac, narudzba_id)
        (self._pohrana.dokumenti / datoteka).write_text(
            sadrzaj(narudzba_id, kupac, dogadjaj, kolicina, iznos, autorizacija), encoding="utf-8"
        )
        return self._baza.umetni(
            "INSERT INTO racuni (narudzba_id, kupac, datoteka) VALUES (?, ?, ?)", (narudzba_id, kupac, datoteka)
        )
