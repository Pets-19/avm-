-- ================================================================
-- GEOSPATIAL ENHANCEMENT - DATABASE SETUP
-- Phase 1: Quick Win Implementation
-- Date: October 6, 2025
-- ================================================================

-- Step 1: Create area_coordinates table
-- Stores GPS coordinates and pre-calculated distances for each area
CREATE TABLE IF NOT EXISTS area_coordinates (
    id SERIAL PRIMARY KEY,
    area_name VARCHAR(255) UNIQUE NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    distance_to_metro_km DECIMAL(5, 2),
    distance_to_beach_km DECIMAL(5, 2),
    distance_to_mall_km DECIMAL(5, 2),
    distance_to_school_km DECIMAL(5, 2),
    distance_to_business_km DECIMAL(5, 2),
    neighborhood_score DECIMAL(3, 2) DEFAULT 3.5,
    geocoded_at TIMESTAMP DEFAULT NOW(),
    data_source VARCHAR(50) DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_area_name ON area_coordinates(area_name);
CREATE INDEX idx_geocoded_at ON area_coordinates(geocoded_at);

-- Step 2: Insert top 10 Dubai areas with coordinates and distances
-- These are manually researched coordinates and distances
INSERT INTO area_coordinates 
(area_name, latitude, longitude, distance_to_metro_km, distance_to_beach_km, distance_to_mall_km, neighborhood_score) 
VALUES
-- Premium Waterfront Areas
('Dubai Marina', 25.0805, 55.1409, 0.5, 0.2, 0.3, 4.5),
('Palm Jumeirah', 25.1124, 55.1390, 2.5, 0.05, 1.8, 4.7),

-- Downtown & Business Districts
('Downtown Dubai', 25.1972, 55.2744, 0.1, 3.5, 0.2, 4.8),
('Business Bay', 25.1881, 55.2629, 0.05, 2.8, 0.8, 4.3),
('Jumeirah Lake Towers', 25.0695, 55.1419, 0.02, 1.5, 0.5, 4.2),

-- Family Communities
('Arabian Ranches', 25.0518, 55.2681, 8.5, 15.0, 3.5, 4.0),
('Dubai Sports City', 25.0421, 55.2203, 7.2, 12.0, 4.2, 3.8),
('Jumeirah Village Circle', 25.0581, 55.2090, 5.5, 10.0, 2.8, 3.9),

-- Established Areas
('Al Barsha', 25.1142, 55.1964, 0.3, 8.5, 0.2, 4.0),
('International City', 25.1701, 55.4140, 3.5, 18.0, 2.5, 3.2)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_at = NOW();

-- Step 3: Create property_location_cache table
-- Stores calculated location premiums per property combination (area + type + bedrooms)
CREATE TABLE IF NOT EXISTS property_location_cache (
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

-- Step 4: Create amenities reference table
-- Stores locations of key amenities (metro, beach, mall, etc.)
CREATE TABLE IF NOT EXISTS amenities (
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

-- Step 5: Insert metro stations (Dubai Metro Red & Green Lines)
INSERT INTO amenities (name, type, latitude, longitude, importance_score) VALUES
-- Red Line (Major Stations)
('Dubai Marina Metro', 'metro', 25.0850, 55.1450, 9),
('Burj Khalifa/Dubai Mall Metro', 'metro', 25.1972, 55.2789, 10),
('Business Bay Metro', 'metro', 25.1881, 55.2629, 9),
('Mall of Emirates Metro', 'metro', 25.1176, 55.2003, 8),
('Jumeirah Lakes Towers Metro', 'metro', 25.0695, 55.1419, 8),
('DMCC Metro', 'metro', 25.0732, 55.1447, 7),
('Ibn Battuta Mall Metro', 'metro', 25.0438, 55.1172, 7),
('Financial Centre Metro', 'metro', 25.2203, 55.2803, 9),
('Emirates Towers Metro', 'metro', 25.2175, 55.2822, 9),
('Nakheel Metro', 'metro', 25.0708, 55.1345, 7)
ON CONFLICT DO NOTHING;

-- Step 6: Insert beach/waterfront locations
INSERT INTO amenities (name, type, latitude, longitude, importance_score) VALUES
('JBR Beach', 'beach', 25.0781, 55.1372, 10),
('Jumeirah Beach', 'beach', 25.2138, 55.2566, 9),
('Kite Beach', 'beach', 25.1904, 55.2516, 9),
('La Mer Beach', 'beach', 25.2283, 55.2956, 8),
('Sunset Beach', 'beach', 25.0967, 55.1395, 7),
('Dubai Marina Walk', 'beach', 25.0766, 55.1395, 8)
ON CONFLICT DO NOTHING;

-- Step 7: Insert major shopping malls
INSERT INTO amenities (name, type, latitude, longitude, importance_score) VALUES
('Dubai Mall', 'mall', 25.1975, 55.2796, 10),
('Mall of the Emirates', 'mall', 25.1176, 55.2003, 9),
('Dubai Marina Mall', 'mall', 25.0766, 55.1395, 8),
('Ibn Battuta Mall', 'mall', 25.0438, 55.1172, 8),
('City Centre Deira', 'mall', 25.2525, 55.3331, 7),
('City Centre Mirdif', 'mall', 25.2183, 55.4106, 7),
('BurJuman', 'mall', 25.2531, 55.3034, 7)
ON CONFLICT DO NOTHING;

-- Step 8: Insert business districts
INSERT INTO amenities (name, type, latitude, longitude, importance_score) VALUES
('DIFC (Dubai International Financial Centre)', 'business', 25.2145, 55.2813, 10),
('Business Bay', 'business', 25.1881, 55.2629, 9),
('Dubai Internet City', 'business', 25.0975, 55.1637, 8),
('Dubai Media City', 'business', 25.1007, 55.1632, 8),
('Jumeirah Lake Towers', 'business', 25.0695, 55.1419, 8),
('Dubai Silicon Oasis', 'business', 25.1214, 55.3822, 7)
ON CONFLICT DO NOTHING;

-- Step 9: Verification queries
-- Run these to verify setup

-- Check area_coordinates
SELECT 
    COUNT(*) as total_areas,
    COUNT(DISTINCT area_name) as unique_areas,
    AVG(distance_to_metro_km) as avg_metro_distance,
    AVG(distance_to_beach_km) as avg_beach_distance
FROM area_coordinates;

-- Check amenities
SELECT 
    type,
    COUNT(*) as count,
    AVG(importance_score) as avg_importance
FROM amenities
WHERE active = TRUE
GROUP BY type
ORDER BY avg_importance DESC;

-- Sample location premium calculation (for testing)
SELECT 
    area_name,
    ROUND(
        GREATEST(0, 15 - (COALESCE(distance_to_metro_km, 10) * 3)) +
        GREATEST(0, 30 - (COALESCE(distance_to_beach_km, 10) * 6)) +
        GREATEST(0, 8 - (COALESCE(distance_to_mall_km, 10) * 2)),
        2
    ) as estimated_premium_pct
FROM area_coordinates
ORDER BY estimated_premium_pct DESC
LIMIT 10;

-- ================================================================
-- SETUP COMPLETE
-- Next: Run this SQL file, then implement Python functions in app.py
-- ================================================================
