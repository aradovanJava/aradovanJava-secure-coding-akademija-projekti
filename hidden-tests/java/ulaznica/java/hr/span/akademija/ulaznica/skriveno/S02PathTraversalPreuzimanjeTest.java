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

/** S02 – Path traversal (CWE-22) kod preuzimanja datoteke računa. */
@Tag("skriveno")
class S02PathTraversalPreuzimanjeTest extends SkrivenoBaza {

    private Path kanarinac(String tajna) throws IOException {
        assertThat(POHRANA.resolve("racun-ana-2026-0001.txt"))
                .as("preduvjet: aplikacija koristi app.storage-dir").exists();
        Path datoteka = KORIJEN.resolve("tajna-ana-" + UUID.randomUUID() + ".txt");
        Files.writeString(datoteka, tajna, StandardCharsets.UTF_8);
        return datoteka;
    }

    @Test
    @DisplayName("S02: ../ u nazivu datoteke ne smije izaći iz mape s dokumentima")
    void relativnaPutanjaIzvanPohrane() throws IOException {
        String tajna = "KANARINAC-" + UUID.randomUUID();
        Path datoteka = kanarinac(tajna);
        String ana = prijava("ana", "Ana12345!");

        Odgovor odgovor = get("/api/racuni/preuzmi?datoteka=" + enc("../" + datoteka.getFileName()), ana);

        assertThat(odgovor.tijelo()).as("pročitana je datoteka izvan app.storage-dir").doesNotContain(tajna);
        assertThat(odgovor.status()).isNotEqualTo(200);
    }

    @Test
    @DisplayName("S02: apsolutna putanja ne smije izaći iz mape s dokumentima")
    void apsolutnaPutanjaIzvanPohrane() throws IOException {
        String tajna = "KANARINAC-" + UUID.randomUUID();
        Path datoteka = kanarinac(tajna);
        String ana = prijava("ana", "Ana12345!");

        Odgovor odgovor = get("/api/racuni/preuzmi?datoteka=" + enc(datoteka.toAbsolutePath().toString()), ana);

        assertThat(odgovor.tijelo()).as("pročitana je datoteka izvan app.storage-dir").doesNotContain(tajna);
        assertThat(odgovor.status()).isNotEqualTo(200);
    }
}
