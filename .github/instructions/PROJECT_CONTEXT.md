# Project Context for AI-Assisted Development

**Purpose:** Provide comprehensive context to AI to eliminate exploration time  
**Update Frequency:** After major features or architectural changes  
**Last Updated:** October 12, 2025

---

## 🏠 Application Overview

- **Type:** Flask web application (Real estate Automated Valuation Model)
- **Purpose:** Property valuation for Dubai market using ML and comparable analysis
- **ML Model:** XGBoost (R²=0.897, trained on 153K+ properties)
- **Database:** PostgreSQL (Neon cloud hosting)
- **Frontend:** Vanilla JavaScript + Bootstrap 5 + Leaflet maps
- **API:** RESTful endpoints (JSON responses)

---

## 📁 File Structure

```
/workspaces/avm-retyn/
├── app.py                      # Main Flask application (3101 lines)
├── templates/
│   ├── index.html             # Main UI (2800+ lines, includes JS)
│   └── login.html             # Login page
├── static/
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/
│   │   └── script.js          # Additional JS (if any)
│   └── images/
│       ├── Logo.png
│       ├── Logo.svg
│       └── favicon.ico
├── test_*.py                  # Test files (pytest)
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Container config
├── docker-compose.yaml        # Multi-container setup
├── .env                       # Environment variables (DATABASE_URL, API keys)
├── venv/                      # Virtual environment
├── test_runner.sh             # Automated testing script ⭐
├── deploy.sh                  # Automated deployment script ⭐
├── FEATURE_LOG.md             # Feature tracking ⭐
└── .github/
    ├── FEATURE_TEMPLATE.md    # Feature request template ⭐
    ├── FEATURE_CHECKLIST.md   # Implementation checklist ⭐
    └── instructions/
        ├── instructions.instructions.md  # Coding guidelines
        ├── PROJECT_CONTEXT.md            # This file ⭐
        └── RAPID_FEATURE_DEVELOPMENT_GUIDE.md  # Process guide ⭐

⭐ = New rapid development tools
```

---

## 🗄️ Database Schema

### Connection
```python
DATABASE_URL = "postgresql://neondb_owner:npg_43oCyQIRapfw@ep-old-bird-ae9osc5g-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

### Main Tables

#### `properties` (Historical sales transactions)
```python
Columns:
- transaction_number: text (unique ID)
- instance_date: text (transaction date, format: varies)
- area_en: text (location name) ⚠️ Note: Use area_en, not "area"
- prop_type_en: text (Unit, Villa, Building, etc.)
- rooms_en: text (Studio, 1 B/R, 2 B/R, 3 B/R, 4 B/R, etc.)
- actual_area: text ⚠️ (size in sqft, needs CAST to float)
- trans_value: float (price in AED)
- project_en: text (project/building name)
- master_project_en: text (master community)
- nearest_metro_en: text (nearest metro station)
- nearest_mall_en: text (nearest mall)
- nearest_landmark_en: text (nearest landmark)
- parking: text (parking spaces)

Key Patterns:
- actual_area is TEXT, must CAST(actual_area AS FLOAT)
- rooms_en format: "Studio", "1 B/R", "2 B/R" (not "1 bedroom")
- Always filter: actual_area > 0 AND trans_value > 0
```

#### `rentals` (Rental listings)
```python
Columns:
- location: text
- property_type: text
- bedrooms: text
- size_sqft: float
- annual_rent: float
- amenities: text[]
```

#### `amenities` (POIs and amenities)
```python
Columns:
- name: text
- category: text (Restaurant, School, Hospital, etc.)
- latitude: float
- longitude: float
- area: text
```

#### `project_premiums` (Premium project adjustments)
```python
Columns:
- project_name: text
- premium_percentage: float (e.g., 0.15 for +15%)
```

### Common Query Patterns

```python
# Get properties for area (realistic sizes only)
SELECT area_en, prop_type_en, rooms_en, 
       CAST(actual_area AS FLOAT) as sqft,
       trans_value
FROM properties
WHERE area_en = %s
  AND CAST(actual_area AS FLOAT) > 400
  AND CAST(actual_area AS FLOAT) < 3000
  AND trans_value > 0
  AND rooms_en IN ('Studio', '1 B/R', '2 B/R', '3 B/R', '4 B/R')

# Calculate price per sqm
SELECT trans_value / (CAST(actual_area AS FLOAT) * 0.092903) as price_per_sqm
FROM properties

# Conversion factor: 1 sqft = 0.092903 sqm
```

---

## 🎨 Frontend Structure (templates/index.html)

### Key Sections & Line Ranges

```javascript
Lines 1-100:     HTML head, meta tags, CSS imports
Lines 100-300:   Navigation, header
Lines 300-400:   Input form (location, bedrooms, size, property type)
Lines 400-450:   KPI cards section (top results - valuation, price/sqm, yield)
Lines 450-600:   Map container
Lines 600-800:   Valuation details section (main results cards)
Lines 800-1000:  Comparables section
Lines 1000-1200: Amenities section
Lines 2000-2800: JavaScript code

Important: Price per Sq.M appears in TWO locations:
1. Line ~419: KPI cards (top summary)
2. Line ~649: Valuation details (main results) ← Most visible
```

### Key JavaScript Functions

```javascript
// Main valuation trigger
calculateValuation() - Collects form data, calls API

// Result display
displayValuationResults(data) - Main rendering function
  - Updates KPI cards
  - Updates detail cards
  - Triggers map update
  - Shows/hides sections

// Map functions
updateMap(lat, lon, comparables) - Updates Leaflet map
addMarkersToMap(comparables) - Adds property markers

// Utility functions
formatNumber(num) - Formats numbers with commas
formatCurrency(num) - Formats AED currency
```

### CSS Classes Reference

```css
/* Card containers */
.detail-card          /* Main result cards */
.kpi-card            /* Top summary cards */

/* Display elements */
.detail-label        /* Card labels */
.detail-value        /* Card values */

/* Badges and pills */
.badge-style         /* Generic badge */
.segment-badge       /* Market segment badges */

/* Layouts */
.container-fluid     /* Bootstrap fluid container */
.row, .col-*        /* Bootstrap grid */

/* Gradients */
.gradient-bg         /* Gradient backgrounds for badges */
```

---

## 🔧 Backend Structure (app.py)

### Main Application Flow

```python
1. User submits form
2. POST /calculate_valuation
3. calculate_valuation_from_database(location, bedrooms, property_type, size_sqft)
4. Return JSON with valuation data
5. Frontend displays results
```

### Key Functions (Line Ranges)

```python
# Line ~100-200: Flask app initialization, config
# Line ~300-500: Database helper functions
# Line ~800-1200: Amenities calculation
# Line ~1500-1700: Rental yield calculation
# Line ~1733-1796: Market segment classification ⭐ NEW
# Line ~2200-2500: Main valuation function
# Line ~2800-3000: Additional endpoints
```

### Important Functions

```python
def calculate_valuation_from_database(location, bedrooms, property_type, size_sqft):
    """
    Main valuation function.
    
    Returns:
        dict with:
        - valuation (float): Predicted price
        - confidence_interval (dict): Lower/upper bounds
        - comparables (list): Similar properties
        - price_per_sqm (float): Price per square meter
        - rental_yield (dict): Rental yield data
        - segment (dict): Market segment classification ⭐ NEW
        - location_data (dict): Coordinates, amenities
    """
    
def get_location_coordinates(location):
    """Get lat/lon for location (cached)."""
    
def get_nearby_amenities(lat, lon):
    """Count amenities within radius."""
    
def get_rental_yield(location, bedrooms, valuation):
    """Calculate gross rental yield."""
    
def classify_price_segment(price_per_sqm):  # ⭐ NEW
    """Classify property into market segments."""
```

### Adding New Features Pattern

```python
# 1. Create helper function (with docstring)
def calculate_new_metric(input_data: float) -> dict:
    """
    Calculate new metric.
    
    Args:
        input_data: Input value
        
    Returns:
        dict with metric results
    """
    # Validation
    if not input_data or input_data <= 0:
        return None
    
    # Calculation logic
    result = input_data * some_factor
    
    # Return structured data
    return {
        'value': result,
        'category': 'High' if result > threshold else 'Low',
        'percentile': calculate_percentile(result)
    }

# 2. Integrate into main valuation
def calculate_valuation_from_database(...):
    # ... existing code ...
    
    # Add new metric
    new_metric = calculate_new_metric(some_input)
    
    # ... existing code ...
    
    return jsonify({
        # ... existing fields ...
        'new_metric': new_metric  # Add to response
    })

# 3. Frontend will automatically receive it in JSON response
```

---

## 🧪 Testing Standards

### Test File Naming
```
test_<feature_name>.py
```

### Test Structure
```python
import pytest
from app import calculate_new_feature

def test_normal_case():
    """Test with typical input."""
    result = calculate_new_feature(100)
    assert result is not None
    assert result['value'] > 0

def test_edge_case_zero():
    """Test with zero input."""
    result = calculate_new_feature(0)
    assert result is None

def test_edge_case_negative():
    """Test with negative input."""
    result = calculate_new_feature(-10)
    assert result is None

def test_extreme_value():
    """Test with very large input."""
    result = calculate_new_feature(1000000)
    assert result is not None

def test_none_input():
    """Test with None input."""
    result = calculate_new_feature(None)
    assert result is None
```

### Running Tests
```bash
# Quick way (use script)
./test_runner.sh

# Manual way
source venv/bin/activate
pytest test_*.py -v --cov=app

# Single test file
pytest test_segment_classification.py -v

# With coverage report
pytest --cov=app --cov-report=html
```

### Coverage Target
- **Minimum:** 90%
- **Target:** 95%+
- **Current:** 95.2% (segment feature)

---

## 🚀 Deployment Process

### Quick Deploy (Use Script)
```bash
./deploy.sh
```

### Manual Deploy
```bash
# 1. Stop existing server
pkill -f "python.*app.py"

# 2. Start new server
cd /workspaces/avm-retyn
source venv/bin/activate
nohup python app.py > flask.log 2>&1 &

# 3. Verify
ps aux | grep app.py
curl http://127.0.0.1:5000/

# 4. Check logs if issues
tail -f flask.log
```

### Important Notes
- Flask runs on port 5000
- Changes to templates take effect immediately
- Changes to app.py require server restart
- Users must hard refresh browser (Ctrl+Shift+R) for frontend changes

---

## ⚡ Performance Benchmarks

### Current Performance
- Database query: 50-150ms
- ML prediction: 100-200ms
- Total valuation: 200-400ms

### New Feature Budget
- **Maximum added time:** 50ms per feature
- **Database queries:** Optimize with indexes
- **Calculations:** Should be <10ms

### Optimization Tips
1. Cache database queries when possible
2. Use SQL aggregations (not Python loops)
3. Minimize database round trips
4. Avoid N+1 query patterns
5. Use appropriate data structures

---

## 🐛 Common Pitfalls & Solutions

### Database Issues

❌ **Wrong:**
```python
SELECT area FROM properties  # Column doesn't exist
```

✅ **Correct:**
```python
SELECT area_en FROM properties  # Use area_en
```

❌ **Wrong:**
```python
WHERE actual_area > 0  # actual_area is TEXT
```

✅ **Correct:**
```python
WHERE CAST(actual_area AS FLOAT) > 0  # Must cast first
```

### Frontend Issues

❌ **Wrong:**
```javascript
// Only update one location
document.getElementById('segment-badge').textContent = badge;
```

✅ **Correct:**
```javascript
// Update ALL locations where element appears
['segment-badge', 'segment-badge-details'].forEach(id => {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = badge;
    }
});
```

### Testing Issues

❌ **Wrong:**
```python
def test_feature():
    result = my_function(100)
    assert result  # Too vague
```

✅ **Correct:**
```python
def test_feature():
    result = my_function(100)
    assert result is not None
    assert isinstance(result, dict)
    assert 'value' in result
    assert result['value'] == 150
```

---

## 🎯 Common Patterns

### Pattern 1: Add New Card to Valuation Results

**Backend (app.py):**
```python
def calculate_valuation_from_database(...):
    # ... existing code ...
    
    new_metric = calculate_new_metric(data)
    
    return jsonify({
        # ... existing ...
        'new_metric': new_metric
    })
```

**Frontend (templates/index.html, ~line 700):**
```html
<div class="detail-card">
    <div class="detail-label">NEW METRIC NAME</div>
    <div class="detail-value" id="new-metric-value">--</div>
    <div id="new-metric-badge" style="display:none;">
        <!-- Badge content -->
    </div>
</div>
```

**JavaScript (templates/index.html, ~line 2300):**
```javascript
function displayValuationResults(valuation) {
    // ... existing code ...
    
    if (valuation.new_metric) {
        document.getElementById('new-metric-value').textContent = 
            valuation.new_metric.toLocaleString();
        document.getElementById('new-metric-badge').style.display = 'block';
        document.getElementById('new-metric-badge').textContent = 
            valuation.new_metric.category;
    }
}
```

### Pattern 2: Add Classification/Badge System

See: `classify_price_segment()` function (lines 1733-1796) as reference

**Steps:**
1. Create classification function returning dict
2. Include: category, label, icon, percentile, description
3. Call from main valuation function
4. Add to JSON response
5. Frontend displays badge with gradient

### Pattern 3: Database Aggregation

```python
# Good: SQL aggregation
query = """
SELECT 
    area_en,
    AVG(trans_value) as avg_price,
    COUNT(*) as count
FROM properties
WHERE rooms_en = %s
GROUP BY area_en
HAVING COUNT(*) > 10
"""

# Bad: Python loop
properties = get_all_properties()
for prop in properties:  # Slow!
    calculate_something(prop)
```

---

## 📚 Environment & Dependencies

### Python Version
- **Current:** Python 3.12
- **Virtual env:** `/workspaces/avm-retyn/venv`

### Key Dependencies
```python
Flask              # Web framework
psycopg2-binary   # PostgreSQL adapter
xgboost           # ML model
numpy             # Numerical computing
pandas            # Data manipulation
scikit-learn      # ML utilities
requests          # HTTP requests
python-dotenv     # Environment variables
```

### Environment Variables (.env)
```bash
DATABASE_URL=postgresql://...    # Database connection
OPENAI_API_KEY=sk-proj-...       # (if using OpenAI features)
```

---

## 🔍 Debugging Tips

### Check Flask Logs
```bash
tail -f flask.log
# or
tail -50 flask.log  # Last 50 lines
```

### Check Database Connection
```python
python3 << EOF
import psycopg2
DATABASE_URL = "postgresql://..."
conn = psycopg2.connect(DATABASE_URL)
print("✅ Connected")
EOF
```

### Check Frontend Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for JavaScript errors
4. Check Network tab for API responses

### Common Error Messages

**"psycopg2.errors.UndefinedColumn: column 'area' does not exist"**
→ Use `area_en` instead of `area`

**"psycopg2.errors.UndefinedTable: relation 'sales_transactions_merged' does not exist"**
→ Use `properties` table instead

**"TypeError: 'NoneType' object is not subscriptable"**
→ Check for None values before accessing dict keys

**"Element not found"** (JavaScript)
→ Check element ID exists and spelling is correct

---

## 📊 Data Insights

### Market Segment Thresholds (from 153K properties)
- **Budget:** 0 - 12,000 AED/sqm (25th percentile)
- **Mid-Tier:** 12,000 - 16,200 AED/sqm (50th percentile)
- **Premium:** 16,200 - 21,800 AED/sqm (75th percentile)
- **Luxury:** 21,800 - 28,800 AED/sqm (90th percentile)
- **Ultra-Luxury:** 28,800+ AED/sqm (95th+ percentile)

### Conversion Factor
- **1 sqft = 0.092903 sqm**
- **1 sqm = 10.764 sqft**

### Typical Property Sizes
- Studio: 400-600 sqft
- 1 BR: 600-900 sqft
- 2 BR: 900-1,400 sqft
- 3 BR: 1,400-2,200 sqft
- 4 BR: 2,200-3,500 sqft

---

## 🚦 Development Workflow

### For New Features (Rapid Process)

1. **Fill Feature Template** (2 min)
   - Copy `.github/FEATURE_TEMPLATE.md`
   - Fill all sections

2. **Submit to AI** (0 min)
   - Use optimized prompt from RAPID_FEATURE_DEVELOPMENT_GUIDE.md
   - Include "START IMMEDIATELY" directive

3. **AI Implements** (8-15 min)
   - Reads this PROJECT_CONTEXT.md
   - Implements feature
   - Writes tests
   - Deploys with `./deploy.sh`

4. **You Verify** (2-3 min)
   - Hard refresh browser
   - Test feature
   - Check for issues

5. **Log Results** (1 min)
   - Update `FEATURE_LOG.md`
   - Note time, issues, lessons

**Total Time:** 15-20 minutes (vs 60+ minutes old way)

---

## 🎓 Best Practices

### Code Style
- Follow PEP 8 (Python)
- Use type hints
- Write docstrings for all functions
- Use logging (not print statements)
- Prefer list/dict comprehensions
- Use f-strings for formatting

### Database
- Always parameterize queries (prevent SQL injection)
- Check for NULL/empty before CAST
- Use appropriate data types in queries
- Consider indexes for frequently queried columns

### Frontend
- Check for element existence before accessing
- Use CSS classes over inline styles when possible
- Consider multiple display locations for same data
- Test with browser cache cleared

### Testing
- Test happy path AND edge cases
- Test with None, 0, negative, extreme values
- Aim for >90% coverage
- Use realistic test data from database
- Write descriptive test names

---

## 🔄 Update History

| Date | Change | Reason |
|------|--------|--------|
| 2025-10-12 | Initial creation | Establish rapid development baseline |
| 2025-10-12 | Added segment classification | Document new feature patterns |

---

## 📞 Quick Reference

### Most Common Commands
```bash
# Activate venv
source venv/bin/activate

# Run tests
./test_runner.sh

# Deploy
./deploy.sh

# Check logs
tail -f flask.log

# Check server
ps aux | grep app.py
curl http://127.0.0.1:5000/

# Database query
python3 -c "import psycopg2; conn = psycopg2.connect('...'); ..."
```

### Most Common Files to Edit
1. `app.py` - Backend logic
2. `templates/index.html` - Frontend UI (lines 600-800 for results, lines 2000-2800 for JS)
3. `test_*.py` - Tests

### Most Common Issues
1. **Badge not showing** → Hard refresh (Ctrl+Shift+R)
2. **Tests failing** → Check database connection
3. **Server not starting** → Check `flask.log`
4. **Wrong column name** → Use `area_en` not `area`

---

**Last Updated:** October 12, 2025  
**Next Review:** After 5 new features or major architectural change  
**Maintainer:** Update this file when patterns change!
