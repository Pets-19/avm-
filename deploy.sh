#!/bin/bash
# Rapid deployment script for AVM project
# Usage: ./deploy.sh

echo "🚀 Deploying Flask application..."
echo ""

# Stop existing server
echo "⏹️  Stopping existing Flask server..."
pkill -f "python.*app.py"
sleep 2

# Check if stopped
if pgrep -f "python.*app.py" > /dev/null; then
    echo "⚠️  Warning: Old server still running, force killing..."
    pkill -9 -f "python.*app.py"
    sleep 1
fi

# Start new server
echo "▶️  Starting Flask server..."
cd /workspaces/avm-retyn
source venv/bin/activate
nohup python app.py > flask.log 2>&1 &

# Wait for startup
echo "⏳ Waiting for server to start..."
sleep 5

# Verify
PID=$(pgrep -f "python.*app.py")
if [ -n "$PID" ]; then
    echo "✅ Flask running (PID: $PID)"
    
    # Test endpoint
    echo "🔍 Testing server response..."
    if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/ | grep -q "200\|302"; then
        echo "✅ Server responding successfully"
        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🎉 DEPLOYMENT SUCCESSFUL"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🌐 URL: http://127.0.0.1:5000"
        echo "📋 PID: $PID"
        echo "📝 Logs: tail -f flask.log"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        exit 0
    else
        echo "❌ Server not responding correctly"
        echo "Last 20 lines of flask.log:"
        tail -20 flask.log
        exit 1
    fi
else
    echo "❌ Flask failed to start"
    echo "Last 20 lines of flask.log:"
    tail -20 flask.log
    exit 1
fi
