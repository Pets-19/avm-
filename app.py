# app.py (OpenAI Integration Version)
import os
import sqlite3
import logging
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session, Response
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import time
import json
import re
import pandas as pd
import numpy as np
import joblib
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import hashlib
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2

# --- Configuration ---
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- ML Model Loading ---
ml_model = None
ml_encoders = None
ml_feature_columns = None
USE_ML = False

try:
    ml_model = joblib.load('models/xgboost_model_v1.pkl')
    ml_encoders = joblib.load('models/label_encoders_v1.pkl')
    ml_feature_columns = joblib.load('models/feature_columns_v1.pkl')
    USE_ML = True
    print("✅ ML model loaded successfully")
except Exception as e:
    print(f"⚠️ ML model not loaded: {e}. Using rule-based pricing only.")
    USE_ML = False

# --- AI Configuration ---
USE_AI_SUMMARY = True
openai_client = None

if OPENAI_API_KEY:
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        print("✅ OpenAI API key configured successfully.")
    except Exception as e:
        print(f"⚠️ OpenAI client initialization failed: {e}")
        USE_AI_SUMMARY = False
else:
    print("⚠️ OpenAI API key not found. AI summary will be disabled.")
    USE_AI_SUMMARY = False

# --- Database Engine ---
engine = None
if DATABASE_URL:
    try:
        # Connection settings optimized for Neon serverless
        engine = create_engine(
            DATABASE_URL,
            echo=True,  # Enable debug logging
            pool_pre_ping=True,  # Enable connection health checks
            pool_size=2,  # Reduced pool size
            max_overflow=5,  # Reduced max overflow
            pool_timeout=30,
            pool_recycle=1800,  # Recycle connections every 30 minutes
            connect_args={
                'sslmode': 'require',  # Force SSL mode
                'connect_timeout': 10,
                'keepalives': 1,       # Enable keepalive
                'keepalives_idle': 30,  # Idle time before sending keepalive
                'keepalives_interval': 10,  # Interval between keepalives
                'keepalives_count': 5   # Max number of keepalive retries
            }
        )
        # Test the connection immediately
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection test successful")
        print("✅ Database engine created successfully.")
    except Exception as e:
        print(f"❌ Failed to create database engine: {e}")
        # Try alternative connection string format
        try:
            if 'postgresql://' in DATABASE_URL:
                alt_url = DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://')
                engine = create_engine(
                    alt_url,
                    pool_pre_ping=True,
                    pool_size=2,
                    connect_args={'sslmode': 'require'}
                )
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                print("✅ Database connection successful with alternative URL")
        except Exception as e2:
            print(f"❌ Alternative connection also failed: {e2}")
else:
    print("❌ DATABASE_URL not found. The application cannot start.")

# --- Dynamic Column Mapping ---
def get_table_columns(table_name):
    if not engine: return []
    try:
        with engine.connect() as conn:
            from sqlalchemy.inspection import inspect
            inspector = inspect(engine)
            return [col['name'] for col in inspector.get_columns(table_name)]
    except Exception as e:
        print(f"⚠️ Could not inspect columns for table '{table_name}': {e}")
        return []

def find_column_name(all_columns, potential_matches):
    for match in potential_matches:
        if match in all_columns:
            return match
    return potential_matches[0]

SALES_COLUMNS = get_table_columns('properties')
RENTALS_COLUMNS = get_table_columns('rentals')

print(f"🔍 SALES COLUMNS: {SALES_COLUMNS}")
print(f"🔍 RENTALS COLUMNS: {RENTALS_COLUMNS}")

SALES_MAP = {
    'price': find_column_name(SALES_COLUMNS, ['trans_value', 'price']),
    'property_type': find_column_name(SALES_COLUMNS, ['prop_type_en', 'prop_sub_type_en', 'property_type']),
    'bedrooms': find_column_name(SALES_COLUMNS, ['rooms_en', 'bedrooms']),
    'status': find_column_name(SALES_COLUMNS, ['is_offplan_en', 'development_status']),
    'area_name': find_column_name(SALES_COLUMNS, ['area_en']),
    'name': find_column_name(SALES_COLUMNS, ['project_en', 'procedure_en', 'property_name']),
}

# --- EXPANDED RENTAL COLUMN SEARCH ---
RENTALS_MAP = {
    'price': find_column_name(RENTALS_COLUMNS, ['annual_amount', 'annual_rent', 'rent_amount', 'amount', 'price', 'rent']),
    'property_type': find_column_name(RENTALS_COLUMNS, ['prop_type_en', 'prop_sub_type_en', 'property_type', 'type']),
    'property_sub_type': find_column_name(RENTALS_COLUMNS, ['prop_sub_type_en', 'property_sub_type', 'sub_type']),
    'area_name': find_column_name(RENTALS_COLUMNS, ['area_en', 'area', 'location']),
    'name': find_column_name(RENTALS_COLUMNS, ['project_en', 'name', 'property_name']),
}

print(f"🔍 SALES MAP: {SALES_MAP}")
print(f"🔍 RENTALS MAP: {RENTALS_MAP}")


app = Flask(__name__, template_folder='templates', static_folder='static')

# --- Authentication Configuration ---
app.secret_key = os.getenv("SECRET_KEY", "retyn-avm-secure-key-2025")  # Use environment variable in production
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this application.'
login_manager.login_message_category = 'info'

# --- Predefined User Accounts (Hardcoded for Security) ---
AUTHORIZED_USERS = {
    'dhanesh@retyn.ai': {
        'password': 'retyn*#123',
        'name': 'Dhanesh',
        'id': 1
    },
    'jumi@retyn.ai': {
        'password': 'retyn*#123', 
        'name': 'Jumi',
        'id': 2
    }
}

class User(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, user_id, email, name):
        self.id = user_id
        self.email = email
        self.name = name
        
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    for email, user_data in AUTHORIZED_USERS.items():
        if str(user_data['id']) == str(user_id):
            return User(user_data['id'], email, user_data['name'])
    return None

# ================================================================
# GEOSPATIAL ENHANCEMENT FUNCTIONS
# Added: October 6, 2025
# Purpose: Location-based premium calculations for improved AVM accuracy
# ================================================================

from math import radians, sin, cos, sqrt, atan2

def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS points in kilometers using Haversine formula.
    
    Args:
        lat1, lon1: First point coordinates (decimal degrees)
        lat2, lon2: Second point coordinates (decimal degrees)
    
    Returns:
        float: Distance in kilometers, or None if inputs are invalid
    
    Example:
        >>> calculate_haversine_distance(25.0805, 55.1409, 25.0850, 55.1450)
        0.52  # ~520 meters
    """
    # Handle None/NULL values
    if None in [lat1, lon1, lat2, lon2]:
        return None
    
    try:
        R = 6371  # Earth's radius in kilometers
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return round(R * c, 2)
    except (ValueError, TypeError) as e:
        print(f"⚠️ Haversine calculation error: {e}")
        return None

def get_location_cache(area_name, property_type, bedrooms):
    """
    Retrieve cached location adjustments for property combination.
    Uses intelligent caching to improve performance.
    
    Args:
        area_name: Area/location name
        property_type: Type of property (Unit, Villa, etc.)
        bedrooms: Number of bedrooms
    
    Returns:
        dict: {
            'cache_hit': bool,
            'premium': float or None,
            'breakdown': dict or None,
            'age_days': int or None,
            'hits': int or None
        }
    """
    if not engine:
        return {'cache_hit': False}
    
    try:
        normalized_area = area_name.strip().lower() if area_name else ''
        
        # M4 FIX: Add 24-hour TTL to cache - only return entries < 24 hours old
        query = text("""
            SELECT 
                location_premium_pct,
                metro_premium,
                beach_premium,
                mall_premium,
                school_premium,
                business_premium,
                neighborhood_premium,
                EXTRACT(DAY FROM NOW() - created_at)::INT as age_days,
                cache_hits
            FROM property_location_cache
            WHERE LOWER(area_name) = :area
              AND property_type = :type
              AND COALESCE(bedrooms, '') = COALESCE(:beds, '')
              AND created_at > NOW() - INTERVAL '24 hours'
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {
                'area': normalized_area,
                'type': property_type or '',
                'beds': bedrooms or ''
            }).fetchone()
        
        if result:
            # Update cache hit counter and last_accessed (async-safe)
            try:
                update_query = text("""
                    UPDATE property_location_cache
                    SET cache_hits = cache_hits + 1,
                        last_accessed = NOW()
                    WHERE LOWER(area_name) = :area
                      AND property_type = :type
                      AND COALESCE(bedrooms, '') = COALESCE(:beds, '')
                """)
                with engine.connect() as conn:
                    conn.execute(update_query, {
                        'area': normalized_area,
                        'type': property_type or '',
                        'beds': bedrooms or ''
                    })
                    conn.commit()
            except Exception as e:
                # Don't fail if cache update fails
                print(f"⚠️ Cache hit update failed (non-critical): {e}")
            
            return {
                'cache_hit': True,
                'premium': float(result[0]) if result[0] is not None else 0,
                'breakdown': {
                    'metro': float(result[1]) if result[1] is not None else 0,
                    'beach': float(result[2]) if result[2] is not None else 0,
                    'mall': float(result[3]) if result[3] is not None else 0,
                    'school': float(result[4]) if result[4] is not None else 0,
                    'business': float(result[5]) if result[5] is not None else 0,
                    'neighborhood': float(result[6]) if result[6] is not None else 0
                },
                'age_days': int(result[7]) if result[7] is not None else 0,
                'hits': int(result[8]) + 1 if result[8] is not None else 1
            }
        
        return {'cache_hit': False}
    
    except Exception as e:
        print(f"❌ Cache lookup error: {e}")
        return {'cache_hit': False}

def calculate_location_premium(area_name):
    """
    Calculate comprehensive location premium based on area coordinates and distances.
    
    Premium Formula (based on Dubai market research):
    - Metro: 15% at 0km, scales down to 0% at 5km (3% per km)
    - Beach: 30% at 0km, scales down to 0% at 5km (6% per km)
    - Mall: 8% at 0km, scales down to 0% at 4km (2% per km)
    - School: 5% at 0km, scales down to 0% at 5km (1% per km)
    - Business: 10% at 0km, scales down to 0% at 5km (2% per km)
    - Neighborhood: (score - 3.0) * 4% → -8% to +8% range
    
    Total capped at: -20% min, +70% max (raised from +50% to preserve granularity in ultra-premium areas)
    
    Args:
        area_name: Area/location name to lookup
    
    Returns:
        dict or None: {
            'total_premium': float,
            'metro_premium': float,
            'beach_premium': float,
            'mall_premium': float,
            'school_premium': float,
            'business_premium': float,
            'neighborhood_premium': float,
            'confidence': float (0-1)
        }
    """
    if not engine:
        return None
    
    try:
        normalized_area = area_name.strip().lower() if area_name else ''
        
        query = text("""
            SELECT 
                distance_to_metro_km,
                distance_to_beach_km,
                distance_to_mall_km,
                distance_to_school_km,
                distance_to_business_km,
                neighborhood_score
            FROM area_coordinates
            WHERE LOWER(area_name) = :area
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {'area': normalized_area}).fetchone()
        
        if not result:
            return None
        
        metro_dist, beach_dist, mall_dist, school_dist, business_dist, neighborhood = result
        
        # Convert Decimal to float for calculations
        metro_dist = float(metro_dist) if metro_dist is not None else None
        beach_dist = float(beach_dist) if beach_dist is not None else None
        mall_dist = float(mall_dist) if mall_dist is not None else None
        school_dist = float(school_dist) if school_dist is not None else None
        business_dist = float(business_dist) if business_dist is not None else None
        neighborhood = float(neighborhood) if neighborhood is not None else None
        
        # Calculate individual premiums (linear decay with reasonable defaults)
        # Note: Use 'if x is not None' to handle 0.0 values correctly (0.0 is falsy but valid!)
        metro_premium = max(0, 15 - (metro_dist if metro_dist is not None else 10) * 3)
        beach_premium = max(0, 30 - (beach_dist if beach_dist is not None else 10) * 6)
        mall_premium = max(0, 8 - (mall_dist if mall_dist is not None else 10) * 2)
        school_premium = max(0, 5 - (school_dist if school_dist is not None else 10) * 1)
        business_premium = max(0, 10 - (business_dist if business_dist is not None else 10) * 2)
        neighborhood_premium = ((neighborhood if neighborhood is not None else 3.0) - 3.0) * 4
        
        # Total premium (capped at reasonable range)
        # M5 FIX: Raised cap from +50% to +70% to preserve granularity in ultra-premium areas
        total = metro_premium + beach_premium + mall_premium + school_premium + business_premium + neighborhood_premium
        total_capped = max(-20, min(70, total))
        
        # Confidence based on data completeness
        data_points = sum([
            1 if metro_dist is not None else 0,
            1 if beach_dist is not None else 0,
            1 if mall_dist is not None else 0,
            1 if school_dist is not None else 0,
            1 if business_dist is not None else 0,
            1 if neighborhood is not None else 0
        ])
        confidence = min(0.95, 0.50 + (data_points / 6) * 0.45)  # 50% to 95% based on completeness
        
        return {
            'total_premium': round(total_capped, 2),
            'metro_premium': round(metro_premium, 2),
            'beach_premium': round(beach_premium, 2),
            'mall_premium': round(mall_premium, 2),
            'school_premium': round(school_premium, 2),
            'business_premium': round(business_premium, 2),
            'neighborhood_premium': round(neighborhood_premium, 2),
            'confidence': round(confidence, 2)
        }
    
    except Exception as e:
        print(f"❌ Premium calculation error for '{area_name}': {e}")
        return None

def get_project_premium(project_name):
    """
    Get premium percentage for a specific project.
    
    Args:
        project_name: Name of the project (e.g., 'Ciel', 'Trump Tower')
    
    Returns:
        dict with keys:
            - premium_percentage: float (0-20)
            - tier: str ('Ultra-Luxury', 'Super-Premium', 'Premium', or None)
        Returns {'premium_percentage': 0, 'tier': None} if not found
    """
    if not project_name or not str(project_name).strip():
        return {'premium_percentage': 0, 'tier': None}
    
    try:
        query = text("""
            SELECT premium_percentage, tier 
            FROM project_premiums 
            WHERE LOWER(project_name) = LOWER(:name)
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {"name": str(project_name).strip()}).fetchone()
            
            if result:
                return {
                    'premium_percentage': float(result[0]),
                    'tier': result[1]
                }
            return {'premium_percentage': 0, 'tier': None}
            
    except Exception as e:
        print(f"⚠️  Project premium error for '{project_name}': {e}")
        return {'premium_percentage': 0, 'tier': None}


def get_project_premium_breakdown(project_name, premium_pct, tier, transaction_count, avg_price_sqm):
    """
    Generate detailed breakdown of project premium for frontend display.
    
    Returns:
        list of dicts with 'factor', 'percentage', and 'description' keys
    """
    breakdown = []
    
    # Calculate breakdown based on tier and premium percentage
    if premium_pct >= 20:  # Ultra-Luxury
        breakdown = [
            {
                'factor': 'International Brand',
                'percentage': round(premium_pct * 0.35, 2),
                'description': 'Globally recognized luxury brand'
            },
            {
                'factor': 'Luxury Amenities',
                'percentage': round(premium_pct * 0.25, 2),
                'description': 'World-class facilities and services'
            },
            {
                'factor': 'Prime Location',
                'percentage': round(premium_pct * 0.15, 2),
                'description': 'Prestigious address and positioning'
            },
            {
                'factor': 'Market Performance',
                'percentage': round(premium_pct * 0.15, 2),
                'description': f'{transaction_count} transactions analyzed'
            },
            {
                'factor': 'Build Quality',
                'percentage': round(premium_pct * 0.10, 2),
                'description': 'Premium finishes and construction'
            }
        ]
    elif premium_pct >= 15:  # Super-Premium
        breakdown = [
            {
                'factor': 'Brand Recognition',
                'percentage': round(premium_pct * 0.40, 2),
                'description': 'Established luxury brand'
            },
            {
                'factor': 'Premium Amenities',
                'percentage': round(premium_pct * 0.25, 2),
                'description': 'High-end facilities (pool, gym, spa)'
            },
            {
                'factor': 'Location Quality',
                'percentage': round(premium_pct * 0.15, 2),
                'description': 'Prime area positioning'
            },
            {
                'factor': 'Market Demand',
                'percentage': round(premium_pct * 0.15, 2),
                'description': f'High liquidity ({transaction_count} properties)'
            },
            {
                'factor': 'Quality Standards',
                'percentage': round(premium_pct * 0.05, 2),
                'description': 'Superior construction quality'
            }
        ]
    else:  # Premium (10%)
        breakdown = [
            {
                'factor': 'Developer Brand',
                'percentage': round(premium_pct * 0.35, 2),
                'description': 'Reputable developer'
            },
            {
                'factor': 'Amenities',
                'percentage': round(premium_pct * 0.30, 2),
                'description': 'Quality facilities included'
            },
            {
                'factor': 'Location',
                'percentage': round(premium_pct * 0.20, 2),
                'description': 'Good area positioning'
            },
            {
                'factor': 'Market Position',
                'percentage': round(premium_pct * 0.15, 2),
                'description': f'Established presence ({transaction_count} properties)'
            }
        ]
    
    return breakdown


def get_similar_projects(project_name, tier, limit=10):
    """
    Get similar premium projects with the same tier.
    Excludes the current project and sorts by transaction activity.
    
    Args:
        project_name: Name of current project
        tier: Premium tier (Ultra-Luxury, Super-Premium, Premium)
        limit: Maximum number of similar projects to return
        
    Returns:
        list: Array of dicts with project details
    """
    if not engine or not project_name or not tier:
        return []
    
    try:
        query = text("""
            SELECT project_name, tier, premium_percentage, 
                   COALESCE(transaction_count, 0) as txn_count
            FROM project_premiums
            WHERE tier = :tier 
              AND LOWER(project_name) != LOWER(:current_project)
            ORDER BY COALESCE(transaction_count, 0) DESC, premium_percentage DESC
            LIMIT :limit
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, {
                'tier': tier,
                'current_project': project_name,
                'limit': limit
            })
            
            similar = []
            for row in result:
                similar.append({
                    'name': row[0],
                    'tier': row[1],
                    'premium': float(row[2]) if row[2] else 0.0,
                    'transactions': int(row[3]) if row[3] else 0
                })
            
            logger.info(f"Found {len(similar)} similar projects for {project_name} (tier: {tier})")
            return similar
            
    except Exception as e:
        logger.error(f"Error fetching similar projects: {e}")
        return []


# Mock data for comparison table (temporary fallback while DB query is being optimized)
# TODO: Replace with real get_similar_projects() once query performance is resolved
MOCK_SIMILAR_PROJECTS = {
    'City Walk Crestlane 2': [
        {'name': 'City Walk Crestlane 3', 'tier': 'Premium', 'premium': 10.0, 'transactions': 38},
        {'name': 'City Walk Crestlane 1', 'tier': 'Premium', 'premium': 9.5, 'transactions': 42},
    ],
    'Trump Tower': [
        {'name': 'Marina 101', 'tier': 'Ultra-Luxury', 'premium': 15.5, 'transactions': 28},
        {'name': 'Princess Tower', 'tier': 'Ultra-Luxury', 'premium': 14.0, 'transactions': 35},
    ],
    'Bluewaters Residences': [
        {'name': 'Address JBR', 'tier': 'Ultra-Luxury', 'premium': 16.0, 'transactions': 22},
        {'name': 'Bulgari Resort', 'tier': 'Ultra-Luxury', 'premium': 17.5, 'transactions': 18},
    ],
    'FIVE Palm Jumeirah': [
        {'name': 'One Palm', 'tier': 'Super-Premium', 'premium': 12.0, 'transactions': 30},
        {'name': 'Serenia Residences', 'tier': 'Super-Premium', 'premium': 11.5, 'transactions': 25},
    ],
    'Dubai Marina Yacht Club': [
        {'name': 'Marina Quays', 'tier': 'Super-Premium', 'premium': 11.0, 'transactions': 33},
        {'name': 'Marina Pinnacle', 'tier': 'Super-Premium', 'premium': 10.8, 'transactions': 28},
    ],
    'Emirates Hills Villa': [
        {'name': 'Dubai Hills Estate', 'tier': 'Super-Premium', 'premium': 10.5, 'transactions': 18},
        {'name': 'Arabian Ranches', 'tier': 'Super-Premium', 'premium': 9.8, 'transactions': 22},
    ],
    'Palm Jumeirah Villa': [
        {'name': 'Palm Jumeirah Apartment', 'tier': 'Super-Premium', 'premium': 12.5, 'transactions': 20},
        {'name': 'Signature Villas', 'tier': 'Super-Premium', 'premium': 13.0, 'transactions': 15},
    ],
    'Downtown Views': [
        {'name': 'Burj Khalifa Residences', 'tier': 'Premium', 'premium': 9.0, 'transactions': 45},
        {'name': 'Opera District', 'tier': 'Premium', 'premium': 8.8, 'transactions': 40},
    ],
    'Emaar Beachfront': [
        {'name': 'Address Beach Resort', 'tier': 'Premium', 'premium': 8.5, 'transactions': 28},
        {'name': 'Beach Vista', 'tier': 'Premium', 'premium': 8.2, 'transactions': 32},
    ],
    'Al Yelayiss 1': [
        {'name': 'Al Yelayiss 2', 'tier': 'Standard', 'premium': 0.0, 'transactions': 15},
    ]
}


def calculate_floor_premium(floor_level, property_type):
    """
    Calculate floor level premium for high-rise properties.
    
    Rules:
    - Ground floor: 0% (baseline)
    - Floors 1-5: +1% per floor (max +5%)
    - Floors 6-15: +0.5% per floor above 5 (max +10%)
    - Floors 16-30: +0.3% per floor above 15 (max +14.5%)
    - Floors 31+: +0.2% per floor above 30 (capped at +25%)
    
    Args:
        floor_level: Floor number (integer or None)
        property_type: Type of property (e.g., 'Unit', 'Villa')
    
    Returns:
        float: Premium percentage (0.0 to 25.0)
    """
    if not floor_level or floor_level <= 0:
        return 0.0
    
    # Floor premium doesn't apply to villas, townhouses, or land
    if property_type and property_type.lower() in ['villa', 'townhouse', 'land', 'plot']:
        return 0.0
    
    floor = min(int(floor_level), 150)  # Cap at 150 floors
    
    if floor <= 5:
        return floor * 1.0
    elif floor <= 15:
        return 5.0 + (floor - 5) * 0.5
    elif floor <= 30:
        return 10.0 + (floor - 15) * 0.3
    else:
        premium = 14.5 + (floor - 30) * 0.2
        return min(premium, 25.0)  # Cap at 25%


def calculate_view_premium(view_type, area_name):
    """
    Calculate view quality premium based on type and location.
    
    View Types & Premiums:
    - Sea View: +15% (prime coastal areas) / +8% (other coastal)
    - Marina View: +12%
    - Golf Course View: +10%
    - Burj Khalifa View: +20% (Downtown) / +10% (other areas)
    - Park View: +5%
    - City Skyline: +7%
    - Partial Sea View: +5%
    - Street View: 0% (baseline)
    
    Args:
        view_type: Type of view (string or None)
        area_name: Area/location name
    
    Returns:
        float: Premium percentage (0.0 to 20.0)
    """
    if not view_type:
        return 0.0
    
    view_lower = view_type.lower()
    area_lower = (area_name or '').lower()
    
    # Prime coastal areas with highest sea view premiums
    prime_coastal = [
        'dubai marina', 'jbr', 'jumeirah beach residence',
        'palm jumeirah', 'bluewaters', 'bluewaters island',
        'emaar beachfront', 'la mer'
    ]
    
    # Sea/Ocean view
    if 'sea view' in view_lower or 'ocean view' in view_lower or 'sea' in view_lower:
        if any(area in area_lower for area in prime_coastal):
            return 15.0
        elif 'jumeirah' in area_lower or 'marina' in area_lower or 'beach' in area_lower:
            return 8.0
        else:
            return 5.0  # Conservative for other areas
    
    # Marina view
    elif 'marina view' in view_lower or 'marina' in view_lower:
        return 12.0
    
    # Golf course view
    elif 'golf' in view_lower:
        return 10.0
    
    # Burj Khalifa view (location-dependent)
    elif 'burj khalifa' in view_lower or 'burj' in view_lower:
        if 'downtown' in area_lower:
            return 20.0
        else:
            return 10.0
    
    # Park/Garden view
    elif 'park' in view_lower or 'garden' in view_lower:
        return 5.0
    
    # City skyline view
    elif 'city' in view_lower or 'skyline' in view_lower:
        return 7.0
    
    # Partial views
    elif 'partial' in view_lower:
        return 5.0
    
    # No premium for street view or unknown
    else:
        return 0.0


def calculate_age_premium(property_age, property_type, is_offplan):
    """
    Calculate property age premium (depreciation).
    
    Rules:
    - Off-plan/New (0 years): +5% (new property premium)
    - 1-3 years: 0% (still new, no depreciation)
    - 4-10 years: -1% per year (-7% max)
    - 11-20 years: -1.5% per year (-22% max cumulative)
    - 21-30 years: -2% per year (-42% max cumulative)
    - 31+ years: -2.5% per year (capped at -50%)
    
    Villas depreciate slower (70% of rate)
    
    Args:
        property_age: Age in years (integer or None)
        property_type: Type of property (e.g., 'Unit', 'Villa')
        is_offplan: Whether property is off-plan/new
    
    Returns:
        float: Premium percentage (-50.0 to +5.0)
    """
    # Off-plan properties get new property premium
    if is_offplan:
        return 5.0
    
    # No age provided, assume new property
    if not property_age or property_age <= 0:
        return 5.0
    
    age = min(int(property_age), 100)  # Cap at 100 years
    
    # Villas depreciate slower than apartments
    depreciation_factor = 0.7 if (property_type and 'villa' in property_type.lower()) else 1.0
    
    # Calculate age-based depreciation
    if age <= 3:
        return 0.0  # Still considered new, no depreciation
    elif age <= 10:
        return -1.0 * (age - 3) * depreciation_factor
    elif age <= 20:
        base_depreciation = -7.0 - 1.5 * (age - 10)
        return base_depreciation * depreciation_factor
    elif age <= 30:
        base_depreciation = -22.0 - 2.0 * (age - 20)
        return base_depreciation * depreciation_factor
    else:
        base_depreciation = -42.0 - 2.5 * (age - 30)
        return max(base_depreciation * depreciation_factor, -50.0)  # Cap at -50%


def update_location_cache(area_name, property_type, bedrooms, premium_data):
    """
    Store calculated premium in cache with conflict handling.
    
    Args:
        area_name: Area/location name
        property_type: Type of property
        bedrooms: Number of bedrooms
        premium_data: dict with premium breakdown from calculate_location_premium()
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not engine or not premium_data:
        return False
    
    try:
        normalized_area = area_name.strip().lower() if area_name else ''
        
        query = text("""
            INSERT INTO property_location_cache (
                area_name, property_type, bedrooms,
                location_premium_pct, metro_premium, beach_premium,
                mall_premium, school_premium, business_premium, neighborhood_premium
            ) VALUES (
                :area, :type, :beds,
                :total, :metro, :beach, :mall, :school, :business, :neighborhood
            )
            ON CONFLICT (area_name, property_type, bedrooms) DO UPDATE SET
                location_premium_pct = EXCLUDED.location_premium_pct,
                metro_premium = EXCLUDED.metro_premium,
                beach_premium = EXCLUDED.beach_premium,
                mall_premium = EXCLUDED.mall_premium,
                school_premium = EXCLUDED.school_premium,
                business_premium = EXCLUDED.business_premium,
                neighborhood_premium = EXCLUDED.neighborhood_premium,
                last_accessed = NOW()
        """)
        
        with engine.connect() as conn:
            conn.execute(query, {
                'area': normalized_area,
                'type': property_type or '',
                'beds': bedrooms or '',
                'total': premium_data['total_premium'],
                'metro': premium_data['metro_premium'],
                'beach': premium_data['beach_premium'],
                'mall': premium_data['mall_premium'],
                'school': premium_data['school_premium'],
                'business': premium_data['business_premium'],
                'neighborhood': premium_data['neighborhood_premium']
            })
            conn.commit()
        
        return True
    
    except Exception as e:
        print(f"❌ Cache update error: {e}")
        return False

# ================================================================
# END GEOSPATIAL FUNCTIONS
# ================================================================

# --- AVM (Automated Valuation Model) Logic with Outlier Filtering ---
def filter_outliers(prices, search_type):
    """
    Advanced outlier filtering for Dubai property market
    Returns filtered prices and outlier statistics
    """
    if len(prices) == 0:
        return prices, {"total_outliers": 0, "outlier_percentage": 0}
    
    # Define market-realistic thresholds based on Dubai property market
    if search_type == 'buy':
        # Sales thresholds - based on actual Dubai market analysis
        MIN_PRICE = 100_000        # Minimum realistic sale price
        MAX_PRICE = 50_000_000     # Maximum realistic residential sale (50M AED)
        # For land/commercial, we're more lenient but still filter extreme outliers
        EXTREME_MAX = 100_000_000  # Absolute maximum for any property type
    else:
        # Rental thresholds - based on actual Dubai rental market
        MIN_PRICE = 10_000         # Minimum realistic annual rent
        MAX_PRICE = 2_000_000      # Maximum realistic residential rent (2M AED)
        EXTREME_MAX = 5_000_000    # Absolute maximum for any rental
    
    # Count outliers before filtering
    original_count = len(prices)
    low_outliers = len(prices[prices < MIN_PRICE])
    high_outliers = len(prices[prices > MAX_PRICE])
    extreme_outliers = len(prices[prices > EXTREME_MAX])
    
    # Apply filtering
    filtered_prices = prices[
        (prices >= MIN_PRICE) & 
        (prices <= MAX_PRICE)
    ]
    
    # Calculate outlier statistics
    total_outliers = original_count - len(filtered_prices)
    outlier_percentage = (total_outliers / original_count) * 100 if original_count > 0 else 0
    
    outlier_stats = {
        "total_outliers": total_outliers,
        "outlier_percentage": outlier_percentage,
        "low_outliers": low_outliers,
        "high_outliers": high_outliers,
        "extreme_outliers": extreme_outliers,
        "original_count": original_count,
        "filtered_count": len(filtered_prices),
        "min_threshold": MIN_PRICE,
        "max_threshold": MAX_PRICE
    }
    
    return filtered_prices, outlier_stats

def calculate_avm_metrics(results_df, search_type, filters):
    """
    Calculates AVM metrics for better data-driven decision making
    Now includes comprehensive outlier filtering for accurate analytics
    """
    if results_df.empty:
        return None
    
    try:
        # Get the appropriate price column
        price_col = SALES_MAP['price'] if search_type == 'buy' else RENTALS_MAP['price']
        
        # Handle the case where rent data uses 'trans_value' alias
        if search_type == 'rent' and 'trans_value' in results_df.columns:
            price_col = 'trans_value'
        
        raw_prices = results_df[price_col].dropna()
        
        if len(raw_prices) == 0:
            return None
        
        # 🔥 APPLY OUTLIER FILTERING
        filtered_prices, outlier_stats = filter_outliers(raw_prices, search_type)
        
        if len(filtered_prices) == 0:
            return None
            
        # Basic statistical analysis on FILTERED data
        price_stats = {
            'median_price': filtered_prices.median(),
            'mean_price': filtered_prices.mean(),
            'std_price': filtered_prices.std(),
            'min_price': filtered_prices.min(),
            'max_price': filtered_prices.max(),
            'q1_price': filtered_prices.quantile(0.25),
            'q3_price': filtered_prices.quantile(0.75),
        }
        
        # Market positioning analysis
        user_budget = filters.get('budget') or filters.get('annual_rent') or 999999999
        user_budget = float(user_budget)
        
        # Calculate percentile of user's budget (using filtered data)
        budget_percentile = (filtered_prices <= user_budget).mean() * 100
        
        # Price range analysis (using filtered data)
        affordable_count = len(filtered_prices[filtered_prices <= user_budget * 0.8])  # 80% of budget
        optimal_count = len(filtered_prices[(filtered_prices > user_budget * 0.8) & (filtered_prices <= user_budget)])
        total_count = len(filtered_prices)
        
        # Market liquidity indicators (now much more accurate)
        price_volatility = (price_stats['std_price'] / price_stats['mean_price']) * 100 if price_stats['mean_price'] > 0 else 0
        
        # Area-based analysis if area is specified (also with outlier filtering)
        area_analysis = None
        if filters.get('area'):
            area_col = SALES_MAP['area_name'] if search_type == 'buy' else RENTALS_MAP['area_name']
            if area_col in results_df.columns:
                area_data = results_df[results_df[area_col].str.contains(filters['area'], case=False, na=False)]
                if not area_data.empty:
                    area_raw_prices = area_data[price_col].dropna()
                    # Apply same outlier filtering to area data
                    area_filtered_prices, area_outlier_stats = filter_outliers(area_raw_prices, search_type)
                    if len(area_filtered_prices) > 0:
                        area_analysis = {
                            'area_median': area_filtered_prices.median(),
                            'area_count': len(area_filtered_prices),
                            'vs_market': ((area_filtered_prices.median() - price_stats['median_price']) / price_stats['median_price']) * 100,
                            'area_outliers_removed': area_outlier_stats['total_outliers']
                        }
        
        return {
            'stats': price_stats,
            'budget_percentile': budget_percentile,
            'affordable_count': affordable_count,
            'optimal_count': optimal_count,
            'total_count': total_count,
            'price_volatility': price_volatility,
            'area_analysis': area_analysis,
            'outlier_info': outlier_stats  # 🔥 NEW: Include outlier statistics
        }
        
    except Exception as e:
        print(f"❌ AVM calculation failed: {e}")
        return None

# --- Market Trends Analysis Functions ---
def get_price_trends(filters, search_type, time_period='6M'):
    """
    Extract time-series price data from existing tables
    Returns data points for trend visualization
    """
    if not engine:
        return []
    
    try:
        # Determine period in months
        period_months = {'3M': 3, '6M': 6, '1Y': 12}.get(time_period, 6)
        
        # Get table and column mappings
        table = 'properties' if search_type == 'buy' else 'rentals'
        date_col = 'instance_date' if search_type == 'buy' else 'registration_date'
        map_config = SALES_MAP if search_type == 'buy' else RENTALS_MAP
        price_col = map_config['price']
        
        # Build WHERE clause using existing logic
        where_clause, params = build_where_clause(filters, map_config, 'budget', is_rent=(search_type == 'rent'))
        
        # Time-series query - group by month
        query = text(f"""
            SELECT 
                DATE_TRUNC('month', CAST("{date_col}" AS DATE)) as month,
                AVG("{price_col}") as avg_price,
                COUNT(*) as transaction_count,
                MIN("{price_col}") as min_price,
                MAX("{price_col}") as max_price,
                AVG(
                    CASE 
                        WHEN "actual_area" IS NOT NULL 
                        AND "actual_area" != '' 
                        AND CAST("actual_area" AS FLOAT) > 0 
                        THEN "{price_col}" / CAST("actual_area" AS FLOAT)
                        ELSE NULL 
                    END
                ) as avg_price_per_sqm
            FROM {table}
            WHERE {where_clause}
            AND "{date_col}" IS NOT NULL
            AND "{date_col}" != ''
            AND CAST("{date_col}" AS DATE) >= NOW() - INTERVAL '{period_months} months'
            GROUP BY DATE_TRUNC('month', CAST("{date_col}" AS DATE))
            ORDER BY month;
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query, params)
            trend_data = []
            for row in result:
                price_per_sqm = float(row[5]) if row[5] else 0
                trend_data.append({
                    'month': row[0].strftime('%Y-%m') if row[0] else None,
                    'avg_price': float(row[1]) if row[1] else 0,
                    'transaction_count': int(row[2]) if row[2] else 0,
                    'min_price': float(row[3]) if row[3] else 0,
                    'max_price': float(row[4]) if row[4] else 0,
                    'avg_price_per_sqm': price_per_sqm
                })
                print(f"🔍 TREND ROW: month={row[0]}, avg_price={row[1]}, avg_price_per_sqm={price_per_sqm}")
            
            print(f"🔍 TREND DATA SUMMARY: {len(trend_data)} months, price_per_sqm values: {[d['avg_price_per_sqm'] for d in trend_data]}")
            return trend_data
            
    except Exception as e:
        print(f"❌ Trend data extraction failed: {e}")
        return []

def calculate_basic_trends(trend_data):
    """
    Calculate comprehensive trend metrics including QoQ, YoY, volatility, and transaction trends
    """
    if not trend_data or len(trend_data) < 2:
        return {
            'trend_direction': 'insufficient_data',
            'percentage_change': 0,
            'trend_strength': 'weak',
            'summary': 'Insufficient data for trend analysis'
        }
    
    try:
        # Extract prices and dates
        prices = [point['avg_price'] for point in trend_data if point['avg_price'] > 0]
        volumes = [point['transaction_count'] for point in trend_data]
        dates = [datetime.strptime(point['month'], '%Y-%m') for point in trend_data]
        
        if len(prices) < 2:
            return {
                'trend_direction': 'insufficient_data',
                'percentage_change': 0,
                'trend_strength': 'weak',
                'summary': 'Insufficient price data for analysis'
            }
        
        # --- BASIC TREND ANALYSIS ---
        first_price = prices[0]
        last_price = prices[-1]
        percentage_change = ((last_price - first_price) / first_price) * 100
        
        # Determine trend direction
        if percentage_change > 5:
            trend_direction = 'upward'
            trend_strength = 'strong' if percentage_change > 15 else 'moderate'
        elif percentage_change < -5:
            trend_direction = 'downward'
            trend_strength = 'strong' if percentage_change < -15 else 'moderate'
        else:
            trend_direction = 'stable'
            trend_strength = 'stable'
        
        # --- 1. QUARTER-OVER-QUARTER ANALYSIS ---
        qoq_change = 0
        qoq_status = 'N/A'
        if len(prices) >= 3:  # Need at least 3 months for QoQ
            # Get last 3 months average vs previous 3 months
            recent_quarter = prices[-3:] if len(prices) >= 6 else prices[-len(prices)//2:]
            previous_quarter = prices[-6:-3] if len(prices) >= 6 else prices[:len(prices)//2]
            
            if previous_quarter:
                recent_avg = sum(recent_quarter) / len(recent_quarter)
                previous_avg = sum(previous_quarter) / len(previous_quarter)
                qoq_change = ((recent_avg - previous_avg) / previous_avg) * 100
                qoq_status = 'Growth' if qoq_change > 0 else 'Decline' if qoq_change < 0 else 'Flat'
        
        # --- 2. YEAR-OVER-YEAR ANALYSIS ---
        yoy_change = 0
        yoy_status = 'N/A'
        if len(trend_data) >= 12:  # Need at least 12 months for true YoY
            # Compare same month last year
            current_month = dates[-1]
            year_ago_data = [point for point in trend_data 
                           if datetime.strptime(point['month'], '%Y-%m').month == current_month.month
                           and datetime.strptime(point['month'], '%Y-%m').year == current_month.year - 1]
            
            if year_ago_data:
                year_ago_price = year_ago_data[0]['avg_price']
                yoy_change = ((last_price - year_ago_price) / year_ago_price) * 100
                yoy_status = 'Growth' if yoy_change > 0 else 'Decline' if yoy_change < 0 else 'Flat'
        elif len(prices) >= 6:
            # Fallback: compare recent 3 months to earliest 3 months
            recent_avg = sum(prices[-3:]) / len(prices[-3:])
            earliest_avg = sum(prices[:3]) / len(prices[:3])
            yoy_change = ((recent_avg - earliest_avg) / earliest_avg) * 100
            yoy_status = f'Period Growth' if yoy_change > 0 else f'Period Decline' if yoy_change < 0 else 'Stable'
        
        # --- 3. MARKET VOLATILITY INDICATORS ---
        volatility = 0
        volatility_index = 'Low'
        price_std = 0
        
        if len(prices) > 2:
            # Calculate price volatility (standard deviation of percentage changes)
            price_changes = [(prices[i] - prices[i-1]) / prices[i-1] * 100 for i in range(1, len(prices))]
            volatility = pd.Series(price_changes).std() if price_changes else 0
            
            # Calculate price standard deviation
            price_std = pd.Series(prices).std()
            
            # Volatility index classification
            if volatility > 10:
                volatility_index = 'High'
            elif volatility > 5:
                volatility_index = 'Moderate'
            else:
                volatility_index = 'Low'
        
        # --- 4. TRANSACTION COUNT TRENDING ---
        volume_trend = 'Stable'
        volume_change = 0
        volume_growth_rate = 0
        
        if len(volumes) >= 2:
            first_volume = volumes[0] if volumes[0] > 0 else 1
            last_volume = volumes[-1] if volumes[-1] > 0 else 1
            volume_change = ((last_volume - first_volume) / first_volume) * 100
            
            if volume_change > 10:
                volume_trend = 'Increasing'
            elif volume_change < -10:
                volume_trend = 'Decreasing'
            else:
                volume_trend = 'Stable'
        
        # Calculate monthly volume growth rate
        if len(volumes) > 1:
            volume_changes = [(volumes[i] - volumes[i-1]) / max(volumes[i-1], 1) * 100 for i in range(1, len(volumes))]
            volume_growth_rate = sum(volume_changes) / len(volume_changes) if volume_changes else 0
        
        # Seasonal pattern detection (simple)
        seasonal_pattern = 'No Pattern'
        if len(trend_data) >= 6:
            monthly_volumes = {}
            for point in trend_data:
                month_num = datetime.strptime(point['month'], '%Y-%m').month
                if month_num not in monthly_volumes:
                    monthly_volumes[month_num] = []
                monthly_volumes[month_num].append(point['transaction_count'])
            
            if len(monthly_volumes) >= 3:
                avg_by_month = {k: sum(v)/len(v) for k, v in monthly_volumes.items()}
                max_month = max(avg_by_month, key=avg_by_month.get)
                min_month = min(avg_by_month, key=avg_by_month.get)
                seasonal_variation = (avg_by_month[max_month] - avg_by_month[min_month]) / avg_by_month[min_month] * 100
                
                if seasonal_variation > 30:
                    seasonal_pattern = f'Seasonal (Peak: Month {max_month})'
        
        # --- ENHANCED SUMMARY ---
        direction_text = {
            'upward': f'rising by {percentage_change:.1f}%',
            'downward': f'declining by {abs(percentage_change):.1f}%',
            'stable': f'stable with {abs(percentage_change):.1f}% variation'
        }.get(trend_direction, 'unclear trend')
        
        summary_parts = [
            f"Market is {direction_text} over the period with {trend_strength} momentum.",
            f"Volatility is {volatility_index.lower()} ({volatility:.1f}%).",
            f"Transaction volume is {volume_trend.lower()}."
        ]
        
        if qoq_status != 'N/A':
            summary_parts.append(f"Quarter-over-quarter: {qoq_status} ({qoq_change:+.1f}%).")
        
        if yoy_status != 'N/A':
            summary_parts.append(f"Year-over-year: {yoy_status} ({yoy_change:+.1f}%).")
        
        summary = " ".join(summary_parts)
        
        # Calculate average monthly volume
        avg_volume = sum(point['transaction_count'] for point in trend_data) / len(trend_data)
        
        # --- ENHANCED METRICS ---
        # Calculate average monthly sale price
        avg_monthly_price = sum(point['avg_price'] for point in trend_data) / len(trend_data)
        
        # Calculate price momentum (acceleration/deceleration detection)
        price_momentum = 'Stable'
        if len(prices) >= 3:
            # Calculate acceleration by comparing successive changes
            price_changes = [((prices[i] - prices[i-1]) / prices[i-1] * 100) for i in range(1, len(prices))]
            
            if len(price_changes) >= 2:
                # Check if changes are increasing (accelerating) or decreasing (decelerating)
                change_trend = 0
                for i in range(1, len(price_changes)):
                    change_trend += (price_changes[i] - price_changes[i-1])
                
                avg_change_trend = change_trend / (len(price_changes) - 1)
                
                if avg_change_trend > 0.5:
                    price_momentum = 'Accelerating'
                elif avg_change_trend < -0.5:
                    price_momentum = 'Decelerating'
        
        # Calculate affordability index (current price vs historical baseline)
        historical_baseline = 2500000  # Dubai market baseline (can be made configurable)
        affordability_index = (avg_monthly_price / historical_baseline) * 100
        
        # Calculate average monthly price per sqm with fallback calculation
        price_per_sqm_values = [point['avg_price_per_sqm'] for point in trend_data if point.get('avg_price_per_sqm', 0) > 0]
        avg_price_per_sqm = sum(price_per_sqm_values) / len(price_per_sqm_values) if price_per_sqm_values else 0
        
        # If no direct price per sqm data, estimate using average property size assumption
        if avg_price_per_sqm == 0 and avg_monthly_price > 0:
            # Use Dubai average property size estimation (1200 sqft = ~111 sqm)
            estimated_avg_sqm = 111  # Average size assumption for Dubai properties
            avg_price_per_sqm = avg_monthly_price / estimated_avg_sqm
            print(f"� FALLBACK: Using estimated price/sqm: {avg_monthly_price} / {estimated_avg_sqm} = {avg_price_per_sqm}")
        
        print(f"�🔍 DEBUG Price/SqM: {len(price_per_sqm_values)} valid values from {len(trend_data)} data points")
        print(f"🔍 DEBUG Price/SqM values: {price_per_sqm_values}")
        print(f"🔍 DEBUG Final Avg Price/SqM: {avg_price_per_sqm}")
        
        # Calculate price per sqm change
        price_per_sqm_change = 0
        if len(price_per_sqm_values) >= 2 and price_per_sqm_values[0] > 0:
            price_per_sqm_change = ((price_per_sqm_values[-1] - price_per_sqm_values[0]) / price_per_sqm_values[0]) * 100
        elif avg_price_per_sqm > 0:
            # Estimate change based on overall price change
            price_per_sqm_change = percentage_change
        
        return {
            # Basic metrics
            'trend_direction': trend_direction,
            'percentage_change': round(percentage_change, 2),
            'trend_strength': trend_strength,
            'avg_monthly_volume': round(avg_volume),
            'data_points': len(trend_data),
            'summary': summary,
            
            # Quarter-over-Quarter
            'qoq_change': round(qoq_change, 2),
            'qoq_status': qoq_status,
            
            # Year-over-Year
            'yoy_change': round(yoy_change, 2),
            'yoy_status': yoy_status,
            
            # Volatility Indicators
            'volatility': round(volatility, 2),
            'volatility_index': volatility_index,
            'price_std': round(price_std, 2),
            
            # Transaction Trending
            'volume_trend': volume_trend,
            'volume_change': round(volume_change, 2),
            'volume_growth_rate': round(volume_growth_rate, 2),
            'seasonal_pattern': seasonal_pattern,
            
            # Enhanced Metrics
            'avg_monthly_price': round(avg_monthly_price),
            'price_momentum': price_momentum,
            'affordability_index': round(affordability_index, 2),
            
            # Price per SqM Metrics
            'avg_price_per_sqm': round(avg_price_per_sqm),
            'price_per_sqm_change': round(price_per_sqm_change, 2)
        }
        
    except Exception as e:
        print(f"❌ Trend calculation failed: {e}")
        return {
            'trend_direction': 'error',
            'percentage_change': 0,
            'trend_strength': 'unknown',
            'summary': 'Error calculating trend metrics'
        }

# --- Shared Logic ---
def generate_ai_summary(filters, results_df, total_results, search_type):
    if not USE_AI_SUMMARY or results_df.empty: 
        return None
    
    project_list_for_prompt = "" # Initialize
    project_insights_prompt_section = "" # Initialize
    avm_insights_prompt_section = "" # Initialize

    # Calculate AVM metrics
    avm_data = calculate_avm_metrics(results_df, search_type, filters)
    
    if avm_data:
        # Format AVM insights for the prompt
        budget_value = filters.get('budget') or filters.get('annual_rent') or 999999999
        budget_value = float(budget_value)
        
        avm_insights_prompt_section = f"""
### AVM (Automated Valuation Model) Analysis
Provide data-driven insights based on these market metrics (outliers filtered for accuracy):
- Market Median: {avm_data['stats']['median_price']:,.0f} AED
- Your Budget Percentile: {avm_data['budget_percentile']:.1f}% (your budget covers {avm_data['budget_percentile']:.1f}% of available properties)
- Affordable Options: {avm_data['affordable_count']} properties under 80% of your budget
- Optimal Range: {avm_data['optimal_count']} properties in your target range (80-100% of budget)
- Market Volatility: {avm_data['price_volatility']:.1f}% (price variation indicator)
- Data Quality: {avm_data['outlier_info']['outlier_percentage']:.1f}% outliers removed ({avm_data['outlier_info']['total_outliers']} records filtered for accuracy)
"""
        
        if avm_data['area_analysis']:
            area_vs_market = avm_data['area_analysis']['vs_market']
            comparison = "premium" if area_vs_market > 0 else "discount"
            avm_insights_prompt_section += f"- Area Premium/Discount: {abs(area_vs_market):.1f}% {comparison} vs market median\n"

    if search_type == 'buy':
        analysis_subject, price_metric, user_goal, budget_key = "sales transactions", "sale price", "a potential buyer", "budget"
        query_text = " ".join([f for f in [filters.get("propertyType"), filters.get("bedrooms"), filters.get("status"), f"in {filters.get('area')}" if filters.get('area') else None] if f and 'Any' not in f and 'All' not in f]) or "all properties"
        
        # --- NEW: Extract project names for the prompt ---
        project_col = SALES_MAP.get('name')
        if project_col and project_col in results_df.columns:
            project_names = results_df[project_col].dropna().unique()
            project_names = [name for name in project_names if str(name).strip()]
            if project_names:
                sample_projects = project_names[:10]
                project_list_for_prompt = f"The data includes properties from various projects."
                # --- NEW: Add a section for Project Insights (Concise Version) ---
                project_insights_prompt_section = f"""
### Project Insights
In 2-3 sentences, summarize the key differences between the most prominent projects in the data. For example, mention which projects have higher transaction volumes (like DAMAC HILLS - CARSON), which ones offer more affordable units, and which ones feature larger apartments (like DAMAC HILLS - GOLF TERRACE).
"""

    else: # rent
        analysis_subject, price_metric, user_goal, budget_key = "rental contracts", "annual rent", "a potential renter", "budget"
        query_text = " ".join([f for f in [filters.get("propertyType"), filters.get("status"), f"in {filters.get('area')}" if filters.get('area') else None] if f and 'Any' not in f and 'All' not in f]) or "all properties"
    
    # Get budget value from either budget or annual_rent parameter
    budget_value = filters.get(budget_key) or filters.get('annual_rent') or 999999999
    
    system_prompt = f"""You are a senior Dubai real estate market analyst and AVM specialist providing executive-level insights to {user_goal}. 
    
You provide structured analysis in a professional, data-driven manner. Focus on actionable insights and market intelligence."""

    user_prompt = f"""
    MARKET CONTEXT: The user is analyzing "{query_text}" with a maximum {price_metric} of {int(budget_value):,} AED.
    DATA SCOPE: {total_results} recent {analysis_subject} found matching these criteria. {project_list_for_prompt}

    Please provide a structured analysis in the following format:

    Start with a 2-3 sentence executive summary highlighting the most critical market insights.

    ### Quick Summary
    Provide a clear opening statement about the total transactions found, followed by 3-4 key market insights presented as clean bullet points. Focus on price ranges, popular areas, and market trends.

    {avm_insights_prompt_section}

    {project_insights_prompt_section}

    FORMATTING INSTRUCTIONS:
    - Use bullet points (- ) for lists
    - Keep each section concise but insightful
    - Focus on actionable insights over generic advice
    - Maintain professional, confident tone
    """
    
    try:
        data_sample = results_df.head(100).to_string(index=False)
        full_user_prompt = f"{user_prompt}\n\nHere is a representative sample of the data:\n{data_sample}"
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_user_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ OpenAI API call failed: {e}")
        return "An error occurred while generating the AI summary."

# --- Helper to build WHERE clauses ---
def build_where_clause(filters, map, price_key, is_rent=False):
    conditions, params = [], {}
    
    # 🔥 OUTLIER FILTERING: Add realistic price bounds
    if is_rent:
        # Rental outlier thresholds
        MIN_PRICE = 10_000      # Minimum realistic annual rent
        MAX_PRICE = 2_000_000   # Maximum realistic residential rent
    else:
        # Sales outlier thresholds  
        MIN_PRICE = 100_000     # Minimum realistic sale price
        MAX_PRICE = 50_000_000  # Maximum realistic residential sale
    
    # Add outlier filtering conditions
    conditions.append(f"\"{map['price']}\" >= :min_price_param")
    conditions.append(f"\"{map['price']}\" <= :max_realistic_price")
    params['min_price_param'] = MIN_PRICE
    params['max_realistic_price'] = MAX_PRICE
    
    # Handle both 'budget' and 'annual_rent' parameter names - FIXED
    budget_value = filters.get('budget') or filters.get('annual_rent') or filters.get(price_key) or 999999999
    # Apply user budget filter (but not higher than our outlier threshold)
    user_max_price = min(int(budget_value), MAX_PRICE)
    conditions.append(f"\"{map['price']}\" <= :budget_param")
    params['budget_param'] = user_max_price

    prop_type = filters.get('propertyType')
    if prop_type and 'All Types' not in prop_type:
        if is_rent:
            # For rentals, search in both PROP_TYPE_EN and PROP_SUB_TYPE_EN
            # Build an OR condition to search both columns
            prop_type_col = find_column_name(RENTALS_COLUMNS, ['prop_type_en'])
            prop_sub_type_col = find_column_name(RENTALS_COLUMNS, ['prop_sub_type_en'])
            
            if prop_type_col and prop_sub_type_col:
                conditions.append(f"(\"{prop_type_col}\" = :prop_type OR \"{prop_sub_type_col}\" = :prop_type)")
            elif prop_type_col:
                conditions.append(f"\"{prop_type_col}\" = :prop_type")
            elif prop_sub_type_col:
                conditions.append(f"\"{prop_sub_type_col}\" = :prop_type")
        else:
            # For sales, use the standard property_type mapping
            conditions.append(f"\"{map['property_type']}\" = :prop_type")
        
        params['prop_type'] = prop_type

    # Apply property sub-type filtering (for rentals only)
    prop_sub_type = filters.get('property_sub_type')
    if prop_sub_type and 'Any' not in prop_sub_type and is_rent:
        if 'property_sub_type' in map and map['property_sub_type']:
            conditions.append(f"\"{map['property_sub_type']}\" = :prop_sub_type")
            params['prop_sub_type'] = prop_sub_type

    # Apply bedrooms filtering for sales only (rentals have insufficient bedroom data)
    bedrooms = filters.get('bedrooms')
    if bedrooms and 'Any' not in bedrooms and not is_rent:
        if 'bedrooms' in map and map['bedrooms']:  # Only if bedrooms column exists
            beds_col = f"\"{map['bedrooms']}\""
            if 'Studio' in bedrooms:
                conditions.append(f"({beds_col} = 'Studio' OR {beds_col} IS NULL)")
            else:
                try:
                    num_beds_str = re.findall(r'\d+', bedrooms)[0]
                    # Sales table might store bedrooms as text
                    conditions.append(f"({beds_col} LIKE '{num_beds_str} %' OR {beds_col} LIKE '%{num_beds_str}%' OR {beds_col} = '{num_beds_str}')")
                except (ValueError, IndexError): 
                    pass
    
    if not is_rent:
        status = filters.get('status')
        if status and 'Any' not in status:
            conditions.append(f"\"{map['status']}\" = :status")
            params['status'] = status
            
    area = filters.get('area')
    if area:
        conditions.append(f"\"{map['area_name']}\" LIKE :area")
        params['area'] = f"%{area}%"
    
    print(f"🔍 WHERE CLAUSE: {' AND '.join(conditions)}")
    print(f"🔍 PARAMS: {params}")
    return " AND ".join(conditions), params

# --- AUTHENTICATION ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Validate credentials
        if email in AUTHORIZED_USERS and AUTHORIZED_USERS[email]['password'] == password:
            user_data = AUTHORIZED_USERS[email]
            user = User(user_data['id'], email, user_data['name'])
            login_user(user, remember=True)  # Remember login for convenience
            
            # Redirect to next page or home
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Access is restricted to authorized personnel only.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/api/property/valuation', methods=['POST'])
@login_required
def get_property_valuation():
    """
    Production Automated Property Valuation API
    Uses 130K+ Dubai transaction database for statistical property valuations
    """
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['property_type', 'area', 'size_sqm']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        # Extract optional Phase 3 parameters (floor, view, age)
        floor_level = data.get('floor_level')  # Optional: floor number
        view_type = data.get('view_type')      # Optional: view quality
        property_age = data.get('property_age')  # Optional: age in years
        esg_score_min = data.get('esg_score_min')  # Optional: minimum ESG sustainability score
        flip_score_min = data.get('flip_score_min')  # Optional: minimum Flip investment score
        
        # Use production database valuation with global engine
        result = calculate_valuation_from_database(
            property_type=data['property_type'],
            area=data['area'],
            size_sqm=float(data['size_sqm']),
            bedrooms=data.get('bedrooms'),  # Optional bedroom filter
            development_status=data.get('development_status'),  # Optional status filter
            floor_level=floor_level,  # Phase 3: Floor premium
            view_type=view_type,      # Phase 3: View premium
            property_age=property_age,  # Phase 3: Age premium
            esg_score_min=esg_score_min,  # ESG sustainability score filter
            flip_score_min=flip_score_min,  # Flip investment score filter
            engine=engine  # Pass the global database engine
        )
        
        if result['success']:
            return jsonify(result)
        else:
            logging.error(f"❌ [VALUATION] Failed: {result.get('error', 'Unknown error')}")
            return jsonify(result), 500
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logging.error(f"❌ [VALUATION] Exception: {str(e)}\n{error_details}")
        return jsonify({
            'success': False, 
            'error': f'Valuation failed: {str(e)}'
        }), 500

def predict_price_ml(property_data: dict) -> dict:
    """
    Predict property price using ML model.
    
    Args:
        property_data: Dictionary containing property features
        
    Returns:
        dict with predicted_price and confidence score
    """
    if not USE_ML or ml_model is None:
        return {'predicted_price': None, 'confidence': 0.0, 'method': 'unavailable'}
    
    try:
        # Create DataFrame from input
        df = pd.DataFrame([property_data])
        
        # Feature engineering (matching training pipeline)
        if 'instance_date' in df.columns:
            df['instance_date'] = pd.to_datetime(df['instance_date'])
            df['transaction_year'] = df['instance_date'].dt.year
            df['transaction_month'] = df['instance_date'].dt.month
            df['transaction_quarter'] = df['instance_date'].dt.quarter
            df['days_since_2020'] = (df['instance_date'] - pd.Timestamp('2020-01-01')).dt.days
        else:
            # Use current date if not provided
            df['transaction_year'] = datetime.now().year
            df['transaction_month'] = datetime.now().month
            df['transaction_quarter'] = (datetime.now().month - 1) // 3 + 1
            df['days_since_2020'] = (datetime.now() - datetime(2020, 1, 1)).days
        
        # Price per square foot
        if 'actual_area' in df.columns:
            df['log_area'] = np.log1p(df['actual_area'])
        
        # Room features
        if 'rooms_en' in df.columns:
            df['room_count'] = df['rooms_en'].str.extract(r'(\d+)').astype(float)
            df['room_density'] = df['room_count'] / (df['actual_area'] / 1000)
            df['room_density'] = df['room_density'].fillna(0)
        else:
            df['room_count'] = 0
            df['room_density'] = 0
        
        # Binary features
        for col in ['is_offplan_en', 'is_free_hold_en']:
            if col in df.columns:
                df[col] = df[col].map({'Yes': 1, 'No': 0}).fillna(0)
            else:
                df[col] = 0
        
        # Categorical encoding using trained encoders
        categorical_cols = [
            'area_en', 'prop_type_en', 'group_en', 'procedure_en',
            'rooms_en', 'parking', 'nearest_metro_en', 'nearest_mall_en', 
            'nearest_landmark_en', 'project_en', 'usage_en', 'prop_sb_type_en'
        ]
        
        for col in categorical_cols:
            if col in df.columns and col in ml_encoders:
                df[col] = df[col].fillna('Unknown')
                known_classes = set(ml_encoders[col].classes_)
                df[f'{col}_encoded'] = df[col].apply(
                    lambda x: ml_encoders[col].transform([x])[0] if x in known_classes else -1
                )
            elif f'{col}_encoded' not in df.columns:
                df[f'{col}_encoded'] = -1
        
        # Interaction features
        if 'area_en_encoded' in df.columns and 'prop_type_en_encoded' in df.columns:
            df['area_proptype_interaction'] = df['area_en_encoded'] * df['prop_type_en_encoded']
        else:
            df['area_proptype_interaction'] = 0
        
        if 'actual_area' in df.columns and 'room_count' in df.columns:
            df['area_rooms_interaction'] = df['actual_area'] * df['room_count']
        else:
            df['area_rooms_interaction'] = 0
        
        # Fill missing numeric columns
        for col in ['total_buyer', 'total_seller', 'procedure_area']:
            if col not in df.columns:
                df[col] = 0
        
        # Add rental features (set to 0 for now, can be enhanced later)
        for col in ['median_rent_nearby', 'rental_availability', 'rent_to_price_ratio']:
            if col not in df.columns:
                df[col] = 0
        
        # Select features in correct order
        X = df[ml_feature_columns]
        X = X.fillna(0)  # Handle any remaining NaN values
        
        # Make prediction
        prediction = ml_model.predict(X)[0]
        
        # Estimate confidence based on feature completeness
        feature_completeness = (X != 0).sum().sum() / len(ml_feature_columns)
        confidence = min(0.95, 0.60 + (feature_completeness * 0.35))  # 60-95% range
        
        return {
            'predicted_price': float(prediction),
            'confidence': float(confidence),
            'method': 'xgboost'
        }
    
    except Exception as e:
        print(f"⚠️ ML prediction failed: {e}")
        return {'predicted_price': None, 'confidence': 0.0, 'method': 'error'}


def classify_price_segment(price_per_sqm):
    """
    Classify property into market segments based on Dubai market data.
    
    Thresholds based on 153K property analysis (2020-2025):
    - Budget: 0-12K (25th percentile)
    - Mid-Tier: 12-16.2K (50th percentile) 
    - Premium: 16.2-21.8K (75th percentile)
    - Luxury: 21.8-28.8K (90th percentile)
    - Ultra-Luxury: 28.8K+ (95th+ percentile)
    
    Args:
        price_per_sqm: Price per square meter in AED
        
    Returns:
        dict with segment info or None if invalid price
    """
    # M2 FIX: Add explicit error message for invalid inputs
    if not price_per_sqm or price_per_sqm <= 0:
        logging.warning(f"⚠️ Price segment classification failed: Invalid price_per_sqm={price_per_sqm}")
        return None
    
    # M3 FIX: Reject unrealistically small values (< 1000 AED/sqm)
    # This is redundant validation since database should prevent this, but adds safety
    if price_per_sqm < 1000:
        logging.warning(f"⚠️ Price segment classification rejected: price_per_sqm={price_per_sqm} too low (< 1000 AED/sqm)")
        return None
    
    if price_per_sqm < 12000:
        return {
            'segment': 'budget',
            'label': 'Budget',
            'icon': '🏘️',
            'percentile': 25,
            'range': '0 - 12,000 AED/sqm',
            'description': 'Value-focused properties in outer areas'
        }
    elif price_per_sqm < 16200:
        return {
            'segment': 'mid',
            'label': 'Mid-Tier',
            'icon': '🏢',
            'percentile': 50,
            'range': '12,000 - 16,200 AED/sqm',
            'description': 'Established areas with good value'
        }
    elif price_per_sqm < 21800:
        return {
            'segment': 'premium',
            'label': 'Premium',
            'icon': '🌟',
            'percentile': 75,
            'range': '16,200 - 21,800 AED/sqm',
            'description': 'Prime locations with high-quality buildings'
        }
    elif price_per_sqm < 28800:
        return {
            'segment': 'luxury',
            'label': 'Luxury',
            'icon': '💎',
            'percentile': 90,
            'range': '21,800 - 28,800 AED/sqm',
            'description': 'Premium positioning in Dubai market'
        }
    else:
        return {
            'segment': 'ultra',
            'label': 'Ultra-Luxury',
            'icon': '🏰',
            'percentile': 95,
            'range': '28,800+ AED/sqm',
            'description': 'Elite properties in top-tier locations'
        }


def calculate_valuation_from_database(property_type: str, area: str, size_sqm: float, engine, bedrooms: str = None, development_status: str = None, floor_level: int = None, view_type: str = None, property_age: int = None, esg_score_min: int = None, flip_score_min: int = None) -> dict:
    """
    Production valuation function using the main app's database engine
    
    Args:
        property_type: Type of property (Unit, Villa, Building, Land)
        area: Location/area name
        size_sqm: Property size in square meters
        engine: SQLAlchemy database engine
        bedrooms: Optional bedroom count filter (Studio, 1-6, or empty for any)
        development_status: Optional status filter (Ready, Off Plan, or empty for any)
        floor_level: Optional floor number for premium calculation
        view_type: Optional view type for premium calculation
        property_age: Optional property age in years
        esg_score_min: Optional minimum ESG sustainability score (0-100)
        flip_score_min: Optional minimum Flip investment score (0-100)
    """
    try:
        import pandas as pd
        from datetime import datetime
        
        print(f"🏗️ [DB] Calculating valuation for {size_sqm}sqm {property_type} in {area}")
        if bedrooms:
            print(f"🛏️  [DB] Filtering for {bedrooms} bedroom(s)")
        if development_status:
            print(f"🏢 [DB] Filtering for {development_status} properties")
        
        if not engine:
            raise Exception("Database engine not available")
        
        # Build SQL query with optional bedroom filter
        bedroom_condition = ""
        if bedrooms:
            if bedrooms == "Studio":
                bedroom_condition = "AND LOWER(rooms_en) LIKE '%studio%'"
            elif bedrooms == "6":
                bedroom_condition = "AND (rooms_en ~ '^[6-9]' OR rooms_en ~ '^[1-9][0-9]')"  # 6 or more
            else:
                # Match patterns like "1 B/R", "2 B/R", etc.
                bedroom_condition = f"AND (rooms_en = '{bedrooms}' OR rooms_en LIKE '{bedrooms} %' OR rooms_en LIKE '%{bedrooms} B/R%')"
        
        # Build SQL query with optional development status filter
        status_condition = ""
        if development_status:
            status_condition = f"AND is_offplan_en = '{development_status}'"
        
        # Build ESG score filter
        esg_condition = ""
        if esg_score_min:
            # Find ESG column using dynamic mapping (follows existing pattern)
            esg_col = find_column_name(SALES_COLUMNS, ['esg_score', 'sustainability_score', 'esg_rating'])
            if esg_col:
                esg_condition = f"AND {esg_col} >= {int(esg_score_min)}"
                print(f"🌱 [DB] Filtering for ESG score >= {esg_score_min}")
        
        flip_condition = ""
        if flip_score_min:
            # Find Flip column using dynamic mapping (follows existing pattern)
            flip_col = find_column_name(SALES_COLUMNS, ['flip_score', 'investment_score', 'flip_rating'])
            if flip_col:
                flip_condition = f"AND {flip_col} >= {int(flip_score_min)}"
                print(f"📈 [DB] Filtering for Flip score >= {flip_score_min}")
        
        # Enhanced SQL query to get comprehensive comparable properties from database
        query = text(f"""
        SELECT 
            area_en as area_name_en,
            prop_type_en as property_type_en,
            trans_value as property_total_value,
            actual_area,
            instance_date,
            project_en,
            rooms_en,
            is_offplan_en
        FROM properties 
        WHERE 
            trans_value > 0 
            AND actual_area IS NOT NULL 
            AND actual_area != ''
            AND actual_area ~ '^[0-9]+\\.?[0-9]*$'  -- Valid numeric format
            AND CAST(actual_area AS NUMERIC) > 0 
            AND area_en IS NOT NULL 
            AND prop_type_en IS NOT NULL
            AND trans_value BETWEEN 100000 AND 50000000  -- Reasonable price range
            AND CAST(actual_area AS NUMERIC) BETWEEN 20 AND 2000  -- Reasonable area range
            {bedroom_condition}
            {status_condition}
            {esg_condition}
            {flip_condition}
            AND (
                LOWER(area_en) LIKE LOWER(:area_param)
                OR (
                    LOWER(prop_type_en) = LOWER(:property_type_param)
                    AND CAST(actual_area AS NUMERIC) BETWEEN :size_min AND :size_max
                )
            )
        ORDER BY 
            CASE 
                WHEN LOWER(area_en) LIKE LOWER(:area_param) 
                AND LOWER(prop_type_en) = LOWER(:property_type_param) THEN 1
                WHEN LOWER(area_en) LIKE LOWER(:area_param) THEN 2
                WHEN LOWER(prop_type_en) = LOWER(:property_type_param) THEN 3
                ELSE 4
            END,
            ABS(CAST(actual_area AS NUMERIC) - :target_size),
            instance_date DESC
        LIMIT 500
        """)
        
        # Parameters for the query
        size_range_factor = 0.3  # ±30%
        params = {
            'area_param': f'%{area}%',
            'property_type_param': property_type,
            'size_min': size_sqm * (1 - size_range_factor),
            'size_max': size_sqm * (1 + size_range_factor),
            'target_size': size_sqm
        }
        
        # Execute query
        with engine.connect() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        
        print(f"🔍 [DB] Found {len(df)} properties in database query")
        
        if len(df) == 0:
            # Check if ESG filter caused empty results
            if esg_score_min:
                error_msg = f"No properties found with ESG score {esg_score_min}+ for {property_type} in {area}. Current ESG data ranges from 25-55. Please try a lower ESG threshold (25+, 40+) or select 'Any Score'."
            else:
                error_msg = f"No comparable properties found in database for {property_type} in {area}"
            raise ValueError(error_msg)
        
        # Data cleaning and preparation
        df = df.dropna(subset=['property_total_value', 'actual_area'])
        
        # Convert string columns to numeric
        df['property_total_value'] = pd.to_numeric(df['property_total_value'], errors='coerce')
        df['actual_area'] = pd.to_numeric(df['actual_area'], errors='coerce')
        
        # Remove rows with invalid numeric conversion
        df = df.dropna(subset=['property_total_value', 'actual_area'])
        
        df = df[df['property_total_value'] > 0]
        df = df[df['actual_area'] > 0]
        
        # Add calculated fields
        df['price_per_sqm'] = df['property_total_value'] / df['actual_area']
        
        # Remove outliers based on price per sqm
        q1 = df['price_per_sqm'].quantile(0.15)
        q3 = df['price_per_sqm'].quantile(0.85)
        df = df[(df['price_per_sqm'] >= q1) & (df['price_per_sqm'] <= q3)]
        
        print(f"📊 [DB] After cleaning: {len(df)} properties remain")
        
        if len(df) == 0:
            raise ValueError("No valid comparable properties after data cleaning")
        
        # Prioritize area + type matches
        area_matches = df[df['area_name_en'].str.contains(area, case=False, na=False)]
        type_matches = df[df['property_type_en'].str.lower() == property_type.lower()]
        area_type_matches = df[
            (df['area_name_en'].str.contains(area, case=False, na=False)) & 
            (df['property_type_en'].str.lower() == property_type.lower())
        ]
        
        # Size filtering for best matches
        size_range = (size_sqm * 0.7, size_sqm * 1.3)
        area_type_size_matches = area_type_matches[
            (area_type_matches['actual_area'] >= size_range[0]) & 
            (area_type_matches['actual_area'] <= size_range[1])
        ]
        
        # Determine which dataset to use for valuation
        if len(area_type_size_matches) >= 5:
            comparables = area_type_size_matches
            confidence_base = 95
            search_scope = f"area + type + size ({area})"
        elif len(area_type_matches) >= 5:
            comparables = area_type_matches
            confidence_base = 90
            search_scope = f"area + type ({area})"
        elif len(area_matches) >= 5:
            comparables = area_matches
            confidence_base = 85
            search_scope = f"area-wide ({area})"
        elif len(type_matches) >= 5:
            comparables = type_matches
            confidence_base = 80
            search_scope = f"city-wide ({property_type})"
        else:
            comparables = df.head(20)  # Use top 20 from sorted results
            confidence_base = 75
            search_scope = "city-wide (mixed)"
        
        print(f"✅ [DB] Using {len(comparables)} comparables with {search_scope} search")
        
        # Calculate valuation using median (more robust)
        median_price = comparables['property_total_value'].median()
        median_price_per_sqm = comparables['price_per_sqm'].median()
        
        # Size-based estimate
        size_based_estimate = median_price_per_sqm * size_sqm
        
        # Blend estimates (70% median market price, 30% size-based calculation)
        rule_based_estimate = 0.7 * median_price + 0.3 * size_based_estimate
        
        # ================================================================
        # ML HYBRID PREDICTION (PHASE 4 - APPROACH #1)
        # ================================================================
        ml_prediction_result = None
        ml_price = None
        final_valuation_method = 'rule_based'
        
        if USE_ML and len(comparables) > 0:
            try:
                # Prepare property data for ML prediction using first comparable as template
                sample_prop = comparables.iloc[0]
                ml_input = {
                    'actual_area': size_sqm,
                    'area_en': area,
                    'prop_type_en': property_type,
                    'rooms_en': bedrooms if bedrooms else sample_prop.get('rooms_en', ''),
                    'is_offplan_en': development_status if development_status else sample_prop.get('is_offplan_en', 'No'),
                    'is_free_hold_en': sample_prop.get('is_free_hold_en', 'Yes'),
                    'project_en': sample_prop.get('project_en', ''),
                    'group_en': sample_prop.get('group_en', ''),
                    'procedure_en': sample_prop.get('procedure_en', ''),
                    'parking': sample_prop.get('parking', ''),
                    'nearest_metro_en': sample_prop.get('nearest_metro_en', ''),
                    'nearest_mall_en': sample_prop.get('nearest_mall_en', ''),
                    'nearest_landmark_en': sample_prop.get('nearest_landmark_en', ''),
                    'usage_en': sample_prop.get('usage_en', 'Residential'),
                    'prop_sb_type_en': sample_prop.get('prop_sb_type_en', ''),
                    'procedure_area': sample_prop.get('procedure_area', size_sqm),
                    'total_buyer': 1,
                    'total_seller': 1
                }
                
                ml_prediction_result = predict_price_ml(ml_input)
                
                if ml_prediction_result and ml_prediction_result['predicted_price']:
                    ml_price = ml_prediction_result['predicted_price']
                    ml_confidence = ml_prediction_result['confidence']
                    
                    print(f"🤖 [ML] Prediction: AED {ml_price:,.0f} (confidence: {ml_confidence:.1%})")
                    print(f"📊 [RULE] Rule-based: AED {rule_based_estimate:,.0f}")
                    
                    # Hybrid approach: 70% ML + 30% Rules (weighted by ML confidence)
                    ml_weight = 0.70 * ml_confidence
                    rule_weight = 1 - ml_weight
                    
                    estimated_value = (ml_weight * ml_price) + (rule_weight * rule_based_estimate)
                    final_valuation_method = 'hybrid'
                    
                    print(f"✨ [HYBRID] Final: AED {estimated_value:,.0f} (ML: {ml_weight:.1%}, Rules: {rule_weight:.1%})")
                else:
                    estimated_value = rule_based_estimate
                    print(f"⚠️ [ML] Prediction unavailable, using rule-based only")
            except Exception as e:
                print(f"❌ [ML] Error: {e}. Falling back to rule-based")
                estimated_value = rule_based_estimate
        else:
            estimated_value = rule_based_estimate
            if not USE_ML:
                print(f"ℹ️ [ML] Model not loaded, using rule-based only")
        
        # ================================================================
        # END ML HYBRID PREDICTION
        # ================================================================
        
        # Calculate confidence score
        confidence = confidence_base
        
        # Bonus for more data
        if len(comparables) >= 20:
            confidence += 3
        elif len(comparables) >= 10:
            confidence += 2
        
        # Bonus for recent data (last 2 years)
        if 'instance_date' in comparables.columns:
            recent_data = pd.to_datetime(comparables['instance_date'], errors='coerce')
            recent_count = (recent_data >= (datetime.now() - pd.DateOffset(years=2))).sum()
            if recent_count > len(comparables) * 0.7:
                confidence += 3
        
        # Penalty for high variance
        price_variance = comparables['property_total_value'].std() / comparables['property_total_value'].mean()
        if price_variance > 0.25:
            confidence -= 3
        elif price_variance < 0.15:
            confidence += 2
        
        confidence = min(max(confidence, 70), 98)  # Keep between 70-98%
        
        # --- RENTAL YIELD CALCULATION (NEW) ---
        rental_data = None
        try:
            print(f"🏠 [RENTAL] Querying rental comparables for {area}, {property_type}")
            
            # Query rental comparables for the same area and property type
            # NOTE: Rentals have both prop_type_en and prop_sub_type_en columns
            # Search in BOTH to maximize results (e.g., "Unit" might be in prop_type_en, not prop_sub_type_en)
            # IMPORTANT: Filter by size (±30%) to get accurate yield for similar properties
            size_min = size_sqm * 0.7  # 30% smaller
            size_max = size_sqm * 1.3  # 30% larger
            
            rental_query = text(f"""
                SELECT 
                    "annual_amount",
                    "prop_sub_type_en",
                    "prop_type_en",
                    "actual_area",
                    "area_en",
                    "registration_date",
                    "project_en"
                FROM rentals 
                WHERE LOWER("area_en") = LOWER(:area)
                AND (
                    LOWER("prop_type_en") LIKE LOWER(:property_type)
                    OR LOWER("prop_sub_type_en") LIKE LOWER(:property_type)
                )
                AND "annual_amount" > 10000 
                AND "annual_amount" < 5000000
                AND "actual_area" IS NOT NULL
                AND "actual_area" != ''
                AND "actual_area" ~ '^[0-9]+\\.?[0-9]*$'
                AND CAST("actual_area" AS NUMERIC) > 0
                AND CAST("actual_area" AS NUMERIC) BETWEEN :size_min AND :size_max
                ORDER BY "registration_date" DESC
                LIMIT 50
            """)
            
            rental_df = pd.read_sql(
                rental_query, 
                engine, 
                params={
                    'area': area, 
                    'property_type': f'%{property_type}%',
                    'size_min': size_min,
                    'size_max': size_max
                }
            )
            
            print(f"🔍 [RENTAL] Query returned {len(rental_df)} rows")
            if len(rental_df) > 0:
                print(f"📊 [RENTAL] Sample types: {rental_df['prop_sub_type_en'].unique()[:5].tolist()}")
                
                # Apply outlier filtering (3× IQR method, same as sales)
                q1 = rental_df['annual_amount'].quantile(0.25)
                q3 = rental_df['annual_amount'].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 3 * iqr
                upper_bound = q3 + 3 * iqr
                
                filtered_rentals = rental_df[
                    (rental_df['annual_amount'] >= lower_bound) &
                    (rental_df['annual_amount'] <= upper_bound)
                ]
                
                print(f"🔍 [RENTAL] After outlier filter: {len(filtered_rentals)} rows")
                if len(filtered_rentals) >= 3:
                    median_annual_rent = filtered_rentals['annual_amount'].median()
                    median_size = filtered_rentals['actual_area'].astype(float).median()
                    
                    # Create rental comparables array for frontend display
                    rental_comparables = []
                    for idx, row in filtered_rentals.iterrows():
                        try:
                            size_sqm = float(row['actual_area']) if row['actual_area'] else 0
                            annual_rent = int(row['annual_amount'])
                            rent_per_sqm = int(annual_rent / size_sqm) if size_sqm > 0 else 0
                            
                            rental_comparables.append({
                                'project_name': row.get('project_en') or row.get('area_en', 'N/A'),
                                'location': row.get('area_en', 'N/A'),
                                'size_sqm': size_sqm,
                                'annual_rent': annual_rent,
                                'rent_per_sqm': rent_per_sqm,
                                'listing_date': str(row.get('registration_date', '')),
                                'property_type': row.get('prop_type_en') or row.get('prop_sub_type_en', 'N/A')
                            })
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ [RENTAL] Skipping row due to conversion error: {e}")
                            continue
                    
                    rental_data = {
                        'annual_rent': round(median_annual_rent),
                        'count': len(filtered_rentals),
                        'price_range': {
                            'low': round(filtered_rentals['annual_amount'].quantile(0.25)),
                            'high': round(filtered_rentals['annual_amount'].quantile(0.75))
                        },
                        'is_city_average': False,
                        'comparables': rental_comparables,
                        'median_size': round(median_size, 1),
                        'median_rent_per_sqm': round(median_annual_rent / median_size) if median_size > 0 else 0
                    }
                    print(f"✅ [RENTAL] Found {len(filtered_rentals)} rental comparables, median: {median_annual_rent:,.0f} AED/year")
                    print(f"📊 [RENTAL] Prepared {len(rental_comparables)} comparables for display")
                else:
                    print(f"⚠️ [RENTAL] Only {len(filtered_rentals)} rentals after filtering (need >= 3)")
            
            # Fallback to city-wide average if insufficient area-specific rentals
            if rental_data is None:
                print(f"⚠️ [RENTAL] Insufficient area rentals, trying city-wide for {property_type}")
                # Also filter city-wide by size (±30%) for better accuracy
                city_rental_query = text(f"""
                    SELECT 
                        "annual_amount",
                        "actual_area",
                        "area_en",
                        "registration_date",
                        "project_en",
                        "prop_type_en",
                        "prop_sub_type_en"
                    FROM rentals 
                    WHERE (
                        LOWER("prop_type_en") LIKE LOWER(:property_type)
                        OR LOWER("prop_sub_type_en") LIKE LOWER(:property_type)
                    )
                    AND "annual_amount" > 10000 
                    AND "annual_amount" < 5000000
                    AND "actual_area" IS NOT NULL
                    AND "actual_area" != ''
                    AND "actual_area" ~ '^[0-9]+\\.?[0-9]*$'
                    AND CAST("actual_area" AS NUMERIC) > 0
                    AND CAST("actual_area" AS NUMERIC) BETWEEN :size_min AND :size_max
                    ORDER BY "registration_date" DESC
                    LIMIT 100
                """)
                
                city_rental_df = pd.read_sql(
                    city_rental_query, 
                    engine, 
                    params={
                        'property_type': f'%{property_type}%',
                        'size_min': size_min,
                        'size_max': size_max
                    }
                )
                
                print(f"🔍 [RENTAL] City-wide query returned {len(city_rental_df)} rows")
                if len(city_rental_df) >= 10:
                    median_city_rent = city_rental_df['annual_amount'].median()
                    median_city_size = city_rental_df['actual_area'].astype(float).median()
                    
                    # Create rental comparables array for city-wide data
                    city_rental_comparables = []
                    for idx, row in city_rental_df.iterrows():
                        try:
                            size_sqm = float(row['actual_area']) if row['actual_area'] else 0
                            annual_rent = int(row['annual_amount'])
                            rent_per_sqm = int(annual_rent / size_sqm) if size_sqm > 0 else 0
                            
                            city_rental_comparables.append({
                                'project_name': row.get('project_en') or row.get('area_en', 'N/A'),
                                'location': row.get('area_en', 'N/A'),
                                'size_sqm': size_sqm,
                                'annual_rent': annual_rent,
                                'rent_per_sqm': rent_per_sqm,
                                'listing_date': str(row.get('registration_date', '')),
                                'property_type': row.get('prop_type_en') or row.get('prop_sub_type_en', 'N/A')
                            })
                        except (ValueError, TypeError) as e:
                            print(f"⚠️ [RENTAL] Skipping city-wide row due to conversion error: {e}")
                            continue
                    
                    rental_data = {
                        'annual_rent': round(median_city_rent),
                        'count': len(city_rental_df),
                        'is_city_average': True,
                        'comparables': city_rental_comparables,
                        'median_size': round(median_city_size, 1),
                        'median_rent_per_sqm': round(median_city_rent / median_city_size) if median_city_size > 0 else 0,
                        'price_range': {
                            'low': round(city_rental_df['annual_amount'].quantile(0.25)),
                            'high': round(city_rental_df['annual_amount'].quantile(0.75))
                        }
                    }
                    print(f"✅ [RENTAL] Using city-wide average: {median_city_rent:,.0f} AED/year ({len(city_rental_df)} rentals)")
                    print(f"📊 [RENTAL] Prepared {len(city_rental_comparables)} city-wide comparables for display")
                else:
                    print(f"⚠️ [RENTAL] Only {len(city_rental_df)} city-wide rentals found (need >= 10)")
        
        except Exception as rental_error:
            print(f"⚠️ [RENTAL] Could not fetch rental data: {rental_error}")
            rental_data = None
        # --- END RENTAL CALCULATION ---
        
        # ================================================================
        # GEOSPATIAL LOCATION PREMIUM (NEW)
        # Added: October 6, 2025
        # ================================================================
        location_premium_pct = 0
        location_breakdown = {}
        cache_status = 'DISABLED'
        
        try:
            print(f"📍 [GEO] Checking location premium for {area}...")
            
            # Step 1: Check cache first
            cache_data = get_location_cache(area, property_type, bedrooms)
            
            if cache_data['cache_hit']:
                # Cache hit - use cached premium
                location_premium_pct = cache_data['premium']
                location_breakdown = cache_data['breakdown']
                cache_status = 'HIT'
                print(f"⚡ [GEO] Cache HIT: {location_premium_pct:+.1f}% premium (hits: {cache_data.get('hits', 0)})")
            else:
                # Cache miss - calculate premium
                premium_data = calculate_location_premium(area)
                
                if premium_data:
                    location_premium_pct = premium_data['total_premium']
                    location_breakdown = {
                        'metro': premium_data['metro_premium'],
                        'beach': premium_data['beach_premium'],
                        'mall': premium_data['mall_premium'],
                        'school': premium_data['school_premium'],
                        'business': premium_data['business_premium'],
                        'neighborhood': premium_data['neighborhood_premium']
                    }
                    cache_status = 'MISS'
                    
                    # Store in cache for future requests
                    update_location_cache(area, property_type, bedrooms, premium_data)
                    
                    print(f"💾 [GEO] Cache MISS: Calculated {location_premium_pct:+.1f}% premium, cached for future")
                    print(f"   📊 [GEO] Breakdown: Metro:{premium_data['metro_premium']:+.1f}%, Beach:{premium_data['beach_premium']:+.1f}%, Mall:{premium_data['mall_premium']:+.1f}%")
                else:
                    # Area not found in geospatial database
                    cache_status = 'NOT_FOUND'
                    print(f"⚠️  [GEO] Area '{area}' not in geospatial database, no premium applied")
            
            # Apply location premium to estimated value
            if location_premium_pct != 0:
                base_value = estimated_value
                estimated_value = estimated_value * (1 + location_premium_pct / 100)
                adjustment = estimated_value - base_value
                print(f"✨ [GEO] Applied {location_premium_pct:+.1f}% location premium: AED {adjustment:+,.0f}")
                print(f"   💰 [GEO] Base value: AED {base_value:,.0f} → Adjusted value: AED {estimated_value:,.0f}")
            
        except Exception as e:
            print(f"❌ [GEO] Location premium error (non-critical): {e}")
            # Don't fail valuation if geospatial fails
            location_premium_pct = 0
            location_breakdown = {}
            cache_status = 'ERROR'
        
        # ================================================================
        # END GEOSPATIAL PREMIUM
        # ================================================================
        
        # ================================================================
        # PROJECT PREMIUM (NEW)
        # Added: October 8, 2025
        # ================================================================
        project_premium_pct = 0
        project_tier = None
        project_name = None
        
        try:
            # Get project name from the subject property (first comparable)
            if len(comparables) > 0 and 'project_en' in comparables.columns:
                project_name = comparables.iloc[0]['project_en']
                
                if project_name and str(project_name).strip():
                    print(f"🏢 [PROJECT] Checking premium for '{project_name}'...")
                    project_data = get_project_premium(project_name)
                    project_premium_pct = project_data['premium_percentage']
                    project_tier = project_data['tier']
                    
                    if project_premium_pct > 0:
                        print(f"⭐ [PROJECT] Premium project detected: {project_tier} tier")
                        print(f"   💎 [PROJECT] Premium: +{project_premium_pct:.1f}%")
                    else:
                        print(f"ℹ️  [PROJECT] Standard project (no premium)")
                else:
                    print(f"ℹ️  [PROJECT] No project name available")
            
            # Apply project premium to estimated value
            if project_premium_pct > 0:
                base_value = estimated_value
                estimated_value = estimated_value * (1 + project_premium_pct / 100)
                adjustment = estimated_value - base_value
                print(f"✨ [PROJECT] Applied +{project_premium_pct:.1f}% project premium: AED {adjustment:+,.0f}")
                print(f"   💰 [PROJECT] Value: AED {base_value:,.0f} → AED {estimated_value:,.0f}")
            
            # Calculate combined premium
            combined_premium_pct = location_premium_pct + project_premium_pct
            if combined_premium_pct != 0:
                print(f"🎯 [PREMIUM] Combined premium: {location_premium_pct:+.1f}% (location) + {project_premium_pct:+.1f}% (project) = {combined_premium_pct:+.1f}%")
        
        except Exception as e:
            print(f"❌ [PROJECT] Project premium error (non-critical): {e}")
            # Don't fail valuation if project premium fails
            project_premium_pct = 0
            project_tier = None
            project_name = None
        
        # ================================================================
        # PHASE 3: PROPERTY-SPECIFIC PREMIUMS (Floor, View, Age)
        # ================================================================
        
        floor_premium_pct = 0
        view_premium_pct = 0
        age_premium_pct = 0
        
        try:
            # Calculate floor premium
            if floor_level is not None:
                floor_premium_pct = calculate_floor_premium(floor_level, property_type)
                if floor_premium_pct > 0:
                    base_value = estimated_value
                    estimated_value = estimated_value * (1 + floor_premium_pct / 100)
                    adjustment = estimated_value - base_value
                    print(f"🏢 [FLOOR] Applied +{floor_premium_pct:.1f}% floor premium (Floor {floor_level}): AED {adjustment:+,.0f}")
                    print(f"   💰 [FLOOR] Value: AED {base_value:,.0f} → AED {estimated_value:,.0f}")
                elif property_type and property_type.lower() in ['villa', 'townhouse', 'land']:
                    print(f"ℹ️  [FLOOR] Floor premium not applicable for {property_type}")
            
            # Calculate view premium
            if view_type:
                view_premium_pct = calculate_view_premium(view_type, area)
                if view_premium_pct > 0:
                    base_value = estimated_value
                    estimated_value = estimated_value * (1 + view_premium_pct / 100)
                    adjustment = estimated_value - base_value
                    print(f"👁️  [VIEW] Applied +{view_premium_pct:.1f}% view premium ({view_type}): AED {adjustment:+,.0f}")
                    print(f"   💰 [VIEW] Value: AED {base_value:,.0f} → AED {estimated_value:,.0f}")
            
            # Calculate age premium (can be negative for older properties)
            if property_age is not None:
                # Detect if property is off-plan (can be enhanced with database field later)
                is_offplan = property_age == 0
                age_premium_pct = calculate_age_premium(property_age, property_type, is_offplan)
                
                if age_premium_pct != 0:
                    base_value = estimated_value
                    estimated_value = estimated_value * (1 + age_premium_pct / 100)
                    adjustment = estimated_value - base_value
                    
                    if age_premium_pct > 0:
                        print(f"⭐ [AGE] Applied +{age_premium_pct:.1f}% new property premium (Age: {property_age} years): AED {adjustment:+,.0f}")
                    else:
                        print(f"📉 [AGE] Applied {age_premium_pct:.1f}% age depreciation (Age: {property_age} years): AED {adjustment:,.0f}")
                    print(f"   💰 [AGE] Value: AED {base_value:,.0f} → AED {estimated_value:,.0f}")
            
            # Calculate total combined premium
            combined_premium_pct = (location_premium_pct + project_premium_pct + 
                                   floor_premium_pct + view_premium_pct + age_premium_pct)
            
            # Apply premium cap (-20% to +70%)
            uncapped_premium = combined_premium_pct
            combined_premium_pct = max(-20.0, min(70.0, combined_premium_pct))
            
            if uncapped_premium != combined_premium_pct:
                print(f"⚠️  [PREMIUM CAP] Total premium capped at {combined_premium_pct:+.1f}% (would be {uncapped_premium:+.1f}%)")
            
            if combined_premium_pct != 0:
                premium_parts = []
                if location_premium_pct != 0:
                    premium_parts.append(f"{location_premium_pct:+.1f}% (location)")
                if project_premium_pct != 0:
                    premium_parts.append(f"{project_premium_pct:+.1f}% (project)")
                if floor_premium_pct != 0:
                    premium_parts.append(f"{floor_premium_pct:+.1f}% (floor)")
                if view_premium_pct != 0:
                    premium_parts.append(f"{view_premium_pct:+.1f}% (view)")
                if age_premium_pct != 0:
                    premium_parts.append(f"{age_premium_pct:+.1f}% (age)")
                
                print(f"🎯 [PREMIUM] Total premium: {' + '.join(premium_parts)} = {combined_premium_pct:+.1f}%")
        
        except Exception as e:
            print(f"❌ [PHASE 3] Property-specific premium error (non-critical): {e}")
            # Don't fail valuation if Phase 3 premiums fail
            floor_premium_pct = 0
            view_premium_pct = 0
            age_premium_pct = 0
        
        # ================================================================
        # END PHASE 3 PREMIUMS
        # ================================================================
        
        # Calculate value range (AFTER all adjustments)
        std_dev = comparables['property_total_value'].std()
        margin = max(std_dev * 0.12, estimated_value * 0.08)  # At least 8% margin
        
        # Prepare comparable properties for response
        comparable_list = []
        for _, comp in comparables.head(10).iterrows():
            comparable_list.append({
                'area_name': comp.get('area_name_en', 'N/A'),
                'property_type': comp.get('property_type_en', 'N/A'),
                'area_sqm': float(comp.get('actual_area', 0)),
                'sold_price': float(comp.get('property_total_value', 0)),
                'price_per_sqm': float(comp.get('price_per_sqm', 0)),
                'project': comp.get('project_en', 'N/A'),
                'transaction_date': str(comp.get('instance_date', 'N/A'))
            })
        
        # Calculate price per sqm and classify segment
        price_per_sqm_value = round(estimated_value / size_sqm) if size_sqm > 0 else 0
        segment_info = classify_price_segment(price_per_sqm_value)
        
        result = {
            'success': True,
            'valuation': {
                'estimated_value': round(estimated_value),
                'confidence_score': round(confidence, 1),
                'price_per_sqm': price_per_sqm_value,
                'segment': segment_info,  # Market segment classification
                'value_range': {
                    'low': round(estimated_value - margin),
                    'high': round(estimated_value + margin)
                },
                'rental_data': rental_data,  # Rental yield data
                'location_premium': {  # Geospatial location premium
                    'total_premium_pct': round(location_premium_pct, 2),
                    'breakdown': location_breakdown,
                    'cache_status': cache_status,
                    'applied': location_premium_pct != 0
                },
                'project_premium': {  # NEW: Project-specific premium
                    'premium_pct': round(project_premium_pct, 2),
                    'tier': project_tier,
                    'project_name': project_name,
                    'applied': project_premium_pct > 0,
                    'breakdown': get_project_premium_breakdown(
                        project_name, 
                        project_premium_pct, 
                        project_tier,
                        len(comparables),
                        round(median_price_per_sqm) if 'median_price_per_sqm' in locals() else 0
                    ) if project_premium_pct > 0 else [],
                    'similar_projects': MOCK_SIMILAR_PROJECTS.get(project_name, []) if project_premium_pct > 0 else []  # Using mock data for Phase 2 Quick Win
                },
                'floor_premium': {  # PHASE 3: Floor level premium
                    'percentage': round(floor_premium_pct, 2),
                    'floor_level': floor_level,
                    'applicable': floor_level is not None and floor_premium_pct != 0,
                    'value': round((estimated_value / (1 + age_premium_pct / 100) / (1 + view_premium_pct / 100)) * (floor_premium_pct / 100)) if floor_premium_pct != 0 else 0
                },
                'view_premium': {  # PHASE 3: View quality premium
                    'percentage': round(view_premium_pct, 2),
                    'view_type': view_type,
                    'applicable': view_type is not None and view_premium_pct != 0,
                    'value': round((estimated_value / (1 + age_premium_pct / 100)) * (view_premium_pct / 100) / (1 + view_premium_pct / 100)) if view_premium_pct != 0 else 0
                },
                'age_premium': {  # PHASE 3: Property age premium/depreciation
                    'percentage': round(age_premium_pct, 2),
                    'property_age': property_age,
                    'applicable': property_age is not None and age_premium_pct != 0,
                    'value': round(estimated_value * (age_premium_pct / 100) / (1 + age_premium_pct / 100)) if age_premium_pct != 0 else 0,
                    'is_new_property': property_age == 0 if property_age is not None else False
                },
                'combined_premium': round(location_premium_pct + project_premium_pct + floor_premium_pct + view_premium_pct + age_premium_pct, 2),  # Updated: Total premium including Phase 3
                'comparables': comparable_list,
                'total_comparables_found': len(comparables),
                'valuation_date': datetime.now().isoformat(),
                'data_source': f"Production Database ({len(df):,} properties analyzed)",
                'search_scope': search_scope,
                'market_data': {
                    'median_price_per_sqm': round(median_price_per_sqm),
                    'price_variance': round(price_variance * 100, 1)
                },
                'ml_data': {  # PHASE 4: ML Hybrid Prediction Data
                    'ml_enabled': USE_ML,
                    'ml_price': round(ml_price) if ml_price else None,
                    'rule_based_price': round(rule_based_estimate),
                    'final_price': round(estimated_value),
                    'valuation_method': final_valuation_method,
                    'ml_confidence': round(ml_prediction_result['confidence'] * 100, 1) if ml_prediction_result else None,
                    'ml_model': ml_prediction_result['method'] if ml_prediction_result else None
                }
            }
        }
        
        print(f"💰 [DB] Valuation complete: {estimated_value:,.0f} AED ({confidence:.1f}% confidence)")
        return result
        
    except Exception as e:
        print(f"❌ [DB] Valuation error: {e}")
        return {
            'success': False,
            'error': str(e),
            'valuation': None
        }

@app.route('/api/export-premium-csv', methods=['POST'])
def export_premium_csv():
    """
    Export project premium breakdown as CSV file.
    Accepts project data and returns downloadable CSV.
    """
    try:
        data = request.json
        project_name = data.get('project_name', 'project')
        tier = data.get('tier', 'Premium')
        premium_pct = data.get('premium_pct', 0)
        breakdown = data.get('breakdown', [])
        
        # Create CSV in memory
        import io
        import csv
        from datetime import date
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header section
        writer.writerow(['Project Premium Breakdown Report'])
        writer.writerow(['Generated:', date.today().strftime('%B %d, %Y')])
        writer.writerow([''])
        writer.writerow(['Project Name:', project_name])
        writer.writerow(['Premium Tier:', tier])
        writer.writerow(['Total Premium:', f'+{premium_pct}%'])
        writer.writerow([''])
        
        # Breakdown table
        writer.writerow(['Factor', 'Percentage', 'Description'])
        for item in breakdown:
            writer.writerow([
                item.get('factor', ''),
                f"+{item.get('percentage', 0)}%",
                item.get('description', '')
            ])
        
        # Prepare download
        output.seek(0)
        safe_name = project_name.replace(' ', '-').replace('/', '-').lower()
        filename = f"premium-breakdown-{safe_name}-{date.today()}.csv"
        
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )
        
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        return jsonify({'error': str(e)}), 500

# --- BUY TAB ENDPOINTS ---
@app.route('/search', methods=['POST'])
@login_required
def search_buy():
    if not engine: return jsonify({'summary': "DB not configured.", 'data': []})
    data = request.json
    where_clause, params = build_where_clause(data, SALES_MAP, 'budget')
    
    count_query = text(f"SELECT COUNT(*) FROM properties WHERE {where_clause};")
    display_query = text(f"SELECT * FROM properties WHERE {where_clause} ORDER BY instance_date DESC LIMIT 500;")
    
    with engine.connect() as conn:
        try:
            total_results = conn.execute(count_query, params).scalar_one()
            results_df = pd.read_sql_query(display_query, conn, params=params)
            display_results_list = results_df.to_dict(orient='records')
        except Exception as e:
            print(f"❌ BUY SEARCH FAILED: {e}")
            total_results, results_df, display_results_list = 0, pd.DataFrame(), []

    ai_summary = generate_ai_summary(data, results_df, total_results, 'buy')
    return jsonify({'summary': ai_summary, 'data': display_results_list})

@app.route('/api/analytics', methods=['POST'])
@login_required
def get_buy_analytics():
    if not engine: return jsonify({'stats': {}})
    data = request.json
    where_clause, params = build_where_clause(data, SALES_MAP, 'budget')
    price_col = f"\"{SALES_MAP['price']}\""
    
    # Enhanced analytics query with price per square meter calculation
    analytics_query = text(f"""
        SELECT 
            COUNT(*) as total_transactions,
            SUM({price_col}) as total_volume,
            AVG({price_col}) as average_price,
            AVG(
                CASE 
                    WHEN "actual_area" IS NOT NULL 
                    AND "actual_area" != '' 
                    AND CAST("actual_area" AS FLOAT) > 0 
                    THEN {price_col} / CAST("actual_area" AS FLOAT)
                    ELSE NULL 
                END
            ) as average_price_per_sqm
        FROM properties 
        WHERE {where_clause};
    """)
    
    with engine.connect() as conn:
        try:
            result = conn.execute(analytics_query, params)
            stats_raw = result.fetchone()
            stats = dict(stats_raw._mapping) if stats_raw else {}
        except Exception as e:
            print(f"❌ BUY ANALYTICS FAILED: {e}")
            stats = {}
    return jsonify({'stats': stats})

@app.route('/api/avm-analytics', methods=['POST'])
@login_required
def get_avm_analytics():
    """New endpoint for detailed AVM metrics"""
    if not engine: return jsonify({'avm_data': None})
    data = request.json
    search_type = 'buy'  # Default to buy, can be extended for rent
    
    where_clause, params = build_where_clause(data, SALES_MAP, 'budget')
    display_query = text(f"SELECT * FROM properties WHERE {where_clause} ORDER BY instance_date DESC LIMIT 1000;")
    
    with engine.connect() as conn:
        try:
            results_df = pd.read_sql_query(display_query, conn, params=params)
            avm_data = calculate_avm_metrics(results_df, search_type, data)
            return jsonify({'avm_data': avm_data})
        except Exception as e:
            print(f"❌ AVM ANALYTICS FAILED: {e}")
            return jsonify({'avm_data': None})

@app.route('/api/trends/price-timeline', methods=['POST'])
@login_required
def get_price_timeline():
    """New endpoint for market trends analysis"""
    if not engine: 
        return jsonify({
            'timeline': [],
            'summary': {'trend_direction': 'error', 'summary': 'Database not configured'}
        })
    
    try:
        data = request.json
        search_type = data.get('search_type', 'buy')  # buy or rent
        time_period = data.get('time_period', '6M')   # 3M, 6M, 1Y
        
        print(f"🔍 TRENDS REQUEST: {search_type}, {time_period}, filters: {data}")
        
        # Pass all filter parameters to get_price_trends
        timeline_data = get_price_trends(data, search_type, time_period)
        
        # Calculate trend summary
        trend_summary = calculate_basic_trends(timeline_data)
        
        print(f"🔍 TRENDS RESPONSE: {len(timeline_data)} data points, trend: {trend_summary.get('trend_direction', 'unknown')}")
        
        return jsonify({
            'timeline': timeline_data,
            'summary': trend_summary,
            'status': 'success'
        })
        
    except Exception as e:
        print(f"❌ TRENDS API FAILED: {e}")
        return jsonify({
            'timeline': [],
            'summary': {
                'trend_direction': 'error',
                'percentage_change': 0,
                'summary': f'Error: {str(e)}'
            },
            'status': 'error'
        })

# --- RENT TAB ENDPOINTS ---
@app.route('/rent-search', methods=['POST'])
@login_required
def search_rent():
    if not engine: return jsonify({'summary': "DB not configured.", 'data': []})
    data = request.json
    print(f"🔍 RENT SEARCH DATA: {data}")
    
    # Use any price key since we handle all in build_where_clause
    where_clause, params = build_where_clause(data, RENTALS_MAP, 'annual_rent', is_rent=True)
    
    count_query = text(f"SELECT COUNT(*) FROM rentals WHERE {where_clause};")
    display_query = text(f"SELECT *, {RENTALS_MAP['price']} as trans_value FROM rentals WHERE {where_clause} ORDER BY registration_date DESC LIMIT 500;")
    
    # Retry logic for database connection
    max_retries = 3
    retry_count = 0
    total_results, results_df, display_results_list = 0, pd.DataFrame(), []
    
    while retry_count < max_retries:
        try:
            # Create a new connection for this request
            conn = engine.connect()
            try:
                total_results = conn.execute(count_query, params).scalar_one()
                results_df = pd.read_sql_query(display_query, conn, params=params)
                display_results_list = results_df.to_dict(orient='records')
                print(f"🔍 RENT RESULTS: {total_results} records found")
                conn.close()
                break
            except Exception as e:
                print(f"❌ RENT SEARCH FAILED (attempt {retry_count + 1}): {e}")
                conn.close()
                retry_count += 1
        except Exception as e:
            print(f"❌ CONNECTION FAILED (attempt {retry_count + 1}): {e}")
            retry_count += 1
            time.sleep(1)  # Wait before retrying

    ai_summary = generate_ai_summary(data, results_df, total_results, 'rent')
    return jsonify({'summary': ai_summary, 'data': display_results_list})

@app.route('/api/rent-analytics', methods=['POST'])
@login_required
def get_rent_analytics():
    if not engine: return jsonify({'stats': {}})
    data = request.json
    print(f"🔍 RENT ANALYTICS DATA: {data}")
    
    # FIRST: Let's check what data we actually have
    try:
        conn = engine.connect()
        # Check total records
        total_check = text("SELECT COUNT(*) FROM rentals;")
        total_records = conn.execute(total_check).scalar_one()
        print(f"🔍 TOTAL RENTAL RECORDS: {total_records}")
        
        # Check distinct property types
        prop_check = text("SELECT DISTINCT \"PROP_SUB_TYPE_EN\" FROM rentals WHERE \"PROP_SUB_TYPE_EN\" IS NOT NULL LIMIT 10;")
        prop_result = conn.execute(prop_check)
        prop_types = [row[0] for row in prop_result]
        print(f"🔍 SAMPLE PROPERTY TYPES: {prop_types}")
        
        # Check distinct room types
        room_check = text("SELECT DISTINCT \"ROOMS\" FROM rentals WHERE \"ROOMS\" IS NOT NULL AND \"ROOMS\" != '' LIMIT 10;")
        room_result = conn.execute(room_check)
        room_types = [row[0] for row in room_result]
        print(f"🔍 SAMPLE ROOM TYPES: {room_types}")
        
        # Check sample annual amounts
        amount_check = text("SELECT \"ANNUAL_AMOUNT\" FROM rentals WHERE \"ANNUAL_AMOUNT\" > 0 LIMIT 5;")
        amount_result = conn.execute(amount_check)
        amounts = [row[0] for row in amount_result]
        print(f"🔍 SAMPLE ANNUAL AMOUNTS: {amounts}")
        
        conn.close()
    except Exception as e:
        print(f"🔍 DEBUG CHECK FAILED: {e}")
    
    # Use any price key since we handle all in build_where_clause
    where_clause, params = build_where_clause(data, RENTALS_MAP, 'annual_rent', is_rent=True)
    price_col = f"\"{RENTALS_MAP['price']}\""
    
    # Enhanced rental analytics query with price per square meter calculation
    analytics_query = text(f"""
        SELECT 
            COUNT(*) as total_transactions,
            SUM({price_col}) as total_volume,
            AVG({price_col}) as average_price,
            AVG(
                CASE 
                    WHEN "actual_area" IS NOT NULL 
                    AND "actual_area" != '' 
                    AND CAST("actual_area" AS FLOAT) > 0 
                    THEN {price_col} / CAST("actual_area" AS FLOAT)
                    ELSE NULL 
                END
            ) as average_price_per_sqm
        FROM rentals 
        WHERE {where_clause};
    """)
    
    # Retry logic for database connection
    max_retries = 3
    retry_count = 0
    stats = {}
    
    while retry_count < max_retries:
        try:
            # Create a new connection for this request
            conn = engine.connect()
            try:
                result = conn.execute(analytics_query, params)
                stats_raw = result.fetchone()
                stats = dict(stats_raw._mapping) if stats_raw else {}
                print(f"🔍 RENT ANALYTICS STATS: {stats}")
                conn.close()
                break
            except Exception as e:
                print(f"❌ RENT ANALYTICS FAILED (attempt {retry_count + 1}): {e}")
                conn.close()
                retry_count += 1
        except Exception as e:
            print(f"❌ CONNECTION FAILED (attempt {retry_count + 1}): {e}")
            retry_count += 1
            time.sleep(1)  # Wait before retrying
    
    return jsonify({'stats': stats})

@app.route('/api/rent-avm-analytics', methods=['POST'])
@login_required
def get_rent_avm_analytics():
    """AVM endpoint for rental analytics"""
    if not engine: return jsonify({'avm_data': None})
    data = request.json
    search_type = 'rent'
    
    where_clause, params = build_where_clause(data, RENTALS_MAP, 'annual_rent', is_rent=True)
    display_query = text(f"SELECT *, {RENTALS_MAP['price']} as trans_value FROM rentals WHERE {where_clause} ORDER BY registration_date DESC LIMIT 1000;")
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = engine.connect()
            try:
                results_df = pd.read_sql_query(display_query, conn, params=params)
                avm_data = calculate_avm_metrics(results_df, search_type, data)
                conn.close()
                return jsonify({'avm_data': avm_data})
            except Exception as e:
                print(f"❌ RENT AVM ANALYTICS FAILED (attempt {retry_count + 1}): {e}")
                conn.close()
                retry_count += 1
        except Exception as e:
            print(f"❌ CONNECTION FAILED (attempt {retry_count + 1}): {e}")
            retry_count += 1
            time.sleep(1)
    
    return jsonify({'avm_data': None})

# --- GENERAL APP ROUTES ---
@app.route('/')
@login_required
def home():
    return render_template('index.html', sales_map=SALES_MAP, rentals_map=RENTALS_MAP)

@app.route('/api/areas/<search_type>')
@login_required
def get_areas(search_type):
    if not engine: return jsonify([])
    
    # Support trends by using properties table (similar to buy)
    if search_type in ['buy', 'trends']:
        table = 'properties'
        area_col = SALES_MAP['area_name']
    else:  # rent
        table = 'rentals'
        area_col = RENTALS_MAP['area_name']
    
    # Retry logic for database connection
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Create a new connection for this request
            conn = engine.connect()
            try:
                # Get unique areas (case-insensitive), preferring Title Case over UPPERCASE
                query = text(f"""
                    SELECT DISTINCT ON (LOWER("{area_col}"))
                        "{area_col}"
                    FROM {table}
                    WHERE "{area_col}" IS NOT NULL
                    ORDER BY LOWER("{area_col}"),
                             CASE 
                                 WHEN "{area_col}" ~ '^[A-Z][a-z]' THEN 1  -- Title Case (prefer)
                                 WHEN "{area_col}" = UPPER("{area_col}") THEN 2  -- UPPERCASE
                                 ELSE 3  -- other
                             END,
                             "{area_col}"
                """)
                result = conn.execute(query)
                areas = [row[0] for row in result]
                conn.close()
                return jsonify(areas)
            except Exception as e:
                print(f"❌ AREAS FETCH FAILED for {search_type} (attempt {retry_count + 1}): {e}")
                conn.close()
                retry_count += 1
        except Exception as e:
            print(f"❌ CONNECTION FAILED (attempt {retry_count + 1}): {e}")
            retry_count += 1
            time.sleep(1)  # Wait before retrying
    
    return jsonify([])

@app.route('/api/top-areas', methods=['POST'])
@login_required
def get_top_areas():
    """Get top performing areas by transaction volume - Basic Implementation"""
    if not engine: 
        return jsonify({'top_areas': [], 'error': 'Database not available'})
    
    data = request.json
    search_type = data.get('search_type', 'buy')  # 'buy' or 'rent'
    time_period = data.get('time_period', '6M')  # '3M', '6M', '1Y'
    limit = data.get('limit', 10)  # Number of top areas to return
    
    # Convert time period to months
    period_months = {'3M': 3, '6M': 6, '1Y': 12}.get(time_period, 6)
    
    # Determine table and columns based on search type
    if search_type == 'buy':
        table = 'properties'
        area_col = SALES_MAP['area_name']
        price_col = SALES_MAP['price']
        date_col = 'instance_date'
    else:
        table = 'rentals' 
        area_col = RENTALS_MAP['area_name']
        price_col = RENTALS_MAP['price']
        date_col = 'registration_date'
    
    # Enhanced query to include price per sqm calculation
    query = text(f"""
        SELECT 
            "{area_col}" as area_name,
            COUNT(*) as transaction_count,
            AVG("{price_col}") as avg_price,
            AVG(
                CASE 
                    WHEN "actual_area" IS NOT NULL 
                    AND "actual_area" != '' 
                    AND CAST("actual_area" AS FLOAT) > 0 
                    THEN "{price_col}" / CAST("actual_area" AS FLOAT)
                    ELSE NULL 
                END
            ) as avg_price_per_sqm,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM {table} WHERE "{area_col}" IS NOT NULL), 2) as market_share_percentage,
            COUNT(CASE WHEN "actual_area" IS NOT NULL AND "actual_area" != '' AND CAST("actual_area" AS FLOAT) > 0 THEN 1 END) as valid_area_count
        FROM {table}
        WHERE "{area_col}" IS NOT NULL 
        AND "{area_col}" != ''
        AND "{price_col}" > 0
        AND CAST("{date_col}" AS DATE) >= NOW() - INTERVAL '{period_months} months'
        GROUP BY "{area_col}"
        HAVING COUNT(*) >= 5
        ORDER BY transaction_count DESC
        LIMIT :limit_param
    """)
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            conn = engine.connect()
            try:
                result = conn.execute(query, {'limit_param': limit})
                top_areas = []
                
                for row in result:
                    top_areas.append({
                        'area_name': row[0],
                        'transaction_count': int(row[1]),
                        'avg_price': float(row[2]) if row[2] else 0,
                        'avg_price_per_sqm': float(row[3]) if row[3] else 0,
                        'market_share_percentage': float(row[4]) if row[4] else 0,
                        'valid_area_count': int(row[5]) if row[5] else 0,
                        'ranking': len(top_areas) + 1
                    })
                
                conn.close()
                print(f"✅ TOP AREAS FETCHED: {len(top_areas)} areas for {search_type} ({time_period})")
                
                return jsonify({
                    'top_areas': top_areas,
                    'search_type': search_type,
                    'time_period': time_period,
                    'total_areas': len(top_areas)
                })
                
            except Exception as e:
                print(f"❌ TOP AREAS QUERY FAILED (attempt {retry_count + 1}): {e}")
                conn.close()
                retry_count += 1
        except Exception as e:
            print(f"❌ CONNECTION FAILED (attempt {retry_count + 1}): {e}")
            retry_count += 1
            time.sleep(1)
    
    return jsonify({'top_areas': [], 'error': 'Failed to fetch data'})

@app.route('/api/property-types/<search_type>')
@login_required
def get_property_types(search_type):
    if not engine: return jsonify([])
    
    # Only provide dynamic property types for rentals
    if search_type == 'rent':
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                conn = engine.connect()
                try:
                    # Get unique values from both PROP_TYPE_EN and PROP_SUB_TYPE_EN
                    prop_type_query = text("SELECT DISTINCT \"PROP_TYPE_EN\" FROM rentals WHERE \"PROP_TYPE_EN\" IS NOT NULL;")
                    prop_sub_type_query = text("SELECT DISTINCT \"PROP_SUB_TYPE_EN\" FROM rentals WHERE \"PROP_SUB_TYPE_EN\" IS NOT NULL;")
                    
                    prop_types = [row[0] for row in conn.execute(prop_type_query)]
                    prop_sub_types = [row[0] for row in conn.execute(prop_sub_type_query)]
                    
                    # Combine and remove duplicates
                    all_types = list(set(prop_types + prop_sub_types))
                    all_types.sort()
                    
                    conn.close()
                    return jsonify(all_types)
                except Exception as e:
                    print(f"❌ PROPERTY TYPES FETCH FAILED for {search_type} (attempt {retry_count + 1}): {e}")
                    conn.close()
                    retry_count += 1
            except Exception as e:
                print(f"❌ CONNECTION FAILED (attempt {retry_count + 1}): {e}")
                retry_count += 1
                time.sleep(1)
        
        return jsonify(['Unit', 'Villa'])  # Fallback
    else:
        # For sales, return static options
        return jsonify(['Unit', 'Building', 'Land'])


# ============================================================================
# PROPERTY FLIP SCORE - Quick Win Feature
# ============================================================================

@app.route('/api/flip-score', methods=['POST'])
@login_required
def flip_score():
    """
    Calculate property flip potential score (1-100)
    
    Formula-based scoring using:
    - Price appreciation (35%)
    - Liquidity/transaction volume (25%)
    - Rental yield (25%)
    - Market segment (15%)
    
    Returns JSON with score, breakdown, and recommendation
    """
    try:
        data = request.get_json()
        
        # Extract and validate parameters
        property_type = data.get('property_type')
        area = data.get('area')
        size_sqm = data.get('size_sqm')
        bedrooms = data.get('bedrooms')
        
        # Validation
        if not all([property_type, area, size_sqm]):
            return jsonify({
                'error': 'Missing required parameters: property_type, area, size_sqm'
            }), 400
        
        try:
            size_sqm = float(size_sqm)
        except (ValueError, TypeError):
            return jsonify({'error': 'size_sqm must be a valid number'}), 400
        
        # Calculate flip score
        result = calculate_flip_score(property_type, area, size_sqm, bedrooms, engine)
        
        return jsonify(result), 200
        
    except Exception as e:
        import logging
        logging.error(f"Flip score calculation error: {str(e)}")
        return jsonify({'error': f'Calculation failed: {str(e)}'}), 500


def calculate_flip_score(property_type: str, area: str, size_sqm: float, bedrooms: str, engine) -> dict:
    """
    Calculate property flip potential score (1-100)
    
    Args:
        property_type: Type of property (Unit, Villa, etc.)
        area: Area name in English
        size_sqm: Property size in square meters
        bedrooms: Number of bedrooms (can be None)
        engine: SQLAlchemy database engine
        
    Returns:
        dict: Flip score with breakdown, rating, and recommendations
    """
    import logging
    
    # Initialize result structure
    result = {
        'flip_score': 0,
        'rating': '',
        'breakdown': {},
        'recommendation': '',
        'confidence': '',
        'data_quality': {}
    }
    
    try:
        # 1. Calculate price appreciation score (35%)
        appreciation_data = _calculate_price_appreciation(area, property_type, engine)
        appreciation_score = appreciation_data['score']
        
        # 2. Calculate liquidity score (25%)
        liquidity_data = _calculate_liquidity_score(area, property_type, engine)
        liquidity_score = liquidity_data['score']
        
        # 3. Calculate rental yield score (25%)
        yield_data = _calculate_yield_score(area, property_type, size_sqm, bedrooms, engine)
        yield_score = yield_data['score']
        
        # 4. Calculate market segment score (15%)
        segment_data = _calculate_segment_score(property_type, area, size_sqm, bedrooms, engine)
        segment_score = segment_data['score']
        
        # Calculate weighted final score
        flip_score = (
            (appreciation_score * 0.35) +
            (liquidity_score * 0.25) +
            (yield_score * 0.25) +
            (segment_score * 0.15)
        )
        
        # Round to integer and ensure 1-100 range
        flip_score = int(round(flip_score))
        flip_score = max(1, min(100, flip_score))
        
        # Build breakdown
        result['flip_score'] = flip_score
        result['breakdown'] = {
            'price_appreciation': {
                'score': appreciation_score,
                'weight': 35,
                'contribution': round(appreciation_score * 0.35, 2),
                'details': appreciation_data.get('details', '')
            },
            'liquidity': {
                'score': liquidity_score,
                'weight': 25,
                'contribution': round(liquidity_score * 0.25, 2),
                'details': liquidity_data.get('details', '')
            },
            'rental_yield': {
                'score': yield_score,
                'weight': 25,
                'contribution': round(yield_score * 0.25, 2),
                'details': yield_data.get('details', '')
            },
            'market_position': {
                'score': segment_score,
                'weight': 15,
                'contribution': round(segment_score * 0.15, 2),
                'details': segment_data.get('details', '')
            }
        }
        
        # Determine rating
        if flip_score >= 80:
            result['rating'] = 'Excellent Flip Potential'
            result['recommendation'] = 'This property shows outstanding flip potential with strong appreciation, high liquidity, and good returns.'
        elif flip_score >= 60:
            result['rating'] = 'Good Flip Potential'
            result['recommendation'] = 'This property has solid flip potential with favorable market conditions and reasonable returns.'
        elif flip_score >= 40:
            result['rating'] = 'Moderate Flip Potential'
            result['recommendation'] = 'This property has moderate flip potential. Consider holding period and market timing carefully.'
        else:
            result['rating'] = 'Low Flip Potential'
            result['recommendation'] = 'This property shows limited flip potential. Better suited for long-term investment or rental income.'
        
        # Determine confidence based on data quality
        total_transactions = appreciation_data.get('transactions', 0) + liquidity_data.get('transactions', 0)
        if total_transactions >= 30:
            result['confidence'] = 'High'
        elif total_transactions >= 10:
            result['confidence'] = 'Medium'
        else:
            result['confidence'] = 'Low'
        
        # Data quality metadata
        result['data_quality'] = {
            'transactions_analyzed': total_transactions,
            'rental_comparables': yield_data.get('comparables', 0),
            'date_range': f"{appreciation_data.get('start_date', 'N/A')} to {appreciation_data.get('end_date', 'N/A')}"
        }
        
        return result
        
    except Exception as e:
        logging.error(f"Flip score calculation error: {str(e)}")
        return {
            'flip_score': 50,
            'rating': 'Unable to Calculate',
            'breakdown': {},
            'recommendation': f'Error calculating flip score: {str(e)}',
            'confidence': 'Low',
            'data_quality': {}
        }


def _calculate_price_appreciation(area: str, property_type: str, engine) -> dict:
    """Calculate price appreciation score based on QoQ growth"""
    import logging
    
    try:
        # Query for quarterly average prices (last 12 months)
        query = text("""
            SELECT 
                EXTRACT(YEAR FROM CAST(instance_date AS TIMESTAMP)) as year,
                EXTRACT(QUARTER FROM CAST(instance_date AS TIMESTAMP)) as quarter,
                AVG(trans_value / CAST(procedure_area AS DOUBLE PRECISION)) as avg_price_sqm,
                COUNT(*) as transaction_count
            FROM properties
            WHERE UPPER(area_en) = UPPER(:area)
              AND prop_type_en = :property_type
              AND CAST(instance_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
              AND trans_value > 0
              AND procedure_area IS NOT NULL
              AND procedure_area ~ '^[0-9.]+$'
            GROUP BY year, quarter
            ORDER BY year DESC, quarter DESC
            LIMIT 4
        """)
        
        result = pd.read_sql(query, engine, params={'area': area, 'property_type': property_type})
        
        if len(result) < 2:
            return {
                'score': 50,
                'details': 'Insufficient data for trend analysis',
                'transactions': 0,
                'start_date': 'N/A',
                'end_date': 'N/A'
            }
        
        # Calculate QoQ growth rate
        latest_price = result.iloc[0]['avg_price_sqm']
        oldest_price = result.iloc[-1]['avg_price_sqm']
        
        if oldest_price == 0 or pd.isna(oldest_price):
            qoq_growth = 0
        else:
            qoq_growth = ((latest_price - oldest_price) / oldest_price) * 100
        
        # Score based on growth rate
        if qoq_growth >= 5:
            score = 100
        elif qoq_growth >= 2:
            score = 70
        elif qoq_growth >= 0:
            score = 40
        else:
            score = 20
        
        return {
            'score': score,
            'details': f'QoQ growth: {qoq_growth:.1f}%',
            'transactions': int(result['transaction_count'].sum()),
            'start_date': f"{int(result.iloc[-1]['year'])}-Q{int(result.iloc[-1]['quarter'])}",
            'end_date': f"{int(result.iloc[0]['year'])}-Q{int(result.iloc[0]['quarter'])}"
        }
        
    except Exception as e:
        logging.error(f"Price appreciation calculation error: {str(e)}")
        return {
            'score': 50,
            'details': 'Error calculating appreciation',
            'transactions': 0,
            'start_date': 'N/A',
            'end_date': 'N/A'
        }


def _calculate_liquidity_score(area: str, property_type: str, engine) -> dict:
    """Calculate liquidity score based on transaction volume"""
    import logging
    
    try:
        query = text("""
            SELECT COUNT(*) as transaction_count
            FROM properties
            WHERE UPPER(area_en) = UPPER(:area)
              AND prop_type_en = :property_type
              AND CAST(instance_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
        """)
        
        result = pd.read_sql(query, engine, params={'area': area, 'property_type': property_type})
        count = int(result.iloc[0]['transaction_count']) if len(result) > 0 else 0
        
        # Score based on transaction volume
        if count >= 50:
            score = 100
        elif count >= 20:
            score = 70
        elif count >= 5:
            score = 40
        else:
            score = 20
        
        return {
            'score': score,
            'details': f'{count} transactions in last 12 months',
            'transactions': count
        }
        
    except Exception as e:
        logging.error(f"Liquidity calculation error: {str(e)}")
        return {
            'score': 50,
            'details': 'Error calculating liquidity',
            'transactions': 0
        }


def _calculate_yield_score(area: str, property_type: str, size_sqm: float, bedrooms: str, engine) -> dict:
    """Calculate rental yield score"""
    import logging
    
    try:
        # Get rental data for this area/type with size filtering (same as main rental yield)
        # Filter rentals within ±30% of property size for better accuracy
        size_min = size_sqm * 0.7
        size_max = size_sqm * 1.3
        
        rental_query = text("""
            SELECT 
                annual_amount,
                actual_area
            FROM rentals
            WHERE UPPER(area_en) = UPPER(:area)
              AND prop_type_en = :property_type
              AND annual_amount > 0
              AND CAST(actual_area AS DOUBLE PRECISION) BETWEEN :size_min AND :size_max
              AND CAST(registration_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
        """)
        
        rental_result = pd.read_sql(rental_query, engine, params={
            'area': area, 
            'property_type': property_type,
            'size_min': size_min,
            'size_max': size_max
        })
        
        if len(rental_result) >= 3:  # Need at least 3 comparables
            # Use MEDIAN rent (same as main rental yield calculation)
            median_rent = rental_result['annual_amount'].median()
            comparables = len(rental_result)
            
            # Estimate property value (simple estimation based on size)
            # Use median price per sqm from recent transactions
            value_query = text("""
                SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY trans_value / CAST(procedure_area AS DOUBLE PRECISION)) as median_price_sqm
                FROM properties
                WHERE UPPER(area_en) = UPPER(:area)
                  AND prop_type_en = :property_type
                  AND CAST(instance_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '6 months'
                  AND trans_value > 0
                  AND procedure_area IS NOT NULL
                  AND procedure_area ~ '^[0-9.]+$'
            """)
            
            value_result = pd.read_sql(value_query, engine, params={'area': area, 'property_type': property_type})
            
            if len(value_result) > 0 and not pd.isna(value_result.iloc[0]['median_price_sqm']):
                median_price_sqm = value_result.iloc[0]['median_price_sqm']
                estimated_value = median_price_sqm * size_sqm
                
                if estimated_value > 0:
                    yield_percentage = (median_rent / estimated_value) * 100
                else:
                    yield_percentage = 5.0  # Default
            else:
                yield_percentage = 5.0  # Default
        else:
            # Insufficient size-filtered data, fallback to area-wide average
            fallback_query = text("""
                SELECT AVG(annual_amount) as avg_rent, COUNT(*) as count
                FROM rentals
                WHERE UPPER(area_en) = UPPER(:area)
                  AND prop_type_en = :property_type
                  AND annual_amount > 0
                  AND CAST(registration_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
            """)
            
            fallback_result = pd.read_sql(fallback_query, engine, params={'area': area, 'property_type': property_type})
            
            if len(fallback_result) > 0 and fallback_result.iloc[0]['count'] > 0:
                avg_rent = fallback_result.iloc[0]['avg_rent']
                comparables = int(fallback_result.iloc[0]['count'])
                
                # Estimate property value
                value_query = text("""
                    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY trans_value / CAST(procedure_area AS DOUBLE PRECISION)) as median_price_sqm
                    FROM properties
                    WHERE UPPER(area_en) = UPPER(:area)
                      AND prop_type_en = :property_type
                      AND CAST(instance_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '6 months'
                      AND trans_value > 0
                      AND procedure_area IS NOT NULL
                      AND procedure_area ~ '^[0-9.]+$'
                """)
                
                value_result = pd.read_sql(value_query, engine, params={'area': area, 'property_type': property_type})
                
                if len(value_result) > 0 and not pd.isna(value_result.iloc[0]['median_price_sqm']):
                    median_price_sqm = value_result.iloc[0]['median_price_sqm']
                    estimated_value = median_price_sqm * size_sqm
                    
                    if estimated_value > 0:
                        yield_percentage = (avg_rent / estimated_value) * 100
                    else:
                        yield_percentage = 5.0
                else:
                    yield_percentage = 5.0
            else:
                # No rental data available, use default
                yield_percentage = 5.0
                comparables = 0
        
        # Score based on yield
        if yield_percentage >= 8:
            score = 100
        elif yield_percentage >= 6:
            score = 80
        elif yield_percentage >= 4:
            score = 60
        else:
            score = 30
        
        return {
            'score': score,
            'details': f'Rental yield: {yield_percentage:.1f}%',
            'comparables': comparables
        }
        
    except Exception as e:
        logging.error(f"Yield score calculation error: {str(e)}")
        return {
            'score': 50,
            'details': 'Error calculating yield',
            'comparables': 0
        }


def _calculate_segment_score(property_type: str, area: str, size_sqm: float, bedrooms: str, engine) -> dict:
    """Calculate score based on market segment"""
    import logging
    
    try:
        # Get median price per sqm for this property
        query = text("""
            SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY trans_value / CAST(procedure_area AS DOUBLE PRECISION)) as median_price_sqm
            FROM properties
            WHERE UPPER(area_en) = UPPER(:area)
              AND prop_type_en = :property_type
              AND CAST(instance_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
              AND trans_value > 0
              AND procedure_area IS NOT NULL
              AND procedure_area ~ '^[0-9.]+$'
        """)
        
        result = pd.read_sql(query, engine, params={'area': area, 'property_type': property_type})
        
        if len(result) > 0 and not pd.isna(result.iloc[0]['median_price_sqm']):
            price_per_sqm = result.iloc[0]['median_price_sqm']
            
            # Determine segment based on price per sqm thresholds (Dubai market)
            if price_per_sqm >= 40000:
                segment = 'Ultra-Luxury'
                score = 40  # Low liquidity for ultra-luxury
            elif price_per_sqm >= 20000:
                segment = 'Luxury'
                score = 60
            elif price_per_sqm >= 12000:
                segment = 'Premium'
                score = 85
            elif price_per_sqm >= 8000:
                segment = 'Mid-Tier'
                score = 100  # Best liquidity for flipping
            else:
                segment = 'Budget'
                score = 70
        else:
            segment = 'Mid-Tier'
            score = 70
        
        return {
            'score': score,
            'details': f'Market segment: {segment}'
        }
        
    except Exception as e:
        logging.error(f"Segment score calculation error: {str(e)}")
        return {
            'score': 70,
            'details': 'Error determining segment'
        }


# =============================================================================
# PROPERTY ARBITRAGE SCORE CALCULATION
# =============================================================================

def _get_market_rental_median(area: str, property_type: str, size_sqm: float, engine) -> dict:
    """Get median rental value for comparable properties"""
    import logging
    
    logging.info(f"🔍 Arbitrage: Getting rental median for {property_type} in {area} (~{size_sqm} sqm)")
    
    try:
        # Size filtering: ±30% of property size
        size_min = size_sqm * 0.7
        size_max = size_sqm * 1.3
        
        # Query with size filter for rentals
        rental_query = text("""
            SELECT annual_amount, actual_area
            FROM rentals
            WHERE UPPER(area_en) = UPPER(:area)
              AND prop_type_en = :property_type
              AND CAST(actual_area AS DOUBLE PRECISION) BETWEEN :size_min AND :size_max
              AND CAST(registration_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
              AND annual_amount > 0
        """)
        
        rental_result = pd.read_sql(
            rental_query, 
            engine, 
            params={
                'area': area, 
                'property_type': property_type,
                'size_min': size_min,
                'size_max': size_max
            }
        )
        
        comparables = len(rental_result)
        logging.info(f"📊 Arbitrage: Found {comparables} rental comparables (size {size_min:.0f}-{size_max:.0f} sqm)")
        
        # Need minimum 3 comparables
        if comparables >= 3:
            median_rent = rental_result['annual_amount'].median()
            logging.info(f"✅ Arbitrage: Rental median = {median_rent:,.0f} AED/year ({comparables} comparables)")
            return {
                'median_rent': float(median_rent),
                'comparables': comparables,
                'success': True
            }
        
        logging.warning(f"⚠️ Arbitrage: Insufficient size-filtered rentals ({comparables}), trying fallback...")
        # Fallback: area-wide average if insufficient size-filtered data
        fallback_query = text("""
            SELECT AVG(annual_amount) as avg_rent
            FROM rentals
            WHERE UPPER(area_en) = UPPER(:area)
              AND prop_type_en = :property_type
              AND CAST(registration_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
              AND annual_amount > 0
        """)
        
        fallback_result = pd.read_sql(fallback_query, engine, params={'area': area, 'property_type': property_type})
        
        if len(fallback_result) > 0 and not pd.isna(fallback_result.iloc[0]['avg_rent']):
            avg_rent = fallback_result.iloc[0]['avg_rent']
            logging.info(f"✅ Arbitrage: Using fallback rental avg = {avg_rent:,.0f} AED/year (area-wide)")
            return {
                'median_rent': float(avg_rent),
                'comparables': 0,  # Indicate fallback used
                'success': True
            }
        
        logging.error(f"❌ Arbitrage: No rental data found for {property_type} in {area}")
        return {'success': False, 'median_rent': 0, 'comparables': 0}
        
    except Exception as e:
        logging.error(f"Market rental median error: {str(e)}")
        return {'success': False, 'median_rent': 0, 'comparables': 0}


def _get_comparable_sales(area: str, property_type: str, size_sqm: float, engine) -> dict:
    """Get median sale price for comparable properties"""
    import logging
    
    logging.info(f"🔍 Arbitrage: Getting sales median for {property_type} in {area} (~{size_sqm} sqm)")
    
    try:
        # Size filtering: ±30% of property size
        size_min = size_sqm * 0.7
        size_max = size_sqm * 1.3
        
        # Query with size filter for sales
        sales_query = text("""
            SELECT trans_value, procedure_area
            FROM properties
            WHERE UPPER(area_en) = UPPER(:area)
              AND prop_type_en = :property_type
              AND CAST(procedure_area AS DOUBLE PRECISION) BETWEEN :size_min AND :size_max
              AND CAST(instance_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
              AND trans_value > 0
              AND procedure_area IS NOT NULL
              AND procedure_area ~ '^[0-9.]+$'
        """)
        
        sales_result = pd.read_sql(
            sales_query, 
            engine, 
            params={
                'area': area, 
                'property_type': property_type,
                'size_min': size_min,
                'size_max': size_max
            }
        )
        
        comparables = len(sales_result)
        logging.info(f"📊 Arbitrage: Found {comparables} sales comparables (size {size_min:.0f}-{size_max:.0f} sqm)")
        
        # Need minimum 3 comparables
        if comparables >= 3:
            median_price = sales_result['trans_value'].median()
            logging.info(f"✅ Arbitrage: Sales median = {median_price:,.0f} AED ({comparables} comparables)")
            return {
                'median_price': float(median_price),
                'comparables': comparables,
                'success': True
            }
        
        logging.warning(f"⚠️ Arbitrage: Insufficient size-filtered sales ({comparables}), trying fallback...")
        # Fallback: area-wide average if insufficient size-filtered data
        fallback_query = text("""
            SELECT AVG(trans_value) as avg_price
            FROM properties
            WHERE UPPER(area_en) = UPPER(:area)
              AND prop_type_en = :property_type
              AND CAST(instance_date AS TIMESTAMP) >= CURRENT_DATE - INTERVAL '12 months'
              AND trans_value > 0
              AND procedure_area IS NOT NULL
              AND procedure_area ~ '^[0-9.]+$'
        """)
        
        fallback_result = pd.read_sql(fallback_query, engine, params={'area': area, 'property_type': property_type})
        
        if len(fallback_result) > 0 and not pd.isna(fallback_result.iloc[0]['avg_price']):
            avg_price = fallback_result.iloc[0]['avg_price']
            logging.info(f"✅ Arbitrage: Using fallback sales avg = {avg_price:,.0f} AED (area-wide)")
            return {
                'median_price': float(avg_price),
                'comparables': 0,  # Indicate fallback used
                'success': True
            }
        
        logging.error(f"❌ Arbitrage: No sales data found for {property_type} in {area}")
        return {'success': False, 'median_price': 0, 'comparables': 0}
        
    except Exception as e:
        logging.error(f"Comparable sales error: {str(e)}")
        return {'success': False, 'median_price': 0, 'comparables': 0}


def _calculate_rental_arbitrage(asking_price: float, market_rent: float, market_value: float) -> dict:
    """Calculate rental arbitrage opportunity"""
    
    # Calculate rental yield on asking price
    if asking_price > 0:
        rental_yield = (market_rent / asking_price) * 100
    else:
        rental_yield = 0
    
    # Calculate value spread (asking vs market)
    if market_value > 0:
        value_spread_pct = ((market_value - asking_price) / market_value) * 100
    else:
        value_spread_pct = 0
    
    # Combined arbitrage potential score (0-100)
    # High rental yield = good for hold & rent
    # Positive value spread = buying below market (instant equity)
    
    yield_score = 0
    if rental_yield >= 8:
        yield_score = 50  # Excellent yield
    elif rental_yield >= 6:
        yield_score = 40
    elif rental_yield >= 4:
        yield_score = 30
    elif rental_yield >= 3:
        yield_score = 20
    else:
        yield_score = 10
    
    spread_score = 0
    if value_spread_pct >= 20:
        spread_score = 50  # Buying 20%+ below market
    elif value_spread_pct >= 10:
        spread_score = 40
    elif value_spread_pct >= 5:
        spread_score = 30
    elif value_spread_pct >= 0:
        spread_score = 20
    elif value_spread_pct >= -5:
        spread_score = 10
    else:
        spread_score = 0  # Overpriced
    
    total_score = yield_score + spread_score
    
    return {
        'arbitrage_score': total_score,
        'rental_yield': rental_yield,
        'value_spread_pct': value_spread_pct,
        'yield_score': yield_score,
        'spread_score': spread_score
    }


def _calculate_arbitrage_score(property_type: str, area: str, size_sqm: float, bedrooms: str, asking_price: float, engine) -> dict:
    """Calculate overall arbitrage opportunity score"""
    import logging
    
    try:
        # Get market rental value
        rental_data = _get_market_rental_median(area, property_type, size_sqm, engine)
        
        # Get market sale value
        sales_data = _get_comparable_sales(area, property_type, size_sqm, engine)
        
        # Check if we have sufficient data
        if not rental_data['success'] or not sales_data['success']:
            return {
                'success': False,
                'error': 'Insufficient market data for arbitrage calculation',
                'arbitrage_score': 0,
                'confidence': 'Low'
            }
        
        market_rent = rental_data['median_rent']
        market_value = sales_data['median_price']
        rental_comparables = rental_data['comparables']
        sales_comparables = sales_data['comparables']
        
        # Calculate arbitrage metrics
        arbitrage_metrics = _calculate_rental_arbitrage(asking_price, market_rent, market_value)
        
        # Determine confidence level
        total_comparables = rental_comparables + sales_comparables
        if total_comparables >= 20:
            confidence = 'High'
        elif total_comparables >= 10:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        # Build detailed breakdown
        breakdown = {
            'rental_yield': {
                'value': arbitrage_metrics['rental_yield'],
                'score': arbitrage_metrics['yield_score'],
                'market_rent': market_rent,
                'comparables': rental_comparables
            },
            'value_spread': {
                'value': arbitrage_metrics['value_spread_pct'],
                'score': arbitrage_metrics['spread_score'],
                'market_value': market_value,
                'asking_price': asking_price,
                'comparables': sales_comparables
            }
        }
        
        return {
            'success': True,
            'arbitrage_score': arbitrage_metrics['arbitrage_score'],
            'rental_yield': arbitrage_metrics['rental_yield'],
            'value_spread_pct': arbitrage_metrics['value_spread_pct'],
            'market_rent': market_rent,
            'market_value': market_value,
            'confidence': confidence,
            'breakdown': breakdown
        }
        
    except Exception as e:
        logging.error(f"Arbitrage score calculation error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'arbitrage_score': 0,
            'confidence': 'Low'
        }


@app.route('/api/arbitrage-score', methods=['POST'])
def arbitrage_score():
    """Calculate property arbitrage opportunity score"""
    import logging
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['property_type', 'area', 'size', 'asking_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        property_type = data['property_type']
        area = data['area']
        size_sqm = float(data['size'])
        bedrooms = data.get('bedrooms', 'Any')
        asking_price = float(data['asking_price'])
        
        logging.info(f"🎯 Arbitrage request: {property_type} in {area}, {size_sqm} sqm, {asking_price:,.0f} AED")
        
        # Validate inputs
        if size_sqm <= 0:
            return jsonify({'error': 'Size must be greater than 0'}), 400
        
        if asking_price <= 0:
            return jsonify({'error': 'Asking price must be greater than 0'}), 400
        
        # Calculate arbitrage score
        result = _calculate_arbitrage_score(property_type, area, size_sqm, bedrooms, asking_price, engine)
        
        if not result['success']:
            return jsonify({
                'error': result.get('error', 'Unable to calculate arbitrage score'),
                'arbitrage_score': 0,
                'confidence': 'Low'
            }), 200  # Return 200 with error info for graceful UI handling
        
        # Return successful result
        return jsonify({
            'arbitrage_score': result['arbitrage_score'],
            'rental_yield': round(result['rental_yield'], 2),
            'value_spread_pct': round(result['value_spread_pct'], 2),
            'market_rent': round(result['market_rent'], 2),
            'market_value': round(result['market_value'], 2),
            'confidence': result['confidence'],
            'breakdown': result['breakdown']
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        logging.error(f"Arbitrage score endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    if not DATABASE_URL:
        print("FATAL: DATABASE_URL is not set for local development.")
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)