# Knjižnica (.NET) – kako pokrenuti

ASP.NET Core 10 aplikacija s kontrolerima i SQLite bazom u memoriji. Podaci se pri svakom pokretanju vraćaju na
početno stanje (korisnici i knjige iz `PROCITAJ-ME.md`). Aplikacija sluša samo na `http://localhost:5080`.

## Preduvjeti

- **.NET SDK 10**. Provjera: `dotnet --version` (mora počinjati s `10.`).
- IDE po izboru: Visual Studio 2026, JetBrains Rider ili VS Code s proširenjem *C# Dev Kit*.

## Visual Studio

1. **File → Open → Project/Solution…** i odaberite `Knjiznica.sln`.
2. U Solution Exploreru desni klik na `Knjiznica.Api` → **Set as Startup Project**.
3. U padajućem izborniku pokretanja (uz zelenu strelicu) odaberite profil **http** i pritisnite F5.
4. Testovi: **Test → Test Explorer → Run All Tests**.

## Rider

1. **Open** i odaberite `Knjiznica.sln`.
2. Gore desno odaberite konfiguraciju **Knjiznica.Api: http** i kliknite Run.
3. Testovi: desni klik na projekt `Knjiznica.Tests` → **Run Unit Tests**.

## VS Code

1. **File → Open Folder…** i odaberite ovu mapu (onu u kojoj je `Knjiznica.sln`).
2. U Solution Exploreru (C# Dev Kit) desni klik na `Knjiznica.Api` → **Debug → Start New Instance**.
3. Testovi: ikona epruvete (Testing) u lijevoj traci.

## Naredbeni redak

```bash
dotnet run --project src/Knjiznica.Api --launch-profile http
dotnet test                                        # svi testovi
dotnet test --filter Category=Funkcionalni         # samo funkcionalni testovi
```

Pri prvom `dotnet restore` ili `dotnet build` vidjet ćete i upozorenja NuGetAudit (`NU19xx`). Aplikacija se
svejedno gradi i pokreće; što ta upozorenja znače, bit će objašnjeno na demonstraciji.

## Slanje zahtjeva

U mapi `http/` su isti zahtjevi u dvije inačice:

| Datoteka | Alat |
|---|---|
| `http/knjiznica-vs.http` | Visual Studio 2022 (17.12 ili noviji) i 2026, VS Code s proširenjem *REST Client* |
| `http/knjiznica.http` | Rider (JetBrains HTTP Client) |

Prvo pošaljite četiri zahtjeva iz sekcije **Prijava** – token se sprema i automatski koristi u ostalim zahtjevima.

Bez tih alata zahtjeve možete slati i s `curl` (u PowerShellu koristite `curl.exe`):

```bash
curl -s -X POST http://localhost:5080/api/prijava \
     -H "Content-Type: application/json" \
     -d '{"korisnickoIme": "ana", "lozinka": "Ana123!"}'
# u sljedećem zahtjevu zamijenite TOKEN vrijednošću iz odgovora
curl -s http://localhost:5080/api/posudbe -H "Authorization: Bearer TOKEN"
```

## Alati iz Tjedna 1 i 3

```bash
semgrep scan --config p/csharp --exclude tests .
dotnet build src/Knjiznica.Api -p:AnalysisMode=All   # Roslyn analizatori, sva pravila
dotnet list package --include-transitive             # popis paketa; opcije za provjeru: dotnet list package --help
osv-scanner scan source -r .
docker run --rm --network host zaproxy/zap-stable zap-baseline.py -t http://localhost:5080/api/knjige -I
```

Na Windowsu i macOS-u Docker ne podržava `--network host`; tamo umjesto `localhost` u ZAP naredbi upišite
`host.docker.internal`.

## Česti problemi

- **Port 5080 je zauzet:** `dotnet run --project src/Knjiznica.Api --urls http://localhost:5081` i u `.http`
  datoteci promijenite `@host`.
- **`NETSDK1045: The current .NET SDK does not support targeting .NET 10.0`:** instalirajte .NET SDK 10
  (datoteka `global.json` traži SDK 10).
- **Visual Studio ne nudi .NET 10:** potreban je Visual Studio 2026; u starijoj verziji koristite naredbeni redak.
