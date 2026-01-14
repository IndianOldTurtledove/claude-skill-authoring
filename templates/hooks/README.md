# Claude Code Hooks Templates

Event-driven automation hooks for Claude Code.

Inspired by [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase).

## Available Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| skill-activation-prompt | UserPromptSubmit | Auto-recommend skills based on user input |
| post-tool-use-tracker | PostToolUse | Track file changes, suggest lint/type checks |

## Installation

### Copy to your project

```bash
cp -r templates/hooks/ .claude/hooks/
chmod +x .claude/hooks/*.sh
```

### Register in settings.json

Add to `.claude/settings.local.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/skill-activation-prompt.sh",
            "timeout": 5,
            "statusMessage": "Analyzing prompt..."
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit|NotebookEdit",
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/post-tool-use-tracker.sh",
            "timeout": 3,
            "statusMessage": "Tracking changes..."
          }
        ]
      }
    ]
  }
}
```

## Customization

### skill-activation-prompt

Requires `skill-rules.json` in `.claude/skills/`. See `templates/skill-rules.json` for format.

### post-tool-use-tracker

Edit `CHECK_COMMANDS` dict in `post-tool-use-tracker.py` to customize:

```python
CHECK_COMMANDS = {
    ".py": {
        "lint": "ruff check {file}",
        "format": "black {file}",
        "type": "mypy {file}",
    },
    ".ts": {
        "lint": "eslint {file}",
        "type": "tsc --noEmit",
    },
    # Add your own...
}
```

## How It Works

```
User Input
    |
    v
[UserPromptSubmit Hook]
    |
    +---> skill-activation-prompt.py
    |         |
    |         +---> Load skill-rules.json
    |         +---> Match keywords/patterns
    |         +---> Output recommendations (to model context)
    |
    v
Model Response
    |
    v
[PostToolUse Hook] (on Edit/Write)
    |
    +---> post-tool-use-tracker.py
              |
              +---> Track modified files
              +---> Suggest check commands (to model context)
```

## Requirements

- Python 3.10+
- No external dependencies (uses stdlib only)

## Testing

```bash
# Test skill-activation-prompt
echo '{"prompt": "help me design an API"}' | python3 skill-activation-prompt.py

# Test post-tool-use-tracker
echo '{"tool_name": "Edit", "tool_input": {"file_path": "src/main.py"}}' | python3 post-tool-use-tracker.py
```
