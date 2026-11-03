"""S04 – CORS ne smije reflektirati proizvoljan Origin uz credentials."""

ZLO = "https://zlo.example"


def _provjeri(odgovor):
    allow = odgovor.headers.get("access-control-allow-origin")
    assert allow not in (ZLO, "*"), f"Access-Control-Allow-Origin: {allow}"


def test_s04_get_s_tudim_originom(sk_client, sk_prijava):
    _provjeri(sk_client.get("/api/ja", headers={**sk_prijava("ana"), "Origin": ZLO}))


def test_s04_preflight_s_tudim_originom(sk_client):
    _provjeri(
        sk_client.options(
            "/api/ja",
            headers={"Origin": ZLO, "Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "authorization"},
        )
    )
