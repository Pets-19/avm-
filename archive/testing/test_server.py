#!/usr/bin/env python3
"""
Test server for the Property Valuation Interface
Bypasses database connection for frontend testing
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from valuation_engine import calculate_valuation
import os

app = Flask(__name__)
app.secret_key = 'test-key-for-dev'

# Mock user class for testing
class MockUser:
    def __init__(self):
        self.name = "Test User"

@app.route('/')
def index():
    # Mock authentication
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    current_user = MockUser()
    
    # Mock data for the interface
    sales_map = {}
    rentals_map = {}
    
    return render_template('index.html', 
                         current_user=current_user,
                         sales_map=sales_map,
                         rentals_map=rentals_map)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Mock authentication - accept retyn/retyn*#123
        if username == 'retyn' and password == 'retyn*#123':
            session['user_id'] = 1
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/api/property/valuation', methods=['POST'])
def property_valuation():
    # Check authentication
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['property_type', 'area', 'size_sqm']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Call the valuation engine
        result = calculate_valuation(
            property_type=data['property_type'],
            area=data['area'],
            size_sqm=float(data['size_sqm'])
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"Valuation error: {e}")
        return jsonify({'error': 'Internal server error occurred'}), 500

if __name__ == '__main__':
    print("🚀 Starting Property Valuation Test Server...")
    print("📍 Login credentials: retyn / retyn*#123")
    print("🌐 Server running at: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080, debug=True)