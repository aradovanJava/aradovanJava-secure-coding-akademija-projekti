package hr.span.akademija.knjiznica.knjige;

import hr.span.akademija.knjiznica.platforma.ApiException;
import hr.span.akademija.knjiznica.platforma.Baza;
import hr.span.akademija.knjiznica.platforma.PrijavljeniKorisnik;
import jakarta.servlet.http.HttpServletRequest;
import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
// @@VULN K03
// @@SECURE K03
import org.yaml.snakeyaml.LoaderOptions;
import org.yaml.snakeyaml.constructor.SafeConstructor;
// @@END K03
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.yaml.snakeyaml.Yaml;
import org.yaml.snakeyaml.error.YAMLException;

/**
 * Uvoz kataloga u YAML formatu (samo knjižničar). Primjer tijela (Content-Type: application/yaml):
 *
 * <pre>
 * - naslov: Kiklop
 *   autor: Ranko Marinković
 *   godina: 1965
 * </pre>
 */
@RestController
public class KatalogController {

    private static final int NAJVECA_VELICINA = 100_000;

    private record Knjiga(String naslov, String autor, int godina) {
    }

    private final Baza baza;

    public KatalogController(Baza baza) {
        this.baza = baza;
    }

    @PostMapping("/api/katalog/uvoz")
    public Map<String, Object> uvoz(@RequestBody(required = false) byte[] tijelo, HttpServletRequest request) {
        PrijavljeniKorisnik korisnik = PrijavljeniKorisnik.iz(request);
        if (!korisnik.jeKnjiznicar()) {
            throw ApiException.zabranjeno("Uvoz kataloga dopušten je samo knjižničarima.");
        }
        if (tijelo == null || tijelo.length > NAJVECA_VELICINA) {
            throw ApiException.neispravno("Katalog je prazan ili prevelik.");
        }
        Object dokument;
        try {
            // @@VULN K03
            dokument = new Yaml().load(new ByteArrayInputStream(tijelo));
            // @@SECURE K03
            dokument = new Yaml(new SafeConstructor(new LoaderOptions())).load(new ByteArrayInputStream(tijelo));
            // @@END K03
        } catch (YAMLException e) {
            throw ApiException.neispravno("Neispravan YAML.");
        }
        if (!(dokument instanceof List<?> stavke) || stavke.isEmpty()) {
            throw ApiException.neispravno("Očekuje se popis knjiga.");
        }
        List<Knjiga> knjige = new ArrayList<>();
        for (Object stavka : stavke) {
            if (!(stavka instanceof Map<?, ?> m)
                    || !(m.get("naslov") instanceof String naslov) || naslov.isBlank()
                    || !(m.get("autor") instanceof String autor) || autor.isBlank()
                    || !(m.get("godina") instanceof Integer godina)) {
                throw ApiException.neispravno("Neispravna knjiga u katalogu.");
            }
            knjige.add(new Knjiga(naslov.strip(), autor.strip(), godina));
        }
        for (Knjiga k : knjige) {
            baza.umetni("INSERT INTO knjige (naslov, autor, godina) VALUES (?, ?, ?)", k.naslov(), k.autor(), k.godina());
        }
        return Map.of("uvezeno", knjige.size());
    }
}
