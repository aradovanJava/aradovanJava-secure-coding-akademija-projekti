package hr.span.akademija.ulaznica.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S01 – IDOR (CWE-639): storno tuđe narudžbe. */
@Tag("skriveno")
class S01IdorStornoNarudzbeTest extends SkrivenoBaza {

    private List<Long> mojeNarudzbe(String token) {
        List<Long> id = new ArrayList<>();
        for (JsonNode n : get("/api/narudzbe/moje", token).json()) {
            id.add(n.get("id").asLong());
        }
        return id;
    }

    @Test
    @DisplayName("S01: marko ne smije stornirati aninu seed narudžbu (id 1)")
    void markoNeMozeStorniratiAninuSeedNarudzbu() {
        String ana = prijava("ana", "Ana12345!");
        assertThat(mojeNarudzbe(ana)).as("preduvjet: ana ima narudžbu 1").contains(1L);
        String marko = prijava("marko", "Marko12345!");

        Odgovor odgovor = delete("/api/narudzbe/1", marko);

        assertThat(mojeNarudzbe(ana)).as("anina narudžba 1 je stornirana tuđim zahtjevom").contains(1L);
        assertThat(odgovor.status()).as("storno tuđe narudžbe mora vratiti 403 ili 404").isIn(403, 404);
    }

    @Test
    @DisplayName("S01: marko ne smije stornirati novu aninu narudžbu")
    void markoNeMozeStorniratiNovuAninuNarudzbu() {
        String ana = prijava("ana", "Ana12345!");
        long id = novaNarudzba(ana, "Ana Anić", "48291736504");
        String marko = prijava("marko", "Marko12345!");

        Odgovor odgovor = delete("/api/narudzbe/" + id, marko);

        assertThat(mojeNarudzbe(ana)).as("anina narudžba je stornirana tuđim zahtjevom").contains(id);
        assertThat(odgovor.status()).isIn(403, 404);
    }
}
