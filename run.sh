#!/usr/bin/env bash
set -euo pipefail

# ITnewsSummary — easy pipeline runner
# Usage: ./run.sh [morning|evening] [--date YYYY-MM-DD]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env (secrets, model config)
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

# Defaults for local Ollama
export OPENAI_BASE_URL="${OPENAI_BASE_URL:-http://localhost:11435/v1}"
export OPENAI_API_KEY="${OPENAI_API_KEY:-ollama}"
export LLM_MODEL="${LLM_MODEL:-gemma4:e4b}"

# Period: arg or auto-detect
PERIOD="${1:-}"
if [ -z "$PERIOD" ]; then
    HOUR="$(date +%H)"
    if [ "$HOUR" -lt 14 ]; then
        PERIOD="morning"
    else
        PERIOD="evening"
    fi
fi

echo "=== ITnewsSummary :: $PERIOD ==="
exec python3 main.py "$PERIOD" "${@:2}"
