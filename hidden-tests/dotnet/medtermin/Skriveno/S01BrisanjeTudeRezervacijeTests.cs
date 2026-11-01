using System.Net;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S01 – IDOR: korisnik ne smije obrisati tuđu rezervaciju.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S01")]
public sealed class S01BrisanjeTudeRezervacijeTests
{
    [Fact]
    public async Task MarkoNeMozeObrisatiAninuRezervaciju()
    {
        await using var app = new SkrivenoApp();
        var marko = await app.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await marko.DeleteAsync("/api/rezervacije/1");

        Assert.True(odgovor.StatusCode is HttpStatusCode.NotFound or HttpStatusCode.Forbidden,
            $"Očekivano 403 ili 404, dobiveno {(int)odgovor.StatusCode}.");
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");
        var moje = await SkrivenoApp.Json(await ana.GetAsync("/api/rezervacije/moje"));
        Assert.Contains(moje.EnumerateArray(), r => r.GetProperty("id").GetInt64() == 1);
    }
}
