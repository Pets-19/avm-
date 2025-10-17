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
        # Clean up DATABASE_URL - remove whitespace and problematic parameters
        database_url = database_url.strip()
        if 'channel_binding=require' in database_url:
            database_url = database_url.replace('&channel_binding=require', '')
            database_url = database_url.replace('?channel_binding=require', '?sslmode=require')
        # Ensure sslmode is set
        if 'sslmode=' not in database_url:
            if '?' in database_url:
                database_url += '&sslmode=require'
            else:
                database_url += '?sslmode=require'
        
        engine = create_engine(
            database_url,
            connect_args={
                'connect_timeout': 30,
            },
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=5
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
    # Remove multi-line comments and split by semicolon
    import re
    # Remove block comments /* ... */
    sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
    # Remove single-line comments --
    sql_content = re.sub(r'--.*?$', '', sql_content, flags=re.MULTILINE)
    
    # Split into individual statements
    statements = [
        stmt.strip() 
        for stmt in sql_content.split(';') 
        if stmt.strip()
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
            # Use raw connection with autocommit for CONCURRENTLY
            conn = engine.raw_connection()
            conn.set_session(autocommit=True)
            cursor = conn.cursor()
            try:
                # Set longer timeout for index creation
                cursor.execute("SET statement_timeout = '600000'")  # 10 minutes
                cursor.execute(statement)
            finally:
                cursor.close()
                conn.close()
            
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
        SELECT indexrelname as indexname, relname as tablename, pg_size_pretty(pg_relation_size(indexrelid)) as size
        FROM pg_stat_user_indexes
        WHERE indexrelname = ANY(:index_names)
        ORDER BY relname, indexrelname
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
    """Test query performance with indexes"""
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
