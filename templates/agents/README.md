# Claude Code Agents

Specialized agents for specific tasks in your Claude Code workflow.

Inspired by [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase).

## What Are Agents?

Agents are specialized prompts that provide structured workflows for specific tasks. They're invoked via the Task tool with detailed instructions.

## Available Agent Templates

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| code-reviewer | Code review | After completing a feature |
| error-resolver | Fix errors | When encountering build/runtime errors |
| refactor-planner | Plan refactoring | Before major code restructuring |

## How to Use

Reference agent files when using the Task tool:

```
Use the Task tool with subagent_type="general-purpose",
include the agent instructions in the prompt
```

Or read the agent file first and follow its workflow manually.

## Creating Custom Agents

1. Create `your-agent.md` in `.claude/agents/`
2. Follow the template structure:
   - Trigger conditions
   - Workflow steps
   - Output format
   - Constraints/rules
3. Document in this README

## Agent File Structure

```markdown
# Agent Name

[Brief description]

## Trigger Conditions
[When to use this agent]

## Workflow
### Step 1: ...
### Step 2: ...
### Step 3: ...

## Output Format
[Expected output structure]

## Constraints
[Rules the agent must follow]
```

## Best Practices

1. **Be specific** - Clear trigger conditions
2. **Step-by-step** - Break down complex workflows
3. **Output structure** - Define expected format
4. **Constraints** - Set boundaries
