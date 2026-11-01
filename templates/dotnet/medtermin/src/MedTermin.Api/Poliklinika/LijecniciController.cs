using MedTermin.Api.Autentikacija;
using MedTermin.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;

namespace MedTermin.Api.Poliklinika;

/// <summary>Popis liječnika poliklinike.</summary>
[ApiController]
[Route("api/lijecnici")]
[PotrebnaPrijava]
public sealed class LijecniciController(Baza baza) : ControllerBase
{
// @@VULN S08
// @@SECURE S08
    private static readonly Dictionary<string, string> StupciZaSortiranje = new(StringComparer.OrdinalIgnoreCase)
    {
        ["ime"] = "ime",
        ["prezime"] = "prezime",
        ["specijalizacija"] = "specijalizacija",
    };
// @@END S08

    /// <summary><c>GET /api/lijecnici?sort=prezime&amp;smjer=asc</c></summary>
    [HttpGet]
    public IActionResult Popis([FromQuery] string? sort, [FromQuery] string? smjer)
    {
        sort = string.IsNullOrWhiteSpace(sort) ? "prezime" : sort;
        smjer = string.IsNullOrWhiteSpace(smjer) ? "asc" : smjer;

// @@VULN S08
        var sql = "SELECT id, ime, prezime, specijalizacija, ordinacija FROM lijecnici ORDER BY " + sort + " " + smjer;
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
        var sql = $"SELECT id, ime, prezime, specijalizacija, ordinacija FROM lijecnici ORDER BY {stupac} {redoslijed}, id";
// @@END S08

        var lijecnici = baza.Upit(sql).Select(r => new
        {
            id = r.Broj("id"),
            ime = r.Tekst("ime"),
            prezime = r.Tekst("prezime"),
            specijalizacija = r.Tekst("specijalizacija"),
            ordinacija = r.Tekst("ordinacija"),
        });
        return Ok(lijecnici);
    }
}
