#!/usr/bin/env python3
"""Package a skill into a distributable .skill file."""

import os
import sys
import zipfile
from pathlib import Path

# Import validation from sibling module
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from quick_validate import validate_skill


def package_skill(skill_path: str, output_dir: str | None = None) -> Path | None:
    """
    Package a skill folder into a .skill file (ZIP format).

    Args:
        skill_path: Path to the skill directory
        output_dir: Optional output directory (defaults to current dir)

    Returns:
        Path to the created .skill file, or None on failure
    """
    path = Path(skill_path)

    if not path.exists() or not path.is_dir():
        print(f"Error: Skill directory not found: {skill_path}")
        return None

    # Validate before packaging
    print(f"Validating {skill_path}...")
    is_valid, errors = validate_skill(skill_path)

    if not is_valid:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return None

    print("Validation passed")

    # Determine output path
    skill_name = path.name
    output_path = Path(output_dir) if output_dir else Path('.')
    output_file = output_path / f"{skill_name}.skill"

    # Create ZIP file
    print(f"Creating {output_file}...")

    try:
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(path):
                # Skip __pycache__ and hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

                for file in files:
                    if file.startswith('.'):
                        continue

                    file_path = Path(root) / file
                    arc_name = file_path.relative_to(path)
                    zf.write(file_path, arc_name)
                    print(f"  + {arc_name}")

        print(f"Package created: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error creating package: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Usage: package_skill.py <skill-path> [output-directory]")
        sys.exit(1)

    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    result = package_skill(skill_path, output_dir)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
