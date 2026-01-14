#!/bin/bash
#
# Post Tool Use Tracker Hook
# Tracks file modifications and suggests check commands
#
# Event: PostToolUse (Edit, Write, MultiEdit, NotebookEdit)
# Inspired by: https://github.com/diet103/claude-code-infrastructure-showcase
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_FILE="$SCRIPT_DIR/post-tool-use-tracker.py"

if command -v python3 &> /dev/null; then
    python3 "$PY_FILE"
elif command -v python &> /dev/null; then
    python "$PY_FILE"
else
    echo "[file-tracker] Error: Python not found" >&2
    exit 1
fi
