# 🎯 PROPERTY FLIP SCORE IMPLEMENTATION PROMPT

**Feature:** Property Flip Score Calculator  
**Priority:** Quick Win (Week 1 launch)  
**Development Time:** 1-2 days  
**Approach:** Formula-based scoring (Approach #1)

---

## 📋 PROMPT FOR AI ASSISTANT (COPY THIS)

```
I need to implement a "Property Flip Score" feature for the AVM (Automated Valuation Model) application. This is a quick win feature that leverages existing data to calculate a 1-100 score indicating how good a property is for flipping (buying and reselling within 12-24 months).

---

## CONTEXT

**Current System:**
- Flask application with PostgreSQL database (Neon cloud)
- Main file: `/workspaces/avm-retyn/app.py`
- Database tables: `properties` (153K+ transactions), `rentals`, `amenities`, `project_premiums`
- Existing features: Property valuation, rental yield calculator, market segment classification
- ML model: XGBoost (R²=0.897)
- Testing: pytest with >90% coverage target

**Existing Functions to Leverage:**
1. `calculate_valuation_from_database()` - Main valuation function
2. Rental yield calculator - Already implemented
3. Market segment classification - Just implemented (5 tiers)
4. Database queries for price trends

---

## REQUIREMENT

**Feature Name:** Property Flip Score

**User Story:**
"As a property investor, I want to know how good a property is for flipping (short-term buy-sell), so I can identify high-profit opportunities quickly."

**Input:**
- Property type (Apartment, Villa, Townhouse)
- Area/Location (e.g., "Dubai Marina", "Palm Jumeirah")
- Size in sqm
- Number of bedrooms

**Output:**
```json
{
  "flip_score": 78,
  "rating": "High Potential",
  "breakdown": {
    "price_appreciation": {"score": 85, "weight": 35, "contribution": 29.75},
    "liquidity": {"score": 70, "weight": 25, "contribution": 17.5},
    "rental_yield": {"score": 80, "weight": 25, "contribution": 20},
    "market_position": {"score": 75, "weight": 15, "contribution": 11.25}
  },
  "recommendation": "This property shows strong flip potential with consistent price appreciation and good liquidity.",
  "confidence": "High",
  "data_quality": {
    "transactions_analyzed": 45,
    "rental_comparables": 12,
    "date_range": "2023-10-12 to 2024-10-12"
  }
}
```

---

## SCORING FORMULA

### Final Score Calculation:
```
flip_score = (appreciation_score × 0.35) + 
             (liquidity_score × 0.25) + 
             (yield_score × 0.25) + 
             (segment_score × 0.15)
```

### Component 1: Price Appreciation Score (35% weight)
Calculate QoQ (Quarter-over-Quarter) growth rate for the area:
```python
# Query properties table for last 4 quarters
# Calculate: ((Q4_avg_price - Q1_avg_price) / Q1_avg_price) * 100

Scoring:
- QoQ growth ≥5%: 100 points
- QoQ growth 2-5%: 70 points
- QoQ growth 0-2%: 40 points
- QoQ growth <0% (decline): 20 points
```

**SQL Query Example:**
```sql
SELECT 
  EXTRACT(QUARTER FROM transaction_date) as quarter,
  AVG(price_per_sqm) as avg_price
FROM properties
WHERE area_en = %s 
  AND property_type_en = %s
  AND transaction_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY quarter
ORDER BY quarter DESC
LIMIT 4;
```

### Component 2: Liquidity Score (25% weight)
Count transactions in the area over last 12 months:
```python
Scoring:
- ≥50 transactions/year: 100 points
- 20-49 transactions: 70 points
- 5-19 transactions: 40 points
- <5 transactions: 20 points
```

**SQL Query Example:**
```sql
SELECT COUNT(*) as transaction_count
FROM properties
WHERE area_en = %s 
  AND property_type_en = %s
  AND transaction_date >= CURRENT_DATE - INTERVAL '12 months';
```

### Component 3: Rental Yield Score (25% weight)
Use existing rental yield calculator, then score:
```python
Scoring:
- Yield ≥8%: 100 points
- Yield 6-8%: 80 points
- Yield 4-6%: 60 points
- Yield <4%: 30 points
```

### Component 4: Market Segment Score (15% weight)
Use existing segment classification (Budget, Mid-Tier, Premium, Luxury, Ultra-Luxury):
```python
Scoring:
- Mid-Tier: 100 (highest liquidity for flipping)
- Premium: 85
- Budget: 70
- Luxury: 60
- Ultra-Luxury: 40 (lowest liquidity)
```

---

## IMPLEMENTATION DETAILS

### File 1: `/workspaces/avm-retyn/app.py`

**Add new route after existing valuation routes (~line 400):**
```python
@app.route('/api/flip-score', methods=['POST'])
def flip_score():
    """Calculate property flip potential score"""
    try:
        # Extract parameters
        data = request.get_json()
        property_type = data.get('property_type')
        area = data.get('area')
        size_sqm = float(data.get('size_sqm'))
        bedrooms = data.get('bedrooms')
        
        # Validate inputs
        if not all([property_type, area, size_sqm]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Calculate flip score
        result = calculate_flip_score(property_type, area, size_sqm, bedrooms, engine)
        
        return jsonify(result), 200
        
    except Exception as e:
        logging.error(f"Flip score calculation error: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

**Add main calculation function:**
```python
def calculate_flip_score(property_type, area, size_sqm, bedrooms, engine):
    """
    Calculate property flip potential score (1-100)
    
    Args:
        property_type: Type of property (Apartment, Villa, Townhouse)
        area: Area name in English
        size_sqm: Property size in square meters
        bedrooms: Number of bedrooms (optional)
        engine: SQLAlchemy database engine
        
    Returns:
        dict: Flip score with breakdown and recommendations
    """
    # Initialize result structure
    result = {
        'flip_score': 0,
        'rating': '',
        'breakdown': {},
        'recommendation': '',
        'confidence': '',
        'data_quality': {}
    }
    
    # 1. Calculate price appreciation score (35%)
    appreciation_data = _calculate_price_appreciation(area, property_type, engine)
    appreciation_score = appreciation_data['score']
    
    # 2. Calculate liquidity score (25%)
    liquidity_data = _calculate_liquidity_score(area, property_type, engine)
    liquidity_score = liquidity_data['score']
    
    # 3. Calculate rental yield score (25%)
    # Use existing rental yield calculator
    yield_data = _calculate_yield_score(area, property_type, size_sqm, bedrooms, engine)
    yield_score = yield_data['score']
    
    # 4. Calculate market segment score (15%)
    # Use existing segment classification
    segment_data = _calculate_segment_score(property_type, area, size_sqm, bedrooms, engine)
    segment_score = segment_data['score']
    
    # Calculate weighted final score
    flip_score = (
        (appreciation_score * 0.35) +
        (liquidity_score * 0.25) +
        (yield_score * 0.25) +
        (segment_score * 0.15)
    )
    
    # Round to integer
    flip_score = int(round(flip_score))
    
    # Ensure score is in 1-100 range
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
        result['recommendation'] = 'This property shows limited flip potential. Better suited for long-term investment.'
    
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
```

**Add helper functions:**
```python
def _calculate_price_appreciation(area, property_type, engine):
    """Calculate price appreciation score based on QoQ growth"""
    try:
        # Query for quarterly average prices (last 12 months)
        query = text("""
            SELECT 
                EXTRACT(YEAR FROM transaction_date) as year,
                EXTRACT(QUARTER FROM transaction_date) as quarter,
                AVG(price_per_sqm) as avg_price_sqm,
                COUNT(*) as transaction_count
            FROM properties
            WHERE area_en = :area 
              AND property_type_en = :property_type
              AND transaction_date >= CURRENT_DATE - INTERVAL '12 months'
              AND price_per_sqm > 0
            GROUP BY year, quarter
            ORDER BY year DESC, quarter DESC
            LIMIT 4
        """)
        
        result = pd.read_sql(query, engine, params={'area': area, 'property_type': property_type})
        
        if len(result) < 2:
            # Insufficient data
            return {
                'score': 50,  # Neutral score
                'details': 'Insufficient data for trend analysis',
                'transactions': 0,
                'start_date': 'N/A',
                'end_date': 'N/A'
            }
        
        # Calculate QoQ growth rate
        latest_price = result.iloc[0]['avg_price_sqm']
        oldest_price = result.iloc[-1]['avg_price_sqm']
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


def _calculate_liquidity_score(area, property_type, engine):
    """Calculate liquidity score based on transaction volume"""
    try:
        query = text("""
            SELECT COUNT(*) as transaction_count
            FROM properties
            WHERE area_en = :area 
              AND property_type_en = :property_type
              AND transaction_date >= CURRENT_DATE - INTERVAL '12 months'
        """)
        
        result = pd.read_sql(query, engine, params={'area': area, 'property_type': property_type})
        count = int(result.iloc[0]['transaction_count'])
        
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


def _calculate_yield_score(area, property_type, size_sqm, bedrooms, engine):
    """Calculate rental yield score"""
    # This should call existing rental yield calculator
    # For now, placeholder implementation
    # TODO: Integrate with existing rental yield calculator
    
    try:
        # Placeholder - replace with actual rental yield calculation
        yield_percentage = 6.5  # Example yield
        
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
            'comparables': 10  # Number of rental comparables used
        }
        
    except Exception as e:
        logging.error(f"Yield score calculation error: {str(e)}")
        return {
            'score': 50,
            'details': 'Error calculating yield',
            'comparables': 0
        }


def _calculate_segment_score(property_type, area, size_sqm, bedrooms, engine):
    """Calculate score based on market segment"""
    # This should call existing segment classification
    # For now, placeholder implementation
    # TODO: Integrate with existing segment classification
    
    try:
        # Placeholder - replace with actual segment classification
        segment = 'Mid-Tier'  # Example segment
        
        segment_scores = {
            'Mid-Tier': 100,
            'Premium': 85,
            'Budget': 70,
            'Luxury': 60,
            'Ultra-Luxury': 40
        }
        
        score = segment_scores.get(segment, 70)
        
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
```

---

### File 2: `/workspaces/avm-retyn/templates/index.html`

**Add HTML section after rental yield card (~line 450):**
```html
<!-- Property Flip Score Card -->
<div class="card mt-4" id="flip-score-card" style="display: none;">
    <div class="card-header bg-warning text-white">
        <h5><i class="fas fa-chart-line"></i> Property Flip Score</h5>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-4 text-center">
                <div class="flip-score-circle">
                    <svg width="150" height="150">
                        <circle cx="75" cy="75" r="60" stroke="#e9ecef" stroke-width="15" fill="none"/>
                        <circle id="flip-score-progress" cx="75" cy="75" r="60" stroke="#ffc107" stroke-width="15" 
                                fill="none" stroke-dasharray="377" stroke-dashoffset="377" 
                                transform="rotate(-90 75 75)" style="transition: stroke-dashoffset 1s ease;"/>
                        <text x="75" y="75" text-anchor="middle" dy=".3em" font-size="32" font-weight="bold" id="flip-score-value">--</text>
                    </svg>
                </div>
                <h4 id="flip-score-rating" class="mt-3">--</h4>
                <span id="flip-score-confidence" class="badge badge-info">--</span>
            </div>
            <div class="col-md-8">
                <h6>Score Breakdown:</h6>
                <div class="flip-score-breakdown">
                    <div class="breakdown-item">
                        <span class="breakdown-label">Price Appreciation (35%)</span>
                        <div class="progress">
                            <div id="appreciation-bar" class="progress-bar bg-success" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="appreciation-details" class="text-muted">--</small>
                    </div>
                    <div class="breakdown-item mt-2">
                        <span class="breakdown-label">Liquidity (25%)</span>
                        <div class="progress">
                            <div id="liquidity-bar" class="progress-bar bg-info" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="liquidity-details" class="text-muted">--</small>
                    </div>
                    <div class="breakdown-item mt-2">
                        <span class="breakdown-label">Rental Yield (25%)</span>
                        <div class="progress">
                            <div id="yield-bar" class="progress-bar bg-primary" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="yield-details" class="text-muted">--</small>
                    </div>
                    <div class="breakdown-item mt-2">
                        <span class="breakdown-label">Market Position (15%)</span>
                        <div class="progress">
                            <div id="segment-bar" class="progress-bar bg-warning" role="progressbar" style="width: 0%"></div>
                        </div>
                        <small id="segment-details" class="text-muted">--</small>
                    </div>
                </div>
                <div class="alert alert-info mt-3" id="flip-recommendation">
                    <strong>Recommendation:</strong> <span id="flip-recommendation-text">--</span>
                </div>
                <small class="text-muted" id="flip-data-quality">Data quality: --</small>
            </div>
        </div>
    </div>
</div>
```

**Add CSS styling in `<style>` section:**
```css
.flip-score-circle {
    display: inline-block;
}

.flip-score-breakdown .breakdown-item {
    margin-bottom: 10px;
}

.breakdown-label {
    font-weight: 500;
    font-size: 14px;
}

.progress {
    height: 20px;
}

#flip-recommendation {
    border-left: 4px solid #ffc107;
}
```

---

### File 3: `/workspaces/avm-retyn/static/js/script.js`

**Add functions after rental yield code (~line 300):**
```javascript
// Fetch flip score
function fetchFlipScore() {
    const propertyType = document.getElementById('property_type').value;
    const area = document.getElementById('area').value;
    const sizeSqm = document.getElementById('size').value;
    const bedrooms = document.getElementById('bedrooms').value;
    
    fetch('/api/flip-score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            property_type: propertyType,
            area: area,
            size_sqm: sizeSqm,
            bedrooms: bedrooms
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Flip score error:', data.error);
            return;
        }
        displayFlipScore(data);
    })
    .catch(error => {
        console.error('Flip score fetch error:', error);
    });
}

// Display flip score in UI
function displayFlipScore(data) {
    // Show card
    document.getElementById('flip-score-card').style.display = 'block';
    
    // Update main score
    const score = data.flip_score;
    document.getElementById('flip-score-value').textContent = score;
    
    // Update circular progress
    const circumference = 2 * Math.PI * 60; // radius = 60
    const offset = circumference - (score / 100) * circumference;
    document.getElementById('flip-score-progress').style.strokeDashoffset = offset;
    
    // Update rating and confidence
    document.getElementById('flip-score-rating').textContent = data.rating;
    document.getElementById('flip-score-confidence').textContent = data.confidence + ' Confidence';
    
    // Update breakdown bars
    const breakdown = data.breakdown;
    document.getElementById('appreciation-bar').style.width = breakdown.price_appreciation.score + '%';
    document.getElementById('appreciation-details').textContent = breakdown.price_appreciation.details;
    
    document.getElementById('liquidity-bar').style.width = breakdown.liquidity.score + '%';
    document.getElementById('liquidity-details').textContent = breakdown.liquidity.details;
    
    document.getElementById('yield-bar').style.width = breakdown.rental_yield.score + '%';
    document.getElementById('yield-details').textContent = breakdown.rental_yield.details;
    
    document.getElementById('segment-bar').style.width = breakdown.market_position.score + '%';
    document.getElementById('segment-details').textContent = breakdown.market_position.details;
    
    // Update recommendation
    document.getElementById('flip-recommendation-text').textContent = data.recommendation;
    
    // Update data quality
    const dq = data.data_quality;
    document.getElementById('flip-data-quality').textContent = 
        `Data quality: ${dq.transactions_analyzed} transactions analyzed, ${dq.rental_comparables} rental comparables (${dq.date_range})`;
    
    // Scroll to flip score card
    document.getElementById('flip-score-card').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Integrate into existing valuation flow
// Add this line in the existing calculateValuation() function after rental yield:
// fetchFlipScore();
```

---

### File 4: `/workspaces/avm-retyn/tests/test_flip_score.py`

**Create new test file:**
```python
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, calculate_flip_score, _calculate_price_appreciation, _calculate_liquidity_score
from sqlalchemy import create_engine
import logging

# Setup
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_engine():
    # Use test database or mock
    # For now, use production database (read-only operations)
    DATABASE_URL = os.getenv('DATABASE_URL')
    engine = create_engine(DATABASE_URL)
    return engine


# Unit Tests

def test_flip_score_high_potential(db_engine):
    """Test high flip score for Dubai Marina apartment"""
    result = calculate_flip_score(
        property_type='Apartment',
        area='Dubai Marina',
        size_sqm=100,
        bedrooms=2,
        engine=db_engine
    )
    
    assert 'flip_score' in result
    assert 1 <= result['flip_score'] <= 100
    assert result['rating'] in ['Excellent Flip Potential', 'Good Flip Potential', 'Moderate Flip Potential', 'Low Flip Potential']
    assert result['confidence'] in ['High', 'Medium', 'Low']
    assert 'breakdown' in result
    assert len(result['breakdown']) == 4


def test_flip_score_low_potential(db_engine):
    """Test low flip score for ultra-luxury property"""
    result = calculate_flip_score(
        property_type='Villa',
        area='Palm Jumeirah',
        size_sqm=500,
        bedrooms=5,
        engine=db_engine
    )
    
    assert 'flip_score' in result
    assert 1 <= result['flip_score'] <= 100
    # Ultra-luxury typically has lower flip scores due to liquidity


def test_price_appreciation_calculation(db_engine):
    """Test price appreciation helper function"""
    result = _calculate_price_appreciation('Dubai Marina', 'Apartment', db_engine)
    
    assert 'score' in result
    assert 1 <= result['score'] <= 100
    assert 'details' in result
    assert 'transactions' in result


def test_liquidity_calculation(db_engine):
    """Test liquidity helper function"""
    result = _calculate_liquidity_score('Dubai Marina', 'Apartment', db_engine)
    
    assert 'score' in result
    assert 1 <= result['score'] <= 100
    assert 'details' in result
    assert 'transactions' in result


def test_flip_score_missing_data(db_engine):
    """Test flip score with area that has minimal data"""
    result = calculate_flip_score(
        property_type='Apartment',
        area='UnknownArea123',
        size_sqm=100,
        bedrooms=2,
        engine=db_engine
    )
    
    # Should still return valid score (graceful degradation)
    assert 'flip_score' in result
    assert result['confidence'] == 'Low'


def test_flip_score_boundary_values(db_engine):
    """Test flip score stays within 1-100 range"""
    # Test multiple properties
    areas = ['Dubai Marina', 'Downtown Dubai', 'JBR']
    
    for area in areas:
        result = calculate_flip_score(
            property_type='Apartment',
            area=area,
            size_sqm=100,
            bedrooms=2,
            engine=db_engine
        )
        
        assert 1 <= result['flip_score'] <= 100, f"Score out of bounds for {area}"


def test_flip_score_breakdown_sum(db_engine):
    """Test that breakdown contributions sum to final score"""
    result = calculate_flip_score(
        property_type='Apartment',
        area='Dubai Marina',
        size_sqm=100,
        bedrooms=2,
        engine=db_engine
    )
    
    breakdown = result['breakdown']
    total_contribution = (
        breakdown['price_appreciation']['contribution'] +
        breakdown['liquidity']['contribution'] +
        breakdown['rental_yield']['contribution'] +
        breakdown['market_position']['contribution']
    )
    
    # Allow 1-point rounding difference
    assert abs(result['flip_score'] - total_contribution) <= 1


# Integration Tests

def test_api_endpoint(client):
    """Test /api/flip-score endpoint"""
    response = client.post('/api/flip-score', json={
        'property_type': 'Apartment',
        'area': 'Dubai Marina',
        'size_sqm': 100,
        'bedrooms': 2
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'flip_score' in data
    assert 'breakdown' in data


def test_api_missing_parameters(client):
    """Test API with missing parameters"""
    response = client.post('/api/flip-score', json={
        'property_type': 'Apartment'
        # Missing area and size_sqm
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_api_performance(client):
    """Test API response time < 500ms"""
    import time
    
    start = time.time()
    response = client.post('/api/flip-score', json={
        'property_type': 'Apartment',
        'area': 'Dubai Marina',
        'size_sqm': 100,
        'bedrooms': 2
    })
    end = time.time()
    
    elapsed_ms = (end - start) * 1000
    
    assert response.status_code == 200
    assert elapsed_ms < 500, f"Response time {elapsed_ms}ms exceeds 500ms target"


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

---

## CONSTRAINTS

1. **Performance:** API response time must be <500ms
2. **Testing:** Maintain >90% code coverage
3. **Error Handling:** Graceful degradation when data is sparse
4. **Score Range:** Always return 1-100 (never 0, never >100)
5. **Database:** Read-only queries (no writes)
6. **Dependencies:** Use existing libraries only (no new pip installs)
7. **Code Style:** Follow PEP 8, use type hints, use logging (not print)
8. **Compatibility:** Flask app running on Python 3.12

---

## EDGE CASES TO HANDLE

1. **Sparse data** (area with <5 transactions) → Return neutral scores (50) with "Low confidence"
2. **Missing rental data** → Use area averages or flag in details
3. **New areas** (<6 months data) → Use city-wide trends with disclaimer
4. **Ultra-luxury properties** (low volume) → Adjust liquidity expectations
5. **Off-plan properties** → Flag as "Not applicable - no transaction history"
6. **Invalid inputs** (negative size, empty area) → Return 400 error with clear message
7. **Database timeout** → Return 500 error, log details
8. **Division by zero** (0 transactions) → Use fallback neutral score

---

## TESTING CHECKLIST

Run these tests to verify implementation:

```bash
# Run all tests
pytest tests/test_flip_score.py -v

# Run with coverage
pytest tests/test_flip_score.py --cov=app --cov-report=html

# Test specific property
curl -X POST http://localhost:5000/api/flip-score \
  -H "Content-Type: application/json" \
  -d '{"property_type":"Apartment","area":"Dubai Marina","size_sqm":100,"bedrooms":2}'
```

Expected results:
- All 10 tests pass
- Coverage >90%
- API returns 200 with valid JSON
- Response time <500ms

---

## SUCCESS CRITERIA

✅ Feature is complete when:
1. All 10 tests pass with >90% coverage
2. API endpoint returns valid JSON in <500ms
3. UI displays flip score with breakdown
4. Edge cases handled gracefully (no crashes)
5. Code passes flake8 linting
6. Documentation updated (README, API docs)

---

## DELIVERABLES

Please implement:
1. Backend functions in `app.py` (calculate_flip_score + helpers)
2. API endpoint `/api/flip-score`
3. Frontend display in `index.html` + `script.js`
4. Test suite in `tests/test_flip_score.py`
5. Run tests and confirm >90% coverage

Then report:
- Test results (pass/fail count)
- Performance benchmark (actual response time)
- Any edge cases discovered
- Next steps for integration with existing features

---

## EXAMPLE OUTPUT

When testing with Dubai Marina apartment (100 sqm, 2BR), expect:
```json
{
  "flip_score": 78,
  "rating": "Good Flip Potential",
  "breakdown": {
    "price_appreciation": {"score": 85, "weight": 35, "contribution": 29.75, "details": "QoQ growth: 4.2%"},
    "liquidity": {"score": 95, "weight": 25, "contribution": 23.75, "details": "67 transactions in last 12 months"},
    "rental_yield": {"score": 80, "weight": 25, "contribution": 20, "details": "Rental yield: 6.8%"},
    "market_position": {"score": 100, "weight": 15, "contribution": 15, "details": "Market segment: Mid-Tier"}
  },
  "recommendation": "This property has solid flip potential with favorable market conditions and reasonable returns.",
  "confidence": "High",
  "data_quality": {
    "transactions_analyzed": 67,
    "rental_comparables": 12,
    "date_range": "2023-Q4 to 2024-Q4"
  }
}
```

---

## NOTES FOR AI ASSISTANT

- Use existing database connection (don't create new one)
- Leverage existing functions where possible (rental yield, segment classification)
- TODO comments indicate where to integrate with existing code
- Follow project conventions (logging, error handling, response format)
- Prioritize working code over perfect code (can refine later)
- If stuck, implement basic version first, then enhance

---

**Let's implement this feature! 🚀**
```

---

## 🚀 QUICK WINS BUNDLE PROMPT (ALL 5 FEATURES)

For implementing all 5 quick wins today, I'll create a separate comprehensive prompt:

