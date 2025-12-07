#!/bin/bash
# Monitor bot logs in real-time and highlight scheduler messages

echo "=== Monitoring bot logs (Ctrl+C to stop) ==="
echo "Looking for scheduler messages..."
echo ""

tail -f /home/azune/Documents/coding/discord-bot/bot_console.log 2>/dev/null | grep --line-buffered -E "(scheduler|Scheduled|BACKFILL|Economic|⏰|📊|✅)" &
TAIL_PID=$!

# Also monitor process stdout if available
if [ -f nohup.out ]; then
    tail -f nohup.out 2>/dev/null | grep --line-buffered -E "(scheduler|Scheduled|BACKFILL|Economic|⏰|📊|✅)" &
    TAIL2_PID=$!
fi

echo "Press Ctrl+C to stop monitoring..."
wait $TAIL_PID 2>/dev/null

if [ ! -z "$TAIL2_PID" ]; then
    kill $TAIL2_PID 2>/dev/null
fi
