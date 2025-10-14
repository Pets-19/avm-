#!/usr/bin/env python3
"""
Test suite for Market Activity consolidation (Volume Trend + Growth Rate merge)
"""

import unittest
import re
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestMarketActivityMerge(unittest.TestCase):
    """Test Market Activity consolidation functionality"""
    
    def setUp(self):
        """Load the HTML template for testing"""
        with open('/workspaces/avm-retyn/templates/index.html', 'r') as f:
            self.html_content = f.read()
    
    def test_market_activity_element_exists(self):
        """Test that unified market-activity element exists"""
        # Should have market-activity element instead of separate volume elements
        self.assertIn('id="market-activity"', self.html_content, 
                     "Should have unified market-activity element")
    
    def test_redundant_volume_elements_removed(self):
        """Test that separate volume-trend and volume-growth elements are removed"""
        # Should not have separate volume elements anymore
        self.assertNotIn('id="volume-trend"', self.html_content,
                        "Redundant volume-trend element should be removed")
        self.assertNotIn('id="volume-growth"', self.html_content,
                        "Redundant volume-growth element should be removed")
    
    def test_market_activity_javascript_integration(self):
        """Test that JavaScript updates market-activity element correctly"""
        # Should reference market-activity in JavaScript
        self.assertIn('market-activity', self.html_content,
                     "JavaScript should reference market-activity element")
        
        # Should not reference old volume elements in JavaScript
        volume_trend_refs = re.findall(r'getElementById\(["\']volume-trend["\']\)', self.html_content)
        volume_growth_refs = re.findall(r'getElementById\(["\']volume-growth["\']\)', self.html_content)
        
        self.assertEqual(len(volume_trend_refs), 0, 
                        "JavaScript should not reference volume-trend element")
        self.assertEqual(len(volume_growth_refs), 0,
                        "JavaScript should not reference volume-growth element")
    
    def test_market_activity_section_header(self):
        """Test that section is properly labeled"""
        # Should have appropriate section label for market activity
        self.assertIn('Market Activity', self.html_content,
                     "Should have Market Activity section or label")

if __name__ == '__main__':
    print("🧪 Testing Market Activity Merge...")
    unittest.main()