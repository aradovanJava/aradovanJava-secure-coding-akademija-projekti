using Knjiznica.Api.Infrastruktura;

namespace Knjiznica.Api.Posudbe;

/// <summary>Članarina je istekla.</summary>
public sealed class ClanarinaIsteklaException(string poruka) : Exception(poruka);

/// <summary>Provjera članarine prije posudbe.</summary>
public sealed class ClanarinaServis(Baza baza)
{
    public void Provjeri(long korisnikId)
    {
        var status = baza.Jedan("SELECT clanarina FROM korisnici WHERE id = $id", ("$id", korisnikId))?["clanarina"] as string;
        if (status == "AKTIVNA")
        {
            return;
        }
        if (status == "ISTEKLA")
        {
            throw new ClanarinaIsteklaException("Članarina je istekla.");
        }
        throw new InvalidOperationException($"Nepoznat status članarine: {status}");
    }
}
