"""S10 – utrka kod kupnje zadnje ulaznice (događaj 5: kapacitet 100, prodano 99)."""

import threading

import httpx2 as httpx

DOGADJAJ = 5
ZAHTJEVA = 10


def _stanje(app):
    red = app.state.baza.jedan("SELECT kapacitet, prodano FROM dogadjaji WHERE id = ?", (DOGADJAJ,))
    return red["kapacitet"], red["prodano"]


def test_s10_samo_jedan_kupuje_zadnju_ulaznicu(sk_posluzitelj):
    kapacitet, prodano = _stanje(sk_posluzitelj.app)
    assert kapacitet - prodano == 1, "preduvjet: događaj 5 ima točno jednu slobodnu ulaznicu"
    url = sk_posluzitelj.url
    tokeni = []
    with httpx.Client(base_url=url, timeout=30) as klijent:
        for i in range(ZAHTJEVA):
            username = f"utrka{i}x{threading.get_ident() % 1000}"
            r = klijent.post(
                "/api/auth/register",
                json={"username": username, "password": "Utrka12345!", "email": f"{username}@primjer.hr",
                      "ime": "U", "prezime": "T"},
            )
            assert r.status_code == 201, r.text
            r = klijent.post("/api/auth/login", json={"username": username, "password": "Utrka12345!"})
            assert r.status_code == 200, r.text
            tokeni.append(r.json()["token"])

    start = threading.Barrier(ZAHTJEVA)
    statusi: list[int] = []
    brava = threading.Lock()

    def kupi(token: str) -> None:
        with httpx.Client(base_url=url, timeout=60) as k:
            start.wait(timeout=20)
            r = k.post(
                "/api/narudzbe",
                json={"dogadjajId": DOGADJAJ, "kolicina": 1, "imeNaUlaznici": "Zadnja ulaznica",
                      "oib": "12345678903"},
                headers={"Authorization": f"Bearer {token}"},
            )
        with brava:
            statusi.append(r.status_code)

    dretve = [threading.Thread(target=kupi, args=(t,)) for t in tokeni]
    for d in dretve:
        d.start()
    for d in dretve:
        d.join(timeout=90)

    kapacitet, prodano = _stanje(sk_posluzitelj.app)
    assert statusi.count(201) == 1, f"broj uspješnih kupnji zadnje ulaznice (statusi: {sorted(statusi)})"
    assert statusi.count(409) == ZAHTJEVA - 1, f"ostali moraju dobiti 409 (statusi: {sorted(statusi)})"
    assert prodano == kapacitet, f"prodano={prodano}, kapacitet={kapacitet}"
