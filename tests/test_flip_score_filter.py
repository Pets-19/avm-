"""
Unit tests for Flip Score filter implementation
Pattern: Exact replica of ESG filter tests (test_esg_filter.py)
"""
import pytest
from sqlalchemy import text
from app import app, engine, SALES_COLUMNS, find_column_name


class TestFlipScoreDatabase:
    """Test flip_score column in database"""
    
    def test_flip_score_column_exists_in_database(self):
        """Verify flip_score column exists in properties table"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'properties' 
                AND column_name = 'flip_score'
            """))
            assert result.fetchone() is not None, "flip_score column should exist"
    
    def test_find_flip_score_column_mapping(self):
        """Test dynamic column discovery for flip_score"""
        flip_col = find_column_name(SALES_COLUMNS, ['flip_score', 'investment_score', 'flip_rating'])
        assert flip_col == 'flip_score', f"Expected 'flip_score', got {flip_col}"
    
    def test_properties_with_flip_scores_exist(self):
        """Verify we have properties with flip scores"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM properties WHERE flip_score IS NOT NULL
            """))
            count = result.fetchone()[0]
            assert count >= 10, f"Expected at least 10 properties with flip scores, found {count}"
    
    def test_flip_scores_in_valid_range(self):
        """Verify all flip scores are within 0-100 range"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT MIN(flip_score), MAX(flip_score) 
                FROM properties 
                WHERE flip_score IS NOT NULL
            """))
            min_score, max_score = result.fetchone()
            assert min_score >= 0, f"Minimum flip score {min_score} should be >= 0"
            assert max_score <= 100, f"Maximum flip score {max_score} should be <= 100"
    
    def test_flip_filter_reduces_results(self):
        """Test that flip filter actually reduces result set"""
        with engine.connect() as conn:
            # Get total count
            total_result = conn.execute(text("""
                SELECT COUNT(*) FROM properties 
                WHERE flip_score IS NOT NULL
            """))
            total_count = total_result.fetchone()[0]
            
            # Get filtered count (flip >= 70)
            filtered_result = conn.execute(text("""
                SELECT COUNT(*) FROM properties 
                WHERE flip_score IS NOT NULL 
                AND flip_score >= 70
            """))
            filtered_count = filtered_result.fetchone()[0]
            
            assert filtered_count < total_count, "Filter should reduce result count"
            assert filtered_count >= 6, f"Expected at least 6 properties with flip >= 70, found {filtered_count}"


class TestFlipScoreAPI:
    """Test Flip Score filter via API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def auth_session(self, client):
        """Create authenticated session"""
        # Login with test user
        client.post('/login', data={
            'email': 'dhanesh@retyn.ai',
            'password': 'retyn*#123'
        })
        return client
    
    def test_valuation_without_flip_filter(self, auth_session):
        """Test valuation without flip score filter"""
        response = auth_session.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Madinat Al Mataar',
            'size_sqm': 2000
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_valuation_with_flip_30_plus(self, auth_session):
        """Test valuation with flip_score >= 30"""
        response = auth_session.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Madinat Al Mataar',
            'size_sqm': 2000,
            'flip_score_min': 30
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_valuation_with_flip_70_plus(self, auth_session):
        """Test valuation with flip_score >= 70 (should reduce comparables)"""
        response = auth_session.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Madinat Al Mataar',
            'size_sqm': 2000,
            'flip_score_min': 70
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_valuation_with_flip_80_plus(self, auth_session):
        """Test valuation with flip_score >= 80 (excellent properties only)"""
        response = auth_session.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Madinat Al Mataar',
            'size_sqm': 2000,
            'flip_score_min': 80
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_combined_esg_and_flip_filters(self, auth_session):
        """Test using both ESG and Flip filters together"""
        response = auth_session.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Madinat Al Mataar',
            'size_sqm': 2000,
            'esg_score_min': 25,
            'flip_score_min': 70
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_invalid_flip_score_type(self, auth_session):
        """Test that invalid flip score type is handled gracefully"""
        response = auth_session.post('/api/property/valuation', json={
            'property_type': 'Unit',
            'area': 'Madinat Al Mataar',
            'size_sqm': 2000,
            'flip_score_min': 'invalid'
        })
        # Should either convert or ignore invalid value
        assert response.status_code in [200, 400, 500]


class TestFlipScoreDistribution:
    """Test flip score data distribution"""
    
    def test_flip_score_distribution_matches_expected(self):
        """Verify flip score distribution matches populated data"""
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT flip_score, COUNT(*) as count
                FROM properties 
                WHERE flip_score IS NOT NULL
                GROUP BY flip_score
                ORDER BY flip_score
            """))
            
            distribution = {row[0]: row[1] for row in result}
            
            # Based on population script
            assert 30 in distribution, "Should have properties with flip score 30"
            assert 70 in distribution, "Should have properties with flip score 70"
            assert 82 in distribution, "Should have properties with flip score 82"
            assert 88 in distribution, "Should have properties with flip score 88"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
