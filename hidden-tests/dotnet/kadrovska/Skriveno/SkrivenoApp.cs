using System.Collections.Concurrent;
using System.Net;
using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Xunit;

namespace Kadrovska.Tests.Skriveno;

/// <summary>
/// Nastavnička tvornica aplikacije za skrivene testove (neovisna o javnim testnim pomoćnim klasama).
/// Svaka instanca: vlastita in-memory baza s poznatim connection stringom, vlastite privremene mape
/// i hvatanje cijelog loga.
/// </summary>
public sealed class SkrivenoApp : WebApplicationFactory<Program>
{
    public SkrivenoApp()
    {
        Mapa = Path.Combine(Path.GetTempPath(), "skriveno-kadrovska", Guid.NewGuid().ToString("N"));
        DirektorijDokumenata = Path.Combine(Mapa, "pohrana");
        DirektorijPoste = Path.Combine(Mapa, "posta");
        Directory.CreateDirectory(Mapa);
        ConnectionString = $"Data Source=skriveno-kadrovska-{Guid.NewGuid():N};Mode=Memory;Cache=Shared";
    }

    public string Mapa { get; }
    public string DirektorijDokumenata { get; }
    public string DirektorijPoste { get; }
    public string ConnectionString { get; }
    public SkrivenoLog Log { get; } = new();

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Development");
        builder.ConfigureAppConfiguration((_, konfiguracija) => konfiguracija.AddInMemoryCollection(
            new Dictionary<string, string?>
            {
                ["App:StorageDir"] = DirektorijDokumenata,
                ["App:MailboxDir"] = DirektorijPoste,
                ["ConnectionStrings:Default"] = ConnectionString,
            }));
        builder.ConfigureLogging(logging => logging.AddProvider(Log));
    }

    /// <summary>Klijent bez praćenja preusmjeravanja i bez automatskih kolačića.</summary>
    public HttpClient Klijent() =>
        CreateClient(new WebApplicationFactoryClientOptions { AllowAutoRedirect = false, HandleCookies = false });

    public async Task<string> TokenAsync(string username, string password)
    {
        var odgovor = await Klijent().PostAsJsonAsync("/api/auth/login", new { username, password });
        Assert.Equal(HttpStatusCode.OK, odgovor.StatusCode);
        return (await Json(odgovor)).GetProperty("token").GetString()!;
    }

    public async Task<HttpClient> KlijentZaAsync(string username, string password)
    {
        var klijent = Klijent();
        klijent.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", await TokenAsync(username, password));
        return klijent;
    }

    public async Task RegistrirajAsync(string username, string password)
    {
        var odgovor = await Klijent().PostAsJsonAsync("/api/auth/register", new
        {
            username,
            password,
            email = $"{username}@primjer.hr",
            ime = "Skriveni",
            prezime = "Test",
        });
        Assert.Equal(HttpStatusCode.Created, odgovor.StatusCode);
    }

    public static async Task<JsonElement> Json(HttpResponseMessage odgovor)
    {
        var tekst = await odgovor.Content.ReadAsStringAsync();
        using var dokument = JsonDocument.Parse(tekst);
        return dokument.RootElement.Clone();
    }
}

public sealed record SkrivenoLogZapis(LogLevel Razina, string Kategorija, string Poruka);

/// <summary>Hvata sve zapise loga aplikacije u memoriju.</summary>
public sealed class SkrivenoLog : ILoggerProvider
{
    private readonly ConcurrentQueue<SkrivenoLogZapis> _zapisi = new();

    public IReadOnlyList<SkrivenoLogZapis> Zapisi => _zapisi.ToArray();

    public ILogger CreateLogger(string categoryName) => new HvatacLoga(categoryName, _zapisi);

    public void Dispose()
    {
    }

    private sealed class HvatacLoga(string kategorija, ConcurrentQueue<SkrivenoLogZapis> zapisi) : ILogger
    {
        public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;

        public bool IsEnabled(LogLevel logLevel) => logLevel != LogLevel.None;

        public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception,
            Func<TState, Exception?, string> formatter)
        {
            var poruka = formatter(state, exception);
            if (exception is not null)
            {
                poruka += Environment.NewLine + exception;
            }
            zapisi.Enqueue(new SkrivenoLogZapis(logLevel, kategorija, poruka));
        }
    }
}
