using System.Net;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S02 – path traversal kod preuzimanja nalaza.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S02")]
public sealed class S02PreuzimanjeDatotekeTests
{
    [Theory]
    [InlineData("../tajna-ana-{0}.txt")]
    [InlineData("../tajna-{0}.txt")]
    [InlineData("{1}")]
    public async Task DatotekaIzvanPohraneNijeDostupna(string predlozak)
    {
        await using var app = new SkrivenoApp();
        var oznaka = Guid.NewGuid().ToString("N");
        var tajna = $"TAJNO-{Guid.NewGuid():N}";
        File.WriteAllText(Path.Combine(app.Mapa, $"tajna-ana-{oznaka}.txt"), tajna);
        File.WriteAllText(Path.Combine(app.Mapa, $"tajna-{oznaka}.txt"), tajna);
        var apsolutna = Path.Combine(app.Mapa, $"tajna-ana-{oznaka}.txt");
        var datoteka = string.Format(predlozak, oznaka, apsolutna);
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");

        var odgovor = await ana.GetAsync("/api/nalazi/preuzmi?datoteka=" + Uri.EscapeDataString(datoteka));
        var tijelo = await odgovor.Content.ReadAsStringAsync();

        Assert.NotEqual(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.DoesNotContain(tajna, tijelo);
    }
}
