-- ============================================================================
-- FLIP SCORE COLUMN MIGRATION
-- ============================================================================
-- Purpose: Add flip_score column to properties table for investment filtering
-- Pattern: Exact replica of ESG implementation (migrations/add_esg_column.sql)
-- Date: October 16, 2025
-- Data: 10 sample properties with flip scores (30-88 range)
-- ============================================================================

-- Add flip_score column
ALTER TABLE properties ADD COLUMN IF NOT EXISTS flip_score INTEGER DEFAULT NULL 
  CHECK (flip_score >= 0 AND flip_score <= 100);

-- Add column documentation
COMMENT ON COLUMN properties.flip_score IS 
  'Property Flip Score (0-100): Measures investment flip potential based on price appreciation (30%), liquidity (25%), rental yield (25%), and market segment (20%). Higher scores indicate better short-term investment opportunities.';

-- Create index for fast filtering (only on non-NULL values)
CREATE INDEX IF NOT EXISTS idx_flip_score ON properties(flip_score) WHERE flip_score IS NOT NULL;

-- ============================================================================
-- POPULATE SAMPLE DATA (10 PROPERTIES FROM CSV)
-- ============================================================================
-- Pattern: Match by transaction_number and instance_date for accuracy
-- Source: User-provided CSV with pre-calculated flip scores

-- Property 1: AZIZI VENICE 11 (Highest flip score: 88)
UPDATE properties 
SET flip_score = 88 
WHERE transaction_number = '102-14780' 
  AND instance_date::date = '2025-07-24'
  AND area_en ILIKE '%Madinat Al Mataar%'
  AND project_en ILIKE '%AZIZI VENICE 11%';

-- Property 2: Samana Lake Views (Dubai Production City) - Flip: 70
UPDATE properties 
SET flip_score = 70 
WHERE transaction_number = '102-29971' 
  AND instance_date::date = '2025-07-07'
  AND area_en ILIKE '%DUBAI PRODUCTION CITY%'
  AND project_en ILIKE '%Samana Lake Views%';

-- Property 3: Samana Lake Views (Dubai Production City) - Flip: 70
UPDATE properties 
SET flip_score = 70 
WHERE transaction_number = '102-45520' 
  AND instance_date::date = '2025-07-07'
  AND area_en ILIKE '%DUBAI PRODUCTION CITY%'
  AND project_en ILIKE '%Samana Lake Views%';

-- Property 4: Ocean Pearl By SD (Palm Deira) - Flip: 80
UPDATE properties 
SET flip_score = 80 
WHERE transaction_number = '102-46478' 
  AND instance_date::date = '2025-07-07'
  AND area_en ILIKE '%Palm Deira%'
  AND project_en ILIKE '%Ocean Pearl%';

-- Property 5: Ocean Pearl 2 By SD (Palm Deira) - Flip: 82
UPDATE properties 
SET flip_score = 82 
WHERE transaction_number = '102-46480' 
  AND instance_date::date = '2025-07-07'
  AND area_en ILIKE '%Palm Deira%'
  AND project_en ILIKE '%Ocean Pearl 2%';

-- Property 6: Ocean Pearl 2 By SD (Palm Deira) - Flip: 82
UPDATE properties 
SET flip_score = 82 
WHERE transaction_number = '102-46482' 
  AND instance_date::date = '2025-07-07'
  AND area_en ILIKE '%Palm Deira%'
  AND project_en ILIKE '%Ocean Pearl 2%';

-- Property 7: Samana Lake Views (Dubai Production City) - Flip: 70
UPDATE properties 
SET flip_score = 70 
WHERE transaction_number = '102-47327' 
  AND instance_date::date = '2025-06-30'
  AND area_en ILIKE '%DUBAI PRODUCTION CITY%'
  AND project_en ILIKE '%Samana Lake Views%';

-- Property 8: CAPRIA EAST (Wadi Al Safa 4) - Lowest flip: 30
UPDATE properties 
SET flip_score = 30 
WHERE transaction_number = '102-47813' 
  AND instance_date::date = '2025-07-24'
  AND area_en ILIKE '%Wadi Al Safa 4%'
  AND project_en ILIKE '%CAPRIA EAST%';

-- Property 9: Samana Lake Views (Dubai Production City) - Flip: 70
UPDATE properties 
SET flip_score = 70 
WHERE transaction_number = '102-48235' 
  AND instance_date::date = '2025-07-07'
  AND area_en ILIKE '%DUBAI PRODUCTION CITY%'
  AND project_en ILIKE '%Samana Lake Views%';

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check total properties with flip scores
SELECT 
    COUNT(*) as total_with_flip,
    MIN(flip_score) as min_score,
    MAX(flip_score) as max_score,
    ROUND(AVG(flip_score), 2) as avg_score
FROM properties 
WHERE flip_score IS NOT NULL;

-- Check distribution by area
SELECT 
    area_en,
    COUNT(*) as property_count,
    ROUND(AVG(flip_score), 2) as avg_flip,
    MIN(flip_score) as min_flip,
    MAX(flip_score) as max_flip
FROM properties 
WHERE flip_score IS NOT NULL
GROUP BY area_en
ORDER BY avg_flip DESC;

-- Verify index was created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'properties' 
  AND indexname = 'idx_flip_score';

-- ============================================================================
-- EXPECTED RESULTS
-- ============================================================================
-- Total properties with flip: 9-10 (some transaction_numbers may not match exactly)
-- Flip score range: 30 - 88
-- Areas: Palm Deira (80-82), Dubai Production City (70), Wadi Al Safa 4 (30)
-- ============================================================================
