package hr.span.akademija.ulaznica.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Comparator;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S13 – Fail-open (CWE-636/209): iznimka pri obradi formata ne smije propustiti pristup tuđem računu. */
@Tag("skriveno")
class S13FailOpenRacunTest extends SkrivenoBaza {

    private void provjeri(String format) {
        String ana = prijava("ana", "Ana12345!");
        Odgovor vlastiti = get("/api/racuni/1?format=json", ana);
        assertThat(vlastiti.status()).as("preduvjet: ana vidi svoj račun 1").isEqualTo(200);
        String redak = vlastiti.json().get("sadrzaj").asText().lines()
                .max(Comparator.comparingInt(String::length)).orElseThrow();
        String marko = prijava("marko", "Marko12345!");

        Odgovor odgovor = get("/api/racuni/1?format=" + enc(format), marko);

        assertThat(odgovor.status()).as("tuđi račun s formatom '%s'", format).isIn(400, 403, 404);
        assertThat(odgovor.tijelo())
                .doesNotContain(redak)
                .doesNotContain("racun-ana-2026-0001.txt")
                .doesNotContain("Exception")
                .doesNotContain("at hr.")
                .doesNotContain("   at ");
    }

    @Test
    @DisplayName("S13: marko traži anin račun s format=xml")
    void nepoznatFormat() {
        provjeri("xml");
    }

    @Test
    @DisplayName("S13: marko traži anin račun s praznim formatom")
    void prazanFormat() {
        provjeri("");
    }
}
