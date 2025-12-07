"""
Utility functions for Discord News Bot
Includes retry logic with exponential backoff
"""

import asyncio
import functools
from typing import Callable, Any
from datetime import datetime
import pytz

# Import logger
try:
    from logger_config import get_logger
    logger = get_logger('utils')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
) -> Callable:
    """
    Decorator for retrying async functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff calculation
    
    Example:
        @retry_with_backoff(max_retries=3, base_delay=1)
        async def fetch_api():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Log success if it's a retry
                    if attempt > 0:
                        logger.info(f"✅ {func.__name__} succeeded on attempt {attempt + 1}/{max_retries}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"⚠️ {func.__name__} failed (attempt {attempt + 1}/{max_retries}): {str(e)[:100]}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"❌ {func.__name__} failed after {max_retries} attempts: {str(e)[:200]}"
                        )
            
            # All retries exhausted, raise the last exception
            raise last_exception
        
        return wrapper
    return decorator


def get_vietnam_time() -> datetime:
    """Get current time in Vietnam timezone (UTC+7)"""
    VN_TZ = pytz.timezone('Asia/Ho_Chi_Minh')
    return datetime.now(VN_TZ)


def format_timestamp(dt: datetime, format_str: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """
    Truncate text to max_length, adding suffix if truncated
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: String to append if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def safe_get(dictionary: dict, *keys, default=None) -> Any:
    """
    Safely get nested dictionary values
    
    Example:
        safe_get(data, 'user', 'profile', 'name', default='Unknown')
    """
    current = dictionary
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.now()
        
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls 
                      if (now - call_time).total_seconds() < 60]
        
        # If at limit, wait
        if len(self.calls) >= self.calls_per_minute:
            oldest_call = min(self.calls)
            wait_time = 60 - (now - oldest_call).total_seconds()
            
            if wait_time > 0:
                logger.info(f"⏳ Rate limit reached. Waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                self.calls = []
        
        # Record this call
        self.calls.append(now)


# Global rate limiters for different services
glassnode_limiter = RateLimiter(calls_per_minute=30)
santiment_limiter = RateLimiter(calls_per_minute=30)
theblock_limiter = RateLimiter(calls_per_minute=60)
phutcrypto_limiter = RateLimiter(calls_per_minute=60)
rss_limiter = RateLimiter(calls_per_minute=100)

# Dictionary for easy access
rate_limiters = {
    'glassnode': glassnode_limiter,
    'santiment': santiment_limiter,
    'theblock': theblock_limiter,
    '5phutcrypto': phutcrypto_limiter,
    'rss': rss_limiter
}
