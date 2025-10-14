"""
Dubai Property Valuation Engine - Statistical Approach
Uses 130K+ Dubai transaction dataset for automated property valuations
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os

# Cache for dataset to avoid repeated CSV loading
_dataset_cache = None

def load_dubai_dataset():
    """Load Dubai valuation dataset with caching"""
    global _dataset_cache
    
    if _dataset_cache is None:
        csv_path = 'static/valuation_data/Valuation - Dubai.csv'
        if os.path.exists(csv_path):
            _dataset_cache = pd.read_csv(csv_path)
            # Clean and prepare data
            _dataset_cache = _dataset_cache.dropna(subset=['property_total_value', 'actual_area'])
            _dataset_cache = _dataset_cache[_dataset_cache['property_total_value'] > 0]
            _dataset_cache = _dataset_cache[_dataset_cache['actual_area'] > 0]
        else:
            raise FileNotFoundError(f"Dataset not found at {csv_path}")
    
    return _dataset_cache

def find_comparable_properties(property_data, max_comparables=5):
    """Find comparable properties using statistical filtering"""
    df = load_dubai_dataset()
    
    # Start with area filtering
    area_matches = df[df['area_name_en'] == property_data.get('area_name', '')]
    
    # If no area matches, expand to city-wide
    if len(area_matches) < 3:
        area_matches = df
    
    # Filter by property type
    if property_data.get('property_type'):
        type_matches = area_matches[
            area_matches['property_type_en'] == property_data['property_type']
        ]
        if len(type_matches) < 3:
            type_matches = area_matches  # Fallback to all types in area
    else:
        type_matches = area_matches
    
    # Filter by size (±30% of target area)
    target_area = property_data.get('area_sqm', 100)
    size_matches = type_matches[
        (type_matches['actual_area'] >= target_area * 0.7) &
        (type_matches['actual_area'] <= target_area * 1.3)
    ]
    
    if len(size_matches) < 3:
        size_matches = type_matches  # Fallback
    
    # Sort by most recent and take top comparables
    comparables = size_matches.sort_values('instance_date', ascending=False).head(max_comparables)
    
    return comparables

def calculate_confidence_score(property_data, comparables):
    """Calculate confidence score based on comparable quality"""
    if len(comparables) == 0:
        return 70  # Minimum confidence
    
    base_score = 75
    
    # More comparables = higher confidence
    if len(comparables) >= 5:
        base_score += 10
    elif len(comparables) >= 3:
        base_score += 5
    
    # Same area = higher confidence
    same_area_count = len(comparables[comparables['area_name_en'] == property_data.get('area_name', '')])
    if same_area_count > 0:
        base_score += min(same_area_count * 3, 10)
    
    # Recent transactions = higher confidence
    recent_count = len(comparables[comparables['procedure_year'] >= 2023])
    if recent_count > 0:
        base_score += min(recent_count * 2, 8)
    
    return min(base_score, 95)  # Cap at 95%

def calculate_valuation(property_data):
    """
    Main valuation function using statistical analysis
    
    Args:
        property_data (dict): Property details
        {
            'area_sqm': 120.5,
            'property_type': 'Unit', 
            'area_name': 'Business Bay',
            'bedrooms': 2
        }
    
    Returns:
        dict: Valuation result with estimate, confidence, and comparables
    """
    try:
        # Find comparable properties
        comparables = find_comparable_properties(property_data)
        
        if len(comparables) == 0:
            # Fallback to city-wide averages
            df = load_dubai_dataset()
            city_avg_price_per_sqm = df['property_total_value'].sum() / df['actual_area'].sum()
            estimated_value = city_avg_price_per_sqm * property_data.get('area_sqm', 100)
            confidence = 70
        else:
            # Calculate price per sqm from comparables
            comparables['price_per_sqm'] = comparables['property_total_value'] / comparables['actual_area']
            median_price_per_sqm = comparables['price_per_sqm'].median()
            
            # Estimate property value
            estimated_value = median_price_per_sqm * property_data.get('area_sqm', 100)
            
            # Calculate confidence
            confidence = calculate_confidence_score(property_data, comparables)
        
        # Generate value range (±12%)
        margin = estimated_value * 0.12
        
        # Prepare comparable properties for response
        comparable_list = []
        if len(comparables) > 0:
            for _, comp in comparables.head(3).iterrows():
                comparable_list.append({
                    'area_name': comp.get('area_name_en', 'N/A'),
                    'property_type': comp.get('property_type_en', 'N/A'),
                    'area_sqm': float(comp.get('actual_area', 0)),
                    'sold_price': float(comp.get('property_total_value', 0)),
                    'price_per_sqm': float(comp.get('property_total_value', 0) / comp.get('actual_area', 1)),
                    'transaction_year': int(comp.get('procedure_year', 2024))
                })
        
        return {
            'success': True,
            'valuation': {
                'estimated_value': round(estimated_value),
                'confidence_score': round(confidence, 1),
                'price_per_sqm': round(estimated_value / property_data.get('area_sqm', 100)),
                'value_range': {
                    'low': round(estimated_value - margin),
                    'high': round(estimated_value + margin)
                },
                'comparables': comparable_list,
                'total_comparables_found': len(comparables),
                'valuation_date': datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'valuation': None
        }