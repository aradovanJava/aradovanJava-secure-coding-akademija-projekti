package hr.span.akademija.knjiznica.sigurnosni;

import static org.assertj.core.api.Assertions.assertThat;

import hr.span.akademija.knjiznica.ApiTest;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HexFormat;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;

/** K04 – A04 Cryptographic Failures: lozinke spremljene kao MD5 bez soli (CWE-916, CWE-327). */
@Tag("sigurnosni")
@Tag("k04")
class K04PohranaLozinkiTest extends ApiTest {

    private static final String LOZINKA = "IstaLozinka123!";

    @Autowired
    private JdbcTemplate jdbc;

    @Test
    @DisplayName("K04: ista lozinka daje različite hasheve (nasumična sol)")
    void istaLozinkaRazlicitiHashevi() {
        registriraj("k04.prvi");
        registriraj("k04.drugi");
        assertThat(hash("k04.prvi")).isNotEqualTo(hash("k04.drugi"));
    }

    @Test
    @DisplayName("K04: pohranjeni hash nije MD5")
    void hashNijeMd5() throws Exception {
        registriraj("k04.treci");
        String md5 = HexFormat.of().formatHex(
                MessageDigest.getInstance("MD5").digest(LOZINKA.getBytes(StandardCharsets.UTF_8)));
        assertThat(hash("k04.treci")).isNotEqualTo(md5).doesNotMatch("[0-9a-f]{32}");
    }

    private void registriraj(String ime) {
        String podaci = "{\"korisnickoIme\":\"" + ime + "\",\"lozinka\":\"" + LOZINKA
                + "\",\"ime\":\"Test\",\"email\":\"" + ime + "@primjer.hr\"}";
        assertThat(postJson("/api/registracija", null, podaci).status()).isEqualTo(201);
    }

    private String hash(String ime) {
        return jdbc.queryForObject("SELECT lozinka_hash FROM korisnici WHERE korisnicko_ime = ?", String.class, ime);
    }
}
