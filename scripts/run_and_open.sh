#!/usr/bin/env bash
set -euo pipefail

# run_and_open.sh — Run the pipeline then open HTML in Windows browser
# Usage: scripts/run_and_open.sh [morning|evening]
#   OPEN_ONLY=1        skip pipeline run, just open existing HTML
#   OPEN_HTML=<path>   explicit HTML file (with OPEN_ONLY=1)
# If period omitted, auto-detect from current hour (run.sh logic: before 14 = morning)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

PERIOD="${1:-}"
if [ -z "$PERIOD" ]; then
  HOUR="$(date +%H)"
  if [ "$HOUR" -lt 14 ]; then
    PERIOD="morning"
  else
    PERIOD="evening"
  fi
fi

LOG_DIR="$PROJECT_ROOT/output"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/cron.log"

log() {
  local ts; ts="$(date '+%Y-%m-%d %H:%M:%S')"
  printf '%s [run_and_open] %s\n' "$ts" "$*" >> "$LOG_FILE"
  printf '%s [run_and_open] %s\n' "$ts" "$*"
}

if [ -z "${OPEN_ONLY:-}" ]; then
  log "Starting $PERIOD run ..."
  if ! bash "$PROJECT_ROOT/run.sh" "$PERIOD" >> "$LOG_FILE" 2>&1; then
    log "ERROR: run.sh $PERIOD failed (see log above)"
    exit 1
  fi
  log "run.sh $PERIOD completed successfully"
fi

TODAY="$(date +%Y-%m-%d)"
HTML_FILE="${OPEN_HTML:-$PROJECT_ROOT/output/$TODAY/$PERIOD.html}"

if [ ! -f "$HTML_FILE" ]; then
  log "ERROR: HTML not found at $HTML_FILE"
  exit 1
fi

log "Opening $HTML_FILE in Windows browser ..."

# Detect WSL interop availability
if [ -z "${WSL_INTEROP:-}" ] && [ -f /proc/sys/fs/binfmt_misc/WSLInterop ]; then
  for f in /run/WSL/*_interop; do
    if [ -S "$f" ] 2>/dev/null; then
      export WSL_INTEROP="$f"
      log "Sourced WSL_INTEROP from $f"
      break
    fi
  done
fi

# Resolve Windows interop binary by absolute path (don't rely on PATH in cron)
find_wsl_binary() {
  # 1) PATH lookup (interactive shells)
  local p; p="$(command -v explorer.exe 2>/dev/null)" && { [ -x "$p" ] && printf '%s\n' "$p" && return 0; }
  # 2) Probe /mnt/*/Windows/ directories
  local d f
  for d in /mnt/*/Windows; do
    [ -d "$d" ] || continue
    # Prefer powershell.exe (returns 0 on success)
    f="$d/System32/WindowsPowerShell/v1.0/powershell.exe"
    [ -x "$f" ] && { printf '%s\n' "$f" && return 0; }
    f="$d/explorer.exe"
    [ -x "$f" ] && { printf '%s\n' "$f" && return 0; }
  done
  return 1
}

WSL_BIN="$(find_wsl_binary || true)"
WIN_PATH="$(wslpath -w "$HTML_FILE")"

if [ -n "$WSL_BIN" ]; then
  BIN_NAME="$(basename "$WSL_BIN")"
  log "Found interop binary: $WSL_BIN"
  case "$BIN_NAME" in
    powershell.exe)
      log "powershell.exe -NoProfile Start-Process '$WIN_PATH'"
      "$WSL_BIN" -NoProfile Start-Process "'$WIN_PATH'" 2>> "$LOG_FILE" \
        && log "Browser open: OK (exit 0)" \
        || log "Browser open: FAILED (exit $?)"
      ;;
    explorer.exe)
      log "explorer.exe $WIN_PATH (exit bypassed — explorer.exe exits 1 even on success)"
      "$WSL_BIN" "$WIN_PATH" 2>> "$LOG_FILE" && rc=0 || rc=$?
      log "Browser open: attempted (explorer.exe exit=$rc, see Windows taskbar)"
      ;;
  esac
else
  log "WARNING: No Windows interop binary found — HTML at $HTML_FILE (open manually)"
fi

log "$PERIOD run complete"
