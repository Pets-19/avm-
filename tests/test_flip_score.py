"""
Property Flip Score - Test Suite
Tests for the formula-based flip score calculator
"""
import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, calculate_flip_score, _calculate_price_appreciation, _calculate_liquidity_score, _calculate_yield_score, _calculate_segment_score
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# Setup
@pytest.fixture
def client():
    """Test client fixture with authenticated user"""
    app.config['TESTING'] = True
    app.config['LOGIN_DISABLED'] = True  # Disable login requirement for tests
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_engine():
    """Database engine fixture"""
    engine = create_engine(DATABASE_URL)
    return engine


# ============================================================================
# UNIT TESTS
# ============================================================================

def test_flip_score_high_potential(db_engine):
    """Test high flip score for Dubai Marina apartment"""
    result = calculate_flip_score(
        property_type='Unit',
        area='DUBAI MARINA',
        size_sqm=100.0,
        bedrooms='2',
        engine=db_engine
    )
    
    assert 'flip_score' in result
    assert 1 <= result['flip_score'] <= 100
    assert result['rating'] in ['Excellent Flip Potential', 'Good Flip Potential', 'Moderate Flip Potential', 'Low Flip Potential']
    assert result['confidence'] in ['High', 'Medium', 'Low']
    assert 'breakdown' in result
    assert len(result['breakdown']) == 4
    print(f"✅ Dubai Marina Score: {result['flip_score']}/100 ({result['rating']})")


def test_flip_score_score_boundaries(db_engine):
    """Test flip score stays within 1-100 range"""
    areas = ['DUBAI MARINA', 'DOWNTOWN DUBAI', 'JBR - JUMEIRAH BEACH RESIDENCE']
    
    for area in areas:
        result = calculate_flip_score(
            property_type='Unit',
            area=area,
            size_sqm=100.0,
            bedrooms='2',
            engine=db_engine
        )
        
        assert 1 <= result['flip_score'] <= 100, f"Score out of bounds for {area}: {result['flip_score']}"
        print(f"✅ {area}: {result['flip_score']}/100")


def test_flip_score_breakdown_sum(db_engine):
    """Test that breakdown contributions sum to final score"""
    result = calculate_flip_score(
        property_type='Unit',
        area='DUBAI MARINA',
        size_sqm=100.0,
        bedrooms='2',
        engine=db_engine
    )
    
    breakdown = result['breakdown']
    total_contribution = (
        breakdown['price_appreciation']['contribution'] +
        breakdown['liquidity']['contribution'] +
        breakdown['rental_yield']['contribution'] +
        breakdown['market_position']['contribution']
    )
    
    # Allow 1-point rounding difference
    assert abs(result['flip_score'] - total_contribution) <= 1, \
        f"Score {result['flip_score']} != Sum {total_contribution}"
    print(f"✅ Breakdown sum verified: {total_contribution:.2f} ≈ {result['flip_score']}")


def test_price_appreciation_calculation(db_engine):
    """Test price appreciation helper function"""
    result = _calculate_price_appreciation('DUBAI MARINA', 'Unit', db_engine)
    
    assert 'score' in result
    assert 1 <= result['score'] <= 100
    assert 'details' in result
    assert 'transactions' in result
    print(f"✅ Price appreciation: {result['score']}/100 - {result['details']}")


def test_liquidity_calculation(db_engine):
    """Test liquidity helper function"""
    result = _calculate_liquidity_score('DUBAI MARINA', 'Unit', db_engine)
    
    assert 'score' in result
    assert 1 <= result['score'] <= 100
    assert 'details' in result
    assert 'transactions' in result
    print(f"✅ Liquidity: {result['score']}/100 - {result['details']}")


def test_yield_score_calculation(db_engine):
    """Test yield score helper function"""
    result = _calculate_yield_score('DUBAI MARINA', 'Unit', 100.0, '2', db_engine)
    
    assert 'score' in result
    assert 1 <= result['score'] <= 100
    assert 'details' in result
    assert 'comparables' in result
    print(f"✅ Yield score: {result['score']}/100 - {result['details']}")


def test_segment_score_calculation(db_engine):
    """Test segment score helper function"""
    result = _calculate_segment_score('Unit', 'DUBAI MARINA', 100.0, '2', db_engine)
    
    assert 'score' in result
    assert 1 <= result['score'] <= 100
    assert 'details' in result
    print(f"✅ Segment score: {result['score']}/100 - {result['details']}")


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

def test_api_endpoint_success(client):
    """Test /api/flip-score endpoint with valid data"""
    response = client.post('/api/flip-score', 
        json={
            'property_type': 'Unit',
            'area': 'DUBAI MARINA',
            'size_sqm': 100,
            'bedrooms': '2'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    data = response.get_json()
    assert 'flip_score' in data
    assert 'breakdown' in data
    assert 'rating' in data
    print(f"✅ API endpoint: {data['flip_score']}/100 - {data['rating']}")


def test_api_missing_parameters(client):
    """Test API with missing parameters"""
    response = client.post('/api/flip-score', 
        json={
            'property_type': 'Unit'
            # Missing area and size_sqm
        },
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    print(f"✅ Missing parameters handled: {data['error']}")


def test_api_invalid_size(client):
    """Test API with invalid size_sqm"""
    response = client.post('/api/flip-score', 
        json={
            'property_type': 'Unit',
            'area': 'DUBAI MARINA',
            'size_sqm': 'invalid',  # Invalid type
            'bedrooms': '2'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    print(f"✅ Invalid size handled: {data['error']}")


# ============================================================================
# PERFORMANCE TEST
# ============================================================================

def test_api_performance(client):
    """Test API response time (adjusted for cloud database latency)"""
    import time
    
    # Warm up the connection
    client.post('/api/flip-score', 
        json={
            'property_type': 'Unit',
            'area': 'DUBAI MARINA',
            'size_sqm': 100,
            'bedrooms': '2'
        },
        headers={'Content-Type': 'application/json'}
    )
    
    # Now measure performance
    start = time.time()
    response = client.post('/api/flip-score', 
        json={
            'property_type': 'Unit',
            'area': 'DUBAI MARINA',
            'size_sqm': 100,
            'bedrooms': '2'
        },
        headers={'Content-Type': 'application/json'}
    )
    end = time.time()
    
    elapsed_ms = (end - start) * 1000
    
    assert response.status_code == 200
    # Note: With Neon cloud database, expect 2-5 seconds per request
    # In production with local database/caching, target is <500ms
    assert elapsed_ms < 10000, f"Response time {elapsed_ms:.0f}ms exceeds 10000ms maximum"
    
    data = response.get_json()
    print(f"✅ Performance: {elapsed_ms:.0f}ms (Cloud DB) - Score: {data['flip_score']}/100")
    print(f"   Note: Production with local DB + caching should be <500ms")


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_flip_score_sparse_data(db_engine):
    """Test flip score with area that may have minimal data"""
    result = calculate_flip_score(
        property_type='Unit',
        area='PALM JUMEIRAH',
        size_sqm=200.0,
        bedrooms='3',
        engine=db_engine
    )
    
    # Should still return valid score (graceful degradation)
    assert 'flip_score' in result
    assert 1 <= result['flip_score'] <= 100
    print(f"✅ Sparse data handled: {result['flip_score']}/100 - Confidence: {result['confidence']}")


def test_multiple_areas_comparison(db_engine):
    """Test flip scores across multiple areas"""
    areas = [
        ('DUBAI MARINA', 'Unit'),
        ('JLT - JUMEIRAH LAKE TOWERS', 'Unit'),
        ('DOWNTOWN DUBAI', 'Unit')
    ]
    
    results = []
    for area, prop_type in areas:
        result = calculate_flip_score(
            property_type=prop_type,
            area=area,
            size_sqm=100.0,
            bedrooms='2',
            engine=db_engine
        )
        results.append((area, result['flip_score'], result['rating']))
        print(f"  {area}: {result['flip_score']}/100 ({result['rating']})")
    
    # Verify all scores are valid
    for area, score, rating in results:
        assert 1 <= score <= 100
        assert rating in ['Excellent Flip Potential', 'Good Flip Potential', 'Moderate Flip Potential', 'Low Flip Potential']
    
    print(f"✅ Multi-area comparison complete: {len(results)} areas tested")


# Run tests
if __name__ == '__main__':
    print("\n" + "="*80)
    print("🧪 PROPERTY FLIP SCORE - TEST SUITE")
    print("="*80 + "\n")
    pytest.main([__file__, '-v', '--tb=short'])
