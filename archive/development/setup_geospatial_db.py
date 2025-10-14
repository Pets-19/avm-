#!/usr/bin/env python3
"""
Geospatial Database Setup Script
Executes the SQL setup file using the Flask app's database connection
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    sys.exit(1)

print("🔄 Connecting to database...")

try:
    # Create engine (same config as app.py)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=5,
        pool_timeout=30,
        connect_args={
            'sslmode': 'require',
            'connect_timeout': 10
        }
    )
    
    # Test connection
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("✅ Database connected")
    
    # Read SQL file
    print("\n🔄 Reading SQL setup file...")
    with open('sql/geospatial_setup.sql', 'r') as f:
        sql_script = f.read()
    
    # Split into individual statements (skip comments and empty lines)
    statements = []
    current_statement = []
    
    for line in sql_script.split('\n'):
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('--'):
            continue
        
        current_statement.append(line)
        
        # If line ends with semicolon, it's end of statement
        if line.endswith(';'):
            statements.append(' '.join(current_statement))
            current_statement = []
    
    print(f"✅ Found {len(statements)} SQL statements\n")
    
    # Execute statements (each in its own transaction)
    for i, statement in enumerate(statements, 1):
        try:
            # Skip SELECT verification queries for now
            if statement.strip().upper().startswith('SELECT'):
                continue
            
            with engine.connect() as conn:
                conn.execute(text(statement))
                conn.commit()
            
            # Show progress for major operations
            if 'CREATE TABLE' in statement.upper():
                table_name = statement.split('TABLE')[1].split('(')[0].strip().split()[0].replace('IF NOT EXISTS', '').strip()
                print(f"✅ [{i}/{len(statements)}] Created table: {table_name}")
            elif 'INSERT INTO' in statement.upper():
                table_name = statement.split('INTO')[1].split('(')[0].strip().split()[0]
                print(f"✅ [{i}/{len(statements)}] Inserted data into: {table_name}")
            elif 'CREATE INDEX' in statement.upper():
                print(f"✅ [{i}/{len(statements)}] Created index")
            else:
                print(f"✅ [{i}/{len(statements)}] Executed statement")
                
        except Exception as e:
            # Check if it's a "already exists" error (which is OK)
            if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
                print(f"⚠️  [{i}/{len(statements)}] Already exists (skipping)")
            else:
                print(f"❌ [{i}/{len(statements)}] Error: {e}")
                # Continue with next statement
    
    # Verification
    print("\n🔍 Verifying setup...")
    with engine.connect() as conn:
        # Check area_coordinates
        result = conn.execute(text("SELECT COUNT(*) FROM area_coordinates"))
        area_count = result.fetchone()[0]
        print(f"✅ Areas loaded: {area_count}")
        
        # Check amenities by type
        result = conn.execute(text("""
            SELECT type, COUNT(*) 
            FROM amenities 
            WHERE active = TRUE 
            GROUP BY type 
            ORDER BY type
        """))
        print(f"✅ Amenities loaded:")
        for row in result:
            print(f"   - {row[0]}: {row[1]} locations")
        
        # Check cache table
        result = conn.execute(text("SELECT COUNT(*) FROM property_location_cache"))
        cache_count = result.fetchone()[0]
        print(f"✅ Cache entries: {cache_count}")
        
        # Show sample premiums
        result = conn.execute(text("""
            SELECT 
                area_name,
                ROUND(
                    GREATEST(0, 15 - (COALESCE(distance_to_metro_km, 10) * 3)) +
                    GREATEST(0, 30 - (COALESCE(distance_to_beach_km, 10) * 6)) +
                    GREATEST(0, 8 - (COALESCE(distance_to_mall_km, 10) * 2)),
                    2
                ) as estimated_premium_pct,
                distance_to_metro_km,
                distance_to_beach_km
            FROM area_coordinates
            ORDER BY estimated_premium_pct DESC
            LIMIT 5
        """))
        
        print(f"\n📊 Top 5 Areas by Estimated Premium:")
        print(f"{'Area':<30} {'Premium':<10} {'Metro(km)':<12} {'Beach(km)'}")
        print("-" * 65)
        for row in result:
            print(f"{row[0]:<30} {row[1]:>7}% {row[2]:>10.2f} {row[3]:>10.2f}")
    
    print("\n🎉 Geospatial database setup complete!")
    print("\n📝 Next steps:")
    print("   1. Review the setup (areas and amenities loaded)")
    print("   2. Add geospatial functions to app.py")
    print("   3. Integrate into valuation endpoint")
    
except Exception as e:
    print(f"\n❌ Setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    if 'engine' in locals():
        engine.dispose()
