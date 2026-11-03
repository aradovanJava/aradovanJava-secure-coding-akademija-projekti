# FastAPI mehanizmi umjesto ručnih provjera (Python 3.12+)

Pokretanje: `docker compose up -d` u `../keycloak`, zatim (jednom) okruženje i tajna pa aplikacija:

```bash
python -m venv .venv
source .venv/bin/activate              # Windows (PowerShell): .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
cp .env.primjer .env                   # Windows: copy .env.primjer .env – zatim u .env upišite OKVIRI_OBAVIJESTI_API_KLJUC
python -m okviri                       # http://localhost:8000 (PyCharm/VS Code: run.py)
```

Testovi: `pytest` – **ne trebaju Keycloak** (RSA ključ se generira u testu, JWKS je u memoriji).
Statička analiza: `ruff check .` i `bandit -c pyproject.toml -r okviri`.

## Prije (ručna provjera u T2) → poslije (mehanizam okvira)

| Tema (T2) | Prije: ručno | Poslije: FastAPI i provjerene biblioteke | Gdje |
|---|---|---|---|
| Prijava i tokeni | `TokenStore` (nasumični token u mapi), `token_iz_zahtjeva()` čita zaglavlje ili kolačić `SESSION` | **JWT od Keycloaka** (PyJWT): potpis preko JWKS-a (`jwt.PyJWKClient`), `algorithms=["RS256"]` zadan u kodu, `exp`, `iss` i `aud` obavezni | `sigurnost/tokeni.py`, `postavke.py` |
| Tko je prijavljen | `Prijavljeni` iz vlastite mape tokena | `PrijavljeniKorisnik`: `username` = `preferred_username`, uloge iz `realm_access.roles` (kao `KeycloakJwtKonverter` / `KeycloakUloge`) | `sigurnost/tokeni.py`, `sigurnost/ovlasti.py` |
| Zaštićene putanje | ruta je zaštićena samo ako netko ne zaboravi parametar `Prijavljeni` | **globalna ovisnost** `FastAPI(dependencies=[Depends(zadano_zabranjeno)])`: svaka ruta traži token, osim izričito označenih s `@javno` (zadano zabranjeno) | `aplikacija.py`, `sigurnost/ovlasti.py` |
| Vlasništvo (IDOR, S01) | `if rezervacija["pacijent"] != korisnik.username` u servisu | ponovno upotrebljiva ovisnost `Vlasnistvo(...)` → tip parametra `VlastitaRezervacija`; tuđa ili nepostojeća → 404, u ruti nema `if`-a za ovlasti | `sigurnost/ovlasti.py`, `rezervacije.py` |
| Uloge | `if korisnik.is_admin` | `Security(prijavljeni_korisnik, scopes=["ADMIN"])` na **routeru** `/api/admin` (vrijedi i za svaku novu rutu pod tim prefiksom) | `rezervacije.py` |
| CORS (S04) | vlastiti `CorsMiddleware` koji vraća `Origin` iz zahtjeva | Starletteov `CORSMiddleware` s popisom `OKVIRI_CORS_DOPUSTENI_ORIGINI` (točni origini; `*` odbijen pri pokretanju), bez kolačića | `aplikacija.py`, `postavke.py` |
| Sigurnosna zaglavlja (S09) | CSP samo na stranici za ispis | čisti ASGI middleware za **svaki** odgovor: CSP, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Cache-Control`; HSTS iza HTTPS-a; `TrustedHostMiddleware`; uvicorn bez zaglavlja `server` | `sigurnost/zaglavlja.py`, `aplikacija.py`, `__main__.py` |
| Lozinke (S07) | `hashlib.sha256(lozinka)` ili `argon2.PasswordHasher` bez nadogradnje starih hasheva | **pwdlib** `PasswordHash((Argon2Hasher(), BcryptHasher(), StariSha256()))`: novi hashevi Argon2id, stari (bcrypt, SHA-256 iz T2) se provjere i **automatski nadograde** pri prijavi (`verify_and_update`) | `sigurnost/lozinke.py`, `prijava.py` |
| Pogađanje lozinki | ništa | **limits** (fixed window) kao ovisnost rute prijave: N pokušaja/min po IP → `429` + `Retry-After` | `sigurnost/ogranicenje.py`, `prijava.py` |
| Tajne | u kodu ili u `postavke.py` sa zadanom vrijednošću | **pydantic-settings**: varijable okruženja / `.env` (u `.gitignore`), `SecretStr` (ne ispisuje se), bez zadane vrijednosti → aplikacija se ne pokreće bez tajne | `postavke.py`, `obavijesti.py`, `.env.primjer` |
| Greške 401/403/422/500 | `ApiGreska` po rutama | rukovatelji iznimkama: `{ "greska": "..." }`, 401 s `WWW-Authenticate: Bearer`, neispravan zahtjev → 400 **bez unesenih vrijednosti** (zadani 422 FastAPI-ja vraća i lozinku iz tijela!), 500 bez stack tracea; `debug=False`, Swagger UI samo lokalno | `sigurnost/greske.py`, `aplikacija.py` |
| Zapisivanje (S12) | – | neuspjela prijava `WARNING` s korisničkim imenom, bez lozinke (`SecretStr`); `username` dopušta samo `[A-Za-z0-9._@-]` (nema lažnih redaka u logu) | `prijava.py` |

**CSRF** zaštita nije potrebna jer je API *stateless*, a token je u zaglavlju `Authorization` (preglednik ga ne
šalje sam). Ako vaš T2 projekt zadrži kolačić `SESSION` (obrazac `/prijava`), dodajte CSRF token (npr. *double
submit* kolačić ili `starlette-csrf`) i provjeru zaglavlja `Origin` za svaki POST/DELETE.

**Zašto `limits`, a ne `slowapi`?** `slowapi` je omotač iste biblioteke `limits` (iz Flask-Limitera) s dekoratorom
koji traži parametar `request` u svakoj ruti i `app.state.limiter`. Ovdje je `limits` izravno jedna FastAPI
ovisnost (`dependencies=[Depends(ogranicenje_prijave)]`) – isti algoritam i spremišta (memorija, Redis), manje
„magije”, a odgovor 429 je u istom JSON formatu kao ostale greške. Brojači su u memoriji jednog procesa; za više
instanci: `storage_from_string("redis://…")` ili ograničenje na API gatewayu. Iza reverse proxyja pokrenite uvicorn
s `--forwarded-allow-ips`, inače su svi klijenti „ista IP adresa”.

## Testovi (pytest + `TestClient`)

`tests/conftest.py` generira RSA ključ, potpisuje tokene kakve izdaje Keycloak (`iss`, `aud`, `preferred_username`,
`realm_access.roles`) i zamjenjuje **samo izvor javnih ključeva**: `app.dependency_overrides[izvor_kljuceva]`
(FastAPI mehanizam za testove). Provjera potpisa, claimova, uloga i vlasništva radi istim kodom kao u produkciji.

- `test_sigurnost_api.py` – 401 bez tokena, samo vlastite, 404 za tuđu/nepostojeću, ADMIN smije sve, 403 za ADMIN
  popis, **zadano zabranjeno za svaku rutu iz OpenAPI sheme** (i za rutu dodanu naknadno), zaglavlja, CORS, Host, 500 bez detalja.
- `test_tokeni.py` – krivi ključ, izmijenjen sadržaj, istekao token, drugi `iss`/`aud`, nepoznat `kid`, `alg: none`
  i HS256 potpisan javnim ključem (zamjena algoritma) → 401; mapiranje `preferred_username` i `realm_access.roles`.
- `test_lozinke_i_prijava.py` – Argon2id sa solju, nadogradnja bcrypt i SHA-256 hasha pri prijavi, isti odgovor za
  krivu lozinku i nepostojećeg korisnika, log bez lozinke i API ključa, 400 bez unesene lozinke.
- `test_ogranicenje_prijave.py` – 429 + `Retry-After` nakon N pokušaja. `test_postavke.py` – bez tajne nema
  pokretanja, `*` u CORS-u i `http://` issuer izvan razvoja su odbijeni.

## Kako to prenijeti u svoj T2 projekt

1. `pip install "pyjwt[crypto]"` (ako prelazite na Keycloak) ili zadržite vlastitu prijavu, ali s `pwdlib` i `limits`.
2. Dodajte globalnu ovisnost `zadano_zabranjeno` i označite javne rute s `@javno`; ručne provjere prijave obrišite
   tek kad testovi prolaze.
3. Provjere vlasništva premjestite u ovisnost (`Vlasnistvo(...)`); u ruti ne smije ostati `if` za ovlasti.
4. Vlastiti CORS middleware zamijenite Starletteovim `CORSMiddleware` s popisom origina iz konfiguracije; tajne u
   `.env` / varijable okruženja (`pydantic-settings`, `SecretStr`).
5. Pokrenite T2 testove (`pytest`) i DevSecOps cjevovod (`../../devsecops`).
