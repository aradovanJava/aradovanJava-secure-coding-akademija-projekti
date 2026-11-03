"""Lokalna prijava (za aplikacije koje još imaju vlastitu prijavu kao u T2): pwdlib + ograničenje pokušaja.

Uz Keycloak lozinke čuva Keycloak, a aplikacija samo provjerava JWT.
"""

import logging
import threading
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pwdlib import PasswordHash
from pydantic import BaseModel, ConfigDict, Field, SecretStr

from okviri.sigurnost.ogranicenje import ogranicenje_prijave
from okviri.sigurnost.ovlasti import javno

log = logging.getLogger(__name__)

NEISPRAVNA_PRIJAVA = "Neispravno korisničko ime ili lozinka."
# Hash iz T2 (SHA-256 bez soli) – zamjenjuje se Argon2id hashem pri prvoj uspješnoj prijavi.
STARI_HASH_MARKO = "78bc5813d03977dbf07326fae76c9a3e1504f4c20291cf523b6a95d148a904b9"


class LokalniKorisnici:
    def __init__(self, hasher: PasswordHash) -> None:
        self._hasher = hasher
        self._brava = threading.Lock()
        self._lazni_hash = hasher.hash("lazna-lozinka-za-jednako-trajanje")
        self._hashevi = {"ana": hasher.hash("Ana12345!"), "marko": STARI_HASH_MARKO}

    def provjeri(self, username: str, lozinka: str) -> bool:
        hash_lozinke = self._hashevi.get(username)
        if hash_lozinke is None:
            self._hasher.verify(lozinka, self._lazni_hash)  # isto trajanje kao za postojećeg korisnika
            log.warning("Neuspjela prijava za korisnika %s", username)
            return False
        ispravna, novi_hash = self._hasher.verify_and_update(lozinka, hash_lozinke)
        if not ispravna:
            log.warning("Neuspjela prijava za korisnika %s", username)
            return False
        if novi_hash is not None:
            with self._brava:
                self._hashevi[username] = novi_hash
            log.info("Hash lozinke korisnika %s nadograđen na trenutni algoritam", username)
        log.info("Uspješna prijava korisnika %s", username)
        return True

    def hash(self, username: str) -> str | None:
        return self._hashevi.get(username)


class PrijavaZahtjev(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Samo uobičajeni znakovi: u logu nema prijeloma redaka ni kontrolnih znakova iz korisničkog unosa.
    username: str = Field(min_length=1, max_length=100, pattern=r"^[A-Za-z0-9._@-]+$")
    # SecretStr: lozinka se ne ispisuje u repr(), logu ni porukama o greškama.
    password: SecretStr = Field(min_length=1, max_length=200)


router = APIRouter(tags=["prijava"])


def lokalni_korisnici(request: Request) -> LokalniKorisnici:
    return request.app.state.lokalni_korisnici


@router.post("/api/auth/login", dependencies=[Depends(ogranicenje_prijave)])
@javno
def prijava(zahtjev: PrijavaZahtjev, korisnici: Annotated[LokalniKorisnici, Depends(lokalni_korisnici)]) -> dict:
    if not korisnici.provjeri(zahtjev.username, zahtjev.password.get_secret_value()):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, NEISPRAVNA_PRIJAVA)
    # U ovom primjeru tokene izdaje Keycloak; lokalna prijava samo potvrđuje vjerodajnice.
    return {"username": zahtjev.username, "poruka": "Vjerodajnice su ispravne."}
