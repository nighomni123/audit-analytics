"""Serve an empty synthetic engagement for the real React browser test."""
from __future__ import annotations

import tempfile
from pathlib import Path

import uvicorn

from audit_analytics.api.app import create_app


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="audit-browser-") as directory:
        database = Path(directory) / "audit.db"
        uvicorn.run(create_app(database), host="127.0.0.1", port=8789, log_level="warning")


if __name__ == "__main__":
    main()
