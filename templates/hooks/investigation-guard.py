#!/usr/bin/env python3
"""
PreToolUse Hook: Enforce Investigation Before Code Modification

Logic:
- Track Read/Grep call history for each file
- If Edit is attempted on a file never Read, warn/block and prompt investigation first
- Especially strict for debug scenarios

Event: PreToolUse (Read, Grep, Edit, Write, MultiEdit)
Input: JSON HookInput (stdin)
Output: Warning/block message (stderr for warnings, exit code 2 for blocking)
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# State file: record investigated files
STATE_FILE = Path.home() / ".claude" / "investigation-state.json"


def load_state() -> dict:
    """Load investigation state"""
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
            # Clean records older than 1 hour
            cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
            data["investigated"] = {
                k: v for k, v in data.get("investigated", {}).items()
                if v.get("timestamp", "") > cutoff
            }
            return data
        except Exception:
            pass
    return {"investigated": {}, "edit_attempts": {}}


def save_state(state: dict):
    """Save investigation state"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def normalize_path(file_path: str) -> str:
    """Normalize file path"""
    return str(Path(file_path).resolve())


def main():
    try:
        data = json.load(sys.stdin)
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})

        state = load_state()
        now = datetime.now().isoformat()

        # Record Read/Grep operations
        if tool_name in ("Read", "Grep"):
            file_path = tool_input.get("file_path") or tool_input.get("path", "")
            if file_path:
                norm_path = normalize_path(file_path)
                state["investigated"][norm_path] = {
                    "tool": tool_name,
                    "timestamp": now
                }
                save_state(state)
            sys.exit(0)

        # Check Edit/Write operations
        if tool_name in ("Edit", "Write", "MultiEdit"):
            file_path = tool_input.get("file_path", "")
            if not file_path:
                sys.exit(0)

            norm_path = normalize_path(file_path)

            # Check if this file has been investigated
            if norm_path not in state["investigated"]:
                # Record uninvestigated edit attempt
                attempts = state.setdefault("edit_attempts", {})
                attempts[norm_path] = attempts.get(norm_path, 0) + 1
                save_state(state)

                # First attempt: warning
                if attempts[norm_path] == 1:
                    print(f"WARNING: Attempting to modify uninvestigated file {file_path}", file=sys.stderr)
                    print("Suggest using Read tool first to understand the context.", file=sys.stderr)
                    print("If this is a new file creation, ignore this warning.", file=sys.stderr)
                    # Don't block, just warn
                    sys.exit(0)

                # Second+ attempt: block
                if attempts[norm_path] >= 2:
                    print(f"BLOCKED: Multiple attempts to modify uninvestigated file {file_path}", file=sys.stderr)
                    print("", file=sys.stderr)
                    print("Systematic Debugging requires:", file=sys.stderr)
                    print("1. Use Read tool to view the current file content", file=sys.stderr)
                    print("2. Use Grep to search related code and error messages", file=sys.stderr)
                    print("3. Understand the root cause before making changes", file=sys.stderr)
                    sys.exit(2)  # Block operation

        sys.exit(0)

    except Exception:
        # Silent failure, don't affect normal workflow
        sys.exit(0)


if __name__ == "__main__":
    main()
