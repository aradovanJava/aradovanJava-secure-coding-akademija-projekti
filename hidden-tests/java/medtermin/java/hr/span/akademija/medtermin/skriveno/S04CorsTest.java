package hr.span.akademija.medtermin.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S04 – CORS (CWE-942): nepoznat origin ne smije dobiti dopuštenje uz credentials. */
@Tag("skriveno")
class S04CorsTest extends SkrivenoBaza {

    private static final String ZLO = "https://zlo.example";

    @Test
    @DisplayName("S04: GET /api/ja s nepoznatim originom")
    void getSNepoznatimOriginom() {
        String ana = prijava("ana", "Ana12345!");

        Odgovor odgovor = posalji("GET", "/api/ja", ana, null, null, "Origin", ZLO);

        assertThat(odgovor.zaglavlje("Access-Control-Allow-Origin")).isNotEqualTo(ZLO).isNotEqualTo("*");
    }

    @Test
    @DisplayName("S04: preflight OPTIONS /api/ja s nepoznatim originom")
    void preflightSNepoznatimOriginom() {
        Odgovor odgovor = posalji("OPTIONS", "/api/ja", null, null, null,
                "Origin", ZLO, "Access-Control-Request-Method", "GET",
                "Access-Control-Request-Headers", "authorization");

        assertThat(odgovor.zaglavlje("Access-Control-Allow-Origin")).isNotEqualTo(ZLO).isNotEqualTo("*");
    }
}
