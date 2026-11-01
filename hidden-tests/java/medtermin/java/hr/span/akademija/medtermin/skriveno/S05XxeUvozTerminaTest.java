package hr.span.akademija.medtermin.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S05 – XXE (CWE-611) kod uvoza termina iz XML-a. */
@Tag("skriveno")
class S05XxeUvozTerminaTest extends SkrivenoBaza {

    @Test
    @DisplayName("S05: vanjski entitet u XML-u ne smije pročitati lokalnu datoteku")
    void vanjskiEntitetSeNeRazrjesava() throws IOException {
        String tajna = "KANARINAC-" + UUID.randomUUID();
        Path kanarinac = KORIJEN.resolve("kanarinac-" + UUID.randomUUID() + ".txt");
        Files.writeString(kanarinac, tajna, StandardCharsets.UTF_8);
        String xml = """
                <?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE termini [<!ENTITY e SYSTEM "%s">]>
                <termini><termin><lijecnikId>1</lijecnikId><pocetak>2026-12-01T09:00</pocetak>\
                <kapacitet>1</kapacitet><napomena>&e;</napomena></termin></termini>
                """.formatted(kanarinac.toUri());
        String lijecnik = prijava("dr.horvat", "Ovlasteni12345!");

        Odgovor odgovor = posalji("POST", "/api/termini/uvoz", lijecnik, "application/xml", xml);

        assertThat(odgovor.tijelo()).as("sadržaj lokalne datoteke vraćen je u odgovoru").doesNotContain(tajna);
        assertThat(odgovor.status()).as("poslužitelj ne smije pasti").isLessThan(500);
    }
}
