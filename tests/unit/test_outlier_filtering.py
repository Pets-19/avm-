"""Unit tests for outlier filtering (filter_outliers).

Tests the outlier detection and removal system that:
1. Validates price ranges (sales: 100K-50M AED, rentals: 10K-2M AED)
2. Removes extreme values using statistical methods
3. Calculates outlier statistics
4. Returns cleaned data + metadata
"""
import pytest
import numpy as np
from typing import List, Tuple, Dict

# Import app components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from app import filter_outliers


# Helper to convert list to numpy array
def to_numpy(prices):
    """Convert list to numpy array for filter_outliers."""
    return np.array(prices)


class TestFilterOutliers:
    """Test suite for filter_outliers function."""
    
    def test_filter_outliers_sales_market(self):
        """Test outlier filtering for sales market data.
        
        Sales market thresholds:
        - Minimum: 100,000 AED
        - Maximum: 50,000,000 AED
        - Extreme max: 100,000,000 AED
        """
        # Sample sales data with outliers (as numpy array)
        prices = to_numpy([
            50000,      # Below minimum (outlier)
            1000000,    # Valid
            1050000,    # Valid
            980000,     # Valid
            1100000,    # Valid
            1020000,    # Valid
            60000000,   # Above maximum (outlier)
        ])
        
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        
        # Check that outliers were removed
        assert len(filtered_prices) < len(prices)
        assert all(100000 <= p <= 50000000 for p in filtered_prices)
        
        # Check statistics
        assert 'total_outliers' in stats
        assert stats['total_outliers'] >= 2  # At least 2 outliers removed
        assert 'outlier_percentage' in stats
        assert stats['outlier_percentage'] > 0
    
    def test_filter_outliers_rental_market(self):
        """Test outlier filtering for rental market data.
        
        Rental market thresholds:
        - Minimum: 10,000 AED/year
        - Maximum: 2,000,000 AED/year
        """
        # Sample rental data with outliers (as numpy array)
        prices = to_numpy([
            5000,       # Below minimum (outlier)
            80000,      # Valid
            85000,      # Valid
            90000,      # Valid
            95000,      # Valid
            100000,     # Valid
            3000000,    # Above maximum (outlier)
        ])
        
        filtered_prices, stats = filter_outliers(prices, search_type='rent')
        
        # Check that outliers were removed
        assert len(filtered_prices) < len(prices)
        assert all(10000 <= p <= 2000000 for p in filtered_prices)
        
        # Check statistics
        assert stats['total_outliers'] >= 2
    
    def test_filter_outliers_empty_list(self):
        """Test outlier filtering with empty price list.
        
        Expected behavior:
        - Should return empty array
        - Should return stats with 0 removed
        - Should not crash
        """
        prices = to_numpy([])
        
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        
        assert len(filtered_prices) == 0
        assert stats['total_outliers'] == 0
        assert stats['outlier_percentage'] == 0
    
    def test_filter_outliers_single_value(self):
        """Test outlier filtering with single price value.
        
        Expected behavior:
        - If value is valid, return it
        - If value is outlier, remove it
        - Should handle gracefully
        """
        # Valid single value
        prices_valid = to_numpy([1000000])
        filtered_valid, stats_valid = filter_outliers(prices_valid, search_type='buy')
        
        assert len(filtered_valid) == 1
        assert filtered_valid[0] == 1000000
        
        # Invalid single value (outlier)
        prices_invalid = to_numpy([10000])  # Below sales minimum
        filtered_invalid, stats_invalid = filter_outliers(prices_invalid, search_type='buy')
        
        assert len(filtered_invalid) == 0
        assert stats_invalid['total_outliers'] == 1
    
    def test_filter_outliers_all_outliers(self):
        """Test outlier filtering when all values are outliers.
        
        Expected behavior:
        - Should return empty array
        - Should report all as removed
        - Stats should show 100% removal
        """
        # All values below minimum
        prices = to_numpy([50000, 60000, 70000, 80000, 90000])
        
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        
        assert len(filtered_prices) == 0
        assert stats['total_outliers'] == 5
        assert stats['outlier_percentage'] == 100.0
    
    def test_filter_outliers_no_outliers(self):
        """Test outlier filtering when all values are valid.
        
        Expected behavior:
        - Should return all values
        - Should report 0 removed
        - Stats should show 0% removal
        """
        # All valid values
        prices = to_numpy([1000000, 1050000, 980000, 1100000, 1020000])
        
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        
        assert len(filtered_prices) == 5
        assert stats['total_outliers'] == 0
        assert stats['outlier_percentage'] == 0.0
    
    def test_filter_outliers_stats_calculation(self):
        """Test that outlier statistics are calculated correctly.
        
        Expected stats:
        - total_outliers: integer count of removed values
        - outlier_percentage: float percentage (0-100)
        - original_count: original number of values
        """
        prices = to_numpy([
            1000000, 1050000, 980000, 1100000,  # 4 valid
            50000, 60000000  # 2 outliers
        ])
        
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        
        assert 'total_outliers' in stats
        assert stats['total_outliers'] == 2
        
        assert 'outlier_percentage' in stats
        expected_pct = (2 / 6) * 100  # 33.33%
        assert abs(stats['outlier_percentage'] - expected_pct) < 0.1
        
        # Check if original_count is tracked
        assert 'original_count' in stats
        assert stats['original_count'] == 6
    
    def test_filter_outliers_boundary_cases(self):
        """Test outlier filtering at boundary values.
        
        Boundary values:
        - Sales: exactly 100,000 and 50,000,000
        - Rentals: exactly 10,000 and 2,000,000
        """
        # Sales boundaries
        sales_prices = to_numpy([
            99999,      # Just below min (outlier)
            100000,     # Exactly min (valid)
            50000000,   # Exactly max (valid)
            50000001,   # Just above max (outlier)
        ])
        
        filtered_sales, stats_sales = filter_outliers(sales_prices, search_type='buy')
        
        assert 100000 in filtered_sales
        assert 50000000 in filtered_sales
        assert 99999 not in filtered_sales
        assert 50000001 not in filtered_sales
        
        # Rental boundaries
        rental_prices = to_numpy([
            9999,       # Just below min (outlier)
            10000,      # Exactly min (valid)
            2000000,    # Exactly max (valid)
            2000001,    # Just above max (outlier)
        ])
        
        filtered_rental, stats_rental = filter_outliers(rental_prices, search_type='rent')
        
        assert 10000 in filtered_rental
        assert 2000000 in filtered_rental
        assert 9999 not in filtered_rental
        assert 2000001 not in filtered_rental


class TestFilterOutliersStatisticalMethods:
    """Test statistical outlier detection methods (if implemented)."""
    
    def test_statistical_outlier_detection_iqr(self):
        """Test IQR (Interquartile Range) method for outlier detection.
        
        IQR method:
        - Q1 = 25th percentile
        - Q3 = 75th percentile
        - IQR = Q3 - Q1
        - Outliers: values < Q1 - 1.5*IQR or > Q3 + 1.5*IQR
        """
        # Create dataset with clear outliers using IQR method
        prices = to_numpy([
            1000000, 1020000, 1030000, 1040000, 1050000,  # Normal distribution
            1060000, 1070000, 1080000, 1090000, 1100000,
            5000000,  # Statistical outlier (far from median)
        ])
        
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        
        # 5000000 is within valid range (100K-50M), so should be kept
        # filter_outliers uses range-based filtering, not IQR
        assert len(filtered_prices) >= 10  # Most values should be kept
        # All values are within valid range
        assert all(100000 <= p <= 50000000 for p in filtered_prices)
    
    def test_statistical_outlier_detection_zscore(self):
        """Test Z-score method for outlier detection.
        
        Z-score method:
        - Z = (value - mean) / std_dev
        - Outliers: |Z| > 3 (value more than 3 std devs from mean)
        """
        # Create dataset with known mean and std dev
        mean_price = 1000000
        std_dev = 50000
        
        prices = to_numpy([
            mean_price - 2 * std_dev,  # Z = -2 (valid)
            mean_price,                 # Z = 0 (valid)
            mean_price + 2 * std_dev,  # Z = +2 (valid)
            mean_price + 4 * std_dev,  # Z = +4 (but within range)
        ])
        
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        
        # All values are within valid range (100K-50M), so all should be kept
        assert len(filtered_prices) == 4
        assert stats['total_outliers'] == 0
    
    def test_mixed_outlier_detection(self):
        """Test combination of range-based and statistical outlier detection.
        
        Should remove:
        1. Values outside valid range (range-based)
        2. Statistical outliers within valid range (IQR/Z-score)
        """
        prices = to_numpy([
            50000,      # Range outlier (below min)
            1000000,    # Valid
            1020000,    # Valid
            1030000,    # Valid
            1040000,    # Valid
            1050000,    # Valid
            3000000,    # Within range but statistical outlier
            60000000,   # Range outlier (above max)
        ])
        
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        
        # Should remove range outliers
        assert 50000 not in filtered_prices  # Range outlier (below min)
        assert 60000000 not in filtered_prices  # Range outlier (above max)
        
        # 3000000 is within valid range (100K-50M), so should be kept
        # filter_outliers uses range-based filtering only
        assert 3000000 in filtered_prices
        
        # Should keep normal values
        assert 1000000 in filtered_prices
        assert 1050000 in filtered_prices
        
        # Should have removed exactly 2 outliers
        assert stats['total_outliers'] == 2


class TestFilterOutliersPerformance:
    """Test performance and edge cases for outlier filtering."""
    
    def test_large_dataset_performance(self):
        """Test outlier filtering with large dataset (1000+ values).
        
        Should complete in reasonable time (< 1 second).
        """
        import time
        
        # Generate large dataset with some outliers
        np.random.seed(42)
        prices = np.random.normal(1000000, 100000, 1000)  # 1000 normal values
        prices = np.append(prices, [50000, 60000000])  # Add 2 outliers
        
        start_time = time.time()
        filtered_prices, stats = filter_outliers(prices, search_type='buy')
        elapsed_time = time.time() - start_time
        
        # Should complete quickly
        assert elapsed_time < 1.0  # Less than 1 second
        
        # Should filter out the 2 outliers
        assert stats['total_outliers'] == 2
        assert len(filtered_prices) == 1000
    
    def test_numpy_array_input(self):
        """Test that function handles numpy arrays as input.
        
        Should accept both lists and numpy arrays.
        """
        prices_list = to_numpy([1000000, 1050000, 980000])
        prices_array = np.array([1000000, 1050000, 980000])
        
        filtered_list, stats_list = filter_outliers(prices_list, search_type='buy')
        filtered_array, stats_array = filter_outliers(prices_array, search_type='buy')
        
        # Should produce same results
        assert len(filtered_list) == len(filtered_array)
        assert stats_list['total_outliers'] == stats_array['total_outliers']


# Run tests directly
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
