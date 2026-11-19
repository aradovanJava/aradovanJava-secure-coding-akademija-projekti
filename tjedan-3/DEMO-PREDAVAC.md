# Tjedan 3 – demonstracije na nastavi (SAMO ZA PREDAVAČA, ne ide u pakete)

Paketi za polaznike imaju upute za demonstracije u svojim README-ima (`okviri/README.md` – „Demonstracija”,
`devsecops/README.md` – odjeljak 6, `sigurnost-baza-podataka/README.md` – odjeljci 5 i 6). Ovdje je samo ono što
ovisi o privatnom repozitoriju: kako brzo doći do „ispravljenog” stanja **bez otkrivanja rješenja T2/T3**.

| Dan | Prezentacija | Demonstracija | Bilješke govornika |
|---|---|---|---|
| Dan 1 | P1 – Sigurnost i zaštita programske potpore i DevSecOps | A (okviri, poglavlja 2–5), B (DevSecOps, poglavlje 6) | P1, svaki slajd |
| Dan 2 | P2 – Sigurnost baza podataka | C (baza, poglavlja 2–8) | P2, svaki slajd |
| Dan 3 | P3 – Ispitivanje sigurnosti, rizik i usklađenost (radionica) | D (demo repozitorij za svih pet blokova) + pipeline polaznika na njihovim repozitorijima | P3, svaki slajd |

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

## D. Dan 3 – ispitivanje, rizik i usklađenost (P3, radionica)

Gotov primjer svih pet blokova na MedTerminu (Java): privatni repozitorij
<https://github.com/aradovanJava/t3-dan3-medtermin-demo>, vodič po blokovima u njegovu `docs/README.md`.
Izvor i ponovno stvaranje: `tjedan-3/dan3-demo/` (`pripremi-dan3.sh`, zakrpe, README).

- Blok 1: PR #11 (nadogradnja umjesto općih iznimki), Dependabot PR-ovi, PR #13 (S06 → SCA + Semgrep crveni) i
  PR #14 (S10 → svi alati zeleni, pada samo sigurnosni test).
- Blok 2: plan ispitivanja, `docs/rucni-testovi.http` na lokalnoj aplikaciji (`./mvnw spring-boot:run`), nalaz
  N-01 s PR-om #12 (test crven → popravak zelen) i otvoren nalaz N-02.
- Blokovi 3–5: `docs/dfd.md`, `stride.md`, `registar-rizika.md`, `asvs.md`, `uskladenost.md`.
- **Ne otvarajte** `src/main/` ni diff PR-a #14 (rješenje T2). Dokumenti u `docs/` su riješen primjer za MedTermin –
  pokazujte ih na projektoru, ne dijelite ih polaznicima.

**Python verzija** (za grupe s T2 u Pythonu): <https://github.com/aradovanJava/t3-dan3-medtermin-demo-python>,
izvor i ponovno stvaranje u `tjedan-3/dan3-demo-python/`. Isti blokovi i dokumenti, uz razlike:

- Blok 1: prvo pokretanje zeleno bez ijedne iznimke; lekcija o ovisnostima je R-02 (`requirements.txt` pribija samo
  izravne ovisnosti, tranzitivne bez hasha); 9 Dependabot PR-ova, svi prolaze; PR #11 (S06 → Semgrep + OSV-Scanner +
  pip-audit, Bandit samo informativno) i PR #12 (S10 → pada samo sigurnosni test).
- Blok 2: `python -m medtermin` (port 8000), `pytest -m sigurnost`; N-01 u PR-u #10 (test crven → popravak zelen).
- Blokovi 3–5: STRIDE ima 30 prijetnji (dodatno Swagger UI bez prijave i tranzitivne ovisnosti), ASVS 33 ✅ · 12 ⚠️ ·
  7 ❌ · 18 ➖ (Argon2 umjesto bcrypta: 6.2.8 ✅).
- **Ne otvarajte** `medtermin/` ni diff PR-a #12.

## Provjera prije nastave

CI u ovom repozitoriju provjerava sve demonstracije: `t3-okviri` (skripta `demo_okviri.py` nad Javom, .NET-om i
Pythonom s pravim Keycloakom), `t3-devsecops` (vrata prolaze na `all-secure`, padaju na `all-vuln`) i `t3-baze`
(demo „Aplikacija i baza” u tri tehnologije: prije rješenja ≥ 10 upozorenja, poslije 0, isti ispis u sva tri jezika).
