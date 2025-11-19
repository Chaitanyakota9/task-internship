from typing import Any, Dict, Optional, Tuple

# CacheKey uniquely identifies a cached response
CacheKey = Tuple[str, str, str, Optional[str], Optional[float]]

# Simple in-memory cache dictionary
Cache: Dict[CacheKey, Dict[str, Any]] = {}


def make_key(
    symbol: str,
    start: str,
    end: str,
    sample_file: Optional[str],
    timeout: Optional[float],
) -> CacheKey:
    # Create a normalized cache key for a given query
    return (symbol.upper(), start, end, sample_file, timeout)


def get_cache(key: CacheKey) -> Optional[Dict[str, Any]]:
    # Return cached value if present
    return Cache.get(key)


def set_cache(key: CacheKey, value: Dict[str, Any]) -> None:
    # Save a value into the cache
    Cache[key] = value


def drop_cache(key: CacheKey) -> None:
    # Remove a single cache entry
    Cache.pop(key, None)


def clear_cache() -> None:
    # Clear all cached entries (mainly used in tests)
    Cache.clear()


