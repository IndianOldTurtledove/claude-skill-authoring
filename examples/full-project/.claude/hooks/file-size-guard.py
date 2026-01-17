#!/usr/bin/env python3
"""
File Size Guard Hook

Checks file line count, warns AI to split file when threshold exceeded.
Event: PostToolUse (Edit, Write, MultiEdit)

Input: JSON HookInput (stdin)
Output: JSON format (stdout) - injected to Claude context via additionalContext

IMPORTANT: PostToolUse plain text stdout will NOT be injected to Claude context!
Must use JSON format (hookSpecificOutput.additionalContext) for Claude to see.

Threshold configuration:
- Default: 500 lines
- Override via FILE_SIZE_LIMIT environment variable
"""

import json
import os
import sys
from pathlib import Path

# Line count threshold
LINE_LIMIT = int(os.environ.get("FILE_SIZE_LIMIT", "500"))

# Excluded file patterns (these files are allowed to exceed limit)
EXCLUDED_PATTERNS = [
    # Generated files
    "generated",
    "auto-generated",
    # Third-party/vendor
    "node_modules",
    "vendor",
    ".venv",
    "venv",
    # Data files
    ".csv",
    ".json",
    ".lock",
    # Config files
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    # Migrations
    "migrations",
    # Test snapshots
    "__snapshots__",
]

# File type to split suggestions mapping
SPLIT_SUGGESTIONS = {
    ".py": [
        "Split classes into separate module files",
        "Extract utility functions to utils.py",
        "Move constants to constants.py",
        "Use services/ directory for business logic",
    ],
    ".vue": [
        "Split large components into sub-components",
        "Extract composables to separate files",
        "Move styles to separate .scss files",
        "Use components/ directory for organization",
    ],
    ".ts": [
        "Move type definitions to types.ts",
        "Extract utility functions to utils.ts",
        "Split by feature into multiple modules",
    ],
    ".tsx": [
        "Split into smaller components",
        "Extract hooks to separate files",
        "Move styles to separate files",
    ],
    ".js": [
        "Split by feature into multiple modules",
        "Extract utility functions",
        "Use ES6 modules for organization",
    ],
}


def is_excluded(file_path: str) -> bool:
    """Check if file is in exclusion list"""
    file_path_lower = file_path.lower()
    for pattern in EXCLUDED_PATTERNS:
        if pattern in file_path_lower:
            return True
    return False


def count_lines(file_path: str) -> int | None:
    """Count file lines"""
    try:
        path = Path(file_path)
        if not path.exists():
            return None
        return len(path.read_text(encoding="utf-8").splitlines())
    except Exception:
        return None


def get_file_extension(file_path: str) -> str:
    """Get file extension"""
    return Path(file_path).suffix.lower()


def format_warning(file_path: str, line_count: int) -> str:
    """Format warning message"""
    ext = get_file_extension(file_path)
    suggestions = SPLIT_SUGGESTIONS.get(ext, ["Consider splitting file into smaller modules"])

    lines = []
    lines.append("")
    lines.append("!" * 60)
    lines.append("  FILE SIZE WARNING")
    lines.append("!" * 60)
    lines.append("")
    lines.append(f"  File: {file_path}")
    lines.append(f"  Lines: {line_count} (limit: {LINE_LIMIT})")
    lines.append("")
    lines.append("  This file exceeds the recommended size limit.")
    lines.append("  Large files are harder to maintain and understand.")
    lines.append("")
    lines.append("  RECOMMENDED ACTIONS:")
    for i, suggestion in enumerate(suggestions, 1):
        lines.append(f"    {i}. {suggestion}")
    lines.append("")
    lines.append("  Please consider refactoring before adding more code.")
    lines.append("")
    lines.append("!" * 60)
    lines.append("")

    return "\n".join(lines)


def main():
    """Main function"""
    try:
        # Read stdin
        input_str = sys.stdin.read()
        if not input_str.strip():
            return

        try:
            hook_input = json.loads(input_str)
        except json.JSONDecodeError:
            return

        # Get tool info
        tool_name = hook_input.get("tool_name", "")
        tool_input = hook_input.get("tool_input", {})

        # Only process edit-related tools
        if tool_name not in ["Edit", "Write", "MultiEdit", "NotebookEdit"]:
            return

        # Extract file paths
        files_to_check = []

        if tool_name in ["Edit", "Write", "NotebookEdit"]:
            file_path = tool_input.get("file_path", "")
            if file_path:
                files_to_check.append(file_path)

        elif tool_name == "MultiEdit":
            edits = tool_input.get("edits", [])
            for edit in edits:
                file_path = edit.get("file_path", "")
                if file_path and file_path not in files_to_check:
                    files_to_check.append(file_path)

        # Check each file
        warnings = []
        for file_path in files_to_check:
            # Skip excluded files
            if is_excluded(file_path):
                continue

            # Count lines
            line_count = count_lines(file_path)
            if line_count is None:
                continue

            # Check if exceeds threshold
            if line_count > LINE_LIMIT:
                warnings.append(format_warning(file_path, line_count))

        # Output using JSON format to inject into Claude context
        if warnings:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": "\n".join(warnings)
                }
            }
            print(json.dumps(output))

    except Exception:
        # Silent fail, don't affect normal operations
        pass


if __name__ == "__main__":
    main()
