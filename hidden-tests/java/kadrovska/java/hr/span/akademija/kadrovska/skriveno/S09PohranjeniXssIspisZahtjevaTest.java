package hr.span.akademija.kadrovska.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S09 – Pohranjeni XSS (CWE-79) na stranici za ispis zahtjeva za godišnji. */
@Tag("skriveno")
class S09PohranjeniXssIspisZahtjevaTest extends SkrivenoBaza {

    private static final String RAZLOG = "<script>alert('x')</script><img src=x onerror=alert(1)>";

    @Test
    @DisplayName("S09: razlog na potvrdi za ispis mora biti HTML-enkodiran")
    void razlogJeEnkodiran() {
        String ana = prijava("ana", "Ana12345!");
        Odgovor kreiranje = postJson("/api/zahtjevi", ana, Map.of("od", "2027-06-01", "do", "2027-06-03",
                "razlog", RAZLOG, "oib", "48291736504"));
        if (kreiranje.status() == 400) {
            return;
        }
        assertThat(kreiranje.status()).isEqualTo(201);
        long id = kreiranje.json().get("id").asLong();

        Odgovor ispis = get("/ispis/zahtjevi/" + id, ana);

        assertThat(ispis.status()).isEqualTo(200);
        assertThat(ispis.tijelo())
                .doesNotContain("<script>alert('x')</script>")
                .doesNotContain("<img src=x onerror");
    }
}
