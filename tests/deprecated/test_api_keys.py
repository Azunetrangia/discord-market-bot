#!/usr/bin/env python3
"""Test Glassnode (RSS) and Santiment API keys"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_glassnode():
    """Test Glassnode Insights RSS feed accessibility"""
    url = 'https://insights.glassnode.com/feed/'
    try:
        async with aiohttp.ClientSession() as session:
            print(f"📡 Testing Glassnode RSS: {url}")
            async with session.get(url) as response:
                print(f"   Status: {response.status}")
                if response.status == 200:
                    text = await response.text()
                    # crude check for RSS feed content
                    if '<rss' in text or '<feed' in text:
                        print("   ✅ Glassnode RSS reachable and looks like a feed")
                        return True
                    else:
                        print("   ❌ Response received but not an RSS feed")
                        return False
                else:
                    print("   ❌ Failed to fetch Glassnode RSS")
                    return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

async def test_santiment():
    """Test Santiment API"""
    api_key = os.getenv('SANTIMENT_API_KEY')
    
    if not api_key:
        print("❌ SANTIMENT_API_KEY không tồn tại trong .env")
        return False
    
    print(f"✅ SANTIMENT_API_KEY found: {api_key[:10]}...")
    
    try:
        query = """
        {
          getNews(
            size: 5
            tag: "news"
          ) {
            id
            title
            description
            url
            publishedAt
          }
        }
        """
        
        async with aiohttp.ClientSession() as session:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Apikey {api_key}'
            }
            url = 'https://api.santiment.net/graphql'
            
            print(f"📡 Testing Santiment API: {url}")
            async with session.post(url, json={'query': query}, headers=headers) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'errors' in data:
                        print(f"   ❌ GraphQL Errors: {data['errors']}")
                        return False
                    
                    news = data.get('data', {}).get('getNews', [])
                    print(f"   ✅ Success! Found {len(news)} articles")
                    
                    if news:
                        print(f"\n   First article:")
                        print(f"   - Title: {news[0].get('title', 'N/A')}")
                        print(f"   - URL: {news[0].get('url', 'N/A')}")
                    return True
                else:
                    text = await response.text()
                    print(f"   ❌ Error: {text[:200]}")
                    return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

async def main():
    print("=" * 60)
    print("🔍 TESTING API KEYS")
    print("=" * 60)
    
    print("\n📊 Testing Glassnode RSS...")
    glassnode_ok = await test_glassnode()
    
    print("\n" + "=" * 60)
    print("\n🔗 Testing Santiment...")
    santiment_ok = await test_santiment()
    
    print("\n" + "=" * 60)
    print("\n📋 SUMMARY:")
    print(f"   Glassnode RSS:   {'✅ OK' if glassnode_ok else '❌ FAILED'}")
    print(f"   Santiment: {'✅ OK' if santiment_ok else '❌ FAILED'}")
    print("=" * 60)

if __name__ == '__main__':
    asyncio.run(main())
