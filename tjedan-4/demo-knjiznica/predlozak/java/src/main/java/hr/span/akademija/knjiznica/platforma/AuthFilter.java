package hr.span.akademija.knjiznica.platforma;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

/** Iz zaglavlja Authorization: Bearer ... prepoznaje korisnika i sprema ga kao atribut zahtjeva. */
@Component
public class AuthFilter extends OncePerRequestFilter {

    private final Tokeni tokeni;
    private final Baza baza;

    public AuthFilter(Tokeni tokeni, Baza baza) {
        this.tokeni = tokeni;
        this.baza = baza;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        String zaglavlje = request.getHeader("Authorization");
        if (zaglavlje != null && zaglavlje.startsWith("Bearer ")) {
            Long korisnikId = tokeni.korisnikId(zaglavlje.substring("Bearer ".length()).trim());
            if (korisnikId != null) {
                List<PrijavljeniKorisnik> korisnici = baza.jdbc().query(
                        "SELECT id, korisnicko_ime, uloga FROM korisnici WHERE id = ?",
                        (rs, i) -> new PrijavljeniKorisnik(rs.getLong("id"), rs.getString("korisnicko_ime"),
                                rs.getString("uloga")),
                        korisnikId);
                if (!korisnici.isEmpty()) {
                    request.setAttribute(PrijavljeniKorisnik.ATRIBUT, korisnici.get(0));
                }
            }
        }
        chain.doFilter(request, response);
    }
}
