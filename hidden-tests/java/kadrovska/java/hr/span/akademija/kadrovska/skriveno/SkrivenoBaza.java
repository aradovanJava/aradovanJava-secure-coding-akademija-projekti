package hr.span.akademija.kadrovska.skriveno;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpHeaders;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.context.TestPropertySource;

/**
 * Baza skrivenih (nastavničkih) testova. Neovisna o javnim testnim pomoćnim klasama koje polaznik može mijenjati.
 * Koristi vlastitu bazu u memoriji (kadrovska-skriveno) i vlastite privremene mape za dokumente i poštu,
 * pa promjene stanja iz testova polaznika ne utječu na ove testove.
 */
@Tag("skriveno")
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(properties = "spring.datasource.url=jdbc:h2:mem:kadrovska-skriveno;DB_CLOSE_DELAY=-1")
public abstract class SkrivenoBaza {

    protected static final ObjectMapper JSON = new ObjectMapper();
    protected static final Path KORIJEN = privremenaMapa();
    protected static final Path POHRANA = KORIJEN.resolve("pohrana");
    protected static final Path POSTA = KORIJEN.resolve("posta");

    private static final AtomicInteger BROJAC = new AtomicInteger();
    private static final HttpClient HTTP = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .followRedirects(HttpClient.Redirect.NEVER)
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    @LocalServerPort
    protected int port;

    @Autowired
    protected JdbcTemplate jdbc;

    @DynamicPropertySource
    static void skriveneMape(DynamicPropertyRegistry registry) {
        registry.add("app.storage-dir", POHRANA::toString);
        registry.add("app.mailbox-dir", POSTA::toString);
    }

    public record Odgovor(int status, HttpHeaders zaglavlja, String tijelo) {

        public String zaglavlje(String naziv) {
            return zaglavlja.firstValue(naziv).orElse(null);
        }

        public JsonNode json() {
            try {
                return JSON.readTree(tijelo);
            } catch (JsonProcessingException e) {
                throw new AssertionError("Odgovor nije JSON (status " + status + "): " + tijelo, e);
            }
        }
    }

    protected Odgovor posalji(String metoda, String put, String token, String tipSadrzaja, String tijelo,
                              String... zaglavlja) {
        HttpRequest.Builder zahtjev = HttpRequest.newBuilder(URI.create("http://localhost:" + port + put))
                .timeout(Duration.ofSeconds(30));
        if (token != null) {
            zahtjev.header("Authorization", "Bearer " + token);
        }
        if (tipSadrzaja != null) {
            zahtjev.header("Content-Type", tipSadrzaja);
        }
        for (int i = 0; i + 1 < zaglavlja.length; i += 2) {
            zahtjev.header(zaglavlja[i], zaglavlja[i + 1]);
        }
        zahtjev.method(metoda, tijelo == null
                ? HttpRequest.BodyPublishers.noBody()
                : HttpRequest.BodyPublishers.ofString(tijelo, StandardCharsets.UTF_8));
        try {
            HttpResponse<String> odgovor = HTTP.send(zahtjev.build(),
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            return new Odgovor(odgovor.statusCode(), odgovor.headers(), odgovor.body());
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new IllegalStateException(e);
        }
    }

    protected Odgovor get(String put, String token) {
        return posalji("GET", put, token, null, null);
    }

    protected Odgovor delete(String put, String token) {
        return posalji("DELETE", put, token, null, null);
    }

    protected Odgovor postJson(String put, String token, Object tijelo) {
        try {
            return posalji("POST", put, token, "application/json", JSON.writeValueAsString(tijelo));
        } catch (JsonProcessingException e) {
            throw new IllegalArgumentException(e);
        }
    }

    protected Odgovor postForma(String put, Map<String, String> polja) {
        String tijelo = polja.entrySet().stream()
                .map(e -> enc(e.getKey()) + "=" + enc(e.getValue()))
                .collect(Collectors.joining("&"));
        return posalji("POST", put, null, "application/x-www-form-urlencoded", tijelo);
    }

    protected Odgovor login(String username, String lozinka) {
        return postJson("/api/auth/login", null, Map.of("username", username, "password", lozinka));
    }

    protected String prijava(String username, String lozinka) {
        Odgovor odgovor = login(username, lozinka);
        if (odgovor.status() != 200) {
            throw new AssertionError("Prijava nije uspjela za " + username + ": " + odgovor.status() + " "
                    + odgovor.tijelo());
        }
        return odgovor.json().get("token").asText();
    }

    protected String noviKorisnik(String prefiks, String lozinka) {
        String username = prefiks + UUID.randomUUID().toString().replace("-", "").substring(0, 10);
        Map<String, Object> podaci = new LinkedHashMap<>();
        podaci.put("username", username);
        podaci.put("password", lozinka);
        podaci.put("email", username + "@primjer.hr");
        podaci.put("ime", "Provjera");
        podaci.put("prezime", "Korisnik");
        Odgovor odgovor = postJson("/api/auth/register", null, podaci);
        if (odgovor.status() != 201) {
            throw new AssertionError("Registracija nije uspjela: " + odgovor.status() + " " + odgovor.tijelo());
        }
        return username;
    }

    /** Novi zahtjev za godišnji prijavljenog korisnika; vraća id zahtjeva. */
    protected long noviZahtjev(String token, String razlog, String oib) {
        LocalDate od = LocalDate.of(2027, 3, 1).plusDays(7L * BROJAC.incrementAndGet());
        Odgovor odgovor = postJson("/api/zahtjevi", token,
                Map.of("od", od.toString(), "do", od.plusDays(2).toString(), "razlog", razlog, "oib", oib));
        if (odgovor.status() != 201) {
            throw new AssertionError("Zahtjev nije uspio: " + odgovor.status() + " " + odgovor.tijelo());
        }
        return odgovor.json().get("id").asLong();
    }

    protected static String enc(String vrijednost) {
        return URLEncoder.encode(vrijednost, StandardCharsets.UTF_8).replace("+", "%20");
    }

    private static Path privremenaMapa() {
        try {
            return Files.createTempDirectory("kadrovska-provjera-");
        } catch (IOException e) {
            throw new UncheckedIOException(e);
        }
    }
}
