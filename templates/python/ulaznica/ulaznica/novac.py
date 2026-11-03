"""Novčani iznosi u eurima (dvije decimale)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def iznos(vrijednost: object) -> Decimal:
    """Iznos iz baze ili iz ulaznih podataka, zaokružen na cente (npr. ``"25"`` → ``Decimal("25.00")``)."""
    broj = Decimal(str(vrijednost).strip())
    if not broj.is_finite():
        raise ValueError(f"Neispravan iznos: {vrijednost}")
    return broj.quantize(CENT, rounding=ROUND_HALF_UP)


def u_json(vrijednost: object) -> float:
    """Iznos kao JSON broj (npr. ``25.0``)."""
    return float(iznos(vrijednost))
