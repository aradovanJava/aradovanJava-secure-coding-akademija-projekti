using System.Net;
using System.Net.Http.Json;
using Knjiznica.Tests.Infrastruktura;
using Xunit;

namespace Knjiznica.Tests.Sigurnosni;

/// <summary>K06 – A06 Insecure Design: produljenje posudbe bez poslovnih ograničenja (CWE-840, CWE-20).</summary>
[Trait("Category", "Sigurnosni")]
[Trait("Ranjivost", "K06")]
public sealed class K06ProduljenjeTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    [Theory]
    [InlineData(365)]
    [InlineData(-30)]
    [InlineData(0)]
    public async Task NeispravanBrojDanaVraca400(int dana)
    {
        var ana = await app.KlijentZaAsync("ana");
        var prije = await Rok(ana, 3);
        var odgovor = await ana.PostAsJsonAsync("/api/posudbe/3/produzi", new { dana });
        Assert.Equal(HttpStatusCode.BadRequest, odgovor.StatusCode);
        Assert.Equal(prije, await Rok(ana, 3));
    }

    [Fact]
    public async Task NajviseDvaProduljenja()
    {
        var ana = await app.KlijentZaAsync("ana");
        var statusi = new List<HttpStatusCode>();
        for (var i = 0; i < 3; i++)
        {
            statusi.Add((await ana.PostAsJsonAsync("/api/posudbe/2/produzi", new { dana = 7 })).StatusCode);
        }
        Assert.Equal(new[] { HttpStatusCode.OK, HttpStatusCode.OK, HttpStatusCode.Conflict }, statusi);
    }

    private static async Task<string> Rok(HttpClient klijent, long posudbaId)
    {
        var json = await (await klijent.GetAsync("/api/posudbe")).CitajJsonAsync();
        return json.EnumerateArray().Single(p => p.GetProperty("id").GetInt64() == posudbaId).GetProperty("rok").GetString()!;
    }
}
