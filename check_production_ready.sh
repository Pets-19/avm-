#!/bin/bash
# Quick Production Readiness Check
# Run this before deployment

echo "🔍 PRODUCTION READINESS CHECK"
echo "=============================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

# Test 1: Critical files exist
echo "📁 Checking critical files..."
FILES=("app.py" "requirements.txt" "Dockerfile" "docker-compose.yaml" "valuation_engine.py")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file exists"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} $file MISSING"
        ((FAIL++))
    fi
done
echo ""

# Test 2: ML model files
echo "🤖 Checking ML model files..."
MODEL_FILES=("models/xgboost_model_v1.pkl" "models/label_encoders_v1.pkl" "models/feature_columns_v1.pkl")
for file in "${MODEL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅${NC} $file exists"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} $file MISSING"
        ((FAIL++))
    fi
done
echo ""

# Test 3: Templates and static files
echo "🎨 Checking frontend files..."
if [ -f "templates/index.html" ]; then
    echo -e "${GREEN}✅${NC} templates/index.html exists"
    ((PASS++))
else
    echo -e "${RED}❌${NC} templates/index.html MISSING"
    ((FAIL++))
fi

if [ -f "static/css/style.css" ]; then
    echo -e "${GREEN}✅${NC} static/css/style.css exists"
    ((PASS++))
else
    echo -e "${RED}❌${NC} static/css/style.css MISSING"
    ((FAIL++))
fi

if [ -f "static/js/script.js" ]; then
    echo -e "${GREEN}✅${NC} static/js/script.js exists"
    ((PASS++))
else
    echo -e "${RED}❌${NC} static/js/script.js MISSING"
    ((FAIL++))
fi
echo ""

# Test 4: .env file
echo "🔐 Checking environment variables..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✅${NC} .env file exists"
    
    # Check if it has required variables
    if grep -q "DATABASE_URL" .env; then
        echo -e "${GREEN}✅${NC} DATABASE_URL configured"
        ((PASS++))
    else
        echo -e "${RED}❌${NC} DATABASE_URL missing in .env"
        ((FAIL++))
    fi
    
    if grep -q "OPENAI_API_KEY" .env; then
        echo -e "${GREEN}✅${NC} OPENAI_API_KEY configured"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠️${NC}  OPENAI_API_KEY missing (optional but recommended)"
    fi
else
    echo -e "${RED}❌${NC} .env file MISSING - CREATE IT BEFORE DEPLOYMENT!"
    ((FAIL++))
fi
echo ""

# Test 5: .gitignore configured correctly
echo "🚫 Checking .gitignore..."
if grep -q "data/rentals_training.csv" .gitignore; then
    echo -e "${GREEN}✅${NC} Large CSV files excluded from git"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️${NC}  rentals_training.csv not in .gitignore"
fi

if grep -q ".env" .gitignore; then
    echo -e "${GREEN}✅${NC} .env excluded from git (security)"
    ((PASS++))
else
    echo -e "${RED}❌${NC} .env NOT in .gitignore - SECURITY RISK!"
    ((FAIL++))
fi
echo ""

# Test 6: Archive organization
echo "📦 Checking file organization..."
if [ -d "archive" ]; then
    DOC_COUNT=$(ls archive/documentation/ 2>/dev/null | wc -l)
    TEST_COUNT=$(ls archive/testing/ 2>/dev/null | wc -l)
    DEV_COUNT=$(ls archive/development/ 2>/dev/null | wc -l)
    echo -e "${GREEN}✅${NC} Archive created: $DOC_COUNT docs, $TEST_COUNT tests, $DEV_COUNT dev files"
    ((PASS++))
else
    echo -e "${YELLOW}⚠️${NC}  No archive folder (optional)"
fi
echo ""

# Test 7: Database connectivity (optional - requires Python)
echo "🗄️  Testing database connection..."
if command -v python &> /dev/null; then
    if python -c "from app import engine; conn = engine.connect(); conn.close(); print('✅ Database connection successful')" 2>/dev/null; then
        ((PASS++))
    else
        echo -e "${RED}❌${NC} Database connection failed"
        ((FAIL++))
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Python not available, skipping DB test"
fi
echo ""

# Test 18: Verify Performance Indexes Exist
echo "🔍 Checking database performance indexes..."
if command -v python3 &> /dev/null; then
    INDEX_CHECK=$(python3 << 'EOF'
import os
import sys
from sqlalchemy import create_engine, text

try:
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("SKIP")
        sys.exit(0)
    
    # Clean DATABASE_URL: strip whitespace/newlines and remove channel_binding parameter
    import re
    database_url = database_url.strip()
    if '&channel_binding=' in database_url or '?channel_binding=' in database_url:
        database_url = re.sub(r'[&?]channel_binding=[^&]*', '', database_url)
    
    engine = create_engine(database_url, connect_args={'sslmode': 'require'})
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE indexname IN ('idx_properties_area_type', 'idx_rentals_area_type')
        """))
        count = result.scalar()
    
    print(count)
except Exception as e:
    print(f"ERROR")
    sys.exit(0)
EOF
)
    
    if [ "$INDEX_CHECK" == "2" ]; then
        echo -e "${GREEN}✅${NC} Performance indexes exist (2/2)"
        ((PASS++))
    elif [ "$INDEX_CHECK" == "1" ]; then
        echo -e "${YELLOW}⚠️${NC}  Partial performance indexes (1/2) - missing index"
    elif [ "$INDEX_CHECK" == "SKIP" ]; then
        echo -e "${YELLOW}⚠️${NC}  DATABASE_URL not set, skipping index check"
    elif [ "$INDEX_CHECK" == "ERROR" ]; then
        echo -e "${YELLOW}⚠️${NC}  Could not verify indexes (DB connection issue)"
    else
        echo -e "${RED}❌${NC} Missing performance indexes (found $INDEX_CHECK/2)"
        ((FAIL++))
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Python not available, skipping index check"
fi
echo ""

# Summary
echo "=============================="
echo "📊 RESULTS"
echo "=============================="
echo -e "Passed: ${GREEN}$PASS${NC}"
echo -e "Failed: ${RED}$FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED - READY FOR PRODUCTION!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review PRODUCTION_LAUNCH_CHECKLIST.md"
    echo "2. Commit changes: git add . && git commit -m 'Production ready'"
    echo "3. Push to repo: git push origin master"
    echo "4. Deploy: docker-compose up -d"
    exit 0
else
    echo -e "${RED}❌ $FAIL CRITICAL ISSUES FOUND${NC}"
    echo "Fix the issues above before deployment!"
    exit 1
fi
