#!/usr/bin/env python3
"""Test Santiment insights với code mới"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cogs.news_cog import NewsCog
from dotenv import load_dotenv

load_dotenv()

async def test_santiment():
    """Test fetch Santiment insights"""
    
    # Create a mock bot object
    class MockBot:
        pass
    
    bot = MockBot()
    cog = NewsCog(bot)
    
    print("=" * 70)
    print("🔍 TESTING SANTIMENT INSIGHTS")
    print("=" * 70)
    
    print("\n📡 Fetching Santiment insights...")
    insights = await cog.fetch_santiment_news()
    
    if insights:
        print(f"✅ Success! Found {len(insights)} insights\n")
        
        for i, insight in enumerate(insights, 1):
            print(f"📊 Insight #{i}:")
            print(f"   ID: {insight.get('id')}")
            print(f"   Title: {insight.get('title', 'N/A')[:80]}")
            print(f"   Author: {insight.get('user', {}).get('username', 'N/A')}")
            print(f"   Published: {insight.get('publishedAt', 'N/A')}")
            print(f"   State: {insight.get('readyState', 'N/A')}")
            
            # Show text preview
            text = insight.get('text', '')
            if text:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(text, 'html.parser')
                clean_text = soup.get_text()[:150]
                print(f"   Preview: {clean_text}...")
            print()
    else:
        print("❌ No insights returned")
    
    print("=" * 70)

if __name__ == '__main__':
    asyncio.run(test_santiment())
