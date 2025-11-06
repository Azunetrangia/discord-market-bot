# 📡 API Reference & Technical Details

## Messari API

### Endpoint sử dụng:
```
GET https://data.messari.io/api/v1/news
```

### Headers:
```python
{
    'x-messari-api-key': 'YOUR_API_KEY'
}
```

### Response Format:
```json
{
  "data": [
    {
      "id": "abc123",
      "title": "Bitcoin Price Analysis",
      "url": "https://...",
      "content": "...",
      "published_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Rate Limits:
- Free tier: ~20 requests/minute
- Pro tier: Varies by plan

### Documentation:
https://messari.io/api/docs

---

## Santiment API

### Endpoint sử dụng:
```
POST https://api.santiment.net/graphql
```

### Headers:
```python
{
    'Content-Type': 'application/json',
    'Authorization': 'Apikey YOUR_API_KEY'
}
```

### GraphQL Query:
```graphql
{
  getNews(size: 5, tag: "news") {
    id
    title
    description
    url
    publishedAt
  }
}
```

### Rate Limits:
- Free tier: 300 queries/month
- Pro tier: Varies by plan

### Documentation:
https://api.santiment.net/graphiql

---

## CoinGecko API

### Endpoints sử dụng:

#### 1. Get Price (Simple Price)
```
GET https://api.coingecko.com/api/v3/simple/price
```

**Parameters:**
- `ids`: Coin IDs (comma-separated)
- `vs_currencies`: usd
- `x_cg_demo_api_key`: YOUR_API_KEY (in header)

**Example:**
```python
params = {
    'ids': 'bitcoin,ethereum',
    'vs_currencies': 'usd'
}
headers = {
    'x_cg_demo_api_key': 'YOUR_API_KEY'
}
```

**Response:**
```json
{
  "bitcoin": {
    "usd": 43000.50
  },
  "ethereum": {
    "usd": 2300.25
  }
}
```

#### 2. Get Market Chart (7 days)
```
GET https://api.coingecko.com/api/v3/coins/{id}/market_chart
```

**Parameters:**
- `vs_currency`: usd
- `days`: 7
- `x_cg_demo_api_key`: YOUR_API_KEY (in header)

**Response:**
```json
{
  "prices": [
    [1704067200000, 43000.50],
    [1704153600000, 43500.25],
    ...
  ],
  "market_caps": [...],
  "total_volumes": [...]
}
```

### Rate Limits:
- Free tier: 10-30 calls/minute
- **Demo Plan (with API Key)**: 500 calls/minute
- Pro tier: 10,000+ calls/minute

### CoinGecko ID Mapping:
Bot tự động map các ticker phổ biến:

| Ticker | CoinGecko ID |
|--------|--------------|
| BTC | bitcoin |
| ETH | ethereum |
| BNB | binancecoin |
| SOL | solana |
| XRP | ripple |
| ADA | cardano |
| DOGE | dogecoin |
| DOT | polkadot |
| MATIC | polygon |
| AVAX | avalanche-2 |
| LINK | chainlink |
| UNI | uniswap |
| ATOM | cosmos |
| LTC | litecoin |
| ETC | ethereum-classic |

**Search for other coins:**
https://api.coingecko.com/api/v3/search?query=YOUR_COIN

### Documentation:
https://www.coingecko.com/api/documentation

---

## RSS Feeds

### Thư viện: feedparser

**Supported Formats:**
- RSS 2.0
- RSS 1.0
- Atom

**Usage:**
```python
import feedparser

feed = feedparser.parse('https://example.com/rss.xml')

for entry in feed.entries:
    title = entry.title
    link = entry.link
    summary = entry.summary
    published = entry.published_parsed
```

**Common RSS Feeds for Crypto:**
- CoinDesk: `https://www.coindesk.com/arc/outboundfeeds/rss/`
- Cointelegraph: `https://cointelegraph.com/rss`
- Bitcoin Magazine: `https://bitcoinmagazine.com/.rss/full/`
- Decrypt: `https://decrypt.co/feed`

### Documentation:
https://feedparser.readthedocs.io/

---

## Background Tasks (discord.py)

### News Checker Loop

**Interval:** 10 minutes (600 seconds)

**Logic:**
```python
@tasks.loop(minutes=10)
async def news_checker(self):
    # 1. Load config
    config = self.load_news_config()
    last_posts = self.load_last_posts()
    
    # 2. Check Messari
    if config['messari_channel']:
        news = await self.fetch_messari_news()
        for article in news:
            if article['id'] not in last_posts['messari']:
                # Post to channel
                # Save ID
    
    # 3. Check Santiment
    # Similar logic
    
    # 4. Check RSS Feeds
    for feed in config['rss_feeds']:
        entries = await self.fetch_rss_feed(feed['url'])
        # Check and post
    
    # 5. Save last_posts
    self.save_last_posts(last_posts)
```

### Price Checker Loop

**Interval:** 60 seconds

**Logic:**
```python
@tasks.loop(seconds=60)
async def price_checker(self):
    # 1. Load all alerts
    alerts = self.load_alerts()
    
    # 2. Get unique coin IDs
    coin_ids = list(set([a['ticker'] for a in alerts]))
    
    # 3. Batch fetch prices (1 API call)
    prices = self.cg.get_price(ids=coin_ids, vs_currencies='usd')
    
    # 4. Check each alert
    for alert in alerts:
        current_price = prices[alert['ticker']]['usd']
        
        if current_price >= alert['target_price']:
            # 5. Create chart
            chart = await self.create_price_chart(...)
            
            # 6. Send notification
            await channel.send(content=mention, embed=embed, file=chart)
            
            # 7. Remove alert
            alerts_to_remove.append(alert)
    
    # 8. Save updated alerts
    self.save_alerts(remaining_alerts)
```

---

## Chart Generation (Matplotlib)

### Dependencies:
```python
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
```

### Chart Creation Process:
```python
async def create_price_chart(self, coin_id, ticker_display, current_price, target_price):
    # 1. Fetch 7-day data
    data = self.cg.get_coin_market_chart_by_id(
        id=coin_id,
        vs_currency='usd',
        days=7
    )
    
    # 2. Parse data
    timestamps = [datetime.fromtimestamp(p[0]/1000) for p in data['prices']]
    prices = [p[1] for p in data['prices']]
    
    # 3. Create plot
    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, prices, linewidth=2, color='#2E86C1', label='Giá')
    
    # 4. Add target line
    plt.axhline(y=target_price, color='#E74C3C', linestyle='--', linewidth=2, label='Mục tiêu')
    
    # 5. Mark current price
    plt.plot(timestamps[-1], current_price, 'o', markersize=10, color='#27AE60', label='Hiện tại')
    
    # 6. Format and save
    plt.title(f'{ticker_display}/USD - 7 Ngày')
    plt.xlabel('Ngày')
    plt.ylabel('Giá (USD)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'data/chart_{coin_id}.png', dpi=100)
    plt.close()
    
    return f'data/chart_{coin_id}.png'
```

### Chart Features:
- **Size:** 12x6 inches, 100 DPI
- **Style:** seaborn-v0_8-darkgrid
- **Colors:**
  - Price line: #2E86C1 (Blue)
  - Target line: #E74C3C (Red, dashed)
  - Current price: #27AE60 (Green dot)
- **Format:**
  - X-axis: Date (DD/MM)
  - Y-axis: Price with $ and commas

---

## Data Persistence

### File Structure

#### news_config.json
```json
{
  "messari_channel": 1234567890,
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

#### last_post_ids.json
```json
{
  "messari": ["id1", "id2", "..."],
  "santiment": ["id1", "id2", "..."],
  "rss": {
    "https://example.com/rss.xml": ["id1", "id2", "..."]
  }
}
```

**Note:** Mỗi list giữ tối đa 100 IDs để tránh file quá lớn.

#### alerts.json
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

### Thread Safety
- Tất cả file I/O đều synchronous (blocking)
- Background tasks chạy async nhưng không conflict vì:
  - News checker: 10 phút/lần
  - Price checker: 60 giây/lần
  - Không có concurrent writes to same file

---

## Discord.py Views & Modals

### Persistent Views
```python
class MainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # Never timeout
```

**Benefits:**
- Buttons work even after bot restart
- No expiration

### Timeout Views
```python
class NewsMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)  # 3 minutes
```

**Use Cases:**
- Sub-menus
- Selection dialogs
- Temporary interactions

### Modals
```python
class AddAlertModal(discord.ui.Modal, title="Thêm Cảnh báo Giá"):
    ticker = discord.ui.TextInput(
        label="Ticker (Mã coin)",
        placeholder="Ví dụ: BTC, ETH",
        required=True,
        style=discord.TextStyle.short
    )
    
    async def on_submit(self, interaction):
        # Process data
        pass
```

**Input Styles:**
- `TextStyle.short`: Single line (default)
- `TextStyle.paragraph`: Multi-line

---

## Error Handling

### API Errors
```python
try:
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            data = await response.json()
        else:
            print(f"API Error: {response.status}")
except Exception as e:
    print(f"Network Error: {e}")
```

### Discord Errors
```python
try:
    await interaction.response.send_message(...)
except discord.errors.InteractionResponded:
    await interaction.followup.send(...)
except discord.errors.NotFound:
    print("Channel/Message not found")
```

### File I/O Errors
```python
try:
    with open(path, 'r') as f:
        data = json.load(f)
except FileNotFoundError:
    data = default_value
except json.JSONDecodeError:
    print("Invalid JSON")
    data = default_value
```

---

## Performance Optimization

### Batch API Requests
```python
# ❌ BAD: Multiple requests
for alert in alerts:
    price = get_price(alert['ticker'])

# ✅ GOOD: One batch request
tickers = [a['ticker'] for a in alerts]
prices = get_price(ids=tickers)
```

### Async Operations
```python
# ✅ All API calls are async
async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
        data = await response.json()
```

### Memory Management
```python
# Limit stored IDs to 100
if len(last_posts['messari']) > 100:
    last_posts['messari'] = last_posts['messari'][-100:]
```

### Chart Cleanup
```python
# Delete chart after sending
try:
    os.remove(chart_path)
except:
    pass
```

---

## Security Best Practices

### ✅ Do's:
- Use environment variables for secrets
- Validate user input
- Check permissions before actions
- Use ephemeral messages for sensitive data

### ❌ Don'ts:
- Never hardcode API keys
- Never commit .env file
- Don't trust user input without validation
- Don't expose internal errors to users

---

## Testing

### Test News Feed:
```python
# Use a public RSS feed
URL = "https://news.ycombinator.com/rss"
feed = feedparser.parse(URL)
print(f"Found {len(feed.entries)} entries")
```

### Test CoinGecko:
```python
cg = CoinGeckoAPI(api_key='YOUR_KEY')
price = cg.get_price(ids='bitcoin', vs_currencies='usd')
print(price)  # {'bitcoin': {'usd': 43000.5}}
```

### Test Chart Generation:
```python
# Set low target price to trigger immediately
target = current_price - 1000
```

---

## Useful Resources

- **discord.py Docs**: https://discordpy.readthedocs.io/
- **CoinGecko API**: https://www.coingecko.com/api/documentation
- **Matplotlib Gallery**: https://matplotlib.org/stable/gallery/
- **feedparser Docs**: https://feedparser.readthedocs.io/
- **aiohttp Docs**: https://docs.aiohttp.org/

---

**Last Updated:** 2025-01-01
