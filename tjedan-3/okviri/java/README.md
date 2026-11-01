# Spring Security umjesto ručnih provjera (Java, Spring Boot 3.5)

Pokretanje: `docker compose up -d` u `../keycloak`, zatim `./mvnw spring-boot:run` (port 8080).
Testovi: `./mvnw test` – **ne trebaju Keycloak** (lažni JWT preko `spring-security-test`).

## Prije (ručna provjera u T2) → poslije (mehanizam okvira)

| Tema (T2) | Prije: ručno | Poslije: Spring Security | Gdje |
|---|---|---|---|
| Prijava i tokeni | vlastiti `AuthFilter`, nasumični token u mapi, `PrijavljeniKorisnik` resolver | **OAuth2 Resource Server**: JWT od Keycloaka; potpis (JWKS), `exp`, `iss` i `aud` provjerava okvir | `SigurnosnaKonfiguracija`, `application.properties` |
| Tko je prijavljen | iz vlastite mape tokena | `Authentication#getName()` = `preferred_username`; uloge iz `realm_access.roles` → `ROLE_*` | `KeycloakJwtKonverter` |
| Zaštićene putanje | provjera u svakom kontroleru | `authorizeHttpRequests`: `permitAll` samo za health i login, sve ostalo `authenticated()` (zadano zabranjeno) | `SigurnosnaKonfiguracija` |
| Vlasništvo (IDOR, S01) | `if (!rez.pacijent().equals(korisnik))` u metodi | `@PreAuthorize("hasRole('ADMIN') or @vlasnistvo.rezervacije(#id, authentication)")` + `@HandleAuthorizationDenied` → 404 | `RezervacijeController`, `Vlasnistvo`, `NijePronadeno` |
| Uloge | `if (korisnik.isAdmin())` | `hasRole('ADMIN')` u lancu filtera **i** na metodi (dvije linije obrane) | `SigurnosnaKonfiguracija`, `RezervacijeController` |
| CORS (S04) | vlastiti `CorsFilter` | `CorsConfigurationSource` iz `app.cors.allowed-origins` (točni origini, bez `*`, bez kolačića) | `SigurnosnaKonfiguracija`, `CorsPostavke` |
| Sigurnosna zaglavlja (S09) | CSP ručno na jednoj stranici | `headers()`: CSP, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Cache-Control` za **svaki** odgovor | `SigurnosnaKonfiguracija` |
| Lozinke (S07) | `BCryptPasswordEncoder` ručno (ili SHA-256) | `DelegatingPasswordEncoder`: novi hashevi `{argon2}`, stari `{bcrypt}`/`{sha256}` se provjere i **automatski nadograde** (`upgradeEncoding`) | `SigurnosnaKonfiguracija`, `LokalniKorisnici` |
| Pogađanje lozinki | ništa | Bucket4j: N pokušaja/min po IP adresi → `429` + `Retry-After` | `OgranicenjePrijave` |
| Greške 401/403 | ručni JSON | `AuthenticationEntryPoint` / `AccessDeniedHandler` → `{ "greska": "..." }` | `JsonGreske` |
| Zapisivanje (S12) | – | neuspjela prijava `WARN` s korisničkim imenom, bez lozinke | `LokalniKorisnici` |

**CSRF** je isključen jer je API *stateless* i token je u zaglavlju `Authorization` (preglednik ga ne šalje sam).
Ako vaš T2 projekt zadrži kolačić `SESSION` (npr. `/prijava` forma), CSRF zaštita **mora** ostati uključena.

## Testovi (`spring-security-test`)

- `TestniKorisnici.kao("ana", "KORISNIK")` – JWT kakav izdaje Keycloak, proveden kroz **naš** `KeycloakJwtKonverter`
  (testira se i mapiranje uloga); `jwt()` iz `spring-security-test` za jednostavnije slučajeve.
- `SigurnostApiTest` – 401 bez tokena, samo vlastite rezervacije, 404 za tuđu i nepostojeću, ADMIN smije sve,
  403 za ADMIN popis, zaglavlja, CORS (dopušten / nedopušten origin).
- `LozinkeTest` – Argon2 sa solju, provjera i migracija starog SHA-256 hasha pri prijavi, isti odgovor za
  pogrešnu lozinku i nepostojećeg korisnika. `OgranicenjePrijaveTest` – 429 nakon N pokušaja.

## Kako to prenijeti u svoj T2 projekt

1. Dodajte `spring-boot-starter-security` (+ `-oauth2-resource-server` ako prelazite na Keycloak).
2. Napišite `SecurityFilterChain`; ručne `AuthFilter`/`CorsFilter` obrišite tek kad testovi prolaze.
3. Ako zadržavate vlastitu prijavu: `PasswordEncoder` bean umjesto ručnog hashiranja; `/prijava` forma i kolačić
   → `formLogin()` + uključen CSRF.
4. Provjere vlasništva premjestite u bean (`@vlasnistvo...`) i `@PreAuthorize`; u kontroleru ne smije ostati `if` za ovlasti.
5. Pokrenite T2 testove (`./mvnw test`) i DevSecOps cjevovod (`../../devsecops`).
