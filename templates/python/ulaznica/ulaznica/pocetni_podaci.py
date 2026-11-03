"""Početni podaci (baza je u memoriji pa se puni pri svakom pokretanju).

Lozinke se spremaju istom metodom kao pri registraciji.
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal

from ulaznica.platforma.kontekst import Kontekst
from ulaznica.racuni.servis import sadrzaj

log = logging.getLogger(__name__)

# (naziv, mjesto, datum, cijena, kapacitet, prodano) – id 1–8
DOGADJAJI = [
    ("Gibonni – akustični koncert", "Lisinski, Zagreb", "2026-12-05T20:00:00", "35.00", 1800, 1),
    ("Hamlet", "HNK Zagreb", "2026-12-08T19:30:00", "22.00", 700, 2),
    ("Jazz večer u Tvornici", "Tvornica kulture, Zagreb", "2026-12-10T21:00:00", "18.00", 600, 0),
    ("Orašar – balet", "HNK Split", "2026-12-15T19:00:00", "28.00", 650, 0),
    ("Zagrebačka filharmonija – zadnja ulaznica", "Lisinski, Zagreb", "2026-12-18T19:30:00", "30.00", 100, 99),
    ("Božićni koncert", "Katedrala, Đakovo", "2026-12-20T18:00:00", "15.00", 400, 0),
    ("Stand-up večer", "Kerempuh, Zagreb", "2027-01-10T20:00:00", "20.00", 300, 0),
    ("Novogodišnji koncert", "Arena Pula", "2026-12-31T22:00:00", "45.00", 5000, 0),
]

# (dogadjaj_id, kupac, kolicina, ime_na_ulaznici, oib, iznos, autorizacija) – id 1–2
NARUDZBE = [
    (1, "ana", 1, "Ana Anić", "48291736504", "35.00", "AUTH-5000"),
    (2, "marko", 2, "Marko Marić", "73019485267", "44.00", "AUTH-5001"),
]

# (narudzba_id, kupac, datoteka) – id 1–2
RACUNI = [
    (1, "ana", "racun-ana-2026-0001.txt"),
    (2, "marko", "racun-marko-2026-0002.txt"),
]


def ucitaj(ctx: Kontekst) -> None:
    ctx.pohrana.pripremi()
    ctx.pohrana.zapisi_ako_ne_postoji(
        "racun-ana-2026-0001.txt",
        sadrzaj(1, "ana", "Gibonni – akustični koncert", 1, Decimal("35.00"), "AUTH-5000"),
    )
    ctx.pohrana.zapisi_ako_ne_postoji(
        "racun-marko-2026-0002.txt", sadrzaj(2, "marko", "Hamlet", 2, Decimal("44.00"), "AUTH-5001")
    )

    korisnici = ctx.korisnici
    korisnici.kreiraj("ana", "Ana12345!", "ana@primjer.hr", "Ana", "Anić", "KORISNIK", "48291736504")
    korisnici.kreiraj("marko", "Marko12345!", "marko@primjer.hr", "Marko", "Marić", "KORISNIK", "73019485267")
    korisnici.kreiraj(
        "organizator", "Ovlasteni12345!", "organizator@primjer.hr", "Nina", "Novak", "ORGANIZATOR", "50617283940"
    )
    korisnici.kreiraj("admin", "Admin12345!", "admin@primjer.hr", "Ivana", "Admin", "ADMIN", "61728394051")

    baza = ctx.baza
    with baza.transakcija():
        for dogadjaj in DOGADJAJI:
            baza.izvrsi(
                "INSERT INTO dogadjaji (naziv, mjesto, datum, cijena, kapacitet, prodano) VALUES (?, ?, ?, ?, ?, ?)",
                dogadjaj,
            )
        sada = datetime.now().isoformat(timespec="seconds")
        for dogadjaj_id, kupac, kolicina, ime_na_ulaznici, oib, iznos, autorizacija in NARUDZBE:
            baza.izvrsi(
                "INSERT INTO narudzbe (dogadjaj_id, kupac, kolicina, ime_na_ulaznici, oib, iznos, kreirano, "
                "autorizacija) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (dogadjaj_id, kupac, kolicina, ime_na_ulaznici, oib, iznos, sada, autorizacija),
            )
        for racun in RACUNI:
            baza.izvrsi("INSERT INTO racuni (narudzba_id, kupac, datoteka) VALUES (?, ?, ?)", racun)
    log.info("Početni podaci su učitani")
