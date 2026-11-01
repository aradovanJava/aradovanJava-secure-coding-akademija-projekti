using System.Net;
using System.Text;
using MedTermin.Tests.Infrastruktura;
using Xunit;

namespace MedTermin.Tests.Funkcionalno;

[Trait("Category", "Funkcionalno")]
public sealed class UvozIPostavkeTests(MedTerminFactory factory) : IClassFixture<MedTerminFactory>
{
    private const string Raspored = """
        <?xml version="1.0" encoding="utf-8"?>
        <termini>
          <termin>
            <lijecnikId>1</lijecnikId>
            <pocetak>2026-12-01T09:00</pocetak>
            <kapacitet>1</kapacitet>
            <napomena>Jutarnji termin</napomena>
          </termin>
          <termin>
            <lijecnikId>2</lijecnikId>
            <pocetak>2026-12-01T10:30</pocetak>
            <kapacitet>2</kapacitet>
            <napomena>Kontrolni pregledi</napomena>
          </termin>
        </termini>
        """;

    private static StringContent Xml(string xml) => new(xml, Encoding.UTF8, "application/xml");

    [Fact]
    public async Task LijecnikUvoziRasporedIzXmla()
    {
        var klijent = await factory.KlijentZaAsync("dr.horvat", "Ovlasteni12345!");

        var odgovor = await klijent.PostAsync("/api/termini/uvoz", Xml(Raspored));

        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        var json = await odgovor.CitajJsonAsync();
        Assert.Equal(2, json.GetProperty("uvezeno").GetInt32());
        var prvi = json.GetProperty("termini")[0];
        Assert.True(prvi.GetProperty("id").GetInt64() > 10);
        Assert.Equal("2026-12-01T09:00", prvi.GetProperty("pocetak").GetString());
        Assert.Equal("Jutarnji termin", prvi.GetProperty("napomena").GetString());
    }

    [Fact]
    public async Task NeispravanXmlVraca400()
    {
        var klijent = await factory.KlijentZaAsync("admin", "Admin12345!");

        var odgovor = await klijent.PostAsync("/api/termini/uvoz", Xml("<termini><termin>"));

        Assert.Equal(HttpStatusCode.BadRequest, odgovor.StatusCode);
    }

    [Fact]
    public async Task PacijentNeMozeUvoziti()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var odgovor = await klijent.PostAsync("/api/termini/uvoz", Xml(Raspored));

        Assert.Equal(HttpStatusCode.Forbidden, odgovor.StatusCode);
    }

    [Fact]
    public async Task PostavkeObavijestiUYamlu()
    {
        var klijent = await factory.KlijentZaAsync("marko", "Marko12345!");
        const string yaml = """
            podsjetnik: true
            satiPrije: 48
            kanal: sms
            """;

        var odgovor = await klijent.PostAsync("/api/postavke", new StringContent(yaml, Encoding.UTF8, "application/yaml"));

        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        var postavke = (await odgovor.CitajJsonAsync()).GetProperty("postavke");
        Assert.True(postavke.GetProperty("podsjetnik").GetBoolean());
        Assert.Equal(48, postavke.GetProperty("satiPrije").GetInt32());
        Assert.Equal("sms", postavke.GetProperty("kanal").GetString());

        var spremljeno = (await (await klijent.GetAsync("/api/postavke")).CitajJsonAsync()).GetProperty("postavke");
        Assert.Equal(48, spremljeno.GetProperty("satiPrije").GetInt32());
    }

    [Fact]
    public async Task NeispravnePostavkeVracaju400()
    {
        var klijent = await factory.KlijentZaAsync("ana", "Ana12345!");

        var odgovor = await klijent.PostAsync("/api/postavke", new StringContent("satiPrije: puno", Encoding.UTF8, "text/plain"));

        Assert.Equal(HttpStatusCode.BadRequest, odgovor.StatusCode);
    }
}
