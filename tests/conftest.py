"""Shared pytest fixtures for test suite."""
import os
import pytest
from unittest.mock import MagicMock, Mock, patch
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from typing import Dict, Any, List

# Import Flask app for testing
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app as flask_app


# Database Fixtures
@pytest.fixture
def test_db_engine():
    """Create in-memory SQLite database engine for testing.
    
    This fixture provides an isolated database for each test.
    Uses StaticPool to maintain single connection for SQLite in-memory DB.
    """
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    yield test_engine
    test_engine.dispose()


@pytest.fixture
def mock_engine():
    """Mock database engine with predefined sample results.
    
    Returns a mock that simulates database queries with realistic data.
    """
    mock_eng = MagicMock()
    
    # Mock connection context manager
    mock_conn = MagicMock()
    mock_eng.connect.return_value.__enter__.return_value = mock_conn
    mock_eng.connect.return_value.__exit__.return_value = None
    
    # Mock query results for properties table
    mock_result = MagicMock()
    mock_result.fetchall.return_value = [
        (1000000, 1000, 'Unit', 2, 'Dubai Marina', '2023-01-15'),
        (1050000, 1050, 'Unit', 2, 'Dubai Marina', '2023-02-20'),
        (980000, 980, 'Unit', 2, 'Dubai Marina', '2023-03-10'),
    ]
    mock_result.rowcount = 3
    mock_conn.execute.return_value = mock_result
    
    return mock_eng


# Flask App Fixtures
@pytest.fixture
def client():
    """Create Flask test client.
    
    Provides unauthenticated client for testing public endpoints.
    """
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    
    with flask_app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client):
    """Create authenticated Flask test client.
    
    Simulates logged-in user with valid session.
    Uses hardcoded credentials from app.py AUTHORIZED_USERS.
    """
    # Login with valid credentials
    response = client.post('/login', data={
        'email': 'dhanesh@retyn.ai',
        'password': 'retyn*#123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    yield client


# Mock External Services Fixtures
@pytest.fixture
def mock_redis():
    """Mock Redis client for caching tests.
    
    Simulates Redis operations without actual connection.
    """
    redis_mock = MagicMock()
    redis_mock.get.return_value = None  # Default: cache miss
    redis_mock.set.return_value = True
    redis_mock.delete.return_value = 1
    redis_mock.exists.return_value = 0
    redis_mock.ping.return_value = True
    
    return redis_mock


@pytest.fixture
def mock_openai():
    """Mock OpenAI API client for AI summary tests.
    
    Prevents actual API calls during testing.
    """
    openai_mock = MagicMock()
    
    # Mock chat completion response
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "AI-generated market summary"
    openai_mock.chat.completions.create.return_value = mock_completion
    
    return openai_mock


# Sample Data Fixtures
@pytest.fixture
def sample_property_data() -> Dict[str, Any]:
    """Provide sample property data for testing.
    
    Returns dict with typical property attributes.
    """
    return {
        'property_type': 'Unit',
        'area': 'Dubai Marina',
        'size': 1000,
        'bedrooms': 2,
        'floor': 10,
        'view': 'Marina View',
        'age': 5,
        'project_name': 'Marina Heights',
        'transaction_type': 'sales'
    }


@pytest.fixture
def sample_properties_list() -> List[Dict[str, Any]]:
    """Provide list of sample properties for bulk testing.
    
    Returns 5 properties with varying characteristics.
    """
    return [
        {'trans_value': 1000000, 'actual_area': 1000, 'prop_type_en': 'Unit', 'rooms_en': '2', 'area_en': 'Dubai Marina'},
        {'trans_value': 1050000, 'actual_area': 1050, 'prop_type_en': 'Unit', 'rooms_en': '2', 'area_en': 'Dubai Marina'},
        {'trans_value': 980000, 'actual_area': 980, 'prop_type_en': 'Unit', 'rooms_en': '2', 'area_en': 'Dubai Marina'},
        {'trans_value': 1020000, 'actual_area': 1020, 'prop_type_en': 'Unit', 'rooms_en': '2', 'area_en': 'Dubai Marina'},
        {'trans_value': 990000, 'actual_area': 990, 'prop_type_en': 'Unit', 'rooms_en': '2', 'area_en': 'Dubai Marina'},
    ]


@pytest.fixture
def sample_area_coordinates() -> Dict[str, Any]:
    """Provide sample area coordinates for geospatial testing.
    
    Returns GPS and distance data for Dubai Marina.
    """
    return {
        'area_name': 'Dubai Marina',
        'latitude': 25.0804,
        'longitude': 55.1392,
        'distance_to_metro_km': 0.5,
        'distance_to_beach_km': 0.2,
        'distance_to_mall_km': 0.3,
        'distance_to_school_km': 1.0,
        'distance_to_business_km': 2.0,
        'neighborhood_score': 4.5
    }


# Database Mock Fixtures
@pytest.fixture
def mock_db_connection():
    """Mock database connection with execute method.
    
    Useful for testing queries without actual database.
    """
    conn_mock = MagicMock()
    
    # Mock execute method with flexible return value
    result_mock = MagicMock()
    result_mock.fetchall.return_value = []
    result_mock.fetchone.return_value = None
    result_mock.rowcount = 0
    conn_mock.execute.return_value = result_mock
    
    return conn_mock


# Patching Fixtures
@pytest.fixture
def patch_database_engine(mock_engine):
    """Patch app.engine with mock engine.
    
    Use with 'with' statement to temporarily replace database.
    """
    with patch('app.engine', mock_engine):
        yield mock_engine


@pytest.fixture
def patch_redis_client(mock_redis):
    """Patch app.redis_client with mock Redis.
    
    Use with 'with' statement to temporarily replace Redis client.
    """
    with patch('app.redis_client', mock_redis):
        yield mock_redis


# Test Configuration
@pytest.fixture(scope='session', autouse=True)
def test_environment():
    """Set up test environment variables.
    
    Runs once per test session, automatically applied to all tests.
    """
    os.environ['TESTING'] = '1'
    os.environ['USE_REDIS_CACHE'] = '0'  # Disable Redis by default in tests
    os.environ['USE_AI_SUMMARY'] = '0'  # Disable AI by default in tests
    yield
    # Cleanup after all tests
    os.environ.pop('TESTING', None)
    os.environ.pop('USE_REDIS_CACHE', None)
    os.environ.pop('USE_AI_SUMMARY', None)
