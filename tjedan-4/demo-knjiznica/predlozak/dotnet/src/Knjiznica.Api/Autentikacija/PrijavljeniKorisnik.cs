namespace Knjiznica.Api.Autentikacija;

/// <summary>Korisnik kojeg je <see cref="AutentikacijaMiddleware"/> prepoznao iz zaglavlja Authorization: Bearer ...</summary>
public sealed record PrijavljeniKorisnik(long Id, string KorisnickoIme, string Uloga)
{
    public bool JeKnjiznicar => Uloga == "KNJIZNICAR";
}

public static class PrijavljeniKorisnikExtensions
{
    internal const string Kljuc = "prijavljeniKorisnik";

    /// <summary>Prijavljeni korisnik ili <c>null</c> ako zahtjev nema valjan token.</summary>
    public static PrijavljeniKorisnik? Korisnik(this HttpContext context) =>
        context.Items.TryGetValue(Kljuc, out var k) ? k as PrijavljeniKorisnik : null;
}
