#!/usr/bin/env python3
"""Test Santiment API với các queries khác nhau"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_santiment_query(query_name, query):
    """Test một GraphQL query của Santiment"""
    api_key = os.getenv('SANTIMENT_API_KEY')
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Apikey {api_key}'
            }
            url = 'https://api.santiment.net/graphql'
            
            print(f"\n📡 Testing: {query_name}")
            
            async with session.post(url, json={'query': query}, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"   Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if 'errors' in data:
                        print(f"   ❌ GraphQL Errors:")
                        for error in data['errors']:
                            print(f"      - {error.get('message', 'Unknown error')}")
                        return False
                    
                    print(f"   ✅ Success!")
                    
                    # Hiển thị data structure
                    if 'data' in data:
                        data_keys = list(data['data'].keys())
                        print(f"   Data keys: {data_keys}")
                        
                        for key in data_keys:
                            value = data['data'][key]
                            if isinstance(value, list):
                                print(f"   {key}: {len(value)} items")
                                if len(value) > 0:
                                    print(f"      First item keys: {list(value[0].keys())}")
                                    print(f"      Sample: {str(value[0])[:200]}")
                            elif isinstance(value, dict):
                                print(f"   {key}: {list(value.keys())}")
                    
                    return True
                else:
                    text = await response.text()
                    print(f"   ❌ Error: {text[:200]}")
                    return False
                    
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False

async def main():
    print("=" * 70)
    print("🔍 TESTING SANTIMENT API QUERIES")
    print("=" * 70)
    
    # Query 1: Insights (thay vì news)
    query1 = """
    {
      allInsights(
        page: 1
        pageSize: 5
      ) {
        id
        title
        text
        readyState
        publishedAt
        user {
          username
        }
      }
    }
    """
    
    # Query 2: Projects (assets)
    query2 = """
    {
      allProjects(page: 1, pageSize: 5) {
        id
        name
        slug
        ticker
      }
    }
    """
    
    # Query 3: Timeline events
    query3 = """
    {
      timelineEvents(
        cursor: {type: BEFORE, datetime: "2025-11-06T00:00:00Z"}
        limit: 5
      ) {
        cursor {
          after
          before
        }
        events {
          id
          post {
            title
            createdAt
            user {
              username
            }
          }
        }
      }
    }
    """
    
    # Query 4: Featured insights
    query4 = """
    {
      featuredInsights {
        id
        title
        text
        publishedAt
        user {
          username
        }
      }
    }
    """
    
    queries = [
        ("All Insights", query1),
        ("All Projects", query2),
        ("Timeline Events", query3),
        ("Featured Insights", query4),
    ]
    
    results = {}
    for name, query in queries:
        results[name] = await test_santiment_query(name, query)
        await asyncio.sleep(0.5)
    
    print("\n" + "=" * 70)
    print("📋 SUMMARY:")
    for name, success in results.items():
        status = "✅ OK" if success else "❌ FAILED"
        print(f"   {status:12} {name}")
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(main())
