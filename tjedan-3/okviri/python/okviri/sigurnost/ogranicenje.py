"""Ograničavanje broja pokušaja prijave: N pokušaja u minuti po IP adresi, zatim 429 + Retry-After.

Biblioteka limits (fixed window) – ista koju interno koristi slowapi – kao obična FastAPI ovisnost na ruti
prijave. Brojači su u memoriji jednog procesa; za više instanci: storage_from_string("redis://…")
ili ograničenje na API gatewayu.
"""

import math
import time

from fastapi import HTTPException, Request, status
from limits import RateLimitItemPerMinute
from limits.storage import MemoryStorage, Storage
from limits.strategies import FixedWindowRateLimiter

PREVISE_POKUSAJA = "Previše pokušaja prijave. Pokušajte ponovno kasnije."


class OgranicenjePrijave:
    def __init__(self, pokusaja_u_minuti: int, spremiste: Storage | None = None) -> None:
        self._limit = RateLimitItemPerMinute(pokusaja_u_minuti)
        self._limiter = FixedWindowRateLimiter(spremiste or MemoryStorage())

    def provjeri(self, kljuc: str) -> None:
        if self._limiter.hit(self._limit, "prijava", kljuc):
            return
        reset, _ = self._limiter.get_window_stats(self._limit, "prijava", kljuc)
        sekundi = max(1, math.ceil(reset - time.time()))
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, PREVISE_POKUSAJA, headers={"Retry-After": str(sekundi)})


def ogranicenje_prijave(request: Request) -> None:
    """Ovisnost rute: dependencies=[Depends(ogranicenje_prijave)].

    Iza reverse proxyja IP dolazi iz X-Forwarded-For samo ako mu uvicorn vjeruje (--forwarded-allow-ips),
    inače su svi klijenti "ista adresa".
    """
    ip = request.client.host if request.client else "nepoznato"
    request.app.state.ogranicenje_prijave.provjeri(ip)
