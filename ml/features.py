"""Feature engineering helpers shared between training and inference."""

from __future__ import annotations

import pandas as pd


FEATURE_COLUMNS = [
    "return_1d",
    "rolling_mean_5",
    "rolling_std_5",
    "rolling_mean_20",
    "rolling_std_20",
    "volume_mean_5",
    "volume_std_5",
]  # Order of columns expected by the model


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Given an OHLCV dataframe, compute model features."""
    df = frame.copy()
    features = pd.DataFrame(index=df.index)

    features["return_1d"] = df["Close"].pct_change()
    features["rolling_mean_5"] = df["Close"].rolling(5).mean()
    features["rolling_std_5"] = df["Close"].rolling(5).std()
    features["rolling_mean_20"] = df["Close"].rolling(20).mean()
    features["rolling_std_20"] = df["Close"].rolling(20).std()
    features["volume_mean_5"] = df["Volume"].rolling(5).mean()
    features["volume_std_5"] = df["Volume"].rolling(5).std()

    return features


