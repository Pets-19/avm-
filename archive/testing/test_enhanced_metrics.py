#!/usr/bin/env python3
"""
Test Enhanced Market Trend Metrics
Tests for avg_monthly_price, price_momentum, and affordability_index
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import calculate_basic_trends

class TestEnhancedMetrics(unittest.TestCase):
    
    def test_average_monthly_price_calculation(self):
        """Test that avg_monthly_price is calculated and returned"""
        # Mock trend data with varying prices
        mock_trend_data = [
            {'month': '2025-03', 'avg_price': 2500000, 'transaction_count': 4000},
            {'month': '2025-04', 'avg_price': 2800000, 'transaction_count': 5000},
            {'month': '2025-05', 'avg_price': 2700000, 'transaction_count': 4500},
        ]
        
        result = calculate_basic_trends(mock_trend_data)
        
        # Should have avg_monthly_price field
        self.assertIn('avg_monthly_price', result)
        
        # Should be average of all monthly prices: (2.5M + 2.8M + 2.7M) / 3 = 2.67M
        expected_avg = (2500000 + 2800000 + 2700000) / 3
        self.assertAlmostEqual(result['avg_monthly_price'], expected_avg, delta=1000)
    
    def test_price_momentum_calculation(self):
        """Test price momentum detection"""
        # Mock trend data showing acceleration
        mock_trend_data = [
            {'month': '2025-01', 'avg_price': 2500000, 'transaction_count': 4000},
            {'month': '2025-02', 'avg_price': 2600000, 'transaction_count': 4200},
            {'month': '2025-03', 'avg_price': 2750000, 'transaction_count': 4500},
            {'month': '2025-04', 'avg_price': 2900000, 'transaction_count': 5000},
        ]
        
        result = calculate_basic_trends(mock_trend_data)
        
        # Should have price_momentum field
        self.assertIn('price_momentum', result)
        
        # With accelerating price increases, should be 'Accelerating'
        self.assertEqual(result['price_momentum'], 'Accelerating')
    
    def test_affordability_index_calculation(self):
        """Test affordability index relative to historical average"""
        # Mock trend data with current prices above historical
        mock_trend_data = [
            {'month': '2025-03', 'avg_price': 3000000, 'transaction_count': 4000},
            {'month': '2025-04', 'avg_price': 3100000, 'transaction_count': 5000},
        ]
        
        result = calculate_basic_trends(mock_trend_data)
        
        # Should have affordability_index field
        self.assertIn('affordability_index', result)
        
        # Should be a valid index value
        self.assertIsInstance(result['affordability_index'], (int, float))
    
    def test_enhanced_metrics_with_minimal_data(self):
        """Test enhanced metrics work with minimal data (2 months)"""
        mock_trend_data = [
            {'month': '2025-06', 'avg_price': 2600000, 'transaction_count': 5000},
            {'month': '2025-07', 'avg_price': 2700000, 'transaction_count': 5200},
        ]
        
        result = calculate_basic_trends(mock_trend_data)
        
        # All new metrics should be present
        self.assertIn('avg_monthly_price', result)
        self.assertIn('price_momentum', result) 
        self.assertIn('affordability_index', result)
        
        # Avg price should be (2.6M + 2.7M) / 2 = 2.65M
        expected_avg = (2600000 + 2700000) / 2
        self.assertEqual(result['avg_monthly_price'], expected_avg)

if __name__ == '__main__':
    print("🧪 Testing Enhanced Market Trend Metrics...")
    unittest.main(verbosity=2)