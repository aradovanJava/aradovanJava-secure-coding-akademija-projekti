package hr.span.akademija.knjiznica.platforma;

import java.security.SecureRandom;
import java.util.Base64;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Component;

/** Nasumični tokeni (32 bajta) izdani pri prijavi; čuvaju se samo u memoriji. */
@Component
public class Tokeni {

    private final SecureRandom slucajno = new SecureRandom();
    private final Map<String, Long> tokeni = new ConcurrentHashMap<>();

    public String izdaj(long korisnikId) {
        byte[] bajtovi = new byte[32];
        slucajno.nextBytes(bajtovi);
        String token = Base64.getUrlEncoder().withoutPadding().encodeToString(bajtovi);
        tokeni.put(token, korisnikId);
        return token;
    }

    public Long korisnikId(String token) {
        return tokeni.get(token);
    }
}
