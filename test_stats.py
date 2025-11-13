import pytest
from stats import get_stock_stats, _make_cache_key, _CACHE


class TestCacheKey:
    
    def test_cache_key_uppercase(self):
        key = _make_cache_key("msft", "2024-01-01", "2024-01-31", None, None)
        assert key[0] == "MSFT"


class TestStatsCalculation:
    
    def setup_method(self):
        _CACHE.clear()
    
    def test_basic_stats_calculation(self):
        result = get_stock_stats(
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


class TestCaching:
    
    def setup_method(self):
        _CACHE.clear()
    
    def test_cache_hit_on_second_request(self):
        params = {
            "symbol": "AAPL",
            "start": "2024-01-01",
            "end": "2024-01-10",
            "sample_file": "data/aapl_2024.csv"
        }
        
        result1 = get_stock_stats(**params)
        assert result1["cache_hit"] is False
        
        result2 = get_stock_stats(**params)
        assert result2["cache_hit"] is True


class TestErrorHandling:
    
    def test_file_not_found(self):
        result = get_stock_stats(
            symbol="FAKE",
            start="2024-01-01",
            end="2024-01-31",
            sample_file="data/nonexistent.csv"
        )
        
        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
