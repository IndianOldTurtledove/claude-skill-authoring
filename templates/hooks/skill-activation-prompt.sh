#!/bin/bash
#
# Skill Activation Prompt Hook
# 在用户提交提示词时自动推荐相关 Skills
#
# 触发事件: UserPromptSubmit
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [ -z "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(dirname "$0")"
fi

PY_FILE="$SCRIPT_DIR/skill-activation-prompt.py"

# Check if Python file exists
if [ ! -f "$PY_FILE" ]; then
    echo "[skill-activation] Error: $PY_FILE not found" >&2
    exit 1
fi

# Run Python script
if command -v python3 &> /dev/null; then
    exec python3 "$PY_FILE"
elif command -v python &> /dev/null; then
    exec python "$PY_FILE"
else
    echo "[skill-activation] Error: Python not found" >&2
    exit 1
fi
