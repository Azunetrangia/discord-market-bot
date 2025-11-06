import asyncio
from bs4 import BeautifulSoup
import aiohttp
from datetime import datetime, timedelta
import pytz

async def test_fetch():
    url = "https://www.investing.com/economic-calendar/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    now_vn = datetime.now(vietnam_tz)
    today_vn = now_vn.date()
    
    print(f"📅 Now in UTC+7: {now_vn.strftime('%Y-%m-%d %H:%M')}")
    print(f"📅 Today: {today_vn}")
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                rows = soup.find_all('tr', {'class': 'js-event-item'})
                print(f"📊 Found {len(rows)} total events from HTML")
                
                events_today = []
                events_future = []
                events_past = []
                
                # Check ALL rows, not just 20
                for i, row in enumerate(rows):
                    event_datetime_str = row.get('data-event-datetime', '')
                    
                    if not event_datetime_str:
                        print(f"  {i+1}. NO data-event-datetime attribute")
                        continue
                    
                    try:
                        # Parse as UTC-5 (naive datetime)
                        event_dt_utc5 = datetime.strptime(event_datetime_str, '%Y/%m/%d %H:%M:%S')
                        
                        # Convert to UTC+7 (add 12 hours) and make it timezone-aware
                        event_dt_vn_naive = event_dt_utc5 + timedelta(hours=12)
                        event_dt_vn = vietnam_tz.localize(event_dt_vn_naive)
                        
                        # Get event name
                        event_elem = row.find('td', {'class': 'event'})
                        event_name = event_elem.text.strip() if event_elem else 'Unknown'
                        
                        # Check date
                        is_today = event_dt_vn.date() == today_vn
                        is_future = event_dt_vn >= now_vn
                        
                        status = ""
                        if is_today and is_future:
                            events_future.append((event_dt_vn, event_name))
                            status = "✅ TODAY + FUTURE"
                        elif is_today:
                            events_past.append((event_dt_vn, event_name))
                            status = "⏰ TODAY + PAST"
                        else:
                            events_today.append((event_dt_vn, event_name))
                            status = f"📅 OTHER DAY ({event_dt_vn.date()})"
                        
                        print(f"  {i+1}. {event_dt_vn.strftime('%Y-%m-%d %H:%M')} - {event_name[:40]:40} | {status}")
                        
                    except Exception as e:
                        print(f"  {i+1}. Error parsing: {e}")
                
                print(f"\n📊 Summary:")
                print(f"   - Today + Future (should show): {len(events_future)}")
                print(f"   - Today + Past (filtered out): {len(events_past)}")
                print(f"   - Other days: {len(events_today)}")
                
                if events_future:
                    print(f"\n✅ First 5 future events:")
                    for dt, name in events_future[:5]:
                        print(f"   {dt.strftime('%H:%M')} - {name[:50]}")
                else:
                    print(f"\n⚠️ NO FUTURE EVENTS FOUND!")

if __name__ == "__main__":
    asyncio.run(test_fetch())
