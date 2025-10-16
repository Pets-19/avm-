-- Insert User's 10 Properties with Flip Scores
-- Date: October 16, 2025
-- Purpose: Add test data for Flip Score filter UAT testing

BEGIN;

-- Delete any existing test data first (idempotent)
DELETE FROM properties WHERE transaction_number LIKE 'TEST-FLIP-%';

-- Insert the 10 properties from user's CSV
INSERT INTO properties (
    is_offplan_en, is_free_hold_en, usage_en, area_en, prop_type_en, prop_sb_type_en,
    trans_value, procedure_area, actual_area, rooms_en, parking,
    project_en, esg_score, flip_score,
    instance_date, transaction_number, group_en, procedure_en,
    nearest_metro_en, nearest_mall_en, nearest_landmark_en,
    total_buyer, total_seller, master_project_en
)
VALUES
-- Property 1: AZIZI VENICE 11 (Flip: 88, ESG: 30) - Madinat Al Mataar
('Off-Plan', 'Free Hold', 'Residential', 'Madinat Al Mataar', 'Unit', 'Flat',
 640000, 35.27, 35.27, 'Studio', 1,
 'AZIZI VENICE 11', 30, 88,
 '2025-10-01', 'TEST-FLIP-001', 'Sale', 'Sale',
 NULL, NULL, NULL, 0, 0, NULL),

-- Property 2: Samana Lake Views (Flip: 70, ESG: 25) - Dubai Production City
('Off-Plan', 'Free Hold', 'Residential', 'DUBAI PRODUCTION CITY', 'Unit', 'Flat',
 609292.8, 38.7, 38.7, 'Studio', 1,
 'Samana Lake Views', 25, 70,
 '2025-10-01', 'TEST-FLIP-002', 'Sale', 'Sale',
 'Damac Properties', 'Marina Mall', 'Sports City Swimming Academy', 0, 0, NULL),

-- Property 3: Samana Lake Views (Flip: 70, ESG: 25) - Dubai Production City
('Off-Plan', 'Free Hold', 'Residential', 'DUBAI PRODUCTION CITY', 'Unit', 'Flat',
 657324.72, 38.7, 38.7, 'Studio', 1,
 'Samana Lake Views', 25, 70,
 '2025-10-01', 'TEST-FLIP-003', 'Sale', 'Sale',
 'Damac Properties', 'Marina Mall', 'Sports City Swimming Academy', 0, 0, NULL),

-- Property 4: Ocean Pearl By SD (Flip: 80, ESG: 60) - Palm Deira
('Off-Plan', 'Free Hold', 'Residential', 'Palm Deira', 'Unit', 'Flat',
 3152355.36, 149.94, 149.94, '2 B/R', 1,
 'Ocean Pearl By SD', 60, 80,
 '2025-10-01', 'TEST-FLIP-004', 'Sale', 'Sale',
 NULL, NULL, NULL, 0, 0, NULL),

-- Property 5: Ocean Pearl 2 By SD (Flip: 82, ESG: 65) - Palm Deira
('Off-Plan', 'Free Hold', 'Residential', 'Palm Deira', 'Unit', 'Flat',
 2149000, 81.48, 81.48, '1 B/R', 1,
 'Ocean Pearl 2 By SD', 65, 82,
 '2025-10-01', 'TEST-FLIP-005', 'Sale', 'Sale',
 NULL, NULL, NULL, 0, 0, NULL),

-- Property 6: Ocean Pearl 2 By SD (Flip: 82, ESG: 65) - Palm Deira
('Off-Plan', 'Free Hold', 'Residential', 'Palm Deira', 'Unit', 'Flat',
 2076800, 82.75, 82.75, '1 B/R', 1,
 'Ocean Pearl 2 By SD', 65, 82,
 '2025-10-01', 'TEST-FLIP-006', 'Sale', 'Sale',
 NULL, NULL, NULL, 0, 0, NULL),

-- Property 7: Samana Lake Views (Flip: 70, ESG: 25) - Dubai Production City
('Off-Plan', 'Free Hold', 'Residential', 'DUBAI PRODUCTION CITY', 'Unit', 'Flat',
 733739.04, 43.97, 43.97, 'Studio', 1,
 'Samana Lake Views', 25, 70,
 '2025-10-01', 'TEST-FLIP-007', 'Sale', 'Sale',
 'Damac Properties', 'Marina Mall', 'Sports City Swimming Academy', 0, 0, NULL),

-- Property 8: CAPRIA EAST (Flip: 30, ESG: 25) - Wadi Al Safa 4
('Off-Plan', 'Free Hold', 'Residential', 'Wadi Al Safa 4', 'Unit', 'Flat',
 3236000, 156.39, 156.39, '2 B/R', 1,
 'CAPRIA EAST', 25, 30,
 '2025-10-01', 'TEST-FLIP-008', 'Sale', 'Sale',
 NULL, NULL, NULL, 0, 0, NULL),

-- Property 9: Samana Lake Views (Flip: 70, ESG: 25) - Dubai Production City
('Off-Plan', 'Free Hold', 'Residential', 'DUBAI PRODUCTION CITY', 'Unit', 'Flat',
 1061915.4, 77.21, 77.21, '1 B/R', 1,
 'Samana Lake Views', 25, 70,
 '2025-10-01', 'TEST-FLIP-009', 'Sale', 'Sale',
 'Damac Properties', 'Marina Mall', 'Sports City Swimming Academy', 0, 0, NULL);

-- Verify insertion
SELECT 
    project_en,
    area_en,
    actual_area,
    trans_value,
    flip_score,
    esg_score,
    rooms_en
FROM properties
WHERE transaction_number LIKE 'TEST-FLIP-%'
ORDER BY flip_score DESC, trans_value DESC;

-- Summary statistics
SELECT 
    'Total properties inserted' as metric,
    COUNT(*) as value
FROM properties
WHERE transaction_number LIKE 'TEST-FLIP-%'
UNION ALL
SELECT 
    'Flip score range' as metric,
    MIN(flip_score) || ' - ' || MAX(flip_score) as value
FROM properties
WHERE transaction_number LIKE 'TEST-FLIP-%';

COMMIT;

-- Success message
SELECT '✅ Successfully inserted 9 properties with flip scores!' as status;
