using System.Globalization;
using System.Text;
using Knjiznica.Api.Autentikacija;
using Knjiznica.Api.Infrastruktura;
using Microsoft.AspNetCore.Mvc;
using YamlDotNet.Serialization;

namespace Knjiznica.Api.Katalog;

/// <summary>
/// Uvoz kataloga u YAML formatu (samo knjižničar). Primjer tijela (Content-Type: application/yaml):
/// <code>
/// - naslov: Kiklop
///   autor: Ranko Marinković
///   godina: 1965
/// </code>
/// </summary>
[ApiController]
public sealed class KatalogController(Baza baza, ILogger<KatalogController> logger) : ControllerBase
{
    private const int NajvecaVelicina = 100_000;

    [HttpPost("/api/katalog/uvoz")]
    public async Task<IActionResult> Uvoz()
    {
        var korisnik = HttpContext.Korisnik();
        if (korisnik is null)
        {
            return Greska.Neprijavljen();
        }
        if (!korisnik.JeKnjiznicar)
        {
            return Greska.Zabranjeno("Uvoz kataloga dopušten je samo knjižničarima.");
        }
        string yaml;
        using (var citac = new StreamReader(Request.Body, Encoding.UTF8))
        {
            yaml = await citac.ReadToEndAsync(HttpContext.RequestAborted);
        }
        if (yaml.Length == 0 || yaml.Length > NajvecaVelicina)
        {
            return Greska.Neispravno("Katalog je prazan ili prevelik.");
        }

        List<Dictionary<string, object>>? stavke;
        try
        {
            var deserializer = new DeserializerBuilder().Build();
            stavke = deserializer.Deserialize<List<Dictionary<string, object>>>(new StringReader(yaml));
        }
        catch (Exception ex)
        {
            logger.LogInformation("Katalog nije u ispravnom YAML formatu: {Poruka}", ex.Message);
            return Greska.Neispravno("Neispravan YAML.");
        }
        if (stavke is null || stavke.Count == 0)
        {
            return Greska.Neispravno("Očekuje se popis knjiga.");
        }

        var knjige = new List<(string Naslov, string Autor, int Godina)>();
        foreach (var stavka in stavke)
        {
            if (stavka is null
                || !stavka.TryGetValue("naslov", out var n) || n is not string naslov || string.IsNullOrWhiteSpace(naslov)
                || !stavka.TryGetValue("autor", out var a) || a is not string autor || string.IsNullOrWhiteSpace(autor)
                || !stavka.TryGetValue("godina", out var g)
                || !int.TryParse(g as string, NumberStyles.Integer, CultureInfo.InvariantCulture, out var godina))
            {
                return Greska.Neispravno("Neispravna knjiga u katalogu.");
            }
            knjige.Add((naslov.Trim(), autor.Trim(), godina));
        }
        foreach (var k in knjige)
        {
            baza.Umetni("INSERT INTO knjige (naslov, autor, godina) VALUES ($n, $a, $g)",
                ("$n", k.Naslov), ("$a", k.Autor), ("$g", k.Godina));
        }
        return Ok(new { uvezeno = knjige.Count });
    }
}
