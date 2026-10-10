#!/bin/bash
# Build double-clickable macOS .app launchers for the audit-analytics workbench.
#
# The workbench is already a web app (FastAPI serves the built React bundle on
# 127.0.0.1). These launchers only wrap the start/stop lifecycle so it opens
# with one double-click and no terminal. Binds stay on 127.0.0.1 by design.
#
# Usage: scripts/build_desktop_app.sh
# Re-run after moving the repository: the absolute project root is baked in.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dist"
APPS=("Audit Analytics" "Stop Audit Analytics")

PY="$ROOT/.venv/bin/python"
DB="$ROOT/engagements/local/audit.db"
RUNDIR="$ROOT/engagements/local"
LOG="$RUNDIR/server.log"
PIDFILE="$RUNDIR/server.pid"
PORT=8788
URL="http://127.0.0.1:$PORT"

if [ ! -x "$PY" ]; then
  echo "error: venv python missing at $PY" >&2
  echo "       run: uv sync --frozen --all-extras --group dev" >&2
  exit 1
fi

mkdir -p "$RUNDIR"

bundle() {  # bundle <name> <script-body-file>
  local name="$1" body="$2"
  local app="$OUT/$name.app"
  local slug
  slug="$(printf '%s' "$name" | tr -cd '[:alnum:]' | tr 'A-Z' 'a-z')"
  rm -rf "$app"
  mkdir -p "$app/Contents/MacOS"
  cp "$body" "$app/Contents/MacOS/$name"
  chmod +x "$app/Contents/MacOS/$name"
  cat > "$app/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key><string>$name</string>
  <key>CFBundleDisplayName</key><string>$name</string>
  <key>CFBundleExecutable</key><string>$name</string>
  <key>CFBundleIdentifier</key><string>com.nighomni123.audit-analytics.$slug</string>
  <key>CFBundleVersion</key><string>1.0.0</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleShortVersionString</key><string>1.0.0</string>
  <key>LSMinimumSystemVersion</key><string>11.0</string>
  <key>NSHighResolutionCapable</key><true/>
  <key>NSSupportsAutomaticTermination</key><false/>
  <key>NSSupportsSuddenTermination</key><false/>
</dict>
</plist>
PLIST
  echo "built  $app"
}

# ---------------------------------------------------------------- start app
cat > "$RUNDIR/.launch" <<LAUNCH
#!/bin/bash
# Audit Analytics - start the local workbench and open it in the browser.
set -uo pipefail

PY="$PY"
DB="$DB"
RUNDIR="$RUNDIR"
LOG="$LOG"
PIDFILE="$PIDFILE"
PORT=$PORT
URL="$URL"
ROOT="$ROOT"

alive() { curl -fsS -m 2 "\$URL/api/health" >/dev/null 2>&1; }

# Already up: just bring the browser to the front. One tap stays one tap.
if alive; then
  open "\$URL"
  exit 0
fi

mkdir -p "\$RUNDIR"
nohup "\$PY" "\$ROOT/run.py" serve --db "\$DB" --port "\$PORT" >>"\$LOG" 2>&1 &
echo \$! > "\$PIDFILE"

for _ in \$(seq 1 60); do
  alive && break
  sleep 0.5
done

if ! alive; then
  osascript -e 'display alert "Audit Analytics could not start" \
    message "The local server did not come up on port '"$PORT"'. See the log at:
'"$LOG"'" with title "Audit Analytics"'
  exit 1
fi

open "\$URL"
LAUNCH

# ----------------------------------------------------------------- stop app
cat > "$RUNDIR/.stop" <<STOP
#!/bin/bash
# Audit Analytics - stop the local workbench server.
set -uo pipefail

PIDFILE="$PIDFILE"
URL="$URL"
LOG="$LOG"
DIALOG_TITLE="Audit Analytics"

if ! [ -f "\$PIDFILE" ]; then
  osascript -e 'display alert "Audit Analytics is not running" \
    message "Nothing to stop." with title "Audit Analytics"'
  exit 0
fi

PID="\$(cat "\$PIDFILE" 2>/dev/null || true)"
if [ -n "\${PID:-}" ] && kill -0 "\$PID" 2>/dev/null; then
  kill "\$PID" 2>/dev/null
  for _ in \$(seq 1 20); do
    kill -0 "\$PID" 2>/dev/null || break
    sleep 0.25
  done
  kill -9 "\$PID" 2>/dev/null
fi
rm -f "\$PIDFILE"

osascript -e 'display alert "Audit Analytics stopped" \
  message "The local server is shut down." with title "Audit Analytics"'
STOP

bundle "Audit Analytics" "$RUNDIR/.launch"
bundle "Stop Audit Analytics" "$RUNDIR/.stop"
rm -f "$RUNDIR/.launch" "$RUNDIR/.stop"

# A malformed Info.plist makes macOS ignore the bundle entirely, and the
# launcher still "works" when invoked by hand -- so verify what Finder needs.
for name in "${APPS[@]}"; do
  plutil -lint "$OUT/$name.app/Contents/Info.plist" >/dev/null
  bash -n "$OUT/$name.app/Contents/MacOS/$name"
  [ -x "$OUT/$name.app/Contents/MacOS/$name" ]
  echo "verified  $name.app"
done

echo
echo "One-tap launch:  open '$OUT/Audit Analytics.app'"
echo "To stop:        open '$OUT/Stop Audit Analytics.app'"
echo "Drag either to  /Applications if you want it in the Dock."
