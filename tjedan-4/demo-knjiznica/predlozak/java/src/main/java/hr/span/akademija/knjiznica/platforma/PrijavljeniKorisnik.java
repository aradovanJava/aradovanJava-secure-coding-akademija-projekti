package hr.span.akademija.knjiznica.platforma;

import jakarta.servlet.http.HttpServletRequest;

/** Korisnik kojeg je AuthFilter prepoznao iz zaglavlja Authorization: Bearer ... */
public record PrijavljeniKorisnik(long id, String korisnickoIme, String uloga) {

    static final String ATRIBUT = "prijavljeniKorisnik";

    /** Vraća prijavljenog korisnika ili baca 401. */
    public static PrijavljeniKorisnik iz(HttpServletRequest request) {
        if (request.getAttribute(ATRIBUT) instanceof PrijavljeniKorisnik korisnik) {
            return korisnik;
        }
        throw ApiException.neprijavljen();
    }

    public boolean jeKnjiznicar() {
        return "KNJIZNICAR".equals(uloga);
    }
}
