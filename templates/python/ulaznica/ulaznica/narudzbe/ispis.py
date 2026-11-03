"""Ulaznica za ispis (HTML)."""

from __future__ import annotations

from datetime import datetime
# @@VULN S09
# @@SECURE S09
from html import escape
# @@END S09

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from ulaznica.platforma.autentikacija import Prijavljeni
from ulaznica.platforma.greske import ApiGreska
from ulaznica.platforma.kontekst import Ctx

router = APIRouter()


@router.get("/ispis/narudzbe/{narudzba_id}", response_class=HTMLResponse)
def ispis_ulaznice(narudzba_id: int, korisnik: Prijavljeni, ctx: Ctx) -> HTMLResponse:
    n = ctx.narudzbe.pronadi(narudzba_id)
    if n is None or not (korisnik.is_admin or n["kupac"] == korisnik.username):
        raise ApiGreska.nije_pronadeno("Narudžba nije pronađena.")
    datum = datetime.fromisoformat(n["datum"]).strftime("%d.%m.%Y. u %H:%M") if n["datum"] else ""
    sadrzaj = f"""<!DOCTYPE html>
<html lang="hr">
<head>
<meta charset="UTF-8">
<title>Ulaznica br. {n["id"]}</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 40rem; margin: 2rem auto; }}
.ulaznica {{ border: 2px dashed #333; padding: 1rem 1.5rem; }}
dt {{ font-weight: bold; margin-top: .5rem; }}
</style>
</head>
<body>
<div class="ulaznica">
<h1>{_tekst(ctx.postavke.naziv)}</h1>
<h2>{_tekst(n["dogadjaj"])}</h2>
<dl>
<dt>Ime na ulaznici</dt><dd>{_tekst(n["imeNaUlaznici"])}</dd>
<dt>Mjesto</dt><dd>{_tekst(n["mjesto"])}</dd>
<dt>Datum</dt><dd>{datum}</dd>
<dt>Broj ulaznica</dt><dd>{n["kolicina"]}</dd>
<dt>Broj narudžbe</dt><dd>{n["id"]}</dd>
</dl>
<p>Ulaznicu pokažite na ulazu (ispisanu ili na mobitelu).</p>
</div>
</body>
</html>
"""
    odgovor = HTMLResponse(content=sadrzaj)
    # @@VULN S09
    # @@SECURE S09
    odgovor.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'unsafe-inline'"
    # @@END S09
    return odgovor


# @@VULN S09
def _tekst(vrijednost: str | None) -> str:
    return "" if vrijednost is None else vrijednost
# @@SECURE S09
def _tekst(vrijednost: str | None) -> str:
    return "" if vrijednost is None else escape(vrijednost)
# @@END S09
