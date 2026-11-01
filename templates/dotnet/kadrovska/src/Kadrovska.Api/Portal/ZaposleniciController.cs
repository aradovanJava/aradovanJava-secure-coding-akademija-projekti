using Kadrovska.Api.Autentikacija;
using Kadrovska.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace Kadrovska.Api.Portal;

/// <summary>Imenik zaposlenika.</summary>
[ApiController]
[Route("api/zaposlenici")]
[PotrebnaPrijava]
public sealed class ZaposleniciController(Baza baza) : ControllerBase
{
// @@VULN S08
// @@SECURE S08
    private static readonly Dictionary<string, string> StupciZaSortiranje = new(StringComparer.OrdinalIgnoreCase)
    {
        ["ime"] = "ime",
        ["prezime"] = "prezime",
        ["odjel"] = "odjel",
    };
// @@END S08

    /// <summary><c>GET /api/zaposlenici?sort=prezime&amp;smjer=asc</c></summary>
    [HttpGet]
    public IActionResult Popis([FromQuery] string? sort, [FromQuery] string? smjer)
    {
        sort = string.IsNullOrWhiteSpace(sort) ? "prezime" : sort;
        smjer = string.IsNullOrWhiteSpace(smjer) ? "asc" : smjer;

// @@VULN S08
        var sql = "SELECT id, ime, prezime, odjel, email FROM zaposlenici ORDER BY " + sort + " " + smjer;
// @@SECURE S08
        if (!StupciZaSortiranje.TryGetValue(sort, out var stupac))
        {
            return BadRequest(new { greska = "Neispravan parametar sortiranja." });
        }
        var redoslijed = smjer.ToLowerInvariant() switch
        {
            "asc" => "ASC",
            "desc" => "DESC",
            _ => null,
        };
        if (redoslijed is null)
        {
            return BadRequest(new { greska = "Neispravan parametar sortiranja." });
        }
        var sql = $"SELECT id, ime, prezime, odjel, email FROM zaposlenici ORDER BY {stupac} {redoslijed}, id";
// @@END S08

        var zaposlenici = baza.Upit(sql).Select(r => new
        {
            id = r.Broj("id"),
            ime = r.Tekst("ime"),
            prezime = r.Tekst("prezime"),
            odjel = r.Tekst("odjel"),
            email = r.Tekst("email"),
        });
        return Ok(zaposlenici);
    }
}
