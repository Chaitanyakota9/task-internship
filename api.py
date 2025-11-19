from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import Optional, List

import joblib
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import yfinance as yf

# Import local modules for stats and ML features
from stats import fetch
from ml.features import build_features

# Path to the trained RandomForest model
MODEL_PATH = Path("models/stock_model.pkl")
# Global variable that will hold the loaded model
MODEL = None
# List of feature column names expected by the model
FEATURE_COLUMNS: List[str] = []

# Load the model once when the app starts up
if MODEL_PATH.exists():
    payload = joblib.load(MODEL_PATH)
    MODEL = payload.get("model")
    FEATURE_COLUMNS = payload.get("features", [])


# Request body model for batch stats endpoint
class Batch(BaseModel):
    tickers: List[str]
    start: str
    end: str
    timeout: Optional[float] = 15.0
    use_cache: Optional[bool] = True


# Create the FastAPI application
app = FastAPI(
    title="Stock Statistics API",
    description="Fetch stock statistics on-demand from yfinance",
    version="1.0.0",
)
@app.get("/")
async def home():
    # Serve the HTML UI
    return FileResponse("index.html")


@app.get("/health")
async def check():
    # Simple health-check endpoint
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/stats")
async def get_stock(
    ticker: str = Query(..., description="Stock ticker symbol (e.g., MSFT, AAPL)"),
    start: str = Query(..., description="Start date (YYYY-MM-DD format)"),
    end: str = Query(..., description="End date (YYYY-MM-DD format)"),
    timeout: Optional[float] = Query(15.0, description="Request timeout in seconds"),#timeout is the time after which the request will be cancelled if not completed
    use_cache: Optional[bool] = Query(True, description="Use caching for faster responses"),
    refresh_cache: Optional[bool] = Query(False, description="Force refresh cache"),
    sample_file: Optional[str] = Query(None, description="Optional CSV file for offline testing"),
):
    # Get stats for a single ticker over a date range
    try:
        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD format.",
            )

        result = fetch(
            symbol=ticker.upper(),
            start=start,
            end=end,
            timeout=timeout,
            debug=False,  # Suppress debug printing in the API layer
            sample_file=sample_file,
            use_cache=use_cache,
            refresh_cache=refresh_cache,
        )

        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to fetch data: {result['error']}",
            )

        return JSONResponse(content=result, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/stats/batch")  # POST to handle multiple stocks in one request
async def get_many(body: Batch):
    # Get stats for multiple tickers in a single request
    try:
        datetime.strptime(body.start, "%Y-%m-%d")
        datetime.strptime(body.end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD format.",
        )

    # Clean up ticker symbols and take at most 10
    tickers = [t.strip().upper() for t in body.tickers if t.strip()]
    tickers = tickers[:10]  # Limit up to 10 stocks

    if not tickers:
        raise HTTPException(status_code=400, detail="No tickers provided.")

    results = {}
    for symbol in tickers:
        result = fetch(
            symbol=symbol,
            start=body.start,
            end=body.end,
            timeout=body.timeout,
            debug=False,
            sample_file=None,
            use_cache=body.use_cache,
            refresh_cache=False,
        )
        results[symbol] = result

    return {
        "items": results,
        "count": len(results),
        "period": {"start": body.start, "end": body.end},
    }


@app.get("/api/compare")
async def compare(
    tickers: str = Query(..., description="Comma-separated list like AAPL,MSFT,GOOGL"),
    start: str = Query(..., description="Start date (YYYY-MM-DD format)"),
    end: str = Query(..., description="End date (YYYY-MM-DD format)"),
    timeout: Optional[float] = Query(15.0, description="Request timeout in seconds"),
):
    # Compare multiple tickers and calculate extra metrics
    try:
        datetime.strptime(start, "%Y-%m-%d")
        datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD format.",
        )

    # Split the comma-separated string into a list and normalize
    symbols = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    symbols = symbols[:5]  # Limit upto 5 symbols

    if not symbols:
        raise HTTPException(status_code=400, detail="No tickers provided.")

    items = []
    for symbol in symbols:
        result = fetch(
            symbol=symbol,
            start=start,
            end=end,
            timeout=timeout,
            debug=False,
            sample_file=None,
            use_cache=True,
            refresh_cache=False,
        )
        if "error" in result:
            continue

        price_range = result["high"] - result["low"]
        avg = result["average_close"]
        # How wide the high-low range is compared to the average price
        range_percent = (price_range / avg * 100) if avg > 0 else 0.0

        item = dict(result)
        item["range_percent"] = round(range_percent, 2)
        items.append(item)

    if not items:
        raise HTTPException(status_code=404, detail="No data for any ticker.")

    items.sort(key=lambda r: r.get("average_close", 0.0), reverse=True)

    return {
        "items": items,
        "period": {"start": start, "end": end},
        "top_symbol": items[0]["symbol"],
    }
def _fetch_history(symbol: str, days: int) -> pd.DataFrame:
    # Download recent price history for a symbol
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    data = yf.download(
        symbol,
        start=start,
        end=end,
        progress=False,
        auto_adjust=False,
        threads=False,
    )
    return data


@app.get("/api/predict")
async def predict_price(
    ticker: str = Query(..., description="Ticker symbol to run through the model"),
    lookback: int = Query(120, ge=40, le=365, description="Historical days to pull"),
):
    # Predict next-day close price using the trained model
    if MODEL is None or not FEATURE_COLUMNS:
        raise HTTPException(status_code=503, detail="Model not available. Train it first.")

    history = _fetch_history(ticker.upper(), lookback + 40)
    if history.empty:
        raise HTTPException(status_code=404, detail="Unable to download market data.")

    features = build_features(history).dropna()
    rows = features.tail(lookback)
    if rows.empty:
        raise HTTPException(status_code=400, detail="Not enough data to build features.")

    try:
        matrix = rows[FEATURE_COLUMNS]
    except KeyError as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Missing feature column {exc} in computed data.",
        ) from exc

    preds = MODEL.predict(matrix)
    if len(preds) == 0:
        raise HTTPException(status_code=500, detail="Model returned no predictions.")
    prediction = float(sum(preds) / len(preds))

    return {
        "ticker": ticker.upper(),
        "prediction": round(prediction, 4),
        "as_of": rows.index[-1].strftime("%Y-%m-%d"),
        "features_used": FEATURE_COLUMNS,
    }


if __name__ == "__main__":
    # Run the API directly with `python api.py`
    print(" Starting Stock Statistics API...")
    print(" API Documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
