using System.Net;
using System.Text;
using MedTermin.Tests.Infrastruktura;
using Xunit;

namespace MedTermin.Tests.Funkcionalno;

[Trait("Category", "Funkcionalno")]
public sealed class NalaziTests(MedTerminFactory factory) : IClassFixture<MedTerminFactory>
{
    [Fact]
    public async Task MojiNalaziSadrzeSamoVlastiteNalaze()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var nalazi = await (await klijent.GetAsync("/api/nalazi/moji")).CitajJsonAsync();

        var nalaz = Assert.Single(nalazi.EnumerateArray());
        Assert.Equal("Krvna slika", nalaz.GetProperty("naziv").GetString());
        Assert.Equal("nalaz-ana-krvna-slika.txt", nalaz.GetProperty("datoteka").GetString());
    }

    [Fact]
    public async Task PreuzimanjeVlastiteDatoteke()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var odgovor = await klijent.GetAsync("/api/nalazi/preuzmi?datoteka=nalaz-ana-krvna-slika.txt");

        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        var sadrzaj = await odgovor.Content.ReadAsStringAsync();
        Assert.Contains("Nalaz: Krvna slika", sadrzaj);
        Assert.Contains("Hemoglobin", sadrzaj);
    }

    [Fact]
    public async Task NalazUJsonFormatu()
    {
        var klijent = await factory.KlijentZaAsync("marko", "Marko12345!");

        var odgovor = await klijent.GetAsync("/api/nalazi/2?format=json");

        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        var json = await odgovor.CitajJsonAsync();
        Assert.Equal(2, json.GetProperty("id").GetInt64());
        Assert.Equal("RTG kralježnice", json.GetProperty("naziv").GetString());
        Assert.Contains("fizikalna terapija", json.GetProperty("sadrzaj").GetString());
    }

    [Fact]
    public async Task NalazUPdfFormatu()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var odgovor = await klijent.GetAsync("/api/nalazi/1?format=pdf");

        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        Assert.Equal("application/pdf", odgovor.Content.Headers.ContentType?.MediaType);
        var bajtovi = await odgovor.Content.ReadAsByteArrayAsync();
        Assert.StartsWith("%PDF-", Encoding.ASCII.GetString(bajtovi, 0, 5));
        Assert.Contains("Hemoglobin", Encoding.ASCII.GetString(bajtovi));
    }

    [Fact]
    public async Task AdministratorVidiSveNalaze()
    {
        var klijent = await factory.KlijentZaAsync("admin", "Admin12345!");

        var odgovor = await klijent.GetAsync("/api/nalazi/1?format=json");

        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
    }
}
