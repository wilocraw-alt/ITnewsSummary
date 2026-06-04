#!/usr/bin/env bash
set -euo pipefail

# run_and_open.sh — Run the pipeline with cron logging
# Browser open is handled by run.sh via scripts/open_html.sh (single open).
# Usage: scripts/run_and_open.sh [morning|evening]
# If period omitted, auto-detect from current hour.

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

mkdir -p "$PROJECT_ROOT/output"
LOG_FILE="$PROJECT_ROOT/output/cron.log"

log() {
  local ts; ts="$(date '+%Y-%m-%d %H:%M:%S')"
  printf '%s [run_and_open] %s\n' "$ts" "$*" >> "$LOG_FILE"
  printf '%s [run_and_open] %s\n' "$ts" "$*"
}

log "Starting $PERIOD run ..."
if ! bash "$PROJECT_ROOT/run.sh" "$PERIOD" >> "$LOG_FILE" 2>&1; then
  log "ERROR: run.sh $PERIOD failed (see log above)"
  exit 1
fi

log "run.sh $PERIOD completed successfully (browser open handled by run.sh)"
log "$PERIOD run complete"
