"""
Database module for Discord News Bot
SQLite-based persistent storage with atomic operations
"""

import sqlite3
import json
from contextlib import contextmanager
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from logger_config import get_logger

logger = get_logger('database')


class Database:
    """SQLite database manager for bot data"""
    
    def __init__(self, db_path: str = 'data/news_bot.db'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
        logger.info(f"Database initialized at {self.db_path}")
    
    @contextmanager
    def connect(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Enable dict-like row access
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}", exc_info=True)
            raise
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize database schema"""
        with self.connect() as conn:
            # Guild configurations table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS guild_configs (
                    guild_id INTEGER PRIMARY KEY,
                    glassnode_channel INTEGER,
                    santiment_channel INTEGER,
                    phutcrypto_channel INTEGER,
                    theblock_channel INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # RSS feeds table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS rss_feeds (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    channel_id INTEGER NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id) ON DELETE CASCADE,
                    UNIQUE(guild_id, url)
                )
            ''')
            
            # Posted articles table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS posted_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    article_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    title TEXT,
                    url TEXT,
                    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (guild_id) REFERENCES guild_configs(guild_id) ON DELETE CASCADE,
                    UNIQUE(guild_id, article_id, source)
                )
            ''')
            
            # Translation cache table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS translation_cache (
                    text_hash TEXT PRIMARY KEY,
                    original_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_posted_guild_source ON posted_articles(guild_id, source)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_posted_article_id ON posted_articles(article_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_rss_guild ON rss_feeds(guild_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_translation_used ON translation_cache(last_used)')
            
            logger.info("Database schema initialized successfully")
    
    # ==================== Guild Config Methods ====================
    
    def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """Get configuration for a guild"""
        with self.connect() as conn:
            cursor = conn.execute(
                'SELECT * FROM guild_configs WHERE guild_id = ?',
                (guild_id,)
            )
            row = cursor.fetchone()
            
            if row:
                config = dict(row)
                # Load RSS feeds
                config['rss_feeds'] = self.get_rss_feeds(guild_id)
                return config
            else:
                # Return default config
                return {
                    'guild_id': guild_id,
                    'glassnode_channel': None,
                    'santiment_channel': None,
                    'phutcrypto_channel': None,
                    'theblock_channel': None,
                    'rss_feeds': []
                }
    
    def save_guild_config(self, guild_id: int, config: Dict[str, Any]):
        """Save guild configuration"""
        with self.connect() as conn:
            conn.execute('''
                INSERT INTO guild_configs (
                    guild_id, glassnode_channel, santiment_channel, 
                    phutcrypto_channel, theblock_channel, updated_at
                ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(guild_id) DO UPDATE SET
                    glassnode_channel = excluded.glassnode_channel,
                    santiment_channel = excluded.santiment_channel,
                    phutcrypto_channel = excluded.phutcrypto_channel,
                    theblock_channel = excluded.theblock_channel,
                    updated_at = CURRENT_TIMESTAMP
            ''', (
                guild_id,
                config.get('glassnode_channel'),
                config.get('santiment_channel'),
                config.get('5phutcrypto_channel'),  # Note: key mapping
                config.get('theblock_channel')
            ))
            
            logger.debug(f"Saved config for guild {guild_id}")
    
    # ==================== RSS Feed Methods ====================
    
    def get_rss_feeds(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all RSS feeds for a guild"""
        with self.connect() as conn:
            cursor = conn.execute(
                'SELECT id, name, url, channel_id, enabled FROM rss_feeds WHERE guild_id = ? AND enabled = 1',
                (guild_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def add_rss_feed(self, guild_id: int, name: str, url: str, channel_id: int):
        """Add new RSS feed"""
        with self.connect() as conn:
            cursor = conn.execute('''
                INSERT INTO rss_feeds (guild_id, name, url, channel_id)
                VALUES (?, ?, ?, ?)
            ''', (guild_id, name, url, channel_id))
            
            logger.info(f"Added RSS feed '{name}' for guild {guild_id}")
            return cursor.lastrowid
    
    def remove_rss_feed(self, guild_id: int, url: str):
        """Remove RSS feed"""
        with self.connect() as conn:
            conn.execute(
                'UPDATE rss_feeds SET enabled = 0 WHERE guild_id = ? AND url = ?',
                (guild_id, url)
            )
            logger.info(f"Removed RSS feed {url} for guild {guild_id}")
    
    def get_all_rss_feeds(self) -> List[Dict[str, Any]]:
        """Get all RSS feeds across all guilds"""
        with self.connect() as conn:
            cursor = conn.execute('''
                SELECT id as feed_id, guild_id, name as source_name, url, enabled
                FROM rss_feeds
                ORDER BY guild_id, name
            ''')
            return [dict(row) for row in cursor.fetchall()]
    
    def get_all_guild_configs(self) -> List[Dict[str, Any]]:
        """Get all guild configurations"""
        with self.connect() as conn:
            cursor = conn.execute('''
                SELECT guild_id, glassnode_channel, santiment_channel,
                       phutcrypto_channel, theblock_channel
                FROM guild_configs
                ORDER BY guild_id
            ''')
            configs = []
            for row in cursor.fetchall():
                config = dict(row)
                # Get enabled sources (from RSS feeds)
                config['enabled_sources'] = [
                    feed.get('name', feed.get('source_name', 'Unknown'))
                    for feed in self.get_rss_feeds(config['guild_id'])
                ]
                configs.append(config)
            return configs
    
    def delete_rss_feed(self, feed_id: int):
        """Delete RSS feed permanently"""
        with self.connect() as conn:
            conn.execute('DELETE FROM rss_feeds WHERE id = ?', (feed_id,))
            logger.info(f"Deleted RSS feed {feed_id}")
    
    # ==================== Posted Articles Methods ====================
    
    def is_article_posted(self, guild_id: int, article_id: str, source: str) -> bool:
        """Check if article was already posted"""
        with self.connect() as conn:
            cursor = conn.execute(
                'SELECT 1 FROM posted_articles WHERE guild_id = ? AND article_id = ? AND source = ?',
                (guild_id, article_id, source)
            )
            return cursor.fetchone() is not None
    
    def mark_article_posted(self, guild_id: int, article_id: str, source: str, 
                           title: str = None, url: str = None):
        """Mark article as posted"""
        with self.connect() as conn:
            conn.execute('''
                INSERT OR IGNORE INTO posted_articles (guild_id, article_id, source, title, url)
                VALUES (?, ?, ?, ?, ?)
            ''', (guild_id, article_id, source, title, url))
    
    def get_posted_articles(self, guild_id: int, source: str, limit: int = 100) -> List[str]:
        """Get list of posted article IDs for a source"""
        with self.connect() as conn:
            cursor = conn.execute('''
                SELECT article_id FROM posted_articles
                WHERE guild_id = ? AND source = ?
                ORDER BY posted_at DESC
                LIMIT ?
            ''', (guild_id, source, limit))
            return [row['article_id'] for row in cursor.fetchall()]
    
    def cleanup_old_articles(self, days: int = 30):
        """Remove posted articles older than X days"""
        with self.connect() as conn:
            cursor = conn.execute('''
                DELETE FROM posted_articles
                WHERE posted_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            deleted = cursor.rowcount
            logger.info(f"Cleaned up {deleted} old articles (>{days} days)")
            return deleted
    
    # ==================== Translation Cache Methods ====================
    
    def get_translation(self, text_hash: str) -> Optional[str]:
        """Get cached translation"""
        with self.connect() as conn:
            cursor = conn.execute(
                'SELECT translated_text FROM translation_cache WHERE text_hash = ?',
                (text_hash,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update usage stats
                conn.execute('''
                    UPDATE translation_cache
                    SET last_used = CURRENT_TIMESTAMP, use_count = use_count + 1
                    WHERE text_hash = ?
                ''', (text_hash,))
                return row['translated_text']
            
            return None
    
    def save_translation(self, text_hash: str, original: str, translated: str):
        """Save translation to cache"""
        with self.connect() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO translation_cache (text_hash, original_text, translated_text)
                VALUES (?, ?, ?)
            ''', (text_hash, original, translated))
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get translation cache statistics"""
        with self.connect() as conn:
            cursor = conn.execute('SELECT COUNT(*), SUM(use_count) FROM translation_cache')
            row = cursor.fetchone()
            return {
                'total_entries': row[0] or 0,
                'total_uses': row[1] or 0
            }
    
    def cleanup_old_translations(self, days: int = 90):
        """Remove unused translations older than X days"""
        with self.connect() as conn:
            cursor = conn.execute('''
                DELETE FROM translation_cache
                WHERE last_used < datetime('now', '-' || ? || ' days')
            ''', (days,))
            deleted = cursor.rowcount
            logger.info(f"Cleaned up {deleted} old translations (>{days} days)")
            return deleted
    
    # ==================== Statistics Methods ====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall bot statistics"""
        with self.connect() as conn:
            stats = {}
            
            # Total guilds
            cursor = conn.execute('SELECT COUNT(*) FROM guild_configs')
            stats['total_guilds'] = cursor.fetchone()[0]
            
            # Total RSS feeds
            cursor = conn.execute('SELECT COUNT(*) FROM rss_feeds WHERE enabled = 1')
            stats['total_rss_feeds'] = cursor.fetchone()[0]
            
            # Total articles posted
            cursor = conn.execute('SELECT COUNT(*) FROM posted_articles')
            stats['total_articles'] = cursor.fetchone()[0]
            
            # Articles by source
            cursor = conn.execute('''
                SELECT source, COUNT(*) as count
                FROM posted_articles
                GROUP BY source
            ''')
            stats['articles_by_source'] = {row['source']: row['count'] for row in cursor.fetchall()}
            
            # Cache stats
            stats['cache'] = self.get_cache_stats()
            
            return stats
    
    # ==================== Migration Methods ====================
    
    def migrate_from_json(self, config_path: str, last_posts_path: str):
        """Migrate data from old JSON files to database"""
        logger.info("Starting JSON to SQLite migration...")
        
        try:
            # Load old JSON configs
            with open(config_path, 'r', encoding='utf-8') as f:
                old_configs = json.load(f)
            
            with open(last_posts_path, 'r', encoding='utf-8') as f:
                old_posts = json.load(f)
            
            # Migrate configs
            if 'guilds' in old_configs:
                for guild_id_str, config in old_configs['guilds'].items():
                    guild_id = int(guild_id_str)
                    
                    # Save main config
                    self.save_guild_config(guild_id, config)
                    
                    # Migrate RSS feeds
                    for feed in config.get('rss_feeds', []):
                        try:
                            self.add_rss_feed(
                                guild_id,
                                feed['name'],
                                feed['url'],
                                feed['channel_id']
                            )
                        except sqlite3.IntegrityError:
                            # Feed already exists
                            pass
            
            # Migrate posted articles
            if 'guilds' in old_posts:
                for guild_id_str, posts in old_posts['guilds'].items():
                    guild_id = int(guild_id_str)
                    
                    # Migrate each source
                    for source, article_ids in posts.items():
                        if source == 'rss':
                            # Handle RSS feeds
                            for feed_url, ids in article_ids.items():
                                for article_id in ids:
                                    self.mark_article_posted(guild_id, article_id, f'rss:{feed_url}')
                        else:
                            # Handle regular sources
                            for article_id in article_ids:
                                self.mark_article_posted(guild_id, article_id, source)
            
            logger.info("✅ Migration completed successfully!")
            
        except Exception as e:
            logger.error(f"Migration error: {e}", exc_info=True)
            raise


# Global database instance
db = None

def get_database() -> Database:
    """Get global database instance"""
    global db
    if db is None:
        db = Database()
    return db
