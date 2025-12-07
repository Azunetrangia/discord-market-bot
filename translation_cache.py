"""
Translation cache system with hash-based storage
Reduces API calls to Google Translate by 70-90%
"""

import hashlib
from typing import Optional
from datetime import datetime

from logger_config import get_logger
from database import get_database

logger = get_logger('translation_cache')


class TranslationCache:
    """Cache for translated texts to reduce API calls"""
    
    def __init__(self):
        self.db = get_database()
        self.hit_count = 0
        self.miss_count = 0
        self.session_start = datetime.now()
    
    def _hash_text(self, text: str) -> str:
        """Generate hash for text"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[str]:
        """Get cached translation"""
        text_hash = self._hash_text(text)
        translation = self.db.get_translation(text_hash)
        
        if translation:
            self.hit_count += 1
            logger.debug(f"Cache HIT for text hash {text_hash[:8]}...")
            return translation
        else:
            self.miss_count += 1
            logger.debug(f"Cache MISS for text hash {text_hash[:8]}...")
            return None
    
    def set(self, text: str, translation: str):
        """Save translation to cache"""
        text_hash = self._hash_text(text)
        self.db.save_translation(text_hash, text, translation)
        logger.debug(f"Cached translation {text_hash[:8]}... ({len(text)} chars)")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        db_stats = self.db.get_cache_stats()
        
        return {
            'session_hits': self.hit_count,
            'session_misses': self.miss_count,
            'session_total': total_requests,
            'session_hit_rate': hit_rate,
            'total_cached': db_stats['total_entries'],
            'total_uses': db_stats['total_uses'],
            'session_duration': (datetime.now() - self.session_start).total_seconds()
        }
    
    def print_stats(self):
        """Print cache statistics"""
        stats = self.get_stats()
        
        logger.info("=" * 50)
        logger.info("Translation Cache Statistics")
        logger.info("=" * 50)
        logger.info(f"Session Duration: {stats['session_duration']:.1f}s")
        logger.info(f"Session Hits: {stats['session_hits']}")
        logger.info(f"Session Misses: {stats['session_misses']}")
        logger.info(f"Session Hit Rate: {stats['session_hit_rate']:.1f}%")
        logger.info(f"Total Cached Entries: {stats['total_cached']}")
        logger.info(f"Total Cache Uses: {stats['total_uses']}")
        logger.info("=" * 50)
    
    def clear_old_cache(self, days: int = 90):
        """Clear cache entries older than X days"""
        deleted = self.db.cleanup_old_translations(days)
        logger.info(f"Cleared {deleted} old cache entries (>{days} days)")
        return deleted


# Global cache instance
_cache = None

def get_translation_cache() -> TranslationCache:
    """Get global translation cache instance"""
    global _cache
    if _cache is None:
        _cache = TranslationCache()
    return _cache
