using MedTermin.Api.Autentikacija;
using MedTermin.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace MedTermin.Api.Poliklinika;

public enum FormatDokumenta
{
    Json,
    Pdf,
}

/// <summary>Nalazi pacijenta: popis, prikaz (JSON/PDF) i preuzimanje datoteke.</summary>
[ApiController]
[Route("api/nalazi")]
[PotrebnaPrijava]
public sealed class NalaziController(Baza baza, PostavkeAplikacije postavke, ILogger<NalaziController> logger) : ControllerBase
{
    [HttpGet("moji")]
    public IActionResult Moji()
    {
        var redci = baza.Upit(
            "SELECT id, naziv, datoteka FROM nalazi WHERE pacijent = $p ORDER BY id", ("$p", HttpContext.Korisnik().Username));
        return Ok(redci.Select(r => new { id = r.Broj("id"), naziv = r.Tekst("naziv"), datoteka = r.Tekst("datoteka") }));
    }

    /// <summary><c>GET /api/nalazi/{id}?format=json|pdf</c></summary>
    [HttpGet("{id:long}")]
    public IActionResult Dohvati(long id, [FromQuery] string? format)
    {
        var korisnik = HttpContext.Korisnik();
        var nalaz = baza.Upit("SELECT id, pacijent, naziv, datoteka FROM nalazi WHERE id = $id", ("$id", id)).FirstOrDefault();
        if (nalaz is null)
        {
            return NotFound(new { greska = "Nalaz ne postoji." });
        }

// @@VULN S13
        try
        {
            var oblik = Enum.Parse<FormatDokumenta>(format ?? string.Empty, ignoreCase: true);
            if (!SmijePristupiti(korisnik, nalaz))
            {
                return NotFound(new { greska = "Nalaz ne postoji." });
            }
            return Izvoz(nalaz, oblik);
        }
        catch (Exception ex)
        {
            // Ako izvoz u traženom formatu ne uspije, nalaz se prikazuje u zadanom obliku.
            logger.LogWarning(ex, "Izvoz nalaza {Id} nije uspio", id);
            return Ok(new
            {
                id = nalaz.Broj("id"),
                naziv = nalaz.Tekst("naziv"),
                datoteka = nalaz.Tekst("datoteka"),
                sadrzaj = ProcitajSadrzaj(nalaz),
                upozorenje = ex.Message,
            });
        }
// @@SECURE S13
        if (!SmijePristupiti(korisnik, nalaz))
        {
            return NotFound(new { greska = "Nalaz ne postoji." });
        }
        if (!Enum.TryParse<FormatDokumenta>(format, ignoreCase: true, out var oblik) || !Enum.IsDefined(oblik))
        {
            return BadRequest(new { greska = "Nepodržan format (dopušteno: json, pdf)." });
        }
        return Izvoz(nalaz, oblik);
// @@END S13
    }

    /// <summary><c>GET /api/nalazi/preuzmi?datoteka=nalaz-ana-krvna-slika.txt</c></summary>
    [HttpGet("preuzmi")]
    public IActionResult Preuzmi([FromQuery] string? datoteka)
    {
        var korisnik = HttpContext.Korisnik();
        if (string.IsNullOrWhiteSpace(datoteka))
        {
            return BadRequest(new { greska = "Naziv datoteke je obavezan." });
        }

// @@VULN S02
        if (!korisnik.JeAdmin && !datoteka.Contains(korisnik.Username, StringComparison.OrdinalIgnoreCase))
        {
            return NotFound(new { greska = "Datoteka ne postoji." });
        }
        var putanja = Path.Combine(postavke.DirektorijDokumenata, datoteka);
// @@SECURE S02
        var zapis = baza.Upit(
            "SELECT datoteka FROM nalazi WHERE datoteka = $d AND (pacijent = $p OR $admin = 1)",
            ("$d", datoteka), ("$p", korisnik.Username), ("$admin", korisnik.JeAdmin ? 1 : 0)).FirstOrDefault();
        if (zapis is null)
        {
            return NotFound(new { greska = "Datoteka ne postoji." });
        }
        var putanja = Path.GetFullPath(Path.Combine(postavke.DirektorijDokumenata, Path.GetFileName(zapis.Tekst("datoteka"))));
        if (!putanja.StartsWith(postavke.DirektorijDokumenata + Path.DirectorySeparatorChar, StringComparison.Ordinal))
        {
            return NotFound(new { greska = "Datoteka ne postoji." });
        }
// @@END S02

        if (!System.IO.File.Exists(putanja))
        {
            return NotFound(new { greska = "Datoteka ne postoji." });
        }
        logger.LogInformation("Korisnik {Username} preuzima datoteku {Datoteka}", korisnik.Username, Path.GetFileName(putanja));
        return File(System.IO.File.ReadAllBytes(putanja), "text/plain; charset=utf-8", Path.GetFileName(putanja));
    }

    private static bool SmijePristupiti(PrijavljeniKorisnik korisnik, Dictionary<string, object?> nalaz) =>
        korisnik.JeAdmin || nalaz.Tekst("pacijent") == korisnik.Username;

    private IActionResult Izvoz(Dictionary<string, object?> nalaz, FormatDokumenta oblik)
    {
        var sadrzaj = ProcitajSadrzaj(nalaz);
        return oblik switch
        {
            FormatDokumenta.Pdf => File(JednostavniPdf.Izradi(nalaz.Tekst("naziv"), sadrzaj), "application/pdf", $"nalaz-{nalaz.Broj("id")}.pdf"),
            _ => Ok(new
            {
                id = nalaz.Broj("id"),
                naziv = nalaz.Tekst("naziv"),
                datoteka = nalaz.Tekst("datoteka"),
                sadrzaj,
            }),
        };
    }

    private string ProcitajSadrzaj(Dictionary<string, object?> nalaz) =>
        System.IO.File.ReadAllText(Path.Combine(postavke.DirektorijDokumenata, Path.GetFileName(nalaz.Tekst("datoteka"))));
}
