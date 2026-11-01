#!/usr/bin/env bash
# SCA – analiza ovisnosti (biblioteka trećih strana).
#  1. SBOM (CycloneDX JSON) – popis svih ovisnosti, uključujući tranzitivne
#  2. OSV-Scanner nad SBOM-om (baza osv.dev: GHSA, NVD, …)
#  3. .NET: dotnet list package --vulnerable --include-transitive (NuGet audit)
source "$(dirname "$0")/zajednicko.sh"

# ---------- 1. SBOM ----------
if [ "$STACK" = java ]; then
  # Profil -Psca iz pom.xml (cyclonedx-maven-plugin); test ovisnosti nisu uključene.
  "${MVN[@]}" -Psca -DskipTests cyclonedx:makeAggregateBom
  cp target/bom.json "$IZVJESTAJI/sbom.cdx.json"
else
  dotnet restore "$SLN"
  if [ ! -x "$ALATI/dotnet/dotnet-CycloneDX" ]; then
    dotnet tool install --tool-path "$ALATI/dotnet" CycloneDX --version "$CYCLONEDX_DOTNET_VERZIJA"
  fi
  "$ALATI/dotnet/dotnet-CycloneDX" "$API_PROJEKT" -o "$IZVJESTAJI" -fn sbom.cdx.json -F Json \
    || "$ALATI/dotnet/dotnet-CycloneDX" "$API_PROJEKT" -o "$IZVJESTAJI" -fn sbom.cdx.json -j
fi

# ---------- 2. OSV-Scanner ----------
OSV="$ALATI/osv-scanner-$OSV_SCANNER_VERZIJA"
if [ ! -x "$OSV" ]; then
  base="https://github.com/google/osv-scanner/releases/download/v$OSV_SCANNER_VERZIJA"
  preuzmi "$base/osv-scanner_linux_amd64" "$OSV" "$base/osv-scanner_SHA256SUMS"
  chmod +x "$OSV"
fi
# Izlazni kod: 0 = nema nalaza, 1 = ima nalaza (gate odlučuje), ostalo = greška alata.
osv() { # format odrediste
  local rc=0
  "$OSV" scan source --config osv-scanner.toml -L "$IZVJESTAJI/sbom.cdx.json" --format "$1" > "$2" || rc=$?
  if [ "$rc" -gt 1 ]; then echo "::error::OSV-Scanner nije uspio (izlazni kod $rc)"; exit "$rc"; fi
}
osv json "$IZVJESTAJI/osv.json"
osv sarif "$IZVJESTAJI/osv.sarif"

# ---------- 3. .NET: NuGet audit ----------
if [ "$STACK" = dotnet ]; then
  dotnet list "$SLN" package --vulnerable --include-transitive --format json > "$IZVJESTAJI/nuget-audit.json"
  python3 ci/sarif.py nuget "$IZVJESTAJI/nuget-audit.json" "$IZVJESTAJI/nuget-audit.sarif"
fi

ls -l "$IZVJESTAJI"
