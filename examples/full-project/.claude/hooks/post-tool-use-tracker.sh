#!/bin/bash
#
# Post Tool Use Tracker Hook
# Tracks file modifications and suggests check commands
#
# Event: PostToolUse (Edit, Write, MultiEdit, NotebookEdit)
# Inspired by: https://github.com/diet103/claude-code-infrastructure-showcase
#

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [ -z "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(dirname "$0")"
fi

PY_FILE="$SCRIPT_DIR/post-tool-use-tracker.py"

# Check if Python file exists
if [ ! -f "$PY_FILE" ]; then
    echo "[file-tracker] Error: $PY_FILE not found" >&2
    exit 1
fi

# Run Python script with exec to properly pass stdin
if command -v python3 &> /dev/null; then
    exec python3 "$PY_FILE"
elif command -v python &> /dev/null; then
    exec python "$PY_FILE"
else
    echo "[file-tracker] Error: Python not found" >&2
    exit 1
fi
