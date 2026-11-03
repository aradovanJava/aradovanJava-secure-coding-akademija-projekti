"""S10 – utrka kod prijave na zadnje slobodno mjesto edukacije (edukacija 3: kapacitet 20, prijavljeno 19)."""

import threading
import uuid

import httpx2 as httpx

EDUKACIJA = 3
ZAHTJEVA = 10


def _stanje(app):
    red = app.state.baza.jedan("SELECT kapacitet, prijavljeno FROM edukacije WHERE id = ?", (EDUKACIJA,))
    return red["kapacitet"], red["prijavljeno"]


def test_s10_samo_jedan_dobiva_zadnje_mjesto(sk_posluzitelj):
    kapacitet, prijavljeno = _stanje(sk_posluzitelj.app)
    assert kapacitet - prijavljeno == 1, "preduvjet: edukacija 3 ima točno jedno slobodno mjesto"
    url = sk_posluzitelj.url
    tokeni = []
    with httpx.Client(base_url=url, timeout=30) as klijent:
        for _ in range(ZAHTJEVA):
            username = f"utrka{uuid.uuid4().hex[:10]}"
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

    def prijavi(token: str) -> None:
        with httpx.Client(base_url=url, timeout=60) as k:
            start.wait(timeout=20)
            r = k.post(f"/api/edukacije/{EDUKACIJA}/prijava", headers={"Authorization": f"Bearer {token}"})
        with brava:
            statusi.append(r.status_code)

    dretve = [threading.Thread(target=prijavi, args=(t,)) for t in tokeni]
    for d in dretve:
        d.start()
    for d in dretve:
        d.join(timeout=90)

    kapacitet, prijavljeno = _stanje(sk_posluzitelj.app)
    assert statusi.count(201) == 1, f"broj uspješnih prijava na zadnje mjesto (statusi: {sorted(statusi)})"
    assert statusi.count(409) == ZAHTJEVA - 1, f"ostali moraju dobiti 409 (statusi: {sorted(statusi)})"
    assert prijavljeno == kapacitet, f"prijavljeno={prijavljeno}, kapacitet={kapacitet}"
