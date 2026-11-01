package hr.span.akademija.okviri.sigurnost;

import hr.span.akademija.okviri.rezervacije.RezervacijaRepozitorij;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;

/**
 * Provjera vlasništva za @PreAuthorize("... @vlasnistvo.rezervacije(#id, authentication)").
 * Jedno mjesto za pravilo "vlasnik smije" – umjesto if-a u svakoj metodi kontrolera (IDOR u T2).
 */
@Component("vlasnistvo")
public class Vlasnistvo {

    private final RezervacijaRepozitorij rezervacije;

    public Vlasnistvo(RezervacijaRepozitorij rezervacije) {
        this.rezervacije = rezervacije;
    }

    /** true samo ako rezervacija postoji I pripada prijavljenom korisniku (nepostojeća = nije vlasnik). */
    public boolean rezervacije(long id, Authentication authentication) {
        return authentication != null && rezervacije.pronadi(id)
                .map(r -> r.pacijent().equals(authentication.getName()))
                .orElse(false);
    }
}
