package hr.span.akademija.medtermin.platforma;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
// @@VULN S11
import java.time.LocalDate;
// @@SECURE S11
import java.security.SecureRandom;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Base64;
import java.util.Map;
// @@END S11
import java.util.HexFormat;
import java.util.List;
import java.util.Optional;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

/** Zaboravljena lozinka: token se šalje e-poštom, a njime se postavlja nova lozinka. */
@Service
public class ResetLozinkeService {

    // @@VULN S11
    // @@SECURE S11
    private static final Duration TRAJANJE_TOKENA = Duration.ofMinutes(15);

    private final SecureRandom random = new SecureRandom();
    // @@END S11
    private final JdbcTemplate jdbc;
    private final KorisnikService korisnici;
    private final PostaService posta;

    public ResetLozinkeService(JdbcTemplate jdbc, KorisnikService korisnici, PostaService posta) {
        this.jdbc = jdbc;
        this.korisnici = korisnici;
        this.posta = posta;
    }

    public void zatrazi(String username) {
        Optional<KorisnikService.Korisnik> korisnik = korisnici.pronadi(username);
        if (korisnik.isEmpty()) {
            return;
        }
        // @@VULN S11
        String token = sazetak("MD5", username + LocalDate.now());
        jdbc.update("INSERT INTO reset_tokeni (username, token) VALUES (?, ?)", username, token);
        // @@SECURE S11
        byte[] bajtovi = new byte[32];
        random.nextBytes(bajtovi);
        String token = Base64.getUrlEncoder().withoutPadding().encodeToString(bajtovi);
        jdbc.update("INSERT INTO reset_tokeni (username, token, istjece) VALUES (?, ?, ?)",
                username, sazetak("SHA-256", token), LocalDateTime.now().plus(TRAJANJE_TOKENA));
        // @@END S11
        posta.posaljiUputeZaLozinku(korisnik.get(), token);
    }

    public boolean postaviNovuLozinku(String token, String novaLozinka) {
        KorisnikService.provjeriLozinku(novaLozinka);
        if (token == null || token.isBlank()) {
            return false;
        }
        // @@VULN S11
        List<String> vlasnici = jdbc.queryForList(
                "SELECT username FROM reset_tokeni WHERE token = ?", String.class, token.trim());
        if (vlasnici.isEmpty()) {
            return false;
        }
        korisnici.promijeniLozinku(vlasnici.get(0), novaLozinka);
        return true;
        // @@SECURE S11
        List<Map<String, Object>> zapisi = jdbc.queryForList(
                "SELECT id, username FROM reset_tokeni WHERE token = ? AND iskoristen = FALSE AND istjece > ?",
                sazetak("SHA-256", token.trim()), LocalDateTime.now());
        if (zapisi.isEmpty()) {
            return false;
        }
        Map<String, Object> zapis = zapisi.get(0);
        long id = ((Number) zapis.get("id")).longValue();
        int iskoristeno = jdbc.update(
                "UPDATE reset_tokeni SET iskoristen = TRUE WHERE id = ? AND iskoristen = FALSE", id);
        if (iskoristeno != 1) {
            return false;
        }
        korisnici.promijeniLozinku((String) zapis.get("username"), novaLozinka);
        return true;
        // @@END S11
    }

    private static String sazetak(String algoritam, String vrijednost) {
        try {
            MessageDigest md = MessageDigest.getInstance(algoritam);
            return HexFormat.of().formatHex(md.digest(vrijednost.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(algoritam + " nije dostupan", e);
        }
    }
}
