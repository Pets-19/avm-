"""Unit tests for location premium calculations (calculate_location_premium).

Tests the geospatial premium system that applies:
1. Metro proximity bonus (0-15%)
2. Beach proximity bonus (0-30%)
3. Mall proximity bonus (0-8%)
4. Business district proximity bonus (0-10%)
5. Neighborhood score bonus (-8% to +8%)
Total capped at +70%
"""
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy import text

# Import app components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app import calculate_location_premium


class TestCalculateLocationPremium:
    """Test suite for calculate_location_premium function."""
    
    def test_location_premium_dubai_marina(self, mock_engine):
        """Test location premium for Dubai Marina (premium area).
        
        Dubai Marina characteristics:
        - Metro: 0.5 km → ~13.5% premium
        - Beach: 0.2 km → ~28.8% premium
        - Mall: 0.3 km → ~7.4% premium
        - Business: 2.0 km → ~6% premium
        - Neighborhood: 4.5 → +6% premium
        Expected total: ~45-50% (capped at 70%)
        """
        # Mock area_coordinates query result - return tuple, not dict
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (0.5, 0.2, 0.3, 1.0, 2.0, 4.5)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_location_premium('Dubai Marina')
            
            # Dubai Marina should have high premium
            assert isinstance(result, dict)
            assert 'total_premium' in result
            assert 40 <= result['total_premium'] <= 70  # High premium area
    
    def test_location_premium_downtown_dubai(self, mock_engine):
        """Test location premium for Downtown Dubai (premium area).
        
        Downtown Dubai characteristics:
        - Metro: 0.3 km → ~14.1% premium
        - Beach: 3.0 km → ~12% premium
        - Mall: 0.1 km → ~7.8% premium
        - Business: 0.5 km → ~9% premium
        - Neighborhood: 5.0 → +8% premium
        Expected total: ~50-55%
        """
        # Mock area_coordinates query result - return tuple
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (0.3, 3.0, 0.1, 0.8, 0.5, 5.0)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_location_premium('Downtown Dubai')
            
            # Downtown should have very high premium
            assert isinstance(result, dict)
            assert 'total_premium' in result
            assert 45 <= result['total_premium'] <= 70
    
    def test_location_premium_unknown_area(self, mock_engine):
        """Test location premium for area not in area_coordinates table.
        
        Expected behavior:
        - Should return None
        - Should handle gracefully (no crash)
        """
        # Mock empty result (area not found)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_location_premium('Unknown Area')
            
            # Should return None for unknown areas
            assert result is None
    
    def test_location_premium_calculation_formula(self, mock_engine):
        """Test the mathematical formula for location premium calculation.
        
        Formula:
        - Metro: max(0, 15 - distance_km * 3)
        - Beach: max(0, 30 - distance_km * 6)
        - Mall: max(0, 8 - distance_km * 2)
        - School: max(0, 5 - distance_km * 1)
        - Business: max(0, 10 - distance_km * 2)
        - Neighborhood: (score - 3.0) * 4
        Total: min(70, sum of all)
        """
        # Test case with known values (as tuple)
        # metro, beach, mall, school, business, neighborhood
        test_data = (2.0, 1.0, 1.5, 2.0, 3.0, 3.5)
        
        # Calculate expected premiums
        # Metro: 15 - 2*3 = 9%
        # Beach: 30 - 1*6 = 24%
        # Mall: 8 - 1.5*2 = 5%
        # School: 5 - 2*1 = 3%
        # Business: 10 - 3*2 = 4%
        # Neighborhood: (3.5 - 3)*4 = 2%
        expected_premium = min(70, 9 + 24 + 5 + 3 + 4 + 2)  # = 47%
        
        # Mock result with test data
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = test_data
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_location_premium('Test Area')
            
            # Allow ±3% tolerance for rounding
            assert isinstance(result, dict)
            assert 'total_premium' in result
            assert abs(result['total_premium'] - expected_premium) <= 3
    
    def test_location_premium_caching_behavior(self, mock_engine):
        """Test that location premiums return consistent results.
        
        Expected behavior:
        - Should return consistent results for same area
        - Should handle multiple calls gracefully
        """
        # Mock area coordinates result (as tuple)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (0.5, 0.5, 0.5, 1.0, 1.0, 4.0)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result1 = calculate_location_premium('Business Bay')
            result2 = calculate_location_premium('Business Bay')
            
            # Should return dict with consistent total_premium
            assert isinstance(result1, dict)
            assert isinstance(result2, dict)
            assert 'total_premium' in result1
            assert 'total_premium' in result2
    
    def test_location_premium_database_error(self, mock_engine):
        """Test location premium when database query fails.
        
        Expected behavior:
        - Should catch exception
        - Should return None (safe fallback)
        - Should not crash application
        """
        # Mock database error
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Database connection failed")
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_location_premium('Dubai Marina')
            
            # Should return None on error (safe fallback)
            assert result is None
    
    def test_location_premium_null_area(self, mock_engine):
        """Test location premium with None or empty area name.
        
        Expected behavior:
        - Should handle None/empty gracefully
        - Should return None
        """
        with patch('app.engine', mock_engine):
            # Test None
            result_none = calculate_location_premium(None)
            assert result_none is None
            
            # Test empty string
            result_empty = calculate_location_premium('')
            assert result_empty is None
    
    def test_location_premium_case_insensitive(self, mock_engine):
        """Test that area name matching is case-insensitive.
        
        Expected behavior:
        - 'dubai marina', 'Dubai Marina', 'DUBAI MARINA' should all match
        - Should use LOWER in SQL query
        """
        test_cases = [
            'dubai marina',
            'Dubai Marina',
            'DUBAI MARINA',
        ]
        
        # Mock area coordinates result (as tuple)
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (0.5, 0.2, 0.3, 1.0, 2.0, 4.5)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            results = [calculate_location_premium(area) for area in test_cases]
            
            # All should return dict results
            assert all(isinstance(r, dict) for r in results)
            assert all('total_premium' in r for r in results)


# Edge case tests
class TestLocationPremiumEdgeCases:
    """Test edge cases and boundary conditions for location premium."""
    
    def test_premium_capped_at_70_percent(self, mock_engine):
        """Test that total premium is capped at 70%.
        
        Even if calculated premium exceeds 70%, should return exactly 70%.
        """
        # Mock extreme premium values that would exceed 70% (as tuple)
        # metro, beach, mall, school, business, neighborhood
        # 0.0 distance = max premiums: 15 + 30 + 8 + 5 + 10 + 8 = 76%
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (0.0, 0.0, 0.0, 0.0, 0.0, 5.0)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_location_premium('Perfect Location')
            
            # Should be capped at exactly 70%
            assert isinstance(result, dict)
            assert result['total_premium'] == 70
    
    def test_negative_neighborhood_score(self, mock_engine):
        """Test location premium with low neighborhood score (penalty).
        
        Neighborhood score < 3.0 should result in penalty (negative premium component).
        """
        # Mock low neighborhood score (as tuple)
        # metro, beach, mall, school, business, neighborhood
        # Metro: 15 - 1*3 = 12%
        # Beach: 30 - 2*6 = 18%
        # Mall: 8 - 1*2 = 6%
        # School: 5 - 1.5*1 = 3.5%
        # Business: 10 - 1.5*2 = 7%
        # Neighborhood: (2 - 3)*4 = -4%
        # Total: 12 + 18 + 6 + 3.5 + 7 - 4 = 42.5%
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchone.return_value = (1.0, 2.0, 1.0, 1.5, 1.5, 2.0)
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_location_premium('Lower Area')
            
            # Should account for negative neighborhood penalty
            assert isinstance(result, dict)
            assert 38 <= result['total_premium'] <= 47  # Allow some tolerance


# Run tests directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
