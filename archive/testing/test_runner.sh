#!/bin/bash
# Rapid testing script for AVM project
# Usage: ./test_runner.sh

echo "🧪 Running all tests..."
echo ""

# Activate venv
source venv/bin/activate

# Run tests with coverage
pytest test_*.py -v --cov=app --cov-report=term-missing 2>&1 | tee test_results.txt

# Extract summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 TEST SUMMARY:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
grep -E "(passed|failed|error)" test_results.txt | tail -1

# Check coverage
echo ""
echo "📈 COVERAGE:"
coverage report --include="app.py" | grep "TOTAL" || echo "No coverage data"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Exit code
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ TESTS FAILED - Check output above"
    exit 1
fi
