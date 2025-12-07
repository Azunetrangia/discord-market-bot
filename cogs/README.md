# 📦 Cogs Package

Thư mục này chứa các Discord Bot Cogs (modules) để tổ chức code.

## 📁 Files

### 🗞️ news_cog.py
-**Chức năng:** Quản lý tin tức tự động
- Tích hợp Glassnode (RSS)
- Tích hợp Santiment API  
- Hỗ trợ nhiều RSS Feeds
- Background task kiểm tra tin mới (10 phút)
- UI: Select Menu, Modal, ChannelSelect

**Classes:**
- `NewsCog` - Main cog class
- `NewsMenuView` - Select menu chính
- `AddRSSModal` - Form thêm RSS
- `ChannelSelectView` - Chọn channel
- `RemoveRSSView` - Xóa RSS

**Background Tasks:**
- `news_checker` - Loop 10 phút

---

### 🔔 alerts_cog.py
**Chức năng:** Quản lý cảnh báo giá crypto
- Tích hợp CoinGecko API
- Kiểm tra giá tự động (60 giây)
- Tự động vẽ biểu đồ 7 ngày
- Ping user khi trigger
- UI: Select Menu, Modal

**Classes:**
- `AlertsCog` - Main cog class
- `AlertsMenuView` - Select menu chính
- `AddAlertModal` - Form thêm alert
- `RemoveAlertView` - Xóa alert

**Background Tasks:**
- `price_checker` - Loop 60 giây

**Chart Generation:**
- Matplotlib integration
- 7-day price history
- Target price visualization

---

### 📄 __init__.py
Package marker file (required for Python imports)

---

## 🔌 How Cogs Work

Cogs are loaded in `main_bot.py`:

```python
async def setup_hook(self):
    await self.load_extension('cogs.news_cog')
    await self.load_extension('cogs.alerts_cog')
```

Each cog must have a `setup()` function:

```python
async def setup(bot):
    await bot.add_cog(MyCog(bot))
```

---

## 🎯 Adding a New Cog

1. Create `new_cog.py` in this folder
2. Create your cog class:
   ```python
   from discord.ext import commands
   
   class NewCog(commands.Cog):
       def __init__(self, bot):
           self.bot = bot
   
   async def setup(bot):
       await bot.add_cog(NewCog(bot))
   ```

3. Load in `main_bot.py`:
   ```python
   await self.load_extension('cogs.new_cog')
   ```

---

## 📊 Cog Statistics

| Cog | Lines | Classes | Tasks | Purpose |
|-----|-------|---------|-------|---------|
| news_cog.py | ~450 | 5 | 1 | News aggregation |
| alerts_cog.py | ~400 | 4 | 1 | Price alerts |

**Total:** ~850 lines of code

---

## 🔄 Cog Lifecycle

```
Bot Start
    ↓
load_extension()
    ↓
Cog.__init__()
    ↓
Cog.cog_load() (if exists)
    ↓
Background tasks start
    ↓
Bot Ready
    ↓
... Running ...
    ↓
Bot Stop
    ↓
Cog.cog_unload()
    ↓
Background tasks stop
```

---

## 🛠️ Development Tips

**Hot Reload (for testing):**
```python
# In Discord
!reload cogs.news_cog
```

**Unload Cog:**
```python
await bot.unload_extension('cogs.news_cog')
```

**Reload Cog:**
```python
await bot.reload_extension('cogs.news_cog')
```

---

## 📚 Learn More

- discord.py Cogs: https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html
- Example Cogs: https://github.com/Rapptz/discord.py/tree/master/examples
