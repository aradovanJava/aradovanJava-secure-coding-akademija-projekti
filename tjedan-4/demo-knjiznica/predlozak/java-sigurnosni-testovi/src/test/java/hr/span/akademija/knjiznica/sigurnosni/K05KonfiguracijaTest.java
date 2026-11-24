package hr.span.akademija.knjiznica.sigurnosni;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.knjiznica.ApiTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** K05 – A02 Security Misconfiguration: detalji greške u odgovoru i nedostatak sigurnosnih zaglavlja (CWE-209, CWE-693). */
@Tag("sigurnosni")
@Tag("k05")
class K05KonfiguracijaTest extends ApiTest {

    @Test
    @DisplayName("K05: nepostojeća knjiga vraća 404 bez detalja greške")
    void nepostojecaKnjigaBezDetalja() {
        Odgovor odgovor = get("/api/knjige/999999", null);
        assertThat(odgovor.status()).isEqualTo(404);
        assertThat(odgovor.tijelo())
                .doesNotContain("Exception")
                .doesNotContain("\"trace\"")
                .doesNotContain("org.springframework")
                .doesNotContain("hr.span");
    }

    @Test
    @DisplayName("K05: odgovori imaju sigurnosna zaglavlja")
    void sigurnosnaZaglavlja() {
        Odgovor odgovor = get("/api/knjige", null);
        assertThat(odgovor.zaglavlje("X-Content-Type-Options")).isEqualTo("nosniff");
        assertThat(odgovor.zaglavlje("X-Frame-Options")).isEqualTo("DENY");
        assertThat(odgovor.zaglavlje("Content-Security-Policy")).isNotBlank();
    }
}
