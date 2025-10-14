# 🚀 RENTAL YIELD - STRUCTURED IMPLEMENTATION PROMPTS

**Purpose**: Machine-optimized prompts for AI-assisted implementation  
**Target**: Implement Rental Yield Calculator in 3-4 hours (vs 12 hours estimated)  
**Approach**: Incremental, tested, safe changes with explicit verification

---

## 📋 PREREQUISITES CHECKLIST

Before starting implementation, verify:

```bash
# 1. Check database tables exist
psql $DATABASE_URL -c "SELECT COUNT(*) FROM rentals;"
# Expected: 620,000+ rows

# 2. Verify column names
psql $DATABASE_URL -c "\d rentals" | grep -i "annual_amount\|area_en\|prop_sub"
# Expected: ANNUAL_AMOUNT, AREA_EN, PROP_SUB_TYPE_EN columns present

# 3. Test sample rental query
psql $DATABASE_URL -c "SELECT AVG(\"ANNUAL_AMOUNT\") FROM rentals WHERE \"AREA_EN\" = 'Dubai Hills' LIMIT 10;"
# Expected: Average around 200K-300K AED

# 4. Check current valuation endpoint works
curl -X POST http://localhost:5000/api/property/valuation \
  -H "Content-Type: application/json" \
  -d '{"property_type":"Unit","area":"Dubai Hills","size_sqm":300}'
# Expected: 200 OK with valuation data
```

**✅ All checks passed? Proceed to Implementation.**  
**❌ Any checks failed? Debug database connection first.**

---

## 🎯 PROMPT #1: BACKEND - ADD RENTAL QUERY

**Objective**: Add rental comparable query to existing valuation function  
**Files**: `app.py` (1 file only)  
**Lines Changed**: ~30 lines added  
**Time**: 60 minutes  
**Risk**: 🟢 LOW (read-only query, wrapped in try-catch)

### **PROMPT FOR AI:**

```
TASK: Add rental yield data to property valuation calculation

CONTEXT:
- File: /workspaces/avm-retyn/app.py
- Function: calculate_valuation_from_database() at lines 900-1150
- Current behavior: Returns property valuation with sales comparables
- Desired behavior: Also return rental comparables for yield calculation

REQUIREMENTS:
1. Add rental query AFTER confidence calculation (line ~1105)
2. Query rentals table for same area + property type
3. Apply outlier filtering (3× IQR method, same as sales)
4. Calculate median annual rent from filtered results
5. Add fallback to city-wide average if < 3 area rentals
6. Wrap entire section in try-catch (non-critical feature)
7. Add rental_data field to result dictionary

DATABASE SCHEMA:
Table: rentals
- ANNUAL_AMOUNT: Annual rent in AED
- AREA_EN: Location name (e.g., "Dubai Hills")
- PROP_SUB_TYPE_EN: Property type (e.g., "UNIT", "VILLA")
- ACTUAL_AREA: Size in square meters
- REGISTRATION_DATE: Transaction date

OUTLIER FILTERING LOGIC:
```python
q1 = df['column'].quantile(0.25)
q3 = df['column'].quantile(0.75)
iqr = q3 - q1
lower_bound = q1 - 3 * iqr
upper_bound = q3 + 3 * iqr
filtered = df[(df['column'] >= lower_bound) & (df['column'] <= upper_bound)]
```

EXPECTED OUTPUT STRUCTURE:
```python
rental_data = {
    'annual_rent': 245000,           # Median annual rent
    'count': 38,                     # Number of comparables
    'price_range': {
        'low': 220000,               # Q1 (25th percentile)
        'high': 270000               # Q3 (75th percentile)
    },
    'is_city_average': False         # True if fallback used
}
```

INSERTION POINT:
Find this code block (around line 1105):
```python
        confidence = min(max(confidence, 70), 98)  # Keep between 70-98%
        
        # Calculate value range
        std_dev = comparables['property_total_value'].std()
```

INSERT BEFORE "# Calculate value range":
```python
        confidence = min(max(confidence, 70), 98)
        
        # --- RENTAL YIELD CALCULATION (NEW CODE HERE) ---
        [YOUR IMPLEMENTATION]
        # --- END RENTAL CALCULATION ---
        
        # Calculate value range
        std_dev = comparables['property_total_value'].std()
```

THEN MODIFY result dictionary (around line 1125):
```python
        result = {
            'success': True,
            'valuation': {
                'estimated_value': round(estimated_value),
                'confidence_score': round(confidence, 1),
                'price_per_sqm': round(estimated_value / size_sqm) if size_sqm > 0 else 0,
                'value_range': {
                    'low': round(estimated_value - margin),
                    'high': round(estimated_value + margin)
                },
                'rental_data': rental_data,  # ← ADD THIS FIELD
                'comparables': comparable_list,
                # ... existing fields
            }
        }
```

VALIDATION CHECKS:
1. ✅ Rental query uses parameterized queries (SQL injection safe)
2. ✅ Wrapped in try-catch with rental_data = None fallback
3. ✅ Minimum 3 comparables required (else use city average or None)
4. ✅ Valid range checks: ANNUAL_AMOUNT between 10K-5M AED
5. ✅ Print statements for debugging

EDGE CASES TO HANDLE:
- No rentals in area → Fallback to city-wide average
- < 3 rentals found → Fallback to city-wide average
- Rental query fails → Set rental_data = None (valuation still succeeds)
- Division by zero in outlier calc → Check len(rental_df) >= 3

TEST COMMAND (after implementation):
```bash
python app.py &
sleep 5
curl -X POST http://localhost:5000/api/property/valuation \
  -H "Content-Type: application/json" \
  -H "Cookie: session=..." \
  -d '{"property_type":"Unit","area":"Dubai Hills","size_sqm":300}' | jq '.valuation.rental_data'
```

EXPECTED RESULT:
```json
{
  "annual_rent": 240000,
  "count": 42,
  "price_range": {
    "low": 210000,
    "high": 275000
  }
}
```

STOP CONDITIONS:
- ❌ If changes exceed 50 lines → Break into smaller increments
- ❌ If rental query breaks valuation → Verify try-catch wrapping
- ❌ If response time > 2 seconds → Add LIMIT clause or index

OUTPUT FORMAT:
Provide:
1. Complete code block to insert (with comments)
2. Exact line numbers for insertion
3. Modified result dictionary
4. Confirmation that error handling is present
```

---

## 🎯 PROMPT #2: FRONTEND - DISPLAY YIELD CARD

**Objective**: Show rental yield in valuation results UI  
**Files**: `templates/index.html` (1 file only)  
**Lines Changed**: ~15 lines HTML + ~25 lines JavaScript  
**Time**: 45 minutes  
**Risk**: 🟢 LOW (progressive enhancement, hidden if no data)

### **PROMPT FOR AI:**

```
TASK: Display rental yield in property valuation results

CONTEXT:
- File: /workspaces/avm-retyn/templates/index.html
- Section: Valuation results display (lines 550-600)
- Current: Shows 3 detail cards (Price/SqM, Value Range, Comparables)
- Desired: Add 4th card for Rental Yield (if data available)

REQUIREMENTS:
1. Add HTML card for yield display in valuation-details-grid
2. Initially hidden (display: none)
3. Calculate yield in displayValuationResult() function
4. Show/hide based on data availability
5. Color code yield: Green (≥6%), Orange (4-6%), Red (<4%)
6. Handle edge cases gracefully (null data, zero valuation)

HTML STRUCTURE TO ADD (after line ~575):
Find this section:
```html
<div class="detail-card">
    <h5>Comparable Properties</h5>
    <p><span id="comparables-count">0</span> properties analyzed</p>
</div>
</div> <!-- End valuation-details-grid -->
```

ADD BEFORE closing </div>:
```html
<div class="detail-card">
    <h5>Comparable Properties</h5>
    <p><span id="comparables-count">0</span> properties analyzed</p>
</div>

<!-- NEW RENTAL YIELD CARD -->
<div class="detail-card" id="rental-yield-card" style="display: none;">
    <h5>Gross Rental Yield</h5>
    <p class="yield-percentage" style="font-size: 2rem; font-weight: bold; color: #4CAF50; margin: 10px 0;">
        <span id="rental-yield">--</span>%
    </p>
    <p class="yield-subtitle" style="font-size: 0.9rem; color: #666;">
        <span id="rental-subtitle">Based on market comparables</span>
    </p>
</div>
<!-- END RENTAL YIELD CARD -->

</div> <!-- End valuation-details-grid -->
```

JAVASCRIPT CALCULATION (after line ~2148):
Find displayValuationResult() function, after this line:
```javascript
lastComparablesData = comparables;
```

ADD THIS LOGIC:
```javascript
lastComparablesData = comparables;

// --- RENTAL YIELD DISPLAY (NEW) ---
if (valuation.rental_data && valuation.rental_data.annual_rent && valuation.estimated_value > 0) {
    const grossYield = (valuation.rental_data.annual_rent / valuation.estimated_value * 100).toFixed(2);
    
    // Show card and update value
    document.getElementById('rental-yield-card').style.display = 'block';
    document.getElementById('rental-yield').textContent = grossYield;
    
    // Update subtitle
    let subtitle = `Based on ${valuation.rental_data.count} rental comparables`;
    if (valuation.rental_data.is_city_average) {
        subtitle = `City-wide average (${valuation.rental_data.count} rentals)`;
    }
    document.getElementById('rental-subtitle').textContent = subtitle;
    
    // Color code based on yield
    const yieldElement = document.getElementById('rental-yield');
    if (parseFloat(grossYield) >= 6.0) {
        yieldElement.style.color = '#4CAF50'; // Green - excellent yield
    } else if (parseFloat(grossYield) >= 4.0) {
        yieldElement.style.color = '#FF9800'; // Orange - average yield
    } else {
        yieldElement.style.color = '#F44336'; // Red - low yield
    }
    
    console.log(`💰 Rental Yield: ${grossYield}% (${valuation.rental_data.annual_rent.toLocaleString()} AED/year)`);
} else {
    // No rental data - hide card
    document.getElementById('rental-yield-card').style.display = 'none';
    console.log('⚠️ Rental data not available for this property');
}
// --- END RENTAL YIELD DISPLAY ---
```

VALIDATION CHECKS:
1. ✅ Null checks before division: valuation.rental_data exists
2. ✅ Zero check: valuation.estimated_value > 0
3. ✅ Card hidden by default (progressive enhancement)
4. ✅ Graceful fallback when no data
5. ✅ Console logging for debugging

YIELD COLOR THRESHOLDS (Dubai Market):
- 🟢 ≥6.0%: Excellent (above market average)
- 🟠 4.0-5.9%: Average (typical Dubai yield)
- 🔴 <4.0%: Low (luxury/high-end properties)

EDGE CASES TO HANDLE:
- rental_data is null → Hide card
- annual_rent is 0 → Hide card
- estimated_value is 0 → Hide card (safety check)
- is_city_average flag → Change subtitle text

TEST PROCEDURE:
1. Open http://localhost:5000 in browser
2. Navigate to Property Valuation tab
3. Enter: Unit, Dubai Hills, 300 sqm
4. Click "Get Property Valuation"
5. Verify:
   ✅ Yield card appears after results load
   ✅ Shows percentage (e.g., "5.8%")
   ✅ Shows subtitle with comparable count
   ✅ Color matches yield level (green/orange/red)
6. Test edge case: Enter "Unknown Area"
7. Verify:
   ✅ Valuation shows (may have low confidence)
   ✅ Yield card either shows city average or hidden

EXPECTED VISUAL:
```
┌─────────────────────────────────────┐
│ Gross Rental Yield                  │
│                                     │
│         5.82%                       │  ← Green color
│                                     │
│ Based on 38 rental comparables     │  ← Gray subtitle
└─────────────────────────────────────┘
```

STOP CONDITIONS:
- ❌ If card breaks existing layout → Check CSS grid
- ❌ If yield shows NaN → Add more null checks
- ❌ If console errors → Verify object structure

OUTPUT FORMAT:
Provide:
1. HTML code block (exact placement)
2. JavaScript code block (exact placement)
3. Line numbers for both insertions
4. Screenshot or description of expected visual result
```

---

## 🎯 PROMPT #3: PDF INTEGRATION

**Objective**: Include rental yield in PDF export  
**Files**: `templates/index.html` (PDF generation function only)  
**Lines Changed**: ~15 lines  
**Time**: 30 minutes  
**Risk**: 🟢 LOW (optional section, no breaking changes)

### **PROMPT FOR AI:**

```
TASK: Add rental yield to PDF valuation report

CONTEXT:
- File: /workspaces/avm-retyn/templates/index.html
- Function: generateValuationPDF() at line ~2200
- Current: PDF shows valuation, details, comparables table
- Desired: Add rental yield section after valuation details

REQUIREMENTS:
1. Check if rental_data exists before adding section
2. Calculate gross yield percentage
3. Display yield and annual rent amount
4. Match PDF formatting style (consistent fonts, spacing)
5. Don't break existing PDF layout

INSERTION POINT:
Find this section in generateValuationPDF() (around line 2280):
```javascript
doc.text(`${lastValuationData.total_comparables_found || 0} properties analyzed`, margin + 80, yPos);
yPos += 12;

// === COMPARABLE PROPERTIES TABLE ===
if (lastComparablesData && lastComparablesData.length > 0) {
```

INSERT BETWEEN "yPos += 12;" and "// === COMPARABLE PROPERTIES TABLE ===":
```javascript
yPos += 12;

// === RENTAL YIELD SECTION (NEW) ===
if (lastValuationData.rental_data && lastValuationData.rental_data.annual_rent) {
    const grossYield = (lastValuationData.rental_data.annual_rent / lastValuationData.estimated_value * 100).toFixed(2);
    
    checkPageBreak(20);
    
    // Yield percentage
    doc.setFontSize(10);
    doc.setTextColor(0, 0, 0);
    doc.setFont(undefined, 'bold');
    doc.text('Gross Rental Yield:', margin, yPos);
    doc.setFont(undefined, 'normal');
    doc.text(`${grossYield}%`, margin + 45, yPos);
    yPos += 6;
    
    // Annual rent amount
    doc.setFontSize(9);
    doc.setTextColor(100, 100, 100);
    doc.text(`(Annual Rent: ${formatNumber(lastValuationData.rental_data.annual_rent)} AED)`, margin, yPos);
    yPos += 6;
    
    // Comparables count
    doc.text(`Based on ${lastValuationData.rental_data.count} rental comparables`, margin, yPos);
    yPos += 12;
}
// === END RENTAL YIELD SECTION ===

// === COMPARABLE PROPERTIES TABLE ===
if (lastComparablesData && lastComparablesData.length > 0) {
```

FORMATTING SPECIFICATIONS:
- Font: Helvetica (matches existing PDF)
- Yield label: 10pt, bold, black
- Yield value: 10pt, normal, black
- Annual rent: 9pt, normal, gray (#646464)
- Spacing: 6pt between lines, 12pt after section
- Use existing formatNumber() helper for rent amount

VALIDATION CHECKS:
1. ✅ Check lastValuationData.rental_data exists
2. ✅ Check annual_rent is truthy (not 0 or null)
3. ✅ Use checkPageBreak(20) before section
4. ✅ Use formatNumber() for consistent number formatting

EXPECTED PDF OUTPUT:
```
Price per Sq.M: 13,000 AED/m²
Value Range: 3,864,000 - 4,536,000 AED
Comparable Properties: 42 properties analyzed

Gross Rental Yield: 5.82%
(Annual Rent: 245,000 AED)
Based on 38 rental comparables

Comparable Properties Used
┌───────────────────────────────────┐
│ Project Name | Size | Sale Price │
│ ...                               │
└───────────────────────────────────┘
```

TEST PROCEDURE:
1. Generate valuation for Dubai Hills Unit (300 sqm)
2. Wait for results to load
3. Click "📄 Download Valuation Report (PDF)"
4. Open PDF file
5. Verify:
   ✅ Rental Yield section appears after valuation details
   ✅ Shows percentage (e.g., "5.82%")
   ✅ Shows annual rent amount formatted with commas
   ✅ Shows comparables count
   ✅ Spacing/alignment matches rest of PDF
   ✅ No page break issues

EDGE CASE:
- If no rental_data → Section not added (PDF unchanged)
- If rental_data but annual_rent = 0 → Section not added

STOP CONDITIONS:
- ❌ If PDF formatting breaks → Check font sizes/spacing
- ❌ If page breaks incorrectly → Adjust checkPageBreak(20) value
- ❌ If numbers show NaN → Verify formatNumber() called correctly

OUTPUT FORMAT:
Provide:
1. Complete code block with exact insertion point
2. Line numbers for modification
3. Before/After PDF section structure diagram
```

---

## 🎯 PROMPT #4: TESTING & VALIDATION

**Objective**: Verify rental yield feature works correctly  
**Files**: None (testing only)  
**Time**: 60 minutes  
**Risk**: 🟢 NONE (observation only)

### **PROMPT FOR AI:**

```
TASK: Execute comprehensive test suite for rental yield feature

CONTEXT:
- Feature: Rental yield calculator in AVM
- Components: Backend query + Frontend display + PDF export
- Test environment: Local development server

TEST SUITE:

═══════════════════════════════════════════════════════
TEST 1: NORMAL CASE - DUBAI HILLS UNIT
═══════════════════════════════════════════════════════
**Objective**: Verify standard property with good rental data

**Steps**:
1. Start application: `python app.py`
2. Open http://localhost:5000
3. Login with credentials
4. Navigate to Property Valuation tab
5. Enter:
   - Property Type: Unit
   - Location: Dubai Hills
   - Size: 300 sqm
6. Click "Get Property Valuation"
7. Wait for results (~2 seconds)

**Expected Results**:
✅ Valuation shows ~4.0-4.5M AED
✅ Rental Yield card visible
✅ Yield shows 5.5-6.5% (green color)
✅ Subtitle: "Based on XX rental comparables" (XX > 20)
✅ No console errors
✅ Response time < 2 seconds

**Actual Results**: [RECORD HERE]
- Valuation: __________ AED
- Yield: __________%
- Color: __________
- Comparables: __________
- Errors: __________

═══════════════════════════════════════════════════════
TEST 2: EDGE CASE - RARE AREA
═══════════════════════════════════════════════════════
**Objective**: Verify fallback to city-wide average

**Steps**:
1. Enter:
   - Property Type: Villa
   - Location: Al Barsha South
   - Size: 400 sqm
2. Click "Get Property Valuation"

**Expected Results**:
✅ Valuation shows (may have lower confidence)
✅ Rental Yield card visible
✅ Subtitle: "City-wide average (XXX rentals)" OR card hidden
✅ No crashes

**Actual Results**: [RECORD HERE]
- Yield shown: Yes / No
- Subtitle text: __________
- City average flag: __________

═══════════════════════════════════════════════════════
TEST 3: EDGE CASE - NO RENTAL DATA
═══════════════════════════════════════════════════════
**Objective**: Verify graceful handling of missing data

**Steps**:
1. Check database: `SELECT COUNT(*) FROM rentals WHERE area_en = 'Jumeirah Golf Estates';`
2. If count < 3, use this area; else pick another rare area
3. Enter this area with any property type

**Expected Results**:
✅ Valuation succeeds normally
✅ Rental Yield card hidden (display: none)
✅ Console shows: "⚠️ Rental data not available"
✅ No JavaScript errors

**Actual Results**: [RECORD HERE]
- Card visible: Yes / No
- Console message: __________
- Errors: __________

═══════════════════════════════════════════════════════
TEST 4: PDF EXPORT
═══════════════════════════════════════════════════════
**Objective**: Verify yield appears in PDF report

**Steps**:
1. Generate valuation for Dubai Hills Unit (300 sqm)
2. Click "📄 Download Valuation Report (PDF)"
3. Open downloaded PDF

**Expected Results**:
✅ PDF downloads successfully
✅ Rental Yield section present
✅ Shows percentage (format: "5.82%")
✅ Shows annual rent with commas
✅ Shows comparables count
✅ Formatting consistent with rest of PDF
✅ No overlapping text
✅ Section appears after valuation details, before comparables table

**Actual Results**: [RECORD HERE]
- PDF downloaded: Yes / No
- Yield section present: Yes / No
- Formatting issues: __________

═══════════════════════════════════════════════════════
TEST 5: PERFORMANCE BENCHMARK
═══════════════════════════════════════════════════════
**Objective**: Verify performance impact acceptable

**Steps**:
1. Measure baseline (without yield):
   ```bash
   time curl -X POST http://localhost:5000/api/property/valuation \
     -H "Content-Type: application/json" \
     -d '{"property_type":"Unit","area":"Dubai Hills","size_sqm":300}'
   ```
2. Measure with yield implementation
3. Compare response times

**Expected Results**:
✅ Total response time < 2.0 seconds
✅ Rental query adds < 500ms overhead
✅ No database timeouts
✅ Memory usage stable

**Actual Results**: [RECORD HERE]
- Baseline time: __________ seconds
- With yield time: __________ seconds
- Overhead: __________ ms
- Acceptable: Yes / No

═══════════════════════════════════════════════════════
TEST 6: EDGE CASE - INVALID PROPERTY TYPE
═══════════════════════════════════════════════════════
**Objective**: Verify error handling when valuation fails

**Steps**:
1. Enter invalid property type: "Spaceship"
2. Click "Get Property Valuation"

**Expected Results**:
✅ Error message shown to user
✅ No yield calculation attempted
✅ No JavaScript console errors
✅ Page remains functional

**Actual Results**: [RECORD HERE]
- Error handled: Yes / No
- Console errors: __________

═══════════════════════════════════════════════════════
TEST 7: DATABASE QUERY INSPECTION
═══════════════════════════════════════════════════════
**Objective**: Verify SQL queries correct

**Steps**:
1. Check server logs during valuation request
2. Look for rental query execution
3. Verify SQL syntax and parameters

**Expected Log Output**:
```
🏗️ [DB] Calculating valuation for 300.0sqm Unit in Dubai Hills
✅ [DB] Using 45 comparables with area-specific (Unit) search
🏠 [RENTAL] Found 38 rental comparables, median: 245,000 AED/year
💰 [DB] Valuation complete: 4,200,000 AED (87.3% confidence)
```

**Actual Results**: [RECORD HERE]
- Rental query executed: Yes / No
- Comparables found: __________
- Median rent: __________ AED
- Errors in logs: __________

═══════════════════════════════════════════════════════
SUMMARY CHECKLIST
═══════════════════════════════════════════════════════
- [ ] All 7 tests passed
- [ ] No JavaScript console errors
- [ ] No Python exceptions in logs
- [ ] Response time < 2 seconds
- [ ] PDF includes yield section
- [ ] Edge cases handled gracefully
- [ ] Code follows project conventions (PEP 8, type hints, logging)

PASS CRITERIA:
- ✅ 7/7 tests pass: APPROVED FOR PRODUCTION
- ⚠️ 5-6 tests pass: NEEDS MINOR FIXES
- ❌ < 5 tests pass: MAJOR ISSUES, DO NOT DEPLOY

OUTPUT FORMAT:
Provide:
1. Test results for all 7 cases
2. Screenshots of UI (yield card visible)
3. PDF sample with yield section
4. Performance metrics (response times)
5. Any errors encountered
6. PASS/FAIL recommendation
```

---

## 📊 IMPLEMENTATION TIMELINE

**Total Estimated Time**: 3-4 hours (vs 12 hours original)

```
Hour 1: Backend Implementation
├─ 0:00-0:15: Read implementation plan
├─ 0:15-0:45: Write rental query code
├─ 0:45-1:00: Test with curl/Postman
└─ [CHECKPOINT: Backend returns rental_data]

Hour 2: Frontend Display
├─ 1:00-1:15: Add HTML yield card
├─ 1:15-1:40: Add JavaScript calculation
├─ 1:40-2:00: Test in browser UI
└─ [CHECKPOINT: Yield visible in UI]

Hour 3: PDF & Testing
├─ 2:00-2:20: Add yield to PDF
├─ 2:20-2:40: Test PDF download
├─ 2:40-3:00: Run test suite
└─ [CHECKPOINT: All tests pass]

Hour 4: Polish & Documentation
├─ 3:00-3:15: Fix any edge cases
├─ 3:15-3:30: Add color indicators
├─ 3:30-3:45: Update documentation
└─ 3:45-4:00: Final verification

[DONE: Rental Yield feature complete]
```

---

## 🚨 TROUBLESHOOTING GUIDE

### **Problem**: Rental query returns 0 results

**Symptoms**: rental_data is always None, card never shows

**Debug Steps**:
```bash
# 1. Check rentals table has data
psql $DATABASE_URL -c "SELECT COUNT(*) FROM rentals;"
# Expected: > 600,000

# 2. Check specific area
psql $DATABASE_URL -c "SELECT COUNT(*) FROM rentals WHERE \"AREA_EN\" = 'Dubai Hills';"
# Expected: > 1,000

# 3. Check property type matching
psql $DATABASE_URL -c "SELECT DISTINCT \"PROP_SUB_TYPE_EN\" FROM rentals WHERE \"AREA_EN\" = 'Dubai Hills';"
# Verify "UNIT" or similar exists

# 4. Test exact query
psql $DATABASE_URL -c "SELECT AVG(\"ANNUAL_AMOUNT\") FROM rentals WHERE LOWER(\"AREA_EN\") = 'dubai hills' AND \"PROP_SUB_TYPE_EN\" ILIKE '%UNIT%';"
```

**Solutions**:
- ✅ Fix column name casing (use double quotes for case-sensitive)
- ✅ Adjust LIKE pattern (ILIKE for case-insensitive)
- ✅ Check parameter binding syntax

---

### **Problem**: Response time > 2 seconds

**Symptoms**: Valuation takes 3-4 seconds with rental query

**Debug Steps**:
```bash
# 1. Measure query time
psql $DATABASE_URL -c "EXPLAIN ANALYZE SELECT * FROM rentals WHERE LOWER(\"AREA_EN\") = 'dubai hills' LIMIT 50;"

# 2. Check if index exists
psql $DATABASE_URL -c "\di" | grep rentals
```

**Solutions**:
```sql
-- Add index for faster queries
CREATE INDEX idx_rentals_area_type ON rentals("AREA_EN", "PROP_SUB_TYPE_EN");
CREATE INDEX idx_rentals_amount ON rentals("ANNUAL_AMOUNT") WHERE "ANNUAL_AMOUNT" > 10000;
```

---

### **Problem**: Yield shows NaN or Infinity

**Symptoms**: Card shows "--%" or "NaN%" or "Inf%"

**Debug Steps**:
```javascript
// Add console logging
console.log('Rental data:', valuation.rental_data);
console.log('Estimated value:', valuation.estimated_value);
console.log('Annual rent:', valuation.rental_data?.annual_rent);
```

**Solutions**:
- ✅ Add null checks before division
- ✅ Verify estimated_value > 0
- ✅ Use parseFloat() before toFixed()

---

### **Problem**: PDF section overlaps or breaks layout

**Symptoms**: Text overlapping, missing sections

**Solutions**:
- ✅ Increase checkPageBreak() value (20 → 30)
- ✅ Adjust yPos increments (6 → 8)
- ✅ Verify formatNumber() function exists

---

## ✅ SUCCESS CRITERIA

Feature is PRODUCTION-READY when:

- [x] Backend returns rental_data field in valuation response
- [x] rental_data contains: annual_rent, count, price_range
- [x] Frontend displays yield card when data available
- [x] Yield card hidden when no rental data
- [x] Color coding works: Green (≥6%), Orange (4-6%), Red (<4%)
- [x] PDF includes yield section (when data available)
- [x] All 7 test cases pass
- [x] Response time < 2 seconds
- [x] No console errors or Python exceptions
- [x] Code follows project guidelines (type hints, logging, PEP 8)

**LAUNCH DECISION**: ✅ GO / ⚠️ NEEDS FIXES / ❌ NO GO

---

## 📚 ADDITIONAL RESOURCES

**Database Schema Reference**:
```sql
-- Rentals table structure
CREATE TABLE rentals (
    "AREA_EN" TEXT,                 -- Location name
    "PROP_SUB_TYPE_EN" TEXT,        -- Property type
    "ANNUAL_AMOUNT" NUMERIC,        -- Annual rent (AED)
    "ACTUAL_AREA" NUMERIC,          -- Size (sqm)
    "REGISTRATION_DATE" DATE,       -- Transaction date
    "ROOMS" TEXT                    -- Bedroom count
);
```

**Typical Dubai Rental Yields**:
- Luxury areas (Palm, Downtown): 3-4%
- Premium areas (Marina, JBR): 4-5%
- Mid-market (Dubai Hills, JVC): 5-6%
- Affordable (International City, DSO): 7-9%

**Market Benchmarks**:
- Dubai average: 5.5% gross yield
- Global average: 4.5% gross yield
- Excellent yield: > 6.5%
- Poor yield: < 3.5%

---

**END OF STRUCTURED PROMPTS**

*These prompts are optimized for AI-assisted development. Follow sequentially for best results.*
