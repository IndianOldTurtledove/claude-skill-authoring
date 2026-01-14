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
from pathlib import Path
from typing import Any

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
    prompt_lower = prompt.lower()
    prompt_triggers = triggers.get("promptTriggers", {})

    # Keyword matching
    for keyword in prompt_triggers.get("keywords", []):
        if keyword.lower() in prompt_lower:
            return True

    # Intent pattern matching (regex)
    for pattern in prompt_triggers.get("intentPatterns", []):
        try:
            if re.search(pattern, prompt, re.IGNORECASE):
                return True
        except re.error:
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
        "critical": {"icon": "!!", "label": "Required"},
        "high": {"icon": "**", "label": "Recommended"},
        "medium": {"icon": "*", "label": "Suggested"},
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
    lines.append("  Use: Skill tool to invoke recommended skills")
    lines.append("=" * 60)
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

        prompt = hook_input.get("prompt", "")
        if not prompt:
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
        print(f"[skill-activation] Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
