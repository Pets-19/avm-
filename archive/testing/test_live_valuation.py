#!/usr/bin/env python3
"""
Direct test of valuation with geospatial premium (bypassing authentication).
"""

import sys
sys.path.insert(0, '/workspaces/avm-retyn')

from app import engine, calculate_valuation_from_database
import json

print("="*70)
print("🧪 TESTING LIVE VALUATION WITH GEOSPATIAL PREMIUM")
print("="*70)

# Test 1: Dubai Marina (prime waterfront location)
print("\n📍 TEST 1: Dubai Marina - 100sqm, 2BR Unit")
print("-"*70)

result = calculate_valuation_from_database(
    property_type='Unit',
    area='Dubai Marina',
    size_sqm=100,
    bedrooms='2',
    development_status=None,
    engine=engine
)

if result['success']:
    valuation = result['valuation']
    
    print(f"\n💰 VALUATION RESULTS:")
    print(f"   Estimated Value: AED {valuation['estimated_value']:,}")
    print(f"   Confidence: {valuation['confidence_score']}%")
    print(f"   Price per sqm: AED {valuation['price_per_sqm']:,}")
    
    print(f"\n📊 VALUE RANGE:")
    print(f"   Low:  AED {valuation['value_range']['low']:,}")
    print(f"   High: AED {valuation['value_range']['high']:,}")
    
    # Geospatial premium details
    location_premium = valuation.get('location_premium', {})
    print(f"\n🌍 GEOSPATIAL LOCATION PREMIUM:")
    print(f"   Total Premium: {location_premium.get('total_premium_pct', 0):+.2f}%")
    print(f"   Cache Status: {location_premium.get('cache_status', 'UNKNOWN')}")
    print(f"   Applied: {'✅ YES' if location_premium.get('applied') else '❌ NO'}")
    
    # Premium breakdown
    breakdown = location_premium.get('breakdown', {})
    if breakdown:
        print(f"\n   📍 Premium Breakdown:")
        print(f"      Metro:        {breakdown.get('metro', 0):+.2f}%")
        print(f"      Beach:        {breakdown.get('beach', 0):+.2f}%")
        print(f"      Mall:         {breakdown.get('mall', 0):+.2f}%")
        print(f"      School:       {breakdown.get('school', 0):+.2f}%")
        print(f"      Business:     {breakdown.get('business', 0):+.2f}%")
        print(f"      Neighborhood: {breakdown.get('neighborhood', 0):+.2f}%")
    
    # Rental data
    rental_data = valuation.get('rental_data')
    if rental_data:
        print(f"\n🏠 RENTAL YIELD:")
        print(f"   Annual Rent: AED {rental_data.get('annual_rent', 0):,}")
        print(f"   Rental Comparables: {rental_data.get('count', 0)}")
        annual_rent = rental_data.get('annual_rent', 0)
        est_value = valuation['estimated_value']
        if est_value > 0:
            yield_pct = (annual_rent / est_value) * 100
            print(f"   Gross Yield: {yield_pct:.2f}%")
    
    print(f"\n📈 MARKET DATA:")
    market = valuation.get('market_data', {})
    print(f"   Median Price per sqm: AED {market.get('median_price_per_sqm', 0):,}")
    print(f"   Price Variance: {market.get('price_variance', 0)}%")
    
    print(f"\n📚 COMPARABLES:")
    print(f"   Total Found: {valuation['total_comparables_found']}")
    print(f"   Search Scope: {valuation['search_scope']}")
    
else:
    print(f"\n❌ VALUATION FAILED:")
    print(f"   Error: {result.get('error', 'Unknown error')}")

# Test 2: Downtown Dubai (another prime location)
print("\n"+"="*70)
print("📍 TEST 2: Downtown Dubai - 120sqm, 2BR Unit")
print("-"*70)

result2 = calculate_valuation_from_database(
    property_type='Unit',
    area='Downtown Dubai',
    size_sqm=120,
    bedrooms='2',
    development_status=None,
    engine=engine
)

if result2['success']:
    val2 = result2['valuation']
    loc_prem2 = val2.get('location_premium', {})
    
    print(f"\n💰 Estimated Value: AED {val2['estimated_value']:,}")
    print(f"🌍 Location Premium: {loc_prem2.get('total_premium_pct', 0):+.2f}%")
    print(f"📊 Cache Status: {loc_prem2.get('cache_status', 'UNKNOWN')}")
    print(f"🏆 Confidence: {val2['confidence_score']}%")
else:
    print(f"❌ Error: {result2.get('error')}")

print("\n"+"="*70)
print("✅ GEOSPATIAL PREMIUM TESTING COMPLETE")
print("="*70)
