#!/usr/bin/env python3
"""Test các nguồn crypto research RSS feeds"""

import asyncio
import aiohttp
import feedparser

async def test_rss_feed(name, url):
    """Test một RSS feed"""
    print(f"\n📡 Testing: {name}")
    print(f"   URL: {url}")
    
    try:
        loop = asyncio.get_event_loop()
        feed = await loop.run_in_executor(None, feedparser.parse, url)
        
        if feed.entries:
            print(f"   ✅ Success! Found {len(feed.entries)} articles")
            
            # Show first article
            if len(feed.entries) > 0:
                entry = feed.entries[0]
                print(f"\n   📰 First article:")
                print(f"      Title: {entry.get('title', 'N/A')[:80]}")
                print(f"      Link: {entry.get('link', 'N/A')}")
                print(f"      Published: {entry.get('published', 'N/A')}")
                
                # Check if has description
                desc = entry.get('description', '') or entry.get('summary', '')
                if desc:
                    print(f"      Description: {desc[:100]}...")
            
            return True
        else:
            print(f"   ❌ No entries found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

async def main():
    print("=" * 70)
    print("🔍 TESTING CRYPTO RESEARCH RSS FEEDS")
    print("=" * 70)
    
    # Danh sách RSS feeds về crypto research/analysis
    feeds = [
        # (Legacy Messari removed) Glassnode is recommended below
        
        # CoinDesk Research
        ("CoinDesk Research", "https://www.coindesk.com/arc/outboundfeeds/rss/category/research/"),
        ("CoinDesk Markets", "https://www.coindesk.com/arc/outboundfeeds/rss/category/markets/"),
        
        # Cointelegraph Analysis
        ("Cointelegraph Market Analysis", "https://cointelegraph.com/rss/category/market-analysis"),
        ("Cointelegraph Analysis & Opinion", "https://cointelegraph.com/rss/category/analysis"),
        
        # CryptoSlate Research
        ("CryptoSlate", "https://cryptoslate.com/feed/"),
        
        # The Block Research
        ("The Block", "https://www.theblock.co/rss.xml"),
        
        # Decrypt
        ("Decrypt", "https://decrypt.co/feed"),
        
        # Bitcoin Magazine
        ("Bitcoin Magazine", "https://bitcoinmagazine.com/feed"),
        
        # Glassnode Insights (nếu có RSS)
        ("Glassnode Insights", "https://insights.glassnode.com/feed/"),
        
        # IntoTheBlock
        ("IntoTheBlock Blog", "https://blog.intotheblock.com/rss/"),
        
        # Delphi Digital (nếu có RSS public)
        ("Delphi Digital", "https://members.delphidigital.io/feed/"),
        
        # Bankless
        ("Bankless", "https://banklesshq.com/rss/"),
    ]
    
    results = {}
    for name, url in feeds:
        results[name] = await test_rss_feed(name, url)
        await asyncio.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 SUMMARY:")
    print("=" * 70)
    
    working = []
    failed = []
    
    for name, success in results.items():
        if success:
            working.append(name)
            print(f"   ✅ {name}")
        else:
            failed.append(name)
            print(f"   ❌ {name}")
    
    print("\n" + "=" * 70)
    print(f"✅ Working: {len(working)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print("=" * 70)
    
    if working:
        print("\n🎯 RECOMMENDED WORKING FEEDS:")
        for name in working[:5]:
            print(f"   • {name}")

if __name__ == '__main__':
    asyncio.run(main())
