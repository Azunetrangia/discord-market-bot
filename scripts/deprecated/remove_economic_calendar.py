"""
Script to remove ALL Economic Calendar features from news_cog.py
This will preserve only news-related functionality.
"""

import re

def remove_economic_calendar(input_file, output_file):
    """Remove all Economic Calendar code from news_cog.py"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track which lines to keep
    keep_lines = []
    skip_until = None
    in_economic_class = False
    in_economic_function = False
    in_economic_task = False
    in_economic_command = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip Economic Calendar references in source_type comments
        if "'economic_calendar'" in line or '"economic_calendar"' in line:
            if 'source_type' in line:
                # Replace with comment explaining removal
                keep_lines.append("        # Economic Calendar removed - only news sources supported\n")
                i += 1
                continue
        
        # Skip EconomicMenuView class (lines 743-867 approximately)
        if 'class EconomicMenuView' in line:
            print(f"Removing EconomicMenuView class starting at line {i+1}")
            in_economic_class = True
            # Skip until next class or end of indentation
            i += 1
            while i < len(lines):
                # Check if we've reached the next class or top-level code
                if lines[i].startswith('class ') and 'Economic' not in lines[i]:
                    break
                if lines[i].startswith('async def setup(') or lines[i].startswith('def setup('):
                    break
                i += 1
            continue
        
        # Skip fetch_economic_calendar function
        if 'async def fetch_economic_calendar' in line or 'def fetch_economic_calendar' in line:
            print(f"Removing fetch_economic_calendar function at line {i+1}")
            in_economic_function = True
            # Skip until next function definition at same indentation
            indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith('async def ') or lines[i].strip().startswith('def '):
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    if current_indent <= indent:
                        break
                i += 1
            continue
        
        # Skip send_economic_event_update function
        if 'async def send_economic_event_update' in line:
            print(f"Removing send_economic_event_update function at line {i+1}")
            indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith('async def ') or lines[i].strip().startswith('def '):
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    if current_indent <= indent:
                        break
                i += 1
            continue
        
        # Skip send_daily_summary function
        if 'async def send_daily_summary' in line:
            print(f"Removing send_daily_summary function at line {i+1}")
            indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith('async def ') or lines[i].strip().startswith('def '):
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    if current_indent <= indent:
                        break
                i += 1
            continue
        
        # Skip daily_calendar_summary task
        if '@tasks.loop' in line and i+1 < len(lines) and 'daily_calendar_summary' in lines[i+1]:
            print(f"Removing daily_calendar_summary task at line {i+1}")
            # Skip the decorator and function
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith('@') or (lines[i].strip().startswith('async def ') and 'before_' not in lines[i]):
                    break
                i += 1
            # Also skip the before_loop for this task
            if i < len(lines) and '@' in lines[i] and 'before_daily_calendar_summary' in lines[i+1]:
                i += 1
                while i < len(lines):
                    if lines[i].strip().startswith('async def ') or lines[i].strip().startswith('def '):
                        current_indent = len(lines[i]) - len(lines[i].lstrip())
                        i += 1
                        while i < len(lines):
                            if lines[i].strip() and not lines[i].strip().startswith('#'):
                                new_indent = len(lines[i]) - len(lines[i].lstrip())
                                if new_indent <= current_indent:
                                    break
                            i += 1
                        break
                    i += 1
            continue
        
        # Skip economic_calendar_scheduler task
        if '@tasks.loop' in line and i+1 < len(lines) and 'economic_calendar_scheduler' in lines[i+1]:
            print(f"Removing economic_calendar_scheduler task at line {i+1}")
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith('@') or (lines[i].strip().startswith('async def ') and 'before_' not in lines[i]):
                    break
                i += 1
            # Skip before_loop
            if i < len(lines) and '@' in lines[i] or 'before_economic_calendar_scheduler' in lines[i]:
                i += 1
                while i < len(lines):
                    if lines[i].strip().startswith('async def ') or lines[i].strip().startswith('def '):
                        current_indent = len(lines[i]) - len(lines[i].lstrip())
                        i += 1
                        while i < len(lines):
                            if lines[i].strip() and not lines[i].strip().startswith('#'):
                                new_indent = len(lines[i]) - len(lines[i].lstrip())
                                if new_indent <= current_indent:
                                    break
                            i += 1
                        break
                    i += 1
            continue
        
        # Skip _check_and_post_event function
        if 'async def _check_and_post_event' in line:
            print(f"Removing _check_and_post_event function at line {i+1}")
            indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines):
                if lines[i].strip().startswith('async def ') or lines[i].strip().startswith('def ') or lines[i].strip().startswith('@commands'):
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    if current_indent <= indent:
                        break
                i += 1
            continue
        
        # Skip test commands for economic calendar
        if '@commands.command' in line and i+1 < len(lines):
            next_line = lines[i+1] if i+1 < len(lines) else ""
            if 'testcalendar' in line or 'schedulenow' in line or 'testcalendar' in next_line or 'schedulenow' in next_line:
                print(f"Removing economic calendar command at line {i+1}")
                # Skip until next @commands or async def setup
                i += 1
                while i < len(lines):
                    if lines[i].strip().startswith('@commands') or lines[i].strip().startswith('async def setup'):
                        break
                    i += 1
                continue
        
        # Skip economic_calendar_channel references in config displays
        if 'economic_calendar_channel' in line and ('embed.add_field' in line or 'config.get' in line):
            # Skip this config display section
            if 'if config.get' in line:
                indent = len(line) - len(line.lstrip())
                i += 1
                while i < len(lines):
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    if lines[i].strip() and current_indent <= indent:
                        break
                    i += 1
                continue
        
        # Skip economic calendar initialization in __init__
        if 'self.event_tasks' in line or 'self.scheduled_events' in line:
            i += 1
            continue
        
        # Skip starting economic calendar tasks in __init__
        if 'daily_calendar_summary.start()' in line or 'economic_calendar_scheduler.start()' in line:
            i += 1
            continue
        
        # Skip cancel calls for economic tasks in cog_unload
        if 'daily_calendar_summary.cancel()' in line or 'economic_calendar_scheduler.cancel()' in line:
            i += 1
            continue
        
        # Keep this line
        keep_lines.append(line)
        i += 1
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(keep_lines)
    
    print(f"\n✅ Removed Economic Calendar features")
    print(f"📄 Original: {len(lines)} lines")
    print(f"📄 New: {len(keep_lines)} lines")
    print(f"🗑️ Removed: {len(lines) - len(keep_lines)} lines")

if __name__ == '__main__':
    input_file = '../cogs/news_cog.py'
    output_file = '../cogs/news_cog_cleaned.py'
    
    print("🔧 Removing Economic Calendar features from news_cog.py...")
    remove_economic_calendar(input_file, output_file)
    print(f"\n✅ Done! New file saved to: {output_file}")
    print("\n⚠️ Please review the new file before replacing the original!")
