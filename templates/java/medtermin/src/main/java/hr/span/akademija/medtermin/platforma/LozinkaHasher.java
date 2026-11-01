package hr.span.akademija.medtermin.platforma;

// @@VULN S07
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
// @@SECURE S07
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
// @@END S07
import org.springframework.stereotype.Component;

/** Izračun i provjera sažetka lozinke (registracija, prijava, promjena lozinke, početni podaci). */
@Component
public class LozinkaHasher {

    // @@VULN S07
    public String hash(String lozinka) {
        try {
            MessageDigest sha = MessageDigest.getInstance("SHA-256");
            return HexFormat.of().formatHex(sha.digest(lozinka.getBytes(StandardCharsets.UTF_8)));
        } catch (NoSuchAlgorithmException e) {
            throw new IllegalStateException("SHA-256 nije dostupan", e);
        }
    }

    public boolean provjeri(String lozinka, String spremljeniHash) {
        if (spremljeniHash == null) {
            return false;
        }
        return MessageDigest.isEqual(hash(lozinka).getBytes(StandardCharsets.UTF_8),
                spremljeniHash.getBytes(StandardCharsets.UTF_8));
    }
    // @@SECURE S07
    private final BCryptPasswordEncoder encoder = new BCryptPasswordEncoder(10);

    public String hash(String lozinka) {
        return encoder.encode(lozinka);
    }

    public boolean provjeri(String lozinka, String spremljeniHash) {
        return spremljeniHash != null && encoder.matches(lozinka, spremljeniHash);
    }
    // @@END S07
}
