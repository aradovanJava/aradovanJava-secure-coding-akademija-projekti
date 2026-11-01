using System.Net;
using Xunit;

namespace Kadrovska.Tests.Skriveno;

/// <summary>S13 – greška pri obradi formata ne smije otvoriti pristup tuđoj platnoj listi.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S13")]
public sealed class S13PristupPlatnojListiTests
{
    [Theory]
    [InlineData("xml")]
    [InlineData("")]
    public async Task TudjaPlatnaListaSNepoznatimFormatomNijeDostupna(string format)
    {
        await using var app = new SkrivenoApp();
        var marko = await app.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await marko.GetAsync($"/api/platne-liste/1?format={format}");
        var tijelo = await odgovor.Content.ReadAsStringAsync();

        Assert.True(odgovor.StatusCode is HttpStatusCode.BadRequest or HttpStatusCode.Forbidden or HttpStatusCode.NotFound,
            $"Očekivano 400, 403 ili 404, dobiveno {(int)odgovor.StatusCode}.");
        Assert.DoesNotContain("Bruto", tijelo);
        Assert.DoesNotContain("1512.00", tijelo);
        Assert.DoesNotContain("Exception", tijelo);
        Assert.DoesNotContain("   at ", tijelo);
        Assert.DoesNotContain("at Kadrovska.", tijelo);
    }
}
