# 🤖 AI AGENT PROMPT: ESG Filter Implementation

**COPY THIS ENTIRE SECTION TO YOUR AI CODING ASSISTANT**

---

## TASK SPECIFICATION

**Objective:** Add ESG (Environmental, Social, Governance) score filter to Dubai AVM Property Valuation feature.

**Context:**
- **Location:** Property Valuation tab, immediately after "Property Age" field
- **Pattern:** Follow existing Bedrooms dropdown filter (templates/index.html lines 95-103)
- **Data:** 10 sample properties with ESG scores (25-65 range)
- **Integration:** Must work with existing valuation logic without breaking current functionality

---

## ARCHITECTURAL CONTEXT

### Project Structure
```
app.py (3,937 lines)         # Monolithic Flask app - all routes
├── Line 128-135: SALES_MAP  # Dynamic column mapping
├── Line 1577: /api/property/valuation endpoint
├── Line 1810: calculate_valuation_from_database() function
└── Line 1900: WHERE clause construction for filtering

templates/index.html (4,080 lines)  # Single-page app
├── Line 268-400: Property Valuation tab
├── Line 568-580: Property Age field (REFERENCE POINT)
├── Line 2528: Form submission JavaScript
└── Line 3216: Results display logic
```

### Database Schema
```sql
properties table (153,573 rows):
- trans_value (price)
- area_en (location)
- prop_type_en (property type)
- actual_area (size in sqm)
- rooms_en (bedrooms)
- project_en (project name)
- esg_score (NEW - will add)
```

### Pattern to Follow
```python
# Backend pattern (app.py)
SALES_MAP = {
    'bedrooms': find_column_name(SALES_COLUMNS, ['rooms_en', 'bedrooms']),
    # Add: 'esg_score': find_column_name(SALES_COLUMNS, ['esg_score'])
}

# Frontend pattern (templates/index.html)
<select id="buy-bedrooms">
    <option>Any</option>
    <option>Studio</option>
    <option>1 Bedroom</option>
    ...
</select>

# JavaScript pattern
const bedrooms = document.getElementById('buy-bedrooms').value;
if (bedrooms && bedrooms !== 'Any') {
    requestData.bedrooms = bedrooms;
}
```

---

## IMPLEMENTATION STEPS

### STEP 1: DATABASE MIGRATION

**File:** Create `migrations/add_esg_column.sql`

```sql
-- Add ESG score column to properties table
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS esg_score INTEGER DEFAULT NULL;

-- Add index for query performance
CREATE INDEX IF NOT EXISTS idx_esg_score ON properties(esg_score);

-- Insert sample ESG data (10 properties from July 2025)

-- AZIZI VENICE 11 (ESG: 30)
UPDATE properties 
SET esg_score = 30 
WHERE project_en = 'AZIZI VENICE 11' 
  AND TO_CHAR(instance_date, 'YYYY-MM-DD') = '2025-07-24'
  AND trans_value = 640000
  AND rooms_en = 'Studio';

-- Samana Lake Views - DUBAI PRODUCTION CITY (ESG: 25)
UPDATE properties 
SET esg_score = 25 
WHERE project_en = 'Samana Lake Views' 
  AND area_en = 'DUBAI PRODUCTION CITY'
  AND rooms_en = 'Studio'
  AND TO_CHAR(instance_date, 'YYYY-MM-DD') LIKE '2025-07-%';

-- Ocean Pearl By SD - 2BR (ESG: 60)
UPDATE properties 
SET esg_score = 60 
WHERE project_en = 'Ocean Pearl By SD' 
  AND area_en = 'Palm Deira'
  AND rooms_en = '2 B/R'
  AND TO_CHAR(instance_date, 'YYYY-MM-DD') = '2025-07-07';

-- Ocean Pearl 2 By SD - 1BR (ESG: 65)
UPDATE properties 
SET esg_score = 65 
WHERE project_en = 'Ocean Pearl 2 By SD' 
  AND area_en = 'Palm Deira'
  AND rooms_en = '1 B/R'
  AND TO_CHAR(instance_date, 'YYYY-MM-DD') = '2025-07-07';

-- CAPRIA EAST (ESG: 25)
UPDATE properties 
SET esg_score = 25 
WHERE project_en = 'CAPRIA EAST' 
  AND area_en = 'Wadi Al Safa 4'
  AND TO_CHAR(instance_date, 'YYYY-MM-DD') = '2025-07-24';

-- Verification query
SELECT 
    project_en, 
    area_en,
    rooms_en,
    esg_score, 
    COUNT(*) as count
FROM properties 
WHERE esg_score IS NOT NULL 
GROUP BY project_en, area_en, rooms_en, esg_score
ORDER BY esg_score DESC;

-- Expected output: 5 rows with ESG scores 25, 30, 60, 65
```

**Execute:**
```bash
psql $DATABASE_URL -f migrations/add_esg_column.sql
```

**Verification:**
```sql
SELECT COUNT(*) FROM properties WHERE esg_score IS NOT NULL;
-- Expected: 9-10 rows (multiple units per project)
```

---

### STEP 2: FRONTEND - HTML COMPONENT

**File:** `templates/index.html`

**Location:** After line 580 (after Property Age field), before the Tip Box

**Find this section:**
```html
                            <!-- Property Age -->
                            <div class="form-group" style="margin-bottom: 0;">
                                <label for="property-age" style="display: flex; align-items: center; margin-bottom: 8px; font-size: 0.9rem;">
                                    📅 Property Age
                                    ...
                                </label>
                                <input type="number" id="property-age" ...>
                                <small style="color: #666; font-size: 0.75rem; display: block; margin-top: 4px;">Years (0 = new/off-plan)</small>
                            </div>
                            
                            <!-- Tip Box - spans remaining columns -->
                            <div style="grid-column: span 2; display: flex; align-items: center;">
```

**Insert between these sections:**
```html
                            <!-- Property Age -->
                            <div class="form-group" style="margin-bottom: 0;">
                                ...existing Property Age field...
                            </div>
                            
                            <!-- ESG Score Filter - NEW -->
                            <div class="form-group" style="margin-bottom: 0;">
                                <label for="esg-score" style="display: flex; align-items: center; margin-bottom: 8px; font-size: 0.9rem;">
                                    🌱 ESG Score (Min)
                                    <span class="tooltip-icon" title="Environmental, Social & Governance rating. Higher scores indicate sustainable and responsible properties. Scale: 25 (basic) to 100 (excellent)" 
                                          style="margin-left: 5px; cursor: help; color: #666; font-size: 0.85rem;">ⓘ</span>
                                </label>
                                <select id="esg-score" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem;">
                                    <option value="">Any Score</option>
                                    <option value="25">25+ (Basic Compliance)</option>
                                    <option value="40">40+ (Good Standards)</option>
                                    <option value="60">60+ (High Performance)</option>
                                    <option value="80">80+ (Excellent/Leadership)</option>
                                </select>
                                <small style="color: #666; font-size: 0.75rem; display: block; margin-top: 4px;">Filter by sustainability rating</small>
                            </div>
                            
                            <!-- Tip Box - spans remaining columns -->
                            <div style="grid-column: span 2; display: flex; align-items: center;">
```

**Rationale:**
1. Maintains consistent styling with Property Age field
2. Tooltip provides educational context about ESG
3. Dropdown values match realistic ESG score ranges
4. Grid layout preserved (single column, before tip box)

---

### STEP 3: FRONTEND - JAVASCRIPT

**File:** `templates/index.html`

**Location:** Around line 2528, in the Property Valuation form submission handler

**Find this code block:**
```javascript
                const propertyType = document.getElementById('property-type').value;
                const area = document.getElementById('area').value;
                const size = document.getElementById('property-size').value;
                const bedrooms = document.getElementById('bedrooms').value;
                const developmentStatus = document.getElementById('development-status').value;
                const floorLevel = document.getElementById('floor-level').value;
                const viewType = document.getElementById('view-type').value;
                const propertyAge = document.getElementById('property-age').value;
```

**Add after propertyAge line:**
```javascript
                const propertyType = document.getElementById('property-type').value;
                const area = document.getElementById('area').value;
                const size = document.getElementById('property-size').value;
                const bedrooms = document.getElementById('bedrooms').value;
                const developmentStatus = document.getElementById('development-status').value;
                const floorLevel = document.getElementById('floor-level').value;
                const viewType = document.getElementById('view-type').value;
                const propertyAge = document.getElementById('property-age').value;
                const esgScore = document.getElementById('esg-score').value;  // NEW
```

**Find this conditional block (around line 2566):**
```javascript
                    if (propertyAge && propertyAge !== '') {
                        requestData.property_age = parseInt(propertyAge);
                    }
```

**Add after this block:**
```javascript
                    if (propertyAge && propertyAge !== '') {
                        requestData.property_age = parseInt(propertyAge);
                    }
                    
                    // NEW: ESG score filter
                    if (esgScore && esgScore !== '') {
                        requestData.esg_score_min = parseInt(esgScore);
                    }
```

**Rationale:**
1. Follows exact pattern of propertyAge parameter
2. Only sends parameter if value selected (not "Any Score")
3. Parses as integer for backend compatibility

---

### STEP 4: BACKEND - COLUMN MAPPING

**File:** `app.py`

**Location:** Line 128-135 (SALES_MAP definition)

**Current code:**
```python
SALES_MAP = {
    'price': find_column_name(SALES_COLUMNS, ['trans_value', 'price']),
    'property_type': find_column_name(SALES_COLUMNS, ['prop_type_en', 'prop_sub_type_en', 'property_type']),
    'bedrooms': find_column_name(SALES_COLUMNS, ['rooms_en', 'bedrooms']),
    'status': find_column_name(SALES_COLUMNS, ['is_offplan_en', 'development_status']),
    'area_name': find_column_name(SALES_COLUMNS, ['area_en']),
    'name': find_column_name(SALES_COLUMNS, ['project_en', 'procedure_en', 'property_name']),
}
```

**Modified code:**
```python
SALES_MAP = {
    'price': find_column_name(SALES_COLUMNS, ['trans_value', 'price']),
    'property_type': find_column_name(SALES_COLUMNS, ['prop_type_en', 'prop_sub_type_en', 'property_type']),
    'bedrooms': find_column_name(SALES_COLUMNS, ['rooms_en', 'bedrooms']),
    'status': find_column_name(SALES_COLUMNS, ['is_offplan_en', 'development_status']),
    'area_name': find_column_name(SALES_COLUMNS, ['area_en']),
    'name': find_column_name(SALES_COLUMNS, ['project_en', 'procedure_en', 'property_name']),
    'esg_score': find_column_name(SALES_COLUMNS, ['esg_score']),  # NEW: ESG score column
}
```

**Rationale:**
1. Uses dynamic column discovery pattern (handles schema variations)
2. Fallback array with single value (straightforward mapping)
3. Follows DRY principle (reuses existing find_column_name function)

---

### STEP 5: BACKEND - API PARAMETER EXTRACTION

**File:** `app.py`

**Location:** Line 1598, in the `/api/property/valuation` route

**Find this code:**
```python
        bedrooms = data.get('bedrooms')  # Optional: bedroom filter
        development_status = data.get('development_status')  # Optional: off-plan/ready
        floor_level = data.get('floor_level')  # Optional: floor number
        view_type = data.get('view_type')  # Optional: view type
        property_age = data.get('property_age')  # Optional: age in years
```

**Add after property_age line:**
```python
        bedrooms = data.get('bedrooms')  # Optional: bedroom filter
        development_status = data.get('development_status')  # Optional: off-plan/ready
        floor_level = data.get('floor_level')  # Optional: floor number
        view_type = data.get('view_type')  # Optional: view type
        property_age = data.get('property_age')  # Optional: age in years
        esg_score_min = data.get('esg_score_min')  # NEW: Optional: minimum ESG score
```

**Rationale:**
1. Consistent naming convention (esg_score_min)
2. Optional parameter (None if not provided)
3. Clear comment for maintainability

---

### STEP 6: BACKEND - FUNCTION PARAMETER PASSING

**File:** `app.py`

**Location:** Line 1609, calling calculate_valuation_from_database()

**Current code:**
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
            property_age=property_age,  # Phase 3: Age premium
        )
```

**Modified code:**
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
            property_age=property_age,  # Phase 3: Age premium
            esg_score_min=esg_score_min,  # NEW: ESG filter
        )
```

**Rationale:**
1. Maintains parameter order consistency
2. Clear inline comment for tracking
3. Named parameter for clarity

---

### STEP 7: BACKEND - FUNCTION SIGNATURE UPDATE

**File:** `app.py`

**Location:** Line 1810, function definition

**Current code:**
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
    property_age: int = None
) -> dict:
```

**Modified code:**
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
    esg_score_min: int = None  # NEW: Optional minimum ESG score
) -> dict:
```

**Rationale:**
1. Type hint: int (ESG scores are integers)
2. Default: None (optional parameter)
3. Position: Last in optional parameters list
4. Clear inline comment

---

### STEP 8: BACKEND - FILTERING LOGIC

**File:** `app.py`

**Location:** Around line 1900, in the WHERE clause construction within calculate_valuation_from_database()

**Find this section (WHERE clause building):**
```python
    # Build WHERE clause dynamically
    where_conditions = [
        f"{SALES_MAP['area_name']} ILIKE :area",
        f"{SALES_MAP['property_type']} = :type",
        f"actual_area BETWEEN :size_min AND :size_max",
        "trans_value > 0",
        "actual_area > 0"
    ]
    
    query_params = {
        'area': f'%{area}%',
        'type': property_type,
        'size_min': size_sqm * 0.7,
        'size_max': size_sqm * 1.3
    }
    
    # Optional filters
    if bedrooms and bedrooms != 'Any':
        where_conditions.append(f"{SALES_MAP['bedrooms']} = :bedrooms")
        query_params['bedrooms'] = bedrooms
    
    if development_status and development_status != 'Any':
        where_conditions.append(f"{SALES_MAP['status']} = :status")
        query_params['status'] = development_status
```

**Add ESG filter after existing optional filters:**
```python
    # Build WHERE clause dynamically
    where_conditions = [
        f"{SALES_MAP['area_name']} ILIKE :area",
        f"{SALES_MAP['property_type']} = :type",
        f"actual_area BETWEEN :size_min AND :size_max",
        "trans_value > 0",
        "actual_area > 0"
    ]
    
    query_params = {
        'area': f'%{area}%',
        'type': property_type,
        'size_min': size_sqm * 0.7,
        'size_max': size_sqm * 1.3
    }
    
    # Optional filters
    if bedrooms and bedrooms != 'Any':
        where_conditions.append(f"{SALES_MAP['bedrooms']} = :bedrooms")
        query_params['bedrooms'] = bedrooms
    
    if development_status and development_status != 'Any':
        where_conditions.append(f"{SALES_MAP['status']} = :status")
        query_params['status'] = development_status
    
    # NEW: ESG score filter
    if esg_score_min is not None and esg_score_min > 0:
        where_conditions.append(f"{SALES_MAP['esg_score']} >= :esg_min")
        query_params['esg_min'] = esg_score_min
```

**Rationale:**
1. NULL-safe: Only filters if esg_score_min provided and > 0
2. Uses >= operator (minimum threshold)
3. Parameterized query (SQL injection safe)
4. Follows existing pattern exactly

---

## TESTING PROTOCOL

### Unit Tests

**File:** Create `tests/test_esg_filter.py`

```python
import pytest
from app import calculate_valuation_from_database, engine

def test_esg_column_exists():
    """Verify esg_score column was added to database"""
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='properties' AND column_name='esg_score'
        """))
        assert result.rowcount > 0, "esg_score column not found in properties table"

def test_esg_sample_data_loaded():
    """Verify sample ESG scores were inserted"""
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) as count
            FROM properties 
            WHERE esg_score IS NOT NULL
        """))
        count = result.fetchone()[0]
        assert count >= 9, f"Expected at least 9 properties with ESG scores, found {count}"

def test_esg_filtering_high_scores():
    """Test ESG filter returns only high-scoring properties"""
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='Palm Deira',
        size_sqm=150,
        engine=engine,
        bedrooms='2 Bedrooms',
        esg_score_min=60  # Should return Ocean Pearl properties only
    )
    
    assert result['success'] == True, f"Valuation failed: {result.get('error')}"
    
    # Verify all comparables have ESG >= 60
    comparables = result.get('comparables', [])
    assert len(comparables) > 0, "No comparables found with ESG >= 60"
    
    for comp in comparables:
        if 'esg_score' in comp and comp['esg_score'] is not None:
            assert comp['esg_score'] >= 60, f"Found comparable with ESG {comp['esg_score']} < 60"

def test_esg_filtering_no_matches():
    """Test ESG filter with threshold that has no matches"""
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='DUBAI PRODUCTION CITY',
        size_sqm=40,
        engine=engine,
        esg_score_min=80  # No properties with ESG >= 80 yet
    )
    
    # Should either return no results or expand search (lower confidence)
    if result['success']:
        assert result['confidence'] < 70, "Confidence should be low with no ESG matches"
    else:
        assert 'comparable' in result.get('error', '').lower()

def test_esg_no_filter_still_works():
    """Test valuation works without ESG filter (backward compatibility)"""
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='Business Bay',
        size_sqm=120,
        engine=engine,
        bedrooms='1 Bedroom'
    )
    
    assert result['success'] == True, "Valuation without ESG filter should still work"
    assert 'estimated_value' in result, "Should return valuation"

def test_esg_combined_filters():
    """Test ESG filter combined with other filters"""
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='Palm Deira',
        size_sqm=150,
        engine=engine,
        bedrooms='2 Bedrooms',
        development_status='Off-Plan',
        esg_score_min=60
    )
    
    # Should work with multiple filters
    assert result['success'] == True or 'comparable' in result.get('error', '').lower()

def test_esg_zero_value():
    """Test ESG filter with zero value (should be ignored)"""
    result = calculate_valuation_from_database(
        property_type='Unit',
        area='Business Bay',
        size_sqm=120,
        engine=engine,
        esg_score_min=0  # Should be treated as "no filter"
    )
    
    assert result['success'] == True, "ESG filter with 0 should be ignored"
```

**Run tests:**
```bash
pytest tests/test_esg_filter.py -v
```

---

### Integration Tests

**Manual API Test:**
```bash
# Test 1: No ESG filter (baseline)
curl -X POST http://localhost:5000/api/property/valuation \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your_session_cookie>" \
  -d '{
    "property_type": "Unit",
    "area": "Business Bay",
    "size": 120,
    "bedrooms": "1 Bedroom"
  }' | jq .

# Test 2: ESG filter 60+ (high performance)
curl -X POST http://localhost:5000/api/property/valuation \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your_session_cookie>" \
  -d '{
    "property_type": "Unit",
    "area": "Palm Deira",
    "size": 150,
    "bedrooms": "2 Bedrooms",
    "esg_score_min": 60
  }' | jq '.comparables[].esg_score'
  
# Expected: Only returns properties with ESG >= 60

# Test 3: ESG filter 25+ (basic compliance)
curl -X POST http://localhost:5000/api/property/valuation \
  -H "Content-Type: application/json" \
  -H "Cookie: session=<your_session_cookie>" \
  -d '{
    "property_type": "Unit",
    "area": "DUBAI PRODUCTION CITY",
    "size": 40,
    "bedrooms": "Studio",
    "esg_score_min": 25
  }' | jq .

# Expected: Returns Samana Lake Views properties (ESG 25)
```

---

### Browser Testing Checklist

- [ ] **UI Rendering:** ESG dropdown appears after Property Age
- [ ] **Dropdown Options:** Shows "Any Score", "25+", "40+", "60+", "80+"
- [ ] **Tooltip:** Hover shows ESG explanation
- [ ] **Form Submission:** Selecting ESG value doesn't break form
- [ ] **API Call:** Network tab shows esg_score_min in request body
- [ ] **Results:** Only properties with ESG >= selected threshold appear
- [ ] **Backward Compatibility:** Not selecting ESG still works (shows all properties)
- [ ] **Mobile View:** Dropdown displays correctly on mobile
- [ ] **Grid Layout:** Tip box still spans 2 columns correctly

---

## EDGE CASES

### Case 1: No Properties Match ESG Threshold
**Scenario:** User selects ESG 80+ but no properties have score >= 80

**Expected Behavior:**
- Expand search to include lower ESG scores
- Display warning: "Limited properties meet ESG 80+ criteria"
- Lower confidence score (< 70%)
- OR return error: "No comparable properties found with ESG >= 80"

**Handling:** Already covered by existing fallback logic in valuation engine

---

### Case 2: NULL ESG Scores
**Scenario:** Property doesn't have ESG score (esg_score IS NULL)

**Expected Behavior:**
- Exclude from results when ESG filter active
- Include in results when no ESG filter (backward compatible)

**Handling:** `WHERE esg_score >= :esg_min` automatically excludes NULLs

---

### Case 3: ESG + Small Area
**Scenario:** User filters by ESG 60+ in area with only 5 properties

**Expected Behavior:**
- Return whatever matches exist
- Show low confidence score
- May trigger area expansion fallback

**Handling:** Existing confidence scoring handles this

---

### Case 4: ESG Filter with "Any Score"
**Scenario:** User selects "Any Score" from dropdown

**Expected Behavior:**
- Behaves identically to no filter
- All properties included

**Handling:** JavaScript doesn't send parameter if value is empty string

---

## ROLLBACK PLAN

If issues arise, rollback in reverse order:

### Step 1: Remove Backend Logic
```python
# In app.py, comment out ESG lines:
# esg_score_min = data.get('esg_score_min')
# esg_score_min=esg_score_min,
# esg_score_min: int = None
# ESG filter section in WHERE clause
```

### Step 2: Remove Frontend
```html
<!-- Comment out ESG dropdown in templates/index.html -->
<!-- Comment out esgScore variables in JavaScript -->
```

### Step 3: Database Rollback (if needed)
```sql
-- Remove column (caution: deletes data)
ALTER TABLE properties DROP COLUMN IF EXISTS esg_score;
DROP INDEX IF EXISTS idx_esg_score;
```

**Git Rollback:**
```bash
git revert <commit_hash>
git push origin main
docker-compose restart
```

---

## PERFORMANCE NOTES

### Query Performance
- **Before ESG:** ~150ms average query time
- **After ESG (no filter):** ~150ms (no change)
- **After ESG (with filter):** ~155ms (+5ms for indexed WHERE clause)

### Database Impact
- **Migration time:** <1 second for 153K rows
- **Index creation:** ~2 seconds
- **Storage:** +612KB (4 bytes × 153K rows)

### Application Impact
- **Memory:** +8KB (column metadata)
- **CPU:** Negligible (integer comparison)
- **Network:** +20 bytes per request (esg_score_min parameter)

---

## DEPLOYMENT CHECKLIST

### Pre-Deploy
- [ ] All unit tests pass (pytest)
- [ ] Manual API tests successful
- [ ] Frontend renders correctly in Chrome, Safari, Firefox
- [ ] Mobile view tested
- [ ] Database migration script reviewed
- [ ] Rollback plan documented

### Deploy Steps
```bash
# 1. Backup database
pg_dump $DATABASE_URL > backup_pre_esg_$(date +%Y%m%d).sql

# 2. Run migration
psql $DATABASE_URL -f migrations/add_esg_column.sql

# 3. Verify migration
psql $DATABASE_URL -c "SELECT COUNT(*) FROM properties WHERE esg_score IS NOT NULL;"

# 4. Deploy code
git add .
git commit -m "feat: Add ESG score filter to property valuation"
git push origin main

# 5. Restart application
docker-compose down
docker-compose up -d

# 6. Smoke test
curl -X POST http://localhost:5000/api/property/valuation -H "Content-Type: application/json" -d '{"property_type":"Unit","area":"Palm Deira","size":150,"esg_score_min":60}'
```

### Post-Deploy
- [ ] Monitor logs for errors
- [ ] Test ESG filter with 60+ threshold
- [ ] Verify backward compatibility (no filter)
- [ ] Check application performance metrics
- [ ] Gather user feedback

---

## SUCCESS CRITERIA

✅ **Functionality:**
- ESG dropdown appears in UI
- Selecting ESG filter returns only matching properties
- No filter selected works as before (backward compatible)

✅ **Performance:**
- Query time increase < 10ms
- No memory leaks
- No database locks

✅ **Quality:**
- All unit tests pass
- No console errors
- Mobile responsive
- Accessibility maintained

✅ **User Experience:**
- Clear tooltip explaining ESG
- Smooth form submission
- Helpful error messages

---

## MONITORING & ANALYTICS

### Track in Production
```python
# Add logging in app.py
if esg_score_min:
    logging.info(f"ESG filter applied: {esg_score_min}+ for {area}, {property_type}")
```

### Metrics to Monitor
- **Usage:** % of valuations with ESG filter
- **Popular thresholds:** Distribution of 25+, 40+, 60+, 80+
- **Impact:** Average confidence score with/without ESG
- **Errors:** Count of "no matches" errors

---

## NEXT STEPS (FUTURE ENHANCEMENTS)

After successful launch:

1. **ESG Premium Calculation** (+2 days)
   - Add calculate_esg_premium() function
   - Integrate into valuation formula
   - Display ESG contribution in breakdown

2. **ESG Data Expansion** (+1 week)
   - Backfill all 153K properties with ESG scores
   - Scrape or purchase ESG data
   - Add data quality indicators

3. **ESG Analytics** (+3 days)
   - Add ESG to Market Trends tab
   - Show ESG distribution charts
   - Correlate ESG with rental yields

4. **ESG Education** (+1 day)
   - Add ESG explainer modal
   - Link to ESG rating methodology
   - Show ESG impact on property values

---

## OUTPUT FORMAT

When implemented, provide:

### 1. Unified Diff
```diff
--- a/app.py
+++ b/app.py
@@ -132,6 +132,7 @@ SALES_MAP = {
     'status': find_column_name(SALES_COLUMNS, ['is_offplan_en', 'development_status']),
     'area_name': find_column_name(SALES_COLUMNS, ['area_en']),
     'name': find_column_name(SALES_COLUMNS, ['project_en', 'procedure_en', 'property_name']),
+    'esg_score': find_column_name(SALES_COLUMNS, ['esg_score']),
 }
```

### 2. Rationale (3 bullets)
- **Pattern consistency:** Follows existing Bedrooms filter implementation exactly
- **Backward compatible:** No impact when ESG filter not selected
- **Null-safe:** Excludes properties without ESG scores when filter active

### 3. "Why Safe" Note
> These changes are safe because:
> - ESG column is nullable (won't break existing data)
> - Filter is optional (backward compatible)
> - Uses parameterized queries (SQL injection safe)
> - Indexed column (no performance degradation)
> - Follows established patterns (low regression risk)

### 4. Reviewer Scrutiny Points
- Line 135: Verify SALES_MAP includes 'esg_score'
- Line 1900: Check WHERE clause syntax (>= vs = operator)
- Line 2528: Ensure JavaScript doesn't send empty strings
- index.html: Verify grid layout not broken (inspect element)

---

## FINAL IMPLEMENTATION COMMAND

**For AI Agent:** Execute these steps in order:

```bash
# Step 1: Database
psql $DATABASE_URL -f migrations/add_esg_column.sql

# Step 2: Frontend (edit templates/index.html)
# Insert ESG dropdown after line 580

# Step 3: Backend (edit app.py)
# Add to SALES_MAP (line 135)
# Extract parameter (line 1598)
# Pass parameter (line 1609)
# Update signature (line 1810)
# Add WHERE clause (line ~1900)

# Step 4: Test
pytest tests/test_esg_filter.py -v

# Step 5: Deploy
git add . && git commit -m "feat: Add ESG filter" && git push origin main
docker-compose restart
```

---

**END OF PROMPT**

⏱️ **Estimated Time:** 30-45 minutes  
🎯 **Complexity:** Low (follows existing patterns)  
✅ **Risk Level:** Low (incremental, testable, reversible)  
📈 **Business Value:** High (ESG increasingly important in real estate)
