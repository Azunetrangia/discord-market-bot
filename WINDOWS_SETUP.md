# 🪟 Windows Setup Guide - Discord News Bot

Hướng dẫn chi tiết cài đặt và chạy bot trên Windows 10/11.

---

## 📋 Yêu cầu hệ thống

- **Windows 10/11** (64-bit)
- **Python 3.8+** (Khuyến nghị: Python 3.11)
- **Git for Windows** (optional, để clone repo)
- **8GB RAM** (tối thiểu 4GB)
- **100MB** dung lượng trống

---

## 🚀 Cài đặt từng bước

### Bước 1: Cài đặt Python

1. Download Python từ: https://www.python.org/downloads/
2. **QUAN TRỌNG:** Tick ✅ "Add Python to PATH" khi cài
3. Verify cài đặt:
```cmd
python --version
# Output: Python 3.11.x
```

### Bước 2: Clone Repository

**Option A: Dùng Git**
```cmd
git clone https://github.com/YOUR_USERNAME/discord-bot.git
cd discord-bot
```

**Option B: Download ZIP**
1. Download ZIP từ GitHub
2. Giải nén vào thư mục bạn muốn
3. Mở Command Prompt trong thư mục đó

### Bước 3: Tạo Virtual Environment

```cmd
python -m venv venv
venv\Scripts\activate

# Khi thành công sẽ thấy (venv) ở đầu dòng
```

### Bước 4: Cài đặt Dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

**Nếu gặp lỗi SSL/Certificate:**
```cmd
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

### Bước 5: Cấu hình Environment Variables

1. Copy file template:
```cmd
copy .env.example .env
```

2. Mở `.env` bằng Notepad:
```cmd
notepad .env
```

3. Điền các thông tin:
```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN_HERE
SANTIMENT_API_KEY=your_santiment_api_key_here

# Dashboard (optional)
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your_strong_password_here
DASHBOARD_SECRET_KEY=your_random_secret_key_here
```

4. Lưu và đóng file

### Bước 6: Tạo Thư mục Data

```cmd
mkdir data
mkdir logs
```

### Bước 7: Chạy Bot

```cmd
python main_bot.py
```

**Output thành công:**
```
🤖 Discord Bot Starting...
✅ Bot ready!
✅ Logged in as: YourBotName#1234
✅ Connected to X guilds
```

---

## 🌐 Chạy Dashboard (Optional)

### Mở terminal mới (giữ bot đang chạy)

```cmd
cd path\to\discord-bot
venv\Scripts\activate
python dashboard\app.py
```

### Truy cập Dashboard

Mở trình duyệt: **http://localhost:5000**

- Username: `admin` (hoặc theo .env)
- Password: `admin123` (hoặc theo .env)

---

## 🔧 Troubleshooting

### Lỗi: "python không được nhận dạng"

**Nguyên nhân:** Python chưa được thêm vào PATH

**Fix:**
1. Mở Settings → System → About → Advanced system settings
2. Environment Variables → Path → Edit
3. Thêm đường dẫn Python (VD: `C:\Users\YourName\AppData\Local\Programs\Python\Python311`)
4. Restart Command Prompt

### Lỗi: "No module named 'discord'"

**Fix:**
```cmd
venv\Scripts\activate
pip install discord.py
```

### Lỗi: "Permission denied"

**Fix:** Chạy Command Prompt as Administrator
- Right-click Command Prompt → Run as administrator

### Lỗi: "Address already in use" (Dashboard)

**Fix:** Đổi port trong `dashboard/app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5001)  # Đổi 5000 → 5001
```

### Bot disconnect liên tục

**Nguyên nhân:** Internet không ổn định hoặc token sai

**Fix:**
1. Check `.env` file, đảm bảo DISCORD_TOKEN đúng
2. Regenerate token trên Discord Developer Portal nếu cần

---

## 📱 Chạy Bot Khi Khởi động Windows

### Option 1: Task Scheduler

1. Mở Task Scheduler (Tìm "Task Scheduler" trong Start Menu)
2. Create Basic Task → Tên: "Discord News Bot"
3. Trigger: When I log on
4. Action: Start a program
   - Program: `C:\path\to\discord-bot\venv\Scripts\python.exe`
   - Arguments: `main_bot.py`
   - Start in: `C:\path\to\discord-bot`
5. Finish

### Option 2: Startup Folder

1. Tạo file `start_bot.bat`:
```batch
@echo off
cd /d C:\path\to\discord-bot
call venv\Scripts\activate
python main_bot.py
pause
```

2. Copy shortcut vào Startup folder:
   - Press `Win+R` → `shell:startup`
   - Paste shortcut vào đây

---

## 🌐 Public Dashboard với Ngrok (Windows)

### 1. Download Ngrok

https://ngrok.com/download (chọn Windows)

### 2. Giải nén và thêm vào PATH

Giải nén `ngrok.exe` vào `C:\ngrok\`

### 3. Authenticate

```cmd
ngrok config add-authtoken YOUR_NGROK_TOKEN
```

### 4. Start Tunnel

```cmd
ngrok http 5000
```

### 5. Copy Public URL

Output:
```
Forwarding https://abc123.ngrok-free.dev -> http://localhost:5000
```

Share URL `https://abc123.ngrok-free.dev` để truy cập từ thiết bị khác!

---

## 🔄 Update Bot

```cmd
cd discord-bot
git pull origin main
venv\Scripts\activate
pip install -r requirements.txt --upgrade
python main_bot.py
```

---

## 📊 Monitoring

### Check Bot Status

```cmd
tasklist | findstr python
```

### View Logs

```cmd
type logs\bot.log | more
```

### Database Size

```cmd
dir data\news_bot.db
```

---

## 🛑 Stop Bot

- **Cách 1:** Press `Ctrl+C` trong terminal đang chạy bot
- **Cách 2:** Task Manager → Find python.exe → End Task

---

## 🆘 Support

Gặp vấn đề? Check:

1. **Logs:** `logs\bot.log`
2. **GitHub Issues:** https://github.com/YOUR_REPO/issues
3. **Discord Server:** (nếu có)

---

## 📚 Resources

- **Discord.py Docs:** https://discordpy.readthedocs.io/
- **Python Windows Guide:** https://docs.python.org/3/using/windows.html
- **Git for Windows:** https://gitforwindows.org/
- **Ngrok Windows:** https://ngrok.com/docs/getting-started/?os=windows

---

**Last Updated:** 2025-12-07  
**Tested on:** Windows 11 22H2
