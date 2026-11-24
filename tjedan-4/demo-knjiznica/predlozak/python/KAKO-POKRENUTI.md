# Knjižnica (Python) – kako pokrenuti

FastAPI aplikacija sa SQLite bazom u memoriji. Podaci se pri svakom pokretanju vraćaju na početno stanje
(korisnici i knjige iz `PROCITAJ-ME.md`). Aplikacija sluša samo na `http://localhost:8000`, a interaktivna
dokumentacija API-ja je na `http://localhost:8000/docs`.

## Preduvjeti

- **Python 3.12 ili noviji**. Provjera: `python --version` (na Linuxu i macOS-u često `python3`).
- IDE po izboru: PyCharm ili VS Code s proširenjem *Python*.

## Virtualno okruženje i ovisnosti

```bash
python -m venv .venv
source .venv/bin/activate          # Windows (PowerShell): .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## PyCharm

1. **File → Open…** i odaberite ovu mapu.
2. **Settings → Project → Python Interpreter → Add Interpreter → Add Local Interpreter → Existing** i odaberite
   `.venv` (ili ga PyCharm ponudi sam).
3. Desni klik na `run.py` → **Run 'run'**. U konzoli treba pisati `Uvicorn running on http://127.0.0.1:8000`.
4. Testovi: desni klik na mapu `tests` → **Run 'pytest in tests'**.

## VS Code

1. **File → Open Folder…** i odaberite ovu mapu.
2. **Ctrl+Shift+P → Python: Select Interpreter** i odaberite `.venv`.
3. Otvorite `run.py` i kliknite **Run Python File** (trokut gore desno).
4. Testovi: ikona epruvete (Testing) → **Configure Python Tests → pytest → tests**.

## Naredbeni redak

```bash
python run.py                      # http://localhost:8000
pytest                             # svi testovi
pytest -m funkcionalni             # samo funkcionalni testovi
```

## Slanje zahtjeva

Najjednostavnije je kroz `http://localhost:8000/docs`: pošaljite `POST /api/prijava`, kopirajte token, kliknite
**Authorize** i upišite ga. Isti zahtjevi su i u mapi `http/`:

| Datoteka | Alat |
|---|---|
| `http/knjiznica.http` | HTTP Client u PyCharm Professional (studentska licenca je besplatna) |
| `http/knjiznica-vs.http` | VS Code s proširenjem *REST Client* |

Prvo pošaljite četiri zahtjeva iz sekcije **Prijava** – token se sprema i automatski koristi u ostalim zahtjevima.

## Alati iz Tjedna 1 i 3

```bash
semgrep scan --config p/python --exclude tests .
bandit -r knjiznica
pip-audit -r requirements.txt
osv-scanner scan source -r .
docker run --rm --network host zaproxy/zap-stable zap-baseline.py -t http://localhost:8000/api/knjige -I
```

Bandit i pip-audit instalirani su s `requirements-dev.txt`. Na Windowsu i macOS-u Docker ne podržava
`--network host`; tamo umjesto `localhost` u ZAP naredbi upišite `host.docker.internal`.

## Česti problemi

- **Port 8000 je zauzet:** `uvicorn knjiznica.main:app --port 8001` i u `.http` datoteci promijenite `@host`.
- **Instalacija paketa ne uspijeva:** prvo `python -m pip install --upgrade pip setuptools wheel`, zatim ponovite
  `pip install -r requirements-dev.txt`. Ako i dalje ne ide, koristite Python 3.12.
- **`ModuleNotFoundError: No module named 'knjiznica'`:** naredbe pokrećite iz ove mape (u kojoj je `run.py`).
