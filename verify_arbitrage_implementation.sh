#!/bin/bash
# Arbitrage Score Filter - Final Verification
# Checks all components are in place and working

echo "🔍 Arbitrage Score Filter - Final Verification"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
PASS=0
FAIL=0

# Function to check and report
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC} - $1"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC} - $1"
        ((FAIL++))
    fi
}

echo "📋 Component Checks:"
echo ""

# 1. Check database migration file
if [ -f "migrations/add_arbitrage_score_column.sql" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Database migration file exists"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Database migration file missing"
    ((FAIL++))
fi

# 2. Check frontend dropdown in HTML
if grep -q "arbitrage-score-min" templates/index.html; then
    echo -e "${GREEN}✅ PASS${NC} - Frontend dropdown HTML present"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Frontend dropdown HTML missing"
    ((FAIL++))
fi

# 3. Check JavaScript capture
if grep -q "const arbitrageScoreMin" templates/index.html; then
    echo -e "${GREEN}✅ PASS${NC} - JavaScript parameter capture present"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - JavaScript parameter capture missing"
    ((FAIL++))
fi

# 4. Check JavaScript request building
if grep -q "arbitrage_score_min" templates/index.html; then
    echo -e "${GREEN}✅ PASS${NC} - JavaScript request building present"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - JavaScript request building missing"
    ((FAIL++))
fi

# 5. Check backend parameter extraction
if grep -q "arbitrage_score_min = data.get" app.py; then
    echo -e "${GREEN}✅ PASS${NC} - Backend parameter extraction present"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Backend parameter extraction missing"
    ((FAIL++))
fi

# 6. Check backend function signature
if grep -q "arbitrage_score_min: int = None" app.py; then
    echo -e "${GREEN}✅ PASS${NC} - Backend function signature updated"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Backend function signature not updated"
    ((FAIL++))
fi

# 7. Check backend SQL filter
if grep -q "arbitrage_condition" app.py; then
    echo -e "${GREEN}✅ PASS${NC} - Backend SQL filter logic present"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Backend SQL filter logic missing"
    ((FAIL++))
fi

# 8. Check test file exists
if [ -f "test_arbitrage_filter_integration.py" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Integration test file exists"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Integration test file missing"
    ((FAIL++))
fi

# 9. Check documentation
if [ -f "ARBITRAGE_SCORE_IMPLEMENTATION_COMPLETE.md" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Implementation documentation exists"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Implementation documentation missing"
    ((FAIL++))
fi

# 10. Check quick summary
if [ -f "ARBITRAGE_QUICK_SUMMARY.md" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Quick summary documentation exists"
    ((PASS++))
else
    echo -e "${RED}❌ FAIL${NC} - Quick summary documentation missing"
    ((FAIL++))
fi

echo ""
echo "================================================"
echo "📊 Results:"
echo ""
echo -e "   ${GREEN}Passed:${NC} $PASS/10"
echo -e "   ${RED}Failed:${NC} $FAIL/10"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CHECKS PASSED!${NC}"
    echo ""
    echo "✅ Arbitrage Score filter is fully implemented"
    echo ""
    echo "📋 Ready to:"
    echo "   1. Run integration tests: python test_arbitrage_filter_integration.py"
    echo "   2. Start the app: python app.py"
    echo "   3. Test in browser at http://localhost:5000"
    echo ""
    exit 0
else
    echo -e "${RED}❌ SOME CHECKS FAILED${NC}"
    echo ""
    echo "⚠️  Please review the implementation"
    echo ""
    exit 1
fi
