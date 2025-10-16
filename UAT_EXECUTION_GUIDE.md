# 🧪 UAT EXECUTION GUIDE - Quick Start

**Status:** ⏳ AWAITING UAT EXECUTION  
**System Status:** ✅ ALL CHECKS PASSED - READY FOR TESTING  
**Estimated Time:** 30 minutes

---

## 🚀 Quick Start (5 minutes)

### Option 1: Automated Helper (Recommended)
```bash
cd /workspaces/avm-
./uat_helper.sh verify
```

This will:
- ✅ Check Flask is running
- ✅ Verify database status
- ✅ Show test credentials
- ✅ Display quick test steps

### Option 2: Manual Quick Test
```bash
# 1. Verify system ready
cd /workspaces/avm-
pgrep -f "python app.py"  # Should return a process ID

# 2. Open browser
# URL: http://localhost:5000
# User: dhanesh@retyn.ai
# Pass: retyn*#123

# 3. Quick test (2 minutes)
# - Go to Property Valuation tab
# - Select Flip Score: 70+
# - Area: Madinat Al Mataar
# - Size: 2000
# - Get Valuation
# - Check console (F12): Should show flip_score_min: 70
```

---

## 📋 Full UAT Process

### Step 1: Open UAT Checklist
```bash
# View the checklist
less UAT_FLIP_SCORE_FILTER.md

# Or open in VS Code
code UAT_FLIP_SCORE_FILTER.md
```

### Step 2: Execute Test Cases (12 tests)

**Critical Tests (Must Pass):**
1. ✅ UI Element Visibility - Dropdown visible with 5 options
2. ✅ Filter "Any Score" - Baseline behavior
3. ✅ Filter "30+" - All 10 properties
4. ✅ Filter "70+" - Good properties (6 expected)
5. ✅ Filter "80+" - Excellent only (5 expected)
6. ✅ Combined ESG + Flip - Both filters work together
7. ✅ Filter Reset - Can return to "Any Score"

**Optional Tests (Should Pass):**
8. No Results Scenario
9. Performance Test (< 3 seconds)
10. Regression Check
11. Mobile Responsiveness
12. Browser Compatibility

### Step 3: Monitor Logs During Testing
```bash
# In separate terminal
cd /workspaces/avm-
./uat_helper.sh logs

# Or manually
tail -f flask.log | grep -i flip
```

### Step 4: Complete Sign-Off
Fill in the checklist at bottom of `UAT_FLIP_SCORE_FILTER.md`

---

## 🎯 Expected Test Results

### Test Case 3: Filter "30+" 
**Input:**
- Property Type: Unit
- Area: Madinat Al Mataar
- Size: 2000
- Flip Score: 30+

**Expected:**
- ✅ Console: `flip_score_min: 30`
- ✅ Flask logs: `📈 [DB] Filtering for Flip score >= 30`
- ✅ Comparables: ≤ 10 properties

### Test Case 4: Filter "70+"
**Input:**
- Property Type: Unit
- Area: Madinat Al Mataar
- Size: 2000
- Flip Score: 70+

**Expected:**
- ✅ Console: `flip_score_min: 70`
- ✅ Flask logs: `📈 [DB] Filtering for Flip score >= 70`
- ✅ Comparables: ≤ 6 properties (scores 70, 82, 88)

### Test Case 6: Combined ESG + Flip
**Input:**
- Property Type: Unit
- Area: Business Bay
- Size: 1500
- ESG Score: 40+
- Flip Score: 70+

**Expected:**
- ✅ Console: `esg_score_min: 40, flip_score_min: 70`
- ✅ Flask logs: Both filter messages
- ✅ Properties meet BOTH criteria

---

## 🔍 Troubleshooting

### Issue: Dropdown Not Visible
```bash
# Check Flask restarted after migration
pkill -f "python app.py"
nohup python app.py > flask.log 2>&1 &
sleep 3
tail -20 flask.log  # Look for successful startup
```

### Issue: Filter Not Working
```bash
# Check browser console
# F12 → Console → Look for flip_score_min in request payload

# Check Flask logs
tail -50 flask.log | grep -i flip
```

### Issue: No Results
```bash
# Verify sample data exists
python3 -c "
from app import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM properties WHERE flip_score IS NOT NULL'))
    print(f'Properties with flip scores: {result.fetchone()[0]}')
"
```

---

## ✅ UAT Acceptance Decision

After completing all tests, make decision:

### ✅ APPROVE - All MUST PASS criteria met
```bash
# Next: Production deployment prep
./check_production_ready.sh

# Tag release
git tag v1.1-flip-score-filter
git push origin v1.1-flip-score-filter

# Deploy
# (Follow deployment procedure)
```

### ⚠️ APPROVE WITH NOTES - Some SHOULD PASS failed
```bash
# Document known issues in UAT_FLIP_SCORE_FILTER.md
# Create enhancement tickets
# Proceed with deployment
# Monitor closely
```

### ❌ REJECT - Any MUST PASS criteria failed
```bash
# Document failures in UAT_FLIP_SCORE_FILTER.md
# Create bug tickets with priority
# Do NOT deploy
# Fix issues and retest
```

---

## 📊 Current System Status

**Pre-UAT Health Check Results:**
```
1. Flask Running:            ✅ YES
2. Database Connected:       ✅ YES
3. Flip Score Column:        ✅ EXISTS
4. Sample Data:              ✅ 10 properties
5. Score Distribution:       ✅ CORRECT
   - Score 30:  1 property
   - Score 70:  4 properties
   - Score 82:  3 properties
   - Score 88:  2 properties
6. Index Created:            ✅ YES (idx_flip_score)
7. In SALES_COLUMNS:         ✅ YES
8. Test File Exists:         ✅ YES

✅ ALL CHECKS PASSED - READY FOR UAT
```

---

## 📚 Documentation References

**UAT Checklist:**
- `/workspaces/avm-/UAT_FLIP_SCORE_FILTER.md` (12 test cases)

**Deployment Guide:**
- `/workspaces/avm-/DEPLOYMENT_READY_FLIP_SCORE.md`

**Quick Reference:**
- `/workspaces/avm-/archive/documentation/FLIP_SCORE_FILTER_QUICK_REFERENCE.md`

**Implementation Details:**
- `/workspaces/avm-/FLIP_SCORE_FILTER_COMPLETE.md`

---

## 🚀 After UAT Approval

### Immediate Actions (15 minutes)
1. **Run Production Checks**
   ```bash
   ./check_production_ready.sh
   ```
   Must show: ✅ All 17 health checks passed

2. **Create Git Tag**
   ```bash
   git add .
   git commit -m "feat: Add Flip Score investment filter (Quick Win #1)"
   git tag -a v1.1-flip-score-filter -m "Flip Score Filter - UAT Approved"
   git push origin main --tags
   ```

3. **Deployment Notes**
   - Feature: Flip Score Filter (investment quality filter)
   - Type: Optional filter (non-breaking change)
   - Database: Migration already applied (10 sample properties)
   - Rollback: Simple (remove dropdown from UI)
   - Monitoring: Watch Flask logs for filter usage

4. **Deploy to Production**
   ```bash
   # Follow your deployment procedure
   # Example (if using Docker):
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

5. **Post-Deployment Verification**
   - Access production URL
   - Login and test filter
   - Monitor logs for 24 hours
   - Check error rates

---

## 📞 Support Contacts

**Technical Issues:**
- Check Flask logs: `tail -f flask.log`
- Run helper: `./uat_helper.sh`
- Review docs: `UAT_FLIP_SCORE_FILTER.md`

**UAT Questions:**
- See test case details in UAT checklist
- Expected results documented for each test
- Troubleshooting section included

---

## 🎯 Success Criteria Summary

**MUST PASS (Blocker):**
- [ ] All 5 filter options work
- [ ] Console shows flip_score_min
- [ ] Flask logs show filter message
- [ ] No errors
- [ ] Combines with ESG filter
- [ ] No regression

**SHOULD PASS (Non-blocker):**
- [ ] Performance < 3 seconds
- [ ] Mobile responsive
- [ ] Cross-browser compatible

**Decision Required:**
- [ ] ✅ APPROVE
- [ ] ⚠️ APPROVE WITH NOTES
- [ ] ❌ REJECT

---

**Prepared:** October 16, 2025  
**Status:** ⏳ AWAITING UAT EXECUTION  
**Estimated Completion:** 30 minutes from start
