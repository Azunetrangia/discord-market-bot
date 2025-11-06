# 🤖 Discord News Bot

Bot Discord chuyên nghiệp tổng hợp tin tức kinh tế & crypto tự động với timezone UTC+7:
- 📰 **Tin tức Đa nguồn**: Messari, Santiment, 5phutcrypto, RSS Feeds
- 📅 **Economic Calendar**: Lịch kinh tế từ Investing.com (UTC+7)
- 🌐 **Dịch tự động**: Tự động dịch tin nước ngoài sang tiếng Việt
- 🎨 **Multi-guild Support**: Hỗ trợ nhiều Discord servers cùng lúc
- 🕐 **Timezone UTC+7**: Hiển thị giờ Việt Nam cho tất cả events

## ✨ Tính năng nổi bật

### 📰 Tin tức Crypto & Kinh tế
- **Messari API**: Tin tức crypto market real-time
- **Santiment API**: Phân tích on-chain và insights
- **5phutcrypto.io**: Tin tức & phân tích tiếng Việt
- **RSS Feeds**: Thêm nguồn tùy chỉnh (VNExpress, BBC, CNN...)
- **Tự động dịch**: Tin nước ngoài → Tiếng Việt
- **Phát hiện ngôn ngữ**: Không dịch nguồn tiếng Việt
- **HTML entities decode**: Hiển thị tiếng Việt chuẩn
- Tự động đăng tin mới mỗi 5 phút
- Chống trùng lặp tin thông minh

### 📅 Economic Calendar
- **Investing.com scraper**: Lịch kinh tế tự động
- **Timezone UTC+7**: Hiển thị giờ Việt Nam
- **Filter Impact**: Chỉ High & Medium events
- **Future events only**: Lọc events trong tương lai
- **Date filtering**: URL parameters cho dữ liệu chính xác
- Test command: `!testcalendar` (Admin only)

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
DISCORD_BOT_TOKEN=your_discord_bot_token_here

# API Keys (Optional - nếu sử dụng tính năng tương ứng)
MESSARI_API_KEY=your_messari_api_key_here
SANTIMENT_API_KEY=your_santiment_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here

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

#### 📊 Cài đặt kênh tin Messari
```
🎯 Chức năng:
  • Tin tức crypto market real-time
  • Phân tích thị trường chuyên sâu
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

#### 📅 Cài đặt Economic Calendar
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
  • Chỉ hiển thị events trong tương lai
  
💡 Cách dùng: Chọn channel Discord để nhận lịch kinh tế
```

#### 🧪 Test Economic Calendar
```
💡 Admin Command: !testcalendar
  • Test ngay lập tức (không cần đợi 5 phút)
  • Kiểm tra dữ liệu từ Investing.com
  • Xác minh timezone UTC+7
```

---

### 🤖 Tin tức Tự động (Background)

Bot tự động kiểm tra và đăng tin mới mỗi **5 phút** ⏰:

| Nguồn | Tính năng | Dịch? |
|-------|-----------|-------|
| 📊 **Messari** | Crypto market news | 🌐 Có |
| 🔗 **Santiment** | On-chain analytics | 🌐 Có |
| ⚡ **5phutcrypto** | Tin tiếng Việt | ❌ Không |
| 📅 **Economic Calendar** | Lịch kinh tế (UTC+7) | ❌ Không |
| 📡 **RSS Feeds** | Nguồn tùy chỉnh | 🌐 Auto-detect |

> **💡 Admin Tip**: Dùng lệnh `!testcalendar` để test Economic Calendar ngay lập tức (không cần đợi 5 phút)

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

### 📰 News Checker (Mỗi 5 phút)
- Kiểm tra Messari API
- Kiểm tra Santiment API
- Kiểm tra 5phutcrypto.io
- Kiểm tra tất cả RSS Feeds
- Kiểm tra Economic Calendar (Investing.com)
- So sánh với `last_post_ids` per-guild để chống trùng
- Đăng tin mới vào kênh đã cấu hình
- **Multi-guild support**: Xử lý từng guild độc lập

### � Timezone Handling
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
      "messari_channel": 123456789,
      "santiment_channel": 123456789,
      "5phutcrypto_channel": 123456789,
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
- Đợi 5 phút cho vòng lặp tiếp theo
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

**Repository**: https://github.com/Azunetrangia/discord-market-bot
