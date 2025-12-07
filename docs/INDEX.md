# 📚 Documentation Index

Chào mừng đến với Discord Bot documentation! Chọn tài liệu phù hợp với nhu cầu của bạn.

---

## 🚀 Bắt đầu Nhanh

### Cho người dùng mới:
1. **[QUICKSTART.md](QUICKSTART.md)** - Hướng dẫn cài đặt nhanh 5 phút ⚡
2. **[README.md](README.md)** - Hướng dẫn đầy đủ về tất cả tính năng 📖

### Khi gặp vấn đề:
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Giải quyết lỗi thường gặp 🔧

---

## 👨‍💻 Cho Developers

### Hiểu kiến trúc:
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Tổng quan về project, cấu trúc, data flow 🏗️
- **[API_REFERENCE.md](API_REFERENCE.md)** - Chi tiết technical: APIs, code, performance 📡
- **[SUMMARY.md](SUMMARY.md)** - Tóm tắt toàn bộ project trong 1 file 📋

### Theo dõi thay đổi:
- **[CHANGELOG.md](CHANGELOG.md)** - Lịch sử phiên bản và thay đổi 📝

---

## 📂 File Structure

```
discord-bot/
│
├── 📖 Documentation (Bạn đang ở đây!)
│   ├── INDEX.md              ← 📍 Bạn đang đọc file này
│   ├── README.md             → Hướng dẫn chính
│   ├── QUICKSTART.md         → Setup nhanh
│   ├── TROUBLESHOOTING.md    → Giải quyết lỗi
│   ├── PROJECT_OVERVIEW.md   → Kiến trúc project
│   ├── API_REFERENCE.md      → Chi tiết technical
│   ├── SUMMARY.md            → Tóm tắt project
│   └── CHANGELOG.md          → Lịch sử versions
│
├── 🤖 Bot Code
│   ├── main_bot.py           → Entry point, /start command
│   ├── bot.py                → Convenience wrapper
│   └── cogs/
│       ├── news_cog.py       → Quản lý tin tức
│       └── alerts_cog.py     → Quản lý cảnh báo
│
├── ⚙️ Configuration
│   ├── .env.example          → Template cho API keys
│   ├── .gitignore            → Git ignore rules
│   ├── requirements.txt      → Python dependencies
│   └── LICENSE               → MIT License
│
├── 💾 Data (Auto-created)
│   ├── news_config.json      → News sources config
│   ├── last_post_ids.json    → Posted articles tracking
│   └── alerts.json           → Active price alerts
│
└── 🚀 Scripts
    ├── start.sh              → Linux/Mac launcher
    └── start.bat             → Windows launcher
```

---

## 🎯 Quick Navigation

### Tôi muốn...

#### ...cài đặt bot lần đầu
→ **[QUICKSTART.md](QUICKSTART.md)** hoặc **[README.md](README.md) § Cài đặt**

#### ...hiểu cách sử dụng bot
→ **[README.md](README.md) § Hướng dẫn Sử dụng**

#### ...sửa lỗi
→ **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

#### ...hiểu code hoạt động thế nào
→ **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** + **[API_REFERENCE.md](API_REFERENCE.md)**

#### ...đóng góp code
→ **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) § Contributing**

#### ...biết bot có những gì
→ **[SUMMARY.md](SUMMARY.md)**

#### ...tìm API endpoints
→ **[API_REFERENCE.md](API_REFERENCE.md)**

#### ...xem lịch sử updates
→ **[CHANGELOG.md](CHANGELOG.md)**

---

## 📊 Documentation Stats

| File | Lines | Purpose |
|------|-------|---------|
| README.md | ~500 | Main documentation |
| QUICKSTART.md | ~150 | Quick setup |
| TROUBLESHOOTING.md | ~1000 | Error solutions |
| PROJECT_OVERVIEW.md | ~600 | Architecture |
| API_REFERENCE.md | ~1000 | Technical details |
| SUMMARY.md | ~400 | Project summary |
| CHANGELOG.md | ~200 | Version history |
| INDEX.md | ~100 | This file |

**Total:** ~4,000 lines of documentation

---

## 🎓 Learning Path

### Beginner → Advanced

1. **Start:** [QUICKSTART.md](QUICKSTART.md)
   - Cài đặt bot trong 5 phút
   - Chạy bot lần đầu
   - Test các chức năng cơ bản

2. **Learn:** [README.md](README.md)
   - Hiểu tất cả tính năng
   - Học cách sử dụng UI
   - Cấu hình news & alerts

3. **Troubleshoot:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
   - Fix common errors
   - Debug issues
   - Optimize performance

4. **Deep Dive:** [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
   - Hiểu kiến trúc
   - Data flow
   - Design decisions

5. **Master:** [API_REFERENCE.md](API_REFERENCE.md)
   - API endpoints
   - Code patterns
   - Advanced usage

6. **Contribute:** Start coding!
   - Extend features
   - Fix bugs
   - Improve docs

---

## 📱 Quick Reference Cards

### Commands
```
/start  →  Khởi động bot, truy cập tất cả chức năng
```

### UI Flow
```
/start
  ├─ [Quản lý Tin tức] (Admin only)
   │   ├─ Cài đặt kênh Glassnode
  │   ├─ Cài đặt kênh Santiment
  │   ├─ Thêm RSS Feed
  │   ├─ Xóa RSS Feed
  │   └─ Liệt kê nguồn tin
  │
  └─ [Quản lý Cảnh báo]
      ├─ Thêm Cảnh báo
      ├─ Liệt kê Cảnh báo
      └─ Xóa Cảnh báo
```

### Files
```
Code:     main_bot.py, cogs/*.py
Config:   .env, requirements.txt
Data:     data/*.json
Docs:     *.md files
Scripts:  start.sh, start.bat
```

### APIs
```
Glassnode (RSS):    https://insights.glassnode.com/feed/
Santiment:          api.santiment.net/graphql
CoinGecko:          api.coingecko.com/api/v3/*
```

---

## 🔍 Search Guide

### Tìm thông tin về...

**Setup & Configuration:**
- `.env` → README.md § Cài đặt
- API keys → QUICKSTART.md § Bước 2
- Dependencies → requirements.txt + README.md § Cài đặt

**Features:**
- News management → README.md § Quản lý Tin tức
- Price alerts → README.md § Quản lý Cảnh báo
- Background tasks → API_REFERENCE.md § Background Tasks

**Code:**
- Views & UI → PROJECT_OVERVIEW.md § User Interactions
- API calls → API_REFERENCE.md § API Integrations
- Data storage → API_REFERENCE.md § Data Persistence

**Errors:**
- Any error message → TROUBLESHOOTING.md (search by error)
- Network issues → TROUBLESHOOTING.md § Network Errors
- Permission errors → TROUBLESHOOTING.md § Permission Errors

**APIs:**
- Glassnode → API_REFERENCE.md § Glassnode (RSS)
- Santiment → API_REFERENCE.md § Santiment API
- CoinGecko → API_REFERENCE.md § CoinGecko API
- RSS → API_REFERENCE.md § RSS Feeds

---

## 💡 Pro Tips

### Reading Strategy:

1. **First time user?**
   - QUICKSTART.md (5 min)
   - Test bot
   - Back to README.md for details

2. **Got an error?**
   - Go straight to TROUBLESHOOTING.md
   - Search for error message
   - Follow steps

3. **Want to modify code?**
   - PROJECT_OVERVIEW.md (understand structure)
   - API_REFERENCE.md (find code examples)
   - Start coding!

4. **Just exploring?**
   - SUMMARY.md (quick overview)
   - README.md (full tour)
   - PROJECT_OVERVIEW.md (deep dive)

---

## 📞 Get Help

**Documentation:**
1. Search this INDEX for topic
2. Go to relevant .md file
3. Use Ctrl+F to search within file

**Still stuck?**
- Check TROUBLESHOOTING.md
- Read error message carefully
- Look in console logs
- Create GitHub Issue (if repo available)
- Ask in discord.py Discord server

**Before asking:**
- [ ] Read relevant docs
- [ ] Checked TROUBLESHOOTING.md
- [ ] Tried restart
- [ ] Verified .env config
- [ ] Checked console logs

---

## 🎉 You're Ready!

Choose your path:

- 🆕 **New user?** → [QUICKSTART.md](QUICKSTART.md)
- 📖 **Want full guide?** → [README.md](README.md)
- 🔧 **Have issues?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 👨‍💻 **Developer?** → [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- 📊 **Quick overview?** → [SUMMARY.md](SUMMARY.md)

**Happy bot building! 🚀**

---

## 📝 Document Versions

| File | Last Updated | Status |
|------|--------------|--------|
| INDEX.md | 2025-01-01 | ✅ Current |
| README.md | 2025-01-01 | ✅ Current |
| QUICKSTART.md | 2025-01-01 | ✅ Current |
| TROUBLESHOOTING.md | 2025-01-01 | ✅ Current |
| PROJECT_OVERVIEW.md | 2025-01-01 | ✅ Current |
| API_REFERENCE.md | 2025-01-01 | ✅ Current |
| SUMMARY.md | 2025-01-01 | ✅ Current |
| CHANGELOG.md | 2025-01-01 | ✅ Current |

**All docs synced with code version 1.0.0**

---

**Need to update docs?** Edit the relevant .md file and update the "Last Updated" date above.
