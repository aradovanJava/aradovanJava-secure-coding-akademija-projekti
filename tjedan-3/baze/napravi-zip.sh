#!/usr/bin/env bash
# Gradi paket za polaznike: dist/sigurnost-baza-podataka.zip (BEZ mape rjesenje/), s demo aplikacijama.
set -euo pipefail
cd "$(dirname "$0")"

IME=sigurnost-baza-podataka
STAGE="dist/stage/$IME"
rm -rf dist
mkdir -p "$STAGE/backup" "$STAGE/audit" "$STAGE/skripte/postavljanje"

cp docker-compose.yml .env.primjer README.md ZADACI.md "$STAGE/"
cp skripte/*.sh skripte/provjera.sql "$STAGE/skripte/"
cp skripte/postavljanje/*.sql "$STAGE/skripte/postavljanje/"
touch "$STAGE/backup/.gitkeep" "$STAGE/audit/.gitkeep"
# Demo „Aplikacija i baza” (Python, Java, C#) – bez build ostataka i lokalnih okruženja.
cp -r aplikacija "$STAGE/aplikacija"
find "$STAGE/aplikacija" \( -name target -o -name bin -o -name obj -o -name .venv -o -name __pycache__ \
  -o -name .ruff_cache -o -name .idea -o -name .vs \) -type d -prune -exec rm -rf {} +

# Sigurnosna provjera: rješenje i lokalne tajne ne smiju završiti u paketu.
if find "$STAGE" -path '*rjesenje*' -o -name '.env' | grep -q .; then
  echo "GREŠKA: paket sadrži rjesenje/ ili .env" >&2
  exit 1
fi

(cd dist/stage && zip -q -r -X "../$IME.zip" "$IME")
rm -rf dist/stage
echo "Paket: $(pwd)/dist/$IME.zip"
unzip -l "dist/$IME.zip"
