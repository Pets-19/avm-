#!/usr/bin/env python3
"""
Simple diagnostic to test if the trend API is working with proper authentication
"""

import requests
import json

# Test the API with a simple request
url = "http://localhost:5000/api/trends/price-timeline"
headers = {
    'Content-Type': 'application/json'
}
data = {
    "search_type": "buy",
    "time_period": "6M", 
    "area": "Dubai",
    "budget": 5000000,
    "propertyType": ""
}

print("🔍 Testing trend API endpoint...")

try:
    # First, try to get the main page to establish session
    session = requests.Session()
    
    # Get the login page to establish session
    login_response = session.get("http://localhost:5000/")
    print(f"Main page status: {login_response.status_code}")
    
    # Try the API call
    response = session.post(url, headers=headers, json=data)
    print(f"API Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"✅ API Success: {len(result.get('timeline', []))} data points")
            print(f"Status: {result.get('status', 'unknown')}")
            if result.get('timeline'):
                print(f"Sample data: {result['timeline'][0]}")
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
            print(f"Raw response: {response.text[:200]}...")
    else:
        print(f"❌ API failed with status {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
except Exception as e:
    print(f"❌ Connection failed: {e}")