#!/usr/bin/env python3
"""
Post Tool Use Tracker Hook

Tracks file modifications and suggests appropriate check commands.
Event: PostToolUse (Edit, Write, MultiEdit, NotebookEdit)

Input: JSON HookInput (stdin)
Output: JSON format (stdout) - injected to Claude context via additionalContext

IMPORTANT: PostToolUse plain text stdout will NOT be injected to Claude context!
Must use JSON format (hookSpecificOutput.additionalContext) for Claude to see.

Inspired by: https://github.com/diet103/claude-code-infrastructure-showcase
"""

import json
import sys
from pathlib import Path

# Project root directory (customize for your project)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# File type to check commands mapping
# Customize this for your project's toolchain
CHECK_COMMANDS: dict[str, dict[str, str]] = {
    # Python files
    ".py": {
        "lint": "ruff check {file}",
        "format": "ruff format {file}",
        "type": "pyright {file}",
    },
    # TypeScript files
    ".ts": {
        "lint": "npx eslint {file}",
        "type": "npx tsc --noEmit",
    },
    ".tsx": {
        "lint": "npx eslint {file}",
        "type": "npx tsc --noEmit",
    },
    # JavaScript files
    ".js": {
        "lint": "npx eslint {file}",
    },
    ".jsx": {
        "lint": "npx eslint {file}",
    },
    # Vue files
    ".vue": {
        "lint": "npx eslint {file}",
    },
    # JSON files
    ".json": {
        "validate": "python3 -m json.tool {file} > /dev/null",
    },
    # Shell scripts
    ".sh": {
        "lint": "shellcheck {file}",
    },
    # Rust files
    ".rs": {
        "check": "cargo check",
        "lint": "cargo clippy",
    },
    # Go files
    ".go": {
        "lint": "golangci-lint run {file}",
        "format": "gofmt -w {file}",
    },
}


def detect_file_type(file_path: str) -> str | None:
    """Detect file type from extension"""
    path = Path(file_path)
    return path.suffix.lower() if path.suffix else None


def get_check_commands(file_path: str) -> list[str]:
    """Get check commands for a file"""
    commands = []
    file_type = detect_file_type(file_path)

    if file_type and file_type in CHECK_COMMANDS:
        for cmd in CHECK_COMMANDS[file_type].values():
            if cmd:
                commands.append(cmd.format(file=file_path))

    return commands


def format_output(modified_files: list[str], check_commands: dict[str, list[str]]) -> str:
    """Format output"""
    if not modified_files:
        return ""

    lines = []
    lines.append("")
    lines.append("-" * 50)
    lines.append("  FILE TRACKER")
    lines.append("-" * 50)

    lines.append("")
    lines.append("Modified files:")
    for f in modified_files:
        lines.append(f"  - {f}")

    if check_commands:
        lines.append("")
        lines.append("Suggested checks:")
        seen_commands = set()
        for cmds in check_commands.values():
            for cmd in cmds:
                if cmd not in seen_commands:
                    lines.append(f"  $ {cmd}")
                    seen_commands.add(cmd)

    lines.append("-" * 50)
    lines.append("")

    return "\n".join(lines)


def main():
    """Main function"""
    try:
        input_str = sys.stdin.read()
        if not input_str.strip():
            return

        try:
            hook_input = json.loads(input_str)
        except json.JSONDecodeError:
            # Silent fail, don't affect user experience
            return

        tool_name = hook_input.get("tool_name", "")
        tool_input = hook_input.get("tool_input", {})

        # Only process edit-related tools
        if tool_name not in ["Edit", "Write", "MultiEdit", "NotebookEdit"]:
            return

        # Extract modified file paths
        modified_files = []

        if tool_name in ["Edit", "Write", "NotebookEdit"]:
            file_path = tool_input.get("file_path", "")
            if file_path:
                # Try to make relative path
                try:
                    rel_path = str(Path(file_path).relative_to(PROJECT_ROOT))
                except ValueError:
                    rel_path = file_path
                modified_files.append(rel_path)

        elif tool_name == "MultiEdit":
            edits = tool_input.get("edits", [])
            for edit in edits:
                file_path = edit.get("file_path", "")
                if file_path:
                    try:
                        rel_path = str(Path(file_path).relative_to(PROJECT_ROOT))
                    except ValueError:
                        rel_path = file_path
                    if rel_path not in modified_files:
                        modified_files.append(rel_path)

        if not modified_files:
            return

        # Generate check commands
        check_commands: dict[str, list[str]] = {}
        for file_path in modified_files:
            cmds = get_check_commands(file_path)
            if cmds:
                check_commands[file_path] = cmds

        # Output using JSON format to inject into Claude context
        output_text = format_output(modified_files, check_commands)
        if output_text:
            json_output = {
                "hookSpecificOutput": {
                    "hookEventName": "PostToolUse",
                    "additionalContext": output_text
                }
            }
            print(json.dumps(json_output))

    except Exception:
        # Silent fail, don't affect normal workflow
        pass


if __name__ == "__main__":
    main()
