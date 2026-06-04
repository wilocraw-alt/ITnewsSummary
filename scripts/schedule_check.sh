#!/usr/bin/env bash
# schedule_check.sh — Check if ITnewsSummary schedule is active

INIT="$(ps -p 1 -o comm= 2>/dev/null || echo "unknown")"
echo "Init system: $INIT"

if [ "$INIT" = "systemd" ]; then
  echo "--- systemd user timers ---"
  systemctl --user list-timers --all 2>/dev/null | grep -E "itnewssummary|UNIT" || echo "(no itnewssummary timer found)"
  echo ""
  echo "--- systemd service status ---"
  systemctl --user status itnewssummary.service 2>/dev/null || echo "(service not found)"
else
  echo "--- crontab entries ---"
  crontab -l 2>/dev/null | grep -E "ITnewsSummary|run_and_open" || echo "(no ITnewsSummary entries found)"
fi
