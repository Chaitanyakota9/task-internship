# Stock Statistics API 📊

A FastAPI-based REST API that fetches stock statistics on-demand from yfinance with intelligent caching.

## Features

✅ **On-demand data fetching** from yfinance  
✅ **Intelligent caching** for faster subsequent requests  
✅ **Offline testing** with CSV sample files  
✅ **Lazy imports** - yfinance only loads when needed  
✅ **Clean API design** with automatic documentation  

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the API

### Start the Server

```bash
python api.py
```

The API will start on `http://127.0.0.1:8000`

### Access Documentation

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API Endpoints

### GET `/api/stats`

Fetch stock statistics for a given ticker and date range.

**Query Parameters:**
- `ticker` (required): Stock ticker symbol (e.g., MSFT, AAPL)
- `start` (required): Start date in YYYY-MM-DD format
- `end` (required): End date in YYYY-MM-DD format
- `timeout` (optional): Request timeout in seconds (default: 15.0)
- `use_cache` (optional): Enable caching (default: true)
- `refresh_cache` (optional): Force refresh cache (default: false)
- `sample_file` (optional): Path to CSV file for offline testing

**Example Request:**

```bash
# Live data from yfinance
curl "http://127.0.0.1:8000/api/stats?ticker=MSFT&start=2023-01-01&end=2023-12-31"

# Offline testing with CSV
curl "http://127.0.0.1:8000/api/stats?ticker=MSFT&start=2024-11-01&end=2024-11-05&sample_file=data/msft_2024.csv"
```

**Example Response:**

```json
{
  "symbol": "MSFT",
  "period": {
    "start": "2024-11-01",
    "end": "2024-11-05"
  },
  "high": 468.35,
  "low": 366.5,
  "average_close": 420.31,
  "last_close": 421.5,
  "cache_hit": false
}
```

### GET `/health`

Health check endpoint.

```bash
curl "http://127.0.0.1:8000/health"
```

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-11-12T17:30:00.000000"
}
```

## CLI Tool

You can also use the command-line interface:

```bash
python main.py --symbol MSFT --start 2024-11-01 --end 2024-11-05 --debug
```

**CLI Options:**
- `--symbol`: Stock ticker symbol
- `--start`: Start date (YYYY-MM-DD)
- `--end`: End date (YYYY-MM-DD)
- `--timeout`: Request timeout in seconds
- `--debug`: Enable debug output
- `--sample-file`: Path to CSV file for offline testing
- `--no-cache`: Disable caching
- `--refresh-cache`: Force refresh cache

## Data Files

The `data/` directory contains sample CSV files for offline testing:

- `msft_2024.csv` - Full 2024 MSFT data (252 trading days)
- `aapl_2024.csv` - Full 2024 AAPL data (252 trading days)
- `amzn_sample.csv` - Sample AMZN data
- `googl_sample.csv` - Sample GOOGL data
- `tsla_sample.csv` - Sample TSLA data

## Caching

The API implements intelligent caching:

- **Cache Key**: `(symbol, start_date, end_date, sample_file, timeout)`
- **Cache Hit**: Returns `"cache_hit": true` for cached responses
- **Cache Miss**: Returns `"cache_hit": false` for fresh data

Subsequent requests with the same parameters return instantly from cache!

## Performance

- **Lazy Import**: yfinance only loads when making network requests
- **Instant Offline Mode**: CSV files load in <1ms
- **Cached Responses**: Return in <1ms after first request

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Invalid date format or parameters
- `404`: Data not found for the given ticker/date range
- `500`: Internal server error

## License

MIT License

