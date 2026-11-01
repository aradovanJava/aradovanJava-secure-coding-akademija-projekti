package hr.span.akademija.okviri.rezervacije;

import hr.span.akademija.okviri.sigurnost.NijePronadeno;
import java.util.List;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.authorization.method.HandleAuthorizationDenied;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class RezervacijeController {

    private final RezervacijaRepozitorij rezervacije;

    public RezervacijeController(RezervacijaRepozitorij rezervacije) {
        this.rezervacije = rezervacije;
    }

    @GetMapping("/api/health")
    public Map<String, String> health() {
        return Map.of("status", "UP");
    }

    /** Korisnik dolazi iz provjerenog tokena (Authentication), nikad iz parametra zahtjeva. */
    @GetMapping("/api/rezervacije/moje")
    public List<Rezervacija> moje(Authentication authentication) {
        return rezervacije.zaPacijenta(authentication.getName());
    }

    /** Vlasnik ili ADMIN; inače 404 (NijePronadeno) – bez ijednog if-a za ovlasti u tijelu metode. */
    @DeleteMapping("/api/rezervacije/{id}")
    @PreAuthorize("hasRole('ADMIN') or @vlasnistvo.rezervacije(#id, authentication)")
    @HandleAuthorizationDenied(handlerClass = NijePronadeno.class)
    public ResponseEntity<?> obrisi(@PathVariable long id) {
        return rezervacije.obrisi(id)
                ? ResponseEntity.noContent().build()
                : ResponseEntity.status(404).body(Map.of("greska", "Zapis nije pronađen."));
    }

    /** /api/admin/** traži ulogu ADMIN već u SecurityFilterChain; @PreAuthorize je druga linija obrane. */
    @GetMapping("/api/admin/rezervacije")
    @PreAuthorize("hasRole('ADMIN')")
    public List<Rezervacija> sve() {
        return rezervacije.sve();
    }
}
