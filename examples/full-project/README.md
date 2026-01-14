# Full Project Example

This is a complete example showing all Claude Code infrastructure components working together.

## Structure

```
full-project/
├── .claude/
│   ├── hooks/                      # Event hooks
│   │   ├── skill-activation-prompt.py
│   │   ├── skill-activation-prompt.sh
│   │   ├── post-tool-use-tracker.py
│   │   └── post-tool-use-tracker.sh
│   ├── skills/
│   │   └── skill-rules.json        # Trigger rules
│   ├── agents/
│   │   ├── code-reviewer.md
│   │   └── error-resolver.md
│   ├── rules/
│   │   └── example-rule.md         # Project rules
│   └── settings.local.json         # Hooks config
├── dev/
│   ├── active/                     # In-progress tasks
│   └── archive/                    # Completed tasks
└── src/                            # Your code here
```

## How to Use

1. Copy this entire directory to your project root
2. Customize `skill-rules.json` for your skills
3. Edit `post-tool-use-tracker.py` CHECK_COMMANDS for your toolchain
4. Restart Claude Code

## Testing

```bash
# Test skill activation
echo '{"prompt": "help me design an API"}' | python3 .claude/hooks/skill-activation-prompt.py

# Test file tracker
echo '{"tool_name": "Edit", "tool_input": {"file_path": "src/main.py"}}' | python3 .claude/hooks/post-tool-use-tracker.py
```
