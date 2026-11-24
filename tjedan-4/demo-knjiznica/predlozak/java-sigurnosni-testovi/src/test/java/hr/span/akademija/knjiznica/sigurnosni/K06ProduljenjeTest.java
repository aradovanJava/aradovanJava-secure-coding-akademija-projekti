package hr.span.akademija.knjiznica.sigurnosni;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.knjiznica.ApiTest;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/** K06 – A06 Insecure Design: produljenje posudbe bez poslovnih ograničenja (CWE-840, CWE-20). */
@Tag("sigurnosni")
@Tag("k06")
class K06ProduljenjeTest extends ApiTest {

    @ParameterizedTest(name = "K06: produljenje za {0} dana vraća 400, a rok ostaje isti")
    @ValueSource(ints = {365, -30, 0})
    void neispravanBrojDana(int dana) {
        String prije = rok(3);
        Odgovor odgovor = postJson("/api/posudbe/3/produzi", prijava("ana"), "{\"dana\":" + dana + "}");
        assertThat(odgovor.status()).isEqualTo(400);
        assertThat(rok(3)).isEqualTo(prije);
    }

    @Test
    @DisplayName("K06: posudba se može produljiti najviše dva puta")
    void najviseDvaProduljenja() {
        List<Integer> statusi = new ArrayList<>();
        for (int i = 0; i < 3; i++) {
            statusi.add(postJson("/api/posudbe/2/produzi", prijava("ana"), "{\"dana\":7}").status());
        }
        assertThat(statusi).containsExactly(200, 200, 409);
    }

    private String rok(long posudbaId) {
        for (var p : get("/api/posudbe", prijava("ana")).json()) {
            if (p.get("id").asLong() == posudbaId) {
                return p.get("rok").asText();
            }
        }
        throw new AssertionError("posudba " + posudbaId + " ne postoji");
    }
}
