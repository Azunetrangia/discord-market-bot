# 🧪 Hướng Dẫn Test Bot Economic Calendar

## ✅ Bot đang chạy
- Process ID: Kiểm tra bằng `ps aux | grep main_bot.py`
- Log file: `/home/azune/Documents/coding/discord-bot/bot_console.log`

## 📋 Các lệnh test trong Discord

### 1. Test calendar fetch (không post lên channel)
Lệnh này chỉ lấy dữ liệu và hiển thị trong channel hiện tại, không trigger scheduler:

```
!testcalendar
```

**Kết quả mong đợi:**
- Bot sẽ lấy events từ Investing.com
- Hiển thị tất cả events Medium/High impact từ giờ hiện tại → cuối ngày
- Tạo embed với danh sách events

### 2. Trigger scheduler ngay (no pre-alert/backfill)
Lệnh này sẽ cancel tất cả tasks cũ và chạy scheduler mới ngay lập tức (fetch → summary → schedule per-event checks):

```
!schedulenow
```

**Kết quả mong đợi:**
- Bot sẽ lấy events trong phạm vi now → 04:30 next day và gửi daily summary + schedule per-event checks.
- Không có backfill hoặc pre-alerts: the scheduler does not post missed pre-event alerts.
- Hiển thị số tasks đã schedule

### 3. Xem cấu hình hiện tại
```
!newsconfig list
```

Hiển thị channel nào đã được cấu hình cho Economic Calendar.

### 4. Cấu hình channel Economic Calendar (nếu chưa có)
```
!newsconfig economic
```

Chọn channel để bot post economic calendar events.

## 📊 Giám sát logs real-time

Chạy script monitoring trong terminal:

```bash
cd /home/azune/Documents/coding/discord-bot
./scripts/monitor_bot.sh
```

Hoặc dùng tail trực tiếp:

```bash
tail -f bot_console.log | grep -E "(scheduler|Scheduled|BACKFILL|Economic|⏰|📊)"
```

## 🧪 Test Scenarios

### Scenario A: Daily summary + per-event checks
1. At 07:00 UTC+7 the bot sends a daily summary covering today's events (07:00 → 04:30 next day).
2. For a scheduled event at 14:00, the bot will run checks at:
	- 14:00 (T+0) — attempt posting for all events
	- 14:02 (T+2) — attempt for Medium & High
	- 14:05 (T+5) — attempt for High only
3. The bot posts the actual value only when available; once posted, further checks are skipped.

### Scenario B: Immediate scheduler trigger (no backfill)
1. Run `!schedulenow` to trigger the daily flow immediately.
2. The bot will fetch events, send the summary, and schedule per-event checks. It will not post missed pre-event alerts.

### Scenario C: Event already passed
1. If an event time is already past the check window, `!schedulenow` will skip that event (no posting).

## 📝 Log Messages cần chú ý

Khi scheduler chạy, bạn sẽ thấy:

```
⏰ Economic Calendar before_loop: running initial scheduling at YYYY-MM-DD HH:MM:SS
📊 Found XX economic events from Investing.com
✅ Scraped XX relevant economic events
```

Khi schedule event:
```
⏰ Scheduled pre-alert for [Event Name] at HH:MM
📊 Scheduled actual check for [Event Name] at HH:MM
```

Khi backfill:
```
⏰ [BACKFILL] Posted missed pre-alert for [Event Name] to [Guild Name]
```

Khi post actual:
```
✅ Posted actual value for [Event Name] to [Guild Name]
```

## 🔍 Debug Commands

Kiểm tra bot process:
```bash
ps aux | grep main_bot.py
```

Xem log gần đây:
```bash
tail -100 bot_console.log
```

Restart bot:
```bash
pkill -f main_bot.py
cd /home/azune/Documents/coding/discord-bot
nohup python main_bot.py > bot_console.log 2>&1 &
```

## ⚡ Quick Test Now

1. Mở Discord server nơi bot đang hoạt động
2. Gõ: `!testcalendar` để xem events hôm nay
3. Gõ: `!schedulenow` để trigger scheduler với backfill
4. Xem channel Economic Calendar để kiểm tra có tin gì được post không

## 📌 Notes

- Bot chạy scheduler tự động mỗi ngày lúc 00:00 UTC+7
- Pre-alert được gửi trước event (mặc định 30 phút). NOTE: Trong môi trường test, window pre-alert có thể được mở rộng để thuận tiện.
- Actual checks chạy tại T+0, T+5, T+10 phút sau event
- Backfill chỉ chạy khi bot khởi động hoặc khi gọi `!schedulenow`
