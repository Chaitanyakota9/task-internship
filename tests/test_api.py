import pytest
from fastapi.testclient import TestClient

import api as api_module
from api import app
from cache import _CACHE

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
                "sample_file": "data/msft_2024.csv",
            },
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
            "sample_file": "data/aapl_2024.csv",
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
                "end": "2024-01-31",
            },
        )
        assert response.status_code == 400


class TestBatch:
    def setup_method(self):
        _CACHE.clear()

    def test_batch_uses_body_and_returns_items(self, monkeypatch):
        def fake_fetch(symbol, start, end, timeout=None, debug=False,
                       sample_file=None, use_cache=True, refresh_cache=False):
            return {
                "symbol": symbol,
                "period": {"start": start, "end": end},
                "high": 10.0,
                "low": 5.0,
                "average_close": 7.5,
                "last_close": 8.0,
                "cache_hit": False,
            }

        monkeypatch.setattr(api_module, "fetch", fake_fetch)

        body = {
            "tickers": ["AAPL", "MSFT"],
            "start": "2024-01-01",
            "end": "2024-01-10",
        }

        response = client.post("/api/stats/batch", json=body)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert set(data["items"].keys()) == {"AAPL", "MSFT"}
        assert data["period"]["start"] == "2024-01-01"
        assert data["period"]["end"] == "2024-01-10"


class TestCompare:
    def setup_method(self):
        _CACHE.clear()

    def test_compare_sorts_by_average_and_sets_range(self, monkeypatch):
        def fake_fetch(symbol, start, end, timeout=None, debug=False,
                       sample_file=None, use_cache=True, refresh_cache=False):
            if symbol == "AAPL":
                avg = 20.0
            else:
                avg = 10.0
            return {
                "symbol": symbol,
                "period": {"start": start, "end": end},
                "high": avg + 5.0,
                "low": avg - 5.0,
                "average_close": avg,
                "last_close": avg,
                "cache_hit": False,
            }

        monkeypatch.setattr(api_module, "fetch", fake_fetch)

        params = {
            "tickers": "AAPL,MSFT",
            "start": "2024-01-01",
            "end": "2024-01-10",
        }
        response = client.get("/api/compare", params=params)

        assert response.status_code == 200
        data = response.json()
        items = data["items"]

        # AAPL should be first because it has higher average_close
        assert items[0]["symbol"] == "AAPL"
        assert data["top_symbol"] == "AAPL"

        # each item should include range_percent
        for item in items:
            assert "range_percent" in item


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
