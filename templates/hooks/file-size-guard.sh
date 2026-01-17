#!/bin/bash
# File Size Guard Hook - Shell entry point
# Checks file line count after edit/write operations

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)"
if [ -z "$SCRIPT_DIR" ]; then
    SCRIPT_DIR="$(dirname "$0")"
fi

PY_FILE="$SCRIPT_DIR/file-size-guard.py"

# Check if Python file exists
if [ ! -f "$PY_FILE" ]; then
    echo "[file-size-guard] Error: $PY_FILE not found" >&2
    exit 1
fi

# Run Python script with exec to properly pass stdin
if command -v python3 &> /dev/null; then
    exec python3 "$PY_FILE"
elif command -v python &> /dev/null; then
    exec python "$PY_FILE"
else
    echo "[file-size-guard] Error: Python not found" >&2
    exit 1
fi
