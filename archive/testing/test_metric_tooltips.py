#!/usr/bin/env python3
"""
Test Interactive Metric Tooltips
Tests for tooltip attributes and content accuracy
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestMetricTooltips(unittest.TestCase):
    
    def test_tooltip_attributes_exist(self):
        """Test that metric divs have data-tooltip attributes"""
        # Read the HTML file
        with open('/workspaces/avm-retyn/templates/index.html', 'r') as f:
            html_content = f.read()
        
        # Check for tooltip attributes on key metrics
        self.assertIn('data-tooltip', html_content, "HTML should contain data-tooltip attributes")
        
        # Check specific enhanced metrics have tooltips
        enhanced_metrics = [
            'price-momentum',
            'avg-monthly-price', 
            'affordability-index'
        ]
        
        for metric in enhanced_metrics:
            with self.subTest(metric=metric):
                # Should find the metric ID and a data-tooltip nearby
                self.assertIn(f'id="{metric}"', html_content, f"Metric {metric} should exist")
                
                # Find the line with the metric and check for tooltip in same section
                lines = html_content.split('\n')
                metric_line_found = False
                tooltip_found = False
                
                for i, line in enumerate(lines):
                    if f'id="{metric}"' in line:
                        metric_line_found = True
                        # Check surrounding lines for data-tooltip
                        for j in range(max(0, i-3), min(len(lines), i+4)):
                            if 'data-tooltip=' in lines[j]:
                                tooltip_found = True
                                break
                        break
                
                self.assertTrue(metric_line_found, f"Metric {metric} should be found in HTML")
                self.assertTrue(tooltip_found, f"Tooltip should be found near metric {metric}")
    
    def test_tooltip_css_exists(self):
        """Test that tooltip CSS styling is present"""
        with open('/workspaces/avm-retyn/templates/index.html', 'r') as f:
            html_content = f.read()
        
        # Should contain tooltip CSS classes
        tooltip_css_indicators = [
            '.tooltip',
            'position: relative',
            'data-tooltip'
        ]
        
        # At least one of these should exist in the CSS section
        css_found = any(indicator in html_content for indicator in tooltip_css_indicators)
        self.assertTrue(css_found, "Tooltip CSS styling should be present")
    
    def test_tooltip_javascript_exists(self):
        """Test that tooltip JavaScript functionality is present"""
        with open('/workspaces/avm-retyn/templates/index.html', 'r') as f:
            html_content = f.read()
        
        # Should contain JavaScript for tooltip handling
        js_indicators = [
            'addEventListener',
            'dblclick',
            'tooltip',
            'data-tooltip'
        ]
        
        # At least one of these should exist in script sections
        js_found = any(indicator in html_content for indicator in js_indicators)
        self.assertTrue(js_found, "Tooltip JavaScript should be present")
    
    def test_tooltip_content_accuracy(self):
        """Test that tooltip explanations are accurate and helpful"""
        with open('/workspaces/avm-retyn/templates/index.html', 'r') as f:
            html_content = f.read()
        
        # Check for meaningful explanation content
        explanation_keywords = [
            'Price Momentum',
            'Affordability Index', 
            'baseline',
            'acceleration',
            'deceleration',
            'calculated'
        ]
        
        for keyword in explanation_keywords:
            with self.subTest(keyword=keyword):
                self.assertIn(keyword, html_content, f"Tooltip should contain explanation about {keyword}")

if __name__ == '__main__':
    print("🧪 Testing Interactive Metric Tooltips...")
    unittest.main(verbosity=2)