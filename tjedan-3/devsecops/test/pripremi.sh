#!/usr/bin/env bash
# Test predloška: generira T2 projekt (all-secure / all-vuln), doda DevSecOps predložak i
# napravi git repozitorij – stanje kao kod polaznika nakon kopiranja predloška u svoj projekt.
#   tjedan-3/devsecops/test/pripremi.sh <java|dotnet> <domena> <all-secure|all-vuln> <odredište>
set -euo pipefail
stack=$1; domena=$2; nacin=$3; odr=$4
root=$(cd "$(dirname "$0")/../../.." && pwd)
rm -rf "$odr"
python3 "$root/tools/generate.py" --stack "$stack" --domain "$domena" --mode "$nacin" --dest "$odr"
cp -a "$root/tjedan-3/devsecops/$stack/." "$odr/"
# Iznimke koje bi polaznik s ovim (referentnim) popravkom dodao u ci/prihvaceno.txt – vidi README.
dodatno="$root/tjedan-3/devsecops/test/prihvaceno-$stack-$domena.txt"
[ -f "$dodatno" ] && cat "$dodatno" >> "$odr/ci/prihvaceno.txt"
cd "$odr"
git init -q -b main
git add -A
git -c user.name=ci -c user.email=ci@example.invalid commit -qm "T2 projekt + T3 DevSecOps predložak"
echo "Pripremljeno: $odr ($stack/$domena $nacin)"
