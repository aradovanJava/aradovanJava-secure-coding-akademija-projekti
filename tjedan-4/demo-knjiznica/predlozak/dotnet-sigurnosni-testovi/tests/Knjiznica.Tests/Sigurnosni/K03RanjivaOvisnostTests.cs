using System.Net;
using System.Text;
using Knjiznica.Tests.Infrastruktura;
using Xunit;

namespace Knjiznica.Tests.Sigurnosni;

/// <summary>K03 – A03 Software Supply Chain Failures: YamlDotNet &lt; 5.0.0 (GHSA-rpch-cqj9-h65r) stvara proizvoljne tipove iz tagova.</summary>
[Trait("Category", "Sigurnosni")]
[Trait("Ranjivost", "K03")]
public sealed class K03RanjivaOvisnostTests(KnjiznicaApp app) : IClassFixture<KnjiznicaApp>
{
    [Fact]
    public void KoristiSeAzuriranaVerzijaYamlDotNet()
    {
        // Verzija s kojom je API projekt preveden (16.x ima AssemblyVersion 16.0.0.0).
        var verzija = typeof(Program).Assembly.GetReferencedAssemblies().Single(a => a.Name == "YamlDotNet").Version!;
        Assert.True(verzija.Major >= 16, $"YamlDotNet {verzija} – potrebna je verzija 16.0 ili novija.");
    }

    [Fact]
    public async Task YamlSOznakomTipaSeOdbija()
    {
        // Tag !System.Text.StringBuilder traži od parsera da stvori .NET objekt; siguran parser takav dokument odbija.
        const string katalog = "- naslov: Proba\n  autor: Netko\n  godina: 2001\n  dodatno: !System.Text.StringBuilder {}\n";
        var klijent = await app.KlijentZaAsync("knjiznicar");
        var odgovor = await klijent.PostAsync("/api/katalog/uvoz", new StringContent(katalog, Encoding.UTF8, "application/yaml"));
        Assert.Equal(HttpStatusCode.BadRequest, odgovor.StatusCode);
    }
}
