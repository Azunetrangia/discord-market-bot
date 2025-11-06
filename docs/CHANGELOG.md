# Changelog

Tất cả các thay đổi quan trọng của project sẽ được ghi lại ở đây.

## [1.0.0] - 2025-01-01

### 🎉 Phiên bản đầu tiên

#### ✨ Tính năng

**Core System:**
- ✅ Lệnh `/start` duy nhất với giao diện tương tác đầy đủ
- ✅ Hệ thống Cogs để tổ chức code (news_cog.py, alerts_cog.py)
- ✅ Persistent Views với timeout management
- ✅ Modal forms cho nhập liệu

**📰 Quản lý Tin tức (News Management):**
- ✅ Tích hợp Messari API
- ✅ Tích hợp Santiment API (GraphQL)
- ✅ Hỗ trợ nhiều RSS Feeds tùy chỉnh
- ✅ Background task tự động kiểm tra tin mới (10 phút)
- ✅ Hệ thống chống trùng lặp tin
- ✅ Channel selection per source
- ✅ CRUD operations qua UI:
  - Cài đặt kênh cho Messari
  - Cài đặt kênh cho Santiment
  - Thêm RSS Feed (với Modal)
  - Xóa RSS Feed (với Select Menu)
  - Liệt kê tất cả nguồn tin

**🔔 Cảnh báo Giá (Price Alerts):**
- ✅ Tích hợp CoinGecko API (với API Key)
- ✅ Hỗ trợ 15+ ticker phổ biến (auto-mapping)
- ✅ Background task kiểm tra giá (60 giây)
- ✅ Batch API requests để optimize performance
- ✅ Tự động vẽ biểu đồ 7 ngày với Matplotlib
- ✅ Ping người dùng khi cảnh báo kích hoạt
- ✅ CRUD operations qua UI:
  - Thêm cảnh báo (với Modal validation)
  - Liệt kê cảnh báo của user
  - Xóa cảnh báo (với Select Menu)
- ✅ Per-user alert management
- ✅ Per-channel notification

**📊 Data Persistence:**
- ✅ JSON-based storage system
- ✅ news_config.json - Cấu hình nguồn tin
- ✅ last_post_ids.json - Tracking posted articles
- ✅ alerts.json - Active price alerts
- ✅ Auto-cleanup (max 100 IDs per source)

**🎨 UI/UX:**
- ✅ Rich embeds với màu sắc phân biệt
- ✅ Ephemeral messages cho privacy
- ✅ Select Menus với descriptions
- ✅ Modal forms với validation
- ✅ ChannelSelect cho easy setup
- ✅ Error handling với user-friendly messages

**📈 Charts & Visualization:**
- ✅ Matplotlib integration với Agg backend
- ✅ 7-day price charts
- ✅ Target price line visualization
- ✅ Current price marker
- ✅ Auto-generated và auto-cleanup
- ✅ Professional styling (seaborn theme)

#### 🛠️ Technical

**Dependencies:**
- discord.py >= 2.3.2
- python-dotenv >= 1.0.0
- aiohttp >= 3.9.0
- feedparser >= 6.0.10
- matplotlib >= 3.8.0
- pycoingecko >= 3.1.0

**Architecture:**
- Async/await pattern throughout
- Cogs-based modular design
- Background tasks with proper lifecycle
- Environment-based configuration
- Error handling at all levels

**Security:**
- Environment variables for all secrets
- .gitignore configured
- Admin-only news management
- Input validation for all user inputs
- No sensitive data in logs

#### 📚 Documentation

- ✅ README.md - Comprehensive guide
- ✅ QUICKSTART.md - Quick setup guide
- ✅ API_REFERENCE.md - Technical details
- ✅ Inline code comments
- ✅ .env.example with all required keys

#### 🚀 DevOps

- ✅ start.sh - Linux/Mac startup script
- ✅ start.bat - Windows startup script
- ✅ requirements.txt
- ✅ .gitignore
- ✅ Proper directory structure

#### 🎯 Supported Tickers

BTC, ETH, BNB, SOL, XRP, ADA, DOGE, DOT, MATIC, AVAX, LINK, UNI, ATOM, LTC, ETC

---

## Future Plans

### Version 1.1.0 (Planned)
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Multi-server support
- [ ] User preferences storage
- [ ] Alert history tracking
- [ ] More chart timeframes (1h, 24h, 30d)
- [ ] TradingView charts integration
- [ ] Webhook support for custom integrations

### Version 1.2.0 (Planned)
- [ ] Portfolio tracking
- [ ] Multiple alert conditions (>, <, >=, <=, %)
- [ ] Recurring alerts
- [ ] Alert snooze functionality
- [ ] News sentiment analysis
- [ ] More API sources (CryptoCompare, etc.)

### Version 2.0.0 (Planned)
- [ ] Web dashboard
- [ ] Analytics & statistics
- [ ] Machine learning price predictions
- [ ] Custom indicators
- [ ] Trading signals
- [ ] DeFi protocol integration

---

## Known Issues

### Version 1.0.0
- Matplotlib warnings về backend (harmless, can be ignored)
- Long RSS URLs truncated in embed descriptions
- Chart generation có thể chậm trên server yếu

### Workarounds
- Use API keys để tăng rate limits
- Monitor console logs để debug
- Đảm bảo Python >= 3.8

---

## Breaking Changes

Không có (phiên bản đầu tiên)

---

## Contributors

- Developer: [Your Name]
- Framework: discord.py
- APIs: Messari, Santiment, CoinGecko

---

## License

MIT License

---

**How to Update:**
```bash
git pull
pip install --upgrade -r requirements.txt
python main_bot.py
```
