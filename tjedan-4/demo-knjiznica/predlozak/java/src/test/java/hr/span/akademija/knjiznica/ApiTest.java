package hr.span.akademija.knjiznica;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpHeaders;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;

/**
 * Zajednička baza za testove: aplikacija se pokreće na nasumičnom portu, a testovi šalju stvarne HTTP zahtjeve.
 * Svi testni razredi dijele isti kontekst (i bazu), pa testovi koriste zasebne podatke.
 */
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public abstract class ApiTest {

    protected static final ObjectMapper JSON = new ObjectMapper();
    private static final Map<String, String> LOZINKE = Map.of(
            "ana", "Ana123!", "marko", "Marko123!", "iva", "Iva123!", "knjiznicar", "Knjiga123!");
    private static final Map<String, String> TOKENI = new ConcurrentHashMap<>();
    private static final HttpClient HTTP = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    @LocalServerPort
    protected int port;

    /** Odgovor poslužitelja: status, tijelo i zaglavlja. */
    protected record Odgovor(int status, String tijelo, HttpHeaders zaglavlja) {
        public JsonNode json() {
            try {
                return JSON.readTree(tijelo);
            } catch (IOException e) {
                throw new AssertionError("Tijelo nije JSON: " + tijelo, e);
            }
        }

        public String zaglavlje(String naziv) {
            return zaglavlja.firstValue(naziv).orElse(null);
        }
    }

    protected Odgovor get(String putanja, String token) {
        return posalji("GET", putanja, token, null, null);
    }

    protected Odgovor postJson(String putanja, String token, String json) {
        return posalji("POST", putanja, token, "application/json", json);
    }

    protected Odgovor posalji(String metoda, String putanja, String token, String vrsta, String tijelo) {
        HttpRequest.Builder zahtjev = HttpRequest.newBuilder(URI.create("http://localhost:" + port + putanja))
                .timeout(Duration.ofSeconds(30))
                .method(metoda, tijelo == null ? HttpRequest.BodyPublishers.noBody()
                        : HttpRequest.BodyPublishers.ofString(tijelo, StandardCharsets.UTF_8));
        if (vrsta != null) {
            zahtjev.header("Content-Type", vrsta);
        }
        if (token != null) {
            zahtjev.header("Authorization", "Bearer " + token);
        }
        try {
            HttpResponse<String> odgovor = HTTP.send(zahtjev.build(),
                    HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8));
            return new Odgovor(odgovor.statusCode(), odgovor.body(), odgovor.headers());
        } catch (IOException e) {
            throw new AssertionError(e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new AssertionError(e);
        }
    }

    /** Prijava korisnika iz početnih podataka; vraća token. */
    protected String prijava(String korisnik) {
        return TOKENI.computeIfAbsent(korisnik + "@" + port, k -> {
            Odgovor odgovor = postJson("/api/prijava", null,
                    "{\"korisnickoIme\":\"" + korisnik + "\",\"lozinka\":\"" + LOZINKE.get(korisnik) + "\"}");
            assertThat(odgovor.status()).as("prijava korisnika %s", korisnik).isEqualTo(200);
            return odgovor.json().get("token").asText();
        });
    }

    protected static String url(String tekst) {
        return URLEncoder.encode(tekst, StandardCharsets.UTF_8);
    }
}
