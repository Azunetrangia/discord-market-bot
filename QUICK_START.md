# Quick Start Guide - Discord Bot v2.0

## 🚀 Starting the Bot

```bash
cd /home/azune/Documents/coding/discord-bot
python3 main_bot.py
```

## 📋 What Changed?

### ❌ Removed Features
- Economic Calendar (all functionality removed)
- Button now shows "Coming Soon" message

### ✅ New Features
1. **Professional Logging** - All output goes to log files
2. **Retry Logic** - API failures automatically retry
3. **Rate Limiting** - Prevents API bans
4. **Config Management** - Easy to adjust settings

## 📂 Important Files

```
discord-bot/
├── main_bot.py          # Start here - run this file
├── config.py            # Settings & constants (edit here for changes)
├── logger_config.py     # Logging setup
├── utils.py             # Helper functions
├── .env                 # API keys (NEVER commit this!)
├── cogs/
│   └── news_cog.py     # Main news logic (1,556 lines)
├── data/
│   ├── news_config.json      # Per-guild configuration
│   └── last_post_ids.json    # Track posted articles
└── logs/                      # NEW - Log files here
    ├── bot.log               # General logs
    ├── errors.log            # Errors only
    └── debug.log             # Detailed debug (if enabled)
```

## 🔧 Configuration

### Edit Settings in `config.py`:
```python
NEWS_CHECK_INTERVAL = 180  # Check every 3 minutes
REQUEST_TIMEOUT = 30       # HTTP timeout in seconds
MAX_RETRIES = 3            # Retry failed API calls
GLASSNODE_MAX_ARTICLES = 5 # Articles per fetch
```

### Environment Variables in `.env`:
```bash
DISCORD_TOKEN=your_discord_bot_token_here
SANTIMENT_API_KEY=your_santiment_key_here

# Optional overrides
NEWS_CHECK_INTERVAL=180
REQUEST_TIMEOUT=30
MAX_RETRIES=3
```

## 📊 Viewing Logs

### Real-time logs:
```bash
# Watch all logs
tail -f logs/bot.log

# Watch errors only
tail -f logs/errors.log

# Watch debug (if enabled)
tail -f logs/debug.log
```

### Search logs:
```bash
# Find errors
grep ERROR logs/bot.log

# Find warnings
grep WARNING logs/bot.log

# Find API calls
grep "Fetched" logs/bot.log
```

### Enable debug logging:
Edit `logger_config.py`:
```python
logger = setup_logging(log_level=logging.DEBUG)  # Change INFO to DEBUG
```

## 🔍 Common Issues

### Bot won't start
```bash
# Check syntax
python3 -m py_compile main_bot.py

# Check imports
python3 -c "from cogs.news_cog import NewsCog"

# Check token
grep DISCORD_TOKEN .env
```

### No news appearing
```bash
# Check logs for errors
tail -20 logs/errors.log

# Verify API keys
grep API_KEY .env

# Test individual fetch
python3 -c "import asyncio; from cogs.news_cog import NewsCog; print('OK')"
```

### Rate limit errors
```bash
# Increase retry delay in config.py:
RETRY_BASE_DELAY = 5  # Increase from 1 to 5 seconds
```

## 📝 Testing

### Test news sources:
```python
# In Discord, use /start command
# Then click "Quản lý Tin tức"
# Choose "Liệt kê các nguồn tin" to verify setup
```

### Manual test fetch:
```python
# Create test_fetch.py:
import asyncio
from cogs.news_cog import NewsCog
from discord.ext import commands

async def test():
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
    cog = NewsCog(bot)
    
    # Test Glassnode
    articles = await cog.fetch_glassnode_insights()
    print(f"Glassnode: {len(articles)} articles")
    
    # Test The Block
    articles = await cog.fetch_theblock_news()
    print(f"The Block: {len(articles)} articles")

asyncio.run(test())
```

## 🎯 Useful Commands

### Check bot status:
```bash
# Find bot process
ps aux | grep main_bot.py

# Check bot uptime
ls -lh logs/bot.log
```

### Restart bot:
```bash
# Stop
pkill -f main_bot.py

# Start
python3 main_bot.py &

# Or use screen/tmux for persistent session
screen -S discord-bot
python3 main_bot.py
# Ctrl+A, then D to detach
```

### Clean up logs:
```bash
# Archive old logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/*.log

# Clear current logs
> logs/bot.log
> logs/errors.log
```

## 🔐 Security Reminders

1. **NEVER commit `.env`** - Contains sensitive tokens
2. **Rotate tokens** - If accidentally exposed
3. **Restrict bot permissions** - Only needed permissions
4. **Monitor logs** - Check for suspicious activity
5. **Backup configs** - `data/` folder regularly

## 📈 Monitoring

### Daily checks:
```bash
# Check error count
grep -c ERROR logs/bot.log

# Check warning count  
grep -c WARNING logs/bot.log

# Check news posted today
grep "$(date +%Y-%m-%d)" logs/bot.log | grep "Fetched" | wc -l
```

### Performance metrics:
```bash
# Average API response time (if logged)
grep "response_time" logs/bot.log | awk '{sum+=$NF; count++} END {print sum/count}'

# Failed API calls
grep "retry attempt" logs/bot.log | wc -l
```

## 🆘 Emergency Procedures

### Bot crashed:
1. Check `logs/errors.log` for stack trace
2. Verify .env file exists and has correct tokens
3. Restart bot: `python3 main_bot.py`
4. If persists, check Discord API status

### Rate limited:
1. Increase `RETRY_BASE_DELAY` in config.py
2. Reduce fetch frequency in `@tasks.loop(minutes=X)`
3. Check rate limiter settings in utils.py

### Memory leak:
1. Check log file sizes: `du -h logs/`
2. Check bot memory: `ps aux | grep main_bot.py`
3. Restart bot to clear memory
4. Consider log rotation settings

## 📚 Additional Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Python Logging Guide](https://docs.python.org/3/howto/logging.html)
- [Asyncio Best Practices](https://docs.python.org/3/library/asyncio.html)

## 🎓 Next Steps

1. **Monitor logs** - First few days after deployment
2. **Adjust rate limits** - Based on actual usage
3. **Fine-tune retry delays** - Based on API response times
4. **Add more news sources** - Using existing patterns
5. **Consider database** - If scaling to many guilds

---

**Questions?** Check logs first, then review IMPROVEMENTS_SUMMARY.md for details.
