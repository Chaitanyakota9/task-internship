from typing import Any, Dict, Optional, Tuple


CacheKey = Tuple[str, str, str, Optional[str], Optional[float]]

_CACHE: Dict[CacheKey, Dict[str, Any]] = {}


def make_key(
    symbol: str,
    start: str,
    end: str,
    sample_file: Optional[str],
    timeout: Optional[float],
) -> CacheKey:
    return (symbol.upper(), start, end, sample_file, timeout)


def get_cache(key: CacheKey) -> Optional[Dict[str, Any]]:
    return _CACHE.get(key)


def set_cache(key: CacheKey, value: Dict[str, Any]) -> None:
    _CACHE[key] = value


def drop_cache(key: CacheKey) -> None:
    _CACHE.pop(key, None)


def clear_cache() -> None:
    _CACHE.clear()


