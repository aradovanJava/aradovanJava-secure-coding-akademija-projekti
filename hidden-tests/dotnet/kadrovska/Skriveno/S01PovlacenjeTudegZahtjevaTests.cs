using System.Net;
using Xunit;

namespace Kadrovska.Tests.Skriveno;

/// <summary>S01 – IDOR: zaposlenik ne smije povući tuđi zahtjev za godišnji.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S01")]
public sealed class S01PovlacenjeTudegZahtjevaTests
{
    [Fact]
    public async Task MarkoNeMozePovuciAninZahtjev()
    {
        await using var app = new SkrivenoApp();
        var marko = await app.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await marko.DeleteAsync("/api/zahtjevi/1");

        Assert.True(odgovor.StatusCode is HttpStatusCode.NotFound or HttpStatusCode.Forbidden,
            $"Očekivano 403 ili 404, dobiveno {(int)odgovor.StatusCode}.");
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");
        var moji = await SkrivenoApp.Json(await ana.GetAsync("/api/zahtjevi/moji"));
        Assert.Contains(moji.EnumerateArray(), z => z.GetProperty("id").GetInt64() == 1);
    }
}
