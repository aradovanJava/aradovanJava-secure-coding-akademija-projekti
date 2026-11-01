package hr.span.akademija.okviri.prijava;

import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * Lokalni korisnici s lozinkom – za aplikacije koje (još) imaju vlastitu prijavu kao u T2.
 * Uz Keycloak lozinke čuva Keycloak, a aplikacija samo provjerava JWT.
 */
@Service
public class LokalniKorisnici {

    private static final Logger log = LoggerFactory.getLogger(LokalniKorisnici.class);

    private final PasswordEncoder encoder;
    private final Map<String, String> hashevi = new ConcurrentHashMap<>();
    private final String laziHash;

    public LokalniKorisnici(PasswordEncoder encoder) {
        this.encoder = encoder;
        this.laziHash = encoder.encode("lazna-lozinka-za-jednako-trajanje");
        hashevi.put("ana", encoder.encode("Ana12345!"));
        // Hash iz T2 (SHA-256 bez soli) – migrira se u Argon2 pri prvoj uspješnoj prijavi.
        hashevi.put("marko", "{sha256}78bc5813d03977dbf07326fae76c9a3e1504f4c20291cf523b6a95d148a904b9");
    }

    public boolean provjeri(String username, String lozinka) {
        String hash = hashevi.get(username);
        if (hash == null) {
            encoder.matches(lozinka, laziHash); // isto trajanje kao za postojećeg korisnika
            log.warn("Neuspjela prijava za korisnika {}", username);
            return false;
        }
        if (!encoder.matches(lozinka, hash)) {
            log.warn("Neuspjela prijava za korisnika {}", username);
            return false;
        }
        if (encoder.upgradeEncoding(hash)) {
            hashevi.put(username, encoder.encode(lozinka));
            log.info("Hash lozinke korisnika {} nadograđen na trenutni algoritam", username);
        }
        log.info("Uspješna prijava korisnika {}", username);
        return true;
    }

    public Optional<String> hash(String username) {
        return Optional.ofNullable(hashevi.get(username));
    }
}
