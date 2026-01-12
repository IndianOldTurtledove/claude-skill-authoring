#!/usr/bin/env python3
"""Quick validation for Claude Code skills."""

import re
import sys
from pathlib import Path

ALLOWED_PROPERTIES = {'name', 'description', 'license', 'allowed-tools', 'metadata'}
NAME_PATTERN = re.compile(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$')
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_SKILL_LINES = 500


def validate_skill(skill_path: str) -> tuple[bool, list[str]]:
    """
    Validate a skill directory.

    Returns:
        (is_valid, list of error messages)
    """
    errors = []
    path = Path(skill_path)

    # Check directory exists
    if not path.exists():
        return False, [f"Path does not exist: {skill_path}"]

    if not path.is_dir():
        return False, [f"Path is not a directory: {skill_path}"]

    # Check SKILL.md exists
    skill_md = path / 'SKILL.md'
    if not skill_md.exists():
        return False, ["SKILL.md not found"]

    content = skill_md.read_text(encoding='utf-8')

    # Check frontmatter exists
    if not content.startswith('---'):
        return False, ["Missing YAML frontmatter (must start with ---)"]

    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return False, ["Invalid frontmatter format (must be enclosed in ---)"]

    frontmatter_text = parts[1].strip()
    body = parts[2]

    # Parse frontmatter (simple key: value)
    frontmatter = {}
    for line in frontmatter_text.split('\n'):
        line = line.strip()
        if not line:
            continue
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Check required fields
    if 'name' not in frontmatter:
        errors.append("Missing required field: name")
    else:
        name = frontmatter['name']
        if not isinstance(name, str):
            errors.append("name must be a string")
        elif not NAME_PATTERN.match(name):
            errors.append(f"Invalid name format: {name}")
        elif len(name) > MAX_NAME_LENGTH:
            errors.append(f"name too long: {len(name)} > {MAX_NAME_LENGTH}")
        elif '--' in name:
            errors.append("name cannot contain consecutive hyphens")
        elif 'anthropic' in name.lower() or 'claude' in name.lower():
            errors.append("name cannot contain 'anthropic' or 'claude'")

    if 'description' not in frontmatter:
        errors.append("Missing required field: description")
    else:
        desc = frontmatter['description']
        if not isinstance(desc, str):
            errors.append("description must be a string")
        elif '<' in desc and '>' in desc:
            errors.append("description cannot contain angle brackets")
        elif len(desc) > MAX_DESCRIPTION_LENGTH:
            errors.append(f"description too long: {len(desc)} > {MAX_DESCRIPTION_LENGTH}")

    # Check for unknown properties
    unknown = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unknown:
        errors.append(f"Unknown frontmatter properties: {unknown}")

    # Check body length
    line_count = len(body.strip().split('\n'))
    if line_count > MAX_SKILL_LINES:
        errors.append(f"SKILL.md body too long: {line_count} > {MAX_SKILL_LINES} lines")

    # Check for Windows paths (actual paths like C:\Users or scripts\file.py)
    windows_path_pattern = re.compile(r'[A-Za-z]:\\|\\[a-zA-Z0-9_-]+\.[a-zA-Z]+')
    if windows_path_pattern.search(content):
        errors.append("Contains Windows-style paths (use / instead)")

    return len(errors) == 0, errors


def main():
    if len(sys.argv) < 2:
        print("Usage: quick_validate.py <skill-directory>")
        sys.exit(1)

    skill_path = sys.argv[1]
    is_valid, errors = validate_skill(skill_path)

    if is_valid:
        print(f"Skill '{skill_path}' is valid")
        sys.exit(0)
    else:
        print(f"Skill '{skill_path}' has errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
