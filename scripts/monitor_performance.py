"""
Performance monitoring script
Tracks cache hit rate, database performance, and bot health
Run this alongside the bot to collect 24-hour statistics
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_database
from translation_cache import get_translation_cache
from logger_config import get_logger

logger = get_logger('monitor')


class PerformanceMonitor:
    """Monitor bot performance metrics"""
    
    def __init__(self, output_file='logs/performance_report.json'):
        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.db = get_database()
        self.cache = get_translation_cache()
        self.start_time = datetime.now()
        self.snapshots = []
    
    def take_snapshot(self):
        """Capture current performance snapshot"""
        now = datetime.now()
        
        # Database stats
        db_stats = self.db.get_statistics()
        
        # Cache stats
        cache_stats = self.cache.get_stats()
        
        # Create snapshot
        snapshot = {
            'timestamp': now.isoformat(),
            'uptime_seconds': (now - self.start_time).total_seconds(),
            'database': {
                'total_guilds': db_stats['total_guilds'],
                'total_rss_feeds': db_stats['total_rss_feeds'],
                'total_articles': db_stats['total_articles'],
                'articles_by_source': db_stats['articles_by_source']
            },
            'cache': {
                'session_hits': cache_stats['session_hits'],
                'session_misses': cache_stats['session_misses'],
                'session_hit_rate': cache_stats['session_hit_rate'],
                'total_cached': cache_stats['total_cached'],
                'total_uses': cache_stats['total_uses']
            }
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def save_report(self):
        """Save performance report to file"""
        report = {
            'monitoring_started': self.start_time.isoformat(),
            'monitoring_ended': datetime.now().isoformat(),
            'total_snapshots': len(self.snapshots),
            'snapshots': self.snapshots
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Performance report saved to {self.output_file}")
    
    def print_summary(self):
        """Print performance summary"""
        if not self.snapshots:
            print("No data collected yet")
            return
        
        latest = self.snapshots[-1]
        first = self.snapshots[0]
        
        print("\n" + "=" * 70)
        print("PERFORMANCE MONITORING SUMMARY")
        print("=" * 70)
        
        # Uptime
        uptime = timedelta(seconds=latest['uptime_seconds'])
        print(f"\n⏱️  Monitoring Duration: {uptime}")
        print(f"📊 Snapshots Collected: {len(self.snapshots)}")
        
        # Database growth
        print("\n📁 DATABASE METRICS:")
        articles_added = (latest['database']['total_articles'] - 
                         first['database']['total_articles'])
        print(f"   • Total Articles: {latest['database']['total_articles']}")
        print(f"   • Articles Added: +{articles_added}")
        print(f"   • Active Guilds: {latest['database']['total_guilds']}")
        print(f"   • RSS Feeds: {latest['database']['total_rss_feeds']}")
        
        # Cache performance
        print("\n🚀 CACHE PERFORMANCE:")
        hit_rate = latest['cache']['session_hit_rate']
        print(f"   • Hit Rate: {hit_rate:.1f}%")
        print(f"   • Cache Hits: {latest['cache']['session_hits']}")
        print(f"   • Cache Misses: {latest['cache']['session_misses']}")
        print(f"   • Total Cached Entries: {latest['cache']['total_cached']}")
        print(f"   • Total Cache Uses: {latest['cache']['total_uses']}")
        
        # Calculate average hit rate if multiple snapshots
        if len(self.snapshots) > 1:
            avg_hit_rate = sum(s['cache']['session_hit_rate'] 
                             for s in self.snapshots) / len(self.snapshots)
            print(f"   • Average Hit Rate: {avg_hit_rate:.1f}%")
        
        # Cache efficiency
        if latest['cache']['session_misses'] > 0:
            api_calls_saved = latest['cache']['session_hits']
            total_requests = latest['cache']['session_hits'] + latest['cache']['session_misses']
            print(f"\n💰 COST SAVINGS:")
            print(f"   • API Calls Saved: {api_calls_saved} out of {total_requests}")
            print(f"   • Efficiency: {hit_rate:.1f}% reduction in API usage")
        
        # Articles by source
        print("\n📰 ARTICLES BY SOURCE:")
        for source, count in sorted(latest['database']['articles_by_source'].items()):
            print(f"   • {source}: {count}")
        
        print("\n" + "=" * 70)
        print(f"📄 Full report: {self.output_file}")
        print("=" * 70 + "\n")
    
    def monitor_continuous(self, interval_minutes=30, duration_hours=24):
        """Monitor continuously for specified duration"""
        end_time = datetime.now() + timedelta(hours=duration_hours)
        snapshot_count = 0
        
        print("=" * 70)
        print("PERFORMANCE MONITORING STARTED")
        print("=" * 70)
        print(f"Duration: {duration_hours} hours")
        print(f"Snapshot Interval: {interval_minutes} minutes")
        print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        print("\nMonitoring... (Press Ctrl+C to stop early)\n")
        
        try:
            while datetime.now() < end_time:
                # Take snapshot
                snapshot = self.take_snapshot()
                snapshot_count += 1
                
                # Log progress
                logger.info(f"Snapshot {snapshot_count} taken")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Snapshot {snapshot_count} - "
                      f"Hit Rate: {snapshot['cache']['session_hit_rate']:.1f}% - "
                      f"Articles: {snapshot['database']['total_articles']}")
                
                # Save after each snapshot
                self.save_report()
                
                # Sleep until next snapshot
                time.sleep(interval_minutes * 60)
            
            print("\n✅ Monitoring completed!")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Monitoring stopped by user")
        
        finally:
            # Final snapshot and report
            self.take_snapshot()
            self.save_report()
            self.print_summary()
    
    def monitor_once(self):
        """Take a single snapshot and print summary"""
        print("Taking performance snapshot...\n")
        self.take_snapshot()
        self.save_report()
        self.print_summary()


def main():
    """Main monitoring function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor Discord bot performance')
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Run continuous monitoring')
    parser.add_argument('--interval', '-i', type=int, default=30,
                       help='Snapshot interval in minutes (default: 30)')
    parser.add_argument('--duration', '-d', type=int, default=24,
                       help='Monitoring duration in hours (default: 24)')
    parser.add_argument('--output', '-o', default='logs/performance_report.json',
                       help='Output file path')
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = PerformanceMonitor(output_file=args.output)
    
    if args.continuous:
        # Continuous monitoring
        monitor.monitor_continuous(
            interval_minutes=args.interval,
            duration_hours=args.duration
        )
    else:
        # One-time snapshot
        monitor.monitor_once()


if __name__ == '__main__':
    main()
