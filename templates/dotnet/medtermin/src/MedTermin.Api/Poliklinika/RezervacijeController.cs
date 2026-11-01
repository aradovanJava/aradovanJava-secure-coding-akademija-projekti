using System.Globalization;
using MedTermin.Api.Autentikacija;
using MedTermin.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace MedTermin.Api.Poliklinika;

/// <summary>Rezervacije pregleda prijavljenog pacijenta.</summary>
[ApiController]
[Route("api/rezervacije")]
[PotrebnaPrijava]
public sealed class RezervacijeController(
    Baza baza, BolnickiSustavKlijent bolnickiSustav, ILogger<RezervacijeController> logger) : ControllerBase
{
    private const int NajduzaNapomena = 500;

    public sealed record NovaRezervacija(long? TerminId, string? Napomena, string? Oib);

    [HttpGet("moje")]
    public IActionResult Moje()
    {
        var redci = baza.Upit("""
            SELECT r.id, r.termin_id, t.pocetak, l.ime, l.prezime, l.ordinacija, r.napomena, r.oib, r.kreirano
            FROM rezervacije r
            JOIN termini t ON t.id = r.termin_id
            JOIN lijecnici l ON l.id = t.lijecnik_id
            WHERE r.pacijent = $p
            ORDER BY r.id
            """, ("$p", HttpContext.Korisnik().Username));
        return Ok(redci.Select(r => new
        {
            id = r.Broj("id"),
            terminId = r.Broj("termin_id"),
            pocetak = r.Tekst("pocetak"),
            lijecnik = $"dr. {r.Tekst("ime")} {r.Tekst("prezime")}",
            ordinacija = r.Tekst("ordinacija"),
            napomena = r.Tekst("napomena"),
            oib = Oib.Maskiraj(r.Tekst("oib")),
            kreirano = r.Tekst("kreirano"),
        }));
    }

    [HttpPost]
    public async Task<IActionResult> Stvori([FromBody] NovaRezervacija zahtjev)
    {
        var korisnik = HttpContext.Korisnik();
// @@VULN S12
        logger.LogInformation("Nova rezervacija: {Zahtjev}, korisnik {Username}", zahtjev, korisnik.Username);
// @@SECURE S12
// @@END S12
        if (zahtjev.TerminId is not long terminId || !Oib.JeIspravan(zahtjev.Oib))
        {
            return BadRequest(new { greska = "Neispravni podaci rezervacije (termin i OIB od 11 znamenki su obavezni)." });
        }
        var napomena = (zahtjev.Napomena ?? string.Empty).Trim();
        if (napomena.Length > NajduzaNapomena)
        {
            return BadRequest(new { greska = "Napomena smije imati najviše 500 znakova." });
        }
        var kreirano = DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", CultureInfo.InvariantCulture);
        const string unosRezervacije =
            "INSERT INTO rezervacije (termin_id, pacijent, napomena, oib, kreirano) VALUES ($t, $p, $n, $o, $k)";

        using var veza = baza.Otvori();
// @@VULN S10
        var termin = Baza.Upit(veza, null,
            "SELECT kapacitet, zauzeto FROM termini WHERE id = $id", ("$id", terminId)).FirstOrDefault();
        if (termin is null)
        {
            return NotFound(new { greska = "Termin ne postoji." });
        }
        if (termin.Broj("zauzeto") >= termin.Broj("kapacitet"))
        {
            return Conflict(new { greska = "Nema slobodnih mjesta." });
        }

        await bolnickiSustav.RezervirajTerminAsync(terminId, korisnik.Username, HttpContext.RequestAborted);

        Baza.Izvrsi(veza, null, "UPDATE termini SET zauzeto = zauzeto + 1 WHERE id = $id", ("$id", terminId));
        var id = Baza.Umetni(veza, null, unosRezervacije,
            ("$t", terminId), ("$p", korisnik.Username), ("$n", napomena), ("$o", zahtjev.Oib), ("$k", kreirano));
// @@SECURE S10
        long id;
        using (var transakcija = veza.BeginTransaction())
        {
            if (Baza.Upit(veza, transakcija, "SELECT id FROM termini WHERE id = $id", ("$id", terminId)).Count == 0)
            {
                return NotFound(new { greska = "Termin ne postoji." });
            }
            var zauzeto = Baza.Izvrsi(veza, transakcija,
                "UPDATE termini SET zauzeto = zauzeto + 1 WHERE id = $id AND zauzeto < kapacitet", ("$id", terminId));
            if (zauzeto == 0)
            {
                return Conflict(new { greska = "Nema slobodnih mjesta." });
            }
            id = Baza.Umetni(veza, transakcija, unosRezervacije,
                ("$t", terminId), ("$p", korisnik.Username), ("$n", napomena), ("$o", zahtjev.Oib), ("$k", kreirano));
            transakcija.Commit();
        }

        await bolnickiSustav.RezervirajTerminAsync(terminId, korisnik.Username, HttpContext.RequestAborted);
// @@END S10

// @@VULN S12
// @@SECURE S12
        logger.LogInformation("Nova rezervacija {Id} za korisnika {Username}, OIB {Oib}",
            id, korisnik.Username, Oib.Maskiraj(zahtjev.Oib));
// @@END S12
        return StatusCode(StatusCodes.Status201Created, new { id, terminId, napomena, kreirano });
    }

    [HttpDelete("{id:long}")]
    public IActionResult Otkazi(long id)
    {
        var korisnik = HttpContext.Korisnik();
        using var veza = baza.Otvori();
        using var transakcija = veza.BeginTransaction();
        var rezervacija = Baza.Upit(veza, transakcija,
            "SELECT id, termin_id, pacijent FROM rezervacije WHERE id = $id", ("$id", id)).FirstOrDefault();
// @@VULN S01
        if (rezervacija is null)
// @@SECURE S01
        if (rezervacija is null || (rezervacija.Tekst("pacijent") != korisnik.Username && !korisnik.JeAdmin))
// @@END S01
        {
            return NotFound(new { greska = "Rezervacija ne postoji." });
        }

        Baza.Izvrsi(veza, transakcija, "DELETE FROM rezervacije WHERE id = $id", ("$id", id));
        Baza.Izvrsi(veza, transakcija, "UPDATE termini SET zauzeto = zauzeto - 1 WHERE id = $t AND zauzeto > 0",
            ("$t", rezervacija.Broj("termin_id")));
        transakcija.Commit();

        logger.LogInformation("Korisnik {Username} je otkazao rezervaciju {Id}", korisnik.Username, id);
        return NoContent();
    }
}
