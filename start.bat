@echo off
REM Script để khởi động bot Discord trên Windows

echo 🤖 Đang khởi động Discord Bot...

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    pause
    exit /b 1
)

REM Kiểm tra file .env
if not exist .env (
    echo ❌ File .env không tồn tại!
    echo 📝 Hãy tạo file .env từ .env.example
    pause
    exit /b 1
)

REM Kiểm tra thư mục data
if not exist data (
    echo 📁 Tạo thư mục data...
    mkdir data
)

REM Kiểm tra các file JSON
if not exist data\news_config.json (
    echo {"glassnode_channel": null, "santiment_channel": null, "rss_feeds": []} > data\news_config.json
)

if not exist data\last_post_ids.json (
    echo {"glassnode": [], "santiment": [], "rss": {}} > data\last_post_ids.json
)

if not exist data\alerts.json (
    echo [] > data\alerts.json
)

REM Chạy bot
echo ✅ Khởi động bot...
python main_bot.py

pause
