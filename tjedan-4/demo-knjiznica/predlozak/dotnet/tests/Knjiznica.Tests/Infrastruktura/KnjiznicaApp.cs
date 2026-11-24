using System.Collections.Concurrent;
using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Logging;
using Xunit;

namespace Knjiznica.Tests.Infrastruktura;

/// <summary>
/// Pokreće cijelu aplikaciju u memoriji (TestServer). Svaka instanca ima svoju bazu sa svježim početnim
/// podacima, pa testne klase ne dijele stanje. Zapisi u dnevnik aplikacije dostupni su u <see cref="Zapisi"/>.
/// </summary>
public sealed class KnjiznicaApp : WebApplicationFactory<Program>
{
    public static readonly IReadOnlyDictionary<string, string> Lozinke = new Dictionary<string, string>
    {
        ["ana"] = "Ana123!",
        ["marko"] = "Marko123!",
        ["iva"] = "Iva123!",
        ["knjiznicar"] = "Knjiga123!",
    };

    private readonly TestniZapisnik _zapisnik = new();

    /// <summary>Poruke koje je aplikacija zapisala u dnevnik (samo kategorije Knjiznica.*).</summary>
    public ConcurrentQueue<(LogLevel Razina, string Poruka)> Zapisi => _zapisnik.Zapisi;

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Development");
        builder.ConfigureLogging(logging => logging.AddProvider(_zapisnik));
    }

    /// <summary>Klijent koji svakom zahtjevu dodaje zaglavlje Authorization: Bearer &lt;token&gt;.</summary>
    public async Task<HttpClient> KlijentZaAsync(string korisnik)
    {
        var klijent = CreateClient();
        var odgovor = await klijent.PostAsJsonAsync("/api/prijava", new { korisnickoIme = korisnik, lozinka = Lozinke[korisnik] });
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        var token = (await odgovor.CitajJsonAsync()).GetProperty("token").GetString()!;
        klijent.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        return klijent;
    }

    private sealed class TestniZapisnik : ILoggerProvider
    {
        public ConcurrentQueue<(LogLevel Razina, string Poruka)> Zapisi { get; } = new();

        public ILogger CreateLogger(string kategorija) => new Zapisnik(this, kategorija);

        public void Dispose()
        {
        }

        private sealed class Zapisnik(TestniZapisnik vlasnik, string kategorija) : ILogger
        {
            public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;

            public bool IsEnabled(LogLevel logLevel) => true;

            public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception,
                Func<TState, Exception?, string> formatter)
            {
                if (kategorija.StartsWith("Knjiznica", StringComparison.Ordinal))
                {
                    vlasnik.Zapisi.Enqueue((logLevel, formatter(state, exception)));
                }
            }
        }
    }
}

public static class TestPomoc
{
    public static async Task<JsonElement> CitajJsonAsync(this HttpResponseMessage odgovor)
    {
        var tekst = await odgovor.Content.ReadAsStringAsync();
        using var dokument = JsonDocument.Parse(tekst);
        return dokument.RootElement.Clone();
    }
}
