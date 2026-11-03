"""S11 – predvidljiv i višekratni token za promjenu lozinke."""

import hashlib
import re
from datetime import date

from .conftest import sk_login, sk_registracija

TOKEN = re.compile(r"Token:\s*(\S+)")


def _zatrazi(klijent, username):
    odgovor = klijent.post("/api/auth/reset-zahtjev", json={"username": username})
    assert odgovor.status_code == 202


def _reset(klijent, token, nova):
    return klijent.post("/api/auth/reset", json={"token": token, "novaLozinka": nova})


def _token_iz_poste(sk_mape, username):
    poruke = sorted(sk_mape.posta.glob(f"{username}-*.txt"))
    assert poruke, f"poruka za {username} u mailbox_dir"
    pogodak = TOKEN.search(poruke[-1].read_text(encoding="utf-8"))
    assert pogodak, "redak 'Token:' u poruci"
    return pogodak.group(1)


def test_s11_token_md5_korisnik_i_datum_ne_vrijedi(sk_client):
    _zatrazi(sk_client, "ana")
    pogodeni = hashlib.md5(("ana" + date.today().isoformat()).encode("utf-8")).hexdigest()  # noqa: S324
    odgovor = _reset(sk_client, pogodeni, "Preuzeta12345!")
    assert odgovor.status_code == 400, "reset pogođenim tokenom je uspio"
    assert sk_login(sk_client, "ana").status_code == 200, "ana se ne može prijaviti starom lozinkom"


def test_s11_token_iz_poruke_vrijedi_samo_jednom(sk_client, sk_mape):
    username = sk_registracija(sk_client, "reset", "Pocetna12345!")
    _zatrazi(sk_client, username)
    token = _token_iz_poste(sk_mape, username)
    prvi = _reset(sk_client, token, "Nova12345!")
    drugi = _reset(sk_client, token, "Druga12345!")
    assert prvi.status_code == 200, "prvi reset legitimnim tokenom"
    assert drugi.status_code == 400, "drugi reset istim tokenom"
    assert sk_login(sk_client, username, "Nova12345!").status_code == 200

