#!/usr/bin/env python3
"""Odredi koje parove <stack>/<domena> treba provjeriti u dev CI-ju (prema promijenjenim datotekama)."""
import json, os, subprocess

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
existing = sorted(f"{s}/{d}" for s in ("java", "dotnet", "python") for d in ("medtermin", "ulaznica", "kadrovska")
                  if os.path.isdir(os.path.join(root, "templates", s, d))
                  and os.path.isdir(os.path.join(root, "hidden-tests", s, d)))
inp = (os.environ.get("INPUT_PAIRS") or "").split()
before = os.environ.get("BEFORE") or ""
pairs = set()
if os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch":
    pairs = set(inp) if inp else set(existing)
else:
    try:
        if not before or set(before) == {"0"}:
            raise RuntimeError("nema prethodnog commita")
        changed = subprocess.check_output(["git", "diff", "--name-only", before, "HEAD"], cwd=root, text=True).split()
    except Exception:
        changed = ["tools/"]
    for f in changed:
        parts = f.split("/")
        if parts[0] in ("templates", "hidden-tests") and len(parts) >= 3:
            pairs.add(f"{parts[1]}/{parts[2]}")
        elif parts[0] in ("tools", "variants.json") or f.startswith(".github/workflows/dev.yml"):
            pairs.update(existing)
pairs = sorted(p for p in pairs if p in existing)
print("Parovi za provjeru:", pairs)
with open(os.environ.get("GITHUB_OUTPUT", "/dev/stdout"), "a") as fh:
    fh.write(f"matrix={json.dumps(pairs)}\n")
