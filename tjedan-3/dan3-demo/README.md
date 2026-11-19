# Demo za Dan 3 – MedTermin, Java (SAMO ZA PREDAVAČA, ne ide u pakete)

Praktični projekt uz **P3 – Ispitivanje sigurnosti, rizik i usklađenost**: svih pet blokova radionice na jednom
T2 projektu (MedTermin, Java, referentno rješenje) s DevSecOps predloškom iz T3 paketa.

- **Repozitorij:** <https://github.com/aradovanJava/t3-dan3-medtermin-demo> (privatan)
- **Vodič po blokovima:** `docs/README.md` u tom repozitoriju

| Blok | U demo repozitoriju |
|---|---|
| 1 Pipeline | PR #11 (opće iznimke → Spring Boot 3.5.16 + Tomcat 10.1.61 + iznimke s rokom), Dependabot PR-ovi (ne prolaze #4 Boot 4.1 – Jackson 3 i #8 SpotBugs 4.10 – novi nalaz), PR #13 i #14 „DOKAZ – ne spajati“ (S06: SCA + Semgrep; S10: pada samo test) |
| 2 Ispitivanje | `docs/plan-ispitivanja.md`, `docs/rucni-testovi.http`, sigurnosni testovi S01–S04, S09, S10, S12, S13, nalaz N-01 (PR #12: test crven → popravak zelen) i N-02 (otvoren) |
| 3 Model prijetnji | `docs/dfd.md` + `dfd.png` (izvor `dfd.dot`), `docs/stride.md` (29 prijetnji) |
| 4 Rizik | `docs/registar-rizika.md` (9 rizika, sva četiri postupanja) |
| 5 Usklađenost | `docs/asvs.md` (svih 70 L1 + 13 L2 ASVS 5.0.0 s dokazima), `docs/sigurnosna-pravila.md`, `docs/uskladenost.md`, `SECURITY.md` |

Provjereno 18. 11. 2026.: vrata zelena na `main` (60 testova, pokrivenost 90,2 %), crvena na PR-ovima #13 i #14 te na
prvom commitu PR-a #12.

## Upute za predavača (Word)

`vodic/T3-Dan3-demo-upute-za-predavaca.docx` – detaljne upute po blokovima (na što kliknuti, što se vidi, što reći,
pitanja s očekivanim odgovorima, priprema i rješavanje problema). Gradi se s
`node vodic/napravi_vodic_dan3.js vodic/T3-Dan3-demo-upute-za-predavaca.docx` (npm paket `docx`; slika `dfd.png` iz
demo repozitorija mora biti u mapi `vodic/`).

## Ponovno stvaranje

```bash
tjedan-3/dan3-demo/pripremi-dan3.sh /tmp/t3-dan3-demo
cd /tmp/t3-dan3-demo
git remote add origin https://github.com/<račun>/t3-dan3-medtermin-demo.git   # prazan PRIVATAN repozitorij
git push -u origin main nalaz/N-01-istek-sesije dokaz/regresija-s06 dokaz/regresija-s10
```

Skripta generira T2 projekt (`devsecops/test/pripremi.sh java medtermin all-secure`) i na njega primjenjuje
zakrpe iz `zakrpe/` (povijest grane `main`) i `dokaz/` (grane za dokaz pada). Za crveno → zeleno na N-01
pushajte granu `nalaz/N-01-istek-sesije` prvo samo s testom (commit 0006), otvorite PR, pa pushajte popravak.
Brojevi PR-ova i poveznice na pokretanja u `docs/` odnose se na izvorni repozitorij – nakon ponovnog stvaranja
ih ažurirajte.

Napomene:
- `osv-scanner.toml` ima iznimke do **31. 1. 2027.** – nakon toga vrata na `main` padaju (namjerno, rizik R-02).
- Dependabot otvara PR-ove odmah nakon prvog pusha; provjera „Pregled ovisnosti u PR-u“ je u privatnom
  repozitoriju crvena (traži GitHub Advanced Security) i ne utječe na vrata.
