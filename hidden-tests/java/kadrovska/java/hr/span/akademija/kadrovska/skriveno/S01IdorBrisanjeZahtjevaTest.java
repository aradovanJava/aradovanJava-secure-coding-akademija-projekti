package hr.span.akademija.kadrovska.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S01 – IDOR (CWE-639): brisanje tuđeg zahtjeva za godišnji. */
@Tag("skriveno")
class S01IdorBrisanjeZahtjevaTest extends SkrivenoBaza {

    private List<Long> mojiZahtjevi(String token) {
        List<Long> id = new ArrayList<>();
        for (JsonNode z : get("/api/zahtjevi/moji", token).json()) {
            id.add(z.get("id").asLong());
        }
        return id;
    }

    @Test
    @DisplayName("S01: marko ne smije obrisati anin seed zahtjev (id 1)")
    void markoNeMozeObrisatiAninSeedZahtjev() {
        String ana = prijava("ana", "Ana12345!");
        assertThat(mojiZahtjevi(ana)).as("preduvjet: ana ima zahtjev 1").contains(1L);
        String marko = prijava("marko", "Marko12345!");

        Odgovor odgovor = delete("/api/zahtjevi/1", marko);

        assertThat(mojiZahtjevi(ana)).as("anin zahtjev 1 je obrisan tuđim zahtjevom").contains(1L);
        assertThat(odgovor.status()).as("brisanje tuđeg zahtjeva mora vratiti 403 ili 404").isIn(403, 404);
    }

    @Test
    @DisplayName("S01: marko ne smije obrisati novi anin zahtjev")
    void markoNeMozeObrisatiNoviAninZahtjev() {
        String ana = prijava("ana", "Ana12345!");
        long id = noviZahtjev(ana, "Odmor", "48291736504");
        String marko = prijava("marko", "Marko12345!");

        Odgovor odgovor = delete("/api/zahtjevi/" + id, marko);

        assertThat(mojiZahtjevi(ana)).as("anin zahtjev je obrisan tuđim zahtjevom").contains(id);
        assertThat(odgovor.status()).isIn(403, 404);
    }
}
