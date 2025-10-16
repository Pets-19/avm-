# User Acceptance Testing - Flip Score Filter
**Feature:** Flip Score Investment Filter  
**Date:** October 16, 2025  
**Version:** 1.0  
**Tester:** _________________

---

## 🎯 Testing Objectives

1. Verify flip score filter is visible and functional
2. Confirm all filter options work correctly
3. Test combined filters (ESG + Flip)
4. Validate data accuracy and performance
5. Ensure no regressions in existing functionality

---

## 📋 Pre-Test Setup

### Environment Check
- [ ] Flask app running on http://localhost:5000
- [ ] Database has 10 properties with flip scores
- [ ] Browser: Chrome/Firefox/Safari (latest version)
- [ ] Console open (F12 → Console tab)
- [ ] Network tab open (F12 → Network tab)

### Verify Installation
```bash
# Check Flask is running
ps aux | grep "python app.py"

# Verify database
cd /workspaces/avm-
python -c "from app import engine; from sqlalchemy import text; \
conn = engine.connect(); \
result = conn.execute(text('SELECT COUNT(*) FROM properties WHERE flip_score IS NOT NULL')); \
print(f'Properties with flip scores: {result.fetchone()[0]}')"

# Expected output: Properties with flip scores: 10
```

**Login Credentials:**
- Email: `dhanesh@retyn.ai`
- Password: `retyn*#123`

---

## 🧪 Test Cases

### TEST 1: UI Element Visibility ✅/❌

**Objective:** Verify flip score dropdown is visible and properly styled

**Steps:**
1. Open http://localhost:5000 in browser
2. Login with credentials above
3. Navigate to **Property Valuation** tab
4. Scroll to optional filters section

**Expected Results:**
- [ ] "📈 Flip Score (Investment)" dropdown visible
- [ ] Located after "🌱 ESG Score" dropdown
- [ ] Dropdown has 5 options:
  - [ ] "Any Score"
  - [ ] "30+ (Low Potential) ✓"
  - [ ] "50+ (Moderate) ✓"
  - [ ] "70+ (Good) ✓"
  - [ ] "80+ (Excellent) ✓"
- [ ] Small text below shows: "Current Flip data: 30-88 range (10 properties)"
- [ ] Styling matches ESG dropdown

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 2: Filter with "Any Score" (Baseline) ✅/❌

**Objective:** Verify default behavior without flip filter

**Steps:**
1. Fill in Property Valuation form:
   - Property Type: **Unit**
   - Area: **Madinat Al Mataar**
   - Size: **2000** sqm
2. Leave Flip Score as **"Any Score"**
3. Click **Get Valuation**
4. Check browser console (F12)

**Expected Results:**
- [ ] Valuation completes successfully
- [ ] Results displayed (price, confidence, comparables)
- [ ] Console shows: `flip_score_min` NOT in request payload
- [ ] Flask logs do NOT show flip filter message

**Actual Results:**
- Number of comparables: _______
- Estimated value: _______
- Confidence: _______

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 3: Filter with "30+" (All Properties) ✅/❌

**Objective:** Test minimum flip score filter (should include all 10 properties)

**Steps:**
1. Fill in Property Valuation form:
   - Property Type: **Unit**
   - Area: **Madinat Al Mataar**
   - Size: **2000** sqm
2. Select Flip Score: **30+**
3. Click **Get Valuation**
4. Check browser console and Flask logs

**Expected Results:**
- [ ] Console shows: `flip_score_min: 30`
- [ ] Flask logs show: `📈 [DB] Filtering for Flip score >= 30`
- [ ] Valuation completes successfully
- [ ] Results include properties with scores 30, 70, 82, 88

**Actual Results:**
- Number of comparables: _______ (expect ≤ 10)
- Estimated value: _______
- Console payload: _______

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 4: Filter with "70+" (Good Properties) ✅/❌

**Objective:** Test mid-range filter (should include scores 70, 82, 88)

**Steps:**
1. Fill in Property Valuation form:
   - Property Type: **Unit**
   - Area: **Madinat Al Mataar**
   - Size: **2000** sqm
2. Select Flip Score: **70+**
3. Click **Get Valuation**

**Expected Results:**
- [ ] Console shows: `flip_score_min: 70`
- [ ] Flask logs show: `📈 [DB] Filtering for Flip score >= 70`
- [ ] Comparables reduced (excludes score 30)
- [ ] Only properties with scores 70, 82, 88 included

**Actual Results:**
- Number of comparables: _______ (expect ≤ 6)
- Estimated value: _______
- Difference from "Any Score": _______

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 5: Filter with "80+" (Excellent Only) ✅/❌

**Objective:** Test strict filter (should include scores 82, 88 only)

**Steps:**
1. Fill in Property Valuation form:
   - Property Type: **Unit**
   - Area: **Madinat Al Mataar**
   - Size: **2000** sqm
2. Select Flip Score: **80+**
3. Click **Get Valuation**

**Expected Results:**
- [ ] Console shows: `flip_score_min: 80`
- [ ] Flask logs show: `📈 [DB] Filtering for Flip score >= 80`
- [ ] Comparables reduced (excludes scores 30, 70)
- [ ] Only properties with scores 82, 88 included

**Actual Results:**
- Number of comparables: _______ (expect ≤ 5)
- Estimated value: _______
- Difference from "70+": _______

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 6: Combined ESG + Flip Filters ✅/❌

**Objective:** Verify flip filter works with existing ESG filter

**Steps:**
1. Fill in Property Valuation form:
   - Property Type: **Unit**
   - Area: **Business Bay**
   - Size: **1500** sqm
2. Select ESG Score: **40+**
3. Select Flip Score: **70+**
4. Click **Get Valuation**

**Expected Results:**
- [ ] Console shows BOTH: `esg_score_min: 40` AND `flip_score_min: 70`
- [ ] Flask logs show ESG filter message: `🌱 [DB] Filtering for ESG score >= 40`
- [ ] Flask logs show Flip filter message: `📈 [DB] Filtering for Flip score >= 70`
- [ ] Valuation uses properties meeting BOTH criteria

**Actual Results:**
- Number of comparables: _______
- Both filters applied: ✅ Yes / ❌ No

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 7: Filter Reset Behavior ✅/❌

**Objective:** Verify filter can be reset to "Any Score"

**Steps:**
1. Select Flip Score: **80+**
2. Click **Get Valuation** (note results)
3. Change Flip Score back to: **Any Score**
4. Click **Get Valuation** again

**Expected Results:**
- [ ] First request: Console shows `flip_score_min: 80`
- [ ] Second request: Console does NOT show `flip_score_min`
- [ ] Comparable count increases when filter removed
- [ ] No errors or cached filter values

**Actual Results:**
- With filter: _______ comparables
- Without filter: _______ comparables

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 8: No Results Scenario ✅/❌

**Objective:** Test behavior when no properties meet criteria

**Steps:**
1. Fill in Property Valuation form:
   - Property Type: **Unit**
   - Area: **Wadi Al Safa** (has only score 30)
   - Size: **1000** sqm
2. Select Flip Score: **80+** (too high for this area)
3. Click **Get Valuation**

**Expected Results:**
- [ ] Graceful handling (no crash)
- [ ] Either: (A) Returns results without flip filter applied, OR
- [ ] (B) Shows message: "No comparable properties found with flip score >= 80"
- [ ] Console shows: `flip_score_min: 80`

**Actual Results:**
- Behavior: _______
- Error message (if any): _______

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 9: Performance Test ✅/❌

**Objective:** Verify filter doesn't cause performance degradation

**Steps:**
1. Open Network tab (F12 → Network)
2. Fill in Property Valuation form
3. Select Flip Score: **70+**
4. Click **Get Valuation**
5. Note response time in Network tab

**Expected Results:**
- [ ] Response time: < 3 seconds
- [ ] No timeout errors
- [ ] Database index is being used (check Flask logs)

**Actual Results:**
- Response time: _______ ms
- Database query time: _______ (from Flask logs)

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 10: Regression - Existing Filters Still Work ✅/❌

**Objective:** Verify no regressions in existing functionality

**Steps:**
1. Test Property Type filter (select Villa)
2. Test Bedrooms filter (select 3)
3. Test Development Status (select Ready)
4. Test ESG Score (select 40+)
5. Test WITHOUT Flip Score selected

**Expected Results:**
- [ ] All existing filters work independently
- [ ] Flip Score dropdown doesn't interfere
- [ ] No console errors
- [ ] Results are accurate

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 11: Mobile Responsiveness ✅/❌

**Objective:** Verify dropdown works on mobile view

**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select iPhone/Android device
4. Navigate to Property Valuation tab
5. Test Flip Score dropdown

**Expected Results:**
- [ ] Dropdown visible on mobile
- [ ] Touch interactions work
- [ ] Options readable
- [ ] Grid layout adjusts properly

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

### TEST 12: Browser Compatibility ✅/❌

**Objective:** Test across different browsers

**Browsers to Test:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

**For Each Browser:**
- Dropdown renders correctly: ✅/❌
- Filter works: ✅/❌
- Console shows correct payload: ✅/❌

**Status:** ✅ Pass / ❌ Fail  
**Notes:** _______________________________________________

---

## 🔍 Edge Cases & Error Handling

### EDGE 1: Invalid Area Name ✅/❌
**Test:** Enter non-existent area with Flip 70+ filter  
**Expected:** Graceful error message  
**Result:** _______

### EDGE 2: Zero Size Input ✅/❌
**Test:** Enter size = 0 with Flip filter  
**Expected:** Validation error before applying filter  
**Result:** _______

### EDGE 3: Special Characters in Area ✅/❌
**Test:** Enter area with special chars (e.g., "Business Bay - 123!")  
**Expected:** Filter still works correctly  
**Result:** _______

### EDGE 4: Very Large Size ✅/❌
**Test:** Enter size = 10000 sqm with Flip 80+  
**Expected:** Either no results or fallback behavior  
**Result:** _______

---

## 📊 Data Validation

### Verify Flip Score Distribution
```bash
cd /workspaces/avm-
python -c "
from app import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('''
        SELECT flip_score, COUNT(*) as count, 
               STRING_AGG(DISTINCT area_en, ', ') as areas
        FROM properties 
        WHERE flip_score IS NOT NULL
        GROUP BY flip_score
        ORDER BY flip_score
    '''))
    print('Score | Count | Areas')
    print('------|-------|------')
    for row in result:
        print(f'{row[0]:5} | {row[1]:5} | {row[2][:50]}')
"
```

**Expected Output:**
```
Score | Count | Areas
------|-------|------
   30 |     1 | Wadi Al Safa
   70 |     4 | DUBAI PRODUCTION...
   82 |     3 | Palm Deira
   88 |     2 | Madinat Al Mataar
```

**Actual Output:** _______

---

## 🐛 Bug Tracking

| Bug ID | Severity | Description | Status |
|--------|----------|-------------|--------|
| 1 |  | | |
| 2 |  | | |
| 3 |  | | |

**Severity Levels:**
- **Critical:** Blocks deployment
- **Major:** Significant impact, workaround exists
- **Minor:** Cosmetic or edge case
- **Enhancement:** Improvement suggestion

---

## ✅ Acceptance Criteria

**MUST PASS (Blocker):**
- [ ] All 5 filter options work correctly
- [ ] Console shows correct `flip_score_min` value
- [ ] Flask logs show filter debug message
- [ ] No errors in console or Flask logs
- [ ] Filter combines with ESG successfully
- [ ] Existing filters not affected (no regression)

**SHOULD PASS (Non-blocker):**
- [ ] Performance < 3 seconds
- [ ] Mobile responsive
- [ ] All browsers work
- [ ] Edge cases handled gracefully

---

## 📝 Final Sign-Off

### Summary
- **Total Test Cases:** 12
- **Passed:** _______
- **Failed:** _______
- **Blocked:** _______
- **Pass Rate:** _______ %

### Tester Comments
_______________________________________________
_______________________________________________
_______________________________________________

### Decision
- [ ] ✅ **APPROVED** - Ready for production deployment
- [ ] ⚠️ **APPROVED WITH NOTES** - Deploy with known issues
- [ ] ❌ **REJECTED** - Requires fixes before deployment

**Signed:** _______________  
**Date:** _______________  
**Next Action:** _______________

---

## 🚀 Post-UAT Actions

If APPROVED:
1. Run production readiness checks: `./check_production_ready.sh`
2. Create deployment notes
3. Tag release: `git tag v1.1-flip-score-filter`
4. Deploy to production
5. Monitor logs for 24 hours
6. Create production verification checklist

If REJECTED:
1. Document all failing tests
2. Create bug tickets
3. Fix issues
4. Retest
5. Repeat UAT
