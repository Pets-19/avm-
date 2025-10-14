# 🚀 GEOSPATIAL IMPLEMENTATION PROMPTS - DETAILED GUIDE

## ⚡ **QUICK WIN PROMPT - USE THIS TODAY (4 hours)**

```markdown
CONTEXT:
I have a Flask-based AVM with PostgreSQL. 
Tables: 'properties' (153k rows), 'rentals' (620k rows)
Current accuracy: ±15-20% variance
Goal: Add basic geospatial location adjustments → ±10-12% variance

TASK: Minimal geospatial enhancement (4-hour implementation)

=== PHASE 1: DATABASE SETUP (30 minutes) ===

CREATE TABLE area_coordinates (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(255) UNIQUE NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    distance_to_metro_km DECIMAL(5, 2),
    distance_to_beach_km DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_area_name ON area_coordinates(area_name);

INSERT INTO area_coordinates (area_name, latitude, longitude, distance_to_metro_km, distance_to_beach_km) VALUES
('Dubai Marina', 25.0805, 55.1409, 0.5, 0.2),
('Downtown Dubai', 25.1972, 55.2744, 0.1, 3.5),
('Business Bay', 25.1881, 55.2629, 0.05, 2.8),
('Jumeirah Lake Towers', 25.0695, 55.1419, 0.02, 1.5),
('Palm Jumeirah', 25.1124, 55.1390, 2.5, 0.05),
('Arabian Ranches', 25.0518, 55.2681, 8.5, 15.0),
('Dubai Sports City', 25.0421, 55.2203, 7.2, 12.0),
('Jumeirah Village Circle', 25.0581, 55.2090, 5.5, 10.0),
('Al Barsha', 25.1142, 55.1964, 0.3, 8.5),
('International City', 25.1701, 55.4140, 3.5, 18.0);

=== PHASE 2: ADD HAVERSINE FUNCTION (15 minutes) ===

Add to app.py (after imports, before routes):

```python
from math import radians, sin, cos, sqrt, atan2

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS points in kilometers.
    
    Args:
        lat1, lon1: First point coordinates (decimal degrees)
        lat2, lon2: Second point coordinates (decimal degrees)
    
    Returns:
        float: Distance in kilometers
    
    Example:
        >>> calculate_haversine_distance(25.0805, 55.1409, 25.0850, 55.1450)
        0.52  # ~520 meters
    """
    # Handle None/NULL values
    if None in [lat1, lon1, lat2, lon2]:
        return None
    
    R = 6371  # Earth's radius in kilometers
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return round(R * c, 2)
```

=== PHASE 3: ADD LOCATION PREMIUM FUNCTION (1 hour) ===

Add to app.py:

```python
def get_location_premium(area_name):
    """
    Calculate location premium percentage based on proximity to amenities.
    
    Premium Formula:
    - Metro proximity: +12% if within 500m, scales down to 0% at 5km
    - Beach proximity: +25% if within 200m, scales down to 0% at 5km
    - Combined cap: Maximum +35% total premium
    
    Args:
        area_name: Area name to lookup (case-insensitive)
    
    Returns:
        dict: {
            'total_premium': float (percentage),
            'metro_premium': float,
            'beach_premium': float,
            'area_found': bool
        }
    """
    if not engine:
        return {'total_premium': 0, 'metro_premium': 0, 'beach_premium': 0, 'area_found': False}
    
    try:
        # Normalize area name (lowercase, trim)
        normalized_area = area_name.strip().lower()
        
        # Query area coordinates
        query = text("""
            SELECT distance_to_metro_km, distance_to_beach_km 
            FROM area_coordinates 
            WHERE LOWER(area_name) = :area_name
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'area_name': normalized_area}).fetchone()
        
        if not result:
            # Area not found - return 0% premium (graceful degradation)
            print(f"⚠️ Area '{area_name}' not found in coordinates database")
            return {'total_premium': 0, 'metro_premium': 0, 'beach_premium': 0, 'area_found': False}
        
        metro_dist, beach_dist = result[0], result[1]
        
        # Calculate metro premium (linear decay from 12% to 0%)
        if metro_dist is not None and metro_dist <= 5.0:
            metro_premium = max(0, 12 * (1 - metro_dist / 5.0))
        else:
            metro_premium = 0
        
        # Calculate beach premium (linear decay from 25% to 0%)
        if beach_dist is not None and beach_dist <= 5.0:
            beach_premium = max(0, 25 * (1 - beach_dist / 5.0))
        else:
            beach_premium = 0
        
        # Combine premiums with cap
        total_premium = min(35, metro_premium + beach_premium)
        
        return {
            'total_premium': round(total_premium, 2),
            'metro_premium': round(metro_premium, 2),
            'beach_premium': round(beach_premium, 2),
            'area_found': True
        }
    
    except Exception as e:
        print(f"❌ Error calculating location premium for '{area_name}': {e}")
        return {'total_premium': 0, 'metro_premium': 0, 'beach_premium': 0, 'area_found': False}
```

=== PHASE 4: INTEGRATE INTO VALUATION ENDPOINT (1 hour) ===

Find the valuation endpoint (around line 900 in app.py):

```python
@app.route('/api/property/valuation', methods=['POST'])
@login_required
def property_valuation():
    # ... existing code to get parameters ...
    
    area = data.get('area', '').strip()
    property_type = data.get('propertyType')
    size = float(data.get('size', 0))
    bedrooms = data.get('bedrooms', '')
    status = data.get('status', '')
    
    # ... existing valuation calculation ...
    base_valuation = calculate_avm(...)  # Your existing AVM logic
    
    # 🆕 NEW: Get location premium
    location_data = get_location_premium(area)
    location_premium_pct = location_data['total_premium']
    
    # Apply location adjustment to base valuation
    if location_premium_pct > 0:
        adjusted_valuation = base_valuation * (1 + location_premium_pct / 100)
        print(f"📍 Location premium for {area}: +{location_premium_pct}% (AED {adjusted_valuation - base_valuation:,.0f})")
    else:
        adjusted_valuation = base_valuation
    
    # Return enhanced response
    return jsonify({
        'valuation': round(adjusted_valuation, 2),
        'base_valuation': round(base_valuation, 2),
        'location_premium_pct': location_premium_pct,
        'location_breakdown': {
            'metro_premium': location_data['metro_premium'],
            'beach_premium': location_data['beach_premium'],
            'area_found': location_data['area_found']
        },
        # ... rest of your existing response ...
    })
```

=== PHASE 5: ADD UNIT TESTS (1.5 hours) ===

Create tests/test_geospatial.py:

```python
import pytest
from app import calculate_haversine_distance, get_location_premium

class TestHaversineDistance:
    def test_known_distance(self):
        """Test with known distance: Dubai Marina to JLT Metro (~1.2km)"""
        dist = calculate_haversine_distance(25.0805, 55.1409, 25.0695, 55.1419)
        assert 1.0 < dist < 1.4, f"Expected ~1.2km, got {dist}km"
    
    def test_same_point(self):
        """Distance from point to itself should be 0"""
        dist = calculate_haversine_distance(25.0805, 55.1409, 25.0805, 55.1409)
        assert dist == 0
    
    def test_null_handling(self):
        """Should handle None values gracefully"""
        dist = calculate_haversine_distance(None, 55.1409, 25.0805, 55.1409)
        assert dist is None

class TestLocationPremium:
    def test_dubai_marina_premium(self):
        """Dubai Marina: Near metro + near beach → High premium"""
        result = get_location_premium("Dubai Marina")
        assert result['area_found'] is True
        assert result['total_premium'] > 20, "Expected >20% for Dubai Marina"
        assert result['metro_premium'] > 0
        assert result['beach_premium'] > 0
    
    def test_arabian_ranches_premium(self):
        """Arabian Ranches: Far from metro + beach → Low premium"""
        result = get_location_premium("Arabian Ranches")
        assert result['area_found'] is True
        assert result['total_premium'] < 5, "Expected <5% for Arabian Ranches"
    
    def test_unknown_area(self):
        """Unknown area should return 0% premium (graceful degradation)"""
        result = get_location_premium("Nonexistent Area")
        assert result['area_found'] is False
        assert result['total_premium'] == 0
    
    def test_case_insensitive(self):
        """Area lookup should be case-insensitive"""
        result1 = get_location_premium("Dubai Marina")
        result2 = get_location_premium("dubai marina")
        result3 = get_location_premium("DUBAI MARINA")
        assert result1['total_premium'] == result2['total_premium'] == result3['total_premium']
    
    def test_premium_cap(self):
        """Total premium should not exceed 35%"""
        result = get_location_premium("Palm Jumeirah")
        assert result['total_premium'] <= 35

class TestValuationIntegration:
    def test_valuation_with_location_premium(self):
        """End-to-end test: Valuation should include location adjustment"""
        # Test with Dubai Marina (high premium area)
        response = client.post('/api/property/valuation', json={
            'area': 'Dubai Marina',
            'propertyType': 'Unit',
            'size': 100,
            'bedrooms': '2'
        })
        
        data = response.get_json()
        assert 'location_premium_pct' in data
        assert data['location_premium_pct'] > 0
        assert data['valuation'] > data['base_valuation']
    
    def test_valuation_without_location_data(self):
        """Valuation should still work if area not geocoded"""
        response = client.post('/api/property/valuation', json={
            'area': 'Unknown Area',
            'propertyType': 'Unit',
            'size': 100,
            'bedrooms': '2'
        })
        
        data = response.get_json()
        assert 'location_premium_pct' in data
        assert data['location_premium_pct'] == 0
        assert data['valuation'] == data['base_valuation']
```

Run tests:
```bash
pytest tests/test_geospatial.py -v
```

=== VERIFICATION CHECKLIST ===

✅ Database table created and populated (10 areas)
✅ Haversine function added and tested
✅ Location premium function added
✅ Valuation endpoint modified
✅ Unit tests passing
✅ No breaking changes to existing functionality
✅ Graceful degradation (0% premium if area not found)

=== EXPECTED RESULTS ===

Before:
- Dubai Marina 100 sqm, 2BR → AED 2,500,000
- Arabian Ranches 100 sqm, 2BR → AED 1,200,000

After:
- Dubai Marina 100 sqm, 2BR → AED 2,750,000 (+10-15% location premium)
- Arabian Ranches 100 sqm, 2BR → AED 1,200,000 (no change, far from amenities)

=== PERFORMANCE IMPACT ===

- Database lookup: ~2ms per valuation
- Haversine calculation: <0.1ms
- Total overhead: ~2-3ms per request
- Negligible impact on user experience

=== SAFETY RATIONALE ===

1. **Backward Compatible:** If area not found, premium = 0% (existing behavior)
2. **Database Isolation:** New table, no modifications to existing schema
3. **Error Handling:** All functions have try/except with graceful fallbacks
4. **Tested:** 10+ unit tests covering edge cases
5. **Capped Premiums:** Max 35% prevents unrealistic adjustments

=== LINES TO SCRUTINIZE ===

1. Line XX: `normalized_area = area_name.strip().lower()` - Ensure no SQL injection
2. Line YY: `total_premium = min(35, metro_premium + beach_premium)` - Verify cap logic
3. Line ZZ: `adjusted_valuation = base_valuation * (1 + location_premium_pct / 100)` - Check math

=== NEXT STEPS (FUTURE) ===

- [ ] Add 190 more areas (total 200 areas in Dubai)
- [ ] Add distance to malls
- [ ] Add neighborhood quality scores
- [ ] Implement caching for performance
- [ ] Add map visualization to frontend

IMPLEMENTATION TIME: 4 hours
EXPECTED ACCURACY IMPROVEMENT: 10-15%
COST: $0 (manual coordinates)
RISK LEVEL: LOW
```

---

## 📋 **APPROACH #2 DETAILED PROMPT (1 Week Implementation)**

```markdown
CONTEXT:
Building on Quick Win success. Now implementing production-grade geospatial system with caching.
Current: Basic area-level geocoding for 10 areas
Goal: Scale to all 200+ areas with intelligent caching

=== WEEK OVERVIEW ===

Day 1-2: Database schema + batch geocoding setup
Day 3-4: Cache implementation + location premium logic
Day 5: Testing + optimization

=== DAY 1-2: DATABASE & BATCH GEOCODING ===

**Step 1: Extend Database Schema**

```sql
-- Extend area_coordinates table
ALTER TABLE area_coordinates ADD COLUMN IF NOT EXISTS:
    distance_to_mall_km DECIMAL(5, 2),
    distance_to_school_km DECIMAL(5, 2),
    distance_to_business_km DECIMAL(5, 2),
    neighborhood_score DECIMAL(3, 2) DEFAULT 3.5,
    geocoded_at TIMESTAMP,
    data_source VARCHAR(50) DEFAULT 'manual';

-- Create property_location_cache table
CREATE TABLE property_location_cache (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(255) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    bedrooms VARCHAR(20),
    location_premium_pct DECIMAL(5, 2) NOT NULL,
    metro_premium DECIMAL(5, 2),
    beach_premium DECIMAL(5, 2),
    mall_premium DECIMAL(5, 2),
    school_premium DECIMAL(5, 2),
    business_premium DECIMAL(5, 2),
    neighborhood_premium DECIMAL(5, 2),
    cache_hits INT DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(area_name, property_type, bedrooms)
);

CREATE INDEX idx_cache_lookup ON property_location_cache(area_name, property_type, bedrooms);
CREATE INDEX idx_last_accessed ON property_location_cache(last_accessed);
CREATE INDEX idx_cache_hits ON property_location_cache(cache_hits DESC);

-- Create amenities table
CREATE TABLE amenities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('metro', 'beach', 'mall', 'school', 'hospital', 'business')),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    importance_score INT DEFAULT 5 CHECK (importance_score BETWEEN 1 AND 10),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_amenity_type ON amenities(type, active);
CREATE INDEX idx_amenity_coords ON amenities(latitude, longitude);

-- Insert metro stations
INSERT INTO amenities (name, type, latitude, longitude, importance_score) VALUES
('Dubai Marina Metro', 'metro', 25.0850, 55.1450, 9),
('Burj Khalifa/Dubai Mall Metro', 'metro', 25.1972, 55.2789, 10),
('Business Bay Metro', 'metro', 25.1881, 55.2629, 9),
('Mall of Emirates Metro', 'metro', 25.1176, 55.2003, 8),
('JLT Metro', 'metro', 25.0695, 55.1419, 8),
('DMCC Metro', 'metro', 25.0732, 55.1447, 7),
('Ibn Battuta Mall Metro', 'metro', 25.0438, 55.1172, 7),
('Nakheel Metro', 'metro', 25.0708, 55.1345, 7),
('Financial Centre Metro', 'metro', 25.2203, 55.2803, 9),
('Emirates Towers Metro', 'metro', 25.2175, 55.2822, 9);

-- Insert beach points
INSERT INTO amenities (name, type, latitude, longitude, importance_score) VALUES
('JBR Beach', 'beach', 25.0781, 55.1372, 10),
('Jumeirah Beach', 'beach', 25.2138, 55.2566, 9),
('Kite Beach', 'beach', 25.1904, 55.2516, 9),
('La Mer Beach', 'beach', 25.2283, 55.2956, 8),
('Sunset Beach', 'beach', 25.0967, 55.1395, 7);

-- Insert major malls
INSERT INTO amenities (name, type, latitude, longitude, importance_score) VALUES
('Dubai Mall', 'mall', 25.1975, 55.2796, 10),
('Mall of the Emirates', 'mall', 25.1176, 55.2003, 9),
('Dubai Marina Mall', 'mall', 25.0766, 55.1395, 8),
('Ibn Battuta Mall', 'mall', 25.0438, 55.1172, 8),
('City Centre Deira', 'mall', 25.2525, 55.3331, 7),
('City Centre Mirdif', 'mall', 25.2183, 55.4106, 7);

-- Insert business districts
INSERT INTO amenities (name, type, latitude, longitude, importance_score) VALUES
('DIFC', 'business', 25.2145, 55.2813, 10),
('Business Bay', 'business', 25.1881, 55.2629, 9),
('Dubai Internet City', 'business', 25.0975, 55.1637, 8),
('Dubai Media City', 'business', 25.1007, 55.1632, 8),
('JLT Cluster', 'business', 25.0695, 55.1419, 8);
```

**Step 2: Batch Geocoding Script**

Create file: `scripts/batch_geocode_areas.py`

```python
import psycopg2
import requests
import time
from os import getenv

# Database connection
DATABASE_URL = getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

def get_unique_areas():
    """Get all unique area names from properties and rentals"""
    cur.execute("""
        SELECT DISTINCT area_en FROM properties 
        WHERE area_en IS NOT NULL
        UNION
        SELECT DISTINCT area_en FROM rentals
        WHERE area_en IS NOT NULL
        ORDER BY area_en
    """)
    return [row[0] for row in cur.fetchall()]

def is_area_geocoded(area_name):
    """Check if area already has coordinates"""
    cur.execute("""
        SELECT 1 FROM area_coordinates 
        WHERE LOWER(area_name) = LOWER(%s)
    """, (area_name,))
    return cur.fetchone() is not None

def geocode_nominatim(area_name):
    """
    Free geocoding using OpenStreetMap Nominatim.
    Rate limit: 1 request per second.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        'q': f"{area_name}, Dubai, UAE",
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': 'RetynAVM/1.0 (contact@retyn.ai)'}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if data:
            return float(data[0]['lat']), float(data[0]['lon'])
        else:
            print(f"  ⚠️ No results for {area_name}")
            return None, None
    except Exception as e:
        print(f"  ❌ Geocoding failed for {area_name}: {e}")
        return None, None

def calculate_distance_to_nearest(lat, lon, amenity_type):
    """Calculate distance to nearest amenity of given type"""
    cur.execute("""
        SELECT name, latitude, longitude,
               (6371 * acos(
                   cos(radians(%s)) * cos(radians(latitude)) *
                   cos(radians(longitude) - radians(%s)) +
                   sin(radians(%s)) * sin(radians(latitude))
               )) AS distance_km
        FROM amenities
        WHERE type = %s AND active = TRUE
        ORDER BY distance_km
        LIMIT 1
    """, (lat, lon, lon, lat, amenity_type))
    
    result = cur.fetchone()
    return round(result[3], 2) if result else None

def calculate_all_distances(lat, lon):
    """Calculate distances to all amenity types"""
    return {
        'metro': calculate_distance_to_nearest(lat, lon, 'metro'),
        'beach': calculate_distance_to_nearest(lat, lon, 'beach'),
        'mall': calculate_distance_to_nearest(lat, lon, 'mall'),
        'school': calculate_distance_to_nearest(lat, lon, 'school'),
        'business': calculate_distance_to_nearest(lat, lon, 'business')
    }

def insert_area_coordinates(area_name, lat, lon, distances):
    """Insert geocoded area with calculated distances"""
    cur.execute("""
        INSERT INTO area_coordinates 
        (area_name, latitude, longitude, distance_to_metro_km, distance_to_beach_km, 
         distance_to_mall_km, distance_to_school_km, distance_to_business_km, 
         geocoded_at, data_source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'nominatim')
        ON CONFLICT (area_name) DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            distance_to_metro_km = EXCLUDED.distance_to_metro_km,
            distance_to_beach_km = EXCLUDED.distance_to_beach_km,
            distance_to_mall_km = EXCLUDED.distance_to_mall_km,
            distance_to_school_km = EXCLUDED.distance_to_school_km,
            distance_to_business_km = EXCLUDED.distance_to_business_km,
            geocoded_at = NOW()
    """, (
        area_name, lat, lon,
        distances['metro'], distances['beach'], distances['mall'],
        distances['school'], distances['business']
    ))
    conn.commit()

def main():
    """Main batch geocoding process"""
    print("🗺️  Starting batch geocoding...")
    
    areas = get_unique_areas()
    print(f"📊 Found {len(areas)} unique areas")
    
    pending = [a for a in areas if not is_area_geocoded(a)]
    print(f"⏳ {len(pending)} areas need geocoding\n")
    
    for i, area in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] Geocoding: {area}")
        
        lat, lon = geocode_nominatim(area)
        
        if lat and lon:
            print(f"  ✅ Coordinates: {lat}, {lon}")
            
            distances = calculate_all_distances(lat, lon)
            print(f"  📍 Distances: Metro={distances['metro']}km, Beach={distances['beach']}km")
            
            insert_area_coordinates(area, lat, lon, distances)
            print(f"  💾 Saved to database")
        
        # Rate limiting (1 req/sec for Nominatim)
        if i < len(pending):
            time.sleep(1.1)
        print()
    
    print(f"✅ Batch geocoding complete! {len(pending)} areas processed.")
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
```

Run script:
```bash
python scripts/batch_geocode_areas.py
```

=== DAY 3-4: CACHE IMPLEMENTATION ===

**Step 3: Cache Functions**

Add to app.py:

```python
def get_location_cache(area_name, property_type, bedrooms):
    """
    Retrieve cached location adjustments.
    
    Returns:
        dict: {
            'cache_hit': bool,
            'premium': float or None,
            'breakdown': dict or None,
            'age_days': int or None
        }
    """
    if not engine:
        return {'cache_hit': False}
    
    try:
        normalized_area = area_name.strip().lower()
        
        query = text("""
            SELECT 
                location_premium_pct,
                metro_premium,
                beach_premium,
                mall_premium,
                school_premium,
                business_premium,
                neighborhood_premium,
                EXTRACT(DAY FROM NOW() - created_at) as age_days,
                cache_hits
            FROM property_location_cache
            WHERE LOWER(area_name) = :area
              AND property_type = :type
              AND bedrooms = :beds
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {
                'area': normalized_area,
                'type': property_type,
                'beds': bedrooms
            }).fetchone()
        
        if result:
            # Update cache hit counter and last_accessed
            update_query = text("""
                UPDATE property_location_cache
                SET cache_hits = cache_hits + 1,
                    last_accessed = NOW()
                WHERE LOWER(area_name) = :area
                  AND property_type = :type
                  AND bedrooms = :beds
            """)
            with engine.connect() as conn:
                conn.execute(update_query, {
                    'area': normalized_area,
                    'type': property_type,
                    'beds': bedrooms
                })
                conn.commit()
            
            return {
                'cache_hit': True,
                'premium': result[0],
                'breakdown': {
                    'metro': result[1],
                    'beach': result[2],
                    'mall': result[3],
                    'school': result[4],
                    'business': result[5],
                    'neighborhood': result[6]
                },
                'age_days': result[7],
                'hits': result[8] + 1
            }
        
        return {'cache_hit': False}
    
    except Exception as e:
        print(f"❌ Cache lookup error: {e}")
        return {'cache_hit': False}

def calculate_location_premium_advanced(area_name):
    """
    Calculate comprehensive location premium.
    
    Formula:
    - Metro: max(0, 15% - (distance * 3%))
    - Beach: max(0, 30% - (distance * 6%))
    - Mall: max(0, 8% - (distance * 2%))
    - School: max(0, 5% - (distance * 1%))
    - Business: max(0, 10% - (distance * 2%))
    - Neighborhood: (score - 3.0) * 4%
    
    Total capped at -20% min, +50% max
    """
    if not engine:
        return None
    
    try:
        normalized_area = area_name.strip().lower()
        
        query = text("""
            SELECT 
                distance_to_metro_km,
                distance_to_beach_km,
                distance_to_mall_km,
                distance_to_school_km,
                distance_to_business_km,
                neighborhood_score
            FROM area_coordinates
            WHERE LOWER(area_name) = :area
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'area': normalized_area}).fetchone()
        
        if not result:
            return None
        
        metro_dist, beach_dist, mall_dist, school_dist, business_dist, neighborhood = result
        
        # Calculate individual premiums
        metro_premium = max(0, 15 - (metro_dist or 10) * 3) if metro_dist is not None else 0
        beach_premium = max(0, 30 - (beach_dist or 10) * 6) if beach_dist is not None else 0
        mall_premium = max(0, 8 - (mall_dist or 10) * 2) if mall_dist is not None else 0
        school_premium = max(0, 5 - (school_dist or 10) * 1) if school_dist is not None else 0
        business_premium = max(0, 10 - (business_dist or 10) * 2) if business_dist is not None else 0
        neighborhood_premium = ((neighborhood or 3.0) - 3.0) * 4
        
        # Total premium (capped)
        total = metro_premium + beach_premium + mall_premium + school_premium + business_premium + neighborhood_premium
        total_capped = max(-20, min(50, total))
        
        return {
            'total_premium': round(total_capped, 2),
            'metro_premium': round(metro_premium, 2),
            'beach_premium': round(beach_premium, 2),
            'mall_premium': round(mall_premium, 2),
            'school_premium': round(school_premium, 2),
            'business_premium': round(business_premium, 2),
            'neighborhood_premium': round(neighborhood_premium, 2),
            'confidence': 0.85 if metro_dist is not None else 0.60
        }
    
    except Exception as e:
        print(f"❌ Premium calculation error: {e}")
        return None

def update_location_cache(area_name, property_type, bedrooms, premium_data):
    """Store calculated premium in cache"""
    if not engine or not premium_data:
        return False
    
    try:
        normalized_area = area_name.strip().lower()
        
        query = text("""
            INSERT INTO property_location_cache (
                area_name, property_type, bedrooms,
                location_premium_pct, metro_premium, beach_premium,
                mall_premium, school_premium, business_premium, neighborhood_premium
            ) VALUES (
                :area, :type, :beds,
                :total, :metro, :beach, :mall, :school, :business, :neighborhood
            )
            ON CONFLICT (area_name, property_type, bedrooms) DO UPDATE SET
                location_premium_pct = EXCLUDED.location_premium_pct,
                metro_premium = EXCLUDED.metro_premium,
                beach_premium = EXCLUDED.beach_premium,
                mall_premium = EXCLUDED.mall_premium,
                school_premium = EXCLUDED.school_premium,
                business_premium = EXCLUDED.business_premium,
                neighborhood_premium = EXCLUDED.neighborhood_premium,
                last_accessed = NOW()
        """)
        
        with engine.connect() as conn:
            conn.execute(query, {
                'area': normalized_area,
                'type': property_type,
                'beds': bedrooms,
                'total': premium_data['total_premium'],
                'metro': premium_data['metro_premium'],
                'beach': premium_data['beach_premium'],
                'mall': premium_data['mall_premium'],
                'school': premium_data['school_premium'],
                'business': premium_data['business_premium'],
                'neighborhood': premium_data['neighborhood_premium']
            })
            conn.commit()
        
        return True
    
    except Exception as e:
        print(f"❌ Cache update error: {e}")
        return False
```

**Step 4: Integrate into Valuation**

Modify valuation endpoint:

```python
@app.route('/api/property/valuation', methods=['POST'])
@login_required
def property_valuation():
    # ... existing parameter extraction ...
    
    area = data.get('area', '').strip()
    property_type = data.get('propertyType')
    size = float(data.get('size', 0))
    bedrooms = data.get('bedrooms', '')
    
    # ... existing AVM calculation ...
    base_valuation = calculate_avm(...)
    
    # 🆕 NEW: Enhanced location premium with caching
    cache_data = get_location_cache(area, property_type, bedrooms)
    
    if cache_data['cache_hit']:
        location_premium = cache_data['premium']
        location_breakdown = cache_data['breakdown']
        cache_status = 'HIT'
        print(f"⚡ Cache hit for {area}, {property_type}, {bedrooms}")
    else:
        premium_data = calculate_location_premium_advanced(area)
        
        if premium_data:
            location_premium = premium_data['total_premium']
            location_breakdown = {
                'metro': premium_data['metro_premium'],
                'beach': premium_data['beach_premium'],
                'mall': premium_data['mall_premium'],
                'school': premium_data['school_premium'],
                'business': premium_data['business_premium'],
                'neighborhood': premium_data['neighborhood_premium']
            }
            
            # Store in cache
            update_location_cache(area, property_type, bedrooms, premium_data)
            cache_status = 'MISS'
            print(f"💾 Cache miss, calculated and stored for {area}")
        else:
            location_premium = 0
            location_breakdown = {}
            cache_status = 'NOT_FOUND'
    
    # Apply premium
    adjusted_valuation = base_valuation * (1 + location_premium / 100)
    
    return jsonify({
        'valuation': round(adjusted_valuation, 2),
        'base_valuation': round(base_valuation, 2),
        'location_premium_pct': location_premium,
        'location_breakdown': location_breakdown,
        'cache_status': cache_status,
        # ... rest of response ...
    })
```

=== DAY 5: TESTING & OPTIMIZATION ===

**Step 5: Comprehensive Tests**

[INCLUDE 15+ TEST CASES COVERING:]
- Cache hit/miss scenarios
- Premium calculations
- Edge cases (NULL values, unknown areas)
- Performance benchmarks
- Concurrent requests

**Step 6: Monitoring Queries**

```sql
-- Cache hit rate
SELECT 
    COUNT(*) FILTER (WHERE cache_hits > 0) * 100.0 / COUNT(*) as hit_rate_pct,
    AVG(cache_hits) as avg_hits_per_entry
FROM property_location_cache;

-- Most cached combinations
SELECT area_name, property_type, bedrooms, cache_hits
FROM property_location_cache
ORDER BY cache_hits DESC
LIMIT 20;

-- Cache cleanup (delete stale entries)
DELETE FROM property_location_cache
WHERE last_accessed < NOW() - INTERVAL '90 days'
  AND cache_hits < 5;
```

=== SUCCESS CRITERIA ===

✅ 200+ areas geocoded
✅ Cache hit rate >75% after 1 week
✅ Valuation latency <50ms
✅ Accuracy improvement to ±10-12%
✅ 0 breaking changes

IMPLEMENTATION TIME: 1 week
EXPECTED ACCURACY IMPROVEMENT: 15-20%
COST: $0 (free Nominatim API)
RISK LEVEL: MEDIUM
```

---

This comprehensive guide provides:
✅ Step-by-step instructions
✅ Complete code snippets
✅ SQL scripts
✅ Testing strategies
✅ Safety considerations
✅ Performance optimizations

**Which approach would you like to implement first?**
1. ⚡ Quick Win (4 hours, today)
2. 📈 Approach #2 (1 week, production-ready)
3. 🎯 Approach #3 (4 weeks, ML-powered)

Let me know and I'll guide you through the implementation! 🚀
