"""
Dubai Property Valuation Engine - Production Database Version
Uses full 130K+ Dubai transaction database for automated property valuations
"""
import pandas as pd
import numpy as np
from datetime import datetime
import os
from sqlalchemy import create_engine, text

# Database connection (same as main app)
DATABASE_URL = os.getenv('DATABASE_URL')
_engine = None
_dataset_cache = {}

def get_database_engine():
    """Get database engine using same configuration as main app"""
    global _engine
    if _engine is None and DATABASE_URL:
        try:
            # Use same connection settings as main app
            _engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_size=2,
                max_overflow=5,
                pool_timeout=30,
                pool_recycle=1800,
                connect_args={
                    'sslmode': 'require',
                    'connect_timeout': 10,
                    'keepalives': 1,
                    'keepalives_idle': 30,
                    'keepalives_interval': 10,
                    'keepalives_count': 5
                }
            )
        except Exception as e:
            print(f"Database engine creation failed: {e}")
            return None
    return _engine

def load_dubai_dataset_from_db():
    """Load Dubai property data from production database"""
    global _dataset_cache
    
    # Use cache key based on current hour to refresh periodically
    cache_key = f"properties_{datetime.now().hour}"
    
    if cache_key not in _dataset_cache:
        engine = get_database_engine()
        if engine is None:
            raise Exception("Database connection not available")
        
        # SQL query to get sales data from properties table
        query = """
        SELECT 
            area_en as area_name_en,
            prop_type_en as property_type_en,
            trans_value as property_total_value,
            actual_area,
            rooms_en,
            instance_date,
            is_offplan_en,
            project_en
        FROM properties 
        WHERE 
            trans_value > 0 
            AND actual_area > 0 
            AND area_en IS NOT NULL 
            AND prop_type_en IS NOT NULL
            AND trans_value BETWEEN 100000 AND 50000000  -- Reasonable price range
            AND actual_area BETWEEN 20 AND 2000  -- Reasonable area range
        ORDER BY instance_date DESC
        """
        
        try:
            with engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn)
                
            # Data cleaning and preparation
            df = df.dropna(subset=['property_total_value', 'actual_area'])
            df = df[df['property_total_value'] > 0]
            df = df[df['actual_area'] > 0]
            
            # Add calculated fields
            df['price_per_sqm'] = df['property_total_value'] / df['actual_area']
            df['transaction_year'] = pd.to_datetime(df['instance_date'], errors='coerce').dt.year
            
            # Remove outliers (properties with price per sqm outside reasonable range)
            q1 = df['price_per_sqm'].quantile(0.1)
            q3 = df['price_per_sqm'].quantile(0.9)
            df = df[(df['price_per_sqm'] >= q1) & (df['price_per_sqm'] <= q3)]
            
            _dataset_cache[cache_key] = df
            print(f"✅ Loaded {len(df):,} property records from database")
            
        except Exception as e:
            print(f"❌ Database query failed: {e}")
            # Fallback to CSV if database fails
            return load_dubai_dataset_from_csv()
    
    return _dataset_cache[cache_key]

def load_dubai_dataset_from_csv():
    """Fallback: Load Dubai dataset from CSV file"""
    csv_path = 'static/valuation_data/Valuation - Dubai.csv'
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=['property_total_value', 'actual_area'])
        df = df[df['property_total_value'] > 0]
        df = df[df['actual_area'] > 0]
        print(f"⚠️ Using CSV fallback with {len(df)} records")
        return df
    else:
        raise FileNotFoundError(f"No dataset available - neither database nor CSV found")

def load_dubai_dataset():
    """Main function to load Dubai dataset - tries database first, then CSV"""
    try:
        return load_dubai_dataset_from_db()
    except Exception as e:
        print(f"Database load failed: {e}")
        return load_dubai_dataset_from_csv()

def find_comparable_properties(property_data, max_comparables=10):
    """Find comparable properties using enhanced statistical filtering"""
    df = load_dubai_dataset()
    
    print(f"🔍 Searching in dataset of {len(df):,} properties")
    
    # Start with area filtering (case-insensitive)
    area_name = property_data.get('area_name', '').lower()
    area_matches = df[df['area_name_en'].str.lower() == area_name]
    
    print(f"🏢 Found {len(area_matches)} properties in '{property_data.get('area_name', '')}'")
    
    # Filter by property type
    if property_data.get('property_type'):
        type_matches = area_matches[
            area_matches['property_type_en'].str.lower() == property_data['property_type'].lower()
        ]
        print(f"🏠 Found {len(type_matches)} {property_data['property_type']} properties in area")
    else:
        type_matches = area_matches
    
    # Size filtering (±30% range)
    target_size = property_data.get('area_sqm', 100)
    size_range = (target_size * 0.7, target_size * 1.3)
    size_matches = type_matches[
        (type_matches['actual_area'] >= size_range[0]) & 
        (type_matches['actual_area'] <= size_range[1])
    ]
    
    print(f"📐 Found {len(size_matches)} properties in size range {size_range[0]:.0f}-{size_range[1]:.0f} sqm")
    
    # If we have enough area+type+size matches, use them
    if len(size_matches) >= 3:
        comparables = size_matches.head(max_comparables)
        confidence_base = 95
        search_scope = f"area-specific ({property_data.get('area_name', '')})"
    
    # Otherwise, expand to area+type (ignore size restriction)
    elif len(type_matches) >= 3:
        comparables = type_matches.head(max_comparables)
        confidence_base = 88
        search_scope = f"area-wide ({property_data.get('area_name', '')})"
    
    # Otherwise, expand to area-wide (all property types)
    elif len(area_matches) >= 3:
        comparables = area_matches.head(max_comparables)
        confidence_base = 82
        search_scope = f"area-wide (all types)"
    
    # Last resort: city-wide search for same property type
    else:
        city_type_matches = df[
            df['property_type_en'].str.lower() == property_data.get('property_type', '').lower()
        ]
        # Apply size filtering for city-wide search
        city_size_matches = city_type_matches[
            (city_type_matches['actual_area'] >= size_range[0]) & 
            (city_type_matches['actual_area'] <= size_range[1])
        ]
        
        if len(city_size_matches) >= 3:
            comparables = city_size_matches.head(max_comparables)
            confidence_base = 75
            search_scope = "city-wide (same type & size)"
        else:
            comparables = city_type_matches.head(max_comparables)
            confidence_base = 70
            search_scope = "city-wide (same type)"
    
    print(f"✅ Selected {len(comparables)} comparables using {search_scope} search")
    
    return comparables, confidence_base

def calculate_confidence_score(comparables, base_confidence, property_data):
    """Calculate confidence score based on data quality"""
    if len(comparables) == 0:
        return 0
    
    confidence = base_confidence
    
    # Bonus for more comparables
    if len(comparables) >= 10:
        confidence += 5
    elif len(comparables) >= 5:
        confidence += 2
    
    # Bonus for recent data
    if 'transaction_year' in comparables.columns:
        recent_years = comparables['transaction_year'] >= (datetime.now().year - 2)
        if recent_years.sum() > len(comparables) * 0.5:
            confidence += 3
    
    # Penalty for high price variance
    price_variance = comparables['property_total_value'].std() / comparables['property_total_value'].mean()
    if price_variance > 0.3:
        confidence -= 5
    elif price_variance < 0.15:
        confidence += 3
    
    return min(max(confidence, 50), 98)  # Keep between 50-98%

def calculate_valuation(property_type: str, area: str, size_sqm: float) -> dict:
    """
    Calculate property valuation using production database
    
    Args:
        property_type: Type of property (Unit, Villa, etc.)
        area: Area name in Dubai
        size_sqm: Property size in square meters
    
    Returns:
        Dictionary containing valuation results
    """
    try:
        # Prepare property data
        property_data = {
            'property_type': property_type,
            'area_name': area,
            'area_sqm': size_sqm
        }
        
        print(f"🏗️ Calculating valuation for {size_sqm}sqm {property_type} in {area}")
        
        # Find comparable properties
        comparables, base_confidence = find_comparable_properties(property_data)
        
        if len(comparables) == 0:
            raise ValueError(f"No comparable properties found for {property_type} in {area}")
        
        # Statistical valuation calculation
        median_price = comparables['property_total_value'].median()
        mean_price = comparables['property_total_value'].mean()
        
        # Use median as primary estimate (more robust against outliers)
        estimated_value = median_price
        
        # Adjust based on size if we have size-similar properties
        if size_sqm > 0:
            median_price_per_sqm = (comparables['property_total_value'] / comparables['actual_area']).median()
            size_based_estimate = median_price_per_sqm * size_sqm
            
            # Blend estimates (70% median price, 30% size-based)
            estimated_value = 0.7 * median_price + 0.3 * size_based_estimate
        
        # Calculate confidence score
        confidence = calculate_confidence_score(comparables, base_confidence, property_data)
        
        # Calculate value range (confidence interval)
        std_dev = comparables['property_total_value'].std()
        margin = std_dev * 0.15  # ±15% based on standard deviation
        
        # Prepare comparable properties for response
        comparable_list = []
        for _, comp in comparables.head(5).iterrows():  # Top 5 for response
            comparable_list.append({
                'area_name': comp.get('area_name_en', 'N/A'),
                'property_type': comp.get('property_type_en', 'N/A'),
                'area_sqm': float(comp.get('actual_area', 0)),
                'sold_price': float(comp.get('property_total_value', 0)),
                'price_per_sqm': float(comp.get('property_total_value', 0) / comp.get('actual_area', 1)),
                'transaction_year': int(comp.get('transaction_year', 2024)) if pd.notna(comp.get('transaction_year')) else 2024
            })
        
        result = {
            'success': True,
            'valuation': {
                'estimated_value': round(estimated_value),
                'confidence_score': round(confidence, 1),
                'price_per_sqm': round(estimated_value / size_sqm) if size_sqm > 0 else 0,
                'value_range': {
                    'low': round(estimated_value - margin),
                    'high': round(estimated_value + margin)
                },
                'comparables': comparable_list,
                'total_comparables_found': len(comparables),
                'valuation_date': datetime.now().isoformat(),
                'data_source': f"Database ({len(load_dubai_dataset()):,} properties)"
            }
        }
        
        print(f"💰 Valuation complete: {estimated_value:,.0f} AED ({confidence:.1f}% confidence)")
        return result
        
    except Exception as e:
        print(f"❌ Valuation error: {e}")
        return {
            'success': False,
            'error': str(e),
            'valuation': None
        }

if __name__ == "__main__":
    # Test the production valuation engine
    print("🧪 Testing Production Valuation Engine")
    result = calculate_valuation("Unit", "Business Bay", 130)
    print("Result:", result)