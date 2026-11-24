"""Pretraga kataloga i podaci o knjizi (javno, bez prijave)."""

from typing import Any

from fastapi import APIRouter, Request

# @@VULN K05
# @@SECURE K05
from knjiznica.greske import ApiGreska

# @@END K05
router = APIRouter(prefix="/api/knjige")


@router.get("")
def pretrazi(request: Request, trazi: str = "") -> list[dict[str, Any]]:
    baza = request.app.state.baza
    # @@VULN K02
    sql = (
        "SELECT id, naslov, autor, godina FROM knjige "
        f"WHERE skrivena = 0 AND naslov LIKE '%{trazi}%' ORDER BY naslov"
    )
    redovi = baza.svi(sql)
    # @@SECURE K02
    if len(trazi) > 100:
        raise ApiGreska.neispravno("Upit je predugačak.")
    # parametrizirani upit; znakovi %, _ i \ u upitu traže se doslovno
    uzorak = "%" + trazi.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
    redovi = baza.svi(
        "SELECT id, naslov, autor, godina FROM knjige "
        "WHERE skrivena = 0 AND naslov LIKE ? ESCAPE '\\' ORDER BY naslov",
        (uzorak,),
    )
    # @@END K02
    return [dict(red) for red in redovi]


@router.get("/{knjiga_id}")
def dohvati(knjiga_id: int, request: Request) -> dict[str, Any]:
    red = request.app.state.baza.jedan(
        "SELECT id, naslov, autor, godina FROM knjige WHERE id = ? AND skrivena = 0", (knjiga_id,)
    )
    # @@VULN K05
    # @@SECURE K05
    if red is None:
        raise ApiGreska.nije_pronadjeno("Knjiga nije pronađena.")
    # @@END K05
    return {"id": red["id"], "naslov": red["naslov"], "autor": red["autor"], "godina": red["godina"]}
