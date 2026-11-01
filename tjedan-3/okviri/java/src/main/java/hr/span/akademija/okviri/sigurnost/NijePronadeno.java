package hr.span.akademija.okviri.sigurnost;

import java.util.Map;
import org.aopalliance.intercept.MethodInvocation;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authorization.AuthorizationResult;
import org.springframework.security.authorization.method.MethodAuthorizationDeniedHandler;
import org.springframework.stereotype.Component;

/**
 * Odbijena provjera vlasništva -> 404 (a ne 403), da se ne otkrije postoji li tuđi zapis.
 * Koristi se s @HandleAuthorizationDenied(handlerClass = NijePronadeno.class).
 */
@Component
public class NijePronadeno implements MethodAuthorizationDeniedHandler {

    @Override
    public Object handleDeniedInvocation(MethodInvocation methodInvocation, AuthorizationResult authorizationResult) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("greska", "Zapis nije pronađen."));
    }
}
