#!/usr/bin/env bash
# Provjera demo aplikacije za jedan stack:
#   1) ranjiva verzija: funkcionalni testovi prolaze, a za svaku ranjivost barem jedan sigurnosni test pada;
#   2) rješenje: svi testovi prolaze.
set -euo pipefail
STACK="$1"
DEMO="$(cd "$(dirname "$0")/.." && pwd)"
RAD="${RUNNER_TEMP:-/tmp}/knjiznica-$STACK"
rm -rf "$RAD" && mkdir -p "$RAD"

python3 "$DEMO/generiraj.py" --stack "$STACK" --mode ranjivo --dest "$RAD/ranjivo"
python3 "$DEMO/generiraj.py" --stack "$STACK" --mode ranjivo --s-testovima --dest "$RAD/ranjivo-t"
python3 "$DEMO/generiraj.py" --stack "$STACK" --mode rjesenje --dest "$RAD/rjesenje"

case "$STACK" in
  java)
    (cd "$RAD/ranjivo" && mvn -B -ntp -q test -Dgroups=funkcionalni)
    (cd "$RAD/ranjivo-t" && mvn -B -ntp test -Dgroups=sigurnosni -Dmaven.test.failure.ignore=true)
    python3 "$DEMO/ci/sazetak.py" --stack java --ocekivano ranjivo "$RAD"/ranjivo-t/target/surefire-reports/TEST-*.xml
    (cd "$RAD/rjesenje" && mvn -B -ntp test)
    python3 "$DEMO/ci/sazetak.py" --stack java --ocekivano rjesenje "$RAD"/rjesenje/target/surefire-reports/TEST-*.xml
    ;;
  dotnet)
    (cd "$RAD/ranjivo" && dotnet test Knjiznica.sln --filter "Category=Funkcionalni")
    (cd "$RAD/ranjivo-t" && dotnet test Knjiznica.sln --filter "Category=Sigurnosni" \
        --logger "trx;LogFileName=sigurnosni.trx" --results-directory "$RAD/trx-ranjivo" || true)
    python3 "$DEMO/ci/sazetak.py" --stack dotnet --ocekivano ranjivo "$RAD"/trx-ranjivo/*.trx
    (cd "$RAD/rjesenje" && dotnet test Knjiznica.sln --logger "trx;LogFileName=svi.trx" --results-directory "$RAD/trx-rjesenje")
    python3 "$DEMO/ci/sazetak.py" --stack dotnet --ocekivano rjesenje "$RAD"/trx-rjesenje/*.trx
    ;;
  python)
    python3 -m venv "$RAD/venv-ranjivo" && "$RAD/venv-ranjivo/bin/pip" install -q -r "$RAD/ranjivo/requirements-dev.txt"
    (cd "$RAD/ranjivo" && "$RAD/venv-ranjivo/bin/python" -m pytest -q -m funkcionalni)
    (cd "$RAD/ranjivo-t" && "$RAD/venv-ranjivo/bin/python" -m pytest -q tests/sigurnosni --junitxml="$RAD/ranjivo.xml" || true)
    python3 "$DEMO/ci/sazetak.py" --stack python --ocekivano ranjivo "$RAD/ranjivo.xml"
    python3 -m venv "$RAD/venv-rjesenje" && "$RAD/venv-rjesenje/bin/pip" install -q -r "$RAD/rjesenje/requirements-dev.txt"
    (cd "$RAD/rjesenje" && "$RAD/venv-rjesenje/bin/python" -m pytest -q --junitxml="$RAD/rjesenje.xml")
    python3 "$DEMO/ci/sazetak.py" --stack python --ocekivano rjesenje "$RAD/rjesenje.xml"
    ;;
  *) echo "nepoznat stack: $STACK" >&2; exit 2 ;;
esac
