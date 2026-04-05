#!/usr/bin/env bash
# validate-python.sh — Python naming + structure convention checker for simurgh-dns
set -euo pipefail

PROJECT_ROOT="${1:-.}"
SRC_DIR="$PROJECT_ROOT/src/simurgh"
TESTS_DIR="$PROJECT_ROOT/tests"
ERRORS=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

pass_check() { echo -e "  ${GREEN}✓${NC} $1"; }
fail_check() { echo -e "  ${RED}✗${NC} $1"; ERRORS=$((ERRORS + 1)); }
warn_check() { echo -e "  ${YELLOW}⚠${NC} $1"; }

echo "=== Python Convention Validator — simurgh-dns ==="
echo ""

# 1. Check for relative imports
echo "Checking imports..."
if grep -rn "^from \.\." "$SRC_DIR" 2>/dev/null; then
    fail_check "Relative imports found — use absolute imports only"
else
    pass_check "No relative imports"
fi

# 2. Check for os.path usage
if grep -rn "import os\.path\|from os\.path\|os\.path\." "$SRC_DIR" 2>/dev/null; then
    fail_check "os.path usage found — use pathlib.Path"
else
    pass_check "No os.path usage"
fi

# 3. Check for Optional[] usage
if grep -rn "Optional\[" "$SRC_DIR" 2>/dev/null; then
    fail_check "Optional[] found — use X | None syntax"
else
    pass_check "No Optional[] usage"
fi

# 4. Check for typing imports of deprecated generics
if grep -rn "from typing import.*\(Dict\|List\|Tuple\|Set\)" "$SRC_DIR" 2>/dev/null; then
    fail_check "Deprecated typing generics found — use lowercase builtins"
else
    pass_check "No deprecated typing generics"
fi

# 5. Check module docstrings
echo ""
echo "Checking docstrings..."
for f in "$SRC_DIR"/*.py "$SRC_DIR"/**/*.py 2>/dev/null; do
    [ -f "$f" ] || continue
    if ! head -1 "$f" | grep -q '"""'; then
        warn_check "Missing module docstring: $f"
    fi
done

# 6. Check pyproject.toml exists
echo ""
echo "Checking project structure..."
if [ -f "$PROJECT_ROOT/pyproject.toml" ]; then
    pass_check "pyproject.toml exists"
else
    fail_check "pyproject.toml missing"
fi

# 7. Check no setup.py or requirements.txt
if [ -f "$PROJECT_ROOT/setup.py" ]; then
    fail_check "setup.py found — use pyproject.toml"
else
    pass_check "No setup.py"
fi

if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
    warn_check "requirements.txt found — prefer pyproject.toml dependencies"
else
    pass_check "No requirements.txt"
fi

# 8. Check src layout
if [ -d "$SRC_DIR" ]; then
    pass_check "src/simurgh/ layout exists"
else
    warn_check "src/simurgh/ layout not found"
fi

# 9. Check tests directory
if [ -d "$TESTS_DIR" ]; then
    pass_check "tests/ directory exists"
else
    warn_check "tests/ directory not found"
fi

# 10. Check for print() in source (should use logging)
echo ""
echo "Checking code quality..."
if grep -rn "^\s*print(" "$SRC_DIR" 2>/dev/null | grep -v "# noqa" | head -5; then
    warn_check "print() calls found — prefer structured logging"
else
    pass_check "No print() calls in source"
fi

# 11. Check for shell=True in subprocess
if grep -rn "shell=True" "$SRC_DIR" 2>/dev/null; then
    fail_check "shell=True found in subprocess — security risk"
else
    pass_check "No shell=True usage"
fi

# Summary
echo ""
echo "=== Summary ==="
if [ "$ERRORS" -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
else
    echo -e "${RED}$ERRORS error(s) found.${NC}"
    exit 1
fi
