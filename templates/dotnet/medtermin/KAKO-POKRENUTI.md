# MedTermin (.NET 10) – kako pokrenuti

## Preduvjeti

- .NET SDK 10.0 (`dotnet --version`)
- Visual Studio 2026, JetBrains Rider ili VS Code s ekstenzijom C# Dev Kit

## Pokretanje

```bash
dotnet run --project src/MedTermin.Api
```

Aplikacija radi na <http://localhost:5080> (profil `http` u `src/MedTermin.Api/Properties/launchSettings.json`).

- Početna stranica: <http://localhost:5080/>
- Web prijava: <http://localhost:5080/prijava>
- Provjera rada: <http://localhost:5080/api/health>

U Visual Studiju otvori `MedTermin.sln`, za početni projekt odaberi `MedTermin.Api` i profil `http`.
U VS Codeu koristi *Run and Debug* (konfiguracija iz `.vscode/launch.json`).

Baza je SQLite u memoriji – pri svakom pokretanju stvara se iznova s početnim podacima. Dokumenti (nalazi) i
„poslane” e-poruke spremaju se u `src/MedTermin.Api/data/dokumenti/` i `src/MedTermin.Api/data/posta/`
(ključevi `App:StorageDir` i `App:MailboxDir` u `appsettings.json`).

## Korisnici

| Korisničko ime | Lozinka | Uloga |
|---|---|---|
| `ana` | `Ana12345!` | KORISNIK (pacijent) |
| `marko` | `Marko12345!` | KORISNIK (pacijent) |
| `dr.horvat` | `Ovlasteni12345!` | LIJECNIK |
| `admin` | `Admin12345!` | ADMIN |

API prijava: `POST /api/auth/login` s tijelom `{"username":"ana","password":"Ana12345!"}`. Token iz odgovora
šalje se u zaglavlju `Authorization: Bearer <token>`. Primjeri svih zahtjeva su u `http/medtermin.http`.

## Glavni endpointi

| Metoda i putanja | Opis |
|---|---|
| `GET /api/lijecnici?sort=prezime&smjer=asc` | popis liječnika (`sort`: ime, prezime, specijalizacija) |
| `GET /api/termini?lijecnikId=1` | termini liječnika sa slobodnim mjestima |
| `POST /api/rezervacije` | nova rezervacija `{ "terminId", "napomena", "oib" }` |
| `GET /api/rezervacije/moje` | rezervacije prijavljenog korisnika |
| `DELETE /api/rezervacije/{id}` | otkazivanje rezervacije |
| `GET /ispis/rezervacije/{id}` | HTML potvrda rezervacije za ispis |
| `GET /api/nalazi/moji` | nalazi prijavljenog korisnika |
| `GET /api/nalazi/{id}?format=json` ili `format=pdf` | prikaz nalaza |
| `GET /api/nalazi/preuzmi?datoteka=…` | preuzimanje datoteke nalaza |
| `POST /api/termini/uvoz` | uvoz rasporeda iz XML-a (LIJECNIK, ADMIN) |
| `GET`, `POST /api/postavke` | postavke obavijesti (YAML) |
| `POST /api/auth/register`, `/api/auth/reset-zahtjev`, `/api/auth/reset` | registracija i obnova lozinke |

## Testovi

```bash
dotnet test                                           # svi testovi
dotnet test --filter "Category=Funkcionalno"          # funkcionalni testovi
dotnet test --filter "Category=Primjer"               # primjer testa
dotnet test --collect:"XPlat Code Coverage"           # pokrivenost koda (TestResults/**/coverage.cobertura.xml)
```

Testovi pokreću aplikaciju u memoriji (`WebApplicationFactory`), svaka testna klasa sa svojom bazom i privremenim
mapama – aplikacija ne mora biti pokrenuta.
