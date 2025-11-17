# Stock Statistics API

Simple FastAPI REST API for stock statistics with caching and Docker support.

## Features

- Clean REST API with FastAPI
- Persistent caching with 1-hour TTL
- Batch queries (up to 10 stocks)
- Stock comparison endpoint
- Docker support
- Comprehensive tests

## Quick Start

```bash
# Local setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api.py

# Docker
./scripts/docker-setup.sh
```

## API Endpoints

### Get Single Stock Stats
```bash
curl "http://localhost:8000/api/stats?ticker=MSFT&start=2024-01-01&end=2024-12-31"
```

### Compare Multiple Stocks
```bash
curl "http://localhost:8000/api/compare?tickers=AAPL,MSFT,GOOGL&start=2024-01-01&end=2024-12-31"
```

### Batch Query
```bash
curl -X POST "http://localhost:8000/api/stats/batch" \
  -H "Content-Type: application/json" \
  -d '{"tickers": ["AAPL", "MSFT"], "start": "2024-01-01", "end": "2024-12-31"}'
```

## Testing

### Unit Tests
```bash
pytest
```

### Smoke Tests
Smoke tests verify basic functionality after deployment. These are run in the CI/CD pipeline:

1. **Health Endpoint** - `GET /health` returns healthy status
2. **Main API Endpoint** - `GET /api/stats` with sample data returns valid response

For local testing:
```bash
./scripts/smoke_tests.sh
```

## Project Structure

```
├── api.py           # Main API (run this!)
├── stats.py         # Stock statistics logic
├── tests/           # Test files
├── scripts/         # Helper scripts
│   ├── docker-setup.sh    # Docker setup script
│   ├── run_tests.sh       # Test runner script
│   └── smoke_tests.sh     # Smoke tests for deployment
├── data/            # Sample CSV files
└── index.html       # Web interface
```

## Docker Installation & Startup

**Prerequisites:** Docker installed, port 8000 available

**Build & Run:**
```bash
docker build -t stock-api:latest .
docker run -d -p 8000:8000 --name stock-api-container stock-api:latest
```

**Verify:**
```bash
docker ps
curl http://localhost:8000/health
```

**Access:** http://localhost:8000

**Manage:**
```bash
docker stop stock-api-container
docker start stock-api-container
docker logs -f stock-api-container
docker rm -f stock-api-container
```

## CI/CD Pipeline

**Current setup:**
- Unit tests run via pytest (14 tests)
- Docker image can be built locally
- Smoke tests available for deployment verification

**To set up CI/CD:**
1. Create `.github/workflows/ci-cd.yml` for automated testing
2. Configure Docker Hub/registry credentials if needed
3. Set up deployment targets (AWS ECS, GCP Cloud Run, etc.) as required

**Smoke tests (2 tests):**
- Health endpoint check
- Main API endpoint verification

MIT License   
