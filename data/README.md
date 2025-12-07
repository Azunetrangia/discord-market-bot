# 💾 Data Directory

Thư mục này chứa các file JSON để lưu trữ dữ liệu của bot.

**Lưu ý:** Thư mục này sẽ được tạo tự động khi bot chạy lần đầu.

---

## 📁 Files

### 📋 news_config.json
**Mục đích:** Lưu cấu hình nguồn tin tức

**Structure:**
```json
{
  "glassnode_channel": 1234567890,
  "santiment_channel": 1234567891,
  "rss_feeds": [
    {
      "name": "Tin Vĩ Mô ABC",
      "url": "https://example.com/rss.xml",
      "channel_id": 1234567892
    }
  ]
}
```

**Fields:**
  "glassnode_channel": 1234567890,
- `santiment_channel`: ID kênh cho tin Santiment (null nếu chưa cài)
- `rss_feeds`: Array các RSS feed đã thêm
  - `name`: Tên hiển thị
  - `url`: URL của RSS feed
  - `channel_id`: ID kênh đăng tin

---

### 🔖 last_post_ids.json
**Mục đích:** Tracking các bài viết đã đăng (chống trùng lặp)

# 💾 Data Directory

This folder contains JSON files the bot uses for persisting configuration and
state. Files are created automatically on first run if they don't exist.

Files
-----

### `news_config.json`
Purpose: per-guild configuration for news sources and their target channels.

Example structure:

```json
{
  "guilds": {
    "123456789012345678": {
      "glassnode_channel": null,
      "santiment_channel": null,
      "5phutcrypto_channel": null,
      "theblock_channel": null,
      "economic_calendar_channel": null,
      "rss_feeds": []
    }
  }
}
```

### `last_post_ids.json`
Purpose: track posted IDs to prevent duplicates (per guild).

Example structure:

```json
{
  "guilds": {
    "123456789012345678": {
      "glassnode": [],
      "santiment": [],
      "5phutcrypto": [],
      "theblock": [],
      "economic_events": [],
      "rss": {}
    }
  }
}
```

Notes:
- The code limits stored IDs per source (typically to the latest 100) to keep the
  file small.

### `alerts.json`
Purpose: active price alerts created by users.

Example:

```json
[
  {
    "user_id": 123456789,
    "ticker": "bitcoin",
    "ticker_display": "BTC",
    "target_price": 69000.0,
    "channel_id": 987654321,
    "created_at": "2025-01-01T12:00:00"
  }
]
```

Maintenance & tips
------------------

- To reset last-post tracking (will allow old posts to be re-posted):

```bash
echo '{"guilds": {}}' > data/last_post_ids.json
```

- To clear all alerts:

```bash
echo '[]' > data/alerts.json
```

- Backup examples:

```bash
cp data/*.json backups/$(date +%Y%m%d)/
find backups/ -mtime +7 -delete
```

Troubleshooting
---------------

If files are missing, create them with safe defaults:

```bash
mkdir -p data
echo '{"guilds": {}}' > data/news_config.json
echo '{"guilds": {}}' > data/last_post_ids.json
echo '[]' > data/alerts.json
```

Validate JSON with `jq` if you run into parsing errors.

Security
--------

- Do not commit secrets to the repo. Keep `.env` out of version control.
- Consider periodic backups of `data/`.

Learn more
----------

- JSON: https://www.json.org/
- Python JSON: https://docs.python.org/3/library/json.html
