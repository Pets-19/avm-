#!/usr/bin/env python3
"""
Flip Score Migration Runner
Execute add_flip_score_column.sql migration using SQLAlchemy
(psql command not available in this environment)
"""

import os
import sys
from pathlib import Path
from sqlalchemy import text
from decimal import Decimal

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app import engine

def run_migration():
    """Execute flip score migration SQL"""
    
    migration_file = Path(__file__).parent / 'migrations' / 'add_flip_score_column.sql'
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    print(f"🔗 Connecting to database...")
    print(f"📄 Reading migration SQL from: {migration_file}")
    
    # Read SQL file
    with open(migration_file, 'r') as f:
        sql_content = f.read()
    
    # Split into individual statements (by semicolon, excluding comments)
    statements = []
    current_statement = []
    
    for line in sql_content.split('\n'):
        # Skip pure comment lines
        if line.strip().startswith('--') or line.strip() == '':
            continue
        
        current_statement.append(line)
        
        # If line ends with semicolon, it's end of statement
        if line.strip().endswith(';'):
            statement = '\n'.join(current_statement)
            if statement.strip():
                statements.append(statement)
            current_statement = []
    
    print(f"📊 Found {len(statements)} SQL statements to execute\n")
    
    # Execute each statement
    success_count = 0
    error_count = 0
    
    with engine.connect() as conn:
        for i, statement in enumerate(statements, 1):
            try:
                # Show first 100 chars of statement
                preview = statement.strip()[:100].replace('\n', ' ')
                print(f"[{i}/{len(statements)}] Executing: {preview}...")
                
                result = conn.execute(text(statement))
                conn.commit()
                
                # If SELECT statement, show results
                if statement.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    if rows:
                        print(f"    ✅ Returned {len(rows)} row(s)")
                        for row in rows[:5]:  # Show first 5 rows
                            print(f"      {dict(row._mapping)}")
                    else:
                        print(f"    ✅ Query executed successfully (0 rows)")
                else:
                    print(f"    ✅ Success")
                
                success_count += 1
                
            except Exception as e:
                # Check if it's a harmless "already exists" error
                if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                    print(f"    ⚠️  Already exists (skipping): {e}")
                    success_count += 1
                else:
                    print(f"    ❌ Error: {e}")
                    error_count += 1
    
    print("\n" + "="*60)
    if error_count == 0:
        print("✅ Flip Score Migration completed successfully!")
    else:
        print(f"⚠️  Migration completed with {error_count} error(s)")
    print("="*60)
    
    # Final verification
    print("\n📊 Database Status:")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_properties,
                COUNT(flip_score) as with_flip,
                MIN(flip_score) as min_flip,
                MAX(flip_score) as max_flip,
                ROUND(AVG(flip_score), 2) as avg_flip
            FROM properties
        """))
        row = result.fetchone()
        print(f"   Total properties: {row[0]:,}")
        print(f"   With flip scores: {row[1]:,}")
        if row[1] > 0:
            print(f"   Flip range: {row[2]} - {row[3]}")
            print(f"   Average flip: {row[4]}")
    
    return error_count == 0

if __name__ == "__main__":
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
