#!/usr/bin/env python3
"""
Extract 3-month Market Trend Analysis numbers for verification
Sales Market, Time Period: 3 Months
"""
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import pandas as pd

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL not found in environment")
    sys.exit(1)

engine = create_engine(DATABASE_URL, echo=False)

def extract_3_month_data():
    """Extract raw data for 3-month analysis"""
    
    print("🔍 EXTRACTING 3-MONTH DATA FOR VERIFICATION")
    print("=" * 60)
    print("Market Type: Sales Market")
    print("Time Period: 3 Months")
    print("Filters: All property types, all areas, no budget limit")
    print("-" * 60)
    
    # Query for 3-month data (same as system uses)
    query = text("""
        SELECT 
            DATE_TRUNC('month', CAST("instance_date" AS DATE)) as month,
            AVG("trans_value") as avg_price,
            COUNT(*) as transaction_count,
            MIN("trans_value") as min_price,
            MAX("trans_value") as max_price
        FROM properties
        WHERE "trans_value" >= 100000 
        AND "trans_value" <= 50000000 
        AND "trans_value" <= 999999999
        AND "instance_date" IS NOT NULL
        AND "instance_date" != ''
        AND CAST("instance_date" AS DATE) >= NOW() - INTERVAL '3 months'
        GROUP BY DATE_TRUNC('month', CAST("instance_date" AS DATE))
        ORDER BY month;
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(query)
            data_points = []
            
            for row in result:
                data_points.append({
                    'month': row[0].strftime('%Y-%m') if row[0] else None,
                    'avg_price': float(row[1]) if row[1] else 0,
                    'transaction_count': int(row[2]) if row[2] else 0,
                    'min_price': float(row[3]) if row[3] else 0,
                    'max_price': float(row[4]) if row[4] else 0
                })
            
            return data_points
            
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        return []

def calculate_3_month_metrics(trend_data):
    """Calculate all metrics exactly as the system does"""
    
    if not trend_data or len(trend_data) < 2:
        return {
            'error': 'Insufficient data for 3-month analysis',
            'data_points': len(trend_data) if trend_data else 0
        }
    
    # Extract arrays
    prices = [point['avg_price'] for point in trend_data if point['avg_price'] > 0]
    volumes = [point['transaction_count'] for point in trend_data]
    
    print(f"📊 RAW DATA POINTS:")
    print("-" * 30)
    for i, point in enumerate(trend_data):
        print(f"   {point['month']}: AED {point['avg_price']:,.0f} ({point['transaction_count']:,} transactions)")
    
    # === 1. PRICE CHANGE ===
    first_price = prices[0]
    last_price = prices[-1]
    percentage_change = ((last_price - first_price) / first_price) * 100
    
    # === 2. TREND DIRECTION ===
    if percentage_change > 5:
        trend_direction = 'upward'
        trend_strength = 'strong' if percentage_change > 15 else 'moderate'
    elif percentage_change < -5:
        trend_direction = 'downward'
        trend_strength = 'strong' if percentage_change < -15 else 'moderate'
    else:
        trend_direction = 'stable'
        trend_strength = 'stable'
    
    # === 3. AVERAGE MONTHLY VOLUME ===
    avg_volume = sum(volumes) / len(volumes)
    
    # === 4. QUARTER-OVER-QUARTER (with 3 months, we compare all available data) ===
    qoq_change = 0
    qoq_status = 'N/A'
    if len(prices) >= 2:
        # With only 3 months, compare recent vs earliest
        if len(prices) >= 3:
            recent_avg = prices[-2:] if len(prices) == 3 else [prices[-1]]
            earlier_avg = prices[:2] if len(prices) == 3 else [prices[0]]
        else:
            recent_avg = [prices[-1]]
            earlier_avg = [prices[0]]
        
        if earlier_avg:
            recent_val = sum(recent_avg) / len(recent_avg)
            earlier_val = sum(earlier_avg) / len(earlier_avg)
            qoq_change = ((recent_val - earlier_val) / earlier_val) * 100
            qoq_status = 'Growth' if qoq_change > 0 else 'Decline' if qoq_change < 0 else 'Flat'
    
    # === 5. YEAR-OVER-YEAR (will use period comparison) ===
    yoy_change = percentage_change  # For 3 months, YoY becomes period change
    yoy_status = 'Period Growth' if yoy_change > 0 else 'Period Decline' if yoy_change < 0 else 'Stable'
    
    # === 6. VOLATILITY ===
    volatility = 0
    volatility_index = 'Low'
    price_std = 0
    
    if len(prices) > 1:
        # Month-over-month changes
        price_changes = [(prices[i] - prices[i-1]) / prices[i-1] * 100 for i in range(1, len(prices))]
        volatility = pd.Series(price_changes).std() if price_changes else 0
        price_std = pd.Series(prices).std()
        
        if volatility > 10:
            volatility_index = 'High'
        elif volatility > 5:
            volatility_index = 'Moderate'
        else:
            volatility_index = 'Low'
    
    # === 7. VOLUME METRICS ===
    volume_change = 0
    volume_growth_rate = 0
    volume_trend = 'Stable'
    
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
        
        # Monthly growth rate
        if len(volumes) > 1:
            volume_changes = [(volumes[i] - volumes[i-1]) / max(volumes[i-1], 1) * 100 for i in range(1, len(volumes))]
            volume_growth_rate = sum(volume_changes) / len(volume_changes) if volume_changes else 0
    
    # === 8. SEASONAL PATTERN ===
    seasonal_pattern = 'No Pattern'
    if len(trend_data) >= 2:
        monthly_volumes = {}
        for point in trend_data:
            month_num = datetime.strptime(point['month'], '%Y-%m').month
            if month_num not in monthly_volumes:
                monthly_volumes[month_num] = []
            monthly_volumes[month_num].append(point['transaction_count'])
        
        if len(monthly_volumes) >= 2:
            avg_by_month = {k: sum(v)/len(v) for k, v in monthly_volumes.items()}
            max_month = max(avg_by_month, key=avg_by_month.get)
            min_month = min(avg_by_month, key=avg_by_month.get)
            seasonal_variation = (avg_by_month[max_month] - avg_by_month[min_month]) / avg_by_month[min_month] * 100
            
            if seasonal_variation > 30:
                seasonal_pattern = f'Seasonal (Peak: Month {max_month})'
    
    # === 9. SUMMARY GENERATION ===
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
    
    return {
        # Basic metrics  
        'trend_direction': trend_direction,
        'percentage_change': round(percentage_change, 2),
        'trend_strength': trend_strength,
        'avg_monthly_volume': round(avg_volume),
        'data_points': len(trend_data),
        
        # Advanced analytics
        'qoq_change': round(qoq_change, 2),
        'qoq_status': qoq_status,
        'yoy_change': round(yoy_change, 2), 
        'yoy_status': yoy_status,
        'volatility': round(volatility, 2),
        'volatility_index': volatility_index,
        'price_std': round(price_std, 2),
        'volume_trend': volume_trend,
        'volume_change': round(volume_change, 2),
        'volume_growth_rate': round(volume_growth_rate, 2),
        'seasonal_pattern': seasonal_pattern,
        'summary': summary,
        
        # Raw data for verification
        'raw_prices': prices,
        'raw_volumes': volumes,
        'raw_data': trend_data
    }

def main():
    print("🚀 STARTING 3-MONTH VERIFICATION EXTRACTION")
    print("=" * 60)
    
    # Extract data
    trend_data = extract_3_month_data()
    
    if not trend_data:
        print("❌ No data retrieved from database")
        return
    
    print(f"\n✅ Retrieved {len(trend_data)} data points")
    
    # Calculate metrics
    metrics = calculate_3_month_metrics(trend_data)
    
    if 'error' in metrics:
        print(f"❌ Calculation error: {metrics['error']}")
        return
    
    print(f"\n📊 3-MONTH MARKET TREND ANALYSIS RESULTS")
    print("=" * 60)
    
    # Display results in the same format as your system
    print("\n🏷️  BASIC METRICS:")
    print("-" * 30)
    print(f"   Trend Direction: {metrics['trend_direction'].upper()}")
    print(f"   Price Change: {metrics['percentage_change']:+.2f}%")
    print(f"   Market Status: {metrics['trend_strength'].upper()}")
    print(f"   Avg Monthly Volume: {metrics['avg_monthly_volume']:,} transactions")
    
    print(f"\n📈 ADVANCED ANALYTICS:")
    print("-" * 30)
    print(f"   Quarter-over-Quarter: {metrics['qoq_status']} ({metrics['qoq_change']:+.2f}%)")
    print(f"   Year-over-Year: {metrics['yoy_status']} ({metrics['yoy_change']:+.2f}%)")
    print(f"   Price Volatility: {metrics['volatility_index']} ({metrics['volatility']:.2f}%)")
    print(f"   Market Stability: ±AED {metrics['price_std']/1000:.2f}K")
    print(f"   Volume Trend: {metrics['volume_trend']} ({metrics['volume_change']:+.2f}%)")
    print(f"   Growth Rate: {metrics['volume_growth_rate']:+.2f}% monthly")
    print(f"   Seasonal Pattern: {metrics['seasonal_pattern']}")
    print(f"   Data Points: {metrics['data_points']}")
    
    print(f"\n📝 GENERATED SUMMARY:")
    print("-" * 30)
    print(f"   {metrics['summary']}")
    
    print(f"\n🔍 VERIFICATION DATA:")
    print("-" * 30)
    print("   Raw Prices:", [f"AED {p:,.0f}" for p in metrics['raw_prices']])
    print("   Raw Volumes:", [f"{v:,}" for v in metrics['raw_volumes']])
    
    print(f"\n✅ VERIFICATION COMPLETE")
    print("=" * 60)
    print("Compare these numbers with your system output for 3-month period")
    print("All calculations use the exact same methodology as the production system")

if __name__ == "__main__":
    main()