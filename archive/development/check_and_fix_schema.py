import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={'sslmode': 'require'})

print("🔍 Checking area_coordinates table structure...\n")

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'area_coordinates'
        ORDER BY ordinal_position
    """))
    
    print("Current columns:")
    cols = []
    for row in result:
        cols.append(row[0])
        print(f"  - {row[0]}: {row[1]}")
    
    # Check what's missing
    required_cols = ['distance_to_metro_km', 'distance_to_beach_km', 'distance_to_mall_km', 
                     'distance_to_school_km', 'distance_to_business_km', 'neighborhood_score']
    missing = [c for c in required_cols if c not in cols]
    
    if missing:
        print(f"\n⚠️  Missing columns: {', '.join(missing)}")
        print("\n🔧 Adding missing columns...")
        
        for col in missing:
            try:
                if col == 'neighborhood_score':
                    conn.execute(text(f"ALTER TABLE area_coordinates ADD COLUMN {col} DECIMAL(3, 2) DEFAULT 3.5"))
                else:
                    conn.execute(text(f"ALTER TABLE area_coordinates ADD COLUMN {col} DECIMAL(5, 2)"))
                conn.commit()
                print(f"  ✅ Added {col}")
            except Exception as e:
                print(f"  ❌ Failed to add {col}: {e}")
    else:
        print("\n✅ All required columns present")

engine.dispose()
