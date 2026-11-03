"""Pokretanje: python -m okviri  ->  http://localhost:8000 (port mijenja varijabla okruženja PORT)."""

import logging
import os
import sys

import uvicorn
from pydantic import ValidationError

from okviri.postavke import Postavke


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        Postavke()  # provjera postavki i tajni prije pokretanja poslužitelja (fail fast)
    except ValidationError as e:
        polja = ", ".join("OKVIRI_" + str(g["loc"][0]).upper() for g in e.errors() if g.get("loc")) or str(e)
        print(f"Neispravne ili nepotpune postavke ({polja}). Vidi .env.primjer i README.", file=sys.stderr)
        sys.exit(2)
    port = int(os.environ.get("PORT", "8000"))
    # Samo 127.0.0.1 (lokalni razvoj); server_header=False: odgovor ne otkriva poslužitelj i verziju.
    uvicorn.run("okviri.aplikacija:napravi_aplikaciju", factory=True, host="127.0.0.1", port=port, server_header=False)


if __name__ == "__main__":
    main()
