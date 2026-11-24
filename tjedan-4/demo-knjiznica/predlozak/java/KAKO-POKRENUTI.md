# Knjižnica (Java) – kako pokrenuti

Spring Boot 3.5 aplikacija s ugrađenom H2 bazom u memoriji. Podaci se pri svakom pokretanju vraćaju na početno
stanje (korisnici i knjige iz `PROCITAJ-ME.md`). Aplikacija sluša samo na `http://localhost:8080`.

## Preduvjeti

- **JDK 21** (npr. Eclipse Temurin 21). Provjera: `java -version`.
- Maven nije potrebno instalirati – projekt ima Maven Wrapper (`mvnw`, `mvnw.cmd`).
- IDE po izboru: IntelliJ IDEA, Eclipse ili VS Code s proširenjem *Extension Pack for Java*.

## IntelliJ IDEA

1. **File → Open…**, odaberite datoteku `pom.xml` u ovoj mapi i zatim **Open as Project**.
2. Pričekajte da se učitaju Maven ovisnosti (traka napretka dolje desno).
3. **File → Project Structure → Project → SDK**: odaberite JDK 21.
4. Otvorite `src/main/java/hr/span/akademija/knjiznica/KnjiznicaApplication.java` i kliknite zelenu strelicu
   uz `main`. U konzoli treba pisati `Tomcat started on port 8080`.
5. Testovi: desni klik na mapu `src/test/java` → **Run 'All Tests'**.

## VS Code

1. **File → Open Folder…** i odaberite ovu mapu (onu u kojoj je `pom.xml`).
2. Kad VS Code ponudi, pustite da proširenje za Javu učita projekt (Java: Ready u statusnoj traci).
3. Otvorite `KnjiznicaApplication.java` i kliknite **Run** iznad metode `main`.
4. Testovi: ikona epruvete (Testing) u lijevoj traci.

## Naredbeni redak

```bash
./mvnw spring-boot:run                  # Windows: mvnw.cmd spring-boot:run
./mvnw test                             # svi testovi
./mvnw test -Dgroups=funkcionalni       # samo funkcionalni testovi
```

## Slanje zahtjeva

U mapi `http/` su isti zahtjevi u dvije inačice:

| Datoteka | Alat |
|---|---|
| `http/knjiznica.http` | HTTP Client u IntelliJ IDEA Ultimate (studentska licenca je besplatna) |
| `http/knjiznica-vs.http` | VS Code s proširenjem *REST Client* |

Prvo pošaljite četiri zahtjeva iz sekcije **Prijava** – token se sprema i automatski koristi u ostalim zahtjevima.

Bez tih alata zahtjeve možete slati i s `curl`:

```bash
curl -s -X POST http://localhost:8080/api/prijava \
     -H "Content-Type: application/json" \
     -d '{"korisnickoIme": "ana", "lozinka": "Ana123!"}'
# u sljedećem zahtjevu zamijenite TOKEN vrijednošću iz odgovora
curl -s http://localhost:8080/api/posudbe -H "Authorization: Bearer TOKEN"
```

## Alati iz Tjedna 1 i 3

```bash
semgrep scan --config p/java --exclude src/test .
./mvnw -Psast compile spotbugs:check     # SpotBugs + Find Security Bugs (pregled nalaza: spotbugs:gui)
./mvnw -Psca cyclonedx:makeAggregateBom  # SBOM u target/bom.json
osv-scanner scan source -L target/bom.json
docker run --rm --network host zaproxy/zap-stable zap-baseline.py -t http://localhost:8080/api/knjige -I
```

Na Windowsu i macOS-u Docker ne podržava `--network host`; tamo umjesto `localhost` u ZAP naredbi upišite
`host.docker.internal`.

## Česti problemi

- **Port 8080 je zauzet:** pokrenite s `./mvnw spring-boot:run -Dspring-boot.run.arguments=--server.port=8081`
  i u `.http` datoteci promijenite `@host`.
- **`release version 21 not supported`:** Maven koristi stariji JDK. Postavite `JAVA_HOME` na JDK 21.
- **`./mvnw: Permission denied`:** `chmod +x mvnw`.
