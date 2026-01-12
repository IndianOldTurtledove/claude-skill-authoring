#!/usr/bin/env python3
"""Initialize a new skill from template."""

import argparse
import re
import stat
import sys
from pathlib import Path

SKILL_TEMPLATE = '''---
name: {name}
description: TODO: Describe what this skill does and when to use it.
---

# {title}

TODO: Brief overview of what this skill does.

## Quick Start

TODO: Essential usage example.

## Key Concepts

TODO: Core concepts Claude needs to know.

## Common Tasks

TODO: Step-by-step guides for common operations.
'''

EXAMPLE_SCRIPT = '''#!/usr/bin/env python3
"""Example utility script for {title}."""

import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: example.py <input>")
        sys.exit(1)

    input_arg = sys.argv[1]
    # TODO: Implement your logic here
    print(f"Processing: {{input_arg}}")


if __name__ == "__main__":
    main()
'''

EXAMPLE_REFERENCE = '''# {title} Reference

TODO: Detailed reference documentation.

## API Reference

TODO: Document APIs, methods, or interfaces.

## Examples

TODO: Provide concrete examples.
'''


def validate_name(name: str) -> bool:
    """Validate skill name format."""
    pattern = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'
    if not re.match(pattern, name):
        return False
    if len(name) > 40:
        return False
    if '--' in name:
        return False
    return True


def to_title(name: str) -> str:
    """Convert hyphen-case to Title Case."""
    return ' '.join(word.capitalize() for word in name.split('-'))


def init_skill(name: str, base_path: str = '.claude/skills') -> Path:
    """Initialize a new skill directory."""
    skill_path = Path(base_path) / name

    if skill_path.exists():
        print(f"Error: Skill directory already exists: {skill_path}")
        sys.exit(1)

    title = to_title(name)

    # Create directories
    skill_path.mkdir(parents=True)
    (skill_path / 'scripts').mkdir()
    (skill_path / 'references').mkdir()

    # Create SKILL.md
    (skill_path / 'SKILL.md').write_text(
        SKILL_TEMPLATE.format(name=name, title=title)
    )

    # Create example script
    script_path = skill_path / 'scripts' / 'example.py'
    script_path.write_text(EXAMPLE_SCRIPT.format(title=title))
    script_path.chmod(script_path.stat().st_mode | stat.S_IXUSR)

    # Create example reference
    (skill_path / 'references' / 'reference.md').write_text(
        EXAMPLE_REFERENCE.format(title=title)
    )

    return skill_path


def main():
    parser = argparse.ArgumentParser(
        description='Initialize a new Claude Code skill'
    )
    parser.add_argument(
        'name',
        help='Skill name (hyphen-case, e.g., "data-analyzer")'
    )
    parser.add_argument(
        '--path',
        default='.claude/skills',
        help='Base path for skills (default: .claude/skills)'
    )
    args = parser.parse_args()

    if not validate_name(args.name):
        print(f"Error: Invalid skill name '{args.name}'")
        print("Requirements:")
        print("  - Lowercase letters, digits, and hyphens only")
        print("  - Max 40 characters")
        print("  - No leading/trailing hyphens")
        print("  - No consecutive hyphens")
        sys.exit(1)

    skill_path = init_skill(args.name, args.path)

    print(f"Skill initialized: {skill_path}")
    print()
    print("Next steps:")
    print(f"  1. Edit {skill_path}/SKILL.md")
    print("  2. Add scripts to scripts/")
    print("  3. Add documentation to references/")
    print(f"  4. Validate: python .claude/skills/skill-authoring/scripts/quick_validate.py {skill_path}")


if __name__ == "__main__":
    main()
