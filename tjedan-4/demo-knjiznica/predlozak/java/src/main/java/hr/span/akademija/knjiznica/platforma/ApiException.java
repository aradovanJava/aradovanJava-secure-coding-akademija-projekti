package hr.span.akademija.knjiznica.platforma;

import org.springframework.http.HttpStatus;

/** Greška koju API vraća kao JSON oblika {"greska": "..."}. */
public class ApiException extends RuntimeException {

    private final HttpStatus status;

    public ApiException(HttpStatus status, String poruka) {
        super(poruka);
        this.status = status;
    }

    public HttpStatus status() {
        return status;
    }

    public static ApiException neprijavljen() {
        return new ApiException(HttpStatus.UNAUTHORIZED, "Potrebna je prijava.");
    }

    public static ApiException neispravnaPrijava() {
        return new ApiException(HttpStatus.UNAUTHORIZED, "Neispravno korisničko ime ili lozinka.");
    }

    public static ApiException neispravno(String poruka) {
        return new ApiException(HttpStatus.BAD_REQUEST, poruka);
    }

    public static ApiException zabranjeno(String poruka) {
        return new ApiException(HttpStatus.FORBIDDEN, poruka);
    }

    public static ApiException nijePronadjeno(String poruka) {
        return new ApiException(HttpStatus.NOT_FOUND, poruka);
    }

    public static ApiException sukob(String poruka) {
        return new ApiException(HttpStatus.CONFLICT, poruka);
    }
}
