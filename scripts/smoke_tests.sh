#!/bin/bash

# Smoke tests for deployment verification
set -e

API_URL="${API_URL:-http://localhost:8000}"

# Test 1: Health endpoint
curl -f "${API_URL}/health" > /dev/null || exit 1

# Test 2: Main API endpoint
curl -f "${API_URL}/api/stats?ticker=MSFT&start=2024-01-01&end=2024-01-10&sample_file=data/msft_2024.csv" > /dev/null || exit 1

echo "Smoke tests passed"

