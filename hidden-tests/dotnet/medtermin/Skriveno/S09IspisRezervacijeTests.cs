using System.Net;
using System.Net.Http.Json;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S09 – pohranjeni XSS na HTML potvrdi rezervacije.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S09")]
public sealed class S09IspisRezervacijeTests
{
    [Fact]
    public async Task NapomenaSeNaIspisuPrikazujeKaoTekst()
    {
        await using var app = new SkrivenoApp();
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");
        var stvaranje = await ana.PostAsJsonAsync("/api/rezervacije", new
        {
            terminId = 9,
            napomena = "<script>alert('x')</script><img src=x onerror=alert(1)>",
            oib = "48291736504",
        });
        Assert.Equal(HttpStatusCode.Created, stvaranje.StatusCode);
        var id = (await SkrivenoApp.Json(stvaranje)).GetProperty("id").GetInt64();

        var ispis = await ana.GetAsync($"/ispis/rezervacije/{id}");
        var html = await ispis.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.OK, ispis.StatusCode);
        Assert.DoesNotContain("<script>alert('x')</script>", html);
        Assert.DoesNotContain("<img src=x onerror", html);
    }
}
