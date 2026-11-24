# Knjižnica – aplikacija za završnu demonstraciju

Ovo je **namjerno ranjiva** aplikacija gradske knjižnice (katalog, članovi i posudbe). Na njoj predavač u Tjednu 4
pokazuje cijeli postupak: alat pronađe nalaz, analizira se uzrok, ranjivost se ispravi, a jedinični test dokaže da
je ispravak uspio i da se greška neće vratiti.

> **Upozorenje:** aplikaciju pokrećite samo lokalno (localhost) i nikad je ne izlažite mreži.

Ista aplikacija postoji u tri tehnologije – odaberite onu u kojoj ste radili projekt:

| Mapa | Tehnologija | Port | Pokretanje |
|---|---|---|---|
| `java/` | Java 21, Spring Boot 3.5, Maven | 8080 | `./mvnw spring-boot:run` |
| `dotnet/` | C#, .NET 10, ASP.NET Core | 5080 | `dotnet run --project src/Knjiznica.Api` |
| `python/` | Python 3.12+, FastAPI | 8000 | `python run.py` |

Detalji za IDE (IntelliJ IDEA, Visual Studio, Rider, VS Code, PyCharm) su u datoteci `KAKO-POKRENUTI.md` u svakoj
mapi. Gotovi zahtjevi su u `http/knjiznica.http` (JetBrains HTTP Client) i `http/knjiznica-vs.http` (Visual Studio,
VS Code s proširenjem REST Client).

## Korisnici

| Korisničko ime | Lozinka | Uloga | Članarina |
|---|---|---|---|
| ana | Ana123! | član | aktivna |
| marko | Marko123! | član | istekla |
| iva | Iva123! | član | suspendirana |
| knjiznicar | Knjiga123! | knjižničar | aktivna |

## API

| Metoda i putanja | Opis | Prijava |
|---|---|---|
| `POST /api/prijava` | prijava, vraća token | ne |
| `POST /api/registracija` | registracija novog člana | ne |
| `GET /api/knjige?trazi=...` | pretraga kataloga | ne |
| `GET /api/knjige/{id}` | podaci o knjizi | ne |
| `GET /api/clanovi/{id}` | profil člana | da |
| `POST /api/katalog/uvoz` | uvoz kataloga u YAML formatu | knjižničar |
| `GET /api/posudbe` | moje posudbe | da |
| `POST /api/posudbe` | nova posudba `{"knjigaId": 5}` | da |
| `POST /api/posudbe/{id}/produzi` | produljenje roka `{"dana": 7}` | da |

Token se šalje u zaglavlju `Authorization: Bearer <token>`.

## Što pokušati sami

Pokrenite alate iz Tjedna 1 i 3 (Semgrep, SpotBugs, Roslyn analizatore ili Bandit, OSV-Scanner, OWASP ZAP) i
usporedite nalaze s onim što predavač pokazuje. Neke ranjivosti alati ne vide – za njih trebate test.
