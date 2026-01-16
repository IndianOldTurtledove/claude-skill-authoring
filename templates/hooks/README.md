# Claude Code Hooks Templates

Event-driven automation hooks for Claude Code.

Inspired by [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase).

## Available Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| skill-activation-prompt | UserPromptSubmit | Auto-recommend skills based on user input |
| debug-mode-detector | UserPromptSubmit | Detect debug scenarios, activate systematic debugging |
| investigation-guard | PreToolUse | Enforce investigation before code modification |
| post-tool-use-tracker | PostToolUse | Track file changes, suggest lint/type checks |
| verification-guard | Stop | Verify code integrity before task completion |

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
          },
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/debug-mode-detector.py\"",
            "timeout": 3,
            "statusMessage": "Checking for debug scenario..."
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Read|Grep|Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/investigation-guard.py\"",
            "timeout": 3,
            "statusMessage": "Checking investigation status..."
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
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/verification-guard.sh\"",
            "timeout": 15,
            "statusMessage": "Verifying code changes..."
          }
        ]
      }
    ]
  }
}
```

## Hook Descriptions

### skill-activation-prompt

Automatically analyzes user prompts and recommends relevant skills based on keyword matching and intent patterns.

**Requires**: `skill-rules.json` in `.claude/skills/`. See `templates/skill-rules.json` for format.

### debug-mode-detector

Intelligently detects debug/bug-fix scenarios using a scoring mechanism:

- **Technical signals**: Error types, stack traces, line numbers, file paths
- **Problem words**: "bug", "fix", "broken", "报错", "崩溃", etc.
- **Frustration signals**: Profanity, repeated attempts, confusion markers
- **Context accumulation**: Tracks session frustration, stricter after multiple triggers

When triggered, outputs a systematic debugging prompt enforcing:
1. Root cause investigation before fixes
2. Pattern analysis against working code
3. Single hypothesis testing
4. Verification after implementation

### investigation-guard

Prevents blind code modifications by enforcing a "Read before Edit" policy:

- Tracks which files have been Read/Grep'd
- First edit attempt on uninvestigated file: **Warning**
- Second+ edit attempt: **Block** (exit code 2)
- State resets after 1 hour

This ensures Claude understands code context before making changes.

### post-tool-use-tracker

Tracks file modifications and suggests appropriate check commands based on file type.

**Customize** `CHECK_COMMANDS` dict in `post-tool-use-tracker.py`:

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

### verification-guard

Runs at task completion to verify code integrity:

- Checks Python syntax for modified `.py` files
- Blocks completion if syntax errors found (exit code 2)
- Can be extended for other file types

## How It Works

```
User Input
    |
    v
[UserPromptSubmit Hooks]
    |
    +---> skill-activation-prompt.py
    |         +---> Load skill-rules.json
    |         +---> Match keywords/patterns
    |         +---> Output recommendations
    |
    +---> debug-mode-detector.py
              +---> Calculate frustration score
              +---> If threshold met, output debug prompt
    |
    v
Model Response
    |
    v
[PreToolUse Hook] (before Edit/Write)
    |
    +---> investigation-guard.py
              +---> Check if file was Read first
              +---> Warn or block if not
    |
    v
[Tool Execution]
    |
    v
[PostToolUse Hook] (after Edit/Write)
    |
    +---> post-tool-use-tracker.py
              +---> Track modified files
              +---> Suggest check commands
    |
    v
[Stop Hook] (task completion)
    |
    +---> verification-guard.sh
              +---> Verify Python syntax
              +---> Block if errors found
```

## Requirements

- Python 3.10+
- No external dependencies (uses stdlib only)
- Bash for shell scripts

## Testing

```bash
# Test skill-activation-prompt
echo '{"prompt": "help me design an API"}' | python3 skill-activation-prompt.py

# Test debug-mode-detector
echo '{"prompt": "TypeError on line 42, crashed again!"}' | python3 debug-mode-detector.py

# Test investigation-guard (simulating Edit without prior Read)
echo '{"tool_name": "Edit", "tool_input": {"file_path": "src/main.py"}}' | python3 investigation-guard.py

# Test post-tool-use-tracker
echo '{"tool_name": "Edit", "tool_input": {"file_path": "src/main.py"}}' | python3 post-tool-use-tracker.py

# Test verification-guard
bash verification-guard.sh
```

## State Files

Some hooks maintain state files in `~/.claude/`:

| File | Hook | Purpose |
|------|------|---------|
| `debug-detector-state.json` | debug-mode-detector | Track cumulative frustration, trigger count |
| `investigation-state.json` | investigation-guard | Track investigated files, edit attempts |

These files auto-clean old entries (30 min for debug, 1 hour for investigation).
