#!/usr/bin/env python3
"""
Simulate API call for Palm Deira 150sqm with Arbitrage 80+ filter
This replicates the exact valuation request that returns HTTP 500
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, '/workspaces/avm-')

from app import calculate_valuation_from_database, engine
import traceback

print("=" * 70)
print("🧪 SIMULATING API CALL: Palm Deira 150sqm, Arbitrage 80+")
print("=" * 70)
print()

# Exact parameters from user's request
request_data = {
    'property_type': 'Unit',
    'area': 'Palm Deira',
    'size_sqm': 150.0,
    'bedrooms': None,  # Any bedrooms
    'development_status': None,  # Any status
    'floor_level': None,
    'view_type': None,
    'property_age': None,
    'esg_score_min': None,
    'flip_score_min': None,
    'arbitrage_score_min': 80  # User selected 80+
}

print("📋 Request Parameters:")
for key, value in request_data.items():
    if value is not None:
        print(f"   {key}: {value}")
print()

print("🔄 Calling calculate_valuation_from_database()...")
print()

try:
    result = calculate_valuation_from_database(
        property_type=request_data['property_type'],
        area=request_data['area'],
        size_sqm=request_data['size_sqm'],
        bedrooms=request_data['bedrooms'],
        development_status=request_data['development_status'],
        floor_level=request_data['floor_level'],
        view_type=request_data['view_type'],
        property_age=request_data['property_age'],
        esg_score_min=request_data['esg_score_min'],
        flip_score_min=request_data['flip_score_min'],
        arbitrage_score_min=request_data['arbitrage_score_min'],
        engine=engine
    )
    
    print("=" * 70)
    print("✅ SUCCESS - Valuation completed without error")
    print("=" * 70)
    print()
    
    if result['success']:
        print("📊 Valuation Result:")
        print(f"   Estimated Value: {result.get('estimated_value', 0):,.0f} AED")
        print(f"   Price per sqm: {result.get('price_per_sqm', 0):,.0f} AED/sqm")
        print(f"   Confidence: {result.get('confidence', 0)}%")
        print(f"   Comparables used: {result.get('comparables_count', 0)}")
        
        if 'rental_data' in result and result['rental_data']:
            print(f"\n💰 Rental Yield:")
            rental = result['rental_data']
            print(f"   Annual Rent: {rental.get('annual_rent', 0):,.0f} AED/year")
            print(f"   Gross Yield: {rental.get('gross_yield', 0):.2f}%")
            print(f"   Rental Comparables: {rental.get('comparables', 0)}")
        else:
            print(f"\n⚠️  No rental data available")
        
        print()
        print("🎉 This should work in the browser!")
    else:
        print("❌ Valuation returned success=False")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print("=" * 70)
    print("❌ ERROR - This is what's causing HTTP 500!")
    print("=" * 70)
    print()
    print(f"Exception Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print()
    print("Full Traceback:")
    print("-" * 70)
    traceback.print_exc()
    print("-" * 70)
    print()
    print("🔍 This is the exact error the user is seeing!")
