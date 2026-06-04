#!/usr/bin/env bash
set -euo pipefail

# schedule_uninstall.sh — Remove ITnewsSummary scheduled entries

echo "=== ITnewsSummary scheduler uninstall ==="

INIT="$(ps -p 1 -o comm= 2>/dev/null || echo "unknown")"

if [ "$INIT" = "systemd" ]; then
  echo "Removing systemd user timer ..."
  systemctl --user stop itnewssummary.timer 2>/dev/null || true
  systemctl --user disable itnewssummary.timer 2>/dev/null || true
  rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/systemd/user/itnewssummary.service"
  rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/systemd/user/itnewssummary.timer"
  systemctl --user daemon-reload
  echo "systemd timer removed."
else
  echo "Removing crontab entries ..."
  (crontab -l 2>/dev/null || true) \
    | grep -v "ITnewsSummary" \
    | grep -v "run_and_open" \
    | crontab -
  echo "Crontab entries removed."
fi

echo "Done."
