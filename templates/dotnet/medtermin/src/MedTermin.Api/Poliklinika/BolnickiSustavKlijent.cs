namespace MedTermin.Api.Poliklinika;

/// <summary>
/// Klijent bolničkog informacijskog sustava (BIS): termin rezerviran u poliklinici upisuje se i u raspored
/// bolnice. U lokalnom okruženju poziv se simulira uz uobičajeno mrežno kašnjenje.
/// </summary>
public sealed class BolnickiSustavKlijent(ILogger<BolnickiSustavKlijent> logger)
{
    private static readonly TimeSpan Kasnjenje = TimeSpan.FromMilliseconds(150);

    public async Task RezervirajTerminAsync(long terminId, string pacijent, CancellationToken cancellationToken)
    {
        await Task.Delay(Kasnjenje, cancellationToken);
        logger.LogInformation("BIS: termin {TerminId} upisan za pacijenta {Pacijent}", terminId, pacijent);
    }
}
