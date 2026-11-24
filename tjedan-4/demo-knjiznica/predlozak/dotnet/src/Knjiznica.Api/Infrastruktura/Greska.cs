using Microsoft.AspNetCore.Mvc;

namespace Knjiznica.Api.Infrastruktura;

/// <summary>Odgovori s greškom oblika {"greska": "..."}.</summary>
public static class Greska
{
    public static ObjectResult Neprijavljen() => S(401, "Potrebna je prijava.");

    public static ObjectResult NeispravnaPrijava() => S(401, "Neispravno korisničko ime ili lozinka.");

    public static ObjectResult Neispravno(string poruka) => S(400, poruka);

    public static ObjectResult Zabranjeno(string poruka) => S(403, poruka);

    public static ObjectResult NijePronadjeno(string poruka) => S(404, poruka);

    public static ObjectResult Sukob(string poruka) => S(409, poruka);

    private static ObjectResult S(int status, string poruka) => new(new { greska = poruka }) { StatusCode = status };
}
