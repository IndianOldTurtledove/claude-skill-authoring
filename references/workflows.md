# Workflow Patterns

Patterns for structuring multi-step tasks.

## Sequential Workflow

For tasks with natural progression:

```markdown
## PDF Form Workflow

1. **Analyze**: `python scripts/analyze.py form.pdf`
2. **Map fields**: Edit `fields.json`
3. **Validate**: `python scripts/validate.py fields.json`
4. **Fill**: `python scripts/fill.py form.pdf fields.json output.pdf`
5. **Verify**: `python scripts/verify.py output.pdf`
```

### With Checklist

For complex tasks, provide a copyable checklist:

```markdown
## Document Processing

Copy this checklist:

- [ ] Step 1: Analyze input
- [ ] Step 2: Transform data
- [ ] Step 3: Validate output
- [ ] Step 4: Generate report

**Step 1: Analyze**
Run: `python scripts/analyze.py input.file`
...
```

## Conditional Workflow

For tasks with decision points:

```markdown
## Document Workflow

1. Determine task type:

   **Creating new?** -> Follow "Creation" below
   **Editing existing?** -> Follow "Editing" below

2. Creation workflow:
   - Use template library
   - Build from scratch
   - Export

3. Editing workflow:
   - Unpack existing
   - Modify content
   - Validate
   - Repack
```

## Feedback Loop

For quality-critical operations:

```markdown
## Editing Process

1. Make edits
2. **Validate**: `python scripts/validate.py`
3. If errors:
   - Review error message
   - Fix issue
   - Return to step 2
4. **Only proceed when validation passes**
5. Finalize output
```

## Plan-Validate-Execute

For complex, error-prone operations:

```markdown
## Batch Update

1. **Plan**: Generate changes
   python scripts/analyze.py input.xlsx > changes.json

2. **Validate**: Check plan
   python scripts/validate_plan.py changes.json
   Fix errors before proceeding.

3. **Execute**: Apply changes
   python scripts/apply.py input.xlsx changes.json output.xlsx

4. **Verify**: Check results
   python scripts/verify.py output.xlsx
```

## Choosing the Right Pattern

| Task Type | Pattern |
|-----------|---------|
| Linear steps | Sequential |
| Complex/trackable | Sequential + Checklist |
| Decision points | Conditional |
| Quality-critical | Feedback Loop |
| High-risk batch | Plan-Validate-Execute |
