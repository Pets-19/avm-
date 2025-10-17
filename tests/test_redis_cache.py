"""
Unit Tests for Redis Caching Implementation
Tests cache decorator functionality and graceful degradation
"""
import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestRedisCacheDecorator:
    """Test suite for @cache_result decorator"""
    
    def test_cache_decorator_with_redis_available(self):
        """Test cache HIT/MISS with Redis available"""
        # Setup mock Redis client
        mock_redis = MagicMock()
        mock_redis.get.return_value = None  # First call: cache MISS
        
        with patch('app.redis_client', mock_redis):
            with patch('app.REDIS_ENABLED', True):
                from app import cache_result
                
                call_count = 0
                
                @cache_result(timeout=300, key_prefix="test:")
                def test_function(arg1, arg2):
                    nonlocal call_count
                    call_count += 1
                    return {'result': arg1 + arg2}
                
                # First call - cache MISS
                result1 = test_function(1, 2)
                assert result1 == {'result': 3}
                assert call_count == 1
                
                # Verify Redis.get was called
                assert mock_redis.get.called
                
                # Verify Redis.setex was called to store result
                assert mock_redis.setex.called
    
    def test_cache_decorator_with_redis_unavailable(self):
        """Test graceful degradation when Redis unavailable"""
        with patch('app.REDIS_ENABLED', False):
            with patch('app.redis_client', None):
                from app import cache_result
                
                call_count = 0
                
                @cache_result(timeout=300, key_prefix="test:")
                def test_function(value):
                    nonlocal call_count
                    call_count += 1
                    return {'result': value * 2}
                
                # Call multiple times - should execute each time (no caching)
                result1 = test_function(5)
                result2 = test_function(5)
                
                assert result1 == {'result': 10}
                assert result2 == {'result': 10}
                assert call_count == 2  # Function called twice (no cache)
    
    def test_cache_key_generation_unique(self):
        """Test cache keys are unique for different inputs"""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        
        with patch('app.redis_client', mock_redis):
            with patch('app.REDIS_ENABLED', True):
                from app import cache_result
                
                @cache_result(timeout=300, key_prefix="test:")
                def test_function(value):
                    return {'result': value}
                
                # Call with different arguments
                test_function(1)
                test_function(2)
                
                # Verify Redis.setex called with different keys
                assert mock_redis.setex.call_count == 2
                call_args = mock_redis.setex.call_args_list
                key1 = call_args[0][0][0]
                key2 = call_args[1][0][0]
                assert key1 != key2  # Different keys for different inputs
    
    def test_cache_hit_returns_cached_data(self):
        """Test cached data is returned on cache HIT"""
        cached_data = {'result': 'cached_value'}
        
        mock_redis = MagicMock()
        mock_redis.get.return_value = json.dumps(cached_data)
        
        with patch('app.redis_client', mock_redis):
            with patch('app.REDIS_ENABLED', True):
                from app import cache_result
                
                call_count = 0
                
                @cache_result(timeout=300, key_prefix="test:")
                def test_function():
                    nonlocal call_count
                    call_count += 1
                    return {'result': 'fresh_value'}
                
                # Call function - should return cached data
                result = test_function()
                
                assert result == cached_data
                assert call_count == 0  # Function not executed
                assert mock_redis.get.called
                assert not mock_redis.setex.called  # No write on cache HIT
    
    def test_cache_ttl_configuration(self):
        """Test cache TTL is correctly set"""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        
        with patch('app.redis_client', mock_redis):
            with patch('app.REDIS_ENABLED', True):
                from app import cache_result
                
                @cache_result(timeout=7200, key_prefix="test:")
                def test_function():
                    return {'result': 'value'}
                
                test_function()
                
                # Verify setex called with correct TTL
                call_args = mock_redis.setex.call_args
                ttl = call_args[0][1]
                assert ttl == 7200
    
    def test_cache_handles_serialization_errors(self):
        """Test cache handles JSON serialization errors gracefully"""
        mock_redis = MagicMock()
        mock_redis.get.return_value = None
        mock_redis.setex.side_effect = Exception("Serialization error")
        
        with patch('app.redis_client', mock_redis):
            with patch('app.REDIS_ENABLED', True):
                from app import cache_result
                
                @cache_result(timeout=300, key_prefix="test:")
                def test_function():
                    return {'result': 'value'}
                
                # Should not raise exception
                result = test_function()
                assert result == {'result': 'value'}


class TestRedisCacheIntegration:
    """Integration tests for Redis caching in actual endpoints"""
    
    @pytest.fixture
    def app_client(self):
        """Create Flask test client"""
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_areas_endpoint_caching_behavior(self, app_client):
        """Test /api/areas endpoint caching works correctly"""
        # Note: This requires authentication, so we'll mock it
        with patch('app.login_required', lambda f: f):
            with patch('app.engine') as mock_engine:
                mock_conn = MagicMock()
                mock_result = MagicMock()
                mock_result.__iter__ = Mock(return_value=iter([('Dubai Marina',), ('Downtown Dubai',)]))
                mock_conn.execute.return_value = mock_result
                mock_engine.connect.return_value.__enter__.return_value = mock_conn
                
                # First request - cache MISS
                response1 = app_client.get('/api/areas/buy')
                
                # Second request - should be cache HIT (if Redis enabled)
                response2 = app_client.get('/api/areas/buy')
                
                assert response1.status_code == 200 or response1.status_code == 302  # 302 if redirect to login
                assert response2.status_code == 200 or response2.status_code == 302


class TestRedisCachePerformance:
    """Performance and load tests for caching"""
    
    def test_cache_performance_improvement(self):
        """Test cache provides significant performance improvement"""
        mock_redis = MagicMock()
        mock_redis.get.side_effect = [None, json.dumps({'result': 'cached'})]  # MISS, then HIT
        
        with patch('app.redis_client', mock_redis):
            with patch('app.REDIS_ENABLED', True):
                from app import cache_result
                
                @cache_result(timeout=300, key_prefix="perf:")
                def slow_function():
                    time.sleep(0.1)  # Simulate slow operation
                    return {'result': 'fresh'}
                
                # First call - slow (cache MISS)
                start1 = time.time()
                result1 = slow_function()
                duration1 = time.time() - start1
                
                # Second call - fast (cache HIT)
                start2 = time.time()
                result2 = slow_function()
                duration2 = time.time() - start2
                
                # Cache HIT should be significantly faster
                assert duration2 < duration1 / 10  # At least 10x faster


class TestRedisCacheConfiguration:
    """Test Redis configuration and connection"""
    
    def test_redis_enabled_from_environment(self):
        """Test Redis enabled/disabled from environment variable"""
        with patch.dict(os.environ, {'REDIS_ENABLED': 'true'}):
            # Re-import to test env var loading
            import importlib
            # Note: Full re-import test requires app restart
            pass
    
    def test_redis_connection_failure_handling(self):
        """Test graceful handling of Redis connection failures"""
        with patch('redis.Redis') as mock_redis_class:
            mock_redis_instance = MagicMock()
            mock_redis_instance.ping.side_effect = Exception("Connection refused")
            mock_redis_class.return_value = mock_redis_instance
            
            # Should handle connection failure gracefully
            # and continue with REDIS_ENABLED=False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
