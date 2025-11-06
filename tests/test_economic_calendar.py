import requests
import json
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup

load_dotenv()

print("="*80)
print("📊 TEST ECONOMIC CALENDAR - ALTERNATIVE SOURCES")
print("="*80)

# Option 1: Investing.com Economic Calendar (Web Scraping)
print("\n1️⃣ Testing Investing.com Economic Calendar...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    url = 'https://www.investing.com/economic-calendar/'
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        print(f"✅ Investing.com accessible (Status: {response.status_code})")
        print(f"   Content length: {len(response.text)} bytes")
        # Kiểm tra có economic events không
        if 'economicCalendarRow' in response.text or 'event' in response.text.lower():
            print("   ✅ Có dữ liệu Economic Calendar!")
    else:
        print(f"❌ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Option 2: Forex Factory Calendar
print("\n2️⃣ Testing Forex Factory Calendar...")
try:
    url = 'https://www.forexfactory.com/calendar'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        print(f"✅ Forex Factory accessible (Status: {response.status_code})")
        print(f"   Content length: {len(response.text)} bytes")
        if 'calendar__row' in response.text or 'impact' in response.text.lower():
            print("   ✅ Có dữ liệu Economic Calendar!")
    else:
        print(f"❌ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Option 3: TradingView Economic Calendar
print("\n3️⃣ Testing TradingView Economic Calendar...")
try:
    url = 'https://www.tradingview.com/economic-calendar/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        print(f"✅ TradingView accessible (Status: {response.status_code})")
        print(f"   Content length: {len(response.text)} bytes")
    else:
        print(f"❌ Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Option 4: FMP API status check
print("\n4️⃣ Testing FMP API...")
FMP_API_KEY = os.getenv('FMP_API_KEY')
try:
    # Test với endpoint đơn giản hơn
    url = f'https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={FMP_API_KEY}'
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        print(f"✅ FMP API Key hoạt động (tested with profile endpoint)")
        print(f"   Response: {response.json()[0].get('companyName', 'N/A')}")
    else:
        print(f"❌ FMP API Status: {response.status_code}")
        print(f"   Message: {response.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print("📝 KẾT LUẬN & KHUYẾN NGHỊ:")
print("="*80)
print("""
FMP Economic Calendar endpoint đã bị legacy và yêu cầu subscription mới.

🎯 GIẢI PHÁP TỐT NHẤT:

1. FOREX FACTORY (Khuyến nghị #1)
   - Miễn phí 100%
   - Dữ liệu chính xác, real-time
   - Web scraping đơn giản
   
2. INVESTING.COM 
   - Miễn phí
   - Nhiều dữ liệu
   - Cần xử lý chống crawl
   
3. TRADINGECONOMICS API
   - Cần subscription (~$50/tháng)
   - API chính thức
   
Bạn muốn tôi implement scraper cho Forex Factory không? 
Nó sẽ cho bạn lịch kinh tế miễn phí và chính xác!
""")

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    
    print(f"✅ Nhận được {len(data)} sự kiện kinh tế\n")
    
    # Lọc các sự kiện High và Medium impact
    important_events = []
    for event in data:
        if event.get('impact') in ['High', 'Medium']:
            important_events.append(event)
    
    print(f"📊 Có {len(important_events)} sự kiện quan trọng (High/Medium impact)\n")
    print("="*80)
    
    # Hiển thị 10 sự kiện đầu tiên
    for i, event in enumerate(important_events[:10]):
        print(f"\n{i+1}. {event.get('event', 'Unknown Event')}")
        print(f"   🌍 Quốc gia: {event.get('country', 'N/A')}")
        print(f"   ⚡ Mức độ: {event.get('impact', 'Unknown')}")
        print(f"   📅 Thời gian: {event.get('date', 'N/A')}")
        
        # Chuyển sang múi giờ VN
        try:
            event_time = datetime.fromisoformat(event.get('date', '').replace('Z', '+00:00'))
            vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
            event_time_vn = event_time.astimezone(vn_tz)
            print(f"   🕐 Giờ VN: {event_time_vn.strftime('%d/%m/%Y %H:%M')}")
        except:
            pass
        
        if event.get('estimate') is not None:
            print(f"   📈 Dự kiến: {event.get('estimate')}")
        if event.get('previous') is not None:
            print(f"   📉 Trước đó: {event.get('previous')}")
        if event.get('actual') is not None:
            print(f"   ✅ THỰC TẾ: {event.get('actual')}")
        
        print(f"   🆔 ID: {event.get('date')}_{event.get('event')}_{event.get('country')}")
        print("-"*80)
    
    if len(important_events) > 10:
        print(f"\n... và {len(important_events) - 10} sự kiện khác")
    
else:
    print(f"❌ Lỗi: {response.status_code}")
    print(response.text)
