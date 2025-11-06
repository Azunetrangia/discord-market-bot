import asyncio
from bs4 import BeautifulSoup
import aiohttp
from datetime import datetime, timedelta
import pytz

async def test_with_date_filter():
    # Try different date formats
    today = datetime.now(pytz.timezone('Asia/Ho_Chi_Minh'))
    date_str = today.strftime('%Y-%m-%d')
    
    urls_to_try = [
        f"https://www.investing.com/economic-calendar/?dateFrom={date_str}&dateTo={date_str}",
        f"https://www.investing.com/economic-calendar/{date_str}",
        "https://www.investing.com/economic-calendar/",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.investing.com/',
    }
    
    async with aiohttp.ClientSession() as session:
        for url in urls_to_try:
            print(f"\n🔍 Testing URL: {url}")
            try:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        rows = soup.find_all('tr', {'class': 'js-event-item'})
                        print(f"   Found {len(rows)} events")
                        
                        if len(rows) > 0:
                            # Check first 3 events dates
                            for i, row in enumerate(rows[:3]):
                                event_dt = row.get('data-event-datetime', '')
                                event_elem = row.find('td', {'class': 'event'})
                                event_name = event_elem.text.strip() if event_elem else 'Unknown'
                                print(f"   {i+1}. {event_dt} - {event_name[:50]}")
                    else:
                        print(f"   ❌ Status: {response.status}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_with_date_filter())
