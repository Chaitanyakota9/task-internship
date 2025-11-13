import pytest
import pandas as pd
import os
from stats import get_stock_stats


class TestDatasetFiles:
    
    def test_all_datasets_exist(self):
        files = [
            "data/msft_2024.csv",
            "data/aapl_2024.csv",
            "data/googl_sample.csv",
            "data/amzn_sample.csv",
            "data/tsla_sample.csv"
        ]
        for file in files:
            assert os.path.exists(file), f"{file} not found"


class TestDatasetStructure:
    
    def test_datasets_have_required_columns(self):
        df = pd.read_csv("data/msft_2024.csv", index_col=0)
        required = ["Open", "High", "Low", "Close", "Volume"]
        for col in required:
            assert col in df.columns


class TestDataQuality:
    
    def test_no_negative_prices(self):
        df = pd.read_csv("data/msft_2024.csv", index_col=0)
        assert (df["High"] > 0).all()
        assert (df["Low"] > 0).all()
    
    def test_high_greater_than_low(self):
        df = pd.read_csv("data/aapl_2024.csv", index_col=0)
        assert (df["High"] >= df["Low"]).all()


class TestDatasetUsability:
    
    def test_datasets_work_with_stats_function(self):
        datasets = [
            ("MSFT", "data/msft_2024.csv"),
            ("AAPL", "data/aapl_2024.csv"),
            ("GOOGL", "data/googl_sample.csv")
        ]
        
        for symbol, file in datasets:
            result = get_stock_stats(
                symbol=symbol,
                start="2024-01-01",
                end="2024-01-10",
                sample_file=file,
                use_cache=False
            )
            assert "error" not in result
            assert result["symbol"] == symbol


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
