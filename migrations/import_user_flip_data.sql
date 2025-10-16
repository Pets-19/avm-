-- Import User's 10 Properties with Flip Scores & ESG Scores
-- Date: October 16, 2025
-- Purpose: Update existing properties with flip_score and esg_score from user's CSV

-- ============================================================================
-- IMPORTANT: This script UPDATES existing properties in the database
-- ============================================================================

BEGIN;

-- Property 1: AZIZI VENICE 11 - Madinat Al Mataar (35.27 sqm)
UPDATE properties
SET flip_score = 88, esg_score = 30
WHERE project_en ILIKE '%AZIZI VENICE 11%'
  AND area_en ILIKE '%Madinat Al Mataar%'
  AND actual_area BETWEEN 35.0 AND 35.5
  AND trans_value BETWEEN 635000 AND 645000;

-- Property 2: Samana Lake Views - Dubai Production City (38.7 sqm, 609K)
UPDATE properties
SET flip_score = 70, esg_score = 25
WHERE project_en ILIKE '%Samana Lake Views%'
  AND area_en ILIKE '%DUBAI PRODUCTION%'
  AND actual_area BETWEEN 38.5 AND 39.0
  AND trans_value BETWEEN 605000 AND 615000;

-- Property 3: Samana Lake Views - Dubai Production City (38.7 sqm, 657K)
UPDATE properties
SET flip_score = 70, esg_score = 25
WHERE project_en ILIKE '%Samana Lake Views%'
  AND area_en ILIKE '%DUBAI PRODUCTION%'
  AND actual_area BETWEEN 38.5 AND 39.0
  AND trans_value BETWEEN 655000 AND 660000;

-- Property 4: Ocean Pearl By SD - Palm Deira (149.94 sqm)
UPDATE properties
SET flip_score = 80, esg_score = 60
WHERE project_en ILIKE '%Ocean Pearl%'
  AND area_en ILIKE '%Palm Deira%'
  AND actual_area BETWEEN 149.0 AND 150.5
  AND trans_value BETWEEN 3150000 AND 3160000;

-- Property 5: Ocean Pearl 2 By SD - Palm Deira (81.48 sqm)
UPDATE properties
SET flip_score = 82, esg_score = 65
WHERE project_en ILIKE '%Ocean Pearl 2%'
  AND area_en ILIKE '%Palm Deira%'
  AND actual_area BETWEEN 81.0 AND 82.0
  AND trans_value BETWEEN 2145000 AND 2155000;

-- Property 6: Ocean Pearl 2 By SD - Palm Deira (82.75 sqm)
UPDATE properties
SET flip_score = 82, esg_score = 65
WHERE project_en ILIKE '%Ocean Pearl 2%'
  AND area_en ILIKE '%Palm Deira%'
  AND actual_area BETWEEN 82.5 AND 83.0
  AND trans_value BETWEEN 2075000 AND 2080000;

-- Property 7: Samana Lake Views - Dubai Production City (43.97 sqm)
UPDATE properties
SET flip_score = 70, esg_score = 25
WHERE project_en ILIKE '%Samana Lake Views%'
  AND area_en ILIKE '%DUBAI PRODUCTION%'
  AND actual_area BETWEEN 43.5 AND 44.5
  AND trans_value BETWEEN 730000 AND 740000;

-- Property 8: CAPRIA EAST - Wadi Al Safa 4 (156.39 sqm)
UPDATE properties
SET flip_score = 30, esg_score = 25
WHERE project_en ILIKE '%CAPRIA EAST%'
  AND area_en ILIKE '%Wadi Al Safa 4%'
  AND actual_area BETWEEN 156.0 AND 157.0
  AND trans_value BETWEEN 3230000 AND 3240000;

-- Property 9: Samana Lake Views - Dubai Production City (77.21 sqm)
UPDATE properties
SET flip_score = 70, esg_score = 25
WHERE project_en ILIKE '%Samana Lake Views%'
  AND area_en ILIKE '%DUBAI PRODUCTION%'
  AND actual_area BETWEEN 77.0 AND 78.0
  AND trans_value BETWEEN 1060000 AND 1065000;

-- ============================================================================
-- Verify Results
-- ============================================================================

-- Check how many properties were updated
SELECT 
    project_en,
    area_en,
    actual_area,
    trans_value,
    flip_score,
    esg_score
FROM properties
WHERE (flip_score IS NOT NULL AND flip_score > 0)
   OR (esg_score IS NOT NULL AND esg_score > 0)
ORDER BY flip_score DESC, esg_score DESC;

-- Summary statistics
SELECT 
    COUNT(*) as total_with_scores,
    MIN(flip_score) as min_flip,
    MAX(flip_score) as max_flip,
    AVG(flip_score) as avg_flip,
    MIN(esg_score) as min_esg,
    MAX(esg_score) as max_esg,
    AVG(esg_score) as avg_esg
FROM properties
WHERE flip_score IS NOT NULL AND flip_score > 0;

COMMIT;

-- ============================================================================
-- NOTES:
-- - This updates existing properties in the database
-- - Matches are fuzzy (ILIKE) to handle case variations
-- - Price and size ranges allow for small variations
-- - If no exact match found, property will not be updated
-- - Check the SELECT results to see what was updated
-- ============================================================================
