#!/bin/bash
# Quick fixes script - Run sau khi audit

echo "🔧 Applying Critical Fixes..."
echo "================================"
echo ""

# 1. Check requirements.txt
echo "📦 Checking requirements.txt..."
if ! grep -q "Flask" requirements.txt; then
    echo "Flask>=3.0.0" >> requirements.txt
    echo "✅ Added Flask to requirements.txt"
else
    echo "✓ Flask already in requirements.txt"
fi

if ! grep -q "requests" requirements.txt; then
    echo "requests>=2.31.0" >> requirements.txt
    echo "✅ Added requests to requirements.txt"
else
    echo "✓ requests already in requirements.txt"
fi

echo ""

# 2. Clean up economic calendar files
echo "🗑️  Cleaning up unused economic calendar files..."
ECONOMIC_FILES=(
    "scripts/check_economic_history.py"
    "scripts/dryrun_calendar.py"
    "scripts/send_test_economic_post.py"
    "scripts/remove_economic_calendar.py"
    "scripts/test_calendar_timeline.py"
    "scripts/economic_calendar_solutions.py"
)

mkdir -p scripts/deprecated 2>/dev/null

for file in "${ECONOMIC_FILES[@]}"; do
    if [ -f "$file" ]; then
        mv "$file" "scripts/deprecated/"
        echo "✅ Moved $file to deprecated/"
    fi
done

echo ""

# 3. Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data/backups 2>/dev/null
echo "✅ Directories created"

echo ""

# 4. Check .gitignore
echo "🚫 Checking .gitignore..."
if ! grep -q "\.db" .gitignore; then
    echo "⚠️  .gitignore needs update - see COMPREHENSIVE_AUDIT_FINAL.md"
else
    echo "✓ .gitignore looks good"
fi

echo ""

# 5. Remove runtime files from git
echo "🗑️  Removing runtime files from git..."
git rm --cached bot.pid dashboard.pid 2>/dev/null && echo "✅ Removed .pid files from git" || echo "✓ No .pid files in git"
git rm --cached logs/*.log 2>/dev/null && echo "✅ Removed log files from git" || echo "✓ No log files in git"

echo ""

# 6. Check database
echo "💾 Checking database..."
if [ -f "data/news_bot.db" ]; then
    SIZE=$(du -h data/news_bot.db | cut -f1)
    echo "✓ Database exists: $SIZE"
    
    # Get stats
    GUILDS=$(sqlite3 data/news_bot.db "SELECT COUNT(*) FROM guild_configs;" 2>/dev/null)
    FEEDS=$(sqlite3 data/news_bot.db "SELECT COUNT(*) FROM rss_feeds WHERE enabled=1;" 2>/dev/null)
    ARTICLES=$(sqlite3 data/news_bot.db "SELECT COUNT(*) FROM posted_articles;" 2>/dev/null)
    
    echo "  - Guilds: $GUILDS"
    echo "  - Active Feeds: $FEEDS"
    echo "  - Articles Posted: $ARTICLES"
else
    echo "⚠️  Database not found - will be created on first run"
fi

echo ""

# 7. Check if bot is running
echo "🤖 Checking bot status..."
if pgrep -f "main_bot.py" > /dev/null; then
    PID=$(pgrep -f "main_bot.py")
    echo "✅ Bot is RUNNING (PID: $PID)"
else
    echo "⚠️  Bot is NOT running"
    echo "   Start with: python main_bot.py"
fi

echo ""

# 8. Check dashboard status
echo "🌐 Checking dashboard status..."
if pgrep -f "dashboard/app.py" > /dev/null; then
    PID=$(pgrep -f "dashboard/app.py")
    echo "✅ Dashboard is RUNNING (PID: $PID)"
    
    # Get public URL if ngrok is running
    if pgrep -f "ngrok" > /dev/null; then
        URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['tunnels'][0]['public_url'])" 2>/dev/null)
        if [ ! -z "$URL" ]; then
            echo "   Public URL: $URL"
        fi
    fi
else
    echo "⚠️  Dashboard is NOT running"
    echo "   Start with: python dashboard/app.py"
fi

echo ""

# 9. Summary
echo "================================"
echo "✅ Critical fixes applied!"
echo ""
echo "📋 Next Steps:"
echo "   1. Review COMPREHENSIVE_AUDIT_FINAL.md"
echo "   2. Commit changes: git add . && git commit -m 'Apply critical fixes'"
echo "   3. Test on Windows (see WINDOWS_SETUP.md)"
echo "   4. Deploy Phase 3 (Docker) when ready"
echo ""
echo "================================"
