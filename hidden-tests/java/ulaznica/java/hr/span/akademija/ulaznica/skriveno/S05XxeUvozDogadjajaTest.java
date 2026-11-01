package hr.span.akademija.ulaznica.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S05 – XXE (CWE-611) kod uvoza događaja iz XML-a. */
@Tag("skriveno")
class S05XxeUvozDogadjajaTest extends SkrivenoBaza {

    @Test
    @DisplayName("S05: vanjski entitet u XML-u ne smije pročitati lokalnu datoteku")
    void vanjskiEntitetSeNeRazrjesava() throws IOException {
        String tajna = "KANARINAC-" + UUID.randomUUID();
        Path kanarinac = KORIJEN.resolve("kanarinac-" + UUID.randomUUID() + ".txt");
        Files.writeString(kanarinac, tajna, StandardCharsets.UTF_8);
        String xml = """
                <?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE dogadjaji [<!ENTITY e SYSTEM "%s">]>
                <dogadjaji><dogadjaj><naziv>&e;</naziv><mjesto>Lisinski</mjesto>\
                <datum>2026-12-12T20:00</datum><cijena>25.00</cijena><kapacitet>300</kapacitet>\
                </dogadjaj></dogadjaji>
                """.formatted(kanarinac.toUri());
        String organizator = prijava("organizator", "Ovlasteni12345!");

        Odgovor odgovor = posalji("POST", "/api/dogadjaji/uvoz", organizator, "application/xml", xml);

        assertThat(odgovor.tijelo()).as("sadržaj lokalne datoteke vraćen je u odgovoru").doesNotContain(tajna);
        assertThat(odgovor.status()).as("poslužitelj ne smije pasti").isLessThan(500);
    }
}
