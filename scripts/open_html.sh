#!/usr/bin/env bash
set -euo pipefail

# open_html.sh — Open a local HTML file in the Windows default browser
# Usage: scripts/open_html.sh <html-file-path>
# Shared by run.sh and run_and_open.sh; resolves interop binary by absolute path.

HTML_FILE="${1:?Usage: open_html.sh <html-file-path>}"

if [ ! -f "$HTML_FILE" ]; then
  echo "open_html: ERROR: $HTML_FILE not found" >&2
  exit 1
fi

# Detect WSL interop availability
if [ -z "${WSL_INTEROP:-}" ] && [ -f /proc/sys/fs/binfmt_misc/WSLInterop ]; then
  for f in /run/WSL/*_interop; do
    if [ -S "$f" ] 2>/dev/null; then
      export WSL_INTEROP="$f"
      break
    fi
  done
fi

# Resolve Windows interop binary by absolute path (don't rely on PATH in cron)
find_wsl_binary() {
  local p; p="$(command -v explorer.exe 2>/dev/null)" && { [ -x "$p" ] && printf '%s\n' "$p" && return 0; }
  local d f
  for d in /mnt/*/Windows; do
    [ -d "$d" ] || continue
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
  case "$(basename "$WSL_BIN")" in
    powershell.exe)
      "$WSL_BIN" -NoProfile Start-Process "'$WIN_PATH'" && rc=0 || rc=$?
      echo "open_html: powershell.exe Start-Process '$WIN_PATH' (exit $rc)"
      exit $rc
      ;;
    explorer.exe)
      "$WSL_BIN" "$WIN_PATH" && rc=0 || rc=$?
      echo "open_html: explorer.exe '$WIN_PATH' (exit $rc)"
      exit 0
      ;;
  esac
else
  echo "open_html: WARNING: No Windows interop binary found — open manually: $HTML_FILE" >&2
  exit 0
fi
