#!/usr/bin/env python3
"""
Test script to verify bedroom filter functionality in Market Trends
"""

import requests
import json

def test_bedroom_filter():
    """Test the bedroom filter in trends API"""
    
    # Login first
    login_data = {
        'username': 'retyn',
        'password': 'retyn*#123'
    }
    
    session = requests.Session()
    
    # Login
    login_response = session.post('http://127.0.0.1:5000/login', data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        # Test trends API with bedroom filter
        trends_data = {
            'search_type': 'buy',
            'time_period': '6M',
            'propertyType': '',
            'bedrooms': '2 Bedrooms',  # Test bedroom filtering
            'area': '',
            'budget': 999999999
        }
        
        print(f"\nTesting trends API with data: {json.dumps(trends_data, indent=2)}")
        
        trends_response = session.post('http://127.0.0.1:5000/api/trends/price-timeline', 
                                      json=trends_data)
        
        print(f"Trends API status: {trends_response.status_code}")
        
        if trends_response.status_code == 200:
            result = trends_response.json()
            print(f"Success! Timeline data points: {len(result.get('timeline', []))}")
            
            if result.get('timeline'):
                print(f"Sample timeline entry: {result['timeline'][0]}")
                
            if result.get('summary'):
                summary = result['summary']
                print(f"Trend direction: {summary.get('trend_direction')}")
                print(f"Price change: {summary.get('percentage_change')}%")
                print(f"Average price: AED {summary.get('avg_monthly_price', 0):,.0f}")
                
            return True
        else:
            print(f"Trends API failed: {trends_response.text}")
            return False
    else:
        print("Login failed")
        return False

if __name__ == "__main__":
    success = test_bedroom_filter()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")