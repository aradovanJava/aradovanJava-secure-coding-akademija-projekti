using System.Net;
using Xunit;

namespace Ulaznica.Tests.Skriveno;

/// <summary>S01 – IDOR: kupac ne smije stornirati tuđu narudžbu.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S01")]
public sealed class S01StornoTudeNarudzbeTests
{
    [Fact]
    public async Task MarkoNeMozeStorniratiAninuNarudzbu()
    {
        await using var app = new SkrivenoApp();
        var marko = await app.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await marko.DeleteAsync("/api/narudzbe/1");

        Assert.True(odgovor.StatusCode is HttpStatusCode.NotFound or HttpStatusCode.Forbidden,
            $"Očekivano 403 ili 404, dobiveno {(int)odgovor.StatusCode}.");
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");
        var moje = await SkrivenoApp.Json(await ana.GetAsync("/api/narudzbe/moje"));
        Assert.Contains(moje.EnumerateArray(), n => n.GetProperty("id").GetInt64() == 1);
    }
}
