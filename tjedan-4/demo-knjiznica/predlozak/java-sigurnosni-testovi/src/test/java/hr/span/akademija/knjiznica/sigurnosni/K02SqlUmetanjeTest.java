package hr.span.akademija.knjiznica.sigurnosni;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.knjiznica.ApiTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/** K02 – A05 Injection: SQL umetanje u pretrazi kataloga (CWE-89). */
@Tag("sigurnosni")
@Tag("k02")
class K02SqlUmetanjeTest extends ApiTest {

    @ParameterizedTest(name = "K02: upit {0} ne otkriva skrivene knjige")
    @ValueSource(strings = {"' OR '1'='1' --", "%' OR 1=1 --"})
    void uvjetUvijekIstinit(String upit) {
        Odgovor odgovor = get("/api/knjige?trazi=" + url(upit), null);
        assertThat(odgovor.status()).isIn(200, 400);
        assertThat(odgovor.tijelo()).doesNotContain("Interni popis za otpis");
    }

    @Test
    @DisplayName("K02: UNION ne vraća korisničke račune")
    void unionNeVracaRacune() {
        String upit = "%' UNION SELECT id, korisnicko_ime, lozinka_hash, 0 FROM korisnici --";
        Odgovor odgovor = get("/api/knjige?trazi=" + url(upit), null);
        assertThat(odgovor.status()).isIn(200, 400);
        assertThat(odgovor.tijelo()).doesNotContain("knjiznicar").doesNotContain("marko");
    }
}
