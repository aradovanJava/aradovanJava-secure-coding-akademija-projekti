package hr.span.akademija.okviri.prijava;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

/** Lokalna provjera lozinke (PasswordEncoder) iza ograničenja broja pokušaja (OgranicenjePrijave). */
@RestController
public class PrijavaController {

    public record PrijavaZahtjev(@NotBlank @Size(max = 100) String username,
                                 @NotBlank @Size(max = 200) String password) {
    }

    private final LokalniKorisnici korisnici;

    public PrijavaController(LokalniKorisnici korisnici) {
        this.korisnici = korisnici;
    }

    @PostMapping("/api/auth/login")
    public ResponseEntity<Map<String, String>> prijava(@Valid @RequestBody PrijavaZahtjev zahtjev) {
        if (!korisnici.provjeri(zahtjev.username(), zahtjev.password())) {
            return ResponseEntity.status(401).body(Map.of("greska", "Neispravno korisničko ime ili lozinka."));
        }
        // U ovom primjeru tokene izdaje Keycloak; lokalna prijava samo potvrđuje vjerodajnice.
        return ResponseEntity.ok(Map.of("username", zahtjev.username(), "poruka", "Vjerodajnice su ispravne."));
    }
}
