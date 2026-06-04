#!/usr/bin/env bash
set -euo pipefail

# ITnewsSummary — easy pipeline runner
# Usage: ./run.sh [morning|evening] [--date YYYY-MM-DD]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Detect available Ollama endpoint: prefer local Linux (11435), fallback to Windows (11434)
if command -v curl &>/dev/null; then
    if curl -s -o /dev/null --connect-timeout 2 http://localhost:11435 2>/dev/null; then
        OLLAMA_BASE="http://localhost:11435"
    else
        OLLAMA_BASE="http://localhost:11434"
    fi
elif command -v wget &>/dev/null; then
    if wget -q --spider --timeout=2 http://localhost:11435 2>/dev/null; then
        OLLAMA_BASE="http://localhost:11435"
    else
        OLLAMA_BASE="http://localhost:11434"
    fi
else
    # fallback: bash /dev/tcp check
    if { exec 3<>/dev/tcp/localhost/11435; } 2>/dev/null; then
        exec 3<&- 3>&-
        OLLAMA_BASE="http://localhost:11435"
    else
        OLLAMA_BASE="http://localhost:11434"
    fi
fi

# Load .env (secrets, model config) — will be overridden by auto-detect below
if [ -f .env ]; then
    set -a
    . .env
    set +a
fi

# Override with detected Ollama URL; keep other vars from .env
export OPENAI_BASE_URL="${OLLAMA_BASE}/v1"
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
