import pytest
import pandas as pd
from fastapi.testclient import TestClient

import api as api_module
from api import app
from cache import Cache

client = TestClient(app)


class TestHealth:
    def test_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestStats:
    def setup_method(self):
        Cache.clear()

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
        Cache.clear()

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
        Cache.clear()

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


class DummyModel:
    def predict(self, X):
        return [123.45] * len(X)


class TestPredict:
    def setup_method(self):
        Cache.clear()
        api_module.MODEL = None
        api_module.FEATURE_COLUMNS = []

    def test_predict_returns_value(self, monkeypatch):
        api_module.MODEL = DummyModel()
        api_module.FEATURE_COLUMNS = ["f1", "f2"]

        dummy_history = pd.DataFrame({"Close": [1, 2, 3], "Volume": [100, 110, 120]})
        dummy_features = pd.DataFrame(
            {"f1": [0.1, 0.2], "f2": [0.3, 0.4]},
            index=pd.date_range("2024-01-01", periods=2, freq="D"),
        )

        monkeypatch.setattr(api_module, "_fetch_history", lambda symbol, days: dummy_history)
        monkeypatch.setattr(api_module, "build_features", lambda history: dummy_features)

        response = client.get("/api/predict", params={"ticker": "AAPL", "lookback": 60})
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] == 123.45
        assert data["ticker"] == "AAPL"

    def test_predict_without_model_fails(self):
        api_module.MODEL = None
        api_module.FEATURE_COLUMNS = []
        response = client.get("/api/predict", params={"ticker": "AAPL"})
        assert response.status_code == 503


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
