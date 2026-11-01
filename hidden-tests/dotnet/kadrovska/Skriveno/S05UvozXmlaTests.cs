using System.Text;
using Xunit;

namespace Kadrovska.Tests.Skriveno;

/// <summary>S05 – XXE: vanjski entiteti u XML-u ne smiju se razrješavati.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S05")]
public sealed class S05UvozXmlaTests
{
    [Fact]
    public async Task VanjskiEntitetNeSmijeProcitatiDatoteku()
    {
        await using var app = new SkrivenoApp();
        var kanarinac = Path.Combine(app.Mapa, $"kanarinac-{Guid.NewGuid():N}.txt");
        var tajna = $"KANARINAC{Guid.NewGuid():N}";
        File.WriteAllText(kanarinac, tajna);
        var uri = new Uri(kanarinac).AbsoluteUri;
        var xml = $"""
            <?xml version="1.0" encoding="utf-8"?>
            <!DOCTYPE edukacije [<!ENTITY e SYSTEM "{uri}">]>
            <edukacije><edukacija><naziv>&e;</naziv><datum>2026-12-03</datum><kapacitet>15</kapacitet></edukacija></edukacije>
            """;
        var voditelj = await app.KlijentZaAsync("voditelj", "Ovlasteni12345!");

        var odgovor = await voditelj.PostAsync("/api/edukacije/uvoz", new StringContent(xml, Encoding.UTF8, "application/xml"));
        var tijelo = await odgovor.Content.ReadAsStringAsync();

        Assert.DoesNotContain(tajna, tijelo);
    }
}
