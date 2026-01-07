"""
Advanced Caching Utilities
Provides decorators and utilities for Redis caching with TTL and invalidation
"""
from functools import wraps
from typing import Any, Callable, Optional, Union
import json
import hashlib
from app.database.redis_client import get_redis
from app.core.logging import logger
import asyncio

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_parts = []
    
    # Add args
    for arg in args:
        if isinstance(arg, (str, int, float, bool)):
            key_parts.append(str(arg))
        elif isinstance(arg, dict):
            key_parts.append(json.dumps(arg, sort_keys=True))
        else:
            key_parts.append(str(hash(str(arg))))
    
    # Add kwargs
    for k, v in sorted(kwargs.items()):
        if isinstance(v, (str, int, float, bool)):
            key_parts.append(f"{k}:{v}")
        elif isinstance(v, dict):
            key_parts.append(f"{k}:{json.dumps(v, sort_keys=True)}")
        else:
            key_parts.append(f"{k}:{hash(str(v))}")
    
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached(
    ttl: int = 3600,
    key_prefix: str = "",
    invalidate_on: Optional[list] = None
):
    """
    Decorator for caching function results in Redis
    
    Args:
        ttl: Time to live in seconds (default: 1 hour)
        key_prefix: Prefix for cache keys
        invalidate_on: List of cache keys to invalidate when this function is called
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                redis = await get_redis()
                
                # Generate cache key
                func_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
                arg_key = cache_key(*args, **kwargs)
                cache_key_str = f"cache:{func_key}:{arg_key}"
                
                # Try to get from cache
                cached_value = await redis.get(cache_key_str)
                if cached_value:
                    logger.debug(f"Cache hit: {cache_key_str}")
                    return json.loads(cached_value)
                
                # Cache miss - execute function
                logger.debug(f"Cache miss: {cache_key_str}")
                result = await func(*args, **kwargs)
                
                # Store in cache
                await redis.setex(
                    cache_key_str,
                    ttl,
                    json.dumps(result, default=str)
                )
                
                # Invalidate related caches if specified
                if invalidate_on:
                    for key in invalidate_on:
                        pattern = f"cache:{key}:*"
                        keys = await redis.keys(pattern)
                        if keys:
                            await redis.delete(*keys)
                            logger.debug(f"Invalidated cache pattern: {pattern}")
                
                return result
                
            except Exception as e:
                logger.warning(f"Cache error for {func.__name__}: {e}")
                # Fallback to direct execution
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(async_wrapper(*args, **kwargs))
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

async def invalidate_cache(pattern: str):
    """Invalidate all cache keys matching pattern"""
    try:
        redis = await get_redis()
        keys = await redis.keys(f"cache:{pattern}*")
        if keys:
            await redis.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache keys matching pattern: {pattern}")
            return len(keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache invalidation error: {e}")
        return 0

async def get_cache_stats() -> dict:
    """Get cache statistics"""
    try:
        redis = await get_redis()
        info = await redis.info('memory')
        keys = await redis.keys('cache:*')
        
        return {
            'total_keys': len(keys),
            'memory_used': info.get('used_memory_human', 'N/A'),
            'memory_peak': info.get('used_memory_peak_human', 'N/A')
        }
    except Exception as e:
        logger.warning(f"Cache stats error: {e}")
        return {'error': str(e)}

async def clear_all_cache():
    """Clear all cache"""
    try:
        redis = await get_redis()
        keys = await redis.keys('cache:*')
        if keys:
            await redis.delete(*keys)
            logger.info(f"Cleared {len(keys)} cache keys")
            return len(keys)
        return 0
    except Exception as e:
        logger.warning(f"Cache clear error: {e}")
        return 0


