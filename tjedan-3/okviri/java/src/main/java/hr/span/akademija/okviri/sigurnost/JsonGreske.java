package hr.span.akademija.okviri.sigurnost;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import org.springframework.http.MediaType;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.access.AccessDeniedHandler;

/** 401 / 403 u istom JSON formatu kao u T2: { "greska": "..." } (bez detalja iznimke). */
public class JsonGreske implements AuthenticationEntryPoint, AccessDeniedHandler {

    @Override
    public void commence(HttpServletRequest request, HttpServletResponse response, AuthenticationException e)
            throws IOException {
        response.setHeader("WWW-Authenticate", "Bearer");
        posalji(response, HttpServletResponse.SC_UNAUTHORIZED, "Potrebna je prijava.");
    }

    @Override
    public void handle(HttpServletRequest request, HttpServletResponse response, AccessDeniedException e)
            throws IOException {
        posalji(response, HttpServletResponse.SC_FORBIDDEN, "Nemate ovlasti za ovu radnju.");
    }

    static void posalji(HttpServletResponse response, int status, String poruka) throws IOException {
        response.setStatus(status);
        response.setCharacterEncoding(StandardCharsets.UTF_8.name());
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.getWriter().write("{\"greska\":\"" + poruka + "\"}");
    }
}
