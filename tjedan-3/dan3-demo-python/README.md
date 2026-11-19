# Demo za Dan 3 – MedTermin, Python (SAMO ZA PREDAVAČA, ne ide u pakete)

Praktični projekt uz **P3 – Ispitivanje sigurnosti, rizik i usklađenost**: svih pet blokova radionice na jednom
T2 projektu (MedTermin, Python / FastAPI, referentno rješenje) s DevSecOps predloškom iz T3 paketa. Ista priča kao
Java demo u `../dan3-demo/`, za grupe koje su T2 radile u Pythonu.

- **Repozitorij:** <https://github.com/aradovanJava/t3-dan3-medtermin-demo-python> (privatan)
- **Vodič po blokovima:** `docs/README.md` u tom repozitoriju (uključuje tablicu razlika prema Java demu)

| Blok | U demo repozitoriju |
|---|---|
| 1 Pipeline | prvo pokretanje zeleno **bez ijedne iznimke**; `requirements.txt` pribija samo izravne ovisnosti (R-02); 9 Dependabot PR-ova (#1–#9, svi prolaze); PR #11 i #12 „DOKAZ – ne spajati“ (S06: Semgrep + OSV-Scanner + pip-audit; S10: pada samo test) |
| 2 Ispitivanje | `docs/plan-ispitivanja.md`, `docs/rucni-testovi.http` (port 8000), `tests/sigurnost/` (S01–S04, S09, S10, S12, S13; `pytest -m sigurnost`), nalaz N-01 (PR #10: test crven → popravak zelen) i N-02 (otvoren) |
| 3 Model prijetnji | `docs/dfd.md` + `dfd.png` (izvor `dfd.dot`), `docs/stride.md` (30 prijetnji) |
| 4 Rizik | `docs/registar-rizika.md` (9 rizika, sva četiri postupanja; R-02 nezaključane tranzitivne ovisnosti, R-04 seed računi i Swagger UI) |
| 5 Usklađenost | `docs/asvs.md` (svih 70 L1 + 14 L2 ASVS 5.0.0 s dokazima), `docs/sigurnosna-pravila.md`, `docs/uskladenost.md`, `SECURITY.md` |

Provjereno 19. 11. 2026.: vrata zelena na `main` (60 testova, pokrivenost 89 %), crvena na PR-ovima #11 i #12 te na
prvom commitu PR-a #10.

## Ponovno stvaranje

```bash
tjedan-3/dan3-demo-python/pripremi-dan3.sh /tmp/t3-dan3-demo-python
cd /tmp/t3-dan3-demo-python
git remote add origin https://github.com/<račun>/t3-dan3-medtermin-demo-python.git   # prazan PRIVATAN repozitorij
git push -u origin main nalaz/N-01-istek-sesije dokaz/regresija-s06 dokaz/regresija-s10
```

Skripta generira T2 projekt (`devsecops/test/pripremi.sh python medtermin all-secure`) i na njega primjenjuje
zakrpe iz `zakrpe/` (povijest grane `main`) i `dokaz/` (grane za dokaz pada, odvojene od `main` nakon sigurnosnih
testova). Provjereno: sve četiri grane dobivaju isto stablo kao izvorni repozitorij.

Za crveno → zeleno na N-01 pushajte granu `nalaz/N-01-istek-sesije` prvo samo s testom (commit 0003), otvorite PR,
pa pushajte popravak (0004). Brojevi PR-ova i poveznice na pokretanja u `docs/` odnose se na izvorni repozitorij –
nakon ponovnog stvaranja ih ažurirajte.

Napomene:
- Python verzija nema iznimki s rokom (`ci/prihvaceno.txt` i `osv-scanner.toml` su prazni). Ako se kasnije objavi
  ranjivost u nekoj ovisnosti, vrata na `main` padnu sama – to je dobar trenutak za Dependabot PR uživo.
- Tranzitivne ovisnosti nisu zaključane (namjerno, rizik R-02), pa SBOM i nalazi SCA ovise o danu pokretanja.
- Dependabot otvara PR-ove odmah nakon prvog pusha; provjera „Pregled ovisnosti u PR-u“ je u privatnom
  repozitoriju crvena (traži GitHub Advanced Security) i ne utječe na vrata.
