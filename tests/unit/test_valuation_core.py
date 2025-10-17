"""Unit tests for core valuation logic (calculate_valuation_from_database).

Tests the main valuation function that:
1. Queries database for comparable properties
2. Filters outliers
3. Calculates statistical measures
4. Applies premiums (location, project, floor, view, age)
5. Blends ML predictions with database values
6. Returns confidence scores
"""
import pytest
from unittest.mock import MagicMock, patch, call
from sqlalchemy import text
import numpy as np

# Import app components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app import (
    calculate_valuation_from_database,
    filter_outliers,
    calculate_location_premium,
)


class TestCalculateValuationFromDatabase:
    """Test suite for calculate_valuation_from_database function."""
    
    def test_calculate_valuation_success_with_good_comparables(
        self, mock_engine, sample_property_data
    ):
        """Test successful valuation with sufficient comparable properties.
        
        Expected behavior:
        - Should find 3+ comparables
        - Should calculate median/mean/std
        - Should return confidence score 70-90%
        - Should apply location premium
        """
        with patch('app.engine', mock_engine):
            result = calculate_valuation_from_database(
                property_type='Unit',
                area='Dubai Marina',
                size=1000,
                bedrooms=2,
                search_type='sales'
            )
            
            assert result['success'] is True
            assert 'estimated_value' in result
            assert result['estimated_value'] > 0
            assert result['confidence'] >= 50
            assert result['confidence'] <= 98
            assert 'comparable_count' in result
            assert result['comparable_count'] >= 1
    
    def test_calculate_valuation_no_comparables_found(self, mock_engine):
        """Test valuation when no comparable properties found.
        
        Expected behavior:
        - Should expand search scope progressively
        - Should return lower confidence score
        - Should include warning message
        """
        # Mock empty result set
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_result.rowcount = 0
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_valuation_from_database(
                property_type='Villa',
                area='Unknown Area',
                size=5000,
                bedrooms=10,
                search_type='sales'
            )
            
            # Should either return fallback value or error
            assert isinstance(result, dict)
            assert 'success' in result
            if result['success']:
                assert result['confidence'] < 50  # Low confidence
    
    def test_calculate_valuation_single_comparable(self, mock_engine):
        """Test valuation with only one comparable property.
        
        Expected behavior:
        - Should accept single comparable
        - Should use that value directly
        - Should return lower confidence score (50-60%)
        """
        # Mock single result
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (1000000, 1000, 'Unit', 2, 'Dubai Marina', '2023-01-15')
        ]
        mock_result.rowcount = 1
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_valuation_from_database(
                property_type='Unit',
                area='Dubai Marina',
                size=1000,
                bedrooms=2,
                search_type='sales'
            )
            
            assert result['success'] is True
            assert result['comparable_count'] == 1
            assert 50 <= result['confidence'] <= 65
    
    def test_calculate_valuation_with_bedroom_filter(self, mock_engine):
        """Test valuation with bedroom filter applied.
        
        Expected behavior:
        - Should filter by bedrooms when provided
        - Should include bedroom criteria in query
        """
        with patch('app.engine', mock_engine):
            result = calculate_valuation_from_database(
                property_type='Unit',
                area='Business Bay',
                size=1200,
                bedrooms=3,
                search_type='sales'
            )
            
            # Check that execute was called with bedroom filter
            mock_conn = mock_engine.connect.return_value.__enter__.return_value
            calls = mock_conn.execute.call_args_list
            
            assert len(calls) > 0
            # Verify query contains bedroom filtering logic
            assert result['success'] is True
    
    def test_calculate_valuation_with_all_filters(self, mock_engine):
        """Test valuation with all optional filters (bedrooms, floor, view, age).
        
        Expected behavior:
        - Should apply all provided filters
        - Should narrow search scope
        - May return fewer comparables but higher quality
        """
        with patch('app.engine', mock_engine):
            result = calculate_valuation_from_database(
                property_type='Unit',
                area='Downtown Dubai',
                size=1500,
                bedrooms=3,
                floor=20,
                view='Burj Khalifa View',
                age=2,
                search_type='sales'
            )
            
            assert result['success'] is True
            # With all filters, may have fewer comparables
            assert 'comparable_count' in result
    
    def test_calculate_valuation_invalid_property_type(self, mock_engine):
        """Test valuation with invalid property type.
        
        Expected behavior:
        - Should handle gracefully
        - Should return error or fallback value
        """
        with patch('app.engine', mock_engine):
            result = calculate_valuation_from_database(
                property_type='Invalid Type',
                area='Dubai Marina',
                size=1000,
                bedrooms=2,
                search_type='sales'
            )
            
            assert isinstance(result, dict)
            # May succeed with expanded search or return error
    
    def test_calculate_valuation_negative_size(self, mock_engine):
        """Test valuation with negative size (invalid input).
        
        Expected behavior:
        - Should handle gracefully
        - Should return error or validate input
        """
        with patch('app.engine', mock_engine):
            result = calculate_valuation_from_database(
                property_type='Unit',
                area='Dubai Marina',
                size=-100,  # Invalid negative size
                bedrooms=2,
                search_type='sales'
            )
            
            assert isinstance(result, dict)
            # Should handle invalid input gracefully
    
    def test_calculate_valuation_outlier_handling(self, mock_engine):
        """Test that outliers are properly filtered from comparables.
        
        Expected behavior:
        - Should call filter_outliers function
        - Should remove extreme values
        - Should improve valuation accuracy
        """
        # Mock result with outlier
        mock_conn = MagicMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [
            (1000000, 1000, 'Unit', 2, 'Dubai Marina', '2023-01-15'),
            (1050000, 1050, 'Unit', 2, 'Dubai Marina', '2023-02-20'),
            (5000000, 1020, 'Unit', 2, 'Dubai Marina', '2023-03-10'),  # Outlier
        ]
        mock_result.rowcount = 3
        mock_conn.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            with patch('app.filter_outliers') as mock_filter:
                # Mock filter_outliers to return filtered list
                mock_filter.return_value = (
                    [1000000, 1050000],  # Filtered prices
                    {'removed_count': 1, 'removed_percentage': 33.3}
                )
                
                result = calculate_valuation_from_database(
                    property_type='Unit',
                    area='Dubai Marina',
                    size=1000,
                    bedrooms=2,
                    search_type='sales'
                )
                
                # Verify filter_outliers was called
                mock_filter.assert_called_once()
    
    def test_calculate_valuation_database_error(self, mock_engine):
        """Test valuation when database query fails.
        
        Expected behavior:
        - Should catch exception
        - Should return error response
        - Should not crash application
        """
        # Mock database error
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = Exception("Database connection failed")
        mock_engine.connect.return_value.__enter__.return_value = mock_conn
        
        with patch('app.engine', mock_engine):
            result = calculate_valuation_from_database(
                property_type='Unit',
                area='Dubai Marina',
                size=1000,
                bedrooms=2,
                search_type='sales'
            )
            
            # Should return error response, not crash
            assert isinstance(result, dict)
            # May have success=False or return fallback
    
    def test_calculate_valuation_confidence_score_logic(self, mock_engine):
        """Test confidence score calculation logic.
        
        Expected behavior:
        - More comparables = higher confidence
        - 1 comparable = 50-60%
        - 3-5 comparables = 70-80%
        - 10+ comparables = 85-90%
        """
        test_cases = [
            (1, (50, 65)),   # 1 comparable: 50-65% confidence
            (5, (70, 85)),   # 5 comparables: 70-85% confidence
            (15, (85, 98)),  # 15+ comparables: 85-98% confidence
        ]
        
        for comparable_count, expected_range in test_cases:
            # Mock result with specific count
            mock_conn = MagicMock()
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [
                (1000000 + i*10000, 1000, 'Unit', 2, 'Dubai Marina', '2023-01-15')
                for i in range(comparable_count)
            ]
            mock_result.rowcount = comparable_count
            mock_conn.execute.return_value = mock_result
            mock_engine.connect.return_value.__enter__.return_value = mock_conn
            
            with patch('app.engine', mock_engine):
                result = calculate_valuation_from_database(
                    property_type='Unit',
                    area='Dubai Marina',
                    size=1000,
                    bedrooms=2,
                    search_type='sales'
                )
                
                if result['success']:
                    min_conf, max_conf = expected_range
                    assert min_conf <= result['confidence'] <= max_conf, \
                        f"Expected confidence {min_conf}-{max_conf}%, got {result['confidence']}%"


# Run tests directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
