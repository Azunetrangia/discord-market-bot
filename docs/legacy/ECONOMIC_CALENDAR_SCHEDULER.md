# Economic Calendar Scheduler (Hybrid design)

## Overview

This document describes the current economic calendar behavior implemented in `cogs/news_cog.py`.

Key behaviour summary:
- Daily summary: sent at 07:00 UTC+7 covering events from 07:00 (today) through 04:30 next day.
- Per-event checks: targeted re-checks at T+0, T+2, T+5 minutes with a retry policy (see details).
- No pre-alerts or backfill: the system intentionally avoids pre-event alerts; instead a daily summary + targeted checks provide concise coverage.
- Filter: only Medium and High impact events are scheduled/checked.

## Scheduler behavior

### Main daily flow (`economic_calendar_scheduler`)

- Runs once per day at **07:00 UTC+7**.
- On run it:
  1. Cancels any remaining scheduled tasks and clears tracking state.
  2. Fetches events covering now → 04:30 next day (Investing.com scrape).
  3. Sends a compact daily summary embed to the configured channel(s).
  4. Schedules per-event check tasks for each relevant event.

### Daily summary

- Sent at 07:00 UTC+7.
- Groups events into time blocks and shows counts/impact breakdown.
- Purpose: give users a clean overview of today's events so they can plan.

### Per-event checks (no pre-alert)

- For each High/Medium event the scheduler creates tasks to run at offsets relative to the event time:
  - T+0 (at event time): run for all scheduled events.
  - T+2 (2 minutes after): run for Medium and High events.
  - T+5 (5 minutes after): run for High events only.
- Each check will re-fetch the event details within a narrow window (±5 minutes) and post the actual value only if available.
- Once an event's actual value has been posted, subsequent checks are skipped via `self.scheduled_events[event_id]['actual_posted']`.

## Data structures

- `self.scheduled_events`: dict mapping stable event ids → state (e.g. `{'actual_posted': False, 'event': {...}}`).
- `self.event_tasks`: list of asyncio Task objects that can be cancelled when the scheduler resets.

## Commands

### `!schedulenow`
- Admin only. Triggers the same flow as the daily scheduler immediately (fetch → summary → schedule checks).

### `!testcalendar`
- Admin only. Fetches events and shows the daily summary without scheduling background tasks.

## Timezone

- All displayed times use **UTC+7** (Asia/Ho_Chi_Minh). Investing.com timestamps are parsed and localized accordingly.

## Retry policy and filters

- Retry offsets: [0, 2, 5] minutes.
- Posting policy:
  - T+0: attempt posting for all events.
  - T+2: attempt for Medium & High.
  - T+5: attempt for High only.

## Advantages of this hybrid approach

- Simpler than pre-alert/backfill flows.
- Users get one clear daily summary and reliable per-event checks.
- Less noisy (no pre-event chimes) while still catching actual releases soon after they occur.

## Testing

1. Trigger scheduler now:
```
!schedulenow
```

2. Check logs for summary + scheduled checks messages.

## Code references

- Scheduler & summary: `cogs/news_cog.py` (search for `economic_calendar_scheduler`, `send_daily_summary`, `_check_and_post_event`)


