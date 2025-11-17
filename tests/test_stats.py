import pytest

from stats import fetch
from cache import make_key, _CACHE


class TestKey:
    
    def test_uppercase(self):
        key = make_key("msft", "2024-01-01", "2024-01-31", None, None)
        assert key[0] == "MSFT"


class TestCalculation:
    
    def setup_method(self):
        _CACHE.clear()
    
    def test_basic(self):
        result = fetch(
            symbol="MSFT",
            start="2024-11-01",
            end="2024-11-05",
            sample_file="data/msft_2024.csv",
            use_cache=False
        )
        
        assert "symbol" in result
        assert "high" in result
        assert "low" in result
        assert "average_close" in result
        assert "cache_hit" in result
        
        assert result["symbol"] == "MSFT"
        assert result["high"] >= result["low"]
        assert result["cache_hit"] is False


class TestCache:
    
    def setup_method(self):
        _CACHE.clear()
    
    def test_hit(self):
        params = {
            "symbol": "AAPL",
            "start": "2024-01-01",
            "end": "2024-01-10",
            "sample_file": "data/aapl_2024.csv"
        }
        
        result1 = fetch(**params)
        assert result1["cache_hit"] is False
        
        result2 = fetch(**params)
        assert result2["cache_hit"] is True


class TestErrors:
    
    def test_file_error(self):
        result = fetch(
            symbol="FAKE",
            start="2024-01-01",
            end="2024-01-31",
            sample_file="data/nonexistent.csv"
        )
        
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
