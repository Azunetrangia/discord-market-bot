#!/bin/bash

# Script để khởi động bot Discord

echo "🤖 Đang khởi động Discord Bot..."

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 chưa được cài đặt!"
    exit 1
fi

# Kiểm tra file .env
if [ ! -f .env ]; then
    echo "❌ File .env không tồn tại!"
    echo "📝 Hãy tạo file .env từ .env.example"
    exit 1
fi

# Kiểm tra thư mục data
if [ ! -d data ]; then
    echo "📁 Tạo thư mục data..."
    mkdir data
fi

# Kiểm tra các file JSON
if [ ! -f data/news_config.json ]; then
    echo '{"glassnode_channel": null, "santiment_channel": null, "rss_feeds": []}' > data/news_config.json
fi

if [ ! -f data/last_post_ids.json ]; then
    echo '{"glassnode": [], "santiment": [], "rss": {}}' > data/last_post_ids.json
fi

if [ ! -f data/alerts.json ]; then
    echo '[]' > data/alerts.json
fi

# Chạy bot
echo "✅ Khởi động bot..."
python3 main_bot.py
