# ✅ Immediate Post-Migration Tasks

## 🎯 **Quick Checklist (Next 24-48 Hours)**

### **1. Verify Migration Accuracy** ✅ DONE
```bash
cd discord-bot
python3 scripts/verify_migration.py
```

**Expected Output:**
```
✅ PASS  Guild Configs
✅ PASS  RSS Feeds
✅ PASS  Posted Articles
✅ PASS  Statistics

🎉 All verifications passed!
```

---

### **2. Monitor Cache Hit Rate (24 Hours)**

#### **Option A: One-time Snapshot**
```bash
# Take current performance snapshot
python3 scripts/monitor_performance.py
```

#### **Option B: Continuous Monitoring (Recommended)**
```bash
# Monitor for 24 hours, snapshot every 30 minutes
python3 scripts/monitor_performance.py --continuous --duration 24 --interval 30

# Or shorter test (2 hours, every 10 minutes)
python3 scripts/monitor_performance.py --continuous --duration 2 --interval 10
```

**What to Watch:**
- ✅ **Target Cache Hit Rate**: 70-90% (after warm-up period)
- ✅ **Articles Posted**: Should match before/after migration
- ✅ **No Errors**: Check logs for any database errors

**Monitor Output Example:**
```
[15:38:16] Snapshot 1 - Hit Rate: 0.0% - Articles: 259
[16:08:16] Snapshot 2 - Hit Rate: 45.2% - Articles: 264
[16:38:16] Snapshot 3 - Hit Rate: 72.5% - Articles: 268
[17:08:16] Snapshot 4 - Hit Rate: 85.1% - Articles: 273
```

---

### **3. Verify Bot Posts Articles Correctly**

#### **Check Logs**
```bash
# Follow bot logs in real-time
tail -f logs/news_cog.log

# Look for these patterns:
# ✅ "Posted: glassnode - ..."
# ✅ "Cached translation ..."
# ✅ "Cache HIT for text hash ..."
```

#### **Check Discord Channels**
- [ ] Verify new articles appear in Discord
- [ ] Verify translations are correct
- [ ] Verify no duplicate posts
- [ ] Verify embeds look correct

#### **Monitor Discord Bot Activity**
```bash
# Check database stats
python3 scripts/monitor_performance.py

# Should see:
# - Articles Added: increasing count
# - Cache Hit Rate: increasing percentage
```

---

### **4. Monitor for 7 Days (Recommended)**

Keep JSON backups for at least **7 days** before cleanup:

```bash
# Check database age
ls -lh data/news_bot.db

# If older than 7 days, safe to cleanup:
python3 scripts/cleanup_old_files.py
```

**Why 7 Days?**
- Catch any edge cases or bugs
- Verify across multiple posting cycles
- Ensure cache performs well
- Build confidence in new system

---

## 📊 **Expected Performance Metrics**

### **Cache Hit Rate Timeline**

| **Time** | **Expected Hit Rate** | **Status** |
|----------|---------------------|-----------|
| 0-2 hours | 0-30% | 🟡 Warming up |
| 2-6 hours | 30-60% | 🟢 Building cache |
| 6-12 hours | 60-80% | 🟢 Good performance |
| 12-24 hours | 70-90% | ✅ Optimal |
| 24+ hours | 85-95% | ✅ Steady state |

### **Database Performance**

| **Metric** | **JSON (Before)** | **SQLite (After)** |
|-----------|------------------|-------------------|
| Article lookup | 50-100ms | 1-5ms |
| Config save | 100-200ms | 10-20ms |
| Concurrent safety | ❌ Unsafe | ✅ Safe |
| Corruption risk | 🔴 High | 🟢 Zero |

---

## 🔍 **Troubleshooting**

### **Problem: Low Cache Hit Rate (<50% after 12 hours)**

**Possible Causes:**
- Bot restarting frequently (cache resets)
- Many unique articles (expected for diverse sources)
- Translation errors causing re-translations

**Check:**
```bash
# View cache stats
python3 scripts/test_database.py

# Check for translation errors in logs
grep "Translation error" logs/*.log
```

### **Problem: No Articles Posted**

**Check:**
1. Bot is running: `ps aux | grep python3 | grep main_bot`
2. Channels configured: Check Discord channel IDs
3. Database accessible: `ls -lh data/news_bot.db`
4. Logs for errors: `tail -100 logs/news_cog.log`

### **Problem: Duplicate Articles**

**Unlikely but if it happens:**
```bash
# Check database for duplicates
sqlite3 data/news_bot.db "
SELECT article_id, COUNT(*) 
FROM posted_articles 
GROUP BY guild_id, article_id 
HAVING COUNT(*) > 1
"
```

### **Problem: Database Locked Error**

**Should not happen with SQLite, but if it does:**
```bash
# Check for concurrent access
lsof data/news_bot.db

# Restart bot to reset connections
```

---

## 📝 **Daily Checks (First 7 Days)**

### **Day 1** ✅
- [x] Run migration verification
- [x] Start 24-hour monitoring
- [ ] Verify first articles posted correctly
- [ ] Check logs for errors

### **Day 2-3**
- [ ] Check cache hit rate >50%
- [ ] Verify no duplicate posts
- [ ] Monitor database size growth

### **Day 4-7**
- [ ] Check cache hit rate >80%
- [ ] Verify consistent performance
- [ ] Prepare for cleanup

### **Day 7+**
- [ ] Run cleanup script (optional)
- [ ] Archive JSON backups
- [ ] Celebrate! 🎉

---

## 🚀 **Performance Report**

After 24 hours, check the report:

```bash
# View JSON report
cat logs/performance_report.json | jq

# Or use monitor script
python3 scripts/monitor_performance.py
```

**Expected Report:**
```json
{
  "monitoring_started": "2025-12-07T15:38:16",
  "monitoring_ended": "2025-12-08T15:38:16",
  "total_snapshots": 48,
  "snapshots": [
    {
      "timestamp": "...",
      "cache": {
        "session_hit_rate": 85.2,
        "total_cached": 247,
        "total_uses": 1453
      },
      "database": {
        "total_articles": 312
      }
    }
  ]
}
```

---

## ✅ **Success Criteria**

Migration is successful if:

- ✅ Verification script passes all checks
- ✅ Cache hit rate reaches 70%+ within 24 hours
- ✅ Bot posts articles correctly to Discord
- ✅ No database errors in logs
- ✅ No duplicate posts
- ✅ Translations are correct
- ✅ Bot runs stably for 7 days

---

## 🆘 **Need Help?**

### **Check Logs**
```bash
# Main bot log
tail -100 logs/discord_bot.log

# News cog log
tail -100 logs/news_cog.log

# Database operations
tail -100 logs/database.log

# Translation cache
tail -100 logs/translation_cache.log
```

### **Get Statistics**
```bash
# Database stats
python3 scripts/test_database.py

# Performance snapshot
python3 scripts/monitor_performance.py

# Verify migration
python3 scripts/verify_migration.py
```

### **Rollback (If Needed)**
If serious issues occur:

1. Stop bot
2. Restore JSON backups from `data/backups/`
3. Delete `data/news_bot.db`
4. Restart bot with old system
5. Report issue for investigation

---

## 📅 **Timeline Summary**

| **Time** | **Task** | **Status** |
|----------|---------|-----------|
| **Now** | Verify migration | ✅ DONE |
| **0-24h** | Monitor cache hit rate | ⏳ IN PROGRESS |
| **24-48h** | Verify stable operation | ⏳ PENDING |
| **Day 7** | Cleanup old files | ⏳ SCHEDULED |

---

**Current Status: ✅ Migration Complete - Monitoring Phase**

Run continuous monitoring now:
```bash
# 24-hour monitoring (recommended)
python3 scripts/monitor_performance.py --continuous --duration 24

# Or quick 2-hour test
python3 scripts/monitor_performance.py --continuous --duration 2
```
