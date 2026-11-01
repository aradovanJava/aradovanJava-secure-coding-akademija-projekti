using System.Net;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S13 – greška pri obradi formata ne smije otvoriti pristup tuđem nalazu.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S13")]
public sealed class S13PristupNalazuTests
{
    [Theory]
    [InlineData("xml")]
    [InlineData("")]
    public async Task TudjiNalazSNepoznatimFormatomNijeDostupan(string format)
    {
        await using var app = new SkrivenoApp();
        var marko = await app.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await marko.GetAsync($"/api/nalazi/1?format={format}");
        var tijelo = await odgovor.Content.ReadAsStringAsync();

        Assert.True(odgovor.StatusCode is HttpStatusCode.BadRequest or HttpStatusCode.Forbidden or HttpStatusCode.NotFound,
            $"Očekivano 400, 403 ili 404, dobiveno {(int)odgovor.StatusCode}.");
        Assert.DoesNotContain("Hemoglobin", tijelo);
        Assert.DoesNotContain("Krvna slika", tijelo);
        Assert.DoesNotContain("Exception", tijelo);
        Assert.DoesNotContain("   at ", tijelo);
        Assert.DoesNotContain("at MedTermin.", tijelo);
    }
}
