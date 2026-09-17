#!/usr/bin/env python3
"""Local journal-entry analytics entry point."""
import os, sys, webbrowser, subprocess, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from audit_analytics.cli import main

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "launch":
        # Start FastAPI adapter with frontend served
        env = os.environ.copy()
        env["AUDIT_DB"] = env.get("AUDIT_DB", os.path.join(os.path.dirname(__file__), "data", "demo.db"))
        proc = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "audit_analytics.api.app:app", "--host", "127.0.0.1", "--port", "8788", "--app-dir", "src"],
            cwd=os.path.dirname(__file__), env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:8788")
        print("Audit Analytics workbench running at http://127.0.0.1:8788")
        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
    else:
        main()
