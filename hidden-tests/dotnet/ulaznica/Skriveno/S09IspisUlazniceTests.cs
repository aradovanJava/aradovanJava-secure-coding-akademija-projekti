using System.Net;
using System.Net.Http.Json;
using Xunit;

namespace Ulaznica.Tests.Skriveno;

/// <summary>S09 – pohranjeni XSS na HTML ulaznici.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S09")]
public sealed class S09IspisUlazniceTests
{
    [Fact]
    public async Task ImeNaUlazniciSePrikazujeKaoTekst()
    {
        await using var app = new SkrivenoApp();
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");
        var stvaranje = await ana.PostAsJsonAsync("/api/narudzbe", new
        {
            dogadjajId = 3,
            kolicina = 1,
            imeNaUlaznici = "<script>alert('x')</script><img src=x onerror=alert(1)>",
            oib = "48291736504",
        });
        Assert.Equal(HttpStatusCode.Created, stvaranje.StatusCode);
        var id = (await SkrivenoApp.Json(stvaranje)).GetProperty("id").GetInt64();

        var ispis = await ana.GetAsync($"/ispis/narudzbe/{id}");
        var html = await ispis.Content.ReadAsStringAsync();

        Assert.Equal(HttpStatusCode.OK, ispis.StatusCode);
        Assert.DoesNotContain("<script>alert('x')</script>", html);
        Assert.DoesNotContain("<img src=x onerror", html);
    }
}
