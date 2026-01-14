#!/usr/bin/env python3
"""
Skill Activation Prompt Hook

Automatically analyzes user prompts and recommends relevant skills.
Event: UserPromptSubmit

Input: JSON HookInput (stdin)
Output: Skill recommendations (stdout) - injected into model context

Inspired by: https://github.com/diet103/claude-code-infrastructure-showcase
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Debug log file
DEBUG_LOG = Path(__file__).parent / "hook-debug.log"


def log_debug(msg: str):
    """Write debug message to log file"""
    try:
        with open(DEBUG_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {msg}\n")
    except Exception:
        pass

# Priority weights for sorting
PRIORITY_WEIGHT = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def find_skill_rules() -> Path | None:
    """Find skill-rules.json in .claude/skills/ directory"""
    # Try relative to this script first
    script_dir = Path(__file__).parent
    candidates = [
        script_dir.parent / "skills" / "skill-rules.json",  # .claude/skills/
        script_dir.parent.parent / ".claude" / "skills" / "skill-rules.json",  # from templates/
        Path.cwd() / ".claude" / "skills" / "skill-rules.json",  # from cwd
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def load_skill_rules() -> dict[str, Any] | None:
    """Load skill-rules.json"""
    rules_path = find_skill_rules()

    if not rules_path:
        return None

    try:
        return json.loads(rules_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[skill-activation] Failed to parse skill-rules.json: {e}", file=sys.stderr)
        return None


def matches_triggers(prompt: str, triggers: dict) -> bool:
    """Check if prompt matches skill trigger rules"""
    # Limit prompt length for performance (avoid regex catastrophic backtracking)
    MAX_PROMPT_LEN = 2000
    if len(prompt) > MAX_PROMPT_LEN:
        prompt = prompt[:MAX_PROMPT_LEN]

    prompt_lower = prompt.lower()
    prompt_triggers = triggers.get("promptTriggers", {})

    # Keyword matching
    for keyword in prompt_triggers.get("keywords", []):
        if keyword.lower() in prompt_lower:
            return True

    # Intent pattern matching (regex) - with timeout protection
    for pattern in prompt_triggers.get("intentPatterns", []):
        try:
            # Use simple patterns only, skip complex ones on long input
            if len(prompt) > 500 and (".*" in pattern or ".+" in pattern):
                continue
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        except (re.error, RecursionError):
            pass

    return False


def analyze_prompt(prompt: str, rules: dict) -> list[tuple[str, dict]]:
    """Analyze prompt and return matching skills"""
    matches = []

    for skill_name, rule in rules.get("skills", {}).items():
        if matches_triggers(prompt, rule.get("triggers", {})):
            matches.append((skill_name, rule))

    # Sort by priority
    matches.sort(
        key=lambda x: PRIORITY_WEIGHT.get(x[1].get("priority", "low"), 0),
        reverse=True
    )

    return matches


def generate_recommendation(matches: list[tuple[str, dict]], config: dict) -> str:
    """Generate recommendation output"""
    if not matches:
        return ""

    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("  SKILL RECOMMENDATION")
    lines.append("=" * 60)
    lines.append("")

    # Group by priority
    grouped: dict[str, list[tuple[str, dict]]] = {}
    for skill_name, rule in matches:
        priority = rule.get("priority", "low")
        if priority not in grouped:
            grouped[priority] = []
        grouped[priority].append((skill_name, rule))

    priority_levels = config.get("priorityLevels", {
        "critical": {"icon": "!!", "label": "MUST USE"},
        "high": {"icon": "**", "label": "SHOULD USE"},
        "medium": {"icon": "*", "label": "Consider"},
        "low": {"icon": "-", "label": "Optional"},
    })

    # Output by priority order
    for priority in ["critical", "high", "medium", "low"]:
        group = grouped.get(priority, [])
        if not group:
            continue

        level = priority_levels.get(priority, {"icon": "-", "label": priority})
        lines.append(f"{level['icon']} {level['label'].upper()}")
        lines.append("-" * 40)

        for skill_name, rule in group:
            enforcement = rule.get("enforcement", "suggest")
            tag = ""
            if enforcement == "warn":
                tag = " [WARN]"
            elif enforcement == "block":
                tag = " [REQUIRED]"
            lines.append(f"  - {skill_name}{tag}")

        lines.append("")

    lines.append("=" * 60)
    lines.append("  ACTION REQUIRED: Use Skill tool to load these skills")
    lines.append("  before proceeding. Skills contain project-specific")
    lines.append("  configurations, APIs, and constraints you MUST follow.")
    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)


def main():
    """Main function"""
    log_debug("=== Hook started ===")
    try:
        # Read stdin with size limit to prevent memory issues
        MAX_INPUT_SIZE = 50000  # 50KB

        # Check if stdin is available and readable
        stdin_closed = sys.stdin.closed
        stdin_readable = sys.stdin.readable() if hasattr(sys.stdin, 'readable') else True
        log_debug(f"stdin.closed={stdin_closed}, stdin.readable()={stdin_readable}")
        if stdin_closed or not stdin_readable:
            log_debug("stdin not readable, exiting silently (possibly --resume)")
            sys.exit(0)  # Exit cleanly, no error

        input_str = sys.stdin.read(MAX_INPUT_SIZE)
        log_debug(f"Read {len(input_str)} bytes from stdin")
        if not input_str or not input_str.strip():
            log_debug("empty input, exiting silently")
            sys.exit(0)  # Exit cleanly, no error

        try:
            hook_input = json.loads(input_str)
            log_debug("JSON parsed successfully")
        except json.JSONDecodeError as e:
            log_debug(f"ERROR: JSON parse error: {e}")
            log_debug(f"Input preview: {input_str[:500]!r}")
            return

        prompt = hook_input.get("prompt", "")
        if not prompt or not isinstance(prompt, str):
            return

        # Skip if prompt looks like raw logs/dumps (contains too many special chars)
        special_char_ratio = sum(1 for c in prompt[:1000] if c in '{}[]<>\\|') / min(len(prompt), 1000)
        if special_char_ratio > 0.1:  # More than 10% special characters
            return

        # Load rules
        rules = load_skill_rules()
        if not rules:
            return

        # Analyze and output recommendations
        matches = analyze_prompt(prompt, rules)
        recommendation = generate_recommendation(matches, rules)

        if recommendation:
            print(recommendation)

    except Exception as e:
        log_debug(f"EXCEPTION: {type(e).__name__}: {e}")
        import traceback
        log_debug(traceback.format_exc())


if __name__ == "__main__":
    main()
