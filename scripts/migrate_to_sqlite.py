"""
Migration script: JSON files → SQLite database
Run this once to migrate existing data
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_database
from logger_config import get_logger

logger = get_logger('migration')


def main():
    """Run migration from JSON to SQLite"""
    print("=" * 60)
    print("Discord Bot: JSON to SQLite Migration")
    print("=" * 60)
    
    # Paths to old JSON files
    config_path = 'data/news_config.json'
    last_posts_path = 'data/last_post_ids.json'
    
    # Check if files exist
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return
    
    if not os.path.exists(last_posts_path):
        print(f"❌ Last posts file not found: {last_posts_path}")
        return
    
    print(f"\n✅ Found JSON files:")
    print(f"   - {config_path}")
    print(f"   - {last_posts_path}")
    
    # Confirm migration
    response = input("\n⚠️  This will migrate data to SQLite. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled.")
        return
    
    print("\n🔄 Starting migration...")
    
    try:
        # Get database instance
        db = get_database()
        
        # Run migration
        db.migrate_from_json(config_path, last_posts_path)
        
        print("\n✅ Migration completed successfully!")
        
        # Show statistics
        stats = db.get_statistics()
        print("\n📊 Database Statistics:")
        print(f"   - Total guilds: {stats['total_guilds']}")
        print(f"   - Total RSS feeds: {stats['total_rss_feeds']}")
        print(f"   - Total articles posted: {stats['total_articles']}")
        print(f"\n   Articles by source:")
        for source, count in stats['articles_by_source'].items():
            print(f"      - {source}: {count}")
        
        # Backup old files
        print("\n💾 Backing up old JSON files...")
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = 'data/backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        shutil.copy(config_path, f"{backup_dir}/news_config_{timestamp}.json.backup")
        shutil.copy(last_posts_path, f"{backup_dir}/last_post_ids_{timestamp}.json.backup")
        
        print(f"   - Backed up to {backup_dir}/")
        
        print("\n✅ All done! Bot is now using SQLite database.")
        print("\n📝 Note: Old JSON files are still in place as backup.")
        print("   You can safely delete them after verifying the bot works correctly.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        print(f"\n❌ Migration failed: {e}")
        print("Check logs for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
