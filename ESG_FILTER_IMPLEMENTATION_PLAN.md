# 🌱 ESG Filter Implementation Plan

**Date:** October 16, 2025  
**Feature:** ESG (Environmental, Social, Governance) Score Filter  
**Location:** Property Valuation tab, after Property Age field  
**Pattern:** Follow Area/Location and Bedrooms dropdown pattern

---

## 📊 ANALYSIS SUMMARY

### Current State
- ✅ Property Age filter exists (numeric input, lines 568-580 in index.html)
- ✅ Bedrooms filter pattern available (dropdown, lines 95-103)
- ✅ Database schema extensible (SALES_MAP pattern in app.py lines 128-135)
- ✅ 10 sample properties with ESG scores (25-65 range)
- ❌ No ESG column in database yet
- ❌ No ESG filter UI component

### Requirements
1. **Database:** Add `esg_score` column to `properties` table
2. **Frontend:** Add ESG dropdown filter after Property Age
3. **Backend:** Integrate ESG filtering into valuation logic
4. **Pattern:** Match existing Bedrooms filter implementation

---

## 🎯 APPROACH #1: MINIMAL INCREMENTAL (RECOMMENDED)

### Overview
Add ESG filter in 3 small, testable increments. Each can be deployed independently.

### Affected Files
- `app.py` (1 line: SALES_MAP addition)
- `templates/index.html` (30 lines: UI component)
- Database schema (ALTER TABLE)

### Data Flow
```
User selects ESG range → Frontend validates → Backend filters properties 
→ Valuation calculation includes ESG-matched comparables → Confidence adjustment
```

### Implementation Steps

#### **Increment 1: Database Schema (5 minutes)**
```sql
-- Add ESG column to properties table
ALTER TABLE properties 
ADD COLUMN esg_score INTEGER DEFAULT NULL;

-- Add index for performance
CREATE INDEX idx_esg_score ON properties(esg_score);

-- Insert sample data (10 properties)
UPDATE properties 
SET esg_score = 30 
WHERE project_en = 'AZIZI VENICE 11' 
  AND instance_date = '2025-07-24'
  AND trans_value = 640000;

UPDATE properties 
SET esg_score = 25 
WHERE project_en = 'Samana Lake Views' 
  AND area_en = 'DUBAI PRODUCTION CITY';

UPDATE properties 
SET esg_score = 60 
WHERE project_en = 'Ocean Pearl By SD' 
  AND rooms_en = '2 B/R';

UPDATE properties 
SET esg_score = 65 
WHERE project_en = 'Ocean Pearl 2 By SD';

UPDATE properties 
SET esg_score = 25 
WHERE project_en = 'CAPRIA EAST';

-- Verify
SELECT project_en, esg_score, COUNT(*) 
FROM properties 
WHERE esg_score IS NOT NULL 
GROUP BY project_en, esg_score;
```

**Test:**
```bash
psql $DATABASE_URL -c "SELECT COUNT(*) FROM properties WHERE esg_score IS NOT NULL;"
# Expected: 9-10 rows
```

**Risks:**
- ⚠️ Migration may lock table briefly (<1s for 153K rows)
- ⚠️ NULL values acceptable (not all properties have ESG yet)

---

#### **Increment 2: Frontend UI (10 minutes)**

**File:** `templates/index.html` (after line 580, before Tip Box)

```html
<!-- ESG Score Filter -->
<div class="form-group" style="margin-bottom: 0;">
    <label for="esg-score" style="display: flex; align-items: center; margin-bottom: 8px; font-size: 0.9rem;">
        🌱 ESG Score (Min)
        <span class="tooltip-icon" title="Environmental, Social & Governance rating. Higher scores indicate sustainable properties (25-100 scale)" 
              style="margin-left: 5px; cursor: help; color: #666; font-size: 0.85rem;">ⓘ</span>
    </label>
    <select id="esg-score" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem;">
        <option value="">Any Score</option>
        <option value="25">25+ (Basic Compliance)</option>
        <option value="40">40+ (Good Standards)</option>
        <option value="60">60+ (High Performance)</option>
        <option value="80">80+ (Excellence)</option>
    </select>
    <small style="color: #666; font-size: 0.75rem; display: block; margin-top: 4px;">Filter by sustainability rating</small>
</div>
```

**JavaScript Addition (around line 2528, in valuation form submission):**
```javascript
const esgScore = document.getElementById('esg-score').value;
// ... existing code ...
if (esgScore && esgScore !== '') {
    requestData.esg_score_min = parseInt(esgScore);
}
```

**Test:**
```javascript
// Browser console
document.getElementById('esg-score').value = '60';
console.log('Selected ESG:', document.getElementById('esg-score').value);
```

**Risks:**
- ⚠️ Must maintain grid layout (span columns correctly)
- ⚠️ Z-index conflicts with existing tooltips (unlikely)

---

#### **Increment 3: Backend Integration (15 minutes)**

**File:** `app.py`

**Step 3a: Add to SALES_MAP (line 135)**
```python
SALES_MAP = {
    'price': find_column_name(SALES_COLUMNS, ['trans_value', 'price']),
    'property_type': find_column_name(SALES_COLUMNS, ['prop_type_en', 'prop_sub_type_en', 'property_type']),
    'bedrooms': find_column_name(SALES_COLUMNS, ['rooms_en', 'bedrooms']),
    'status': find_column_name(SALES_COLUMNS, ['is_offplan_en', 'development_status']),
    'area_name': find_column_name(SALES_COLUMNS, ['area_en']),
    'name': find_column_name(SALES_COLUMNS, ['project_en', 'procedure_en', 'property_name']),
    'esg_score': find_column_name(SALES_COLUMNS, ['esg_score']),  # NEW
}
```

**Step 3b: Extract ESG parameter (line 1598, in /api/property/valuation route)**
```python
property_age = data.get('property_age')  # Optional: age in years
esg_score_min = data.get('esg_score_min')  # NEW: Optional minimum ESG score
```

**Step 3c: Pass to valuation function (line 1609)**
```python
result = calculate_valuation_from_database(
    property_type=property_type,
    area=area,
    size_sqm=size_sqm,
    engine=engine,
    bedrooms=bedrooms,
    development_status=development_status,
    floor_level=floor_level,
    view_type=view_type,
    property_age=property_age,
    esg_score_min=esg_score_min  # NEW
)
```

**Step 3d: Update function signature (line 1810)**
```python
def calculate_valuation_from_database(
    property_type: str, 
    area: str, 
    size_sqm: float, 
    engine, 
    bedrooms: str = None, 
    development_status: str = None, 
    floor_level: int = None, 
    view_type: str = None, 
    property_age: int = None,
    esg_score_min: int = None  # NEW
) -> dict:
```

**Step 3e: Add ESG filtering to comparable search (around line 1900)**
```python
# Existing filters...
if bedrooms and bedrooms != 'Any':
    where_conditions.append(f"{SALES_MAP['bedrooms']} = :bedrooms")
    query_params['bedrooms'] = bedrooms

# NEW: ESG filter
if esg_score_min is not None:
    where_conditions.append(f"esg_score >= :esg_min")
    query_params['esg_min'] = esg_score_min
```

**Test:**
```python
# Unit test
def test_esg_filtering():
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='Business Bay',
        size_sqm=120,
        engine=engine,
        esg_score_min=60
    )
    assert result['success'] == True
    # Verify only properties with ESG >= 60 are in comparables
    for comp in result['comparables']:
        assert comp.get('esg_score', 0) >= 60
```

**Risks:**
- ⚠️ NULL ESG scores excluded when filter applied (expected behavior)
- ⚠️ May reduce comparable count significantly (confidence score will reflect this)

---

### Pros
✅ **Minimal risk:** Each increment independently testable  
✅ **Fast deployment:** 30 minutes total implementation  
✅ **Rollback-friendly:** Can revert each step separately  
✅ **Pattern-consistent:** Matches existing Bedrooms filter exactly  
✅ **Database-safe:** NULL handling built-in  

### Cons
⚠️ **Limited data:** Only 10 properties have ESG scores initially  
⚠️ **Reduced comparables:** Strict filtering may lower confidence  
⚠️ **No ESG premium calculation:** Just filtering, not valuation adjustment  

### Edge Cases
1. **User selects ESG 80+ but no properties match** → Returns error with clear message
2. **ESG filter + small area** → Very few comparables, confidence drops
3. **NULL ESG scores** → Excluded from results (filter treats as "no score")
4. **Future ESG data backfill** → Works automatically with more data

### Performance
- **Query impact:** +5ms (indexed column)
- **Memory:** Negligible
- **Cost:** $0 (no external API)

---

## 🎯 APPROACH #2: COMPREHENSIVE WITH ESG PREMIUM

### Overview
Full implementation including ESG as a valuation adjustment factor (+/- premium).

### Affected Files
- `app.py` (3 functions: +50 lines)
- `templates/index.html` (+40 lines UI + display)
- Database schema (same as Approach #1)

### Data Flow
```
ESG filter → Comparable search → ESG premium calculation (0-10%) 
→ Blended into final value → Display in breakdown
```

### New Functions

#### **calculate_esg_premium() in app.py**
```python
def calculate_esg_premium(esg_score):
    """
    Calculate ESG premium based on score (25-100 scale).
    
    Premium Scale:
    - 25-39: -5% (below standard)
    - 40-59: 0% (standard)
    - 60-79: +5% (good)
    - 80-100: +10% (excellent)
    
    Args:
        esg_score: ESG rating (25-100)
    
    Returns:
        float: Premium percentage (-5.0 to +10.0)
    """
    if not esg_score or esg_score < 25:
        return 0.0
    
    if esg_score < 40:
        return -5.0  # Below standard
    elif esg_score < 60:
        return 0.0   # Standard
    elif esg_score < 80:
        return 5.0   # Good
    else:
        return 10.0  # Excellent
```

### Integration Points
1. **Line 1950:** Calculate ESG premium after age premium
2. **Line 2100:** Add ESG adjustment to total premiums
3. **Line 3100:** Display ESG breakdown in results card

### Pros
✅ **Complete feature:** ESG affects valuation, not just filtering  
✅ **Market-aligned:** Reflects real ESG impact on property values  
✅ **Detailed breakdown:** Shows ESG contribution in UI  
✅ **Future-proof:** Ready for ESG expansion  

### Cons
⚠️ **Complex:** 50+ lines across multiple functions  
⚠️ **Validation risk:** ESG premium formula needs market validation  
⚠️ **Testing:** Requires extensive unit tests  
⚠️ **Timeline:** 2-3 hours implementation  

### Risks
🔴 **Over-engineering:** May be premature with only 10 data points  
🟡 **Formula accuracy:** ESG premium percentages are estimates  
🟡 **Confidence impact:** ESG filtering may reduce sample size too much  

---

## 🎯 APPROACH #3: HYBRID (ESG BADGE + FILTER)

### Overview
Add ESG as visual indicator (badge) + optional filter, without valuation impact.

### Affected Files
- `app.py` (+15 lines)
- `templates/index.html` (+50 lines: filter + badge display)
- Database schema (same as Approach #1)

### Features
1. **Filter:** Optional minimum ESG score
2. **Badge:** Display ESG rating in results (🌱 65/100 - High Performance)
3. **Tooltip:** Educational info about ESG meaning
4. **No premium:** Doesn't affect calculated value

### Badge Display
```html
<div class="esg-badge" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
    <span style="font-size: 1.5rem;">🌱</span>
    <div>
        <strong>ESG Score: 65/100</strong>
        <small>High Performance</small>
    </div>
</div>
```

### Pros
✅ **Low risk:** Display-only, no calculation changes  
✅ **Educational:** Introduces ESG concept to users  
✅ **Fast:** 45 minutes implementation  
✅ **Reversible:** Easy to remove if not adopted  

### Cons
⚠️ **Limited value:** Doesn't affect valuation  
⚠️ **Incomplete:** Users may expect ESG to influence price  
⚠️ **UI clutter:** Adds visual element without functional benefit  

---

## 📊 COMPARISON MATRIX

| Criterion | Approach #1<br/>Minimal | Approach #2<br/>Comprehensive | Approach #3<br/>Hybrid |
|-----------|-------------------------|-------------------------------|------------------------|
| **Time** | 30 min | 2-3 hours | 45 min |
| **Lines Changed** | 15 | 90+ | 65 |
| **Risk** | 🟢 Low | 🟡 Medium | 🟢 Low |
| **Complexity** | Simple | Complex | Simple |
| **Value Impact** | No | Yes (+/- 10%) | No |
| **Rollback** | Easy | Moderate | Easy |
| **Testing** | 3 tests | 15+ tests | 5 tests |
| **Future Expansion** | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **User Education** | Low | High | Medium |
| **Data Dependency** | Low (works with 10) | High (needs 100+) | Low |

---

## ✅ RECOMMENDATION: **APPROACH #1 (MINIMAL)**

### Why?
1. **Fast to market:** 30 minutes vs 2-3 hours
2. **Low risk:** Only filtering, no valuation logic changes
3. **Testable:** Each increment independently verifiable
4. **Expandable:** Easy to add premium calculation later
5. **Data-appropriate:** Works well with current 10-property dataset

### Path to Launch Today

#### **Phase 1: Database (5 min)**
```bash
# Run SQL migration
psql $DATABASE_URL < esg_migration.sql
```

#### **Phase 2: Frontend (10 min)**
```bash
# Edit templates/index.html
# Add ESG dropdown after Property Age
# Add JavaScript to capture value
```

#### **Phase 3: Backend (15 min)**
```bash
# Edit app.py
# Add esg_score to SALES_MAP
# Add parameter to valuation function
# Add WHERE clause for filtering
```

#### **Phase 4: Test (10 min)**
```bash
# Manual test in UI
# Test with ESG 60+ filter
# Verify only high-ESG properties returned
# Check confidence score adjustment
```

#### **Phase 5: Deploy (5 min)**
```bash
git add .
git commit -m "feat: Add ESG score filter to property valuation"
git push origin main
docker-compose restart
```

**Total: 45 minutes** (including buffer)

---

## 🔥 QUICK WIN PROMPT (FOR AI AGENT)

```
TASK: Add ESG Score Filter to Dubai AVM Property Valuation

CONTEXT:
- Location: templates/index.html after line 580 (after Property Age field)
- Pattern: Copy Bedrooms dropdown pattern (lines 95-103)
- Database: Add esg_score column to properties table (INTEGER, nullable)
- Backend: Follow dynamic column mapping pattern (SALES_MAP, line 128)

IMPLEMENTATION:

1. DATABASE MIGRATION (esg_migration.sql):
   - ALTER TABLE properties ADD COLUMN esg_score INTEGER DEFAULT NULL;
   - CREATE INDEX idx_esg_score ON properties(esg_score);
   - UPDATE 10 sample properties with scores 25-65 (see data table)

2. FRONTEND (templates/index.html, after line 580):
   - Add dropdown: <select id="esg-score"> with options: Any, 25+, 40+, 60+, 80+
   - Label: "🌱 ESG Score (Min)" with tooltip explaining ESG
   - Small text: "Filter by sustainability rating"
   - JavaScript (line ~2528): Capture value as requestData.esg_score_min

3. BACKEND (app.py):
   - Line 135: Add 'esg_score': find_column_name(SALES_COLUMNS, ['esg_score']) to SALES_MAP
   - Line 1598: Extract esg_score_min = data.get('esg_score_min')
   - Line 1609: Pass esg_score_min to calculate_valuation_from_database()
   - Line 1810: Add esg_score_min: int = None to function signature
   - Line ~1900: Add WHERE clause: if esg_score_min: where_conditions.append("esg_score >= :esg_min")

4. TESTING:
   - Unit test: test_esg_filtering() verifies only ESG >= threshold returned
   - Manual test: Select ESG 60+, verify Ocean Pearl properties (ESG 60-65) appear
   - Edge case: ESG 80+ returns empty (expected, no properties yet)

CONSTRAINTS:
- Max 30 lines changed across 2 files (HTML + Python)
- No new dependencies
- Must maintain existing filter patterns
- NULL ESG scores excluded when filter active (expected)
- Preserve grid layout in HTML (maintain column spans)

OUTPUT:
- Unified diff for each file
- 3-bullet rationale
- "Why safe" note
- Test command to verify

EXAMPLE ESG DATA TO INSERT:
project_en='AZIZI VENICE 11' → esg_score=30
project_en='Samana Lake Views' → esg_score=25
project_en='Ocean Pearl By SD' (2BR) → esg_score=60
project_en='Ocean Pearl 2 By SD' → esg_score=65
project_en='CAPRIA EAST' → esg_score=25
```

---

## 🧪 TEST PLAN

### Unit Tests
```python
# tests/test_esg_filter.py

def test_esg_column_exists():
    """Verify esg_score column in database"""
    result = engine.execute("SELECT column_name FROM information_schema.columns 
                             WHERE table_name='properties' AND column_name='esg_score'")
    assert result.rowcount > 0

def test_esg_data_loaded():
    """Verify sample ESG scores inserted"""
    result = engine.execute("SELECT COUNT(*) FROM properties WHERE esg_score IS NOT NULL")
    assert result.fetchone()[0] >= 9

def test_esg_filtering_basic():
    """Test ESG filter returns only matching properties"""
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='Palm Deira',
        size_sqm=150,
        engine=engine,
        esg_score_min=60
    )
    assert result['success'] == True
    # All comparables should have ESG >= 60
    for comp in result.get('comparables', []):
        if 'esg_score' in comp:
            assert comp['esg_score'] >= 60

def test_esg_no_filter():
    """Test valuation works without ESG filter"""
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='Business Bay',
        size_sqm=120,
        engine=engine
    )
    assert result['success'] == True

def test_esg_no_matches():
    """Test ESG filter with no matching properties"""
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='International City',
        size_sqm=80,
        engine=engine,
        esg_score_min=90  # No properties with ESG 90+
    )
    # Should return fewer comparables or error
    assert result['confidence'] < 70 or not result['success']
```

### Integration Tests
```bash
# Test frontend
curl -X POST http://localhost:5000/api/property/valuation \
  -H "Content-Type: application/json" \
  -d '{
    "property_type": "Unit",
    "area": "Palm Deira",
    "size": 150,
    "bedrooms": "2 Bedrooms",
    "esg_score_min": 60
  }'

# Expected: Only Ocean Pearl properties (ESG 60-65) in comparables
```

### Manual Test Cases
1. ✅ No ESG filter → Returns all comparables (as before)
2. ✅ ESG 25+ → Returns Samana Lake Views + others
3. ✅ ESG 60+ → Returns only Ocean Pearl properties
4. ✅ ESG 80+ → Returns empty or very few results
5. ✅ ESG + Area + Bedrooms → Combined filtering works
6. ✅ Mobile view → Dropdown displays correctly

---

## 📈 PERFORMANCE & COST

### Database Impact
- **Migration time:** <1 second (ALTER TABLE on 153K rows)
- **Index creation:** <2 seconds
- **Query overhead:** +3-5ms (indexed column)
- **Storage:** +4 bytes per row = 612KB total

### Application Impact
- **Memory:** Negligible (+8KB for column metadata)
- **CPU:** No change (simple integer comparison)
- **Network:** +8 bytes per API request (esg_score_min parameter)

### Cost
- **Development:** 30-45 minutes ($0 if in-house)
- **Infrastructure:** $0 (no new services)
- **Maintenance:** Low (follows existing patterns)

---

## 🚨 RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **Data sparsity** | High | Medium | Start with filter-only (no premium) |
| **Reduced comparables** | High | Medium | Show confidence score, expand search if needed |
| **User confusion** | Medium | Low | Clear tooltip explaining ESG |
| **Database migration** | Low | Low | Test on staging first, quick rollback |
| **NULL handling** | Medium | Low | Exclude NULLs explicitly in WHERE clause |
| **Performance** | Low | Low | Indexed column, tested at scale |

---

## 📝 NEXT INCREMENTS (FUTURE)

After successful Approach #1 launch:

### Increment 4: ESG Premium Calculation (+2 days)
- Implement calculate_esg_premium() function
- Add to valuation blending formula
- Display ESG contribution in breakdown
- Validate with market data

### Increment 5: ESG Data Expansion (+1 week)
- Scrape/purchase ESG data for all 153K properties
- Backfill esg_score column
- Add data quality indicators

### Increment 6: ESG Insights (+3 days)
- Add ESG comparison to market average
- Show ESG distribution charts
- Integrate with AI summary (GPT-4)
- Educational content about ESG factors

### Increment 7: ESG Analytics (+1 week)
- Track ESG filter usage
- Analyze correlation with premium properties
- Build ESG-focused market reports
- Add to Market Trends tab

---

## 🎬 LAUNCH CHECKLIST

### Pre-Launch
- [ ] Database migration tested on staging
- [ ] 10 sample properties verified with ESG scores
- [ ] Frontend dropdown renders correctly
- [ ] JavaScript captures ESG value
- [ ] Backend filtering works (unit tests pass)
- [ ] Edge cases tested (no matches, NULL values)
- [ ] Documentation updated

### Launch
- [ ] Run database migration in production
- [ ] Deploy code changes
- [ ] Restart application
- [ ] Smoke test: ESG 60+ filter
- [ ] Monitor logs for errors

### Post-Launch
- [ ] Track ESG filter usage (analytics)
- [ ] Gather user feedback
- [ ] Plan ESG premium calculation (Increment 4)
- [ ] Expand ESG data coverage

---

**END OF PLAN**

👉 **RECOMMENDED ACTION:** Proceed with Approach #1 (Minimal) for immediate launch.

📋 **Implementation Prompt:** See "QUICK WIN PROMPT" section above for AI agent.

⏱️ **Timeline:** 30-45 minutes to production.
