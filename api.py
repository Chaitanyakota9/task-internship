#!/usr/bin/env python3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
import uvicorn
from datetime import datetime

from stats import get_stock_stats

app = FastAPI(
    title="Stock Statistics API",
    description="Fetch stock statistics on-demand from yfinance",
    version="1.0.0"
)


@app.get("/")
async def root():
    return FileResponse("index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/stats")
async def get_stats(
    ticker: str = Query(..., description="Stock ticker symbol (e.g., MSFT, AAPL)"),
    start: str = Query(..., description="Start date (YYYY-MM-DD format)"),
    end: str = Query(..., description="End date (YYYY-MM-DD format)"),
    timeout: Optional[float] = Query(15.0, description="Request timeout in seconds"),
    use_cache: Optional[bool] = Query(True, description="Use caching for faster responses"),
    refresh_cache: Optional[bool] = Query(False, description="Force refresh cache"),
    sample_file: Optional[str] = Query(None, description="Optional CSV file for offline testing")
):
    try:
        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(end, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD format."
            )
        
        result = get_stock_stats(
            symbol=ticker.upper(),
            start=start,
            end=end,
            timeout=timeout,
            debug=False,
            sample_file=sample_file,
            use_cache=use_cache,
            refresh_cache=refresh_cache
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to fetch data: {result['error']}"
            )
        
        return JSONResponse(content=result, status_code=200)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


if __name__ == "__main__":
    print("🎭 Starting Stock Statistics API...")
    print("📊 API Documentation: http://127.0.0.1:8000/docs")
    print("🔍 Interactive API: http://127.0.0.1:8000/redoc")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
