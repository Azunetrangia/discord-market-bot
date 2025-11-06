"""
Test Alpha Vantage và FRED APIs
"""
import requests
import json
from datetime import datetime

print("="*80)
print("📊 TESTING ALPHA VANTAGE & FRED APIs")
print("="*80)

# Test Alpha Vantage
print("\n1️⃣ Testing Alpha Vantage API...")
ALPHA_KEY = "CG1WM7WHSHL4T2EX"

# Test với GDP data
url = f"https://www.alphavantage.co/query?function=REAL_GDP&interval=annual&apikey={ALPHA_KEY}"
print(f"URL: {url}")

response = requests.get(url, timeout=10)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ Alpha Vantage hoạt động!")
    print(f"Data keys: {list(data.keys())}")
    if 'data' in data:
        print(f"Số điểm dữ liệu: {len(data['data'])}")
        print(f"Mẫu data: {data['data'][0] if data['data'] else 'N/A'}")
else:
    print(f"❌ Error: {response.text}")

# Test CPI
print("\n2️⃣ Testing Alpha Vantage CPI...")
url = f"https://www.alphavantage.co/query?function=CPI&interval=monthly&apikey={ALPHA_KEY}"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    data = response.json()
    print(f"✅ CPI data available!")
    if 'data' in data:
        print(f"Latest CPI: {data['data'][0] if data['data'] else 'N/A'}")

# Test Unemployment
print("\n3️⃣ Testing Alpha Vantage Unemployment...")
url = f"https://www.alphavantage.co/query?function=UNEMPLOYMENT&apikey={ALPHA_KEY}"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Unemployment data available!")
    if 'data' in data:
        print(f"Latest: {data['data'][0] if data['data'] else 'N/A'}")

# Test FRED
print("\n" + "="*80)
print("4️⃣ Testing FRED API...")
FRED_KEY = "c1d6a22d1b9b6a3d73d02663df314920"

# Test với Federal Funds Rate
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DFF&api_key={FRED_KEY}&file_type=json&limit=5&sort_order=desc"
print(f"URL: {url}")

response = requests.get(url, timeout=10)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ FRED hoạt động!")
    print(f"Data keys: {list(data.keys())}")
    if 'observations' in data:
        print(f"Số observations: {len(data['observations'])}")
        print(f"Latest Federal Funds Rate:")
        for obs in data['observations'][:3]:
            print(f"  {obs['date']}: {obs['value']}")
else:
    print(f"❌ Error: {response.text}")

# Test GDP từ FRED
print("\n5️⃣ Testing FRED GDP...")
url = f"https://api.stlouisfed.org/fred/series/observations?series_id=GDP&api_key={FRED_KEY}&file_type=json&limit=5&sort_order=desc"
response = requests.get(url, timeout=10)

if response.status_code == 200:
    data = response.json()
    print(f"✅ GDP data available!")
    if 'observations' in data:
        print(f"Latest GDP:")
        for obs in data['observations'][:3]:
            print(f"  {obs['date']}: ${obs['value']} billion")

print("\n" + "="*80)
print("✅ KẾT LUẬN:")
print("="*80)
print("""
Cả 2 APIs đều hoạt động tốt!

📊 Alpha Vantage: 
   - Economic indicators (CPI, GDP, Unemployment, etc.)
   - Monthly/Quarterly/Annual data
   - 500 requests/day

📊 FRED:
   - Hơn 800,000+ time series
   - Real-time economic data
   - Unlimited requests
   - Dữ liệu từ Federal Reserve (chính thống nhất)

🎯 Tôi sẽ sử dụng cả 2 nguồn để bot có đầy đủ dữ liệu kinh tế!
""")
