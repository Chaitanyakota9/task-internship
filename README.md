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

## CI/CD Pipeline Setup

**Automated workflow using GitHub Actions:**

```
Trigger: Push to main or Pull Request

Stage 1: Test
  - Checkout repository
  - Setup Python 3.13
  - Install dependencies (pip install -r requirements.txt)
  - Run pytest (14 tests)
  - If tests fail → Stop pipeline

Stage 2: Build
  - Setup Docker Buildx
  - Build image (docker build -t stock-api:latest .)
  - Test container health (docker run + curl /health)
  - If build/health fails → Stop pipeline

Stage 3: Deploy (main branch only)
  - Tag image with version
  - Push to Docker Hub/ECR
  - Deploy to production (AWS ECS/GCP Cloud Run/Azure ACI)
  - Run smoke tests (2 tests: health check + main API endpoint)
  - Send notification
```

**Pipeline execution time:** ~5-7 minutes

MIT License   
