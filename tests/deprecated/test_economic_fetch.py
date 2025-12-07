"""
Test script to check economic calendar fetching
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from cogs.news_cog import NewsCog

class FakeBot:
    def __init__(self):
        self.guilds = []
    
    def get_channel(self, channel_id):
        return None
    
    async def wait_until_ready(self):
        return

async def main():
    print("=" * 80)
    print("TESTING ECONOMIC CALENDAR FETCH")
    print("=" * 80)
    
    # Create cog instance
    bot = FakeBot()
    cog = NewsCog(bot)
    
    # Try to cancel background tasks
    try:
        cog.news_checker.cancel()
    except:
        pass
    
    print("\nFetching economic calendar...")
    events = await cog.fetch_economic_calendar()
    
    print(f"\n✅ Found {len(events)} events")
    
    if events:
        print("\nFirst 5 events:")
        for i, event in enumerate(events[:5], 1):
            print(f"\n{i}. {event.get('event', 'N/A')}")
            print(f"   Country: {event.get('country', 'N/A')}")
            print(f"   Impact: {event.get('impact', 'N/A')}")
            print(f"   Time: {event.get('time', 'N/A')}")
            print(f"   Forecast: {event.get('forecast', 'N/A')}")
            print(f"   Actual: {event.get('actual', 'N/A')}")
            print(f"   Previous: {event.get('previous', 'N/A')}")
    else:
        print("\n❌ No events found!")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    asyncio.run(main())
