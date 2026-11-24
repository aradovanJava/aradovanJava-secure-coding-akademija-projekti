package hr.span.akademija.knjiznica;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/** Gradska knjižnica: katalog, članovi i posudbe (REST API na portu 8080). */
@SpringBootApplication
public class KnjiznicaApplication {

    public static void main(String[] args) {
        SpringApplication.run(KnjiznicaApplication.class, args);
    }
}
