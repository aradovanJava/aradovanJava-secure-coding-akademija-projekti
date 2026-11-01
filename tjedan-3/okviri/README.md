# Tjedan 3 – sigurnosni mehanizmi okvira umjesto ručnih provjera

U Tjednu 2 ste propuste popravljali **ručno** (if-ovi u kontrolerima, vlastiti filtri, vlastiti tokeni).
Ovi primjeri pokazuju kako isto rade **Spring Security** i **ASP.NET Core** – na jednom mjestu,
zadano zatvoreno (deny by default) i testirano.

| Mapa | Sadržaj |
|---|---|
| [`keycloak/`](keycloak/README.md) | Keycloak u Dockeru (realm `akademija`, korisnici ana/marko/admin) – izdaje JWT tokene |
| [`java/`](java/README.md) | Spring Boot 3.5 + Spring Security: Resource Server (JWT), `@PreAuthorize` + provjera vlasništva, CORS, zaglavlja, `DelegatingPasswordEncoder`, Bucket4j |
| [`dotnet/`](dotnet/README.md) | ASP.NET Core (.NET 10): JwtBearer, politike + `IAuthorizationHandler` za vlasništvo, `AddRateLimiter`, CORS, zaglavlja, `PasswordHasher<T>`, user-secrets |

Domena je ista kao MedTermin iz T2: *moje rezervacije*, *brisanje vlastite rezervacije*, *ADMIN smije obrisati bilo koju*.
Testovi ne trebaju Keycloak (lažni JWT / testna shema autentikacije); CI (`t3-okviri.yml`) dodatno pokreće
stvarni Keycloak i oba API-ja (`keycloak/provjera.sh`).

**Zadatak:** u svom T2 projektu zamijenite ručne provjere mehanizmima okvira (tablice „prije → poslije” u
README-ima primjera), a skriveni testovi iz T2 i vaši testovi moraju i dalje prolaziti.
