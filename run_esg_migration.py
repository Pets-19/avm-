#!/usr/bin/env python3
"""
Run ESG column migration using SQLAlchemy
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    exit(1)

print("🔗 Connecting to database...")
engine = create_engine(DATABASE_URL, echo=False)

# Read migration file
print("📄 Reading migration SQL...")
with open('migrations/add_esg_column.sql', 'r') as f:
    sql_content = f.read()

# Split into individual statements (skip comments and empty lines)
statements = []
current_statement = []
for line in sql_content.split('\n'):
    line = line.strip()
    # Skip comments and empty lines
    if not line or line.startswith('--'):
        continue
    current_statement.append(line)
    # If line ends with semicolon, it's end of statement
    if line.endswith(';'):
        statements.append(' '.join(current_statement))
        current_statement = []

print(f"📊 Found {len(statements)} SQL statements to execute\n")

# Execute each statement
try:
    with engine.connect() as conn:
        for i, statement in enumerate(statements, 1):
            # Show first 80 chars of statement
            preview = statement[:80] + '...' if len(statement) > 80 else statement
            print(f"[{i}/{len(statements)}] Executing: {preview}")
            
            try:
                result = conn.execute(text(statement))
                
                # Check if it's a SELECT query
                if statement.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    print(f"   ✅ Returned {len(rows)} row(s)")
                    # Show first 3 rows
                    for row in rows[:3]:
                        row_dict = {key: value for key, value in zip(result.keys(), row)}
                        print(f"      {row_dict}")
                else:
                    print(f"   ✅ Success")
                    
                conn.commit()
            except Exception as e:
                # If error is "column already exists", it's okay
                if 'already exists' in str(e).lower():
                    print(f"   ⚠️  Already exists (skipping): {str(e)[:100]}")
                else:
                    print(f"   ❌ Error: {e}")
                    raise
    
    print("\n" + "="*60)
    print("✅ ESG Migration completed successfully!")
    print("="*60)
    
    # Final verification
    print("\n🔍 Verifying ESG column...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                COUNT(*) as total_properties,
                COUNT(esg_score) as with_esg,
                MIN(esg_score) as min_esg,
                MAX(esg_score) as max_esg,
                AVG(esg_score)::NUMERIC(10,2) as avg_esg
            FROM properties
        """))
        row = result.fetchone()
        print(f"\n📊 Database Status:")
        print(f"   Total properties: {row[0]:,}")
        print(f"   With ESG scores: {row[1]:,}")
        print(f"   ESG range: {row[2]} - {row[3]}")
        print(f"   Average ESG: {row[4]}")
        
except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    exit(1)
