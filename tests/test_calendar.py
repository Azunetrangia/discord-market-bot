import asyncio
from bs4 import BeautifulSoup
import aiohttp

async def test_fetch():
    url = "https://www.investing.com/economic-calendar/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                rows = soup.find_all('tr', {'class': 'js-event-item'})
                print(f"📊 Found {len(rows)} total events")
                
                # Check for date headers
                date_headers = soup.find_all('tr', {'class': 'theDay'})
                print(f"📅 Found {len(date_headers)} date headers")
                for dh in date_headers[:3]:
                    print(f"   Date header: {dh.text.strip()}")
                
                impacts = {'High': 0, 'Medium': 0, 'Low': 0}
                
                print("\n📊 First 10 events with date context:")
                for i, row in enumerate(rows[:10]):  # Check first 10
                    # Check if previous sibling is a date header
                    prev_sibling = row.find_previous_sibling('tr', {'class': 'theDay'})
                    date_str = prev_sibling.text.strip() if prev_sibling else 'Unknown'
                    
                    # Get time
                    time_elem = row.find('td', {'class': 'time'})
                    time_str = time_elem.text.strip() if time_elem else ''
                    
                    # Get data-event-datetime attribute if exists
                    event_datetime = row.get('data-event-datetime', '')
                    
                    # Get event name
                    event_elem = row.find('td', {'class': 'event'})
                    event_name = event_elem.text.strip() if event_elem else ''
                    
                    print(f"{i+1}. {event_name[:35]:35} | Time: {time_str:8} | Date: {date_str[:20]:20} | data-event-datetime: {event_datetime}")

if __name__ == "__main__":
    asyncio.run(test_fetch())
