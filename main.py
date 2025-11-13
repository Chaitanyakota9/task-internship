import argparse
import json
import sys

from stats import get_stock_stats


def main():
    parser = argparse.ArgumentParser(description="Get stock statistics for a given period.")
    parser.add_argument("--symbol", type=str, required=True, help="Stock symbol, e.g., AAPL or MSFT")
    parser.add_argument("--start", type=str, required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--timeout", type=float, default=15.0, help="Request timeout in seconds")
    parser.add_argument("--debug", action="store_true", help="Enable verbose debugging output")
    parser.add_argument("--sample-file", type=str, help="CSV file to use instead of downloading live data")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching for this request")
    parser.add_argument("--refresh-cache", action="store_true", help="Force refresh cache for this request")
    args = parser.parse_args()

    result = get_stock_stats(
        args.symbol,
        args.start,
        args.end,
        timeout=args.timeout,
        debug=args.debug,
        sample_file=args.sample_file,
        use_cache=not args.no_cache,
        refresh_cache=args.refresh_cache,
    )
    print(json.dumps(result, indent=4))

    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
