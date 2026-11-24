using Knjiznica.Api.Infrastruktura;

namespace Knjiznica.Api.Autentikacija;

/// <summary>Iz zaglavlja Authorization: Bearer ... prepoznaje korisnika i sprema ga u HttpContext.Items.</summary>
public sealed class AutentikacijaMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context, Tokeni tokeni, Baza baza)
    {
        var zaglavlje = context.Request.Headers.Authorization.ToString();
        if (zaglavlje.StartsWith("Bearer ", StringComparison.Ordinal))
        {
            var korisnikId = tokeni.KorisnikId(zaglavlje["Bearer ".Length..].Trim());
            if (korisnikId is not null)
            {
                var red = baza.Jedan("SELECT id, korisnicko_ime, uloga FROM korisnici WHERE id = $id", ("$id", korisnikId));
                if (red is not null)
                {
                    context.Items[PrijavljeniKorisnikExtensions.Kljuc] = new PrijavljeniKorisnik(
                        (long)red["id"]!, (string)red["korisnicko_ime"]!, (string)red["uloga"]!);
                }
            }
        }
        await next(context);
    }
}
