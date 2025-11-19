"""Simple training script for the RandomForest model."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
import yfinance as yf
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from ml.features import build_features, FEATURE_COLUMNS


def download_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    # Download historical OHLCV data using yfinance
    data = yf.download(
        ticker,
        start=start,
        end=end,
        progress=False,
        auto_adjust=False,
        threads=False,
    )
    if data.empty:
        raise ValueError(f"No data returned for {ticker} between {start} and {end}")
    return data


def train_model(df: pd.DataFrame) -> dict:
    # Train a RandomForest on engineered features and next-day close
    features = build_features(df)
    dataset = features.copy()
    # Target is next day's closing price
    dataset["target"] = df["Close"].shift(-1)
    dataset = dataset.dropna()

    X = dataset[FEATURE_COLUMNS]
    y = dataset["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    return {
        "model": model,
        "features": FEATURE_COLUMNS,
        "metrics": {"mse": float(mse), "r2": float(r2)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Train RandomForest on stock data.")
    parser.add_argument("--ticker", required=True, help="Ticker symbol, e.g. MSFT")
    parser.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    parser.add_argument(
        "--output",
        default="models/stock_model.pkl",
        help="Path to save trained model",
    )
    args = parser.parse_args()

    df = download_data(args.ticker, args.start, args.end)
    payload = train_model(df)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, output_path)

    print(f"Model saved to {output_path}")
    print(f"Metrics: MSE={payload['metrics']['mse']:.4f}, R2={payload['metrics']['r2']:.4f}")


if __name__ == "__main__":
    # Allow running as a script: python -m ml.train_model ...
    main()


