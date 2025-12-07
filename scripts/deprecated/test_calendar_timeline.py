"""
Simple logical test for Economic Calendar Scheduler.

Scenario: Spanish 15-Year Obligacion Auction @ 16:40 on 06/11/2025 (UTC+7)
Timeline test (logical, not time-based):
  - 16:34: Scheduler runs → should schedule pre-alert for 16:35 (future)
  - If bot starts at 16:36 → pre-alert already passed but event not yet (backfill)

This script calls _schedule_events_for_day and inspects the scheduling decisions
without actually waiting for sleeps.
"""
import asyncio
from datetime import datetime, timedelta
import pytz
import sys
import os

# Ensure repo root in path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from cogs.news_cog import NewsCog

# Fake channel/guild/bot
class FakeChannel:
    def __init__(self, name):
        self.name = name
        self.messages = []
    
    async def send(self, embed=None, **kwargs):
        title = getattr(embed, 'title', 'No title')
        self.messages.append({'title': title, 'embed': embed})
        print(f"📨 [SEND] {title[:80]}")

class FakeGuild:
    def __init__(self, id, name):
        self.id = id
        self.name = name

class FakeBot:
    def __init__(self, guilds, channel_map):
        self.guilds = guilds
        self._channel_map = channel_map
    
    def get_channel(self, channel_id):
        return self._channel_map.get(channel_id)
    
    async def wait_until_ready(self):
        return

async def test_scenario_1():
    """Scenario 1: Bot starts at 16:34, event at 16:40 → should schedule pre-alert for 16:35"""
    print("\n" + "="*80)
    print("SCENARIO 1: Scheduler runs at 16:34 (before pre-alert time 16:35)")
    print("="*80)
    
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    
    # Mock datetime.now to return 16:34
    from unittest.mock import patch
    fake_now = tz.localize(datetime(2025, 11, 6, 16, 34, 0))
    
    guild = FakeGuild(9999, 'TestGuild')
    channel = FakeChannel('economic-calendar')
    bot = FakeBot([guild], {7777: channel})
    
    cog = NewsCog(bot)
    try:
        cog.news_checker.cancel()
        cog.daily_calendar_summary.cancel()
        cog.economic_calendar_scheduler.cancel()
    except Exception:
        pass
    
    def fake_load_news_config(guild_id=None):
        return {'economic_calendar_channel': 7777}
    cog.load_news_config = fake_load_news_config
    
    # Event at 16:40
    event = {
        'id': 'test_spanish_auction',
        'event': 'Spanish 15-Year Obligacion Auction',
        'event_name': 'Spanish 15-Year Obligacion Auction',
        'country': 'Spain',
        'impact': 'Medium',
        'time': '16:40',
        'actual': 'N/A',
        'forecast': 'N/A',
        'previous': '3.02%',
    }
    
    print(f"Current time (mocked): {fake_now.strftime('%H:%M')}")
    print(f"Event time: {event['time']}")
    print(f"Expected pre-alert time: 16:35")
    print(f"Expected behavior: Schedule pre-alert for 16:35 (in future)")
    
    # Patch datetime.now in NewsCog
    with patch('cogs.news_cog.datetime') as mock_dt:
        mock_dt.now = lambda tz=None: fake_now.astimezone(tz) if tz else fake_now
        mock_dt.strptime = datetime.strptime
        mock_dt.fromisoformat = datetime.fromisoformat
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        await cog._schedule_events_for_day([event])
    
    print(f"\nResult:")
    print(f"  Tasks scheduled: {len(cog.event_tasks)}")
    print(f"  Messages sent immediately: {len(channel.messages)}")
    
    if len(channel.messages) == 0:
        print(f"  ✅ PASS: No immediate messages (pre-alert scheduled for future)")
    else:
        print(f"  ❌ FAIL: Unexpected immediate message")
    
    if len(cog.event_tasks) >= 4:
        print(f"  ✅ PASS: Scheduled pre-alert + 3 actual checks")
    else:
        print(f"  ⚠️  Only {len(cog.event_tasks)} tasks scheduled")

async def test_scenario_2():
    """Scenario 2: Bot starts at 16:36, event at 16:40 → should backfill pre-alert"""
    print("\n" + "="*80)
    print("SCENARIO 2: Bot starts at 16:36 (after pre-alert 16:35, before event 16:40)")
    print("="*80)
    
    tz = pytz.timezone('Asia/Ho_Chi_Minh')
    
    # Mock datetime.now to return 16:36
    from unittest.mock import patch
    fake_now = tz.localize(datetime(2025, 11, 6, 16, 36, 0))
    
    guild = FakeGuild(9999, 'TestGuild')
    channel = FakeChannel('economic-calendar')
    bot = FakeBot([guild], {7777: channel})
    
    cog = NewsCog(bot)
    try:
        cog.news_checker.cancel()
        cog.daily_calendar_summary.cancel()
        cog.economic_calendar_scheduler.cancel()
    except Exception:
        pass
    
    def fake_load_news_config(guild_id=None):
        return {'economic_calendar_channel': 7777}
    cog.load_news_config = fake_load_news_config
    
    # Event at 16:40
    event = {
        'id': 'test_spanish_auction',
        'event': 'Spanish 15-Year Obligacion Auction',
        'event_name': 'Spanish 15-Year Obligacion Auction',
        'country': 'Spain',
        'impact': 'Medium',
        'time': '16:40',
        'actual': 'N/A',
        'forecast': 'N/A',
        'previous': '3.02%',
    }
    
    print(f"Current time (mocked): {fake_now.strftime('%H:%M')}")
    print(f"Event time: {event['time']}")
    print(f"Pre-alert time was: 16:35 (already passed)")
    print(f"Expected behavior: Post missed pre-alert immediately (backfill)")
    
    # Patch datetime.now in NewsCog
    with patch('cogs.news_cog.datetime') as mock_dt:
        mock_dt.now = lambda tz=None: fake_now.astimezone(tz) if tz else fake_now
        mock_dt.strptime = datetime.strptime
        mock_dt.fromisoformat = datetime.fromisoformat
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        
        await cog._schedule_events_for_day([event])
    
    print(f"\nResult:")
    print(f"  Tasks scheduled: {len(cog.event_tasks)}")
    print(f"  Messages sent immediately: {len(channel.messages)}")
    
    if len(channel.messages) >= 1:
        print(f"  ✅ PASS: Immediate pre-alert sent (backfill)")
        if 'Sắp diễn ra' in channel.messages[0]['title']:
            print(f"  ✅ PASS: Message is pre-alert type")
    else:
        print(f"  ❌ FAIL: No backfill message sent")
    
    if len(cog.event_tasks) >= 3:
        print(f"  ✅ PASS: Scheduled 3 actual checks for future")
    else:
        print(f"  ⚠️  Only {len(cog.event_tasks)} future tasks scheduled")

async def main():
    print("="*80)
    print("ECONOMIC CALENDAR SCHEDULER LOGICAL TEST")
    print("="*80)
    
    await test_scenario_1()
    await test_scenario_2()
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nNote: This test uses mocked time (no real sleeps).")
    print("In production, scheduled tasks will wait real time.")

if __name__ == '__main__':
    asyncio.run(main())
