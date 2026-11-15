# Tjedan 3 – demonstracije na nastavi (SAMO ZA PREDAVAČA, ne ide u pakete)

Paketi za polaznike imaju upute za demonstracije u svojim README-ima (`okviri/README.md` – „Demonstracija”,
`devsecops/README.md` – odjeljak 6, `sigurnost-baza-podataka/README.md` – odjeljci 5 i 6). Ovdje je samo ono što
ovisi o privatnom repozitoriju: kako brzo doći do „ispravljenog” stanja **bez otkrivanja rješenja T2/T3**.

| Dan | Prezentacija | Demonstracija | Bilješke govornika |
|---|---|---|---|
| Dan 1 | P1 – Sigurnost i zaštita programske potpore i DevSecOps | A (okviri, poglavlja 2–5), B (DevSecOps, poglavlje 6) | P1, svaki slajd |
| Dan 2 | P2 – Sigurnost baza podataka | C (baza, poglavlja 2–8) | P2, svaki slajd |
| Dan 3 | radionica: ispitivanje sigurnosti, rizik i usklađenost | pipeline polaznika na njihovim repozitorijima | – |

## A. Mehanizmi okvira (~20 min, P1 poglavlja 2–5)

Sve je u paketu – vidi `okviri/README.md`. Kratko:

```bash
cd tjedan-3/okviri/keycloak && docker compose up -d                  # ~30 s
cd ../python && .venv/bin/python -m okviri                            # ili java / dotnet
python3 ../demo/demo_okviri.py python                                 # Enter između koraka
```

Ako mreža u dvorani nije pouzdana: sve pokrenite i jednom prođite skriptu **prije** nastave (slike i ovisnosti su tada
lokalno). Rezervni plan bez Dockera: `python3 demo/demo_okviri.py --url http://localhost:8000 --bez-keycloaka`
(koraci 1, 2, 8 i 9) i testovi (`pytest -v`) za korake 3–7.

## B. DevSecOps (~25 min, P1 poglavlje 6)

Repozitorij za demonstraciju generira se iz predložaka (isto kao CI `t3-devsecops`):

```bash
tjedan-3/devsecops/test/pripremi.sh python medtermin all-secure /tmp/t3-demo     # ili java / dotnet
cd /tmp/t3-demo
gh repo create aradovanJava/t3-devsecops-demo --private --source . --push
```

- Repozitorij neka bude **privatan** i na nastavi **ne otvarajte izvorni kod** – `all-secure` je referentno rješenje svih
  13 propusta MedTermina (V01–V03 rade na MedTerminu). Pokazujte samo Actions, Summary, artefakte i diff regresije.
- `pripremi.sh` dodaje i iznimke iz `devsecops/test/prihvaceno-<stack>-medtermin.txt` (bez njih Java i .NET vrata ne
  prolaze zbog nalaza na referentnom popravku – vidi `devsecops/README.md`, odjeljak 5). Python prolazi bez iznimaka.
- Prvo pokretanje pustite dan prije (obično 3–10 minuta). Na nastavi: `git switch -c demo/regresija`, promjena iz
  `devsecops/README.md` §6.3 (npr. `PyYAML==5.3.1`), push, PR → crvena vrata za nekoliko minuta.
- Nakon nastave: zatvorite PR, po želji `gh repo delete aradovanJava/t3-devsecops-demo`.

## C. Baza (~25 min, P2)

Koraci 1–5 i 7 iz `sigurnost-baza-podataka/README.md` §6 rade se na paketu. Za korak 6 (ciljano stanje) primijenite
referentno rješenje iz `tjedan-3/baze/rjesenje/` – **samo izlaz, ne skriptu** (to je rješenje zadataka Z2–Z8):

```bash
cd tjedan-3/baze            # ili raspakirani paket + kopija rjesenje/<domena>.sql
docker compose cp rjesenje/medtermin.sql sql:/tmp/rjesenje.sql
docker compose exec -T -e SQLCMDPASSWORD='<sa lozinka>' sql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa \
  -b -I -f 65001 -i /tmp/rjesenje.sql -v APP_LOZINKA='<nova lozinka aplikacije>' ADMIN_LOZINKA='<lozinka dba_admin>' \
  KLJUC_LOZINKA='<lozinka za ključeve>'
# .env: ADMIN_LOGIN=dba_admin, ADMIN_PASSWORD=<lozinka dba_admin>, APP_LOZINKA=<nova lozinka aplikacije>
docker compose up -d
docker compose --profile provjera run --rm provjera                  # sve PROŠLO
docker compose --profile aplikacija run --rm aplikacija-python       # Upozorenja: 0
```

Na kraju `docker compose down -v` i pražnjenje `backup/` i `audit/` (rješenje je stvorilo certifikate i kopije).

## Provjera prije nastave

CI u ovom repozitoriju provjerava sve demonstracije: `t3-okviri` (skripta `demo_okviri.py` nad Javom, .NET-om i
Pythonom s pravim Keycloakom), `t3-devsecops` (vrata prolaze na `all-secure`, padaju na `all-vuln`) i `t3-baze`
(demo „Aplikacija i baza” u tri tehnologije: prije rješenja ≥ 10 upozorenja, poslije 0, isti ispis u sva tri jezika).
