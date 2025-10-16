-- =====================================================
-- ESG Score Column Migration
-- Created: October 16, 2025
-- Purpose: Add ESG (Environmental, Social, Governance) 
--          sustainability score to properties table
-- =====================================================

-- Add ESG score column (0-100 scale)
ALTER TABLE properties 
ADD COLUMN IF NOT EXISTS esg_score INTEGER DEFAULT NULL 
CHECK (esg_score >= 0 AND esg_score <= 100);

-- Add column comment for documentation
COMMENT ON COLUMN properties.esg_score IS 
'ESG sustainability score (0-100). Environmental, Social & Governance rating. Higher scores indicate better sustainability practices.';

-- Create index for query performance
CREATE INDEX IF NOT EXISTS idx_esg_score 
ON properties(esg_score) 
WHERE esg_score IS NOT NULL;

-- =====================================================
-- Sample ESG Data (10 properties for MVP)
-- =====================================================

-- Low ESG Projects (25-30)
UPDATE properties 
SET esg_score = 30 
WHERE project_en ILIKE '%AZIZI VENICE 11%' 
  AND esg_score IS NULL;

UPDATE properties 
SET esg_score = 25 
WHERE project_en ILIKE '%Samana Lake Views%' 
  AND esg_score IS NULL;

UPDATE properties 
SET esg_score = 25 
WHERE project_en ILIKE '%CAPRIA EAST%' 
  AND esg_score IS NULL;

-- High ESG Projects (60-65) - Ocean Pearl series
UPDATE properties 
SET esg_score = 60 
WHERE project_en ILIKE '%Ocean Pearl By SD%' 
  AND prop_type_en = '2 B/R'
  AND esg_score IS NULL;

UPDATE properties 
SET esg_score = 65 
WHERE project_en ILIKE '%Ocean Pearl%' 
  AND prop_type_en = '1 B/R'
  AND esg_score IS NULL;

-- Additional sample projects (moderate range)
UPDATE properties 
SET esg_score = 45 
WHERE project_en ILIKE '%Downtown Views%' 
  AND esg_score IS NULL;

UPDATE properties 
SET esg_score = 55 
WHERE project_en ILIKE '%Marina%' 
  AND area_en ILIKE '%Dubai Marina%'
  AND esg_score IS NULL;

-- =====================================================
-- Verification Queries
-- =====================================================

-- Check total properties with ESG scores
SELECT 
    COUNT(*) as total_with_esg,
    MIN(esg_score) as min_score,
    MAX(esg_score) as max_score,
    AVG(esg_score)::NUMERIC(10,2) as avg_score
FROM properties 
WHERE esg_score IS NOT NULL;

-- Check ESG distribution by area
SELECT 
    area_en,
    COUNT(*) as property_count,
    AVG(esg_score)::NUMERIC(10,2) as avg_esg
FROM properties 
WHERE esg_score IS NOT NULL
GROUP BY area_en
ORDER BY avg_esg DESC
LIMIT 10;

-- Verify index created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'properties' 
  AND indexname = 'idx_esg_score';
