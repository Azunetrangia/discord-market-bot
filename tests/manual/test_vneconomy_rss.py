#!/usr/bin/env python3
"""Test VNEconomy RSS feed để kiểm tra HTML entities"""

import feedparser
import html
import re

url = 'https://vneconomy.vn/macro-economy.rss'

print("=" * 70)
print("🔍 TESTING VNECONOMY RSS FEED WITH FIX")
print("=" * 70)

feed = feedparser.parse(url)

if feed.entries:
    print(f"\n✅ Found {len(feed.entries)} entries\n")
    
    for i, entry in enumerate(feed.entries[:3], 1):
        print(f"📰 Article #{i}:")
        
        # Test title
        title = entry.get('title', '')
        print(f"   Raw title: {title[:100]}")
        
        # Fix VNEconomy format: #225; -> &#225;
        title_fixed = re.sub(r'#(\d+);', r'&#\1;', title)
        title_unescaped = html.unescape(title_fixed)
        print(f"   ✅ Fixed title: {title_unescaped[:100]}")
        
        # Test description
        desc = entry.get('description', '') or entry.get('summary', '')
        if desc:
            print(f"   Raw desc: {desc[:80]}")
            
            # Fix and unescape
            desc_fixed = re.sub(r'#(\d+);', r'&#\1;', desc)
            desc_unescaped = html.unescape(desc_fixed)
            print(f"   ✅ Fixed desc: {desc_unescaped[:80]}")
        
        print()
else:
    print("❌ No entries found")

print("=" * 70)
