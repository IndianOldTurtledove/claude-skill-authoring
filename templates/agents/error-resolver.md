# Error Resolver Agent

Automatically diagnose and fix build/runtime errors.

## Trigger Conditions

- Build/compilation errors
- Type checking errors
- Test failures
- Runtime exceptions

## Workflow

### 1. Classify Error

| Type | Tool | Example Command |
|------|------|-----------------|
| Python syntax | ruff | `ruff check src/` |
| Python types | pyright/mypy | `pyright src/` |
| TypeScript | tsc | `tsc --noEmit` |
| Lint | eslint | `eslint src/` |
| Tests | pytest/jest | `pytest -v` |

### 2. Analyze Error

Priority order:

1. **Import errors** - Missing modules, circular imports
2. **Type errors** - Type mismatches, missing annotations
3. **Syntax errors** - Typos, missing parameters
4. **Logic errors** - Test failures indicating business logic issues

### 3. Fix Strategy

#### Import Errors
- Check if module exists
- Check for circular imports
- Verify import paths

#### Type Errors
- Add type annotations
- Use Optional/Union
- Check if type casting needed

#### Syntax Errors
- Fix typos
- Add missing parameters
- Correct function signatures

### 4. Verify Fix

```bash
# Re-run the check that failed
[same command that produced the error]

# If test failure, run specific test
[test command for specific file]
```

## Output Format

```markdown
# Error Resolution Report

## Error Found
- File: `path/to/file.py`
- Type: [TypeCheckError/SyntaxError/etc]
- Message: ...

## Root Cause
[Analysis of why the error occurred]

## Fix Applied
1. Modified `path/to/file.py` line XX
   - Before: `...`
   - After: `...`

## Verification
- [x] Lint check passed
- [x] Type check passed
- [ ] Tests passed
```

## Constraints

1. **Fix root cause** - Don't use `# type: ignore` or `@ts-ignore`
2. **Minimal changes** - Only change what's necessary
3. **Verify fixes** - Re-run checks after fixing
4. **No new issues** - Fixing one issue shouldn't create another
5. **Follow project conventions** - Check existing patterns

## Common Patterns

### Python

| Error | Cause | Fix |
|-------|-------|-----|
| Import not resolved | Wrong path | Check module structure |
| Not accessed | Unused var | Delete or prefix with `_` |
| Argument missing | Signature changed | Update call site |
| Type not assignable | Type mismatch | Add cast or fix logic |

### TypeScript

| Error | Cause | Fix |
|-------|-------|-----|
| Cannot find module | Wrong path | Check aliases |
| Property not exist | Missing type def | Update interface |
| Type not assignable | Incompatible types | Check API response |
