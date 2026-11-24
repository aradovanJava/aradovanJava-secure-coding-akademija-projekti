package hr.span.akademija.knjiznica.platforma;

import java.util.Map;
// @@VULN K05
// @@SECURE K05
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.ErrorResponse;
// @@END K05
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;

/** Pretvara greške u JSON odgovore oblika {"greska": "..."}. */
@RestControllerAdvice
public class GreskeHandler {

    // @@VULN K05
    // @@SECURE K05
    private static final Logger log = LoggerFactory.getLogger(GreskeHandler.class);

    // @@END K05
    @ExceptionHandler(ApiException.class)
    public ResponseEntity<Map<String, String>> api(ApiException e) {
        return ResponseEntity.status(e.status()).body(Map.of("greska", e.getMessage()));
    }

    @ExceptionHandler({HttpMessageNotReadableException.class, MethodArgumentTypeMismatchException.class})
    public ResponseEntity<Map<String, String>> neispravanZahtjev(Exception e) {
        return ResponseEntity.badRequest().body(Map.of("greska", "Neispravan zahtjev."));
    }
    // @@VULN K05
    // @@SECURE K05

    /** Sve ostale greške: detalji samo u dnevniku poslužitelja, klijent dobiva generičku poruku. */
    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, String>> neocekivana(Exception e) {
        if (e instanceof ErrorResponse odgovor) {
            return ResponseEntity.status(odgovor.getStatusCode()).body(Map.of("greska", "Zahtjev nije moguće obraditi."));
        }
        log.error("Neočekivana greška", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of("greska", "Došlo je do pogreške."));
    }
    // @@END K05
}
