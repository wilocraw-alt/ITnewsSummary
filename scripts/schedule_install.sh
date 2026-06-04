#!/usr/bin/env bash
set -euo pipefail

# schedule_install.sh — Install cron entries for twice-daily pipeline
# Detects init system: prefers systemd user timer if available, else crontab.
# Preserves existing crontab entries (appends idempotently).

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WRAPPER="$SCRIPT_DIR/run_and_open.sh"

echo "=== ITnewsSummary scheduler install ==="
echo "Project root: $PROJECT_ROOT"

# Ensure wrapper is executable
chmod +x "$WRAPPER"

# Detect init system
INIT="$(ps -p 1 -o comm= 2>/dev/null || echo "unknown")"
echo "Init system: $INIT"

if [ "$INIT" = "systemd" ]; then
  echo "systemd detected — installing user timer ..."

  UNIT_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/systemd/user"
  mkdir -p "$UNIT_DIR"

  cat > "$UNIT_DIR/itnewssummary.service" <<-EOF
[Unit]
Description=ITnewsSummary pipeline run (%I)

[Service]
Type=oneshot
WorkingDirectory=$PROJECT_ROOT
ExecStart=$WRAPPER %i
StandardOutput=append:$PROJECT_ROOT/output/cron.log
StandardError=append:$PROJECT_ROOT/output/cron.log
EOF

  cat > "$UNIT_DIR/itnewssummary.timer" <<-EOF
[Unit]
Description=ITnewsSummary twice-daily timer

[Timer]
OnCalendar=08:00,20:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

  systemctl --user daemon-reload
  systemctl --user enable itnewssummary.timer
  systemctl --user start itnewssummary.timer

  echo "systemd timer installed:"
  systemctl --user list-timers --all | grep itnewssummary || true

else
  echo "cron detected — installing crontab entries ..."

  # Check if cron service is running
  if command -v service &>/dev/null; then
    if ! service cron status &>/dev/null && ! service crond status &>/dev/null; then
      echo "WARNING: cron service is not running."
      echo "  Try: sudo service cron start"
      echo "  Or add manually to crontab:"
      echo "    0 8 * * * $WRAPPER morning"
      echo "    0 20 * * * $WRAPPER evening"
      echo "  Skipping crontab install."
      exit 0
    fi
  fi

  # Build idempotent crontab entries (append if not already present)
  CRON_MARKER="# ITnewsSummary"
  ENTRY_MORNING="0 8 * * * $WRAPPER morning"
  ENTRY_EVENING="0 20 * * * $WRAPPER evening"

  (crontab -l 2>/dev/null || true) | (
    # Preserve existing entries, add marker + schedule if not present
    cat
    if ! crontab -l 2>/dev/null | grep -Fq "$CRON_MARKER"; then
      echo ""
      echo "$CRON_MARKER"
      echo "$ENTRY_MORNING"
      echo "$ENTRY_EVENING"
    fi
  ) | crontab -

  echo "Crontab entries installed:"
  crontab -l | grep -E "ITnewsSummary|run_and_open"
fi

echo ""
echo "Done. Verify with:"
echo "  scripts/schedule_check.sh"
echo ""
echo "To remove:"
echo "  scripts/schedule_uninstall.sh"
