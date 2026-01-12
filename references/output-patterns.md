# Output Patterns

Patterns for creating consistent, quality outputs.

## Template Pattern

### Strict Template

Use for outputs requiring exact format (APIs, data structures):

```markdown
## Report Structure

ALWAYS use this exact structure:

# [Title]

## Executive Summary
[One paragraph overview]

## Key Findings
- Finding 1 with data
- Finding 2 with data

## Recommendations
1. Specific action
2. Specific action
```

### Flexible Template

Use when adaptation improves results:

```markdown
## Report Structure

Sensible default, adapt as needed:

# [Title]

## Summary
[Adapt based on analysis]

## Findings
[Tailor to context]
```

## Examples Pattern

Provide input/output pairs for quality-dependent tasks:

```markdown
## Commit Message Format

**Example 1:**
Input: Added user authentication with JWT
Output:
feat(auth): implement JWT-based authentication

Add login endpoint and token validation

**Example 2:**
Input: Fixed date display bug in reports
Output:
fix(reports): correct date formatting

Use UTC timestamps consistently
```

## Choosing the Right Pattern

| Output Type | Pattern | Freedom |
|-------------|---------|---------|
| API responses | Strict template | Low |
| Data formats | Strict template | Low |
| Reports | Flexible template | Medium |
| Creative content | Examples | High |
| Code style | Examples | Medium |

## Key Insight

Match strictness to actual needs. Don't apply one pattern uniformly.
