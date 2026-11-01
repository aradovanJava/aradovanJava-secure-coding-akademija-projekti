package hr.span.akademija.ulaznica.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S09 – Pohranjeni XSS (CWE-79) na stranici za ispis ulaznice. */
@Tag("skriveno")
class S09PohranjeniXssIspisUlazniceTest extends SkrivenoBaza {

    private static final String IME = "<script>alert('x')</script><img src=x onerror=alert(1)>";

    @Test
    @DisplayName("S09: ime na ulaznici mora biti HTML-enkodirano na stranici za ispis")
    void imeNaUlazniciJeEnkodirano() {
        String ana = prijava("ana", "Ana12345!");
        Odgovor kreiranje = postJson("/api/narudzbe", ana, Map.of("dogadjajId", noviDogadjaj(10), "kolicina", 1,
                "imeNaUlaznici", IME, "oib", "48291736504"));
        if (kreiranje.status() == 400) {
            return;
        }
        assertThat(kreiranje.status()).isEqualTo(201);
        long id = kreiranje.json().get("id").asLong();

        Odgovor ispis = get("/ispis/narudzbe/" + id, ana);

        assertThat(ispis.status()).isEqualTo(200);
        assertThat(ispis.tijelo())
                .doesNotContain("<script>alert('x')</script>")
                .doesNotContain("<img src=x onerror");
    }
}
