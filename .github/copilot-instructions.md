# GitHub Copilot Instructions - Dubai Real Estate AVM

## Project Context

**Retyn AVM** is a production-grade automated valuation model for Dubai real estate. It combines XGBoost ML (89.7% R²), 774K+ database records, geospatial analysis, and investment analytics into a Flask web application serving 17 REST APIs.

**Key Architecture:** Hybrid valuation system blending ML predictions (30%) with database comparables (70%) to achieve higher accuracy than pure ML. All data in PostgreSQL; CSV files are backup only.

## Critical File Structure

```
app.py (3,937 lines)           # Monolithic Flask app - all routes, logic, ML integration
valuation_engine.py (321 lines) # Standalone valuation with DB fallback
models/                         # XGBoost model files (5.1MB) - DO NOT regenerate without retraining
  ├── xgboost_model_v1.pkl
  ├── label_encoders_v1.pkl
  └── feature_columns_v1.pkl
data/                          # Training CSVs (30-110MB) - NOT in git, only for ML retraining
templates/index.html (4,080 lines) # Single-page app with 4 tabs (Buy/Rent/Trends/Valuation)
```

## Database Architecture (PostgreSQL)

**Primary Tables:**
- `properties` (153K rows): Sales transactions with `trans_value`, `area_en`, `prop_type_en`, `actual_area`, `rooms_en`
- `rentals` (620K rows): Rental listings with `annual_amount`, `prop_type_en`, `area_en`
- `area_coordinates` (70 rows): GPS + pre-calculated distances for location premiums
- `project_premiums` (10 rows): Brand premiums (Ciel 20%, Trump Tower 15%, etc.)
- `property_location_cache` (dynamic): 24-hour TTL cache to avoid recalculating geospatial premiums

**Column Mapping Pattern:**
```python
# Dynamic column discovery (handles schema variations)
SALES_MAP = {
    'price': find_column_name(SALES_COLUMNS, ['trans_value', 'price']),
    'property_type': find_column_name(SALES_COLUMNS, ['prop_type_en', 'property_type']),
    # ... fallback cascading for database flexibility
}
```

## Core Valuation Flow (app.py lines 1810-2575)

1. **Database Search** → Find comparables (area + type + size ±30%)
2. **Statistical Analysis** → Median/mean/std with outlier filtering
3. **ML Prediction** → XGBoost inference using 30 features
4. **Geospatial Adjustments** → Location premium calculation (see below)
5. **Project Premium** → Brand bonus 0-20% from `project_premiums` table
6. **Floor/View/Age Premiums** → Calculated adjustments (lines 659-823)
7. **Hybrid Blending** → `final_value = 0.7 * db_value + 0.3 * ml_value`
8. **Confidence Scoring** → 50-98% based on comparable count and data quality

**Critical Pattern:** Always blend ML with database - never use ML alone. See `calculate_valuation_from_database()` line 1810.

## Geospatial Premium System (Lines 199-870)

**Formula (capped at +70%):**
```python
total_premium = min(70, sum([
    max(0, 15 - distance_to_metro_km * 3),      # Metro: 15% @ 0km → 0% @ 5km
    max(0, 30 - distance_to_beach_km * 6),      # Beach: 30% @ 0km → 0% @ 5km
    max(0, 8 - distance_to_mall_km * 2),        # Mall: 8% @ 0km → 4km
    max(0, 10 - distance_to_business_km * 2),   # Business: 10% @ 0km → 5km
    (neighborhood_score - 3.0) * 4              # Neighborhood: -8% to +8%
]))
```

**Cache Pattern (M4 fix):** Check `property_location_cache` with `created_at > NOW() - INTERVAL '24 hours'` before calculating. Always update cache after calculation.

## Investment Features

### Flip Score (lines 3116-3590)
100-point system: Price Appreciation (30) + Liquidity (25) + Rental Yield (25) + Segment (20).
Queries both `properties` and `rentals` tables for comprehensive analysis.

### Arbitrage Score (lines 3746-3938)
Identifies undervalued properties by comparing asking price vs market comparables + rental yield potential.

### Rental Yield (integrated into valuation)
`gross_yield = (annual_rent / property_value) * 100` using median from `rentals` table filtered by area + type + size.

## Authentication (Lines 159-191)

**Hardcoded users - NO database:**
```python
AUTHORIZED_USERS = {
    'dhanesh@retyn.ai': {'password': 'retyn*#123', 'name': 'Dhanesh', 'id': 1},
    'jumi@retyn.ai': {'password': 'retyn*#123', 'name': 'Jumi', 'id': 2}
}
```
⚠️ **Security Issue:** Passwords in plaintext. DO NOT add more users here - this needs migration to hashed passwords + database.

## Development Workflow

**Start app:**
```bash
source venv/bin/activate  # Always use venv if present
python app.py             # Dev server on port 5000
```

**Database connection required** - app fails fast if `DATABASE_URL` not in `.env`. No offline mode.

**ML Model Loading:** Happens at startup (lines 28-37). If models missing, falls back to rule-based only (`USE_ML = False`).

**Testing:**
```bash
pytest tests/test_flip_score.py    # 13 tests for flip score logic
pytest tests/test_arbitrage.py     # 20+ tests for arbitrage calculations
```

## Key Patterns & Conventions

### 1. Outlier Filtering (Lines 888-939)
**Always filter before statistical analysis:**
```python
# Sales: 100K-50M AED, Rentals: 10K-2M AED/year
filtered_prices, outlier_stats = filter_outliers(prices, search_type)
# Removes ~10-15% of data for accuracy
```

### 2. Error Handling Pattern
```python
try:
    with engine.connect() as conn:
        result = conn.execute(query)
        conn.commit()
except Exception as e:
    logging.error(f"Operation failed: {e}")
    return {'success': False, 'error': str(e)}
```
Always return structured responses with `success` boolean.

### 3. Dynamic Column Mapping
Database schema may vary - use `find_column_name()` with fallback arrays, never hardcode column names in queries.

### 4. Caching Strategy
- **Location premiums:** 24-hour TTL in `property_location_cache`
- **Dataset loading:** Hourly cache key `f"properties_{datetime.now().hour}"`
- **Connection pool:** 2 base + 5 overflow, 30min recycle

### 5. API Response Structure
```python
return jsonify({
    'success': True/False,
    'data': {...},           # Main payload
    'confidence': 0-98,      # Data quality score
    'metadata': {...},       # Comparables count, search scope
    'error': str or None     # Only if success=False
})
```

## AI Integration (Lines 1356-1459)

**OpenAI GPT-4 for market insights:**
```python
if USE_AI_SUMMARY and openai_client:
    summary = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Analyze: {filters}..."}]
    )
```
Fallback gracefully if API fails - never block valuation on AI summary.

## Common Pitfalls

1. **DON'T modify ML model files** - requires full retraining on 73K properties
2. **DON'T use CSV files in production** - they're 110MB and not in git. Use database queries.
3. **DON'T bypass outlier filtering** - causes wildly inaccurate median/mean calculations
4. **DON'T cache location premiums >24 hours** - market conditions change (M4 fix)
5. **DON'T return prices without confidence scores** - users need to assess reliability
6. **DON'T add SQL queries without connection pooling** - use `with engine.connect()`

## Making Changes

**Adding new area coordinates:**
```sql
INSERT INTO area_coordinates (area_name, latitude, longitude, distance_to_metro_km, ...)
VALUES ('New Area', 25.1234, 55.5678, 1.2, ...);
```

**Adding premium projects:**
```sql
INSERT INTO project_premiums (project_name, premium_percentage, tier)
VALUES ('New Luxury Tower', 15.0, 'Super-Premium');
```

**Modifying valuation logic:**
1. Update `calculate_valuation_from_database()` in app.py line 1810
2. Test with known properties (Dubai Marina, Downtown Dubai)
3. Verify confidence scores remain 50-98% range
4. Check that outlier filtering still removes ~10-15%

## Deployment

**Docker (production):**
```bash
docker-compose up -d  # Runs on port 8003 → 8000 internal
```

**Environment variables required:**
```bash
DATABASE_URL=postgresql://user:pass@host:port/db  # SSL required
OPENAI_API_KEY=sk-...
FLASK_SECRET_KEY=...   # Session encryption
```

**Health checks:** All 17 checks in `check_production_ready.sh` must pass before deploy.

## Debugging Tips

**Check database connection:**
```python
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM properties"))
    print(result.fetchone())
```

**Verify ML model loaded:**
```python
print(f"USE_ML: {USE_ML}")  # Should be True
print(f"Features: {len(ml_feature_columns)}")  # Should be 30
```

**Test location premium:**
```python
premium = calculate_location_premium('Dubai Marina')
# Should return ~45% (metro 0.5km, beach 0.2km, mall 0.3km)
```

**Query rental yield data:**
```sql
SELECT COUNT(*), AVG(annual_amount) FROM rentals 
WHERE area_en ILIKE '%Business Bay%' AND prop_type_en = 'Unit';
```

## Common Production Errors & Solutions

### 1. Database Connection Failures

**Error:** `OperationalError: could not connect to server` or `connection timeout`

**Root Causes:**
- SSL mode misconfiguration
- Connection pool exhausted
- Neon serverless database idle timeout

**Solutions:**
```python
# Check connection settings (app.py lines 60-90)
connect_args={
    'sslmode': 'require',         # MUST be 'require' for Neon
    'connect_timeout': 10,
    'keepalives': 1,              # Enable TCP keepalive
    'keepalives_idle': 30,
    'keepalives_interval': 10,
    'keepalives_count': 5
}

# Test connection immediately:
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("✅ Database connection test successful")
```

**Quick Fix:**
```bash
# Check if DATABASE_URL is set
echo $DATABASE_URL

# Test connection manually
python -c "from app import engine; from sqlalchemy import text; \
           conn = engine.connect(); \
           print(conn.execute(text('SELECT 1')).fetchone())"
```

### 2. ML Model Loading Failures

**Error:** `FileNotFoundError: models/xgboost_model_v1.pkl not found`

**Root Cause:** Model files missing from deployment (not in git due to size)

**Solution:**
```bash
# Check if models exist
ls -lh models/
# Should show:
# xgboost_model_v1.pkl (4.9MB)
# label_encoders_v1.pkl (200KB)
# feature_columns_v1.pkl (615 bytes)

# If missing, app gracefully falls back:
# USE_ML = False (rule-based pricing only)
```

**Production Behavior:**
- App continues to work without ML (database-only valuations)
- No crash, just lower accuracy (~85% vs 89.7%)
- Check logs for: `⚠️ ML model not loaded: [error]. Using rule-based pricing only.`

### 3. Empty Valuation Results

**Error:** `No comparable properties found for [property] in [area]`

**Root Causes:**
- Area name typo or case mismatch
- Property type not in database
- Size too extreme (outside 20-2,000 sqm range)

**Solutions:**
```python
# 1. Check area name spelling (case-insensitive but exact match)
SELECT DISTINCT area_en FROM properties ORDER BY area_en LIMIT 50;

# 2. Verify property type exists
SELECT DISTINCT prop_type_en, COUNT(*) FROM properties 
GROUP BY prop_type_en ORDER BY COUNT(*) DESC;

# 3. Check size distribution
SELECT MIN(actual_area), MAX(actual_area), AVG(actual_area) 
FROM properties WHERE area_en ILIKE '%[area_name]%';
```

**Fallback Logic (valuation_engine.py lines 130-170):**
1. Try area + type + size (±30%)
2. Expand to area + type (any size)
3. Expand to area-wide (all types)
4. Last resort: city-wide same type

### 4. Location Premium Not Showing

**Error:** Location premium returns 0% when area should have premium

**Root Cause:** Area not in `area_coordinates` table (only 70/200+ areas covered)

**Check:**
```sql
-- List areas with geospatial data
SELECT area_name, distance_to_metro_km, distance_to_beach_km 
FROM area_coordinates 
WHERE LOWER(area_name) = LOWER('Dubai Marina');

-- If no results, area has no premium data
```

**Solution:**
```sql
-- Add missing area (requires GPS coordinates and distances)
INSERT INTO area_coordinates 
(area_name, latitude, longitude, distance_to_metro_km, distance_to_beach_km, 
 distance_to_mall_km, distance_to_school_km, distance_to_business_km, neighborhood_score)
VALUES 
('New Area', 25.1234, 55.5678, 2.5, 5.0, 1.5, 3.0, 4.0, 3.8);
```

**Temporary Workaround:** Valuation works without location premium, just less accurate.

### 5. Rental Yield Shows 0%

**Error:** `rental_yield: 0.0` or `No rental data available`

**Root Causes:**
- No rental listings for that area + property type combination
- `annual_amount` column NULL in rentals table
- Property type mismatch (e.g., searching 'Apartment' but data has 'Unit')

**Debug:**
```sql
-- Check if rental data exists for area
SELECT COUNT(*), AVG(annual_amount), prop_type_en 
FROM rentals 
WHERE area_en ILIKE '%Business Bay%' 
GROUP BY prop_type_en;

-- Check for NULL values
SELECT COUNT(*) as total, 
       COUNT(annual_amount) as with_rent,
       COUNT(*) - COUNT(annual_amount) as missing_rent
FROM rentals WHERE area_en ILIKE '%Business Bay%';
```

**Column Mapping Issue (app.py lines 143-147):**
```python
# Rentals table uses multiple potential column names
RENTALS_MAP = {
    'price': find_column_name(RENTALS_COLUMNS, 
             ['annual_amount', 'annual_rent', 'rent_amount', 'amount', 'price', 'rent']),
    # ... if find_column_name fails, may return None
}
```

### 6. Flip Score Calculation Timeout

**Error:** Request takes >10 seconds or times out

**Root Cause:** Queries both `properties` AND `rentals` tables without limits

**Performance Check:**
```sql
-- Check query execution time
EXPLAIN ANALYZE
SELECT AVG(trans_value) FROM properties 
WHERE area_en ILIKE '%Downtown%' 
  AND prop_type_en = 'Unit'
  AND instance_date > NOW() - INTERVAL '6 months';
```

**Optimization (app.py lines 3287-3360):**
```python
# Add LIMIT to prevent full table scans
query = text("""
    SELECT trans_value, instance_date 
    FROM properties 
    WHERE area_en ILIKE :area 
      AND prop_type_en = :type
    ORDER BY instance_date DESC
    LIMIT 500  -- ⚠️ CRITICAL: Always limit large queries
""")
```

### 7. Cache Stale Data (M4 Fix Applied)

**Error:** Location premiums don't reflect recent changes

**Root Cause:** Cache TTL was infinite before M4 fix (Oct 2025)

**Verify Fix Applied:**
```python
# Check app.py line 273 - should have 24-hour TTL:
query = text("""
    SELECT * FROM property_location_cache
    WHERE ... 
      AND created_at > NOW() - INTERVAL '24 hours'  -- ✅ M4 fix
""")
```

**Force Cache Refresh:**
```sql
-- Clear all cache
DELETE FROM property_location_cache;

-- Clear specific area
DELETE FROM property_location_cache 
WHERE LOWER(area_name) = LOWER('Dubai Marina');
```

### 8. Outlier Filtering Too Aggressive

**Error:** Valid properties filtered out (e.g., luxury villas >50M AED)

**Check Thresholds (app.py lines 888-939):**
```python
# Sales market limits:
MIN_PRICE = 100_000        # Minimum: 100K AED
MAX_PRICE = 50_000_000     # Maximum: 50M AED (residential)
EXTREME_MAX = 100_000_000  # Absolute cap: 100M AED

# For ultra-luxury (>50M), may need custom handling
```

**Solution for Edge Cases:**
```python
# Add special handling for ultra-luxury segment
if property_value > 50_000_000:
    # Skip outlier filtering for ultra-luxury
    filtered_prices = prices[prices < 200_000_000]  # Higher cap
```

### 9. OpenAI API Failures

**Error:** `openai.error.RateLimitError` or `API key invalid`

**Graceful Degradation (app.py lines 1356-1459):**
```python
if USE_AI_SUMMARY and openai_client:
    try:
        summary = openai_client.chat.completions.create(...)
    except Exception as e:
        logging.warning(f"AI summary failed: {e}")
        summary = None  # ✅ Continue without AI insights

# App never crashes on AI failure - just skips summary
```

**Check API Key:**
```bash
# Verify environment variable
echo $OPENAI_API_KEY | cut -c1-7  # Should show: sk-proj

# Test API directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 10. Authentication Loop (Redirect Issue)

**Error:** User stuck in login → redirect → login loop

**Root Cause:** `FLASK_SECRET_KEY` not set or changed between restarts

**Fix:**
```bash
# Generate stable secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Add to .env (MUST persist across restarts)
FLASK_SECRET_KEY=your_generated_key_here

# Restart app
docker-compose restart
```

**Session Cookie Check:**
```python
# Verify session configuration (app.py line 153)
app.secret_key = os.getenv("SECRET_KEY", "retyn-avm-secure-key-2025")

# Should use env variable in production, NOT default
```

### Emergency Recovery Commands

**Database Connection Lost:**
```bash
# Restart connection pool
docker-compose restart web

# Check database status
docker-compose logs -f web | grep -i "database\|connection"
```

**Memory Issues:**
```bash
# Check memory usage
docker stats retyn-avm

# Restart with fresh state
docker-compose down && docker-compose up -d
```

**Full Reset (Development Only):**
```bash
# ⚠️ WARNING: Clears all cache and connections
docker-compose down
docker volume prune -f
docker-compose up -d
```

### Log Monitoring

**Check for common error patterns:**
```bash
# Database connection errors
docker-compose logs web | grep -i "operational\|timeout\|ssl"

# ML model errors
docker-compose logs web | grep -i "model\|xgboost\|joblib"

# API errors
docker-compose logs web | grep -i "error\|exception\|failed"

# Performance issues
docker-compose logs web | grep -i "slow\|timeout\|retry"
```

**Healthy Log Output Should Show:**
```
✅ ML model loaded successfully
✅ OpenAI API key configured successfully
✅ Database connection test successful
✅ Database engine created successfully
```

---

**Version:** 2.0 (Oct 2025)  
**Last Updated:** Based on production analysis of 4,257 lines core code  
**Maintainer:** See AUTHORIZED_USERS in app.py line 159
