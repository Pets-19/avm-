#!/usr/bin/env python3
"""
Test script for segment classification feature
Tests the classify_price_segment() function with various inputs
"""

import sys
sys.path.insert(0, '/workspaces/avm-retyn')

from app import classify_price_segment

def test_segment_classification():
    """Run comprehensive tests on segment classification"""
    
    print("=" * 80)
    print("🧪 SEGMENT CLASSIFICATION TEST SUITE")
    print("=" * 80)
    print()
    
    tests = [
        # (price_per_sqm, expected_label, expected_icon, expected_percentile, test_name)
        (5000, 'Budget', '🏘️', 25, 'Low-end property (Al Aweer)'),
        (11999, 'Budget', '🏘️', 25, 'Budget tier upper boundary'),
        (12000, 'Mid-Tier', '🏢', 50, 'Mid-tier lower boundary'),
        (14000, 'Mid-Tier', '🏢', 50, 'Typical mid-tier (Discovery Gardens)'),
        (16199, 'Mid-Tier', '🏢', 50, 'Mid-tier upper boundary'),
        (16200, 'Premium', '🌟', 75, 'Premium lower boundary'),
        (19000, 'Premium', '🌟', 75, 'Typical premium (JBR)'),
        (21799, 'Premium', '🌟', 75, 'Premium upper boundary'),
        (21800, 'Luxury', '💎', 90, 'Luxury lower boundary'),
        (25000, 'Luxury', '💎', 90, 'Typical luxury (Marina)'),
        (27318, 'Luxury', '💎', 90, 'Business Bay example'),
        (28799, 'Luxury', '💎', 90, 'Luxury upper boundary'),
        (28800, 'Ultra-Luxury', '🏰', 95, 'Ultra-luxury lower boundary'),
        (41128, 'Ultra-Luxury', '🏰', 95, 'Palm Jumeirah'),
        (50000, 'Ultra-Luxury', '🏰', 95, 'Burj Khalifa tier'),
        (76513, 'Ultra-Luxury', '🏰', 95, 'Jumeirah Second (highest)'),
    ]
    
    passed = 0
    failed = 0
    
    print("📊 VALID PRICE TESTS:")
    print("-" * 80)
    
    for price, exp_label, exp_icon, exp_pct, test_name in tests:
        result = classify_price_segment(price)
        
        if result is None:
            print(f"❌ FAIL: {test_name}")
            print(f"   Price: {price:,} AED/sqm → Expected: {exp_label}, Got: None")
            failed += 1
            continue
        
        # Check all fields
        label_ok = result['label'] == exp_label
        icon_ok = result['icon'] == exp_icon
        pct_ok = result['percentile'] == exp_pct
        
        if label_ok and icon_ok and pct_ok:
            top_pct = 100 - exp_pct
            print(f"✅ PASS: {test_name}")
            print(f"   {price:>8,} AED/sqm → {result['icon']} {result['label']} (Top {top_pct}%)")
            passed += 1
        else:
            print(f"❌ FAIL: {test_name}")
            print(f"   Price: {price:,} AED/sqm")
            if not label_ok:
                print(f"   Label: Expected '{exp_label}', Got '{result['label']}'")
            if not icon_ok:
                print(f"   Icon: Expected '{exp_icon}', Got '{result['icon']}'")
            if not pct_ok:
                print(f"   Percentile: Expected {exp_pct}, Got {result['percentile']}")
            failed += 1
    
    print()
    print("⚠️  EDGE CASE TESTS:")
    print("-" * 80)
    
    edge_cases = [
        (0, None, 'Zero price'),
        (-100, None, 'Negative price'),
        (None, None, 'None input'),
        (-1, None, 'Negative one'),
        (0.5, None, 'Very small positive'),
    ]
    
    for price, expected, test_name in edge_cases:
        result = classify_price_segment(price)
        
        if result == expected:
            print(f"✅ PASS: {test_name}")
            print(f"   Input: {price} → Correctly returned None")
            passed += 1
        else:
            print(f"❌ FAIL: {test_name}")
            print(f"   Input: {price} → Expected None, Got {result}")
            failed += 1
    
    print()
    print("=" * 80)
    print("📈 TEST SUMMARY")
    print("=" * 80)
    total = passed + failed
    pass_rate = (passed / total * 100) if total > 0 else 0
    print(f"Total Tests: {total}")
    print(f"Passed:      {passed} ✅")
    print(f"Failed:      {failed} ❌")
    print(f"Pass Rate:   {pass_rate:.1f}%")
    print()
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Feature is production-ready!")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review and fix.")
    
    print("=" * 80)
    
    return failed == 0


if __name__ == '__main__':
    success = test_segment_classification()
    sys.exit(0 if success else 1)
