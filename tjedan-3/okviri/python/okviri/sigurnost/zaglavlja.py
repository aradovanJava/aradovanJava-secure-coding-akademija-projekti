"""Sigurnosna zaglavlja za SVAKI odgovor (FastAPI/Starlette ih ne dodaju sami).

Čisti ASGI middleware (bez BaseHTTPMiddleware): dodaje zaglavlja u poruku http.response.start,
pa vrijedi i za odgovore koje stvaraju drugi middlewarei (CORS preflight, TrustedHost) i za greške.
"""

from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

SIGURNOSNA_ZAGLAVLJA = {
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Cache-Control": "no-store",
}
HSTS = "max-age=31536000; includeSubDomains"


class SigurnosnaZaglavlja:
    def __init__(self, app: ASGIApp, hsts: bool = False) -> None:
        self.app = app
        self.zaglavlja = dict(SIGURNOSNA_ZAGLAVLJA)
        if hsts:
            self.zaglavlja["Strict-Transport-Security"] = HSTS

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def posalji(poruka: Message) -> None:
            if poruka["type"] == "http.response.start":
                zaglavlja = MutableHeaders(scope=poruka)
                for ime, vrijednost in self.zaglavlja.items():
                    zaglavlja.setdefault(ime, vrijednost)  # ruta smije postaviti vlastitu (npr. CSP za HTML)
            await send(poruka)

        await self.app(scope, receive, posalji)
