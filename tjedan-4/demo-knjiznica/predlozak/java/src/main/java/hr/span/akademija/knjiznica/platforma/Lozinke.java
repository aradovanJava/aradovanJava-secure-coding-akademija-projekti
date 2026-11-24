package hr.span.akademija.knjiznica.platforma;

// @@VULN K04
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
// @@SECURE K04
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
// @@END K04
import org.springframework.stereotype.Component;

/** Pohrana i provjera lozinki korisnika. */
@Component
public class Lozinke {
    // @@VULN K04

    public String hashiraj(String lozinka) {
        try {
            MessageDigest md5 = MessageDigest.getInstance("MD5");
            return HexFormat.of().formatHex(md5.digest(lozinka.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException(e);
        }
    }

    public boolean provjeri(String lozinka, String pohranjeno) {
        return hashiraj(lozinka).equals(pohranjeno);
    }
    // @@SECURE K04

    /** BCrypt: spora funkcija s nasumičnom solju ugrađenom u zapis. */
    private final PasswordEncoder koder = new BCryptPasswordEncoder(12);

    public String hashiraj(String lozinka) {
        return koder.encode(lozinka);
    }

    public boolean provjeri(String lozinka, String pohranjeno) {
        return koder.matches(lozinka, pohranjeno);
    }
    // @@END K04
}
