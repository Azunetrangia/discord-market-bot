# 🤖 Discord News Bot

Bot Discord chuyên nghiệp tổng hợp tin tức kinh tế & crypto tự động với timezone UTC+7:
- 📰 **Tin tức Đa nguồn**: Glassnode, Santiment, The Block, 5phutcrypto, RSS Feeds
- 📅 **Economic Calendar**: Lịch kinh tế từ Investing.com (UTC+7)
- 🌐 **Dịch tự động**: Tự động dịch tin nước ngoài sang tiếng Việt
- 🎨 **Multi-guild Support**: Hỗ trợ nhiều Discord servers cùng lúc
- 🕐 **Timezone UTC+7**: Hiển thị giờ Việt Nam cho tất cả events

## ✨ Tính năng nổi bật

### 📰 Tin tức Crypto & Kinh tế
- **Glassnode Insights**: On-chain analytics & research (thay thế Messari)
- **Santiment API**: Phân tích on-chain và insights
- **The Block**: Tin tức crypto institutional-grade
- **5phutcrypto.io**: Tin tức & phân tích tiếng Việt
- **RSS Feeds**: Thêm nguồn tùy chỉnh (VNExpress, BBC, CNN...)
- **Tự động dịch**: Tin nước ngoài → Tiếng Việt
- **Phát hiện ngôn ngữ**: Không dịch nguồn tiếng Việt
- **HTML entities decode**: Hiển thị tiếng Việt chuẩn
- Tự động đăng tin mới mỗi 3 phút
- Chống trùng lặp tin thông minh

### 📅 Economic Calendar
- **Polling-based (3-minute loop)**: Bot polls Investing.com every 3 minutes to discover Medium/High impact events.
- **Investing.com scraper**: Lấy dữ liệu lịch kinh tế và chuyển về UTC+7 để hiển thị.
- **Timezone UTC+7**: Hiển thị giờ Việt Nam
- **Behavior**: Bot sends a daily summary at 07:00 UTC+7 and continuously polls for upcoming events. It will:
  - Post a pre-alert for events that fall within the configured pre-alert window (default: 30 minutes; adjustable via `ECONOMIC_PREALERT_MINUTES` in `.env`).
  - Post the actual/result only when Investing.com provides a non-"N/A" actual value.
  - Filter events: only Medium and High impact events are considered.
- **Configuration**: Set `ECONOMIC_PREALERT_MINUTES` in `.env` (1–1440 minutes). Example: `1440` for 24-hour test mode.
- Test commands: `!testcalendar`, `!schedulenow` (Admin only)

## 🚀 Cài đặt

### 1. Clone Repository

```bash
git clone <repository-url>
cd discord-bot
```

### 2. Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình Environment Variables

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Chỉnh sửa file `.env` với các thông tin của bạn:

```env
# Discord Bot Token (từ Discord Developer Portal)
# NOTE: The bot reads `DISCORD_TOKEN` from .env (see .env.example)
DISCORD_TOKEN=your_discord_bot_token_here

# API Keys (Optional - nếu sử dụng tính năng tương ứng)
SANTIMENT_API_KEY=your_santiment_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here

# Economic Calendar Configuration
# Pre-alert window: số phút trước event khi bot gửi thông báo pre-alert
# Mặc định: 30 | Min: 1 | Max: 1440 (24 giờ)
# Ví dụ: set 1440 cho test mode (bot sẽ gửi pre-alert cho events trong 24h tới)
ECONOMIC_PREALERT_MINUTES=30

# Google Translate API (Free tier từ deep-translator)
# Không cần API key - sử dụng deep-translator package
```

### 4. Tạo Discord Bot

1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications)
2. Tạo "New Application"
3. Vào tab "Bot" và tạo bot
4. Copy Bot Token và paste vào `.env`
5. Bật các Privileged Gateway Intents:
   - ✅ PRESENCE INTENT
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT
6. Vào tab "OAuth2" → "URL Generator":
   - Chọn scope: `bot`, `applications.commands`
   - Chọn quyền: `Administrator` (hoặc các quyền cần thiết)
   - Copy URL và mở để thêm bot vào server

### 5. Chạy Bot

```bash
python main_bot.py
```

## 📖 Hướng dẫn Sử dụng

### 🎮 Lệnh Chính: `/start`

Bot chỉ có **MỘT** lệnh slash chính: **`/start`** ⭐

```
Gõ: /start
     ↓
┌─────────────────────────────────────┐
│  🤖 Discord News Bot                │
│  ───────────────────────────────    │
│  Chọn chức năng bạn muốn sử dụng:  │
│                                     │
│  📰 [Quản lý Tin tức]              │
│  📅 [Economic Calendar]            │
└─────────────────────────────────────┘
```

---

### 📰 Quản lý Tin tức (🔐 Admin only)

Nhấn **[Quản lý Tin tức]** → Menu hiện ra:

#### 📊 Cài đặt kênh tin Glassnode
```
🎯 Chức năng:
  • On-chain analytics và research
  • Insights từ Glassnode platform
  • 🌐 Tự động dịch sang tiếng Việt
  
💡 Cách dùng: Chọn channel Discord để nhận tin
```

#### 🔗 Cài đặt kênh tin Santiment
```
🎯 Chức năng:
  • Dữ liệu on-chain analytics
  • Insights từ blockchain
  • 🌐 Tự động dịch sang tiếng Việt
  
💡 Cách dùng: Chọn channel để nhận tin phân tích
```

#### ⚡ Cài đặt kênh 5phutcrypto
```
🎯 Chức năng:
  • Tin tức crypto tiếng Việt 🇻🇳
  • Phân tích & hướng dẫn
  • Không cần dịch
  
💡 Cách dùng: Chọn channel để nhận tin Việt Nam
```

#### � Cài đặt kênh The Block
```
🎯 Chức năng:
  • Institutional-grade crypto news
  • Tin tức chuyên sâu thị trường crypto
  • 🌐 Tự động dịch sang tiếng Việt
  
💡 Cách dùng: Chọn channel để nhận tin The Block
```

#### �📅 Cài đặt Economic Calendar
```
🎯 Chức năng:
  • Lịch kinh tế tự động từ Investing.com
  • 🕐 Hiển thị giờ UTC+7 (Việt Nam)
  • 🔴 High & 🟠 Medium impact events
  • Chỉ hiển thị events trong tương lai
  
💡 Cách dùng: Chọn channel để nhận lịch kinh tế
```

#### 📡 Thêm RSS Feed mới
```
🎯 Chức năng:
  • Thêm nguồn tin tùy chỉnh
  • Hỗ trợ: VNExpress, BBC, CNN, Reuters...
  • 🌐 Tự động phát hiện ngôn ngữ và dịch
  
💡 Cách dùng:
  1️⃣ Nhấn "Thêm một RSS Feed mới"
  2️⃣ Nhập URL và tên nguồn tin
  3️⃣ Chọn channel để đăng tin
  ✅ Bot tự động xử lý!
```

#### 🗑️ Xóa RSS Feed
- Chọn RSS Feed từ danh sách
- Xác nhận xóa → Hoàn tất! ✅

#### 📋 Liệt kê các nguồn tin
- Xem tất cả nguồn đang hoạt động 📊
- Hiển thị channel cho mỗi nguồn 📍

---

### 📅 Economic Calendar (🔐 Admin only)

Nhấn **[Economic Calendar]** để cấu hình lịch kinh tế:

#### 📊 Cài đặt kênh Economic Calendar
```
🎯 Chức năng:
  • Lịch kinh tế tự động từ Investing.com
  • 🕐 Hiển thị giờ UTC+7 (Việt Nam)
  • 🔴 High & 🟠 Medium impact events
  • ⏰ Bot polls Investing.com every 3 minutes and sends a daily summary at 07:00 UTC+7.
  • ✅ Bot posts actual value ngay khi có (chỉ khi `actual` khác "N/A").
  • 🔄 The bot retries checking event results; exact retry windows may vary by configuration.
  
💡 Cách dùng: Chọn channel Discord để nhận lịch kinh tế
```

#### 🧪 Test Economic Calendar
```
💡 Admin Commands:
  • !testcalendar  - Show full calendar cho ngày hôm nay
  • !schedulenow   - Trigger scheduler ngay lập tức
```

**Note on scheduler**
- The project previously experimented with a dynamic scheduler that created per-event scheduled tasks. The current, stable implementation uses a polling loop (every 3 minutes) plus a daily summary at 07:00 UTC+7. Use `!schedulenow` to trigger a scheduler-like flow manually for testing.

---

### 🤖 Tin tức Tự động (Background)

Bot tự động kiểm tra và đăng tin mới mỗi **5 phút** ⏰:

| Nguồn | Tính năng | Dịch? |
|-------|-----------|-------|
| 📊 **Glassnode** | On-chain analytics | 🌐 Có |
| 🔗 **Santiment** | On-chain insights | 🌐 Có |
| ⚡ **5phutcrypto** | Tin tiếng Việt | ❌ Không |
| � **The Block** | Institutional news | 🌐 Có |
| �📅 **Economic Calendar** | Lịch kinh tế (UTC+7) | ❌ Không |
| 📡 **RSS Feeds** | Nguồn tùy chỉnh | 🌐 Auto-detect |

> **💡 Admin Tip**: Dùng lệnh `!testcalendar` để test Economic Calendar ngay lập tức (không cần đợi 3 phút)

## 📁 Cấu trúc Project

```
discord-bot/
├── main_bot.py                  # Entry point
├── cogs/
│   └── news_cog.py              # Tin tức & Economic Calendar
├── data/
│   ├── news_config.json         # Cấu hình per-guild
│   └── last_post_ids.json       # Tracking per-guild
├── docs/                        # Documentation
│   ├── README.md                # Main docs
│   ├── API_REFERENCE.md         # Technical details
│   ├── TROUBLESHOOTING.md       # Common issues
│   └── ...
├── scripts/                     # Utility scripts
│   ├── check_channels.py        # Verify channels
│   ├── verify_multi_guild_posts.py
│   └── ...
├── tests/                       # Test scripts
│   ├── test_calendar.py
│   ├── test_url_variants.py
│   └── ...
├── logs/                        # Log files (gitignored)
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Template
├── requirements.txt             # Dependencies
└── README.md                    # This file
```

## 🛠️ Tech Stack

- **discord.py** (v2.3.2+): Discord bot framework
- **python-dotenv**: Environment variables
- **aiohttp**: Async HTTP requests
- **feedparser**: RSS/Atom feeds parsing
- **BeautifulSoup4**: Web scraping (Economic Calendar)
- **pytz**: Timezone handling (UTC+7)
- **deep-translator**: Google Translate wrapper
- **html**: HTML entities decoding

## ⚙️ Background Tasks

Bot chạy background tasks tự động:

### 📰 News Checker (Mỗi 3 phút)
- Kiểm tra Glassnode Insights RSS
- Kiểm tra Santiment API
- Kiểm tra 5phutcrypto.io
- Kiểm tra The Block RSS
- Kiểm tra tất cả RSS Feeds
- Kiểm tra Economic Calendar (polling mỗi 3 phút)
- So sánh với `last_post_ids` per-guild để chống trùng
- Đăng tin mới vào kênh đã cấu hình
- **Multi-guild support**: Xử lý từng guild độc lập

### 📅 Economic Calendar (Daily Summary)
- Daily summary: sent at 07:00 UTC+7 covering today's Medium/High events.
- Per-event scheduling: the previous dynamic scheduler is disabled in favor of the polling loop; `!schedulenow` can be used to trigger fetch + summary + scheduling for tests.

### 📊 Daily Calendar Summary (7:00 AM UTC+7)
- Gửi tổng hợp lịch kinh tế cho cả ngày
- Categorize theo High/Medium impact
- Hiển thị country, event name, time

### 🕐 Timezone Handling
- **VN_TZ**: `Asia/Ho_Chi_Minh` (UTC+7)
- Economic Calendar: Convert UTC-5 (Investing.com) → UTC+7
- Hiển thị thời gian theo múi giờ Việt Nam
- Filter events: Chỉ hiển thị events trong tương lai

## 🌐 Multi-guild Support

Bot hỗ trợ nhiều Discord servers:

### Data Structure (per-guild)
```json
{
  "guilds": {
    "guild_id_1": {
      "glassnode_channel": 123456789,
      "santiment_channel": 123456789,
      "5phutcrypto_channel": 123456789,
      "theblock_channel": 123456789,
      "economic_calendar_channel": 123456789,
      "rss_feeds": [...]
    },
    "guild_id_2": {
      ...
    }
  }
}
```

### Features
- ✅ Mỗi guild có cấu hình riêng
- ✅ Tracking posts riêng cho mỗi guild
- ✅ Không xung đột dữ liệu giữa các guilds

## 🔒 Bảo mật

- ❌ **KHÔNG** commit file `.env` lên Git
- ✅ File `.env` đã được thêm vào `.gitignore`
- ✅ Tất cả API keys được load từ environment variables
- ✅ Chức năng quản lý tin tức yêu cầu quyền Administrator

## 🐛 Troubleshooting

### Bot không đăng tin
- Kiểm tra API keys trong `.env`
- Kiểm tra channels đã được cấu hình trong `data/news_config.json`
- Xem console logs để debug
- Đợi 3 phút cho vòng lặp tiếp theo
- Verify bot có quyền `Send Messages`, `Embed Links` trong channel

### Economic Calendar không có events
- Kiểm tra URL filtering: Bot fetch từ Investing.com với `?dateFrom={today}&dateTo={today}`
- Timezone: Events được convert từ UTC-5 sang UTC+7
- Filter: Chỉ hiển thị High & Medium impact
- Chỉ events trong tương lai (>= current time UTC+7)
- Sử dụng `!testcalendar` để test ngay

### RSS feed hiển thị lỗi chữ
- ✅ Đã fix: `html.unescape()` decode HTML entities
- Nếu vẫn lỗi: Kiểm tra encoding của RSS feed
- VNExpress, BBC, CNN đã được test thành công

### Không nhận tin từ nguồn tiếng Việt
- Bot tự động phát hiện: `vnexpress`, `vn` trong URL/name
- Không dịch nếu là tiếng Việt
- Kiểm tra feed URL có chính xác không

### Multi-guild issues
- Mỗi guild có file config riêng trong `data/news_config.json`
- Tracking posts riêng trong `data/last_post_ids.json`
- Sử dụng script `scripts/check_channels.py` để verify
- Sử dụng `scripts/verify_multi_guild_posts.py` để kiểm tra posts

### Lỗi import
```bash
pip install -r requirements.txt
# Hoặc
pip install discord.py python-dotenv aiohttp feedparser beautifulsoup4 pytz deep-translator
```

## 📝 License

MIT License - Tự do sử dụng và chỉnh sửa

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng:
1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

## 📧 Liên hệ

Nếu có vấn đề hoặc câu hỏi:
- Mở Issue trên GitHub
- Xem documentation trong folder `docs/`
- Check troubleshooting guide: `docs/TROUBLESHOOTING.md`

## 📚 Documentation

- **README.md** - Main documentation (this file)
- **docs/API_REFERENCE.md** - Technical details
- **docs/TROUBLESHOOTING.md** - Common issues & solutions
- **docs/PROJECT_OVERVIEW.md** - Architecture & structure
- **docs/CHANGELOG.md** - Version history

## 📝 Changelog

### Version 1.3.0 (November 6, 2025)

#### 🎯 Major Changes: Economic Calendar behavior

- ✅ Updated economic calendar flow: the project experimented with a dynamic per-event scheduler, but the stable implementation uses a polling loop (every 3 minutes) plus a daily summary at 07:00 UTC+7. This change improves robustness in environments where precise scheduling or long-lived tasks may be unreliable.
- ✅ The bot posts pre-alerts for upcoming Medium/High events (within the configured pre-alert window) and posts actual values only when Investing.com provides non-"N/A" results.
- ✅ Admin test command `!schedulenow` remains available to trigger an immediate fetch + summary + schedule flow for testing.

### Version 1.2.0 (November 6, 2025)

#### 🎉 New Features
- ✅ **The Block Integration**: Thêm nguồn tin The Block (institutional-grade crypto news)
  - RSS feed: https://www.theblock.co/rss.xml
  - Tự động dịch sang tiếng Việt
  - Dedicated channel configuration

#### 🐛 Bug Fixes
- ✅ **VNEconomy HTML Entities Fix**: Sửa lỗi hiển thị tiếng Việt
  - **Issue**: VNEconomy RSS feed sử dụng malformed HTML entities (`#225;` thay vì `&#225;`)
  - **Solution**: Thêm regex preprocessing `r'#(\d+);'` → `r'&#\1;'` trước khi `html.unescape()`
  - **Result**: Tiếng Việt hiển thị đúng (báo cáo, công ty, etc.)
  - Áp dụng cho tất cả Vietnamese RSS feeds

#### 🔄 API Changes
- ✅ Messari references removed — migrated to Glassnode (RSS)
  - Note: The repository no longer relies on the Messari paid Research API. Glassnode Insights (RSS) is used for on-chain research feeds where available.
  - Glassnode RSS: https://insights.glassnode.com/feed/

- ✅ **Santiment GraphQL Fix**: Cập nhật query structure
  - **Old**: `getNews` query (không tồn tại trong schema)
  - **New**: `allInsights` query với `readyState` filter
  - Working query với proper field selection

#### 🏗️ Infrastructure
- ✅ **Multi-guild Tracking**: Restructure `last_post_ids.json`
  - Thêm guild ID key ở top-level
  - Tracking riêng cho mỗi guild
  - Thêm `theblock` tracking array
  - Fix KeyError khi check The Block articles

#### 📖 Documentation
- ✅ Cập nhật README với tất cả nguồn tin mới
- ✅ Cập nhật `/start` embed command
- ✅ Thêm troubleshooting guide cho VNEconomy
- ✅ Repository rename: `discord-market-bot` → `vn-crypto-news-bot`

#### 🧪 Testing
- ✅ Test script: `test_vneconomy_rss.py` - Verify HTML entities fix
- ✅ Cleared VNEconomy tracking để force re-post articles
- ✅ Verified Vietnamese characters display correctly

### Version 1.1.0 (October 2025)
- ✅ Multi-guild support
- ✅ Economic Calendar (UTC+7)
- ✅ 5phutcrypto.io integration
- ✅ Auto translation with language detection

### Version 1.0.0 (Initial Release)
- ✅ Basic news aggregation
- ✅ RSS feeds support
- ✅ Discord slash commands

## 🎯 Features Roadmap

### Current (v1.0)
- ✅ Multi-guild support
- ✅ Economic Calendar (UTC+7)
- ✅ 5phutcrypto.io integration
- ✅ HTML entities decoding
- ✅ Auto translation to Vietnamese
- ✅ RSS feeds with language detection

### Future
- [ ] Dashboard web interface
- [ ] Analytics & statistics
- [ ] User preferences
- [ ] More economic data sources
- [ ] Portfolio tracking
- [ ] Trading signals

---

**Made with ❤️ for the Vietnamese crypto community**

**Repository**: https://github.com/Azunetrangia/vn-crypto-news-bot
