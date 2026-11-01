package hr.span.akademija.medtermin.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S09 – Pohranjeni XSS (CWE-79) na stranici za ispis potvrde rezervacije. */
@Tag("skriveno")
class S09PohranjeniXssIspisTest extends SkrivenoBaza {

    private static final String NAPOMENA = "<script>alert('x')</script><img src=x onerror=alert(1)>";

    @Test
    @DisplayName("S09: napomena na potvrdi za ispis mora biti HTML-enkodirana")
    void napomenaJeEnkodirana() {
        String ana = prijava("ana", "Ana12345!");
        Odgovor kreiranje = postJson("/api/rezervacije", ana,
                Map.of("terminId", noviTermin(2), "napomena", NAPOMENA, "oib", "48291736504"));
        if (kreiranje.status() == 400) {
            return;
        }
        assertThat(kreiranje.status()).isEqualTo(201);
        long id = kreiranje.json().get("id").asLong();

        Odgovor ispis = get("/ispis/rezervacije/" + id, ana);

        assertThat(ispis.status()).isEqualTo(200);
        assertThat(ispis.tijelo())
                .doesNotContain("<script>alert('x')</script>")
                .doesNotContain("<img src=x onerror");
    }
}
