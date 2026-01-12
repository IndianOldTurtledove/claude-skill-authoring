# Claude Skill Authoring

[English](README.md) | [中文](README_CN.md)

A Claude Code Skill for creating and validating Claude Code Skills. Meta, right?

## What is this?

This is a skill that teaches Claude how to write effective Skills following [Anthropic's official best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

## Installation

### Claude Code (Recommended)

```bash
# Clone to your global skills directory
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git ~/.claude/skills/skill-authoring

# Or clone to a specific project
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git .claude/skills/skill-authoring
```

### Manual

Copy the contents to `.claude/skills/skill-authoring/` in your project or `~/.claude/skills/skill-authoring/` globally.

## Usage

Once installed, Claude will automatically use this skill when you ask about creating or improving Skills.

### Quick Commands

```bash
# Initialize a new skill
python ~/.claude/skills/skill-authoring/scripts/init_skill.py my-skill-name

# Validate a skill
python ~/.claude/skills/skill-authoring/scripts/quick_validate.py path/to/skill/

# Package for distribution
python ~/.claude/skills/skill-authoring/scripts/package_skill.py path/to/skill/
```

### Example Conversation

```
You: Help me create a skill for processing CSV files

Claude: I'll help you create a CSV processing skill. Let me initialize it first...
[Uses init_skill.py to create the structure]
[Writes SKILL.md with proper frontmatter]
[Validates with quick_validate.py]
```

## Skill Structure

```
skill-authoring/
├── SKILL.md                    # Main instructions (loaded when triggered)
├── scripts/
│   ├── init_skill.py          # Initialize new skills from template
│   ├── quick_validate.py      # Validate skill structure and frontmatter
│   └── package_skill.py       # Package skill for distribution
└── references/
    ├── output-patterns.md     # Template and examples patterns
    └── workflows.md           # Sequential, conditional, feedback loop patterns
```

## Key Concepts

### Three-Level Loading

| Level | When | Token Cost | Content |
|-------|------|------------|---------|
| L1: Metadata | Startup | ~100 tokens | name + description |
| L2: Instructions | Triggered | <5k tokens | SKILL.md body |
| L3: Resources | As needed | Unlimited | scripts/, references/ |

### YAML Frontmatter

```yaml
---
name: my-skill-name      # lowercase, hyphens, max 64 chars
description: Does X for Y. Use when working with Y or when user mentions X.
---
```

### Core Principles

1. **Be Concise** - Claude is smart, only add what it doesn't know
2. **Match Freedom to Fragility** - High freedom for flexible tasks, low for critical operations
3. **Progressive Disclosure** - Keep SKILL.md < 500 lines, split details to references/
4. **One-Level Deep References** - Avoid nested file references

## Validation Rules

The `quick_validate.py` script checks:

- SKILL.md exists with valid YAML frontmatter
- `name`: lowercase, hyphens, max 64 chars, no "anthropic"/"claude"
- `description`: max 1024 chars, no angle brackets
- SKILL.md body < 500 lines
- No Windows-style paths

## Resources

- [Anthropic Skills Repository](https://github.com/anthropics/skills) - Official skills from Anthropic
- [Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) - Official documentation
- [Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) - Architecture explanation
- [awesome-claude-skills](https://github.com/travisvn/awesome-claude-skills) - Community skills collection

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
