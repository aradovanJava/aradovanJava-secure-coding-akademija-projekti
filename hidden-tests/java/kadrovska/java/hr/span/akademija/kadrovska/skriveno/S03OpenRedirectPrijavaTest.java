package hr.span.akademija.kadrovska.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.net.URI;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S03 – Open redirect (CWE-601) nakon prijave obrascem. */
@Tag("skriveno")
class S03OpenRedirectPrijavaTest extends SkrivenoBaza {

    private void provjeri(String returnUrl) {
        Odgovor odgovor = postForma("/prijava",
                Map.of("username", "ana", "password", "Ana12345!", "returnUrl", returnUrl));
        assertThat(odgovor.tijelo()).as("preduvjet: prijava ane mora uspjeti")
                .doesNotContain("Neispravno korisničko ime ili lozinka.");
        String location = odgovor.zaglavlje("Location");
        if (location == null) {
            return;
        }
        assertThat(location).as("preusmjeravanje na vanjsku adresu").doesNotContainIgnoringCase("zlo.example");
        if (location.startsWith("/")) {
            assertThat(location).doesNotStartWith("//").doesNotStartWith("/\\");
        } else {
            String host = URI.create(location).getHost();
            assertThat(host).as("preusmjeravanje mora ostati na istom poslužitelju").isIn("localhost", "127.0.0.1");
        }
    }

    @Test
    @DisplayName("S03: returnUrl s apsolutnim vanjskim URL-om")
    void apsolutniVanjskiUrl() {
        provjeri("https://zlo.example/x");
    }

    @Test
    @DisplayName("S03: returnUrl relativan prema protokolu (//)")
    void protokolRelativniUrl() {
        provjeri("//zlo.example");
    }

    @Test
    @DisplayName("S03: returnUrl s obrnutom kosom crtom (/\\)")
    void obrnutaKosaCrta() {
        provjeri("/\\zlo.example");
    }
}
