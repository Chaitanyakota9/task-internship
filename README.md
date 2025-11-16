# Stock Statistics API

FastAPI REST API for stock statistics with caching and Docker support.

## Features

- REST API with FastAPI
- In-memory caching
- Docker containerization
- Automated testing
- CI/CD pipeline

## Quick Start

```bash
# Local
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python api.py

# Docker
./docker-setup.sh
```

## API Usage

```bash
curl "http://localhost:8000/api/stats?ticker=MSFT&start=2024-01-01&end=2024-12-31"
```

**Response:**
```json
{
  "symbol": "MSFT",
  "high": 468.35,
  "low": 366.5,
  "average_close": 420.31,
  "cache_hit": false
}
```

## Testing

```bash
pytest
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
  - Run smoke tests
  - Send notification
```

**Pipeline execution time:** ~5-7 minutes

MIT License   
