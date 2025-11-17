import pytest
from fastapi.testclient import TestClient

from api import app
from stats import _CACHE

client = TestClient(app)


class TestHealth:
    
    def test_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestStats:
    
    def setup_method(self):
        _CACHE.clear()
    
    def test_offline_data(self):
        response = client.get(
            "/api/stats",
            params={
                "ticker": "MSFT",
                "start": "2024-11-01",
                "end": "2024-11-05",
                "sample_file": "data/msft_2024.csv"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["symbol"] == "MSFT"
        assert data["high"] >= data["low"]
    
    def test_caching(self):
        params = {
            "ticker": "AAPL",
            "start": "2024-01-01",
            "end": "2024-01-10",
            "sample_file": "data/aapl_2024.csv"
        }
        
        response1 = client.get("/api/stats", params=params)
        assert response1.json()["cache_hit"] is False
        
        response2 = client.get("/api/stats", params=params)
        assert response2.json()["cache_hit"] is True


class TestValidation:
    
    def test_missing_params(self):
        response = client.get("/api/stats")
        assert response.status_code == 422
    
    def test_bad_date(self):
        response = client.get(
            "/api/stats",
            params={
                "ticker": "MSFT",
                "start": "01-01-2024",
                "end": "2024-01-31"
            }
        )
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
