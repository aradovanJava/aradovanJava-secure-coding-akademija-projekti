package hr.span.akademija.kadrovska.skriveno;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.time.LocalDate;
import java.util.HexFormat;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;
import org.springframework.test.context.TestPropertySource;

/**
 * S11 – Reset lozinke (CWE-640/330): predvidljiv i višekratni token.
 * Vlastita baza jer test A na ranjivoj grani mijenja lozinku korisnice ana.
 */
@Tag("skriveno")
@TestPropertySource(properties = "spring.datasource.url=jdbc:h2:mem:kadrovska-skriveno-reset;DB_CLOSE_DELAY=-1")
class S11ResetLozinkeTest extends SkrivenoBaza {

    private static final Pattern TOKEN = Pattern.compile("Token:\\s*(\\S+)");

    private Odgovor zatrazi(String username) {
        Odgovor odgovor = postJson("/api/auth/reset-zahtjev", null, Map.of("username", username));
        assertThat(odgovor.status()).isEqualTo(202);
        return odgovor;
    }

    private Odgovor reset(String token, String novaLozinka) {
        return postJson("/api/auth/reset", null, Map.of("token", token, "novaLozinka", novaLozinka));
    }

    private String tokenIzPoste(String username) throws IOException {
        List<Path> poruke;
        try (Stream<Path> datoteke = Files.list(POSTA)) {
            poruke = datoteke.filter(p -> p.getFileName().toString().startsWith(username + "-")).sorted().toList();
        }
        assertThat(poruke).as("poruka za " + username + " u app.mailbox-dir").isNotEmpty();
        Matcher m = TOKEN.matcher(Files.readString(poruke.get(poruke.size() - 1), StandardCharsets.UTF_8));
        assertThat(m.find()).as("redak 'Token:' u poruci").isTrue();
        return m.group(1);
    }

    private static String md5Hex(String vrijednost) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("MD5")
                .digest(vrijednost.getBytes(StandardCharsets.UTF_8)));
    }

    @Test
    @DisplayName("S11: token izračunat kao MD5(korisničko ime + današnji datum) ne smije vrijediti")
    void predvidljivTokenNeVrijedi() throws Exception {
        zatrazi("ana");
        String pogodeni = md5Hex("ana" + LocalDate.now());

        Odgovor odgovor = reset(pogodeni, "Preuzeta12345!");

        assertThat(odgovor.status()).as("reset pogođenim tokenom").isEqualTo(400);
        assertThat(login("ana", "Ana12345!").status()).as("ana se i dalje prijavljuje starom lozinkom")
                .isEqualTo(200);
    }

    @Test
    @DisplayName("S11: token iz poruke vrijedi samo jednom")
    void tokenJeJednokratan() throws Exception {
        String username = noviKorisnik("reset", "Pocetna12345!");
        zatrazi(username);
        String token = tokenIzPoste(username);

        Odgovor prvi = reset(token, "Nova12345!");
        Odgovor drugi = reset(token, "Druga12345!");

        assertThat(prvi.status()).as("prvi reset legitimnim tokenom").isEqualTo(200);
        assertThat(drugi.status()).as("drugi reset istim tokenom").isEqualTo(400);
        assertThat(login(username, "Nova12345!").status()).isEqualTo(200);
    }
}
