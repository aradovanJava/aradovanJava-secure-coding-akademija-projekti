#!/usr/bin/env bash
# SAST – statička analiza izvornog koda.
#  * Semgrep (OWASP Top 10 + pravila za jezik) – oba stacka
#  * Java: SpotBugs + Find Security Bugs (profil -Psast iz pom.xml)
#  * .NET: Roslyn analizatori (Microsoft.CodeAnalysis.NetAnalyzers) s AnalysisMode=All
# Skripta NE odlučuje o prolazu – to radi ci/gate.py. Ovdje samo nastaju izvještaji.
source "$(dirname "$0")/zajednicko.sh"

# ---------- Semgrep ----------
# Pravila iz registra (semgrep.dev, bez prijave) + vlastita regresijska pravila projekta (ci/semgrep/).
if [ "$STACK" = java ]; then
  SEMGREP_PRAVILA="${SEMGREP_PRAVILA:-p/owasp-top-ten p/java ci/semgrep}"
else
  SEMGREP_PRAVILA="${SEMGREP_PRAVILA:-p/owasp-top-ten p/csharp ci/semgrep}"
fi
if [ ! -x "$ALATI/semgrep/bin/semgrep" ]; then
  python3 -m venv "$ALATI/semgrep"
  "$ALATI/semgrep/bin/pip" install -q "semgrep==$SEMGREP_VERZIJA"
fi
args=()
for p in $SEMGREP_PRAVILA; do args+=(--config "$p"); done
echo "Semgrep $SEMGREP_VERZIJA, pravila: $SEMGREP_PRAVILA"
# Datoteke koje se ne analiziraju: .semgrepignore (testovi, build izlazi, izvještaji).
"$ALATI/semgrep/bin/semgrep" scan "${args[@]}" --metrics=off --disable-version-check \
  --json-output="$IZVJESTAJI/semgrep.json" --sarif-output="$IZVJESTAJI/semgrep.sarif" .

# ---------- Java: SpotBugs + Find Security Bugs ----------
if [ "$STACK" = java ]; then
  # failOnError=false: nalaze ocjenjuje gate; ovdje samo XML + SARIF izvještaj.
  "${MVN[@]}" -Psast -DskipTests compile spotbugs:spotbugs \
    -Dspotbugs.sarifOutput=true -Dspotbugs.failOnError=false
  cp target/spotbugsXml.xml "$IZVJESTAJI/spotbugs.xml"
  [ -f target/spotbugsSarif.json ] && cp target/spotbugsSarif.json "$IZVJESTAJI/spotbugs.sarif"
fi

# ---------- .NET: Roslyn analizatori ----------
if [ "$STACK" = dotnet ]; then
  # AnalysisMode=All uključuje SVA CA pravila (i sigurnosna CA2xxx/CA3xxx/CA5xxx s analizom toka podataka).
  # ErrorLog zapisuje sve upozorenje u SARIF 2.1 (zarez u vrijednosti mora biti %2C).
  dotnet build "$API_PROJEKT" -c Release --no-incremental \
    -p:AnalysisMode=All -p:TreatWarningsAsErrors=false \
    "-p:ErrorLog=$IZVJESTAJI/roslyn.sarif%2Cversion=2.1" \
    -v:quiet "-clp:NoSummary;ErrorsOnly"
fi

ls -l "$IZVJESTAJI"
