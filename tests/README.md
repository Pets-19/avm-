# Test Suite Documentation - Retyn AVM

## Overview

This document describes the test suite structure, organization, and execution for the Retyn AVM (Automated Valuation Model) application.

**Test Coverage Status:** 26% (improved from ~17% baseline)  
**Total Tests:** 52 passing  
**Test Framework:** pytest 8.4.2 with coverage, mocking, property-based testing

## Test Strategy: Hybrid TDD Approach

We follow a **Hybrid Test-Driven Development (TDD)** approach combining:
1. **Unit Tests** - Fast isolated tests for core functions
2. **Integration Tests** - API endpoint tests with database
3. **Property-Based Tests** - Hypothesis-driven edge case discovery
4. **Security Tests** - SQL injection, XSS, authentication
5. **Load Tests** - Performance under 100+ concurrent users

## Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures (150 lines)
├── unit/                       # Isolated unit tests (fast, no DB)
│   ├── test_location_premium.py    (10 tests, ALL PASSING ✅)
│   ├── test_valuation_core.py      (10 tests, needs API fixes)
│   └── test_outlier_filtering.py   (13 tests, needs API fixes)
├── integration/                # API integration tests (with DB)
│   └── (to be added)
├── property/                   # Hypothesis property-based tests
│   └── (to be added)
├── load/                       # Locust load/performance tests
│   └── (to be added)
├── security/                   # Security vulnerability tests
│   └── (to be added)
├── test_flip_score.py         # Legacy flip score tests (13 passing)
├── test_arbitrage.py          # Legacy arbitrage tests (19 passing)
├── test_redis_cache.py        # Legacy Redis cache tests (10 passing)
├── test_esg_filter.py         # Legacy ESG filter tests (8 failing)
└── test_flip_score_filter.py  # Legacy flip score filter (not run)
```

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Unit Tests Only (Fast)
```bash
pytest tests/unit/ -v
```

### With Coverage Report
```bash
pytest tests/unit/ --cov=app --cov-report=html --cov-report=term
```

### Specific Test File
```bash
pytest tests/unit/test_location_premium.py -v
```

### Watch Mode (Re-run on Changes)
```bash
pytest-watch tests/unit/ -- --cov=app
```

### Coverage Report Only
```bash
pytest tests/unit/ --cov=app --cov-report=term-missing
```

## Test Fixtures (conftest.py)

### Database Fixtures
- `test_db_engine`: In-memory SQLite database for testing
- `mock_engine`: Mock database engine with sample results
- `mock_db_connection`: Mock connection with execute method

### Flask App Fixtures
- `client`: Unauthenticated Flask test client
- `auth_client`: Authenticated Flask test client (logged in)

### Mock Service Fixtures
- `mock_redis`: Mock Redis client for caching tests
- `mock_openai`: Mock OpenAI API client for AI summary tests

### Sample Data Fixtures
- `sample_property_data`: Single property dict
- `sample_properties_list`: List of 5 properties
- `sample_area_coordinates`: GPS and distance data

### Environment Fixtures
- `test_environment`: Auto-applied test environment variables

## Unit Tests

### test_location_premium.py (✅ 10/10 PASSING)

**Purpose:** Test geospatial premium calculations based on proximity to amenities.

**Formula Tested:**
```python
Location Premium (capped at 70%) = sum([
    max(0, 15 - distance_to_metro_km * 3),      # 0-15%
    max(0, 30 - distance_to_beach_km * 6),      # 0-30%
    max(0, 8 - distance_to_mall_km * 2),        # 0-8%
    max(0, 5 - distance_to_school_km * 1),      # 0-5%
    max(0, 10 - distance_to_business_km * 2),   # 0-10%
    (neighborhood_score - 3.0) * 4              # -8% to +8%
])
```

**Tests:**
1. `test_location_premium_dubai_marina` - High premium area (45-50%)
2. `test_location_premium_downtown_dubai` - Ultra-premium area (50-55%)
3. `test_location_premium_unknown_area` - Graceful handling of missing data
4. `test_location_premium_calculation_formula` - Mathematical correctness
5. `test_location_premium_caching_behavior` - Consistent results
6. `test_location_premium_database_error` - Error handling
7. `test_location_premium_null_area` - None/empty area handling
8. `test_location_premium_case_insensitive` - Case-insensitive matching
9. `test_premium_capped_at_70_percent` - Maximum cap enforcement
10. `test_negative_neighborhood_score` - Penalty for low scores

**Coverage:** ~8% of app.py (lines 406-530)

### test_valuation_core.py (🔧 10 tests, needs fixes)

**Purpose:** Test main valuation function that blends ML + database comparables.

**Tests Created:**
1. `test_calculate_valuation_success_with_good_comparables`
2. `test_calculate_valuation_no_comparables_found`
3. `test_calculate_valuation_single_comparable`
4. `test_calculate_valuation_with_bedroom_filter`
5. `test_calculate_valuation_with_all_filters`
6. `test_calculate_valuation_invalid_property_type`
7. `test_calculate_valuation_negative_size`
8. `test_calculate_valuation_outlier_handling`
9. `test_calculate_valuation_database_error`
10. `test_calculate_valuation_confidence_score_logic`

**Status:** Tests written but need API parameter fixes:
- Change `size` to `size_sqm`
- Add `engine` parameter to function calls
- Update mock expectations for proper tuple unpacking

### test_outlier_filtering.py (🔧 13 tests, needs fixes)

**Purpose:** Test statistical outlier detection and removal.

**Tests Created:**
1. `test_filter_outliers_sales_market` - Sales thresholds (100K-50M AED)
2. `test_filter_outliers_rental_market` - Rental thresholds (10K-2M AED)
3. `test_filter_outliers_empty_list` - Empty input handling
4. `test_filter_outliers_single_value` - Single value edge case
5. `test_filter_outliers_all_outliers` - All values removed
6. `test_filter_outliers_no_outliers` - No values removed
7. `test_filter_outliers_stats_calculation` - Statistics accuracy
8. `test_filter_outliers_boundary_cases` - Boundary value testing
9. `test_statistical_outlier_detection_iqr` - IQR method
10. `test_statistical_outlier_detection_zscore` - Z-score method
11. `test_mixed_outlier_detection` - Combined methods
12. `test_large_dataset_performance` - 1000+ values performance
13. `test_numpy_array_input` - Array vs list handling

**Status:** Tests written but need API fixes:
- Change expected dict key from `removed_count` to `total_outliers`
- Change expected dict key from `removed_percentage` to `outlier_percentage`
- Ensure numpy arrays are passed, not lists

## Legacy Tests

### test_flip_score.py (✅ 13 PASSING)
- Tests flip score calculation (0-100 scale)
- Tests liquidity scoring
- Tests price appreciation analysis

### test_arbitrage.py (✅ 19 PASSING)
- Tests arbitrage opportunity detection
- Tests undervalued property identification
- Tests ROI calculations

### test_redis_cache.py (✅ 10 PASSING)
- Tests Redis caching layer
- Tests cache hit/miss behavior
- Tests TTL expiration

### test_esg_filter.py (❌ 8 FAILING)
- Known issues with ESG score filtering
- Needs database schema updates

## Test Coverage Goals

**Current:** 26% (improved from ~17%)  
**Phase 1 (Week 1):** 50% - Unit tests for all core functions  
**Phase 2 (Week 2):** 65% - Integration tests for critical APIs  
**Phase 3 (Week 3):** 75% - Property-based tests with Hypothesis  
**Phase 4 (Week 4):** 80% - Security + load tests

## Key Testing Principles

1. **Fast Unit Tests** - Unit tests should run in <1 second total
2. **Isolated Tests** - No test should depend on another test's state
3. **Realistic Mocks** - Mocks should reflect actual database behavior
4. **Clear Assertions** - Each test should verify one specific behavior
5. **Comprehensive Coverage** - Test happy paths, edge cases, and errors

## Advanced Testing Features

### Property-Based Testing (Hypothesis)
```bash
pip install hypothesis
```

Example:
```python
from hypothesis import given, strategies as st

@given(st.integers(min_value=100000, max_value=50000000))
def test_valuation_with_any_price(price):
    # Hypothesis auto-generates 100+ test cases
    assert calculate_valuation(price) >= 0
```

### Load Testing (Locust)
```bash
pip install locust
locust -f tests/load/test_api_load.py --host=http://localhost:5000
```

### Security Testing
- SQL injection attempts
- XSS payload testing
- Authentication bypass attempts
- Rate limiting validation

## CI/CD Integration

### GitHub Actions (Planned)
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### Pre-Commit Hook
```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/unit/ -q
if [ $? -ne 0 ]; then
    echo "❌ Unit tests failed. Commit aborted."
    exit 1
fi
```

## Troubleshooting

### Import Errors
```python
# Add to sys.path in test files
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import function_to_test
```

### Database Connection Issues
```python
# Use in-memory SQLite for fast tests
@pytest.fixture
def test_db_engine():
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()
```

### Mock Not Working
```python
# Use patch context manager
from unittest.mock import patch

with patch('app.engine', mock_engine):
    result = function_under_test()
```

### Tests Run Slowly
- Use `pytest -x` to stop on first failure
- Use `pytest -k test_name` to run specific tests
- Use `pytest --lf` to re-run last failed tests

## Next Steps

### Immediate (Week 1)
1. ✅ Create test infrastructure (conftest.py)
2. ✅ Create location premium tests (10 passing)
3. 🔧 Fix valuation core tests (parameter updates)
4. 🔧 Fix outlier filtering tests (dict key updates)
5. ⏳ Add 10 more unit tests (rental yield, project premium)

### Week 2 (Integration Tests)
- Test `/api/valuation` endpoint
- Test `/api/flip-score` endpoint
- Test `/api/arbitrage-score` endpoint
- Test authentication flows
- Test error handling

### Week 3 (Property-Based Tests)
- Hypothesis tests for valuation ranges
- Hypothesis tests for location premium bounds
- Hypothesis tests for statistical calculations
- Edge case auto-discovery

### Week 4 (Security + Load)
- SQL injection tests
- XSS payload tests
- Rate limiting tests
- Load tests (100+ concurrent users)
- Performance benchmarking

## Documentation

**Approach #3 - Hybrid TDD:** See COMPREHENSIVE_LAUNCH_ANALYSIS.md Section 4.1  
**Coverage Reports:** `htmlcov/index.html` after running with `--cov-report=html`  
**Test Results:** `pytest --junitxml=junit.xml` for CI integration

## Contact

For questions about the test suite:
- Check existing tests in `tests/` directory
- Review `conftest.py` for available fixtures
- See GitHub Copilot instructions in `.github/copilot-instructions.md`

---

**Last Updated:** January 2025  
**Test Coverage:** 26% (improved from ~17% baseline)  
**Passing Tests:** 52 (10 unit + 42 legacy)  
**Contributors:** AI + Human QA Team
