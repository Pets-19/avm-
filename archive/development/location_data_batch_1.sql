-- Location Premium Data Import
-- Generated: 2025-10-07T17:35:22.609936
-- Records: 50

BEGIN;

-- Area 1: Al Yelayiss 1
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Yelayiss 1', 25.0371, 55.2492,
    12.1, 23.7, 8.8, 1.5,
    20.1, 3.5,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 2: Jumeirah Lakes Towers
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Jumeirah Lakes Towers', 25.0756, 55.1454,
    0.5, 2.8, 4.7, 1.4,
    19.5, 4.0,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 3: Motor City
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Motor City', 25.0483, 55.2426,
    9.8, 17.2, 7.5, 0.8,
    19.2, 3.8,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 4: Burj Khalifa
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Burj Khalifa', 25.1972, 55.2744,
    0.6, 10.8, 0.1, 3.2,
    1.5, 4.8,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 5: Madinat Hind 4
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Madinat Hind 4', 25.0168, 55.3676,
    21.5, 37.1, 15.2, 6.1,
    25.8, 3.2,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 6: Silicon Oasis
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Silicon Oasis', 25.1214, 55.3879,
    14.5, 28.1, 10.1, 0.5,
    17.9, 3.7,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 7: Al Furjan
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Furjan', 25.0256, 55.1581,
    0.7, 10.1, 4.1, 0.9,
    23.1, 3.9,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 8: Arjan
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Arjan', 25.0351, 55.2327,
    8.1, 15.1, 6.1, 0.3,
    18.1, 3.6,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 9: Bukadra
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Bukadra', 25.1761, 55.3342,
    8.1, 18.5, 7.9, 3.1,
    8.5, 3.3,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 10: Dubai Investment Park Second
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Dubai Investment Park Second', 24.9786, 55.1873,
    4.1, 21.9, 13.2, 3.0,
    30.1, 3.4,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 11: Al Yufrah 1
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Yufrah 1', 25.0515, 55.4521,
    24.2, 40.1, 16.5, 8.1,
    28.5, 3.0,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 12: Dubai Hills
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Dubai Hills', 25.1013, 55.2380,
    8.2, 15.5, 1.1, 3.1,
    12.1, 4.5,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 13: Wadi Al Safa 5
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Wadi Al Safa 5', 25.0778, 55.3522,
    15.1, 25.2, 10.0, 1.7,
    16.8, 3.6,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 14: Dubai Creek Harbour
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Dubai Creek Harbour', 25.2064, 55.3456,
    3.9, 19.2, 7.1, 2.2,
    9.8, 4.2,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 15: Dubai South
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Dubai South', 24.8978, 55.1431,
    8.1, 30.5, 21.5, 6.2,
    38.1, 3.5,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 16: Jabal Ali First
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Jabal Ali First', 25.0511, 55.1382,
    1.1, 9.8, 5.1, 2.0,
    25.1, 3.7,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 17: Al Hebiah Fifth
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Hebiah Fifth', 25.0078, 55.2387,
    11.2, 21.5, 10.9, 3.4,
    22.1, 3.4,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 18: INTERNATIONAL CITY PH 1
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'INTERNATIONAL CITY PH 1', 25.1544, 55.4039,
    9.8, 26.1, 9.5, 4.8,
    19.1, 3.1,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 19: Meydan One
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Meydan One', 25.1737, 55.2870,
    3.1, 14.2, 3.5, 1.4,
    4.8, 4.1,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 20: Damac Hills
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Damac Hills', 25.0311, 55.2483,
    12.5, 20.1, 9.1, 0.9,
    21.5, 3.9,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 21: Wadi Al Safa 7
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Wadi Al Safa 7', 25.0398, 55.2856,
    15.2, 24.1, 12.8, 0.9,
    18.5, 3.5,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 22: Madinat Dubai Almelaheyah
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Madinat Dubai Almelaheyah', 25.2648, 55.2658,
    2.1, 5.1, 9.8, 3.5,
    8.2, 3.8,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 23: Wadi Al Safa 3
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Wadi Al Safa 3', 25.0672, 55.2675,
    10.2, 17.9, 8.5, 3.9,
    12.9, 3.7,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 24: INTERNATIONAL CITY PH 2 & 3
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'INTERNATIONAL CITY PH 2 & 3', 25.1385, 55.4311,
    12.5, 28.8, 11.2, 6.5,
    21.8, 3.0,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 25: Town Square
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Town Square', 25.0185, 55.2711,
    15.8, 25.9, 11.5, 0.8,
    23.9, 3.7,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 26: Sobha Heartland
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Sobha Heartland', 25.1771, 55.3074,
    4.5, 15.8, 5.1, 0.6,
    6.2, 4.2,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 27: Al Yelayiss 2
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Yelayiss 2', 25.0095, 55.2751,
    15.1, 26.2, 11.8, 3.5,
    24.9, 3.4,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 28: Dubai Maritime City
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Dubai Maritime City', 25.2671, 55.2653,
    2.1, 5.2, 9.9, 4.1,
    8.1, 3.6,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 29: Dubai Studio City
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Dubai Studio City', 25.0426, 55.2513,
    9.1, 16.5, 7.1, 0.4,
    20.1, 3.7,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 30: Marsa Dubai
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Marsa Dubai', 25.0815, 55.1397,
    0.6, 1.5, 1.1, 2.5,
    20.9, 4.6,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 31: Me'Aisem Second
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Me'Aisem Second', 25.0012, 55.2122,
    9.8, 20.1, 8.8, 4.1,
    25.5, 3.2,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 32: Al Khairan First
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Khairan First', 25.1957, 55.3599,
    3.5, 19.5, 6.5, 2.2,
    11.1, 4.0,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 33: Al Wasl
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Wasl', 25.1964, 55.2549,
    2.8, 8.1, 3.8, 1.8,
    3.9, 4.4,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 34: Emirate Living
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Emirate Living', 25.0662, 55.1711,
    4.1, 8.5, 5.9, 1.1,
    15.1, 4.7,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 35: Discovery Gardens
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Discovery Gardens', 25.0330, 55.1554,
    1.1, 8.9, 2.8, 2.0,
    24.9, 3.6,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 36: Liwan
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Liwan', 25.1025, 55.3688,
    14.1, 26.5, 10.5, 1.2,
    17.2, 3.3,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 37: Al Satwa
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Satwa', 25.2191, 55.2726,
    1.8, 6.9, 4.7, 2.5,
    3.5, 3.8,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 38: The Greens
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'The Greens', 25.0934, 55.1704,
    1.8, 7.8, 4.1, 1.1,
    13.5, 4.2,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 39: Dubai Harbour
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Dubai Harbour', 25.0955, 55.1481,
    1.9, 1.1, 3.1, 3.8,
    19.1, 4.3,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 40: Jumeirah Beach Residence
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Jumeirah Beach Residence', 25.0779, 55.1340,
    1.1, 0.1, 1.8, 2.5,
    22.1, 4.6,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 41: Emaar South
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Emaar South', 24.9085, 55.1861,
    8.5, 31.2, 21.1, 1.1,
    37.2, 3.5,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 42: Down Town Jabal Ali
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Down Town Jabal Ali', 25.0580, 55.1273,
    0.1, 11.2, 4.8, 6.1,
    26.9, 3.5,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 43: Tecom Site D
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Tecom Site D', 25.0951, 55.1782,
    1.1, 7.1, 3.5, 1.1,
    12.8, 4.1,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 44: Palm Jabal Ali
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Palm Jabal Ali', 25.0027, 54.9876,
    14.5, 14.1, 15.9, 10.0,
    38.5, 3.0,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 45: Al Aweer First
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Al Aweer First', 25.1757, 55.5469,
    21.9, 33.3, 17.5, 10.0,
    29.9, 2.9,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 46: Villanova
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Villanova', 25.0521, 55.3595,
    18.5, 29.1, 12.1, 1.9,
    21.1, 3.6,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 47: Remraam
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Remraam', 25.0215, 55.2281,
    10.5, 22.5, 11.8, 0.7,
    24.1, 3.5,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 48: DUBAI HEALTHCARE CITY - PHASE 2
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'DUBAI HEALTHCARE CITY - PHASE 2', 25.2255, 55.3311,
    1.1, 15.1, 8.8, 2.2,
    7.9, 3.8,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 49: Dubai Industrial City
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Dubai Industrial City', 24.8795, 55.0911,
    12.1, 32.5, 25.1, 10.0,
    41.2, 3.1,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

-- Area 50: Arabian Ranches I
INSERT INTO area_coordinates (
    area_name, latitude, longitude,
    distance_to_metro_km, distance_to_beach_km, 
    distance_to_mall_km, distance_to_school_km,
    distance_to_business_km, neighborhood_score,
    geocoded_source, geocoded_at
) VALUES (
    'Arabian Ranches I', 25.0533, 55.2589,
    12.1, 20.3, 7.2, 1.8,
    19.2, 4.2,
    'bulk_import', NOW()
)
ON CONFLICT (area_name) DO UPDATE SET
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    distance_to_metro_km = EXCLUDED.distance_to_metro_km,
    distance_to_beach_km = EXCLUDED.distance_to_beach_km,
    distance_to_mall_km = EXCLUDED.distance_to_mall_km,
    distance_to_school_km = EXCLUDED.distance_to_school_km,
    distance_to_business_km = EXCLUDED.distance_to_business_km,
    neighborhood_score = EXCLUDED.neighborhood_score,
    geocoded_source = EXCLUDED.geocoded_source,
    geocoded_at = NOW();

COMMIT;
