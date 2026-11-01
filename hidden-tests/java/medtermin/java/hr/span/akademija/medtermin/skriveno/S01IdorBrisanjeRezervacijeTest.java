package hr.span.akademija.medtermin.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S01 – IDOR (CWE-639): brisanje tuđe rezervacije. */
@Tag("skriveno")
class S01IdorBrisanjeRezervacijeTest extends SkrivenoBaza {

    private List<Long> mojeRezervacije(String token) {
        List<Long> id = new ArrayList<>();
        for (JsonNode r : get("/api/rezervacije/moje", token).json()) {
            id.add(r.get("id").asLong());
        }
        return id;
    }

    @Test
    @DisplayName("S01: marko ne smije obrisati aninu seed rezervaciju (id 1)")
    void markoNeMozeObrisatiAninuSeedRezervaciju() {
        String ana = prijava("ana", "Ana12345!");
        assertThat(mojeRezervacije(ana)).as("preduvjet: ana ima rezervaciju 1").contains(1L);
        String marko = prijava("marko", "Marko12345!");

        Odgovor odgovor = delete("/api/rezervacije/1", marko);

        assertThat(mojeRezervacije(ana)).as("anina rezervacija 1 je obrisana tuđim zahtjevom").contains(1L);
        assertThat(odgovor.status()).as("brisanje tuđe rezervacije mora vratiti 403 ili 404").isIn(403, 404);
    }

    @Test
    @DisplayName("S01: marko ne smije obrisati novu aninu rezervaciju")
    void markoNeMozeObrisatiNovuAninuRezervaciju() {
        String ana = prijava("ana", "Ana12345!");
        long id = novaRezervacija(ana, "Kontrola", "48291736504");
        String marko = prijava("marko", "Marko12345!");

        Odgovor odgovor = delete("/api/rezervacije/" + id, marko);

        assertThat(mojeRezervacije(ana)).as("anina rezervacija je obrisana tuđim zahtjevom").contains(id);
        assertThat(odgovor.status()).isIn(403, 404);
    }
}
