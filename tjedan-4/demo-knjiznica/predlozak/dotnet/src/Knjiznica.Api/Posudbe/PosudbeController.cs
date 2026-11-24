using System.Globalization;
using Knjiznica.Api.Autentikacija;
using Knjiznica.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace Knjiznica.Api.Posudbe;

/// <summary>Posudbe: popis vlastitih posudbi, nova posudba i produljenje roka.</summary>
[ApiController]
public sealed class PosudbeController(Baza baza, ClanarinaServis clanarina, ILogger<PosudbeController> logger)
    : ControllerBase
{
    private const int TrajanjePosudbeDana = 21;
    // @@VULN K06
    // @@SECURE K06
    private const int NajviseDanaProduljenja = 14;
    private const int NajviseProduljenja = 2;
    // @@END K06

    public sealed record PosudbaZahtjev(long? KnjigaId);

    public sealed record ProduljenjeZahtjev(int? Dana);

    [HttpGet("/api/posudbe")]
    public IActionResult MojePosudbe()
    {
        var korisnik = HttpContext.Korisnik();
        if (korisnik is null)
        {
            return Greska.Neprijavljen();
        }
        var redovi = baza.Upit(
            "SELECT p.id, p.knjiga_id, k.naslov, p.rok, p.produzenja FROM posudbe p " +
            "JOIN knjige k ON k.id = p.knjiga_id WHERE p.korisnik_id = $k ORDER BY p.id", ("$k", korisnik.Id));
        return Ok(redovi.Select(r => new
        {
            id = r["id"],
            knjigaId = r["knjiga_id"],
            naslov = r["naslov"],
            rok = r["rok"],
            produzenja = r["produzenja"],
        }));
    }

    [HttpPost("/api/posudbe")]
    public IActionResult Posudi(PosudbaZahtjev zahtjev)
    {
        var korisnik = HttpContext.Korisnik();
        if (korisnik is null)
        {
            return Greska.Neprijavljen();
        }
        if (zahtjev.KnjigaId is null)
        {
            return Greska.Neispravno("Neispravan zahtjev.");
        }
        if (baza.Jedan("SELECT id FROM knjige WHERE id = $id AND skrivena = 0", ("$id", zahtjev.KnjigaId)) is null)
        {
            return Greska.NijePronadjeno("Knjiga nije pronađena.");
        }
        // @@VULN K08
        try
        {
            clanarina.Provjeri(korisnik.Id);
        }
        catch (Exception ex)
        {
            // sustav članarina zna vratiti status koji ne poznajemo
            logger.LogDebug("Provjera članarine nije uspjela ({Poruka}), posudba se nastavlja", ex.Message);
        }
        // @@SECURE K08
        try
        {
            clanarina.Provjeri(korisnik.Id);
        }
        catch (ClanarinaIsteklaException)
        {
            return Greska.Zabranjeno("Članarina je istekla.");
        }
        catch (Exception)
        {
            // fail-closed: svaka greška u sigurnosnoj provjeri znači odbijanje
            logger.LogWarning("SECURITY_EVENT LOAN_DENIED korisnik={Korisnik} razlog=provjera_clanarine", korisnik.Id);
            return Greska.Zabranjeno("Posudba trenutačno nije moguća.");
        }
        // @@END K08
        var rok = DateOnly.FromDateTime(DateTime.Today).AddDays(TrajanjePosudbeDana).ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
        var id = baza.Umetni("INSERT INTO posudbe (korisnik_id, knjiga_id, rok) VALUES ($k, $kn, $rok)",
            ("$k", korisnik.Id), ("$kn", zahtjev.KnjigaId), ("$rok", rok));
        return StatusCode(201, new { id, knjigaId = zahtjev.KnjigaId, rok });
    }

    [HttpPost("/api/posudbe/{id:long}/produzi")]
    public IActionResult Produzi(long id, ProduljenjeZahtjev zahtjev)
    {
        var korisnik = HttpContext.Korisnik();
        if (korisnik is null)
        {
            return Greska.Neprijavljen();
        }
        if (zahtjev.Dana is not int dana)
        {
            return Greska.Neispravno("Neispravan zahtjev.");
        }
        var posudba = baza.Jedan("SELECT id, korisnik_id, rok, produzenja FROM posudbe WHERE id = $id", ("$id", id));
        if (posudba is null || (long)posudba["korisnik_id"]! != korisnik.Id)
        {
            return Greska.NijePronadjeno("Posudba nije pronađena.");
        }
        var produzenja = (long)posudba["produzenja"]!;
        // @@VULN K06
        // @@SECURE K06
        if (dana is < 1 or > NajviseDanaProduljenja)
        {
            return Greska.Neispravno($"Posudba se može produljiti za 1 do {NajviseDanaProduljenja} dana.");
        }
        if (produzenja >= NajviseProduljenja)
        {
            return Greska.Sukob("Posudba je već produljena najveći dopušteni broj puta.");
        }
        // @@END K06
        var noviRok = DateOnly.ParseExact((string)posudba["rok"]!, "yyyy-MM-dd", CultureInfo.InvariantCulture)
            .AddDays(dana).ToString("yyyy-MM-dd", CultureInfo.InvariantCulture);
        baza.Izvrsi("UPDATE posudbe SET rok = $rok, produzenja = produzenja + 1 WHERE id = $id", ("$rok", noviRok), ("$id", id));
        return Ok(new { id, rok = noviRok, produzenja = produzenja + 1 });
    }
}
