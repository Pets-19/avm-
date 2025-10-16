#!/usr/bin/env python3
"""
Manual test script for ESG filter
Tests the ESG functionality without authentication
"""
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_valuation_with_esg():
    """Test property valuation with ESG filter"""
    
    print("=" * 60)
    print("🧪 MANUAL ESG FILTER TEST")
    print("=" * 60)
    
    # Test 1: No ESG filter (baseline)
    print("\n📊 Test 1: Valuation WITHOUT ESG filter")
    print("-" * 60)
    payload = {
        "property_type": "Unit",
        "area": "Dubai Marina",
        "size_sqm": 150
    }
    
    response = requests.post(f"{BASE_URL}/api/property/valuation", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success')}")
        print(f"📈 Comparable count: {data.get('metadata', {}).get('comparable_count', 'N/A')}")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"❌ Response: {response.text[:200]}")
    
    # Test 2: With ESG filter 25+
    print("\n📊 Test 2: Valuation WITH ESG >= 25")
    print("-" * 60)
    payload_esg = {
        "property_type": "Unit",
        "area": "Dubai Marina",
        "size_sqm": 150,
        "esg_score_min": 25
    }
    
    response = requests.post(f"{BASE_URL}/api/property/valuation", json=payload_esg)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success')}")
        print(f"📈 Comparable count: {data.get('metadata', {}).get('comparable_count', 'N/A')}")
        print(f"🌱 ESG filter applied: 25+")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"❌ Response: {response.text[:200]}")
    
    # Test 3: With ESG filter 60+ (high performance)
    print("\n📊 Test 3: Valuation WITH ESG >= 60 (High Performance)")
    print("-" * 60)
    payload_high_esg = {
        "property_type": "Unit",
        "area": "Dubai Marina",
        "size_sqm": 150,
        "esg_score_min": 60
    }
    
    response = requests.post(f"{BASE_URL}/api/property/valuation", json=payload_high_esg)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success')}")
        print(f"📈 Comparable count: {data.get('metadata', {}).get('comparable_count', 'N/A')}")
        print(f"🌱 ESG filter applied: 60+")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"❌ Response: {response.text[:200]}")
    
    # Test 4: ESG + Bedrooms filter
    print("\n📊 Test 4: ESG >= 40 + 2 Bedrooms (Combined filters)")
    print("-" * 60)
    payload_combined = {
        "property_type": "Unit",
        "area": "Business Bay",
        "size_sqm": 120,
        "bedrooms": "2",
        "esg_score_min": 40
    }
    
    response = requests.post(f"{BASE_URL}/api/property/valuation", json=payload_combined)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Success: {data.get('success')}")
        print(f"📈 Comparable count: {data.get('metadata', {}).get('comparable_count', 'N/A')}")
        print(f"🛏️  Bedrooms filter: 2")
        print(f"🌱 ESG filter: 40+")
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"❌ Response: {response.text[:200]}")
    
    print("\n" + "=" * 60)
    print("✅ Manual test complete!")
    print("=" * 60)

if __name__ == '__main__':
    test_valuation_with_esg()
