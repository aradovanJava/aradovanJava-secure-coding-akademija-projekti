#!/usr/bin/env bash
# CI provjera jednog para <stack>/<domena>: all-vuln (svaki slot pada) + all-secure (sve prolazi) + lint varijanti.
set -uo pipefail
stack=$1; domain=$2
root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d)
status=0
ALL=S01,S02,S03,S04,S05,S06,S07,S08,S09,S10,S11,S12,S13
for mode in all-vuln all-secure; do
  dest="$work/$mode"
  echo "=== $stack/$domain $mode ==="
  if ! python3 "$root/tools/generate.py" --stack "$stack" --domain "$domain" --mode "$mode" --dest "$dest" --with-hidden; then
    echo "::error title=$stack/$domain $mode::Generator ili lint nije uspio (vidi log)"; status=1; continue
  fi
  res="$work/res-$mode"
  if ! "$root/tools/run_tests.sh" "$stack" "$dest" "$res"; then
    echo "::error title=$stack/$domain $mode::Build nije uspio"; status=1; continue
  fi
  exp=""; [ "$mode" = "all-vuln" ] && exp=$ALL
  python3 "$root/tools/check_results.py" --results "$res" --expect-vulnerable "$exp" --gha --label "$stack/$domain $mode" || status=1
done
for v in $(python3 -c "import json,sys;print(' '.join(k for k,x in json.load(open(sys.argv[1])).items() if x['domain']==sys.argv[2]))" "$root/variants.json" "$domain"); do
  python3 "$root/tools/generate.py" --variant "$v" --stack "$stack" --dest "$work/lint-$v" >/dev/null \
    || { echo "::error title=$v $stack::Generator/lint varijante nije uspio"; status=1; }
done
exit $status
