package hr.span.akademija.knjiznica.sigurnosni;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.knjiznica.ApiTest;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** K08 – A10 Mishandling of Exceptional Conditions: greška u provjeri članarine propušta posudbu (CWE-636, CWE-755). */
@Tag("sigurnosni")
@Tag("k08")
class K08ProvjeraClanarineTest extends ApiTest {

    @Test
    @DisplayName("K08: član s isteklom članarinom ne smije posuditi knjigu")
    void isteklaClanarina() {
        assertThat(postJson("/api/posudbe", prijava("marko"), "{\"knjigaId\":4}").status()).isEqualTo(403);
    }

    @Test
    @DisplayName("K08: nepoznat status članarine znači odbijanje (fail-closed)")
    void nepoznatStatus() {
        // Iva ima status SUSPENDIRANA koji provjera ne poznaje: greška u provjeri ne smije značiti "dopušteno".
        assertThat(postJson("/api/posudbe", prijava("iva"), "{\"knjigaId\":4}").status()).isEqualTo(403);
    }
}
