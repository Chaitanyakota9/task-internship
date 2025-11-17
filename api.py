from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional, List
from pydantic import BaseModel
import uvicorn
from datetime import datetime

from stats import fetch


class Batch(BaseModel):
    tickers: List[str]
    start: str
    end: str
    timeout: Optional[float] = 15.0
    use_cache: Optional[bool] = True


app = FastAPI(
    title="Stock Statistics API",
    description="Fetch stock statistics on-demand from yfinance",
    version="1.0.0",
)


@app.get("/")
async def home():
    return FileResponse("index.html")


@app.get("/health")
async def check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/stats")
async def get_stock(
    ticker: str = Query(..., description="Stock ticker symbol (e.g., MSFT, AAPL)"),
    start: str = Query(..., description="Start date (YYYY-MM-DD format)"),
    end: str = Query(..., description="End date (YYYY-MM-DD format)"),
    timeout: Optional[float] = Query(15.0, description="Request timeout in seconds"),
    use_cache: Optional[bool] = Query(True, description="Use caching for faster responses"),
    refresh_cache: Optional[bool] = Query(False, description="Force refresh cache"),
    sample_file: Optional[str] = Query(None, description="Optional CSV file for offline testing"),
):
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
            debug=False,
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


@app.post("/api/stats/batch")
async def get_many(body: Batch):
    try:
        datetime.strptime(body.start, "%Y-%m-%d")
        datetime.strptime(body.end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD format.",
        )

    tickers = [t.strip().upper() for t in body.tickers if t.strip()]
    tickers = tickers[:10]

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
    try:
        datetime.strptime(start, "%Y-%m-%d")
        datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD format.",
        )

    symbols = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    symbols = symbols[:5]

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


if __name__ == "__main__":
    print(" Starting Stock Statistics API...")
    print(" API Documentation: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
