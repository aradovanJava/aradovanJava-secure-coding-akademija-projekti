#!/usr/bin/env bash
# Build + svi testovi + izvještaj o pokrivenosti koda (JaCoCo / Coverlet).
source "$(dirname "$0")/zajednicko.sh"

mkdir -p "$IZVJESTAJI/testovi" "$IZVJESTAJI/pokrivenost"

if [ "$STACK" = java ]; then
  # verify = compile + test (+ JaCoCo report u fazi test) + package
  "${MVN[@]}" verify
  cp -r target/site/jacoco/. "$IZVJESTAJI/pokrivenost/" 2>/dev/null || true
  cp target/surefire-reports/*.xml "$IZVJESTAJI/testovi/" 2>/dev/null || true
  python3 - "$IZVJESTAJI/pokrivenost/jacoco.csv" <<'PY' | while read -r l; do sazetak "$l"; done
import csv, sys
try:
    rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
    m = sum(int(r["LINE_MISSED"]) for r in rows); c = sum(int(r["LINE_COVERED"]) for r in rows)
    print(f"**Pokrivenost redaka (JaCoCo):** {100 * c / max(1, m + c):.1f} % ({c}/{m + c})")
except OSError:
    print("Pokrivenost: nema jacoco.csv")
PY
else
  dotnet test "$SLN" -c Release --collect:"XPlat Code Coverage" \
    --results-directory "$IZVJESTAJI/testovi" --logger "trx;LogFileName=testovi.trx"
  cob=$(find "$IZVJESTAJI/testovi" -name coverage.cobertura.xml | head -1)
  if [ -n "$cob" ]; then
    cp "$cob" "$IZVJESTAJI/pokrivenost/cobertura.xml"
    python3 - "$cob" <<'PY' | while read -r l; do sazetak "$l"; done
import sys, xml.etree.ElementTree as ET
r = ET.parse(sys.argv[1]).getroot()
print(f"**Pokrivenost redaka (Coverlet):** {100 * float(r.get('line-rate', 0)):.1f} % "
      f"({r.get('lines-covered')}/{r.get('lines-valid')})")
PY
  fi
fi
