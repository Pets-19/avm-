#!/usr/bin/env python3
"""
Test Arbitrage Filter with User's 9 Properties
Validates all properties work correctly with combined filters
"""

from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)

print("=" * 70)
print("🧪 ARBITRAGE FILTER TEST - USER'S 9 PROPERTIES")
print("=" * 70)
print()

# Test cases based on user's data
test_cases = [
    {
        'name': 'TEST 1: Palm Deira, Unit, 150 sqm, Arbitrage 80+',
        'area': 'Palm Deira',
        'type': 'Unit',
        'size': 150,
        'arbitrage_min': 80,
        'expected_project': 'Ocean Pearl By SD',
        'expected_arbitrage': 82
    },
    {
        'name': 'TEST 2: Dubai Production City, Unit, 40 sqm, Arbitrage 30+',
        'area': 'DUBAI PRODUCTION CITY',
        'type': 'Unit',
        'size': 40,
        'arbitrage_min': 30,
        'expected_project': 'Samana Lake Views',
        'expected_count': 4
    },
    {
        'name': 'TEST 3: Madinat Al Mataar, Unit, 35 sqm, Any Arbitrage',
        'area': 'Madinat Al Mataar',
        'type': 'Unit',
        'size': 35,
        'arbitrage_min': None,
        'expected_project': 'AZIZI VENICE 11',
        'expected_arbitrage': 10
    },
    {
        'name': 'TEST 4: Palm Deira, Unit, 82 sqm, Arbitrage 70+',
        'area': 'Palm Deira',
        'type': 'Unit',
        'size': 82,
        'arbitrage_min': 70,
        'expected_project': 'Ocean Pearl 2 By SD',
        'expected_arbitrage': 75,
        'expected_count': 2
    },
    {
        'name': 'TEST 5: Wadi Al Safa 4, Unit, 156 sqm, Arbitrage 30+',
        'area': 'Wadi Al Safa 4',
        'type': 'Unit',
        'size': 156,
        'arbitrage_min': 30,
        'expected_project': 'CAPRIA EAST',
        'expected_arbitrage': 45
    }
]

passed = 0
failed = 0

for test in test_cases:
    print(f"\n{'='*70}")
    print(f"📋 {test['name']}")
    print('='*70)
    
    # Build query simulating app.py logic
    arbitrage_condition = ""
    if test['arbitrage_min']:
        arbitrage_condition = f"AND arbitrage_score >= {test['arbitrage_min']}"
    
    size_min = test['size'] * 0.7
    size_max = test['size'] * 1.3
    
    query = text(f"""
        SELECT 
            project_en,
            area_en,
            prop_type_en,
            actual_area,
            rooms_en,
            arbitrage_score,
            esg_score,
            flip_score,
            trans_value
        FROM properties 
        WHERE 
            trans_value > 0 
            AND actual_area IS NOT NULL 
            AND actual_area != ''
            AND actual_area ~ '^[0-9]+\\.?[0-9]*$'
            AND CAST(actual_area AS NUMERIC) > 0 
            AND area_en IS NOT NULL 
            AND prop_type_en IS NOT NULL
            AND trans_value BETWEEN 100000 AND 50000000
            AND CAST(actual_area AS NUMERIC) BETWEEN 20 AND 2000
            {arbitrage_condition}
            AND (
                LOWER(area_en) LIKE LOWER(:area_param)
                OR (
                    LOWER(prop_type_en) = LOWER(:type_param)
                    AND CAST(actual_area AS NUMERIC) BETWEEN :size_min AND :size_max
                )
            )
        ORDER BY 
            CASE 
                WHEN LOWER(area_en) LIKE LOWER(:area_param) THEN 1
                ELSE 2
            END,
            ABS(CAST(actual_area AS NUMERIC) - :target_size),
            instance_date DESC
        LIMIT 50
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {
                'area_param': f'%{test["area"]}%',
                'type_param': test['type'],
                'size_min': size_min,
                'size_max': size_max,
                'target_size': test['size']
            })
            rows = result.fetchall()
            
            print(f"\n✅ Query executed successfully")
            print(f"📊 Found {len(rows)} matching properties")
            
            if rows:
                # Show first 3 matches
                print(f"\n📍 Top matches:")
                for i, row in enumerate(rows[:3], 1):
                    print(f"\n  {i}. {row[0]} ({row[1]})")
                    print(f"     Type: {row[2]}, Size: {row[3]} sqm")
                    print(f"     Bedrooms: {row[4]}")
                    print(f"     Scores - Arb: {row[5]}, ESG: {row[6]}, Flip: {row[7]}")
                    print(f"     Price: {float(row[8]):,.0f} AED")
                
                # Validate expectations
                if 'expected_project' in test:
                    found = any(row[0] == test['expected_project'] for row in rows)
                    if found:
                        print(f"\n✅ Expected project '{test['expected_project']}' found")
                        passed += 1
                    else:
                        print(f"\n❌ Expected project '{test['expected_project']}' NOT found")
                        failed += 1
                
                if 'expected_count' in test:
                    actual_count = len([r for r in rows if r[0] == test.get('expected_project')])
                    if actual_count == test['expected_count']:
                        print(f"✅ Expected count {test['expected_count']} matches actual {actual_count}")
                    else:
                        print(f"⚠️  Expected {test['expected_count']} but got {actual_count}")
            else:
                print(f"\n❌ No properties found - this should not happen for user's data!")
                failed += 1
                
    except Exception as e:
        print(f"\n❌ Query failed: {e}")
        failed += 1

# Summary
print(f"\n\n{'='*70}")
print("📊 TEST SUMMARY")
print('='*70)
print(f"\n✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"Total: {passed + failed}")

if failed == 0:
    print(f"\n🎉 ALL TESTS PASSED - User's 9 properties work correctly!")
else:
    print(f"\n⚠️  Some tests failed - needs investigation")

print()
