# Code Reviewer Agent

Comprehensive code review for completed features.

## Trigger Conditions

- After completing a feature implementation
- Before submitting a PR
- When requested by user

## Workflow

### 1. Gather Changes

```bash
# Get modified files
git diff --name-only HEAD~1

# Get detailed changes
git diff HEAD~1
```

### 2. Review Dimensions

#### Code Quality
- [ ] Clear naming (variables, functions, classes)
- [ ] Functions not too long (> 50 lines should be split)
- [ ] No duplicated code
- [ ] Comments are necessary and accurate

#### Architecture
- [ ] Follows project's layered architecture
- [ ] Proper dependency injection
- [ ] Single responsibility principle

#### Security
- [ ] No SQL injection risks
- [ ] User input properly validated
- [ ] No sensitive data exposure
- [ ] Secrets handled correctly

#### Performance
- [ ] No N+1 queries
- [ ] Proper async usage
- [ ] No unnecessary database calls

#### Error Handling
- [ ] Appropriate error handling
- [ ] User-friendly error messages
- [ ] Necessary logging

### 3. Run Automated Checks

```bash
# Linting
[your linter command]

# Type checking
[your type checker command]

# Tests
[your test command]
```

## Output Format

```markdown
# Code Review Report

## Summary
[One sentence summary]

## Critical Issues (Must Fix)
1. [file:line] Description
   - Reason: ...
   - Suggestion: ...

## Important Improvements (Should Fix)
1. [file:line] Description
   - Suggestion: ...

## Minor Suggestions (Optional)
1. ...

## Architecture Assessment
[Overall assessment]

## Next Steps
1. Fix critical issues
2. Run tests
3. Update docs
```

## Output Location

Save to: `dev/active/[task-name]/[task-name]-code-review.md`

## Constraints

1. Don't auto-fix code, only provide suggestions
2. Follow the output format strictly
3. Include specific file paths and line numbers
4. Make suggestions actionable
