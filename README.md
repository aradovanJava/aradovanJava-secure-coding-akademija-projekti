# Secure Coding akademija – Tjedan 2: samostalni projekti (PRIVATNO – samo za nastavnike)

Ovaj repozitorij sadrži predloške projekata za **15 varijanti** (3 domene; svaka u Javi, .NET-u i Pythonu), **skrivene testove** za
ocjenjivanje, savjete i alate. Polaznici ga **ne smiju vidjeti** – svaki dobiva samo ZIP svoje varijante na Moodleu.

| Mapa / datoteka | Sadržaj |
|---|---|
| `SPEC_T2.md` | specifikacija: domene, 13 ranjivih mjesta (S01–S13), skriveni testovi |
| `variants.json` | raspodjela V01–V15: domena + 9 ranjivih mjesta |
| `templates/<java\|dotnet\|python>/<domena>/` | predlošci s markerima `@@VULN` / `@@SECURE` |
| `hidden-tests/<java\|dotnet\|python>/<domena>/` | skriveni testovi (po jedan ili više po mjestu) |
| `student-docs/` | upute i predlošci koji ulaze u ZIP polaznika (README, alati, izvještaj, STRIDE, ASVS) |
| `tools/generate.py` | generiranje varijanti i ZIP paketa za polaznike |
| `tools/ocijeni.py` | ocjenjivanje predaje skrivenim testovima |
| `tools/savjeti.py` | savjeti (razina 1 i 2) po varijanti za Moodle |
| `.github/workflows/` | `dev` (provjera predložaka), `verify` (svih 15 varijanti), `ocijeni` (ocjenjivanje u CI-ju) |

## Raspodjela ranjivosti po varijantama (● = ranjivo)

| Varijanta | Domena | S01 | S02 | S03 | S04 | S05 | S06 | S07 | S08 | S09 | S10 | S11 | S12 | S13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V01 | medtermin | · | ● | ● | ● | · | ● | ● | ● | · | · | ● | ● | ● |
| V02 | medtermin | ● | · | · | ● | · | ● | ● | ● | ● | · | ● | ● | ● |
| V03 | medtermin | ● | · | ● | · | ● | ● | ● | · | ● | ● | ● | · | ● |
| V04 | medtermin | ● | ● | ● | · | ● | ● | ● | · | ● | ● | · | ● | · |
| V05 | medtermin | · | ● | · | ● | ● | ● | ● | ● | · | ● | ● | ● | · |
| V06 | ulaznica | ● | · | · | ● | ● | ● | ● | · | ● | ● | ● | · | ● |
| V07 | ulaznica | ● | ● | ● | · | ● | ● | ● | · | ● | ● | · | ● | · |
| V08 | ulaznica | ● | · | ● | ● | · | · | ● | ● | · | ● | ● | ● | ● |
| V09 | ulaznica | · | ● | · | · | ● | ● | · | ● | ● | ● | ● | ● | ● |
| V10 | ulaznica | · | ● | ● | ● | · | ● | · | ● | · | ● | ● | ● | ● |
| V11 | kadrovska | ● | · | ● | ● | · | ● | · | ● | · | ● | ● | ● | ● |
| V12 | kadrovska | · | ● | · | · | ● | · | ● | ● | ● | ● | ● | ● | ● |
| V13 | kadrovska | ● | ● | ● | · | ● | · | ● | ● | · | ● | · | ● | ● |
| V14 | kadrovska | · | · | ● | ● | ● | ● | ● | · | ● | · | ● | ● | ● |
| V15 | kadrovska | ● | ● | · | ● | · | ● | ● | · | ● | ● | ● | · | ● |

- **S01** – IDOR (brisanje)
- **S02** – Path traversal
- **S03** – Open redirect
- **S04** – CORS
- **S05** – XXE
- **S06** – Ranjiva YAML biblioteka
- **S07** – Lozinke SHA-256
- **S08** – SQLi u sortiranju
- **S09** – Pohranjeni XSS
- **S10** – Race condition
- **S11** – Reset token
- **S12** – Logiranje
- **S13** – Fail-open

Domene: **medtermin** (V01–V05, naručivanje pregleda), **ulaznica** (V06–V10, prodaja ulaznica),
**kadrovska** (V11–V15, HR portal). Svaka varijanta ima 9 ranjivih i 4 ispravno napisana mjesta.

Polaznik u ZIP-u svoje varijante dobiva sve tri tehnologije (`java/`, `dotnet/`, `python/`) i odabire jednu:
Spring Boot 3.5 (Java 21), ASP.NET Core (.NET 10) ili FastAPI (Python 3.12+). Ranjiva mjesta su ista u sve tri.

## 1. Paketi za polaznike

```bash
python3 tools/generate.py --student all --out dist/      # dist/projekt-V01-medtermin.zip … V15
python3 tools/savjeti.py --out dist/savjeti              # Vxx-razina-1.html, Vxx-razina-2.html
```
Generator nakon svake varijante provjerava da kod ne sadrži tragove ranjivosti (riječi poput „ranjivo”, oznake
slotova, CWE…) – ako ih nađe, prekida se.

## 2. Moodle (sekcija „Tjedan 2”)

- grupe **Projekt V01 … Projekt V15** (vidljivost: samo vlastito članstvo) – **svakog polaznika stavi u točno
  jednu grupu** (Sudionici → Grupe), npr. nasumično ili po želji polaznika za domenu;
- ZIP varijante i dvije stranice sa savjetima vidljivi su samo članovima odgovarajuće grupe;
- **Predaja projekta – Tjedan 2** (zadaća, rok 15. 11. 2026. 23:59, ocjenjivanje rubrikom iz programa);
- **Kviz – Tjedan 2** (15 nasumičnih od 28 pitanja s isječcima koda), forum, upute i Word predlošci.

Korištenje savjeta vidi se u *Izvještaji → Zapisnici* (događaj „Pregled modula stranice”) ili u izvještaju aktivnosti.

## 3. Ocjenjivanje

**U GitHub Actions (bez lokalne instalacije):** ZIP predaje stavi u `predaje/`, commit + push, zatim
*Actions → ocijeni → Run workflow* (naziv datoteke ili `*` za sve). Izvještaj je u sažetku pokretanja i u artefaktu.

**Lokalno** (Python 3.9+ za alate; za predaje: JDK 21, .NET 10 SDK odnosno Python 3.12+):
```bash
python3 tools/ocijeni.py --predaja predaje/V07-Ime-Prezime.zip
```
Izvještaj sadrži: koje su od 9 ranjivosti ispravljene (skriveni testovi), jesu li sigurna mjesta ostala sigurna,
prolaze li funkcionalni testovi, koliko testova polaznika pada na izvornom kodu i prolazi na predaji
(crveno → zeleno), pokrivenost koda i prijedlog razina za rubriku. Razinu samostalnosti korigiraj prema korištenju
savjeta; usklađenost (ASVS, STRIDE) i izvještaj ocjenjuješ ručno.

## 4. Provjera svih varijanti

*Actions → verify → Run workflow* – za svaku od 15 varijanti u sva tri stacka (Java, .NET, Python) provjerava da skriveni testovi padaju
točno za ranjiva mjesta, a funkcionalni testovi prolaze. Pokreni nakon svake izmjene predložaka.
