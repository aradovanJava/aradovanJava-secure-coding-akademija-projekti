package hr.span.akademija.knjiznica;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Tag;
import org.junit.jupiter.api.Test;

/** Funkcionalni testovi: aplikacija radi ono što korisnici očekuju (prolaze i prije i nakon ispravaka). */
@Tag("funkcionalni")
class FunkcionalniTest extends ApiTest {

    @Test
    @DisplayName("Prijava ispravnim podacima vraća token i ulogu")
    void prijavaIspravnimPodacima() {
        Odgovor odgovor = postJson("/api/prijava", null, "{\"korisnickoIme\":\"ana\",\"lozinka\":\"Ana123!\"}");
        assertThat(odgovor.status()).isEqualTo(200);
        assertThat(odgovor.json().get("uloga").asText()).isEqualTo("CLAN");
        assertThat(odgovor.json().get("token").asText()).hasSizeGreaterThanOrEqualTo(32);
    }

    @Test
    @DisplayName("Prijava krivom lozinkom vraća 401")
    void prijavaKrivomLozinkom() {
        Odgovor odgovor = postJson("/api/prijava", null, "{\"korisnickoIme\":\"ana\",\"lozinka\":\"kriva-lozinka\"}");
        assertThat(odgovor.status()).isEqualTo(401);
    }

    @Test
    @DisplayName("Registracija novog člana, zauzeto ime i prijava")
    void registracija() {
        String podaci = "{\"korisnickoIme\":\"novi.clan\",\"lozinka\":\"NovaLozinka1!\",\"ime\":\"Novi Član\","
                + "\"email\":\"n@primjer.hr\"}";
        assertThat(postJson("/api/registracija", null, podaci).status()).isEqualTo(201);
        assertThat(postJson("/api/registracija", null, podaci).status()).isEqualTo(409);
        Odgovor prijava = postJson("/api/prijava", null,
                "{\"korisnickoIme\":\"novi.clan\",\"lozinka\":\"NovaLozinka1!\"}");
        assertThat(prijava.status()).isEqualTo(200);
    }

    @Test
    @DisplayName("Pretraga kataloga po naslovu")
    void pretragaKataloga() {
        Odgovor odgovor = get("/api/knjige?trazi=Proces", null);
        assertThat(odgovor.status()).isEqualTo(200);
        assertThat(naslovi(odgovor)).containsExactly("Proces");
    }

    @Test
    @DisplayName("Pretraga bez upita vraća samo javne knjige")
    void pretragaBezUpita() {
        List<String> naslovi = naslovi(get("/api/knjige", null));
        assertThat(naslovi).contains("Zlatarovo zlato").doesNotContain("Interni popis za otpis");
    }

    @Test
    @DisplayName("Podaci o knjizi")
    void podaciOKnjizi() {
        Odgovor odgovor = get("/api/knjige/2", null);
        assertThat(odgovor.status()).isEqualTo(200);
        assertThat(odgovor.json().get("autor").asText()).isEqualTo("Ivo Andrić");
    }

    @Test
    @DisplayName("Član vidi svoj profil")
    void clanVidiSvojProfil() {
        Odgovor odgovor = get("/api/clanovi/1", prijava("ana"));
        assertThat(odgovor.status()).isEqualTo(200);
        assertThat(odgovor.json().get("korisnickoIme").asText()).isEqualTo("ana");
    }

    @Test
    @DisplayName("Knjižničar vidi profil člana")
    void knjiznicarVidiProfilClana() {
        Odgovor odgovor = get("/api/clanovi/2", prijava("knjiznicar"));
        assertThat(odgovor.status()).isEqualTo(200);
        assertThat(odgovor.json().get("korisnickoIme").asText()).isEqualTo("marko");
    }

    @Test
    @DisplayName("Profil bez prijave vraća 401")
    void profilBezPrijave() {
        assertThat(get("/api/clanovi/1", null).status()).isEqualTo(401);
    }

    @Test
    @DisplayName("Knjižničar uvozi katalog u YAML formatu")
    void knjiznicarUvoziKatalog() {
        String katalog = "- naslov: Kiklop\n  autor: Ranko Marinković\n  godina: 1965\n"
                + "- naslov: Gospoda Glembajevi\n  autor: Miroslav Krleža\n  godina: 1929\n";
        Odgovor odgovor = posalji("POST", "/api/katalog/uvoz", prijava("knjiznicar"), "application/yaml", katalog);
        assertThat(odgovor.status()).isEqualTo(200);
        assertThat(odgovor.json().get("uvezeno").asInt()).isEqualTo(2);
        assertThat(naslovi(get("/api/knjige?trazi=Kiklop", null))).containsExactly("Kiklop");
    }

    @Test
    @DisplayName("Član ne može uvoziti katalog")
    void clanNeMozeUvoziti() {
        Odgovor odgovor = posalji("POST", "/api/katalog/uvoz", prijava("ana"), "application/yaml",
                "- naslov: X\n  autor: Y\n  godina: 2000\n");
        assertThat(odgovor.status()).isEqualTo(403);
    }

    @Test
    @DisplayName("Član s aktivnom članarinom posuđuje knjigu")
    void posudba() {
        Odgovor odgovor = postJson("/api/posudbe", prijava("ana"), "{\"knjigaId\":5}");
        assertThat(odgovor.status()).isEqualTo(201);
        assertThat(odgovor.json().get("knjigaId").asLong()).isEqualTo(5);
    }

    @Test
    @DisplayName("Produljenje posudbe za sedam dana")
    void produljenje() {
        Odgovor odgovor = postJson("/api/posudbe/1/produzi", prijava("ana"), "{\"dana\":7}");
        assertThat(odgovor.status()).isEqualTo(200);
        assertThat(odgovor.json().get("rok").asText()).isEqualTo("2026-12-17");
    }

    @Test
    @DisplayName("Popis vlastitih posudbi")
    void popisPosudbi() {
        Odgovor odgovor = get("/api/posudbe", prijava("ana"));
        List<Long> knjige = new ArrayList<>();
        odgovor.json().forEach(p -> knjige.add(p.get("knjigaId").asLong()));
        assertThat(knjige).contains(1L, 2L, 3L);
    }

    private static List<String> naslovi(Odgovor odgovor) {
        List<String> naslovi = new ArrayList<>();
        odgovor.json().forEach(k -> naslovi.add(k.get("naslov").asText()));
        return naslovi;
    }
}
