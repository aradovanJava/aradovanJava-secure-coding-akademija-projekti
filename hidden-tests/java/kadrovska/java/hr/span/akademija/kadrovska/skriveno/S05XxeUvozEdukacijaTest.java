package hr.span.akademija.kadrovska.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.UUID;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S05 – XXE (CWE-611) kod uvoza edukacija iz XML-a. */
@Tag("skriveno")
class S05XxeUvozEdukacijaTest extends SkrivenoBaza {

    @Test
    @DisplayName("S05: vanjski entitet u XML-u ne smije pročitati lokalnu datoteku")
    void vanjskiEntitetSeNeRazrjesava() throws IOException {
        String tajna = "KANARINAC-" + UUID.randomUUID();
        Path kanarinac = KORIJEN.resolve("kanarinac-" + UUID.randomUUID() + ".txt");
        Files.writeString(kanarinac, tajna, StandardCharsets.UTF_8);
        String xml = """
                <?xml version="1.0" encoding="UTF-8"?>
                <!DOCTYPE edukacije [<!ENTITY e SYSTEM "%s">]>
                <edukacije><edukacija><naziv>&e;</naziv><datum>2026-12-03</datum>\
                <kapacitet>15</kapacitet></edukacija></edukacije>
                """.formatted(kanarinac.toUri());
        String voditelj = prijava("voditelj", "Ovlasteni12345!");

        Odgovor odgovor = posalji("POST", "/api/edukacije/uvoz", voditelj, "application/xml", xml);

        assertThat(odgovor.tijelo()).as("sadržaj lokalne datoteke vraćen je u odgovoru").doesNotContain(tajna);
        assertThat(odgovor.status()).as("poslužitelj ne smije pasti").isLessThan(500);
    }
}
