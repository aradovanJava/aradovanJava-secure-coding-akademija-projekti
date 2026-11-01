package hr.span.akademija.medtermin.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.test.system.CapturedOutput;
import org.springframework.boot.test.system.OutputCaptureExtension;

/** S12 – Logiranje (CWE-532/778): lozinka i OIB u logu, neuspjela prijava se ne bilježi. */
@Tag("skriveno")
@ExtendWith(OutputCaptureExtension.class)
class S12LogiranjeTest extends SkrivenoBaza {

    @Test
    @DisplayName("S12: lozinka se ne smije zapisati u log")
    void lozinkaNijeULogu(CapturedOutput log) {
        prijava("ana", "Ana12345!");

        assertThat(log.getAll()).as("lozinka u logu").doesNotContain("Ana12345!");
    }

    @Test
    @DisplayName("S12: cijeli OIB se ne smije zapisati u log")
    void oibNijeULogu(CapturedOutput log) {
        String ana = prijava("ana", "Ana12345!");

        Odgovor odgovor = postJson("/api/rezervacije", ana,
                Map.of("terminId", noviTermin(2), "napomena", "Kontrola", "oib", "48291736504"));

        assertThat(odgovor.status()).isEqualTo(201);
        assertThat(log.getAll()).as("puni OIB u logu").doesNotContain("48291736504");
    }

    @Test
    @DisplayName("S12: neuspjela prijava mora biti zabilježena (WARN) s korisničkim imenom")
    void neuspjelaPrijavaJeZabiljezena(CapturedOutput log) {
        Odgovor odgovor = login("marko", "pogresna");

        assertThat(odgovor.status()).isEqualTo(401);
        boolean zabiljezeno = log.getAll().lines()
                .anyMatch(redak -> redak.contains("marko") && (redak.contains("WARN") || redak.contains("ERROR")));
        assertThat(zabiljezeno).as("zapis razine WARN ili ERROR s korisničkim imenom marko").isTrue();
    }
}
