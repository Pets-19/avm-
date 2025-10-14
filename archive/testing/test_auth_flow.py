#!/usr/bin/env python3
"""
Quick authentication test to verify login credentials work
"""

import requests
import json

def test_authentication():
    """Test the authentication flow"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔐 Testing Authentication Flow...")
    print("=" * 50)
    
    # Test 1: Access login page
    try:
        login_response = requests.get(f"{base_url}/login")
        print(f"✅ Login page accessible: {login_response.status_code}")
    except Exception as e:
        print(f"❌ Cannot access login page: {e}")
        return
    
    # Test 2: Attempt login with correct credentials
    login_data = {
        'username': 'retyn',
        'password': 'retyn*#123'
    }
    
    try:
        session = requests.Session()
        login_post = session.post(f"{base_url}/login", data=login_data)
        print(f"✅ Login attempt response: {login_post.status_code}")
        
        # Test 3: Try to access main page after login
        if login_post.status_code == 200 or login_post.status_code == 302:
            main_page = session.get(f"{base_url}/")
            print(f"✅ Main page after login: {main_page.status_code}")
            
            # Test 4: Try to access trend API
            trend_data = {
                'search_type': 'buy',
                'time_period': '3_months',
                'propertyType': '',
                'area': 'Dubai',
                'budget': 3000000
            }
            
            trend_response = session.post(
                f"{base_url}/api/trends/price-timeline",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(trend_data)
            )
            
            print(f"✅ Trend API response: {trend_response.status_code}")
            
            if trend_response.status_code == 200:
                try:
                    trend_json = trend_response.json()
                    print(f"✅ Trend API working: {trend_json.get('status', 'unknown')}")
                    if trend_json.get('timeline'):
                        print(f"✅ Timeline data points: {len(trend_json['timeline'])}")
                    else:
                        print("⚠️ No timeline data in response")
                except Exception as e:
                    print(f"❌ Cannot parse trend API response: {e}")
            else:
                print(f"❌ Trend API failed: {trend_response.text[:200]}")
        else:
            print(f"❌ Login failed: {login_post.text[:200]}")
            
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
    
    print("\n🎯 RESOLUTION:")
    print("1. Make sure you're logged in with username: retyn")
    print("2. Use password: retyn*#123")
    print("3. Access the Market Trends tab after login")
    print("4. Click 'Analyze Market Trends' button")

if __name__ == "__main__":
    test_authentication()