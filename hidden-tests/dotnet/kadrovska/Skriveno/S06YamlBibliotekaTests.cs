using System.Net;
using System.Text;
using Xunit;

namespace Kadrovska.Tests.Skriveno;

/// <summary>S06 – ranjiva verzija biblioteke YamlDotNet (GHSA-rpch-cqj9-h65r, &lt; 5.0.0).</summary>
[Trait("Category", "Skriveno")]
[Trait("Slot", "S06")]
public sealed class S06YamlBibliotekaTests
{
    [Fact]
    public void KoristiSeAzuriranaVerzijaYamlDotNet()
    {
        var verzija = typeof(YamlDotNet.Serialization.Deserializer).Assembly.GetName().Version!;

        Assert.True(verzija.Major >= 16, $"YamlDotNet {verzija} – potrebna je verzija 16.0 ili novija.");
    }

    [Fact]
    public async Task YamlSOznakomTipaSeOdbija()
    {
        await using var app = new SkrivenoApp();
        var ana = await app.KlijentZaAsync("ana", "Ana12345!");
        const string yaml = """
            podsjetnik: true
            satiPrije: 24
            kanal: email
            dodatno: !System.Text.StringBuilder {}
            """;

        var odgovor = await ana.PostAsync("/api/postavke", new StringContent(yaml, Encoding.UTF8, "application/yaml"));

        Assert.Equal(HttpStatusCode.BadRequest, odgovor.StatusCode);
    }
}
