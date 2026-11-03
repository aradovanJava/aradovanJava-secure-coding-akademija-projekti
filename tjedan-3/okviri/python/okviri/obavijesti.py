"""Simulacija klijenta vanjskog servisa za obavijesti (u stvarnosti HTTP poziv sa zaglavljem X-Api-Key).

API ključ je TAJNA iz postavki (SecretStr): koristi se, ali se nikad ne ispisuje u log.
"""

import logging
import threading
from urllib.parse import urlsplit

from pydantic import SecretStr

log = logging.getLogger(__name__)


class ObavijestiKlijent:
    def __init__(self, adresa: str, api_kljuc: SecretStr) -> None:
        self._adresa = adresa
        self._api_kljuc = api_kljuc
        self._brava = threading.Lock()
        self.poslano = 0

    def otkazano(self, rezervacija_id: int) -> None:
        _zaglavlja = {"X-Api-Key": self._api_kljuc.get_secret_value()}  # ide samo prema servisu
        with self._brava:
            self.poslano += 1
        log.info(
            "Obavijest o otkazivanju rezervacije %s poslana na %s", rezervacija_id, urlsplit(self._adresa).hostname
        )
