# Technical Implementation - Market Trend Analysis Code

## Core Implementation Files

### 1. Backend API Endpoint (`app.py`)

```python
@app.route('/api/trends/price-timeline', methods=['POST'])
@login_required
def get_trends_timeline():
    """Main API endpoint for market trend analysis"""
    
    filters = request.json
    search_type = filters.get('search_type', 'buy')
    time_period = filters.get('time_period', '6M')
    
    # Extract time-series data
    trend_data = get_price_trends(filters, search_type, time_period)
    
    if not trend_data:
        return jsonify({
            'status': 'error',
            'timeline': [],
            'summary': {'summary': 'No data available for the selected criteria.'}
        })
    
    # Calculate comprehensive metrics
    summary = calculate_basic_trends(trend_data)
    
    return jsonify({
        'status': 'success',
        'timeline': trend_data,
        'summary': summary,
        'search_type': search_type,
        'time_period': time_period
    })
```

### 2. Data Extraction Function

```python
def get_price_trends(filters, search_type, time_period='6M'):
    """Extract time-series price data from database"""
    
    # Convert time period to months
    period_months = {'3M': 3, '6M': 6, '1Y': 12}.get(time_period, 6)
    
    # Determine table and columns
    table = 'properties' if search_type == 'buy' else 'rentals'
    date_col = 'instance_date' if search_type == 'buy' else 'registration_date'
    map_config = SALES_MAP if search_type == 'buy' else RENTALS_MAP
    price_col = map_config['price']
    
    # SQL Query for monthly aggregation
    query = text(f"""
        SELECT 
            DATE_TRUNC('month', CAST("{date_col}" AS DATE)) as month,
            AVG("{price_col}") as avg_price,
            COUNT(*) as transaction_count,
            MIN("{price_col}") as min_price,
            MAX("{price_col}") as max_price
        FROM {table}
        WHERE {where_clause}
        AND "{date_col}" IS NOT NULL
        AND "{date_col}" != ''
        AND CAST("{date_col}" AS DATE) >= NOW() - INTERVAL '{period_months} months'
        GROUP BY DATE_TRUNC('month', CAST("{date_col" AS DATE))
        ORDER BY month;
    """)
    
    # Execute and return formatted data
    with engine.connect() as conn:
        result = conn.execute(query, params)
        return [format_trend_data_point(row) for row in result]
```

### 3. Main Calculation Function

```python
def calculate_basic_trends(trend_data):
    """Calculate all trend metrics"""
    
    if not trend_data or len(trend_data) < 2:
        return insufficient_data_response()
    
    # Extract price and volume arrays
    prices = [point['avg_price'] for point in trend_data if point['avg_price'] > 0]
    volumes = [point['transaction_count'] for point in trend_data]
    
    # === BASIC TREND ANALYSIS ===
    first_price, last_price = prices[0], prices[-1]
    percentage_change = ((last_price - first_price) / first_price) * 100
    trend_direction = classify_trend_direction(percentage_change)
    trend_strength = classify_trend_strength(percentage_change, trend_direction)
    
    # === QUARTER-OVER-QUARTER ANALYSIS ===
    qoq_change, qoq_status = calculate_qoq_analysis(prices)
    
    # === YEAR-OVER-YEAR ANALYSIS ===
    yoy_change, yoy_status = calculate_yoy_analysis(trend_data, prices)
    
    # === VOLATILITY ANALYSIS ===
    volatility, volatility_index, price_std = calculate_volatility_metrics(prices)
    
    # === VOLUME ANALYSIS ===
    volume_metrics = calculate_volume_metrics(volumes)
    
    # === SEASONAL ANALYSIS ===
    seasonal_pattern = detect_seasonal_patterns(trend_data)
    
    # === SUMMARY GENERATION ===
    summary = generate_trend_summary(
        trend_direction, percentage_change, trend_strength,
        volatility, volatility_index, volume_metrics,
        qoq_change, qoq_status, yoy_change, yoy_status
    )
    
    return compile_results(locals())
```

### 4. Individual Calculation Functions

```python
def classify_trend_direction(percentage_change):
    """Classify market trend direction"""
    if percentage_change > 5:
        return 'upward'
    elif percentage_change < -5:
        return 'downward'
    else:
        return 'stable'

def calculate_qoq_analysis(prices):
    """Quarter-over-Quarter analysis"""
    if len(prices) < 3:
        return 0, 'N/A'
    
    # Split into quarters
    if len(prices) >= 6:
        recent_quarter = prices[-3:]
        previous_quarter = prices[-6:-3]
    else:
        mid_point = len(prices) // 2
        recent_quarter = prices[mid_point:]
        previous_quarter = prices[:mid_point]
    
    if not previous_quarter:
        return 0, 'N/A'
    
    recent_avg = sum(recent_quarter) / len(recent_quarter)
    previous_avg = sum(previous_quarter) / len(previous_quarter)
    qoq_change = ((recent_avg - previous_avg) / previous_avg) * 100
    qoq_status = 'Growth' if qoq_change > 0 else 'Decline' if qoq_change < 0 else 'Flat'
    
    return round(qoq_change, 2), qoq_status

def calculate_yoy_analysis(trend_data, prices):
    """Year-over-Year analysis with fallback"""
    if len(trend_data) >= 12:
        # True YoY: same month last year
        current_month = datetime.strptime(trend_data[-1]['month'], '%Y-%m')
        year_ago_data = [
            point for point in trend_data 
            if datetime.strptime(point['month'], '%Y-%m').month == current_month.month
            and datetime.strptime(point['month'], '%Y-%m').year == current_month.year - 1
        ]
        
        if year_ago_data:
            year_ago_price = year_ago_data[0]['avg_price']
            yoy_change = ((prices[-1] - year_ago_price) / year_ago_price) * 100
            yoy_status = 'Growth' if yoy_change > 0 else 'Decline'
            return round(yoy_change, 2), yoy_status
    
    # Fallback: period comparison
    if len(prices) >= 6:
        recent_avg = sum(prices[-3:]) / len(prices[-3:])
        earliest_avg = sum(prices[:3]) / len(prices[:3])
        yoy_change = ((recent_avg - earliest_avg) / earliest_avg) * 100
        yoy_status = 'Period Growth' if yoy_change > 0 else 'Period Decline'
        return round(yoy_change, 2), yoy_status
    
    return 0, 'N/A'

def calculate_volatility_metrics(prices):
    """Calculate price volatility and stability"""
    if len(prices) <= 2:
        return 0, 'Low', 0
    
    # Month-over-month percentage changes
    price_changes = [
        (prices[i] - prices[i-1]) / prices[i-1] * 100 
        for i in range(1, len(prices))
    ]
    
    # Standard deviation of changes (volatility)
    volatility = pd.Series(price_changes).std() if price_changes else 0
    
    # Price standard deviation (stability measure)
    price_std = pd.Series(prices).std()
    
    # Classify volatility
    if volatility > 10:
        volatility_index = 'High'
    elif volatility > 5:
        volatility_index = 'Moderate'
    else:
        volatility_index = 'Low'
    
    return round(volatility, 2), volatility_index, round(price_std, 2)

def calculate_volume_metrics(volumes):
    """Calculate transaction volume trends"""
    if len(volumes) < 2:
        return {
            'volume_trend': 'Stable',
            'volume_change': 0,
            'volume_growth_rate': 0
        }
    
    # Overall volume change
    first_volume = volumes[0] if volumes[0] > 0 else 1
    last_volume = volumes[-1] if volumes[-1] > 0 else 1
    volume_change = ((last_volume - first_volume) / first_volume) * 100
    
    # Classify trend
    if volume_change > 10:
        volume_trend = 'Increasing'
    elif volume_change < -10:
        volume_trend = 'Decreasing'
    else:
        volume_trend = 'Stable'
    
    # Monthly growth rate
    volume_changes = [
        (volumes[i] - volumes[i-1]) / max(volumes[i-1], 1) * 100 
        for i in range(1, len(volumes))
    ]
    volume_growth_rate = sum(volume_changes) / len(volume_changes) if volume_changes else 0
    
    return {
        'volume_trend': volume_trend,
        'volume_change': round(volume_change, 2),
        'volume_growth_rate': round(volume_growth_rate, 2)
    }

def detect_seasonal_patterns(trend_data):
    """Detect seasonal patterns in transaction data"""
    if len(trend_data) < 6:
        return 'No Pattern'
    
    # Group by month number
    monthly_volumes = {}
    for point in trend_data:
        month_num = datetime.strptime(point['month'], '%Y-%m').month
        if month_num not in monthly_volumes:
            monthly_volumes[month_num] = []
        monthly_volumes[month_num].append(point['transaction_count'])
    
    if len(monthly_volumes) < 3:
        return 'No Pattern'
    
    # Calculate averages and find peak
    avg_by_month = {k: sum(v)/len(v) for k, v in monthly_volumes.items()}
    max_month = max(avg_by_month, key=avg_by_month.get)
    min_month = min(avg_by_month, key=avg_by_month.get)
    
    # Check if variation is significant
    seasonal_variation = (
        (avg_by_month[max_month] - avg_by_month[min_month]) / 
        avg_by_month[min_month] * 100
    )
    
    if seasonal_variation > 30:
        return f'Seasonal (Peak: Month {max_month})'
    else:
        return 'No Pattern'

def generate_trend_summary(trend_direction, percentage_change, trend_strength,
                          volatility, volatility_index, volume_metrics,
                          qoq_change, qoq_status, yoy_change, yoy_status):
    """Generate human-readable summary"""
    
    # Direction description
    direction_text = {
        'upward': f'rising by {percentage_change:.1f}%',
        'downward': f'declining by {abs(percentage_change):.1f}%',
        'stable': f'stable with {abs(percentage_change):.1f}% variation'
    }.get(trend_direction, 'unclear trend')
    
    # Build summary parts
    summary_parts = [
        f"Market is {direction_text} over the period with {trend_strength} momentum.",
        f"Volatility is {volatility_index.lower()} ({volatility:.1f}%).",
        f"Transaction volume is {volume_metrics['volume_trend'].lower()}."
    ]
    
    # Add QoQ if available
    if qoq_status != 'N/A':
        summary_parts.append(f"Quarter-over-quarter: {qoq_status} ({qoq_change:+.1f}%).")
    
    # Add YoY if available
    if yoy_status != 'N/A':
        summary_parts.append(f"Year-over-year: {yoy_status} ({yoy_change:+.1f}%).")
    
    return " ".join(summary_parts)
```

## Frontend Implementation (`templates/index.html`)

### JavaScript Functions

```javascript
// Load trend data from API
function loadTrendData() {
    const filters = {
        search_type: document.getElementById('trend-search-type').value,
        time_period: document.getElementById('trend-period').value,
        propertyType: document.getElementById('trend-property-type').value,
        area: document.getElementById('trend-area-search').value,
        budget: parseInt(document.getElementById('trend-budget').value) || 999999999
    };
    
    fetch('/api/trends/price-timeline', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(filters)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            renderTrendChart(data.timeline, filters.search_type);
            updateTrendSummary(data.summary);
            updatePriceTrendIndicators(data.timeline);
        }
    });
}

// Update trend indicators UI
function updatePriceTrendIndicators(trendData) {
    const TREND_THRESHOLDS = {
        ARROW_CHANGE: 2,
        STRONG_GROWTH: 5,
        STRONG_DECLINE: -5,
        MIN_PRICE: 1000
    };
    
    const indicatorsSection = document.getElementById('price-trend-indicators');
    
    if (!trendData || trendData.length < 2) {
        indicatorsSection.style.display = 'none';
        return;
    }
    
    const latest = trendData[trendData.length - 1];
    const previous = trendData[trendData.length - 2];
    
    const changePercent = previous.avg_price > TREND_THRESHOLDS.MIN_PRICE 
        ? ((latest.avg_price - previous.avg_price) / previous.avg_price * 100)
        : 0;
    
    const arrow = changePercent > TREND_THRESHOLDS.ARROW_CHANGE ? '↗️' : 
                 changePercent < -TREND_THRESHOLDS.ARROW_CHANGE ? '↘️' : '→';
    const trendClass = changePercent > 0 ? 'trend-up' : 
                      changePercent < 0 ? 'trend-down' : 'trend-stable';
    const signalText = changePercent > TREND_THRESHOLDS.STRONG_GROWTH ? 'Strong Growth' : 
                      changePercent < TREND_THRESHOLDS.STRONG_DECLINE ? 'Declining' : 'Stable';
    
    // Update UI with calculated values
    indicatorsSection.innerHTML = `
        <h4>📈 Price Trend Analysis</h4>
        <div class="trend-indicators-grid">
            <div class="trend-card">
                <span class="trend-label">Current Trend</span>
                <div class="trend-value">
                    <span class="${trendClass}">${arrow}</span>
                    <span class="${trendClass}">${Math.abs(changePercent).toFixed(1)}%</span>
                </div>
            </div>
            <div class="trend-card">
                <span class="trend-label">Market Signal</span>
                <span class="market-signal ${trendClass}">${signalText}</span>
            </div>
        </div>
    `;
    indicatorsSection.style.display = 'block';
}
```

## Database Schema

### Tables Used
```sql
-- Sales data
CREATE TABLE properties (
    instance_date DATE,
    trans_value DECIMAL(15,2),
    area_en VARCHAR(255),
    prop_type_en VARCHAR(100),
    -- ... other columns
);

-- Rental data  
CREATE TABLE rentals (
    registration_date DATE,
    annual_amount DECIMAL(15,2),
    area_en VARCHAR(255),
    prop_type_en VARCHAR(100),
    -- ... other columns
);
```

### Key Indexes
```sql
CREATE INDEX idx_properties_date ON properties(instance_date);
CREATE INDEX idx_properties_price ON properties(trans_value);
CREATE INDEX idx_rentals_date ON rentals(registration_date);
CREATE INDEX idx_rentals_price ON rentals(annual_amount);
```

This comprehensive implementation ensures accurate, reliable calculations for all your Market Trend Analysis metrics!