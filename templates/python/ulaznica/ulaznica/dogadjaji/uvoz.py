"""Čitanje XML-a s događajima koji šalju organizatori::

    <dogadjaji><dogadjaj><naziv>Koncert</naziv><mjesto>Lisinski</mjesto>
    <datum>2026-12-12T20:00</datum><cijena>25.00</cijena><kapacitet>300</kapacitet></dogadjaj></dogadjaji>
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation

from lxml import etree

from ulaznica import novac
from ulaznica.platforma.greske import ApiGreska


@dataclass(frozen=True)
class Stavka:
    naziv: str
    mjesto: str
    datum: datetime
    cijena: Decimal
    kapacitet: int


def procitaj(xml: bytes) -> list[Stavka]:
    try:
        korijen = _ucitaj(xml)
    except etree.XMLSyntaxError as e:
        raise ApiGreska.neispravno("Neispravan XML.") from e
    stavke: list[Stavka] = []
    for redni_broj, dogadjaj in enumerate(korijen.iter("dogadjaj"), start=1):
        try:
            stavke.append(
                Stavka(
                    naziv=_tekst(dogadjaj, "naziv"),
                    mjesto=_tekst(dogadjaj, "mjesto"),
                    datum=datetime.fromisoformat(_tekst(dogadjaj, "datum")),
                    cijena=novac.iznos(_tekst(dogadjaj, "cijena")),
                    kapacitet=int(_tekst(dogadjaj, "kapacitet")),
                )
            )
        except (ValueError, InvalidOperation) as e:
            raise ApiGreska.neispravno(f"Neispravni podaci u događaju {redni_broj}.") from e
    return stavke


# @@VULN S05
def _ucitaj(xml: bytes) -> etree._Element:
    parser = etree.XMLParser(load_dtd=True, resolve_entities=True, no_network=True)
    return etree.fromstring(xml, parser)
# @@SECURE S05
def _ucitaj(xml: bytes) -> etree._Element:
    parser = etree.XMLParser(load_dtd=False, resolve_entities=False, no_network=True)
    korijen = etree.fromstring(xml, parser)
    # deklaracija tipa dokumenta (DOCTYPE) nije dopuštena
    if korijen.getroottree().docinfo.doctype:
        raise ApiGreska.neispravno("Neispravan XML.")
    return korijen
# @@END S05


def _tekst(roditelj: etree._Element, naziv: str) -> str:
    element = next(roditelj.iter(naziv), None)
    vrijednost = None if element is None else "".join(element.itertext()).strip()
    if not vrijednost:
        raise ValueError(f"Nedostaje element {naziv}")
    return vrijednost
