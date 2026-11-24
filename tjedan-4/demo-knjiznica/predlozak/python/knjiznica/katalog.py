"""Uvoz kataloga u YAML formatu (samo knjižničar).

Primjer tijela zahtjeva (Content-Type: application/yaml):

- naslov: Kiklop
  autor: Ranko Marinković
  godina: 1965
"""

import yaml
from fastapi import APIRouter, Request

from knjiznica.autentikacija import Prijavljeni
from knjiznica.greske import ApiGreska

router = APIRouter(prefix="/api/katalog")

NAJVECA_VELICINA = 100_000


@router.post("/uvoz")
async def uvoz(request: Request, korisnik: Prijavljeni) -> dict[str, int]:
    if korisnik.uloga != "KNJIZNICAR":
        raise ApiGreska.zabranjeno("Uvoz kataloga dopušten je samo knjižničarima.")
    tijelo = (await request.body()).decode("utf-8", errors="replace")
    if len(tijelo) > NAJVECA_VELICINA:
        raise ApiGreska.neispravno("Katalog je prevelik.")
    try:
        # @@VULN K03
        dokument = yaml.load(tijelo, Loader=yaml.FullLoader)
        # @@SECURE K03
        dokument = yaml.safe_load(tijelo)
        # @@END K03
    except yaml.YAMLError as e:
        raise ApiGreska.neispravno("Neispravan YAML.") from e
    if not isinstance(dokument, list) or not dokument:
        raise ApiGreska.neispravno("Očekuje se popis knjiga.")
    knjige: list[tuple[str, str, int]] = []
    for stavka in dokument:
        if not isinstance(stavka, dict):
            raise ApiGreska.neispravno("Neispravna knjiga u katalogu.")
        naslov, autor, godina = stavka.get("naslov"), stavka.get("autor"), stavka.get("godina")
        if not isinstance(naslov, str) or not isinstance(autor, str) or not isinstance(godina, int):
            raise ApiGreska.neispravno("Neispravna knjiga u katalogu.")
        if not naslov.strip() or not autor.strip():
            raise ApiGreska.neispravno("Neispravna knjiga u katalogu.")
        knjige.append((naslov.strip(), autor.strip(), godina))
    for knjiga in knjige:
        request.app.state.baza.izvrsi("INSERT INTO knjige (naslov, autor, godina) VALUES (?, ?, ?)", knjiga)
    return {"uvezeno": len(knjige)}
