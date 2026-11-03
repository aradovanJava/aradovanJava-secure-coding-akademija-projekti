#!/usr/bin/env bash
# Pokreće sve testove generiranog projekta i sprema rezultate (JUnit XML / TRX) u zadanu mapu.
# Uporaba: run_tests.sh <java|dotnet|python> <projektna-mapa> <mapa-za-rezultate>
# Izlazni kod ≠ 0 samo ako build (kompilacija) ne uspije; pali testovi su očekivani.
set -uo pipefail
stack=$1; dir=$2; res=$3
mkdir -p "$res"
log="$res/build.log"
annotate() {  # prvih nekoliko grešaka kompilacije kao GitHub anotacije
  grep -E "$1" "$log" | head -8 | while IFS= read -r l; do echo "::error title=Build ($stack)::${l:0:400}"; done
  echo "----- zadnjih 40 redaka build loga -----"; tail -40 "$log"
}
if [ "$stack" = "java" ]; then
  cd "$dir" || exit 2
  chmod +x mvnw 2>/dev/null || true
  ./mvnw -B -ntp test -Dmaven.test.failure.ignore=true >"$log" 2>&1
  rc=$?
  cp -r target/surefire-reports "$res/" 2>/dev/null || true
  cp target/site/jacoco/jacoco.xml "$res/" 2>/dev/null || true
  if [ $rc -ne 0 ]; then annotate "\[ERROR\].*\.java|COMPILATION ERROR|BUILD FAILURE|APPLICATION FAILED|Caused by"; exit 1; fi
elif [ "$stack" = "python" ]; then
  cd "$dir" || exit 2
  py=${PYTHON:-python3}
  { "$py" -m venv .venv && .venv/bin/python -m pip install -q --disable-pip-version-check -r requirements-dev.txt; } >"$log" 2>&1
  if [ $? -ne 0 ]; then annotate "ERROR|Error|error:"; exit 1; fi
  # pokrivenost: izvor je zadan u pyproject.toml ([tool.coverage.run] source)
  .venv/bin/python -m pytest -p no:cacheprovider -q --junitxml="$res/TEST-pytest.xml" -o junit_family=xunit2 \
     --cov --cov-report=xml:"$res/coverage.xml" >>"$log" 2>&1 || true
  if [ ! -s "$res/TEST-pytest.xml" ]; then annotate "Error|error|Traceback"; exit 1; fi
else
  cd "$dir" || exit 2
  sln=$(ls *.sln | head -1)
  dotnet build "$sln" -c Debug -nologo >"$log" 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then annotate "error [A-Z]+[0-9]+"; exit 1; fi
  dotnet test "$sln" --no-build -nologo --logger "trx;LogFileName=rezultati.trx" --results-directory "$res" \
     --collect:"XPlat Code Coverage" >>"$log" 2>&1 || true
  if ! ls "$res"/*.trx >/dev/null 2>&1; then annotate "error|Exception|crash"; exit 1; fi
fi
exit 0
