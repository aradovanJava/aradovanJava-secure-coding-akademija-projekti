"""S10 – utrka kod rezervacije zadnjeg slobodnog mjesta (termin 7)."""

import threading

import httpx2 as httpx

TERMIN = 7
ZAHTJEVA = 10


def _stanje(app):
    red = app.state.baza.jedan("SELECT kapacitet, zauzeto FROM termini WHERE id = ?", (TERMIN,))
    return red["kapacitet"], red["zauzeto"]


def test_s10_samo_jedan_dobiva_zadnje_mjesto(sk_posluzitelj):
    kapacitet, zauzeto = _stanje(sk_posluzitelj.app)
    assert kapacitet - zauzeto == 1, "preduvjet: termin 7 ima točno jedno slobodno mjesto"
    url = sk_posluzitelj.url
    tokeni = []
    with httpx.Client(base_url=url, timeout=30) as klijent:
        for i in range(ZAHTJEVA):
            username = f"utrka{i}x{threading.get_ident() % 1000}"
            r = klijent.post(
                "/api/auth/register",
                json={
                    "username": username,
                    "password": "Utrka12345!",
                    "email": f"{username}@primjer.hr",
                    "ime": "U",
                    "prezime": "T",
                },
            )
            assert r.status_code == 201, r.text
            r = klijent.post("/api/auth/login", json={"username": username, "password": "Utrka12345!"})
            assert r.status_code == 200, r.text
            tokeni.append(r.json()["token"])

    start = threading.Barrier(ZAHTJEVA)
    statusi: list[int] = []
    brava = threading.Lock()

    def rezerviraj(token: str) -> None:
        with httpx.Client(base_url=url, timeout=60) as k:
            start.wait(timeout=20)
            r = k.post(
                "/api/rezervacije",
                json={"terminId": TERMIN, "napomena": "Zadnji termin", "oib": "12345678903"},
                headers={"Authorization": f"Bearer {token}"},
            )
        with brava:
            statusi.append(r.status_code)

    dretve = [threading.Thread(target=rezerviraj, args=(t,)) for t in tokeni]
    for d in dretve:
        d.start()
    for d in dretve:
        d.join(timeout=90)

    kapacitet, zauzeto = _stanje(sk_posluzitelj.app)
    assert statusi.count(201) == 1, f"broj uspješnih rezervacija zadnjeg mjesta (statusi: {sorted(statusi)})"
    assert statusi.count(409) == ZAHTJEVA - 1, f"ostali moraju dobiti 409 (statusi: {sorted(statusi)})"
    assert zauzeto == kapacitet, f"zauzeto={zauzeto}, kapacitet={kapacitet}"
