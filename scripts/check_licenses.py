"""Reject missing or strong-copyleft frontend dependency metadata."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCKFILE = ROOT / "frontend" / "package-lock.json"
FORBIDDEN_MARKERS = ("AGPL", "GPL", "SSPL")


def main() -> int:
    lock = json.loads(LOCKFILE.read_text(encoding="utf-8"))
    errors = []
    for name, package in lock.get("packages", {}).items():
        if not name:
            continue
        license_name = package.get("license")
        if not license_name:
            errors.append(f"missing license metadata: {name}")
            continue
        if any(marker in license_name.upper() for marker in FORBIDDEN_MARKERS):
            errors.append(f"strong-copyleft license requires manual review: {name} ({license_name})")
    if errors:
        print("Frontend license policy failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    print("Frontend license metadata policy passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
