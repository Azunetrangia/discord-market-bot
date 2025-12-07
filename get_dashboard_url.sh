#!/bin/bash
# Script để lấy public URL của dashboard

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 DISCORD BOT DASHBOARD - PUBLIC ACCESS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if ngrok is running
if ! pgrep -f "ngrok http" > /dev/null; then
    echo "❌ Ngrok is NOT running!"
    echo ""
    echo "To start ngrok, run:"
    echo "   cd /home/azune/Documents/coding/discord-bot"
    echo "   ngrok http 5000 --log=stdout > logs/ngrok.log 2>&1 &"
    echo ""
    exit 1
fi

# Get public URL from ngrok API
URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | \
      python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'] if data.get('tunnels') else '')" 2>/dev/null)

if [ -z "$URL" ]; then
    echo "⏳ Ngrok is starting... please wait a moment"
    echo ""
    exit 0
fi

echo "✅ Status: ONLINE"
echo ""
echo "🌐 Public URL:"
echo "   $URL"
echo ""
echo "🔐 Login Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📱 Access Methods:"
echo "   • From this computer: http://localhost:5000"
echo "   • From any device: $URL"
echo ""
echo "💡 Tips:"
echo "   • Share this URL to access from other devices"
echo "   • URL changes when ngrok restarts"
echo "   • Dashboard shows: feeds, stats, cache analytics"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
