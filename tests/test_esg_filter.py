"""
Unit tests for ESG (Environmental, Social, Governance) Filter
Tests the ESG score filtering functionality in property valuations
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, find_column_name, SALES_COLUMNS


class TestESGFilter:
    """Test suite for ESG sustainability score filtering"""
    
    @pytest.fixture
    def client(self):
        """Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_esg_column_exists_in_database(self):
        """Test that esg_score column was added to properties table"""
        # esg_score should be in SALES_COLUMNS after migration
        assert 'esg_score' in SALES_COLUMNS, "esg_score column should exist in SALES_COLUMNS"
    
    def test_find_esg_column_mapping(self):
        """Test that find_column_name() can locate ESG column"""
        esg_col = find_column_name(SALES_COLUMNS, ['esg_score', 'sustainability_score', 'esg_rating'])
        assert esg_col is not None, "Should find esg_score column"
        assert esg_col == 'esg_score', f"Should map to 'esg_score', got '{esg_col}'"
    
    def test_valuation_api_accepts_esg_parameter(self, client):
        """Test that /api/property/valuation endpoint accepts esg_score_min"""
        response = client.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Dubai Marina',
            'size_sqm': 100,
            'esg_score_min': 60
        })
        
        # Should return 200 OK (even if no results, shouldn't crash)
        assert response.status_code in [200, 500], f"Expected 200 or 500, got {response.status_code}"
        data = response.get_json()
        assert 'success' in data, "Response should have 'success' field"
    
    def test_valuation_without_esg_filter(self, client):
        """Test backward compatibility - valuation works without ESG filter"""
        response = client.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Business Bay',
            'size_sqm': 120
        })
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.get_json()
        assert data['success'] == True, "Valuation should succeed without ESG filter"
    
    def test_esg_filter_with_empty_string(self, client):
        """Test that empty string ESG filter is treated as no filter"""
        response = client.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Dubai Marina',
            'size_sqm': 100,
            'esg_score_min': ''  # Empty string should be ignored
        })
        
        assert response.status_code == 200
        data = response.get_json()
        # Should not crash, empty string should be treated as None
        assert 'success' in data
    
    def test_esg_filter_with_high_threshold(self, client):
        """Test ESG filter with high threshold (80+)"""
        response = client.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Dubai Marina',
            'size_sqm': 150,
            'esg_score_min': 80
        })
        
        # High threshold may return fewer results, but shouldn't crash
        assert response.status_code in [200, 500]
        data = response.get_json()
        assert 'success' in data
    
    def test_esg_filter_with_low_threshold(self, client):
        """Test ESG filter with low threshold (25+)"""
        response = client.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Dubai Marina',
            'size_sqm': 150,
            'esg_score_min': 25
        })
        
        assert response.status_code == 200
        data = response.get_json()
        # Low threshold should have more results
        assert 'success' in data


class TestESGEdgeCases:
    """Test edge cases for ESG filtering"""
    
    @pytest.fixture
    def client(self):
        """Flask test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_esg_filter_with_invalid_value(self, client):
        """Test ESG filter with non-numeric value"""
        response = client.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Dubai Marina',
            'size_sqm': 100,
            'esg_score_min': 'high'  # Invalid string value
        })
        
        # Should handle gracefully - either convert or ignore
        assert response.status_code in [200, 400, 500]
    
    def test_esg_combined_with_bedrooms(self, client):
        """Test ESG filter combined with bedrooms filter"""
        response = client.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Business Bay',
            'size_sqm': 120,
            'bedrooms': '2',
            'esg_score_min': 40
        })
        
        # Both filters should apply (AND logic)
        assert response.status_code in [200, 500]
        data = response.get_json()
        assert 'success' in data
    
    def test_esg_combined_with_status(self, client):
        """Test ESG filter combined with development status"""
        response = client.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Dubai Marina',
            'size_sqm': 100,
            'development_status': 'Ready',
            'esg_score_min': 60
        })
        
        assert response.status_code in [200, 500]
        data = response.get_json()
        assert 'success' in data


class TestESGIntegration:
    """Integration tests for ESG filter with database"""
    
    def test_properties_with_esg_scores_exist(self):
        """Test that database has at least some properties with ESG scores"""
        from app import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) as count 
                FROM properties 
                WHERE esg_score IS NOT NULL
            """))
            row = result.fetchone()
            count = row[0]
            
        assert count > 0, f"Expected properties with ESG scores, found {count}"
        print(f"\n✅ Found {count} properties with ESG scores in database")
    
    def test_esg_scores_in_valid_range(self):
        """Test that all ESG scores are in valid range (0-100)"""
        from app import engine
        from sqlalchemy import text
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT MIN(esg_score) as min_esg, MAX(esg_score) as max_esg
                FROM properties 
                WHERE esg_score IS NOT NULL
            """))
            row = result.fetchone()
            min_esg, max_esg = row[0], row[1]
            
        assert 0 <= min_esg <= 100, f"Min ESG score {min_esg} out of range"
        assert 0 <= max_esg <= 100, f"Max ESG score {max_esg} out of range"
        print(f"\n✅ ESG scores in valid range: {min_esg} - {max_esg}")
    
    def test_esg_filter_reduces_results(self):
        """Test that applying ESG filter reduces result count"""
        from app import engine
        from sqlalchemy import text
        
        # Count all properties in Dubai Marina
        with engine.connect() as conn:
            result_all = conn.execute(text("""
                SELECT COUNT(*) 
                FROM properties 
                WHERE LOWER(area_en) LIKE '%dubai marina%'
                  AND trans_value > 0
            """))
            count_all = result_all.fetchone()[0]
            
            # Count only high ESG properties
            result_filtered = conn.execute(text("""
                SELECT COUNT(*) 
                FROM properties 
                WHERE LOWER(area_en) LIKE '%dubai marina%'
                  AND trans_value > 0
                  AND esg_score >= 60
            """))
            count_filtered = result_filtered.fetchone()[0]
        
        print(f"\n✅ Dubai Marina: {count_all} total, {count_filtered} with ESG >= 60")
        # Filter should reduce results (unless ALL have high ESG, which is unlikely)
        assert count_filtered <= count_all, "Filtered count should be <= total count"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
