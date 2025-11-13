# CI/CD Pipeline Design

Automated testing, build, and deployment pipeline for Stock Statistics API.

---

## 🎯 Overview

The CI/CD pipeline automates three stages:
1. **Test** - Run automated tests
2. **Build** - Build Docker container
3. **Deploy** - Deploy to production

---

## 📋 Pipeline Stages

### **Stage 1: Test**
```
Trigger: Push to main/master or Pull Request
├─ Checkout code from repository
├─ Set up Python 3.13 environment
├─ Install dependencies (pip install -r requirements.txt)
├─ Run unit tests (test_stats.py)
├─ Run integration tests (test_api.py)
├─ Run data tests (test_datasets.py)
├─ Generate test coverage report
└─ If tests fail → Stop pipeline ❌
```

### **Stage 2: Build**
```
Trigger: Tests pass ✅
├─ Set up Docker environment
├─ Build Docker image from Dockerfile
├─ Tag image: stock-api:latest
├─ Run container locally
├─ Test health endpoint
└─ If build/health fails → Stop pipeline ❌
```

### **Stage 3: Deploy**
```
Trigger: Build succeeds ✅ + On main branch
├─ Push Docker image to registry (Docker Hub / AWS ECR)
├─ Deploy to production server
│  Options:
│  ├─ AWS ECS/Fargate
│  ├─ Google Cloud Run
│  ├─ Azure Container Instances
│  └─ Kubernetes cluster
├─ Run smoke tests on production
└─ Send deployment notification
```

---

## 🔧 Tools & Technologies

| Component | Tool | Purpose |
|-----------|------|---------|
| **CI/CD Platform** | GitHub Actions | Automation |
| **Testing** | pytest | Run tests |
| **Containerization** | Docker | Package app |
| **Registry** | Docker Hub | Store images |
| **Deployment** | AWS/GCP/Azure | Host containers |

---

## 📝 GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Set up Python 3.13
      - Install dependencies
      - Run pytest
      - Generate coverage report

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Set up Docker
      - Build image
      - Test container health
      - Push to registry (if main branch)

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - Pull image from registry
      - Deploy to production
      - Run smoke tests
      - Send notification
```

---

## 🚀 Deployment Options

### **Option 1: AWS ECS/Fargate**
```
1. Push image to AWS ECR
2. Update ECS task definition
3. Deploy new task
4. Route traffic via Load Balancer
```

### **Option 2: Google Cloud Run**
```
1. Push image to Google Container Registry
2. Deploy to Cloud Run
3. Auto-scaling enabled
4. Public URL provided
```

### **Option 3: Azure Container Instances**
```
1. Push image to Azure Container Registry
2. Deploy to ACI
3. Configure networking
4. Set up monitoring
```

---

## 🔐 Security & Secrets

```
Required secrets (stored in GitHub):
├─ DOCKER_USERNAME
├─ DOCKER_PASSWORD
├─ AWS_ACCESS_KEY (if using AWS)
├─ AWS_SECRET_KEY
└─ PRODUCTION_SERVER_URL
```

---

## 📊 Pipeline Flow

```
Developer
    ↓
Push code to GitHub
    ↓
GitHub Actions triggered
    ↓
┌─────────────────┐
│   Run Tests     │ ← Unit, Integration, Data tests
│   14 tests      │
└────────┬────────┘
         │ All pass ✅
         ↓
┌─────────────────┐
│  Build Docker   │ ← Build & test container
│  stock-api:v1.0 │
└────────┬────────┘
         │ Build success ✅
         ↓
┌─────────────────┐
│ Push to Registry│ ← Docker Hub / ECR
│ Tag: latest     │
└────────┬────────┘
         │ Push success ✅
         ↓
┌─────────────────┐
│ Deploy to Prod  │ ← AWS/GCP/Azure
│ Port: 8000      │
└────────┬────────┘
         │ Deploy success ✅
         ↓
    Live in Production! 🎉
```

---

## ⏱️ Pipeline Execution Time

```
Test stage:     ~1-2 minutes
Build stage:    ~2-3 minutes
Deploy stage:   ~1-2 minutes
Total:          ~5-7 minutes
```

---

## ✅ Benefits

1. **Automated Testing** - Catches bugs before deployment
2. **Consistent Builds** - Same environment every time
3. **Fast Feedback** - Know immediately if something breaks
4. **Safe Deployments** - Only deploy if tests pass
5. **Rollback Capability** - Previous images always available

---

## 🎯 For Production

Additional steps to add:
- [ ] Add staging environment
- [ ] Implement blue-green deployment
- [ ] Add performance tests
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure alerts (Slack/Email)
- [ ] Add database migrations
- [ ] Implement secrets management (Vault)

---

**Simple, automated, and reliable!** 🚀

