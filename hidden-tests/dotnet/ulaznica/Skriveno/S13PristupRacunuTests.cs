using System.Net;
using Xunit;

namespace Ulaznica.Tests.Skriveno;

/// <summary>S13 – greška pri obradi formata ne smije otvoriti pristup tuđem računu.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S13")]
public sealed class S13PristupRacunuTests
{
    [Theory]
    [InlineData("xml")]
    [InlineData("")]
    public async Task TudjiRacunSNepoznatimFormatomNijeDostupan(string format)
    {
        await using var app = new SkrivenoApp();
        var marko = await app.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await marko.GetAsync($"/api/racuni/1?format={format}");
        var tijelo = await odgovor.Content.ReadAsStringAsync();

        Assert.True(odgovor.StatusCode is HttpStatusCode.BadRequest or HttpStatusCode.Forbidden or HttpStatusCode.NotFound,
            $"Očekivano 400, 403 ili 404, dobiveno {(int)odgovor.StatusCode}.");
        Assert.DoesNotContain("Ukupno za platiti", tijelo);
        Assert.DoesNotContain("Gibonni", tijelo);
        Assert.DoesNotContain("Exception", tijelo);
        Assert.DoesNotContain("   at ", tijelo);
        Assert.DoesNotContain("at Ulaznica.", tijelo);
    }
}
