#!/bin/bash
# Quick commands for immediate post-migration tasks

echo "=================================="
echo "🚀 Discord Bot - Quick Commands"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Verify Migration${NC}"
echo "   python3 scripts/verify_migration.py"
echo ""

echo -e "${BLUE}2. Performance Snapshot${NC}"
echo "   python3 scripts/monitor_performance.py"
echo ""

echo -e "${BLUE}3. Start 24h Monitoring${NC}"
echo "   python3 scripts/monitor_performance.py --continuous --duration 24"
echo ""

echo -e "${BLUE}4. Quick 2h Test${NC}"
echo "   python3 scripts/monitor_performance.py --continuous --duration 2 --interval 10"
echo ""

echo -e "${BLUE}5. View Performance Report${NC}"
echo "   cat logs/performance_report.json | jq"
echo ""

echo -e "${BLUE}6. Check Database Stats${NC}"
echo "   python3 scripts/test_database.py"
echo ""

echo -e "${BLUE}7. View Bot Logs${NC}"
echo "   tail -f logs/news_cog.log"
echo ""

echo -e "${BLUE}8. Cleanup (after 7 days)${NC}"
echo "   python3 scripts/cleanup_old_files.py"
echo ""

echo -e "${GREEN}=================================="
echo "📊 Current Status"
echo "==================================${NC}"

# Database size
if [ -f "data/news_bot.db" ]; then
    DB_SIZE=$(du -h data/news_bot.db | cut -f1)
    echo -e "   Database: ${GREEN}✅${NC} ($DB_SIZE)"
else
    echo -e "   Database: ${YELLOW}❌${NC} Not found"
fi

# Check if monitoring is running
if pgrep -f "monitor_performance.py" > /dev/null; then
    echo -e "   Monitoring: ${GREEN}✅ Running${NC}"
else
    echo -e "   Monitoring: ${YELLOW}Not running${NC}"
fi

# Check if bot is running
if pgrep -f "main_bot.py" > /dev/null; then
    echo -e "   Bot: ${GREEN}✅ Running${NC}"
else
    echo -e "   Bot: ${YELLOW}Not running${NC}"
fi

# Latest report
if [ -f "logs/performance_report.json" ]; then
    REPORT_TIME=$(stat -c %y logs/performance_report.json | cut -d'.' -f1)
    echo -e "   Last Report: $REPORT_TIME"
fi

echo ""
echo -e "${GREEN}=================================="
echo "Run './quick_commands.sh' anytime"
echo "==================================${NC}"
