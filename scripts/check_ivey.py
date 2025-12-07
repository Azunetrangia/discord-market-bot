#!/usr/bin/env python3
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

async def main():
    VN = pytz.timezone('Asia/Ho_Chi_Minh')
    today = datetime.now(VN).strftime('%Y-%m-%d')
    url = f"https://www.investing.com/economic-calendar/?dateFrom={today}&dateTo={today}"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            text = await resp.text()
    soup = BeautifulSoup(text, 'html.parser')
    rows = soup.find_all('tr', {'class':'js-event-item'})
    print(f'Found {len(rows)} rows')
    now_vn = datetime.now(VN)
    for row in rows:
        try:
            event_name = ''
            event_elem = row.find('td', {'class':'event'})
            if event_elem:
                event_name = event_elem.get_text(strip=True)
            if 'Ivey' in event_name or 'Ivey PMI' in event_name:
                print('--- Found Ivey row ---')
                event_datetime_str = row.get('data-event-datetime')
                print('data-event-datetime:', event_datetime_str)
                # parse
                try:
                    dt_utc5 = datetime.strptime(event_datetime_str, '%Y/%m/%d %H:%M:%S')
                    dt_vn = pytz.timezone('Asia/Ho_Chi_Minh').localize(dt_utc5 + timedelta(hours=12))
                    print('converted VN:', dt_vn.strftime('%Y-%m-%d %H:%M:%S %Z'))
                except Exception as e:
                    print('parse error', e)
                # impact
                impact_td = row.find('td', {'class':'sentiment'})
                if impact_td:
                    print('data-img_key:', impact_td.get('data-img_key'))
                # actual/forecast/previous
                for cls in ['act','fore','prev']:
                    td = row.find('td', {'class':cls})
                    print(cls, td.get_text(strip=True) if td else '')
                # time display
                time_td = row.find('td', {'class':'time'})
                print('time cell text:', time_td.get_text(strip=True) if time_td else '')
                # id attr
                print('row attrs:', row.attrs)
        except Exception as e:
            print('row error', e)

if __name__=='__main__':
    asyncio.run(main())
