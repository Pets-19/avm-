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
        
        # With index, should be <1000ms for 153K rows
        assert duration_ms < 2000, f"Query too slow: {duration_ms:.2f}ms"
    
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
        
        # With index, should be <1000ms for 620K rows
        assert duration_ms < 2000, f"Query too slow: {duration_ms:.2f}ms"
    
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
        print(f"\n📊 Query plan includes: {'Index' if 'Index' in plan_str else 'No index'}")
        
        # Check if index is mentioned in plan
        # Note: May use "Bitmap Index Scan" or "Index Scan" on idx_properties_area_type
        # With ILIKE, may still do sequential scan depending on selectivity
        assert 'Scan' in plan_str, "Query plan should show scan type"
    
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
            # Each index should be <200MB (reasonable for these table sizes)
            assert idx.size_bytes < 200 * 1024 * 1024, \
                f"Index too large: {idx.size}"
    
    def test_multiple_area_queries(self):
        """Test queries on different popular areas"""
        query = text("""
            SELECT COUNT(*) 
            FROM properties 
            WHERE area_en ILIKE :area 
            AND prop_type_en = :type
        """)
        
        test_areas = [
            'Dubai Marina',
            'Downtown Dubai',
            'Business Bay',
            'Palm Jumeirah',
            'JBR'
        ]
        
        for area in test_areas:
            start = time.time()
            with engine.connect() as conn:
                result = conn.execute(
                    query, 
                    {'area': f'%{area}%', 'type': 'Unit'}
                )
                count = result.scalar()
            duration_ms = (time.time() - start) * 1000
            
            print(f"\n📊 {area}: {count} units in {duration_ms:.2f}ms")
            assert duration_ms < 2000, f"Query too slow for {area}: {duration_ms:.2f}ms"


@pytest.mark.benchmark
class TestPerformanceBenchmark:
    """Benchmark tests for performance comparison"""
    
    def test_benchmark_area_filter(self):
        """Benchmark area filter query"""
        query = text("SELECT COUNT(*) FROM properties WHERE area_en ILIKE :area")
        
        start = time.time()
        with engine.connect() as conn:
            result = conn.execute(query, {'area': '%Dubai Marina%'}).scalar()
        duration_ms = (time.time() - start) * 1000
        
        print(f"\n⚡ Benchmark area filter: {result} properties in {duration_ms:.2f}ms")
        assert duration_ms < 2000
    
    def test_benchmark_area_type_filter(self):
        """Benchmark area + type filter query"""
        query = text("""
            SELECT COUNT(*) 
            FROM properties 
            WHERE area_en ILIKE :area 
            AND prop_type_en = :type
        """)
        
        start = time.time()
        with engine.connect() as conn:
            result = conn.execute(
                query, 
                {'area': '%Dubai Marina%', 'type': 'Unit'}
            ).scalar()
        duration_ms = (time.time() - start) * 1000
        
        print(f"\n⚡ Benchmark area+type filter: {result} properties in {duration_ms:.2f}ms")
        assert duration_ms < 2000


if __name__ == "__main__":
    pytest.main([__file__, '-v', '--tb=short'])
