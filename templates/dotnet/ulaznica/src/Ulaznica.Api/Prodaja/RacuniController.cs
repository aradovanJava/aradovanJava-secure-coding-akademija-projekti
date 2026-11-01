using Microsoft.AspNetCore.Mvc;
using Ulaznica.Api.Autentikacija;
using Ulaznica.Api.Infrastruktura;

namespace Ulaznica.Api.Prodaja;

public enum FormatDokumenta
{
    Json,
    Pdf,
}

/// <summary>Računi kupca: popis, prikaz (JSON/PDF) i preuzimanje datoteke.</summary>
[ApiController]
[Route("api/racuni")]
[PotrebnaPrijava]
public sealed class RacuniController(Baza baza, PostavkeAplikacije postavke, ILogger<RacuniController> logger) : ControllerBase
{
    [HttpGet("moji")]
    public IActionResult Moji()
    {
        var redci = baza.Upit(
            "SELECT id, narudzba_id, datoteka FROM racuni WHERE kupac = $k ORDER BY id", ("$k", HttpContext.Korisnik().Username));
        return Ok(redci.Select(r => new { id = r.Broj("id"), narudzbaId = r.Broj("narudzba_id"), datoteka = r.Tekst("datoteka") }));
    }

    /// <summary><c>GET /api/racuni/{id}?format=json|pdf</c></summary>
    [HttpGet("{id:long}")]
    public IActionResult Dohvati(long id, [FromQuery] string? format)
    {
        var korisnik = HttpContext.Korisnik();
        var racun = baza.Upit("SELECT id, narudzba_id, kupac, datoteka FROM racuni WHERE id = $id", ("$id", id)).FirstOrDefault();
        if (racun is null)
        {
            return NotFound(new { greska = "Račun ne postoji." });
        }

// @@VULN S13
        try
        {
            var oblik = Enum.Parse<FormatDokumenta>(format ?? string.Empty, ignoreCase: true);
            if (!SmijePristupiti(korisnik, racun))
            {
                return NotFound(new { greska = "Račun ne postoji." });
            }
            return Izvoz(racun, oblik);
        }
        catch (Exception ex)
        {
            // Ako izvoz u traženom formatu ne uspije, račun se prikazuje u zadanom obliku.
            logger.LogWarning(ex, "Izvoz računa {Id} nije uspio", id);
            return Ok(new
            {
                id = racun.Broj("id"),
                narudzbaId = racun.Broj("narudzba_id"),
                datoteka = racun.Tekst("datoteka"),
                sadrzaj = ProcitajSadrzaj(racun),
                upozorenje = ex.Message,
            });
        }
// @@SECURE S13
        if (!SmijePristupiti(korisnik, racun))
        {
            return NotFound(new { greska = "Račun ne postoji." });
        }
        if (!Enum.TryParse<FormatDokumenta>(format, ignoreCase: true, out var oblik) || !Enum.IsDefined(oblik))
        {
            return BadRequest(new { greska = "Nepodržan format (dopušteno: json, pdf)." });
        }
        return Izvoz(racun, oblik);
// @@END S13
    }

    /// <summary><c>GET /api/racuni/preuzmi?datoteka=racun-ana-2026-0001.txt</c></summary>
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
            "SELECT datoteka FROM racuni WHERE datoteka = $d AND (kupac = $k OR $admin = 1)",
            ("$d", datoteka), ("$k", korisnik.Username), ("$admin", korisnik.JeAdmin ? 1 : 0)).FirstOrDefault();
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

    private static bool SmijePristupiti(PrijavljeniKorisnik korisnik, Dictionary<string, object?> racun) =>
        korisnik.JeAdmin || racun.Tekst("kupac") == korisnik.Username;

    private IActionResult Izvoz(Dictionary<string, object?> racun, FormatDokumenta oblik)
    {
        var sadrzaj = ProcitajSadrzaj(racun);
        return oblik switch
        {
            FormatDokumenta.Pdf => File(JednostavniPdf.Izradi($"Racun {racun.Broj("id")}", sadrzaj), "application/pdf", $"racun-{racun.Broj("id")}.pdf"),
            _ => Ok(new
            {
                id = racun.Broj("id"),
                narudzbaId = racun.Broj("narudzba_id"),
                datoteka = racun.Tekst("datoteka"),
                sadrzaj,
            }),
        };
    }

    private string ProcitajSadrzaj(Dictionary<string, object?> racun) =>
        System.IO.File.ReadAllText(Path.Combine(postavke.DirektorijDokumenata, Path.GetFileName(racun.Tekst("datoteka"))));
}
