import json
from copy import deepcopy
from typing import Any, Dict, Optional, Tuple

import pandas as pd

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


def fetch(
    symbol: str,
    start: str,
    end: str,
    *,
    timeout: Optional[float] = None,
    debug: bool = False,
    sample_file: Optional[str] = None,
    use_cache: bool = True,
    refresh_cache: bool = False,
) -> Dict[str, Any]:
    period = {"start": start, "end": end}
    cache_key = make_key(symbol, start, end, sample_file, timeout)

    if refresh_cache:
        if debug:
            print(f"[debug] Refreshing cache for key {cache_key}")
        _CACHE.pop(cache_key, None)

    if use_cache:
        cached = _CACHE.get(cache_key)
        if cached is not None:
            if debug:
                print(f"[debug] Cache hit for key {cache_key}")
            cached_copy = deepcopy(cached)
            cached_copy["cache_hit"] = True
            return cached_copy

    try:
        if sample_file:
            if debug:
                print(f"[debug] Loading sample data from {sample_file}")
            data = pd.read_csv(sample_file, index_col=0, parse_dates=True)
        else:
            if debug:
                print(f"[debug] Downloading data for {symbol} with timeout={timeout}")
            import yfinance as yf
            data = yf.download(
                symbol,
                start=start,
                end=end,
                progress=False,
                timeout=timeout,
                threads=False,
            )
    except Exception as exc:
        if debug:
            print(f"[debug] Failed to download data for {symbol}: {exc}")
        return {"symbol": symbol, "period": period, "error": str(exc)}

    if data.empty:
        if debug:
            print(f"[debug] No data returned for {symbol} between {start} and {end}")
        return {"symbol": symbol, "period": period, "error": "No data found"}

    high = float(data["High"].max())
    low = float(data["Low"].min())
    avg_close = float(data["Close"].mean())
    last_close = float(data["Close"].iloc[-1])

    stats: Dict[str, Any] = {
        "symbol": symbol,
        "period": period,
        "high": round(high, 2),
        "low": round(low, 2),
        "average_close": round(avg_close, 2),
        "last_close": round(last_close, 2),
        "cache_hit": False,
    }

    if use_cache:
        _CACHE[cache_key] = deepcopy(stats)

    if debug:
        print(f"[debug] Computed stats: {json.dumps(stats, indent=2)}")

    return stats
