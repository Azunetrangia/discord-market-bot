"""
Smart Rate Limiter
Prevents API rate limit violations with intelligent throttling
"""

import asyncio
from collections import deque
from time import time
from typing import Dict, Optional
from datetime import datetime, timedelta

from logger_config import get_logger

logger = get_logger('rate_limiter')


class RateLimiter:
    """
    Token bucket rate limiter with per-service tracking
    """
    
    def __init__(self, max_calls: int, period: int, name: str = "default"):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed in the period
            period: Time period in seconds
            name: Name of the rate limiter for logging
        """
        self.max_calls = max_calls
        self.period = period
        self.name = name
        self.calls = deque()
        
        # Statistics
        self.total_calls = 0
        self.total_waits = 0
        self.total_wait_time = 0.0
        
        logger.info(f"RateLimiter '{name}' initialized: {max_calls} calls per {period}s")
    
    async def acquire(self) -> float:
        """
        Acquire permission to make an API call
        Returns: wait time in seconds (0 if no wait needed)
        """
        now = time()
        
        # Remove expired calls from tracking
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()
        
        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            # Calculate wait time
            oldest_call = self.calls[0]
            wait_time = self.period - (now - oldest_call)
            
            if wait_time > 0:
                self.total_waits += 1
                self.total_wait_time += wait_time
                logger.debug(f"RateLimiter '{self.name}': Waiting {wait_time:.2f}s (queue: {len(self.calls)}/{self.max_calls})")
                await asyncio.sleep(wait_time)
                now = time()
                
                # Clean up again after waiting
                while self.calls and self.calls[0] < now - self.period:
                    self.calls.popleft()
        
        # Record this call
        self.calls.append(now)
        self.total_calls += 1
        
        return 0.0 if len(self.calls) < self.max_calls else wait_time
    
    def get_stats(self) -> Dict:
        """Get rate limiter statistics"""
        now = time()
        
        # Count calls in current window
        active_calls = sum(1 for call_time in self.calls if call_time > now - self.period)
        
        return {
            'name': self.name,
            'max_calls': self.max_calls,
            'period': self.period,
            'active_calls': active_calls,
            'total_calls': self.total_calls,
            'total_waits': self.total_waits,
            'total_wait_time': round(self.total_wait_time, 2),
            'avg_wait_time': round(self.total_wait_time / self.total_waits, 2) if self.total_waits > 0 else 0,
            'utilization': round((active_calls / self.max_calls) * 100, 1)
        }
    
    def reset(self):
        """Reset rate limiter statistics"""
        self.calls.clear()
        self.total_calls = 0
        self.total_waits = 0
        self.total_wait_time = 0.0
        logger.info(f"RateLimiter '{self.name}' reset")


class MultiServiceRateLimiter:
    """
    Manages multiple rate limiters for different services
    """
    
    def __init__(self):
        self.limiters: Dict[str, RateLimiter] = {}
        logger.info("MultiServiceRateLimiter initialized")
    
    def add_limiter(self, service: str, max_calls: int, period: int):
        """Add a rate limiter for a service"""
        self.limiters[service] = RateLimiter(max_calls, period, service)
        logger.info(f"Added rate limiter for '{service}': {max_calls} calls per {period}s")
    
    async def acquire(self, service: str) -> float:
        """
        Acquire permission for a service
        Returns: wait time in seconds
        """
        if service not in self.limiters:
            logger.warning(f"No rate limiter for '{service}', allowing call")
            return 0.0
        
        return await self.limiters[service].acquire()
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all rate limiters"""
        return {
            service: limiter.get_stats()
            for service, limiter in self.limiters.items()
        }
    
    def reset_all(self):
        """Reset all rate limiters"""
        for limiter in self.limiters.values():
            limiter.reset()
        logger.info("All rate limiters reset")


# Global rate limiter instance
_global_limiter: Optional[MultiServiceRateLimiter] = None


def get_rate_limiter() -> MultiServiceRateLimiter:
    """Get global rate limiter instance (singleton)"""
    global _global_limiter
    
    if _global_limiter is None:
        _global_limiter = MultiServiceRateLimiter()
        
        # Configure default rate limiters for known services
        # Google Translate: 100 requests per minute (free tier estimate)
        _global_limiter.add_limiter('google_translate', max_calls=100, period=60)
        
        # Glassnode: 300 requests per day (free tier)
        _global_limiter.add_limiter('glassnode', max_calls=12, period=3600)  # 12 per hour
        
        # Santiment: 100 requests per day (free tier)
        _global_limiter.add_limiter('santiment', max_calls=4, period=3600)  # 4 per hour
        
        # Generic RSS fetching: Be nice to servers
        _global_limiter.add_limiter('rss_fetch', max_calls=30, period=60)  # 30 per minute
        
        logger.info("Global rate limiter configured with default limits")
    
    return _global_limiter


# Usage example:
async def example_usage():
    """Example of how to use the rate limiter"""
    limiter = get_rate_limiter()
    
    # Before making a translation API call
    await limiter.acquire('google_translate')
    # ... make API call ...
    
    # Get statistics
    stats = limiter.get_all_stats()
    print(stats)


if __name__ == "__main__":
    # Test rate limiter
    async def test():
        limiter = RateLimiter(max_calls=5, period=10, name="test")
        
        print("Making 10 calls (limit: 5 per 10s)...")
        for i in range(10):
            start = time()
            wait_time = await limiter.acquire()
            elapsed = time() - start
            print(f"Call {i+1}: waited {elapsed:.2f}s")
        
        print("\nStatistics:")
        stats = limiter.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    asyncio.run(test())
