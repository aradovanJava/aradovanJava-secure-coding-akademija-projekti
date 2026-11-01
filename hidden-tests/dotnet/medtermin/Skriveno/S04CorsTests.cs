using System.Net.Http.Headers;
using Xunit;

namespace MedTermin.Tests.Skriveno;

/// <summary>S04 – CORS ne smije dopustiti proizvoljan origin uz vjerodajnice.</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S04")]
public sealed class S04CorsTests
{
    private const string ZloOrigin = "https://zlo.example";

    private static void ProvjeriBezDozvole(HttpResponseMessage odgovor)
    {
        if (odgovor.Headers.TryGetValues("Access-Control-Allow-Origin", out var vrijednosti))
        {
            foreach (var vrijednost in vrijednosti)
            {
                Assert.NotEqual(ZloOrigin, vrijednost.Trim(), StringComparer.OrdinalIgnoreCase);
                Assert.NotEqual("*", vrijednost.Trim());
            }
        }
    }

    [Fact]
    public async Task ZahtjevSNepoznatogOriginaNeDobivaDozvolu()
    {
        await using var app = new SkrivenoApp();
        var token = await app.TokenAsync("ana", "Ana12345!");
        var zahtjev = new HttpRequestMessage(HttpMethod.Get, "/api/ja");
        zahtjev.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
        zahtjev.Headers.Add("Origin", ZloOrigin);

        var odgovor = await app.Klijent().SendAsync(zahtjev);

        ProvjeriBezDozvole(odgovor);
    }

    [Fact]
    public async Task PreflightSNepoznatogOriginaNeDobivaDozvolu()
    {
        await using var app = new SkrivenoApp();
        var zahtjev = new HttpRequestMessage(HttpMethod.Options, "/api/ja");
        zahtjev.Headers.Add("Origin", ZloOrigin);
        zahtjev.Headers.Add("Access-Control-Request-Method", "GET");
        zahtjev.Headers.Add("Access-Control-Request-Headers", "authorization");

        var odgovor = await app.Klijent().SendAsync(zahtjev);

        ProvjeriBezDozvole(odgovor);
    }
}
