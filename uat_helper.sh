#!/bin/bash
# UAT Helper Script - Flip Score Filter
# Usage: ./uat_helper.sh

echo "========================================================"
echo "🧪 UAT HELPER - Flip Score Filter"
echo "========================================================"
echo ""

# Function to check Flask status
check_flask() {
    if pgrep -f "python app.py" > /dev/null; then
        echo "✅ Flask is running"
        return 0
    else
        echo "❌ Flask is NOT running"
        echo "   Start with: nohup python app.py > flask.log 2>&1 &"
        return 1
    fi
}

# Function to monitor Flask logs for flip score filter
monitor_logs() {
    echo ""
    echo "📊 Monitoring Flask logs for flip score activity..."
    echo "   Press Ctrl+C to stop"
    echo ""
    tail -f flask.log | grep --line-buffered -i "flip\|valuation"
}

# Function to check database status
check_database() {
    echo ""
    echo "🔍 Database Status Check..."
    python3 -c "
from app import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check flip score data
    result = conn.execute(text('''
        SELECT 
            COUNT(*) as total,
            MIN(flip_score) as min_score,
            MAX(flip_score) as max_score
        FROM properties 
        WHERE flip_score IS NOT NULL
    '''))
    row = result.fetchone()
    print(f'   Properties with flip scores: {row[0]}')
    print(f'   Score range: {row[1]} - {row[2]}')
    
    # Check distribution
    result2 = conn.execute(text('''
        SELECT flip_score, COUNT(*) as count
        FROM properties 
        WHERE flip_score IS NOT NULL
        GROUP BY flip_score
        ORDER BY flip_score
    '''))
    print('')
    print('   Distribution:')
    for r in result2:
        print(f'   - Score {r[0]}: {r[1]} properties')
"
}

# Function to show test URLs
show_test_urls() {
    echo ""
    echo "🌐 Test URLs and Credentials:"
    echo "   URL: http://localhost:5000"
    echo "   User: dhanesh@retyn.ai"
    echo "   Pass: retyn*#123"
    echo ""
    echo "📋 Quick Test Steps:"
    echo "   1. Login with above credentials"
    echo "   2. Go to 'Property Valuation' tab"
    echo "   3. Find '📈 Flip Score (Investment)' dropdown"
    echo "   4. Select '70+'"
    echo "   5. Fill: Area='Madinat Al Mataar', Size=2000"
    echo "   6. Click 'Get Valuation'"
    echo "   7. Check browser console (F12) for 'flip_score_min: 70'"
}

# Function to run quick verification
quick_verify() {
    echo ""
    echo "⚡ Running Quick Verification..."
    
    # Check Flask
    check_flask
    flask_status=$?
    
    if [ $flask_status -eq 0 ]; then
        # Check database
        check_database
        
        # Show test info
        show_test_urls
        
        echo ""
        echo "========================================================"
        echo "✅ System Ready for UAT"
        echo "========================================================"
        echo ""
        echo "📝 Next Steps:"
        echo "   1. Open UAT_FLIP_SCORE_FILTER.md"
        echo "   2. Execute 12 test cases"
        echo "   3. Complete sign-off checklist"
        echo ""
    else
        echo ""
        echo "⚠️ Flask not running - start it first!"
    fi
}

# Function to show menu
show_menu() {
    echo ""
    echo "Choose an option:"
    echo "  1) Quick Verification (recommended first step)"
    echo "  2) Monitor Flask Logs (real-time)"
    echo "  3) Check Database Status"
    echo "  4) Show Test URLs & Credentials"
    echo "  5) Open UAT Checklist"
    echo "  6) Exit"
    echo ""
    read -p "Enter choice [1-6]: " choice
    
    case $choice in
        1)
            quick_verify
            ;;
        2)
            monitor_logs
            ;;
        3)
            check_database
            ;;
        4)
            show_test_urls
            ;;
        5)
            if [ -f "UAT_FLIP_SCORE_FILTER.md" ]; then
                echo "Opening UAT checklist..."
                cat UAT_FLIP_SCORE_FILTER.md | head -100
                echo ""
                echo "(Full file: UAT_FLIP_SCORE_FILTER.md)"
            else
                echo "❌ UAT_FLIP_SCORE_FILTER.md not found"
            fi
            ;;
        6)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            ;;
    esac
}

# Main execution
if [ "$1" == "verify" ]; then
    quick_verify
elif [ "$1" == "logs" ]; then
    monitor_logs
elif [ "$1" == "db" ]; then
    check_database
else
    # Interactive mode
    quick_verify
    
    # Show menu loop
    while true; do
        show_menu
    done
fi
