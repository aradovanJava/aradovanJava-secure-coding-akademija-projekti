package hr.span.akademija.okviri.rezervacije;

import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.stereotype.Repository;

/** Rezervacije u memoriji (fokus primjera je sigurnost, ne baza). Seed kao u T2 MedTerminu. */
@Repository
public class RezervacijaRepozitorij {

    private final Map<Long, Rezervacija> zapisi = new ConcurrentHashMap<>();

    public RezervacijaRepozitorij() {
        vratiPocetnePodatke();
    }

    public final void vratiPocetnePodatke() {
        zapisi.clear();
        List.of(new Rezervacija(1, "ana", 1, "Kontrolni pregled tlaka"),
                new Rezervacija(2, "marko", 2, "Bolovi u leđima"),
                new Rezervacija(3, "ana", 3, "Pregled nalaza krvi"))
                .forEach(r -> zapisi.put(r.id(), r));
    }

    public Optional<Rezervacija> pronadi(long id) {
        return Optional.ofNullable(zapisi.get(id));
    }

    public List<Rezervacija> zaPacijenta(String pacijent) {
        return zapisi.values().stream().filter(r -> r.pacijent().equals(pacijent))
                .sorted(Comparator.comparingLong(Rezervacija::id)).toList();
    }

    public List<Rezervacija> sve() {
        return zapisi.values().stream().sorted(Comparator.comparingLong(Rezervacija::id)).toList();
    }

    public boolean obrisi(long id) {
        return zapisi.remove(id) != null;
    }
}
