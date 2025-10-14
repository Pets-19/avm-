#!/usr/bin/env python3
"""
Test for Market Condition Merge Feature
Tests that redundant Trend Direction and Market Status are merged into single Market Condition.
"""

import unittest
from bs4 import BeautifulSoup


class TestMarketConditionMerge(unittest.TestCase):
    """Test market condition consolidation functionality"""
    
    def setUp(self):
        """Load the HTML template for testing"""
        with open('/workspaces/avm-retyn/templates/index.html', 'r') as f:
            self.html_content = f.read()
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
    
    def test_single_market_condition_element_exists(self):
        """Test that single market-condition element exists"""
        market_condition = self.soup.find(id='market-condition')
        self.assertIsNotNone(
            market_condition, 
            "Should have a single market-condition element"
        )
    
    def test_redundant_elements_removed(self):
        """Test that old redundant elements are removed"""
        # Should NOT find separate trend-direction and trend-strength
        trend_direction = self.soup.find(id='trend-direction')
        trend_strength = self.soup.find(id='trend-strength')
        
        self.assertIsNone(
            trend_direction, 
            "Redundant trend-direction element should be removed"
        )
        self.assertIsNone(
            trend_strength, 
            "Redundant trend-strength element should be removed"
        )
    
    def test_market_condition_label_exists(self):
        """Test that market condition has proper label"""
        # Find the metric with market condition
        market_condition_metric = None
        for metric in self.soup.find_all(class_='trend-metric'):
            label = metric.find(class_='metric-label')
            if label and 'Market Condition:' in label.get_text():
                market_condition_metric = metric
                break
        
        self.assertIsNotNone(
            market_condition_metric,
            "Should have Market Condition label"
        )
    
    def test_javascript_updates_market_condition(self):
        """Test that JavaScript updates the merged market condition"""
        # Check for JavaScript that updates market-condition element
        script_content = ""
        for script in self.soup.find_all('script'):
            if script.string:
                script_content += script.string
        
        self.assertIn(
            'market-condition',
            script_content,
            "JavaScript should reference market-condition element"
        )
        
        # Should NOT reference old elements
        self.assertNotIn(
            'trend-direction',
            script_content,
            "JavaScript should not reference removed trend-direction"
        )


if __name__ == '__main__':
    print("🧪 Testing Market Condition Merge...")
    unittest.main()