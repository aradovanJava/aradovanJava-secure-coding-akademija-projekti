# Završni ispit – Moodle kvizovi (Tjedan 4, četvrtak 26. 11. 2026.)

SAMO ZA PREDAVAČA – ne objavljivati polaznicima (sadrži točne odgovore).

| Kviz | Termin | Pitanja | Vrijeme | Prolaz |
|---|---|---|---|---|
| Probni ispit – Java / .NET / Python | 16:30–17:15 | 12 općih + 13 iz tehnologije | bez ograničenja unutar termina | – (vježba, neograničeni pokušaji) |
| Završni ispit – Java / .NET / Python | 17:30–19:00 | 25 općih + 25 iz tehnologije | 90 min | 50 % |

- `pitanja_opca.py` – pitanja neovisna o tehnologiji (OWASP Top 10:2025, STRIDE, DevSecOps, baza, rizik, ASVS,
  GDPR, NIS2/ZKS, CRA, demonstracija i vježba „Prva 72 sata”), zajednička za sva tri ispita.
- `pitanja_java.py`, `pitanja_dotnet.py`, `pitanja_python.py` – pitanja samo iz te tehnologije.
- `python3 generiraj_kviz.py` – provjera (4 odgovora, 1 točan, točan odgovor najdulji u najviše 30 % pitanja,
  nema pojmova iz druge tehnologije) i izrada `dist/`:
  - `ZI-sva-pitanja.xml` – sve kategorije jednim uvozom (Moodle XML), kategorije
    `Završni ispit/<skup> – probni ispit|završni ispit`,
  - `ZI-<skup>-probni.xml`, `ZI-<skup>-ispit.xml` – po kategoriji,
  - `kljuc-odgovora.md` – ključ za predavača.

Svaki odgovor ima povratnu informaciju (zašto je točan ili netočan), a opća povratna informacija pitanja navodi
točan odgovor, obrazloženje, zašto ostali nisu točni i gdje je gradivo. U kvizu je pregled postavljen
„odmah nakon pokušaja”, pa polaznici sve to vide čim predaju.
