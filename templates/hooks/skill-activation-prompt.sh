#!/bin/bash
#
# Skill Activation Prompt Hook
# Automatically recommends relevant skills based on user input
#
# Event: UserPromptSubmit
# Inspired by: https://github.com/diet103/claude-code-infrastructure-showcase
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_FILE="$SCRIPT_DIR/skill-activation-prompt.py"

if command -v python3 &> /dev/null; then
    python3 "$PY_FILE"
elif command -v python &> /dev/null; then
    python "$PY_FILE"
else
    echo "[skill-activation] Error: Python not found" >&2
    exit 1
fi
