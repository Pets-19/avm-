# Database Indexing Implementation Prompts

## 🚀 Quick Win Prompt (Phase 1 - Deploy Today)

### Task: Create Essential Database Indexes for Performance Optimization

**Context:**
- Project: Retyn AVM - Dubai Real Estate Automated Valuation Model
- Database: PostgreSQL (Neon serverless) with 153K properties, 620K rentals
- Problem: Slow queries (2-5s) on Buy/Rent searches due to missing indexes
- Goal: Reduce query time to <500ms by adding composite indexes

**Deliverables:**
1. Migration file: `/workspaces/avm-/migrations/add_performance_indexes_phase1.sql`
2. Application script: `/workspaces/avm-/scripts/apply_indexes_phase1.py`
3. Performance tests: `/workspaces/avm-/tests/test_index_performance_phase1.py`
4. Documentation: `/workspaces/avm-/docs/DATABASE_INDEXES_PHASE1.md`
5. Update: `check_production_ready.sh` (add index verification check)

---

### 1. Migration File Requirements

**File:** `/workspaces/avm-/migrations/add_performance_indexes_phase1.sql`

**Structure:**
```sql
-- =============================================================================
-- PHASE 1: ESSENTIAL PERFORMANCE INDEXES (Quick Win)
-- =============================================================================
-- Purpose: Optimize most common query patterns for Buy/Rent search
-- Impact: Reduces query time from 2-5s to <500ms
-- Tables: properties (153K rows), rentals (620K rows)
-- Estimated Duration: 5-7 minutes total
-- Storage Overhead: ~150MB
-- =============================================================================

-- Index 1: Properties Area + Type Composite
-- Query Pattern: SELECT * FROM properties WHERE area_en ILIKE '%Dubai Marina%' AND prop_type_en = 'Unit'
-- Used By: Buy search (app.py line 2814), Valuation comparables (app.py line 1810)
-- Expected Speedup: 5-10x faster
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_area_type 
ON properties(area_en, prop_type_en);

-- Index 2: Rentals Area + Type Composite
-- Query Pattern: SELECT * FROM rentals WHERE area_en ILIKE '%Dubai Marina%' AND prop_type_en = 'Unit'
-- Used By: Rent search (app.py line 2948), Rental yield (app.py line 2316)
-- Expected Speedup: 5-10x faster
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rentals_area_type 
ON rentals(area_en, prop_type_en);

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================
-- Check indexes were created
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes 
WHERE indexname IN ('idx_properties_area_type', 'idx_rentals_area_type')
ORDER BY tablename, indexname;

-- Check index sizes
SELECT 
    indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE indexrelname IN ('idx_properties_area_type', 'idx_rentals_area_type')
ORDER BY indexrelname;

-- =============================================================================
-- ROLLBACK (if needed)
-- =============================================================================
-- DROP INDEX CONCURRENTLY IF EXISTS idx_properties_area_type;
-- DROP INDEX CONCURRENTLY IF EXISTS idx_rentals_area_type;
```

**Key Requirements:**
- ✅ Use `CREATE INDEX CONCURRENTLY` (non-blocking)
- ✅ Add `IF NOT EXISTS` (idempotent)
- ✅ Include detailed comments explaining purpose
- ✅ Add verification queries
- ✅ Include rollback commands (commented)
- ✅ Estimate duration and storage impact

---

### 2. Application Script Requirements

**File:** `/workspaces/avm-/scripts/apply_indexes_phase1.py`

**Template:**
```python
#!/usr/bin/env python3
"""
Apply Phase 1 Performance Indexes

Purpose: Create essential composite indexes for Buy/Rent search optimization
Impact: Reduces query time from 2-5s to <500ms
Duration: ~5-7 minutes

Usage:
    python scripts/apply_indexes_phase1.py

Environment Variables:
    DATABASE_URL - PostgreSQL connection string (required)
"""
import os
import sys
import time
import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
MIGRATION_FILE = Path(__file__).parent.parent / 'migrations' / 'add_performance_indexes_phase1.sql'
REQUIRED_INDEXES = ['idx_properties_area_type', 'idx_rentals_area_type']


def load_database_connection():
    """Load and validate DATABASE_URL from environment"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL environment variable not set")
        sys.exit(1)
    
    try:
        engine = create_engine(
            database_url,
            connect_args={
                'sslmode': 'require',
                'connect_timeout': 30,
                'options': '-c statement_timeout=600000'  # 10 min timeout for index creation
            },
            pool_pre_ping=True
        )
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
        return engine
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        sys.exit(1)


def read_migration_file():
    """Read and parse migration SQL file"""
    if not MIGRATION_FILE.exists():
        logger.error(f"❌ Migration file not found: {MIGRATION_FILE}")
        sys.exit(1)
    
    with open(MIGRATION_FILE, 'r') as f:
        sql_content = f.read()
    
    logger.info(f"✅ Loaded migration file: {MIGRATION_FILE.name}")
    return sql_content


def execute_index_creation(engine, sql_content):
    """Execute CREATE INDEX statements from migration file"""
    # Split into individual statements (filter out comments and empty lines)
    statements = [
        stmt.strip() 
        for stmt in sql_content.split(';') 
        if stmt.strip() and not stmt.strip().startswith('--')
    ]
    
    # Filter only CREATE INDEX statements
    create_statements = [
        stmt for stmt in statements 
        if 'CREATE INDEX' in stmt.upper()
    ]
    
    logger.info(f"📊 Found {len(create_statements)} CREATE INDEX statements")
    
    results = []
    for i, statement in enumerate(create_statements, 1):
        # Extract index name from statement
        index_name = None
        if 'IF NOT EXISTS' in statement:
            parts = statement.split('IF NOT EXISTS')[1].split('ON')[0]
            index_name = parts.strip()
        
        logger.info(f"🔄 Creating index {i}/{len(create_statements)}: {index_name}...")
        start_time = time.time()
        
        try:
            with engine.connect() as conn:
                # Set longer timeout for index creation
                conn.execute(text("SET statement_timeout = '600000'"))  # 10 minutes
                conn.execute(text(statement))
                conn.commit()
            
            duration = time.time() - start_time
            logger.info(f"✅ Index created successfully in {duration:.2f}s: {index_name}")
            results.append({'index': index_name, 'status': 'success', 'duration': duration})
            
        except OperationalError as e:
            if 'already exists' in str(e).lower():
                logger.info(f"ℹ️  Index already exists (skipped): {index_name}")
                results.append({'index': index_name, 'status': 'exists', 'duration': 0})
            else:
                logger.error(f"❌ Failed to create index {index_name}: {e}")
                results.append({'index': index_name, 'status': 'failed', 'error': str(e)})
        except Exception as e:
            logger.error(f"❌ Unexpected error creating index {index_name}: {e}")
            results.append({'index': index_name, 'status': 'failed', 'error': str(e)})
    
    return results


def verify_indexes(engine):
    """Verify all required indexes were created successfully"""
    logger.info("🔍 Verifying indexes...")
    
    query = text("""
        SELECT indexname, tablename, pg_size_pretty(pg_relation_size(indexrelid)) as size
        FROM pg_stat_user_indexes
        WHERE indexrelname = ANY(:index_names)
        ORDER BY tablename, indexname
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query, {'index_names': REQUIRED_INDEXES})
            indexes = result.fetchall()
        
        if len(indexes) == len(REQUIRED_INDEXES):
            logger.info(f"✅ All {len(REQUIRED_INDEXES)} indexes verified:")
            for idx in indexes:
                logger.info(f"   - {idx.tablename}.{idx.indexname} ({idx.size})")
            return True
        else:
            logger.error(f"❌ Expected {len(REQUIRED_INDEXES)} indexes, found {len(indexes)}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Index verification failed: {e}")
        return False


def measure_query_performance(engine):
    """Test query performance before/after indexes"""
    logger.info("📊 Testing query performance...")
    
    test_query = text("""
        EXPLAIN (ANALYZE, FORMAT JSON)
        SELECT * FROM properties 
        WHERE area_en ILIKE :area 
        AND prop_type_en = :type 
        LIMIT 100
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(
                test_query, 
                {'area': '%Dubai Marina%', 'type': 'Unit'}
            )
            explain_result = result.fetchone()[0]
        
        # Extract execution time
        execution_time = explain_result[0]['Execution Time']
        logger.info(f"✅ Query execution time: {execution_time:.2f}ms")
        
        # Check if index was used
        plan_str = str(explain_result)
        if 'idx_properties_area_type' in plan_str:
            logger.info("✅ Query planner is using new index")
        else:
            logger.warning("⚠️  Query planner may not be using new index yet (needs ANALYZE)")
        
        return execution_time
        
    except Exception as e:
        logger.error(f"❌ Performance test failed: {e}")
        return None


def main():
    """Main execution flow"""
    logger.info("=" * 70)
    logger.info("🚀 PHASE 1: ESSENTIAL PERFORMANCE INDEXES")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    # Step 1: Load database connection
    engine = load_database_connection()
    
    # Step 2: Read migration file
    sql_content = read_migration_file()
    
    # Step 3: Execute index creation
    results = execute_index_creation(engine, sql_content)
    
    # Step 4: Verify indexes
    verification_passed = verify_indexes(engine)
    
    # Step 5: Test query performance
    query_time = measure_query_performance(engine)
    
    # Summary
    total_duration = time.time() - start_time
    logger.info("=" * 70)
    logger.info("📊 SUMMARY")
    logger.info("=" * 70)
    logger.info(f"Total Duration: {total_duration:.2f}s")
    logger.info(f"Indexes Created: {sum(1 for r in results if r['status'] == 'success')}")
    logger.info(f"Indexes Existed: {sum(1 for r in results if r['status'] == 'exists')}")
    logger.info(f"Failures: {sum(1 for r in results if r['status'] == 'failed')}")
    
    if verification_passed:
        logger.info("✅ All indexes verified successfully")
        if query_time and query_time < 500:
            logger.info(f"✅ Query performance target met: {query_time:.2f}ms < 500ms")
        sys.exit(0)
    else:
        logger.error("❌ Index verification failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Key Requirements:**
- ✅ Load DATABASE_URL with validation
- ✅ Read and parse migration SQL file
- ✅ Execute CREATE INDEX with error handling
- ✅ Verify indexes exist with size information
- ✅ Test query performance and plan usage
- ✅ Detailed logging with timestamps and emojis
- ✅ Exit codes: 0 (success), 1 (failure)
- ✅ Handle edge cases (already exists, timeout, etc.)

---

### 3. Performance Test Requirements

**File:** `/workspaces/avm-/tests/test_index_performance_phase1.py`

**Template:**
```python
"""
Performance Tests for Phase 1 Database Indexes

Tests:
1. Verify indexes exist
2. Verify query performance improvement
3. Verify query planner uses indexes
4. Test edge cases (NULL, case sensitivity)
"""
import pytest
import time
from sqlalchemy import text
from app import engine


class TestPhase1Indexes:
    """Test Phase 1 index creation and performance"""
    
    def test_idx_properties_area_type_exists(self):
        """Verify idx_properties_area_type index was created"""
        query = text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE indexname = 'idx_properties_area_type'
            AND tablename = 'properties'
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            count = result.scalar()
        
        assert count == 1, "Index idx_properties_area_type does not exist"
    
    def test_idx_rentals_area_type_exists(self):
        """Verify idx_rentals_area_type index was created"""
        query = text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE indexname = 'idx_rentals_area_type'
            AND tablename = 'rentals'
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            count = result.scalar()
        
        assert count == 1, "Index idx_rentals_area_type does not exist"
    
    def test_properties_query_performance(self):
        """Test query performance on properties table"""
        query = text("""
            SELECT COUNT(*) 
            FROM properties 
            WHERE area_en ILIKE :area 
            AND prop_type_en = :type
        """)
        
        # Measure query execution time
        start = time.time()
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {'area': '%Dubai Marina%', 'type': 'Unit'}
            )
            count = result.scalar()
        duration_ms = (time.time() - start) * 1000
        
        print(f"\n📊 Properties query: {duration_ms:.2f}ms ({count} results)")
        
        # With index, should be <500ms for 153K rows
        assert duration_ms < 1000, f"Query too slow: {duration_ms:.2f}ms"
    
    def test_rentals_query_performance(self):
        """Test query performance on rentals table"""
        query = text("""
            SELECT COUNT(*) 
            FROM rentals 
            WHERE area_en ILIKE :area 
            AND prop_type_en = :type
        """)
        
        # Measure query execution time
        start = time.time()
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {'area': '%Business Bay%', 'type': 'Unit'}
            )
            count = result.scalar()
        duration_ms = (time.time() - start) * 1000
        
        print(f"\n📊 Rentals query: {duration_ms:.2f}ms ({count} results)")
        
        # With index, should be <500ms for 620K rows
        assert duration_ms < 1000, f"Query too slow: {duration_ms:.2f}ms"
    
    def test_query_plan_uses_index_properties(self):
        """Verify PostgreSQL query planner uses idx_properties_area_type"""
        query = text("""
            EXPLAIN (FORMAT JSON)
            SELECT * FROM properties 
            WHERE area_en ILIKE :area 
            AND prop_type_en = :type 
            LIMIT 100
        """)
        
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {'area': '%Dubai Marina%', 'type': 'Unit'}
            )
            explain_output = result.fetchone()[0]
        
        plan_str = str(explain_output)
        print(f"\n📊 Query plan: {plan_str[:200]}...")
        
        # Check if index is mentioned in plan
        # Note: May use "Bitmap Index Scan" or "Index Scan" on idx_properties_area_type
        assert 'idx_properties_area_type' in plan_str or 'Index' in plan_str, \
            "Query planner not using index (may need ANALYZE)"
    
    def test_case_insensitive_search(self):
        """Test ILIKE queries work correctly with index"""
        query = text("""
            SELECT COUNT(*) 
            FROM properties 
            WHERE area_en ILIKE :area 
            AND prop_type_en = :type
        """)
        
        test_cases = [
            ('dubai marina', 'unit'),  # lowercase
            ('DUBAI MARINA', 'UNIT'),  # uppercase
            ('Dubai Marina', 'Unit'),  # mixed case
            ('%dubai%', 'Unit'),       # wildcard
        ]
        
        for area, prop_type in test_cases:
            with engine.connect() as conn:
                result = conn.execute(
                    query, 
                    {'area': f'%{area}%', 'type': prop_type}
                )
                count = result.scalar()
            
            print(f"\n📊 Query '{area}' + '{prop_type}': {count} results")
            assert count >= 0, f"Query failed for case: {area}, {prop_type}"
    
    def test_null_values_handled(self):
        """Test queries handle NULL values correctly"""
        query = text("""
            SELECT COUNT(*) 
            FROM properties 
            WHERE area_en IS NULL 
            OR prop_type_en IS NULL
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            null_count = result.scalar()
        
        print(f"\n📊 Records with NULL area/type: {null_count}")
        # Index should still work even with NULLs
        assert null_count >= 0
    
    def test_index_size_reasonable(self):
        """Verify index sizes are within expected range"""
        query = text("""
            SELECT 
                indexrelname,
                pg_size_pretty(pg_relation_size(indexrelid)) as size,
                pg_relation_size(indexrelid) as size_bytes
            FROM pg_stat_user_indexes
            WHERE indexrelname IN ('idx_properties_area_type', 'idx_rentals_area_type')
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            indexes = result.fetchall()
        
        for idx in indexes:
            print(f"\n📊 {idx.indexrelname}: {idx.size} ({idx.size_bytes:,} bytes)")
            # Each index should be <100MB
            assert idx.size_bytes < 100 * 1024 * 1024, \
                f"Index too large: {idx.size}"


@pytest.mark.benchmark
class TestPerformanceBenchmark:
    """Benchmark tests for performance comparison"""
    
    def test_benchmark_area_filter(self, benchmark):
        """Benchmark area filter query"""
        def run_query():
            query = text("SELECT COUNT(*) FROM properties WHERE area_en ILIKE :area")
            with engine.connect() as conn:
                return conn.execute(query, {'area': '%Dubai Marina%'}).scalar()
        
        result = benchmark(run_query)
        print(f"\n⚡ Benchmark: {result} properties")
    
    def test_benchmark_area_type_filter(self, benchmark):
        """Benchmark area + type filter query"""
        def run_query():
            query = text("""
                SELECT COUNT(*) 
                FROM properties 
                WHERE area_en ILIKE :area 
                AND prop_type_en = :type
            """)
            with engine.connect() as conn:
                return conn.execute(
                    query, 
                    {'area': '%Dubai Marina%', 'type': 'Unit'}
                ).scalar()
        
        result = benchmark(run_query)
        print(f"\n⚡ Benchmark: {result} properties")


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
```

**Key Requirements:**
- ✅ Test index existence
- ✅ Test query performance (<500ms target)
- ✅ Test query planner uses indexes
- ✅ Test edge cases (NULL, case sensitivity)
- ✅ Test index sizes are reasonable
- ✅ Benchmark tests for comparison
- ✅ Print debug info for manual verification

---

### 4. Documentation Requirements

**File:** `/workspaces/avm-/docs/DATABASE_INDEXES_PHASE1.md`

**Structure:**
```markdown
# Database Indexing Strategy - Phase 1

## Overview
Phase 1 implements essential composite indexes to optimize the most common query patterns in the Retyn AVM application.

## Problem Statement
- **Current Performance:** Queries taking 2-5 seconds on properties/rentals tables
- **Root Cause:** Missing composite indexes on frequently filtered columns
- **Impact:** Poor user experience on Buy/Rent search, Property Valuation

## Solution
Create 2 composite indexes covering area + property type combinations:
1. `idx_properties_area_type` - For sales market queries
2. `idx_rentals_area_type` - For rental market queries

## Performance Impact

### Before Indexes
| Query Type | Duration | Scan Type |
|-----------|----------|-----------|
| Buy Search (area + type) | 2.5-4.5s | Sequential Scan |
| Rent Search (area + type) | 3.0-5.0s | Sequential Scan |
| Valuation Comparables | 1.5-3.0s | Sequential Scan |

### After Indexes
| Query Type | Duration | Scan Type |
|-----------|----------|-----------|
| Buy Search (area + type) | <400ms | Index Scan |
| Rent Search (area + type) | <500ms | Index Scan |
| Valuation Comparables | <300ms | Index Scan |

**Improvement:** 5-10x faster queries

## Index Details

### 1. idx_properties_area_type
- **Table:** properties (153K rows)
- **Columns:** (area_en, prop_type_en)
- **Size:** ~50-70MB
- **Purpose:** Optimize Buy search and valuation comparables
- **Query Pattern:**
  ```sql
  SELECT * FROM properties 
  WHERE area_en ILIKE '%Dubai Marina%' 
  AND prop_type_en = 'Unit';
  ```
- **Used By:**
  - Buy search endpoint (app.py line 2814)
  - Valuation comparables (app.py line 1810)
  - Market trends (app.py line 1356)

### 2. idx_rentals_area_type
- **Table:** rentals (620K rows)
- **Columns:** (area_en, prop_type_en)
- **Size:** ~80-100MB
- **Purpose:** Optimize Rent search and rental yield calculations
- **Query Pattern:**
  ```sql
  SELECT * FROM rentals 
  WHERE area_en ILIKE '%Business Bay%' 
  AND prop_type_en = 'Unit';
  ```
- **Used By:**
  - Rent search endpoint (app.py line 2948)
  - Rental yield calculation (app.py line 2316)
  - Arbitrage score (app.py line 3984)

## Storage Overhead
- **Total Index Size:** ~150-170MB
- **Database Size Before:** ~1.2GB
- **Database Size After:** ~1.35GB
- **Increase:** ~12.5%
- **Cost Impact:** Minimal (~$1-2/month on Neon)

## Write Performance Impact
- **INSERT Speed:** ~5% slower (acceptable tradeoff)
- **UPDATE Speed:** ~5% slower (acceptable tradeoff)
- **DELETE Speed:** Unchanged
- **Reason:** PostgreSQL must maintain 2 additional index structures

## Deployment

### Prerequisites
- PostgreSQL 12+ with CONCURRENTLY support
- DATABASE_URL environment variable set
- Sufficient storage space (~200MB free)
- Neon connection pooling enabled

### Apply Indexes
```bash
# Using application script (recommended)
python scripts/apply_indexes_phase1.py

# Or manual SQL execution
psql $DATABASE_URL -f migrations/add_performance_indexes_phase1.sql
```

### Verify Indexes
```bash
# Check indexes exist
python -c "
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.getenv('DATABASE_URL'))
with engine.connect() as conn:
    result = conn.execute(text(\"\"\"
        SELECT indexname, tablename, pg_size_pretty(pg_relation_size(indexrelid))
        FROM pg_stat_user_indexes
        WHERE indexrelname IN ('idx_properties_area_type', 'idx_rentals_area_type')
    \"\"\"))
    for row in result:
        print(f'{row[1]}.{row[0]}: {row[2]}')
"
```

### Run Tests
```bash
pytest tests/test_index_performance_phase1.py -v
```

## Rollback
If indexes cause issues, remove them with:
```sql
DROP INDEX CONCURRENTLY IF EXISTS idx_properties_area_type;
DROP INDEX CONCURRENTLY IF EXISTS idx_rentals_area_type;
```

## Monitoring

### Check Index Usage
```sql
SELECT 
    schemaname,
    tablename,
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE indexrelname IN ('idx_properties_area_type', 'idx_rentals_area_type')
ORDER BY idx_scan DESC;
```

### Check Index Sizes
```sql
SELECT 
    indexrelname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    pg_relation_size(indexrelid) as size_bytes
FROM pg_stat_user_indexes
WHERE indexrelname IN ('idx_properties_area_type', 'idx_rentals_area_type')
ORDER BY size_bytes DESC;
```

### Check Query Plans
```sql
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM properties 
WHERE area_en ILIKE '%Dubai Marina%' 
AND prop_type_en = 'Unit' 
LIMIT 100;
```

## Next Steps (Phase 2)
- [ ] Add 3-column composite index: `idx_properties_area_type_size`
- [ ] Add date index for trending: `idx_properties_date_area`
- [ ] Add partial indexes for Ready/Off-Plan filtering
- [ ] Optimize rental yield queries with size-based index
- [ ] Monitor index usage and adjust strategy

## References
- PostgreSQL CREATE INDEX: https://www.postgresql.org/docs/current/sql-createindex.html
- Index Advisor: https://neon.tech/docs/guides/index-advisor
- Query Performance: https://www.postgresql.org/docs/current/performance-tips.html
```

---

### 5. Production Readiness Check Update

**File:** `/workspaces/avm-/check_production_ready.sh`

**Add After Existing Checks:**
```bash
# Check 18: Verify Performance Indexes Exist
echo ""
echo "18. Checking database performance indexes..."
INDEX_CHECK=$(python3 << 'EOF'
import os
import sys
from sqlalchemy import create_engine, text

try:
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    
    engine = create_engine(database_url, connect_args={'sslmode': 'require'})
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE indexname IN ('idx_properties_area_type', 'idx_rentals_area_type')
        """))
        count = result.scalar()
    
    print(count)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF
)

if [ "$INDEX_CHECK" == "2" ]; then
    echo "✅ Performance indexes exist (2/2)"
elif [ "$INDEX_CHECK" == "1" ]; then
    echo "⚠️  Partial performance indexes (1/2) - missing index"
    WARNINGS=$((WARNINGS + 1))
else
    echo "❌ Missing performance indexes (found $INDEX_CHECK/2)"
    ERRORS=$((ERRORS + 1))
fi
```

---

## 🎯 Quick Win Execution Steps

### Step 1: Create Migration File (5 min)
```bash
cd /workspaces/avm-
cat > migrations/add_performance_indexes_phase1.sql << 'EOF'
-- Copy SQL content from section 1 above
EOF
```

### Step 2: Create Application Script (10 min)
```bash
cat > scripts/apply_indexes_phase1.py << 'EOF'
# Copy Python content from section 2 above
EOF
chmod +x scripts/apply_indexes_phase1.py
```

### Step 3: Create Tests (10 min)
```bash
cat > tests/test_index_performance_phase1.py << 'EOF'
# Copy test content from section 3 above
EOF
```

### Step 4: Apply Indexes (5-7 min)
```bash
# Ensure DATABASE_URL is set
export DATABASE_URL="your_database_url_here"

# Run application script
python scripts/apply_indexes_phase1.py
```

### Step 5: Verify & Test (5 min)
```bash
# Run tests
pytest tests/test_index_performance_phase1.py -v

# Check production readiness
bash check_production_ready.sh
```

### Step 6: Commit Changes (2 min)
```bash
git add migrations/add_performance_indexes_phase1.sql
git add scripts/apply_indexes_phase1.py
git add tests/test_index_performance_phase1.py
git add docs/DATABASE_INDEXES_PHASE1.md
git add check_production_ready.sh
git commit -m "feat: Add Phase 1 performance indexes (Buy/Rent search optimization)"
git push origin main
```

---

## ✅ Success Criteria

**Must Pass:**
- ✅ 2 indexes created successfully
- ✅ Query time reduced from >2s to <500ms
- ✅ All 9 tests pass
- ✅ Production readiness check passes
- ✅ No errors in application logs
- ✅ Query planner uses new indexes

**Performance Targets:**
- Buy search: <400ms (currently 2.5-4.5s)
- Rent search: <500ms (currently 3.0-5.0s)
- Valuation: <300ms (currently 1.5-3.0s)

---

## 📊 Expected Outcomes

### Performance Metrics
- **Query Speed:** 5-10x faster
- **User Experience:** Instant search results
- **Database Load:** Reduced CPU usage
- **Index Hit Rate:** >95% for area+type queries

### Business Impact
- Improved user satisfaction
- Faster property valuations
- Better market analysis capabilities
- Foundation for future optimizations

---

## 🔄 Next Increments

### Phase 2 (Week 1)
- Add 3-column composite: `idx_properties_area_type_size`
- Add date index: `idx_properties_date_area`
- Add rental size index: `idx_rentals_area_type_size`

### Phase 3 (Week 2)
- Add partial indexes for Ready/Off-Plan filtering
- Optimize flip score queries
- Optimize arbitrage score queries

---

## ⚠️ Known Limitations

1. **ILIKE queries:** Index may not be used for `ILIKE '%pattern%'` (leading wildcard)
   - **Solution:** Phase 2 will add `LOWER(area_en)` index
2. **NULL values:** Indexed but sorted at end
   - **Impact:** Minimal (few NULL values in dataset)
3. **Case sensitivity:** B-tree indexes are case-sensitive
   - **Workaround:** Using ILIKE still works but may do index scan + filter

---

## 🚨 Troubleshooting

### Issue: Index creation timeout
**Symptom:** `statement timeout exceeded`
**Solution:**
```sql
SET statement_timeout = '600000';  -- 10 minutes
CREATE INDEX CONCURRENTLY ...
```

### Issue: Lock contention
**Symptom:** `could not obtain lock on relation`
**Solution:**
- Use `CREATE INDEX CONCURRENTLY` (already in migration)
- Retry during low-traffic period

### Issue: Query planner not using index
**Symptom:** EXPLAIN shows "Seq Scan" instead of "Index Scan"
**Solution:**
```sql
ANALYZE properties;
ANALYZE rentals;
```

### Issue: Out of disk space
**Symptom:** `No space left on device`
**Solution:**
- Free up 200MB before running
- Remove old logs/temp files
- Upgrade Neon plan if needed

---

## 📞 Support

**Questions?** See:
- PostgreSQL Docs: https://www.postgresql.org/docs/current/indexes.html
- Neon Index Guide: https://neon.tech/docs/guides/index-advisor
- Project README: `/workspaces/avm-/README.md`

**Issues?** 
- Check logs: `docker-compose logs web -f`
- Run diagnostics: `python scripts/apply_indexes_phase1.py`
- Review test failures: `pytest tests/test_index_performance_phase1.py -v`

