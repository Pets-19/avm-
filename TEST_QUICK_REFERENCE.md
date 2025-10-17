# 🚀 Test Coverage Quick Reference Card

## 📊 Current Status (Day 1 Complete)

```
Coverage: 26% (↑ from 17% baseline)
Passing Tests: 52 (10 new unit tests)
Status: ✅ Phase 1 Complete
```

## ⚡ Quick Commands

### Run All Tests
```bash
pytest tests/ -v
```

### Run Unit Tests (Fast)
```bash
pytest tests/unit/ -v
```

### Coverage Report
```bash
pytest tests/unit/test_location_premium.py --cov=app --cov-report=html
open htmlcov/index.html
```

### Run Specific Test
```bash
pytest tests/unit/test_location_premium.py::TestCalculateLocationPremium::test_location_premium_dubai_marina -v
```

### Watch Mode
```bash
pytest-watch tests/unit/
```

## 📁 File Structure

```
tests/
├── conftest.py                      # 11 reusable fixtures ✅
├── unit/
│   ├── test_location_premium.py     # 10 PASSING ✅
│   ├── test_valuation_core.py       # 10 tests (needs fixes 🔧)
│   └── test_outlier_filtering.py    # 13 tests (needs fixes 🔧)
├── test_flip_score.py               # 13 PASSING ✅
├── test_arbitrage.py                # 19 PASSING ✅
└── test_redis_cache.py              # 10 PASSING ✅
```

## 🎯 What's Working

✅ **10 Location Premium Tests** - All passing
- Dubai Marina premium (45-50%)
- Downtown Dubai premium (50-55%)
- Unknown area handling
- Formula verification
- Error handling
- Case sensitivity
- 70% cap enforcement

✅ **Test Infrastructure**
- conftest.py with fixtures
- Mock database engine
- Mock Redis client
- Sample data generators
- Authenticated test client

✅ **Legacy Tests**
- 13 flip score tests
- 19 arbitrage tests
- 10 Redis cache tests

## 🔧 Pending Fixes (50 min)

### test_valuation_core.py (30 min)
**Issue:** Wrong parameter names
```python
# WRONG:
calculate_valuation_from_database(size=1000, ...)

# RIGHT:
calculate_valuation_from_database(size_sqm=1000, engine=mock_engine, ...)
```

### test_outlier_filtering.py (20 min)
**Issue:** Wrong dict keys
```python
# WRONG:
assert stats['removed_count'] == 2

# RIGHT:
assert stats['total_outliers'] == 2
assert stats['outlier_percentage'] == 33.3
```

## 📈 Coverage Roadmap

| Week | Target | Focus |
|------|--------|-------|
| 1 | 50% | Unit tests (core functions) |
| 2 | 65% | Integration tests (APIs) |
| 3 | 75% | Property-based tests |
| 4 | 80% | Security + load tests |

## 🧪 Test Writing Pattern

### 1. Import
```python
import pytest
from unittest.mock import MagicMock, patch
from app import function_to_test
```

### 2. Mock Database Result
```python
mock_conn = MagicMock()
mock_result = MagicMock()
mock_result.fetchone.return_value = (val1, val2, val3)  # TUPLE not dict!
mock_conn.execute.return_value = mock_result
mock_engine.connect.return_value.__enter__.return_value = mock_conn
```

### 3. Test with Patch
```python
with patch('app.engine', mock_engine):
    result = function_to_test(params)
    assert result['expected_key'] == expected_value
```

## 🐛 Common Issues

### Import Error
```python
# Add to top of test file:
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
```

### Mock Not Working
```python
# Use tuple for database results:
mock_result.fetchone.return_value = (val1, val2)  # ✅
mock_result.fetchone.return_value = {'key': val}  # ❌
```

### Tests Run Slow
```bash
# Run only unit tests:
pytest tests/unit/ -v  # Fast

# Skip integration tests:
pytest -m "not integration"
```

## 📚 Key Functions Tested

### ✅ calculate_location_premium(area_name)
**Returns:** dict with `total_premium`, `metro_premium`, etc.
**Coverage:** 90% (10 tests passing)

### 🔧 calculate_valuation_from_database(property_type, area, size_sqm, engine, ...)
**Returns:** dict with `estimated_value`, `confidence`, `comparable_count`
**Coverage:** 0% (10 tests written, needs fixes)

### 🔧 filter_outliers(prices, search_type)
**Returns:** (filtered_prices, outlier_stats dict)
**Coverage:** 0% (13 tests written, needs fixes)

## 💡 Pro Tips

1. **Run tests frequently** - Don't write all tests then run
2. **Use `-x` flag** - Stop on first failure
3. **Use `-v` flag** - Verbose output
4. **Use `--lf`** - Re-run last failed
5. **Check coverage** - Use `--cov-report=html`
6. **Mock externals** - Mock database, Redis, OpenAI
7. **Test edge cases** - None, empty, negative, huge values
8. **Test errors** - Database failures, invalid inputs

## 🎓 Testing Philosophy

- **Unit Tests** → Fast, isolated, no DB
- **Integration Tests** → Realistic, with DB
- **Property Tests** → Auto-generate edge cases
- **Security Tests** → SQL injection, XSS
- **Load Tests** → 100+ concurrent users

## 📞 Quick Help

**Coverage too low?** Add more unit tests  
**Tests too slow?** Use mocks, not real DB  
**Tests failing?** Check function signatures  
**Import errors?** Check sys.path setup  
**Mock not working?** Use tuples not dicts  

## 🏆 Success Metrics

- ✅ 10 location premium tests passing
- ✅ 26% coverage (↑ from 17%)
- ✅ Test infrastructure complete
- ✅ Documentation complete
- 🔧 23 tests need minor fixes
- 🎯 Target: 50% by end of week

---

**Created:** January 2025  
**Status:** Day 1 Complete ✅  
**Next:** Fix 23 pending tests (50 min)
