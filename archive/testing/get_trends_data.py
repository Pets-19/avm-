#!/usr/bin/env python3

import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment variables")
    exit(1)

try:
    # Create database engine
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=2,
        max_overflow=5,
        pool_timeout=30,
        pool_recycle=1800,
        connect_args={'sslmode': 'require'}
    )
    
    print('📊 MARKET TRENDS DASHBOARD - SALES MARKET (6 MONTHS)')
    print('=' * 60)
    
    # Get 6 months of sales data
    six_months_ago = datetime.now() - timedelta(days=180)
    twelve_months_ago = datetime.now() - timedelta(days=365)
    
    # First, let's check what database type we're dealing with
    db_check_query = text("SELECT 1")
    
    with engine.connect() as conn:
        # Check the database schema first
        try:
            schema_query = text("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
            schema_result = conn.execute(schema_query)
            db_type = "sqlite"
            print("🔍 Detected SQLite database")
        except:
            db_type = "postgresql" 
            print("🔍 Detected PostgreSQL database")
    
    if db_type == "sqlite":
        # SQLite compatible query
        current_query = text("""
            SELECT 
                strftime('%Y-%m', instance_date) as month,
                AVG(trans_value) as avg_price,
                AVG(CASE WHEN actual_area > 0 THEN trans_value/actual_area ELSE trans_value/111.0 END) as avg_price_per_sqm,
                COUNT(*) as transaction_count,
                (AVG(trans_value * trans_value) - AVG(trans_value) * AVG(trans_value)) as price_variance,
                MIN(trans_value) as min_price,
                MAX(trans_value) as max_price,
                AVG(trans_value) as median_price
            FROM properties 
            WHERE instance_date >= :six_months_ago 
                AND trans_value > 0
                AND trans_value < 100000000
            GROUP BY strftime('%Y-%m', instance_date)
            ORDER BY month;
        """)
    else:
        # PostgreSQL query (with proper casting for text fields)
        current_query = text("""
            SELECT 
                DATE_TRUNC('month', CAST(instance_date AS timestamp)) as month,
                AVG(trans_value) as avg_price,
                AVG(CASE WHEN CAST(actual_area AS FLOAT) > 0 THEN trans_value/CAST(actual_area AS FLOAT) ELSE trans_value/111.0 END) as avg_price_per_sqm,
                COUNT(*) as transaction_count,
                STDDEV(trans_value) as price_stddev,
                MIN(trans_value) as min_price,
                MAX(trans_value) as max_price,
                PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY trans_value) as median_price
            FROM properties 
            WHERE CAST(instance_date AS timestamp) >= :six_months_ago 
                AND trans_value > 0
                AND trans_value < 100000000
                AND actual_area IS NOT NULL
                AND actual_area != ''
            GROUP BY DATE_TRUNC('month', CAST(instance_date AS timestamp))
            ORDER BY month;
        """)
    
    if db_type == "sqlite":
        # SQLite compatible query
        previous_query = text("""
            SELECT 
                AVG(trans_value) as avg_price,
                AVG(CASE WHEN actual_area > 0 THEN trans_value/actual_area ELSE trans_value/111.0 END) as avg_price_per_sqm,
                COUNT(*) as transaction_count
            FROM properties 
            WHERE instance_date >= :twelve_months_ago AND instance_date < :six_months_ago
                AND trans_value > 0
                AND trans_value < 100000000;
        """)
    else:
        # PostgreSQL query
        previous_query = text("""
            SELECT 
                AVG(trans_value) as avg_price,
                AVG(CASE WHEN CAST(actual_area AS FLOAT) > 0 THEN trans_value/CAST(actual_area AS FLOAT) ELSE trans_value/111.0 END) as avg_price_per_sqm,
                COUNT(*) as transaction_count
            FROM properties 
            WHERE CAST(instance_date AS timestamp) >= :twelve_months_ago AND CAST(instance_date AS timestamp) < :six_months_ago
                AND trans_value > 0
                AND trans_value < 100000000
                AND actual_area IS NOT NULL
                AND actual_area != '';
        """)
    
    with engine.connect() as conn:
        # Get current 6 months data
        current_result = conn.execute(current_query, {"six_months_ago": six_months_ago})
        current_data = current_result.fetchall()
        
        if current_data and len(current_data) > 0:
            # Convert to DataFrame for easier processing
            df_current = pd.DataFrame(current_data, columns=[
                'month', 'avg_price', 'avg_price_per_sqm', 'transaction_count', 
                'price_stddev', 'min_price', 'max_price', 'median_price'
            ])
            
            # Calculate aggregated metrics
            total_transactions = df_current['transaction_count'].sum()
            overall_avg_price = df_current['avg_price'].mean()
            overall_avg_price_per_sqm = df_current['avg_price_per_sqm'].mean()
            overall_median_price = df_current['median_price'].mean()
            overall_min_price = df_current['min_price'].min()
            overall_max_price = df_current['max_price'].max()
            
            # Get previous 6 months for comparison
            prev_result = conn.execute(previous_query, {
                "twelve_months_ago": twelve_months_ago,
                "six_months_ago": six_months_ago
            })
            prev_data = prev_result.fetchone()
            
            # Calculate changes
            if prev_data and prev_data[0]:
                prev_avg_price = float(prev_data[0])
                prev_avg_price_per_sqm = float(prev_data[1])
                prev_transaction_count = int(prev_data[2])
                
                price_change = ((overall_avg_price - prev_avg_price) / prev_avg_price) * 100
                price_per_sqm_change = ((overall_avg_price_per_sqm - prev_avg_price_per_sqm) / prev_avg_price_per_sqm) * 100
                volume_change = ((total_transactions - prev_transaction_count) / prev_transaction_count) * 100
            else:
                price_change = 0
                price_per_sqm_change = 0
                volume_change = 0
                prev_avg_price = overall_avg_price
                prev_avg_price_per_sqm = overall_avg_price_per_sqm
                prev_transaction_count = total_transactions
            
            # Calculate volatility (coefficient of variation)
            monthly_prices = df_current['avg_price'].values
            if len(monthly_prices) > 1:
                volatility = np.std(monthly_prices) / np.mean(monthly_prices)
                stability = max(0, (1 - volatility) * 100)
            else:
                volatility = 0
                stability = 100
            
            # Calculate momentum (trend from first to last month)
            if len(monthly_prices) >= 2:
                momentum = ((monthly_prices[-1] - monthly_prices[0]) / monthly_prices[0]) * 100
            else:
                momentum = 0
            
            # Market condition assessment
            if price_change > 5:
                market_condition = 'Bullish'
            elif price_change < -5:
                market_condition = 'Bearish'
            else:
                market_condition = 'Stable'
            
            # Market activity assessment
            avg_monthly_volume = total_transactions // max(len(current_data), 1)
            if avg_monthly_volume > 1000:
                market_activity = 'High'
            elif avg_monthly_volume > 500:
                market_activity = 'Medium'
            else:
                market_activity = 'Low'
            
            # Affordability index (assuming Dubai median household income of AED 180,000/year)
            affordability_index = overall_avg_price / 180000
            
            # Quarter analysis (last 3 months vs previous 3 months in the 6-month period)
            if len(df_current) >= 3:
                recent_3_months = df_current.tail(3)['avg_price'].mean()
                earlier_3_months = df_current.head(3)['avg_price'].mean()
                qoq_change = ((recent_3_months - earlier_3_months) / earlier_3_months) * 100
            else:
                qoq_change = price_change
            
            # Seasonal pattern analysis
            if momentum > 2:
                seasonal_pattern = 'Upward trend'
            elif momentum < -2:
                seasonal_pattern = 'Downward trend'
            else:
                seasonal_pattern = 'Sideways movement'
            
            # Display results
            print('🏠 MARKET TREND ANALYSIS')
            print(f'Market Condition: {market_condition}')
            print(f'Price Change: {price_change:+.1f}%')
            print(f'Avg Monthly Volume: {avg_monthly_volume:,} transactions')
            print()
            
            print('📈 ADVANCED ANALYTICS')
            print(f'Quarter-over-Quarter: {qoq_change:+.1f}%')
            print(f'Year-over-Year: N/A (insufficient historical data)')
            print(f'Price Stability: {stability:.1f}%')
            print(f'Market Activity: {market_activity}')
            print()
            
            print('📊 ENHANCED ANALYTICS')
            print(f'Avg Monthly Price: AED {overall_avg_price:,.0f}')
            print(f'Price Momentum: {momentum:+.1f}%')
            print(f'Affordability Index: {affordability_index:.1f}x')
            print(f'Avg Price/SqM: AED {overall_avg_price_per_sqm:,.0f}/sqm')
            print(f'Seasonal Pattern: {seasonal_pattern}')
            print(f'Data Points: {len(current_data)} months, {total_transactions:,} transactions')
            print()
            
            print('📋 DETAILED BREAKDOWN:')
            print(f'• Total Transactions (6 months): {total_transactions:,}')
            print(f'• Average Transaction Price: AED {overall_avg_price:,.0f}')
            print(f'• Median Transaction Price: AED {overall_median_price:,.0f}')
            print(f'• Price Range: AED {overall_min_price:,.0f} - AED {overall_max_price:,.0f}')
            print(f'• Price/SqM Change: {price_per_sqm_change:+.1f}%')
            print(f'• Transaction Volume Change: {volume_change:+.1f}%')
            print(f'• Market Volatility: {volatility:.3f} ({(volatility*100):.1f}%)')
            print(f'• Previous Period Avg Price: AED {prev_avg_price:,.0f}')
            print(f'• Previous Period Avg Price/SqM: AED {prev_avg_price_per_sqm:,.0f}/sqm')
            print(f'• Previous Period Volume: {prev_transaction_count:,} transactions')
            
            print('\n📅 MONTHLY BREAKDOWN:')
            for _, row in df_current.iterrows():
                month_str = row['month'].strftime('%Y-%m') if hasattr(row['month'], 'strftime') else str(row['month'])[:7]
                print(f'• {month_str}: {int(row["transaction_count"]):,} transactions, AED {row["avg_price"]:,.0f} avg, AED {row["avg_price_per_sqm"]:,.0f}/sqm')
            
        else:
            print('❌ No sales data found for the specified period')
            
            # Let's check what data is available
            check_query = text("SELECT COUNT(*), MIN(instance_date), MAX(instance_date) FROM properties WHERE trans_value > 0")
            check_result = conn.execute(check_query)
            check_data = check_result.fetchone()
            
            if check_data and check_data[0] > 0:
                print(f'📋 Available data: {check_data[0]:,} total transactions')
                print(f'📅 Date range: {check_data[1]} to {check_data[2]}')
            else:
                print('❌ No transaction data found in database')

except Exception as e:
    print(f"❌ Database connection error: {e}")
    import traceback
    traceback.print_exc()