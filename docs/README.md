# 🤖 Discord News Bot

Bot Discord chuyên nghiệp tổng hợp tin tức kinh tế & crypto tự động với timezone UTC+7:
- 📰 **Tin tức Đa nguồn**: Glassnode (RSS), Santiment, 5phutcrypto, RSS Feeds
- 📅 **Economic Calendar**: Lịch kinh tế từ Investing.com (UTC+7)
- 🌐 **Dịch tự động**: Tự động dịch tin nước ngoài sang tiếng Việt
- 🎨 **Multi-guild Support**: Hỗ trợ nhiều Discord servers cùng lúc
- 🕐 **Timezone UTC+7**: Hiển thị giờ Việt Nam cho tất cả events

## ✨ Tính năng nổi bật

-### 📰 Quản lý Tin tức
- Tích hợp Glassnode Insights (RSS) cho tin tức & phân tích on-chain
- Tích hợp Santiment API cho phân tích on-chain
- Hỗ trợ thêm nhiều RSS Feeds tùy chỉnh (VNExpress, BBC, CNN, Reuters...)
- **Tự động dịch sang tiếng Việt** cho tin nước ngoài
- **Phát hiện tiếng Việt**: Không dịch các nguồn như VNExpress
- Tự động đăng tin mới mỗi 10 phút
- Chống trùng lặp tin thông minh
- Quản lý dễ dàng qua giao diện tương tác
- Hiển thị cả bản dịch và bản gốc

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
DISCORD_TOKEN=your_discord_bot_token_here

# Santiment API Key (https://santiment.net/products-and-plans/sanapi)
SANTIMENT_API_KEY=your_santiment_api_key_here

# CoinGecko API Key (https://www.coingecko.com/en/api/pricing)
COINGECKO_API_KEY=your_coingecko_api_key_here
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

### Lệnh Duy nhất: `/start`

Bot chỉ có **MỘT** lệnh slash duy nhất: `/start`

Tất cả chức năng được truy cập qua giao diện tương tác (Buttons, Select Menus, Modals).

### 📰 Quản lý Tin tức (Chỉ Admin)

1. Gõ `/start` trong Discord
2. Nhấn button **[Quản lý Tin tức]**
3. Chọn một trong các tùy chọn:

#### Cài đặt kênh tin Glassnode (RSS)
- Chọn kênh Discord để nhận tin từ Glassnode Insights (RSS)
- Tin tức sẽ tự động đăng mỗi 10 phút

#### Cài đặt kênh tin Santiment
- Chọn kênh Discord để nhận tin từ Santiment API
- Phân tích on-chain và insights tự động

#### Thêm RSS Feed mới
1. Bot hiển thị Modal hỏi:
   - URL của RSS Feed
   - Tên nguồn tin (hiển thị trong embed)
2. Sau khi submit, chọn kênh để đăng tin
3. Bot sẽ tự động kiểm tra và đăng tin mới

#### Xóa RSS Feed
- Chọn RSS Feed từ danh sách
- Xác nhận xóa

#### Liệt kê các nguồn tin
- Xem tất cả nguồn tin đang hoạt động
- Hiển thị kênh đích cho mỗi nguồn

### 🔔 Quản lý Cảnh báo (Mọi người dùng)

1. Gõ `/start` trong Discord
2. Nhấn button **[Quản lý Cảnh báo]**
3. Chọn một trong các tùy chọn:

#### Thêm Cảnh báo mới
1. Bot hiển thị Modal hỏi:
   - **Ticker**: Mã coin (VD: `BTC`, `ETH`, `SOL`)
   - **Giá mục tiêu**: Giá bạn muốn nhận thông báo (VD: `69000`)
2. Bot sẽ xác nhận và lưu cảnh báo
3. Khi giá đạt mục tiêu:
   - Bot ping bạn trong kênh
   - Gửi embed với thông tin giá
   - Kèm biểu đồ 7 ngày
   - Tự động xóa cảnh báo

#### Liệt kê Cảnh báo của tôi
- Xem tất cả cảnh báo đang hoạt động
- Hiển thị giá mục tiêu, kênh, thời gian tạo

#### Xóa Cảnh báo
- Chọn cảnh báo từ danh sách
- Xác nhận xóa

## 🎯 Ticker Hỗ trợ

Bot hỗ trợ các ticker phổ biến (tự động map sang CoinGecko ID):

| Ticker | Coin | Ticker | Coin |
|--------|------|--------|------|
| BTC | Bitcoin | ETH | Ethereum |
| BNB | Binance Coin | SOL | Solana |
| XRP | Ripple | ADA | Cardano |
| DOGE | Dogecoin | DOT | Polkadot |
| MATIC | Polygon | AVAX | Avalanche |
| LINK | Chainlink | UNI | Uniswap |
| ATOM | Cosmos | LTC | Litecoin |
| ETC | Ethereum Classic | | |

**Lưu ý**: Bạn cũng có thể sử dụng CoinGecko ID trực tiếp (VD: `bitcoin`, `ethereum`)

## 📁 Cấu trúc Project

```
discord-bot/
├── main_bot.py              # File chính, lệnh /start
├── cogs/
│   ├── news_cog.py          # Cog quản lý tin tức
│   └── alerts_cog.py        # Cog quản lý cảnh báo
├── data/
│   ├── news_config.json     # Cấu hình nguồn tin
│   ├── last_post_ids.json   # Lưu ID tin đã đăng (chống trùng)
│   └── alerts.json          # Lưu danh sách cảnh báo
├── .env                     # Environment variables (GIT IGNORE)
├── .env.example             # Template cho .env
├── requirements.txt         # Python dependencies
└── README.md               # File này
```

## 🛠️ Tech Stack

- **discord.py** (v2.3.2+): Discord bot framework
- **python-dotenv**: Quản lý environment variables
- **aiohttp**: Async HTTP requests
- **feedparser**: Parse RSS/Atom feeds
- **matplotlib**: Vẽ biểu đồ giá
- **pycoingecko**: CoinGecko API wrapper

## ⚙️ Background Tasks

Bot chạy 2 background tasks tự động:

-### 📰 News Checker (Mỗi 10 phút)
- Kiểm tra Glassnode RSS
- Kiểm tra Santiment API
- Kiểm tra tất cả RSS Feeds
- So sánh với last_post_ids để chống trùng
- Đăng tin mới vào kênh đã cấu hình

### 🔔 Price Checker (Mỗi 60 giây)
- Load tất cả cảnh báo
- Lấy giá từ CoinGecko (batch request)
- So sánh giá hiện tại với target
- Nếu đạt mục tiêu:
  - Vẽ biểu đồ 7 ngày
  - Gửi thông báo + ping user
  - Xóa cảnh báo

## 🔒 Bảo mật

- ❌ **KHÔNG** commit file `.env` lên Git
- ✅ File `.env` đã được thêm vào `.gitignore`
- ✅ Tất cả API keys được load từ environment variables
- ✅ Chức năng quản lý tin tức yêu cầu quyền Administrator

## 🐛 Troubleshooting

### Bot không phản hồi lệnh `/start`
- Kiểm tra bot đã được thêm vào server chưa
- Kiểm tra bot có quyền "Use Application Commands"
- Đợi vài phút để Discord sync commands
- Restart bot và thử lại

### Không nhận được tin tức
- Kiểm tra API keys trong `.env` có đúng không
- Kiểm tra kênh đã được cài đặt chưa
- Xem console log để debug errors
- Đợi 10 phút cho vòng lặp tiếp theo

### Cảnh báo không kích hoạt
- Kiểm tra `COINGECKO_API_KEY` có đúng không
- Kiểm tra ticker có đúng không (dùng `/start` → Liệt kê)
- Đợi tối đa 60 giây cho vòng lặp kiểm tra
- Xem console log để debug

### Lỗi import matplotlib
```bash
# Linux/Mac
pip install matplotlib

# Windows
pip install matplotlib
# Nếu lỗi, cài Visual C++ Build Tools
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

Nếu có vấn đề hoặc câu hỏi, vui lòng mở Issue trên GitHub.

---

**Made with ❤️ using discord.py**
