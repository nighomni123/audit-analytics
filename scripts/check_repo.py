"""Fail CI when repository hygiene or runtime-boundary policies regress."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DENY_PATH_PARTS = (
    ".env",
    ".npm-cache/",
    ".playwright-browsers/",
    ".uv-cache/",
    "data/",
    "engagements/",
    "evidence/",
    "exports/",
    "frontend/dist/",
    "gpt_thread.md",
)
DENY_SUFFIXES = (".db", ".db-shm", ".db-wal", ".sqlite", ".sqlite3")
REQUIRED = ("LICENSE", "pyproject.toml", "uv.lock", "src/audit_analytics/static/index.html", ".github/workflows/ci.yml")
FORBIDDEN = (
    "CORSMiddleware",
    "ThreadingHTTPServer",
    "JE104932",
    "cdn.tailwindcss.com",
    "/Users/",
    "audit_analytics.server",
)
TEXT_SUFFIXES = {".css", ".html", ".js", ".json", ".md", ".py", ".toml", ".tsx", ".ts", ".yaml", ".yml"}


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True)
    return [item.decode() for item in result.stdout.split(b"\0") if item]


def main() -> int:
    tracked = tracked_files()
    files = [name for name in tracked if (ROOT / name).exists()]
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            errors.append(f"required tracked file missing: {name}")
    for name in files:
        lowered = name.lower()
        if any(part in lowered for part in DENY_PATH_PARTS) or lowered.endswith(DENY_SUFFIXES):
            errors.append(f"prohibited tracked path: {name}")
        if name.startswith("benchmark-results/") or name in {"AGENTS.md", "scripts/check_repo.py"} or Path(name).suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = (ROOT / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for fragment in FORBIDDEN:
            if fragment.lower() in text.lower():
                errors.append(f"forbidden runtime/repository fragment {fragment!r} in {name}")
    if errors:
        print("Repository policy failed:\n- " + "\n- ".join(sorted(set(errors))), file=sys.stderr)
        return 1
    print(f"Repository policy passed for {len(files)} tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
