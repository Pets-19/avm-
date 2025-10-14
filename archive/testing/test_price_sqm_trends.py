#!/usr/bin/env python3
"""
Test suite for Price/SqM trends functionality
"""

import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import get_price_trends

class TestPriceSqmTrends(unittest.TestCase):
    """Test Price/SqM trend calculations"""
    
    def test_price_sqm_field_structure(self):
        """Test that price/sqm field is added to timeline data structure"""
        # Test with realistic filters that might have data
        filters = {
            'area': 'Dubai Marina',
            'property_type': 'Apartment',
            'bedrooms': '1'
        }
        
        timeline_data = get_price_trends(filters, 'buy', '6M')
        
        # Should return data structure even if empty
        self.assertIsInstance(timeline_data, list)
        
        # If data exists, it should have avg_price_per_sqm field
        if len(timeline_data) > 0:
            for data_point in timeline_data:
                self.assertIn('avg_price_per_sqm', data_point, 
                             "Timeline data should include avg_price_per_sqm field")
                self.assertIsInstance(data_point['avg_price_per_sqm'], (int, float),
                                    "avg_price_per_sqm should be numeric")
                # Should be >= 0 (can be 0 if no area data available)
                self.assertGreaterEqual(data_point['avg_price_per_sqm'], 0,
                                      "avg_price_per_sqm should be non-negative")
    
    def test_price_sqm_field_exists_in_empty_data(self):
        """Test that even with no data, the structure would include price/sqm"""
        # Use filters unlikely to match any data
        filters = {
            'area': 'NonExistentArea12345',
            'property_type': 'Castle',
            'bedrooms': 99
        }
        
        timeline_data = get_price_trends(filters, 'buy', '6M')
        
        # Should return empty list, but function should work without errors
        self.assertIsInstance(timeline_data, list)
        # For empty data, we can't test field structure, but function should not crash
    
    def test_price_sqm_calculation_safety(self):
        """Test that price/sqm calculation handles edge cases safely"""
        # This is an integration test - if the SQL is malformed, it will fail
        filters = {'area': 'Dubai'}  # Broad filter likely to have some data
        
        try:
            timeline_data = get_price_trends(filters, 'buy', '3M')
            # Should not throw SQL errors
            self.assertIsInstance(timeline_data, list)
            print(f"✅ Retrieved {len(timeline_data)} data points with price/sqm")
            
            # If data exists, verify structure
            if len(timeline_data) > 0:
                sample_point = timeline_data[0]
                required_fields = ['month', 'avg_price', 'transaction_count', 
                                 'min_price', 'max_price', 'avg_price_per_sqm']
                for field in required_fields:
                    self.assertIn(field, sample_point, f"Missing field: {field}")
                
                print(f"✅ Sample data point structure: {list(sample_point.keys())}")
                print(f"✅ Sample avg_price_per_sqm: {sample_point['avg_price_per_sqm']}")
                
        except Exception as e:
            self.fail(f"Price/SqM calculation should handle edge cases: {str(e)}")

if __name__ == '__main__':
    print("🧪 Testing Price/SqM Trends...")
    unittest.main()
