# 🔧 Troubleshooting Guide

Hướng dẫn giải quyết các vấn đề thường gặp khi sử dụng Discord Bot.

---

## 🚨 Lỗi Khởi động (Startup Errors)

### ❌ "ModuleNotFoundError: No module named 'discord'"

**Nguyên nhân:** Chưa cài đặt dependencies

**Giải pháp:**
```bash
pip install -r requirements.txt

# Hoặc cài thủ công:
pip install discord.py python-dotenv aiohttp feedparser matplotlib pycoingecko
```

**Kiểm tra:**
```bash
pip list | grep discord
# Phải thấy: discord.py  2.3.2 (hoặc cao hơn)
```

---

### ❌ "DISCORD_TOKEN not found in .env"

**Nguyên nhân:** File .env không tồn tại hoặc thiếu token

**Giải pháp:**
```bash
# Tạo file .env từ template
cp .env.example .env

# Mở và chỉnh sửa
nano .env  # hoặc notepad .env trên Windows
```

**Nội dung .env phải có:**
```env
DISCORD_TOKEN=your_actual_token_here
MESSARI_API_KEY=your_key
SANTIMENT_API_KEY=your_key
COINGECKO_API_KEY=your_key
```

---

### ❌ "discord.errors.LoginFailure: Improper token has been passed"

**Nguyên nhân:** Token sai hoặc không hợp lệ

**Giải pháp:**
1. Vào https://discord.com/developers/applications
2. Chọn application của bạn
3. Tab "Bot" → Click "Reset Token"
4. Copy token mới
5. Paste vào file .env
6. **Lưu ý:** Token chỉ hiển thị 1 lần!

---

### ❌ "ImportError: cannot import name 'CoinGeckoAPI'"

**Nguyên nhân:** Package pycoingecko chưa được cài

**Giải pháp:**
```bash
pip install pycoingecko

# Hoặc upgrade nếu đã cài:
pip install --upgrade pycoingecko
```

---

## 🔄 Lỗi Runtime (Runtime Errors)

### ❌ Bot online nhưng không phản hồi lệnh /start

**Nguyên nhân:** Commands chưa được sync

**Giải pháp:**
1. Đợi 5-10 phút để Discord sync tự động
2. Restart bot:
   ```bash
   # Dừng bot (Ctrl+C)
   # Chạy lại
   python main_bot.py
   ```
3. Nếu vẫn không được, kick bot và add lại:
   - Kick bot khỏi server
   - Add lại bằng OAuth2 URL
   - Đảm bảo chọn scope: `bot` + `applications.commands`

**Kiểm tra permissions:**
```python
# Bot phải có quyền:
✅ Use Application Commands
✅ Send Messages
✅ Embed Links
✅ Attach Files
✅ Read Message History
```

---

### ❌ "Interaction failed" khi bấm button

**Nguyên nhân:** Timeout hoặc bot restart

**Giải pháp:**
- Gõ lại `/start`
- Button/View chỉ hoạt động trong thời gian timeout (3 phút cho sub-menus)
- Persistent views (MainView) không bao giờ expire

**Nếu vẫn lỗi:**
```python
# Kiểm tra console logs
# Tìm dòng lỗi và báo cáo
```

---

### ❌ "403 Forbidden" khi bot cố gửi tin

**Nguyên nhân:** Bot thiếu quyền trong channel

**Giải pháp:**
1. Vào Channel Settings → Permissions
2. Tìm role của bot
3. Bật các quyền:
   ```
   ✅ View Channel
   ✅ Send Messages
   ✅ Embed Links
   ✅ Attach Files
   ✅ Mention Everyone (optional cho alerts)
   ```

---

### ❌ "404 Not Found" khi fetch tin tức

**Nguyên nhân:** API endpoint sai hoặc API key không hợp lệ

**Giải pháp:**

**Messari:**
```bash
# Test API key
curl -H "x-messari-api-key: YOUR_KEY" https://data.messari.io/api/v1/news
```

**Santiment:**
```bash
# Test API key
curl -X POST https://api.santiment.net/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: Apikey YOUR_KEY" \
  -d '{"query": "{getMetric(metric: \"price_usd\"){timeseriesData(slug: \"bitcoin\" from: \"2024-01-01T00:00:00Z\" to: \"2024-01-02T00:00:00Z\" interval: \"1d\"){datetime value}}}"}'
```

**CoinGecko:**
```bash
# Test API key
curl -H "x_cg_demo_api_key: YOUR_KEY" "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
```

---

## 📰 Lỗi Tin tức (News Errors)

### ❌ Không nhận được tin từ Messari/Santiment

**Kiểm tra:**
1. API key có đúng không?
   ```bash
   cat .env | grep API_KEY
   ```

2. Kênh đã được cài đặt chưa?
   - Gõ `/start` → Quản lý Tin tức → Liệt kê các nguồn tin
   - Phải thấy kênh được liệt kê

3. Background task có đang chạy?
   ```bash
   # Xem console logs
   # Phải thấy: "Synced commands" khi khởi động
   ```

4. Đợi 10 phút cho vòng lặp tiếp theo

**Debug:**
```python
# Thêm vào news_cog.py, dòng đầu của news_checker:
@tasks.loop(minutes=10)
async def news_checker(self):
    print(f"[DEBUG] Checking news at {datetime.now()}")
    # ... rest of code
```

---

### ❌ RSS Feed không hoạt động

**Nguyên nhân:** URL sai hoặc feed không hợp lệ

**Test RSS Feed:**
```python
import feedparser

# Test trong Python shell
feed = feedparser.parse('YOUR_RSS_URL')
print(f"Entries: {len(feed.entries)}")

if feed.entries:
    print(f"First entry: {feed.entries[0].title}")
else:
    print("No entries found!")
```

**RSS URLs phổ biến:**
```
CoinDesk: https://www.coindesk.com/arc/outboundfeeds/rss/
Cointelegraph: https://cointelegraph.com/rss
Bitcoin Magazine: https://bitcoinmagazine.com/.rss/full/
```

---

### ❌ Tin bị trùng lặp

**Nguyên nhân:** File last_post_ids.json bị lỗi

**Giải pháp:**
```bash
# Reset file
rm data/last_post_ids.json

# Tạo lại
echo '{"messari": [], "santiment": [], "rss": {}}' > data/last_post_ids.json

# Restart bot
```

---

## 🔔 Lỗi Cảnh báo (Alert Errors)

### ❌ "Không tìm thấy coin" khi thêm alert

**Nguyên nhân:** Ticker sai hoặc CoinGecko không support

**Giải pháp:**

**Dùng ticker phổ biến:**
```
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, 
MATIC, AVAX, LINK, UNI, ATOM, LTC, ETC
```

**Tìm CoinGecko ID:**
```bash
# Search coin
curl "https://api.coingecko.com/api/v3/search?query=cardano"

# Dùng 'id' field trong response
# Example: "id": "cardano"
```

**Dùng CoinGecko ID trực tiếp:**
- Thay vì `ADA`, nhập `cardano`
- Thay vì `DOT`, nhập `polkadot`

---

### ❌ Cảnh báo không kích hoạt dù giá đã đạt

**Kiểm tra:**

1. **Alert có tồn tại?**
   ```bash
   cat data/alerts.json
   # Phải thấy alert của bạn
   ```

2. **Background task có chạy?**
   ```bash
   # Xem console logs
   # Mỗi 60 giây phải có activity
   ```

3. **CoinGecko API key có đúng?**
   ```bash
   # Test:
   curl -H "x_cg_demo_api_key: YOUR_KEY" \
     "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
   ```

4. **Điều kiện trigger:**
   - Alert chỉ trigger khi: `current_price >= target_price`
   - Nếu đặt target = 50000 và giá hiện tại = 49999 → Không trigger

**Debug:**
```python
# Thêm vào alerts_cog.py trong price_checker:
for alert in alerts:
    current_price = prices[alert['ticker']]['usd']
    print(f"[DEBUG] {alert['ticker']}: ${current_price} vs ${alert['target_price']}")
```

---

### ❌ Biểu đồ không hiển thị

**Nguyên nhân:** Matplotlib lỗi hoặc thiếu dependencies

**Giải pháp:**

**Linux:**
```bash
sudo apt-get install python3-tk
pip install --upgrade matplotlib
```

**Mac:**
```bash
brew install python-tk
pip install --upgrade matplotlib
```

**Windows:**
```bash
pip install --upgrade matplotlib
# Cài Visual C++ Build Tools nếu lỗi
```

**Test matplotlib:**
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.plot([1, 2, 3], [1, 2, 3])
plt.savefig('test.png')
print("Success! Check test.png")
```

---

### ❌ "Rate limit exceeded" từ CoinGecko

**Nguyên nhân:** Quá nhiều requests

**Giải pháp:**

1. **Dùng API Key (QUAN TRỌNG):**
   - Free tier: 10-30 calls/min
   - Demo (with key): 500 calls/min
   - Đăng ký tại: https://www.coingecko.com/en/api/pricing

2. **Giảm tần suất check:**
   ```python
   # Trong alerts_cog.py
   @tasks.loop(seconds=120)  # Thay vì 60
   ```

3. **Giảm số alert:**
   - Free tier phù hợp cho ~10-20 alerts
   - Demo tier: 100+ alerts

---

## 📊 Lỗi Biểu đồ (Chart Errors)

### ❌ Chart bị méo hoặc không đúng

**Giải pháp:**
```python
# Trong alerts_cog.py, điều chỉnh:
plt.figure(figsize=(12, 6))  # Kích thước
plt.tight_layout()            # Auto spacing
```

---

### ❌ "No data available for coin"

**Nguyên nhân:** CoinGecko không có dữ liệu 7 ngày

**Giải pháp:**
- Coin quá mới (< 7 ngày)
- Thay đổi days parameter:
  ```python
  data = self.cg.get_coin_market_chart_by_id(
      id=coin_id,
      vs_currency='usd',
      days=1  # Thay vì 7
  )
  ```

---

## 🗄️ Lỗi Data (Data Errors)

### ❌ "JSONDecodeError" khi đọc file

**Nguyên nhân:** File JSON bị corrupt

**Giải pháp:**
```bash
# Backup
cp data/alerts.json data/alerts.json.bak

# Reset về default
echo '[]' > data/alerts.json

# Hoặc fix JSON bằng online tool:
# https://jsonlint.com/
```

---

### ❌ File data/ không được tạo

**Giải pháp:**
```bash
# Tạo thủ công
mkdir data

# Tạo các file cần thiết
echo '{"messari_channel": null, "santiment_channel": null, "rss_feeds": []}' > data/news_config.json
echo '{"messari": [], "santiment": [], "rss": {}}' > data/last_post_ids.json
echo '[]' > data/alerts.json
```

---

## 🌐 Lỗi Network (Network Errors)

### ❌ "ConnectionError" / "TimeoutError"

**Nguyên nhân:** Mất kết nối internet hoặc API down

**Giải pháp:**

1. **Kiểm tra internet:**
   ```bash
   ping google.com
   ```

2. **Kiểm tra API status:**
   - Discord: https://discordstatus.com/
   - CoinGecko: https://status.coingecko.com/
   - Messari: Check their Twitter
   - Santiment: Check their Status page

3. **Thêm timeout & retry:**
   ```python
   # Trong aiohttp calls
   async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
       ...
   ```

---

## 💻 Lỗi Hệ thống (System Errors)

### ❌ Bot crashes sau vài giờ

**Nguyên nhân:** Memory leak hoặc uncaught exception

**Giải pháp:**

1. **Enable logging:**
   ```python
   # Thêm vào main_bot.py
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

2. **Monitor resources:**
   ```bash
   # Linux/Mac
   top -p $(pgrep -f main_bot.py)
   
   # Windows Task Manager
   Tìm process "python"
   ```

3. **Auto-restart script:**
   ```bash
   # Linux/Mac
   while true; do
       python main_bot.py
       echo "Bot crashed! Restarting in 5 seconds..."
       sleep 5
   done
   ```

---

### ❌ "Too many open files"

**Nguyên nhân:** Không close file handles

**Giải pháp:**

**Linux:**
```bash
ulimit -n 4096
```

**Code fix:**
```python
# Đảm bảo dùng context manager
async with aiohttp.ClientSession() as session:
    # ... code
# Session tự động close

with open(file, 'r') as f:
    # ... code
# File tự động close
```

---

## 🔒 Lỗi Permissions (Permission Errors)

### ❌ "Missing Permissions" error

**Giải pháp:**

1. **Kiểm tra bot role:**
   - Server Settings → Roles
   - Tìm bot role
   - Đảm bảo có đủ permissions

2. **Channel overrides:**
   - Channel Settings → Permissions
   - Thêm bot role
   - Enable required permissions

3. **Re-invite bot với đủ quyền:**
   - Discord Developer Portal
   - OAuth2 → URL Generator
   - Chọn: `Administrator` (recommended)
   - Hoặc chọn từng quyền cụ thể

---

## 📱 Lỗi Giao diện (UI Errors)

### ❌ Buttons không hiển thị

**Nguyên nhân:** Discord client outdated

**Giải pháp:**
- Update Discord app
- Hoặc dùng Discord web (discord.com)

---

### ❌ Select Menu rỗng

**Nguyên nhân:** Không có dữ liệu

**Example:** "Xóa RSS Feed" mà chưa có RSS nào

**Giải pháp:**
- Thêm dữ liệu trước
- Code đã handle: Hiển thị message "Không có dữ liệu"

---

## 🛠️ Tools Debug

### Enable Debug Mode:

```python
# Thêm vào main_bot.py
import logging

# Set log level
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s'
)

# Chỉ log discord.py
discord.utils.setup_logging(level=logging.DEBUG)
```

### Test Individual Components:

```python
# Test CoinGecko
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI(api_key='YOUR_KEY')
print(cg.get_price(ids='bitcoin', vs_currencies='usd'))

# Test Messari
import aiohttp
import asyncio

async def test():
    async with aiohttp.ClientSession() as session:
        headers = {'x-messari-api-key': 'YOUR_KEY'}
        async with session.get('https://data.messari.io/api/v1/news', headers=headers) as r:
            print(await r.json())

asyncio.run(test())

# Test RSS
import feedparser
feed = feedparser.parse('https://cointelegraph.com/rss')
print(f"Found {len(feed.entries)} entries")
```

---

## 📞 Khi Cần Hỗ trợ

**Thông tin cần cung cấp:**
1. Python version: `python --version`
2. OS: Linux/Mac/Windows
3. Error message đầy đủ (copy từ console)
4. Steps to reproduce
5. File .env có đầy đủ keys không? (Đừng share keys!)
6. Bot có online không?

**Nơi nhận hỗ trợ:**
- GitHub Issues (nếu có repo)
- discord.py Discord Server: https://discord.gg/dpy
- Stack Overflow với tag `discord.py`

---

## ✅ Checklist Tự kiểm tra

Trước khi báo lỗi, hãy check:

```
[ ] Python >= 3.8 installed
[ ] All dependencies installed (pip list)
[ ] .env file exists and has all keys
[ ] Discord bot token is valid
[ ] Bot is added to server with correct permissions
[ ] Internet connection is stable
[ ] API keys are valid and not rate limited
[ ] data/ folder exists with all JSON files
[ ] Console logs don't show obvious errors
[ ] Tried restarting bot
[ ] Waited for command sync (5-10 min)
```

---

**Nếu vẫn không giải quyết được, hãy tạo GitHub Issue với đầy đủ thông tin!**
