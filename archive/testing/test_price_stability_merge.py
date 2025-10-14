#!/usr/bin/env python3
"""
Test for Price Stability Merge Feature
Tests that redundant Price Volatility and Market Stability are merged into single Price Stability.
"""

import unittest
from bs4 import BeautifulSoup


class TestPriceStabilityMerge(unittest.TestCase):
    """Test price stability consolidation functionality"""
    
    def setUp(self):
        """Load the HTML template for testing"""
        with open('/workspaces/avm-retyn/templates/index.html', 'r') as f:
            self.html_content = f.read()
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
    
    def test_single_price_stability_element_exists(self):
        """Test that single price-stability element exists"""
        price_stability = self.soup.find(id='price-stability')
        self.assertIsNotNone(
            price_stability, 
            "Should have a single price-stability element"
        )
    
    def test_redundant_volatility_elements_removed(self):
        """Test that old redundant volatility elements are removed"""
        # Should NOT find separate volatility-index and price-std
        volatility_index = self.soup.find(id='volatility-index')
        price_std = self.soup.find(id='price-std')
        
        self.assertIsNone(
            volatility_index, 
            "Redundant volatility-index element should be removed"
        )
        self.assertIsNone(
            price_std, 
            "Redundant price-std element should be removed"
        )
    
    def test_price_stability_label_exists(self):
        """Test that price stability has proper label"""
        # Find the metric with price stability
        price_stability_metric = None
        for metric in self.soup.find_all(class_='trend-metric'):
            label = metric.find(class_='metric-label')
            if label and 'Price Stability:' in label.get_text():
                price_stability_metric = metric
                break
        
        self.assertIsNotNone(
            price_stability_metric,
            "Should have Price Stability label"
        )
    
    def test_javascript_updates_price_stability(self):
        """Test that JavaScript updates the merged price stability"""
        # Check for JavaScript that updates price-stability element
        script_content = ""
        for script in self.soup.find_all('script'):
            if script.string:
                script_content += script.string
        
        self.assertIn(
            'price-stability',
            script_content,
            "JavaScript should reference price-stability element"
        )
        
        # Should NOT reference old separated elements in main update function
        # Note: They might exist in error handling, so we check main update logic
        main_update_section = script_content.split('function updateTrendSummary')[1].split('function')[0] if 'function updateTrendSummary' in script_content else script_content
        
        self.assertNotIn(
            'volatility-index',
            main_update_section,
            "Main update function should not reference separated volatility-index"
        )


if __name__ == '__main__':
    print("🧪 Testing Price Stability Merge...")
    unittest.main()