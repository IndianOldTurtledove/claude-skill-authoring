# Claude Skill Authoring + Infrastructure

[中文](README.md) | [English](README_EN.md)

A Skill that teaches Claude how to write Skills, **plus a complete Claude Code infrastructure template**.

## What is This?

This project contains two parts:

1. **Skill Writing Guide** - Teaches Claude how to write efficient Skills following [Anthropic's official best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
2. **Infrastructure Templates** - Out-of-the-box Claude Code enhancements (hooks, agents, dev docs)

The infrastructure part is inspired by [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase).

## Quick Start

### One-Click Install (Recommended)

```bash
# Clone the repo
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git
cd claude-skill-authoring

# Install to your project
cd /path/to/your/project
/path/to/claude-skill-authoring/install.sh
```

### Install Only the Skill Guide

```bash
# Clone to global skills directory
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git ~/.claude/skills/skill-authoring

# Or clone to a specific project
git clone https://github.com/IndianOldTurtledove/claude-skill-authoring.git .claude/skills/skill-authoring
```

## Features Overview

### 1. Skill Writing Guide

When you ask questions about creating or improving Skills, Claude will automatically use this skill.

```bash
# Initialize a new skill
python scripts/init_skill.py my-skill-name

# Validate a skill
python scripts/quick_validate.py path/to/skill/

# Package for distribution
python scripts/package_skill.py path/to/skill/
```

### 2. Hooks System

Event-driven automation hooks:

| Hook | Event | Function |
|------|-------|----------|
| skill-activation-prompt | UserPromptSubmit | Analyze user input, recommend relevant Skills |
| post-tool-use-tracker | PostToolUse | Track file changes, suggest lint/type checks |

**How It Works**:

```
User input: "Help me design an API"
    |
    v
[skill-activation-prompt hook]
    |
    v
Output: "Recommend using backend-dev skill"
    |
    v
(Recommendation injected to Claude for decision making)
```

### 3. skill-rules.json

Centralized skill trigger rule configuration:

```json
{
  "skills": {
    "backend-dev": {
      "priority": "high",
      "triggers": {
        "promptTriggers": {
          "keywords": ["API", "backend", "database"],
          "intentPatterns": [".*design.*API.*"]
        },
        "fileTriggers": {
          "include": ["src/api/**/*.py"]
        }
      }
    }
  }
}
```

### 4. Dev Docs System

Cross-session context preservation, solving progress loss after Claude Code context resets:

```
dev/
├── active/
│   └── feature-xxx/
│       ├── feature-xxx-plan.md      # Strategic plan
│       ├── feature-xxx-context.md   # Session progress (update frequently!)
│       └── feature-xxx-tasks.md     # Task checklist
└── archive/                         # Completed tasks
```

### 5. Agent Templates

Specialized agents for specific tasks:

- **code-reviewer** - Code review
- **error-resolver** - Automatic error fixing

## Project Structure

```
claude-skill-authoring/
├── SKILL.md                    # Skill writing guide (main instructions)
├── install.sh                  # One-click install script
├── scripts/                    # Skill tool scripts
│   ├── init_skill.py
│   ├── quick_validate.py
│   └── package_skill.py
├── references/                 # Skill writing references
│   ├── output-patterns.md
│   └── workflows.md
├── templates/                  # Infrastructure templates
│   ├── hooks/                  # Hook templates
│   │   ├── skill-activation-prompt.py
│   │   ├── post-tool-use-tracker.py
│   │   └── README.md
│   ├── skill-rules.json        # Trigger rules template
│   ├── settings.local.json     # Config template
│   ├── dev-docs/               # Dev docs templates
│   │   ├── TEMPLATE-plan.md
│   │   ├── TEMPLATE-context.md
│   │   └── TEMPLATE-tasks.md
│   └── agents/                 # Agent templates
│       ├── code-reviewer.md
│       └── error-resolver.md
└── examples/                   # Complete examples
    └── full-project/
```

## Skill Writing Core Concepts

### Three-Layer Loading Architecture

| Layer | Load Time | Token Cost | Content |
|-------|-----------|------------|---------|
| L1: Metadata | Startup | ~100 tokens | name + description |
| L2: Instructions | Trigger | <5k tokens | SKILL.md body |
| L3: Resources | On-demand | Unlimited | scripts/, references/ |

### YAML Frontmatter

```yaml
---
name: my-skill-name      # lowercase, hyphens, max 64 chars
description: Does X for Y. Use when handling Y or user mentions X.
---
```

### Core Principles

1. **Concise** - Claude is smart, only add what it doesn't know
2. **Freedom matches fragility** - High freedom for flexible tasks, low for critical operations
3. **Progressive disclosure** - Keep SKILL.md < 500 lines, split details to references/
4. **One-level deep references** - Avoid nested file references

## Acknowledgments

- [Anthropic Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase) - Inspiration for infrastructure patterns

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Feel free to submit a Pull Request.
