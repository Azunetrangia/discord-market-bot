# 🚀 Hướng dẫn Nhanh (Quick Start)

## Bước 1: Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

## Bước 2: Cấu hình Bot

1. Copy file `.env.example` thành `.env`:
```bash
cp .env.example .env
```

2. Chỉnh sửa file `.env` và điền các thông tin:

```env
DISCORD_TOKEN=your_discord_bot_token_here
# Glassnode Insights: no API key required, uses RSS at https://insights.glassnode.com/feed/
SANTIMENT_API_KEY=your_santiment_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here
```

### Lấy Discord Bot Token:
1. Vào https://discord.com/developers/applications
2. Tạo "New Application"
3. Vào tab "Bot" → Copy Token
4. Bật tất cả Privileged Gateway Intents
5. Vào "OAuth2" → "URL Generator" → Chọn `bot` + `applications.commands` → Chọn quyền `Administrator`
6. Copy URL và mở để thêm bot vào server

### Lấy API Keys:
- **Glassnode (RSS)**: https://insights.glassnode.com/feed/  (no API key required)
- **Santiment**: https://santiment.net/products-and-plans/sanapi
- **CoinGecko**: https://www.coingecko.com/en/api/pricing

## Bước 3: Chạy Bot

### Linux/Mac:
```bash
chmod +x start.sh
./start.sh
```

### Windows:
```cmd
start.bat
```

### Hoặc chạy trực tiếp:
```bash
python main_bot.py
```

## Bước 4: Sử dụng Bot

1. Trong Discord, gõ `/start`
2. Chọn chức năng bạn muốn:
   - **📰 Quản lý Tin tức** (Chỉ Admin)
   - **🔔 Quản lý Cảnh báo** (Mọi người)

## ✅ Kiểm tra Bot hoạt động

### Test Tin tức:
1. `/start` → Quản lý Tin tức
2. Chọn "Thêm một RSS Feed mới"
3. Nhập URL: `https://news.ycombinator.com/rss`
4. Tên: `Hacker News`
5. Chọn một kênh
6. Đợi 10 phút → Kiểm tra kênh

### Test Cảnh báo:
1. `/start` → Quản lý Cảnh báo
2. Chọn "Thêm Cảnh báo mới"
3. Ticker: `BTC`
4. Giá mục tiêu: Nhập giá thấp hơn giá hiện tại (để test nhanh)
5. Đợi tối đa 60 giây → Bot sẽ ping bạn với biểu đồ

## 📁 Cấu trúc Files

```
discord-bot/
├── main_bot.py           # File chính
├── cogs/                 # Các module chức năng
│   ├── news_cog.py      # Quản lý tin tức
│   └── alerts_cog.py    # Quản lý cảnh báo
├── data/                # Dữ liệu (tự động tạo)
│   ├── news_config.json
│   ├── last_post_ids.json
│   └── alerts.json
├── .env                 # Config (KHÔNG commit)
└── requirements.txt     # Dependencies
```

## 🐛 Gặp lỗi?

### Bot không online:
- Kiểm tra `DISCORD_TOKEN` trong `.env`
- Kiểm tra console có lỗi gì không

### Lệnh /start không hiện:
- Đợi 5-10 phút để Discord sync
- Restart bot
- Kick và add bot lại vào server

### Import error:
```bash
pip install --upgrade -r requirements.txt
```

## 📚 Xem thêm

Đọc file `README.md` để biết chi tiết về tất cả chức năng và cách sử dụng.
