#!/usr/bin/env bash
# Gradi paket za polaznike: dist/devsecops-i-mehanizmi-okvira.zip
# Sadrži devsecops/{README.md,java,dotnet} i okviri/ – BEZ devsecops/test/ (testno stanje i iznimke za MedTermin).
set -euo pipefail
cd "$(dirname "$0")"

IME=devsecops-i-mehanizmi-okvira
STAGE="dist/stage/$IME"
rm -rf dist
mkdir -p "$STAGE/devsecops"

cp devsecops/README.md "$STAGE/devsecops/"
cp -r devsecops/java devsecops/dotnet "$STAGE/devsecops/"
cp -r okviri "$STAGE/okviri"
cat > "$STAGE/PROCITAJ.md" <<'TXT'
# Tjedan 3 – DevSecOps i sigurnosni mehanizmi okvira

- `devsecops/` – predložak CI/CD cjevovoda (testovi, SAST, SCA, tajne, DAST, sigurnosna vrata) za vaš T2 projekt.
  Upute: `devsecops/README.md`.
- `okviri/` – primjeri Spring Security i ASP.NET Core (+ Keycloak) koji zamjenjuju ručne provjere iz T2.
  Upute: `okviri/README.md`.

Što predajete i do kada: stranica „Upute – nadogradnja projekta (Tjedan 3)” na Moodleu.
TXT

# Očisti build ostatke i lokalne tajne.
find "$STAGE" \( -name bin -o -name obj -o -name target -o -name node_modules -o -name .ci-alati -o -name izvjestaji \) -type d -prune -exec rm -rf {} +
find "$STAGE" \( -name '.env' -o -name '*.user' \) -type f -delete

# Sigurnosna provjera: testno stanje i interne iznimke ne smiju u paket.
if find "$STAGE" -path '*/devsecops/test*' -o -name 'prihvaceno-*.txt' -o -path '*rjesenje*' | grep -q .; then
  echo "GREŠKA: paket sadrži devsecops/test, prihvaceno-*.txt ili rjesenje/" >&2
  exit 1
fi

(cd dist/stage && zip -q -r -X "../$IME.zip" "$IME")
rm -rf dist/stage
echo "Paket: $(pwd)/dist/$IME.zip"
unzip -l "dist/$IME.zip" | tail -1
