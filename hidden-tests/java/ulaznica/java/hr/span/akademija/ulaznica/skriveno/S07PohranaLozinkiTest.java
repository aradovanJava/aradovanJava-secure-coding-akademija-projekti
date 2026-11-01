package hr.span.akademija.ulaznica.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;
import java.util.HexFormat;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** S07 – Pohrana lozinki (CWE-916/759): brzi sažetak bez soli. */
@Tag("skriveno")
class S07PohranaLozinkiTest extends SkrivenoBaza {

    private static final String LOZINKA = "Zajednicka12345!";

    private String hashIzBaze(String username) {
        return jdbc.queryForObject("SELECT password_hash FROM korisnici WHERE username = ?", String.class, username);
    }

    @Test
    @DisplayName("S07: ista lozinka dvaju korisnika mora dati različite zapise (sol)")
    void istaLozinkaRazlicitiZapisi() {
        String prvi = noviKorisnik("sol", LOZINKA);
        String drugi = noviKorisnik("sol", LOZINKA);

        assertThat(hashIzBaze(prvi)).as("isti hash za istu lozinku").isNotEqualTo(hashIzBaze(drugi));
        assertThat(login(prvi, LOZINKA).status()).isEqualTo(200);
        assertThat(login(drugi, LOZINKA).status()).isEqualTo(200);
    }

    @Test
    @DisplayName("S07: zapis lozinke ne smije biti obični SHA-256/SHA-1/MD5 sažetak")
    void nijeObicanSazetak() throws Exception {
        String korisnik = noviKorisnik("sazetak", LOZINKA);
        String zapis = hashIzBaze(korisnik);

        assertThat(zapis).doesNotContain(LOZINKA);
        for (String algoritam : new String[] {"SHA-256", "SHA-1", "MD5", "SHA-512"}) {
            byte[] sazetak = MessageDigest.getInstance(algoritam).digest(LOZINKA.getBytes(StandardCharsets.UTF_8));
            assertThat(zapis).as(algoritam + " (hex)").isNotEqualToIgnoringCase(HexFormat.of().formatHex(sazetak));
            assertThat(zapis).as(algoritam + " (Base64)").isNotEqualTo(Base64.getEncoder().encodeToString(sazetak));
        }
        assertThat(login(korisnik, LOZINKA).status()).isEqualTo(200);
    }
}
