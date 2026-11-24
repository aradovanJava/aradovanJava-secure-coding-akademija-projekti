using System.Text.Encodings.Web;
using System.Text.Unicode;
using Knjiznica.Api.Autentikacija;
using Knjiznica.Api.Infrastruktura;
using Knjiznica.Api.Posudbe;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

// Hrvatski znakovi (č, ć, đ, š, ž) u JSON odgovorima ostaju čitljivi.
var jsonEncoder = JavaScriptEncoder.Create(
    UnicodeRanges.BasicLatin, UnicodeRanges.Latin1Supplement, UnicodeRanges.LatinExtendedA);

builder.Services
    .AddControllers()
    .AddJsonOptions(options => options.JsonSerializerOptions.Encoder = jsonEncoder)
    .ConfigureApiBehaviorOptions(options => options.InvalidModelStateResponseFactory =
        _ => new BadRequestObjectResult(new { greska = "Neispravan zahtjev." }));

builder.Services.AddSingleton<Baza>();
builder.Services.AddSingleton<Lozinke>();
builder.Services.AddSingleton<Tokeni>();
builder.Services.AddSingleton<ClanarinaServis>();

var app = builder.Build();

PocetniPodaci.Napuni(app.Services);

// @@VULN K05
app.UseDeveloperExceptionPage();
// @@SECURE K05
// Neočekivane greške: detalji samo u dnevniku poslužitelja, klijent dobiva generičku poruku.
app.UseExceptionHandler(greske => greske.Run(async context =>
{
    context.Response.StatusCode = StatusCodes.Status500InternalServerError;
    await context.Response.WriteAsJsonAsync(new { greska = "Došlo je do pogreške." });
}));

// Sigurnosna zaglavlja na svakom odgovoru.
app.Use(async (context, next) =>
{
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["X-Frame-Options"] = "DENY";
    context.Response.Headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'";
    context.Response.Headers["Referrer-Policy"] = "no-referrer";
    context.Response.Headers["Cross-Origin-Resource-Policy"] = "same-origin";
    context.Response.Headers["Cache-Control"] = "no-store";
    await next();
});
// @@END K05

app.UseMiddleware<AutentikacijaMiddleware>();
app.MapControllers();

app.Run();

/// <summary>Omogućuje <c>WebApplicationFactory&lt;Program&gt;</c> u integracijskim testovima.</summary>
public partial class Program
{
}
