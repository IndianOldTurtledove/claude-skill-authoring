# Dev Docs - Cross-Session Context System

Preserve implementation decisions, progress, and constraints across Claude Code context resets.

Inspired by [claude-code-infrastructure-showcase](https://github.com/diet103/claude-code-infrastructure-showcase).

## When to Use

| Scenario | Use Dev Docs? |
|----------|---------------|
| Tasks > 2 hours | Yes |
| Multi-session features | Yes |
| Complex multi-file changes | Yes |
| Simple bug fixes | No |
| Single-file changes | No |

## Directory Structure

```
dev/
├── README.md           # This file
├── active/             # In-progress tasks
│   └── [task-name]/
│       ├── [task-name]-plan.md      # Strategic plan
│       ├── [task-name]-context.md   # Session progress (update frequently!)
│       └── [task-name]-tasks.md     # Task checklist
└── archive/            # Completed tasks (for reference)
    └── [old-task]/
```

## The Three-File Pattern

### 1. plan.md - Strategic Plan

Create at task start:

```markdown
# [Task Name] Implementation Plan

## Goal
Brief description of what to accomplish

## Design Decisions
- Chose approach A over B because...
- Tech stack choices...

## Implementation Phases
1. Phase 1: ...
2. Phase 2: ...

## Acceptance Criteria
- [ ] Feature A works
- [ ] Tests pass
- [ ] Docs updated

## Risks & Constraints
- Risk: ...
- Constraint: ...

## Key Files
- src/api/routers/xxx.py
- src/components/XxxView.vue
```

### 2. context.md - Session Progress (Critical!)

**Update after every milestone**:

```markdown
# [Task Name] Context

## Last Updated
2024-01-15 15:30

## Current Status
[One-line description of current work]

## Session Progress

### Completed
- [x] Created API endpoint /api/xxx
- [x] Implemented frontend component XxxView.vue

### In Progress
- [ ] Working on form validation

### Blockers
- Need to confirm XXX data format

## Key Discoveries
- Found YYY requires ZZZ first
- DB schema needs adjustment

## Next Session
Continue from form validation, refer to src/api/schemas/xxx.py
```

### 3. tasks.md - Task Checklist

Checkbox format for tracking:

```markdown
# [Task Name] Tasks

## Phase 1: Infrastructure
- [x] Create database model
- [x] Create API Schema
- [ ] Implement CRUD endpoints

## Phase 2: Frontend
- [ ] Create list page
- [ ] Create detail page
- [ ] Create edit form

## Phase 3: Testing
- [ ] Unit tests
- [ ] Integration tests
```

## Workflow

### Starting a New Task

```bash
# 1. Create task directory
mkdir -p dev/active/feature-xxx

# 2. Create the three files
touch dev/active/feature-xxx/feature-xxx-{plan,context,tasks}.md

# 3. Fill in the plan
```

### Each Session

1. **Start**: Read context.md to understand current state
2. **During**: Update context.md after milestones
3. **End**: Update tasks.md and context.md

### Completing a Task

```bash
# Move to archive
mv dev/active/feature-xxx dev/archive/
```

## Key Principles

1. **context.md is core** - Update it frequently
2. **Record decision reasons** - Not just what, but why
3. **Keep it concise** - Bullet points, not essays
4. **Update promptly** - After each phase, not at the end
