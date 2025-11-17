import pytest
import pandas as pd
import os
import sys
sys.path.insert(0, '..')

from stats import fetch


class TestFiles:
    
    def test_exist(self):
        files = [
            "data/msft_2024.csv",
            "data/aapl_2024.csv",
            "data/googl_sample.csv",
            "data/amzn_sample.csv",
            "data/tsla_sample.csv"
        ]
        for file in files:
            assert os.path.exists(file), f"{file} not found"


class TestStructure:
    
    def test_columns(self):
        df = pd.read_csv("data/msft_2024.csv", index_col=0)
        required = ["Open", "High", "Low", "Close", "Volume"]
        for col in required:
            assert col in df.columns


class TestQuality:
    
    def test_prices(self):
        df = pd.read_csv("data/msft_2024.csv", index_col=0)
        assert (df["High"] > 0).all()
        assert (df["Low"] > 0).all()
    
    def test_range(self):
        df = pd.read_csv("data/aapl_2024.csv", index_col=0)
        assert (df["High"] >= df["Low"]).all()


class TestUsability:
    
    def test_fetch(self):
        datasets = [
            ("MSFT", "data/msft_2024.csv"),
            ("AAPL", "data/aapl_2024.csv"),
            ("GOOGL", "data/googl_sample.csv")
        ]
        
        for symbol, file in datasets:
            result = fetch(
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
