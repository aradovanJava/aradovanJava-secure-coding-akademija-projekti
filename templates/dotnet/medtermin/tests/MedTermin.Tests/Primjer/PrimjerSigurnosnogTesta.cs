using System.Net;
using MedTermin.Tests.Infrastruktura;
using Xunit;

namespace MedTermin.Tests.Primjer;

/// <summary>
/// Primjer sigurnosnog testa: opisuje očekivano sigurno ponašanje i provjerava ga preko HTTP-a.
/// Svoje testove piši po istom uzorku u zasebnoj mapi (npr. <c>tests/MedTermin.Tests/Sigurnost/</c>):
/// pripremi stanje (Arrange), pošalji zahtjev (Act) i provjeri odgovor i stanje sustava (Assert).
/// </summary>
[Trait("Category", "Primjer")]
public sealed class PrimjerSigurnosnogTesta(MedTerminFactory factory) : IClassFixture<MedTerminFactory>
{
    [Fact]
    public async Task ZasticeniEndpointBezTokenaVraca401()
    {
        // Arrange – klijent bez tokena i bez kolačića
        var klijent = factory.CreateClient();

        // Act
        var odgovor = await klijent.GetAsync("/api/rezervacije/moje");

        // Assert – pristup je odbijen, a odgovor ne sadrži podatke
        Assert.Equal(HttpStatusCode.Unauthorized, odgovor.StatusCode);
        var json = await odgovor.CitajJsonAsync();
        Assert.Equal("Potrebna je prijava.", json.GetProperty("greska").GetString());
    }
}
