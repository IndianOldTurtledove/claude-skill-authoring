#!/bin/bash
# Stop Hook: Verify Task Completion
#
# Event: Stop
# Purpose: Verify code integrity before task completion
#
# Checks:
# - Python syntax validation for modified .py files
# - Can be extended to check other file types
#
# Exit codes:
# - 0: All checks passed
# - 2: Verification failed (blocks completion)

# Check for recently modified Python files
MODIFIED_PY=$(git diff --name-only 2>/dev/null | grep '\.py$' | head -5)

if [ -n "$MODIFIED_PY" ]; then
    # Check Python syntax
    for file in $MODIFIED_PY; do
        if [ -f "$file" ]; then
            if ! python3 -m py_compile "$file" 2>&1; then
                echo "Verification failed: Python syntax error in $file" >&2
                echo "Please fix the syntax error before completing the task." >&2
                exit 2
            fi
        fi
    done
fi

exit 0
