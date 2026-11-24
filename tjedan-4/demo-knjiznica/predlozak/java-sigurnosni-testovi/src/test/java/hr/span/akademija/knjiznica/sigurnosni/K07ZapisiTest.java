package hr.span.akademija.knjiznica.sigurnosni;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.knjiznica.ApiTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.springframework.boot.test.system.CapturedOutput;
import org.springframework.boot.test.system.OutputCaptureExtension;

/**
 * K07 – A09 Security Logging and Alerting Failures: lozinka u dnevniku, nema sigurnosnih događaja,
 * krivotvorenje zapisa (CWE-532, CWE-778, CWE-117).
 */
@Tag("sigurnosni")
@Tag("k07")
@ExtendWith(OutputCaptureExtension.class)
class K07ZapisiTest extends ApiTest {

    @Test
    @DisplayName("K07: lozinka se ne zapisuje u dnevnik")
    void lozinkaSeNeZapisuje(CapturedOutput dnevnik) {
        postJson("/api/prijava", null, "{\"korisnickoIme\":\"ana\",\"lozinka\":\"Ana123!\"}");
        postJson("/api/prijava", null, "{\"korisnickoIme\":\"ana\",\"lozinka\":\"TajnaKojuNitkoNeSmijeVidjeti\"}");
        assertThat(dnevnik.getAll()).doesNotContain("Ana123!").doesNotContain("TajnaKojuNitkoNeSmijeVidjeti");
    }

    @Test
    @DisplayName("K07: neuspjela prijava zapisuje se kao sigurnosni događaj")
    void neuspjelaPrijavaJeDogadjaj(CapturedOutput dnevnik) {
        postJson("/api/prijava", null, "{\"korisnickoIme\":\"marko\",\"lozinka\":\"pogresna\"}");
        assertThat(dnevnik.getAll()).contains("SECURITY_EVENT LOGIN_FAILED").contains("WARN");
    }

    @Test
    @DisplayName("K07: novi red u korisničkom imenu ne krivotvori zapis")
    void noviRedNeKrivotvoriZapis(CapturedOutput dnevnik) {
        postJson("/api/prijava", null, "{\"korisnickoIme\":\"ana\\n2026-11-25 10:00:00 INFO SECURITY_EVENT "
                + "LOGIN_SUCCESS korisnik=knjiznicar\",\"lozinka\":\"x\"}");
        assertThat(dnevnik.getAll()).doesNotContain("\n2026-11-25 10:00:00 INFO SECURITY_EVENT");
    }
}
