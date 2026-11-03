"""Klijent platnog sustava (autorizacija plaćanja karticom).

U lokalnom okruženju platni sustav nije dostupan pa klijent nakon uobičajenog vremena odziva vraća lokalno
generiranu oznaku autorizacije.
"""

from __future__ import annotations

import itertools
import threading
import time
from decimal import Decimal

VRIJEME_ODZIVA = 0.15  # sekunde


class PlatniSustavKlijent:
    def __init__(self) -> None:
        self._brojac = itertools.count(5002)
        self._brava = threading.Lock()

    def autoriziraj(self, kupac: str, iznos: Decimal) -> str:
        time.sleep(VRIJEME_ODZIVA)
        with self._brava:
            broj = next(self._brojac)
        return f"AUTH-{broj}"
