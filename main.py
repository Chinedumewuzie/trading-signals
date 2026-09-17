"""
FastAPI backend for Trading Signals
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Trading Signals API", version="0.1.0")

# ===== DATA MODELS =====

class SignalResponse(BaseModel):
    symbol: str
    signal: str
    current_price: float
    intrinsic_value: float
    margin_of_safety: float
    graham_score: int
    confidence: float
    timestamp: str

class WatchlistItem(BaseModel):
    symbol: str
    added_at: str

class AnalysisRequest(BaseModel):
    symbol: str
    current_price: float
    current_eps: float
    revenue_per_share: float
    current_ratio: float
    net_working_capital: float
    long_term_debt: float
    years_of_dividends: int
    earnings_deficit_years: int
    eps_growth_rate: float
    nav_per_share: float
    eps_growth_pct: float
    price_to_book: float


# ===== IN-MEMORY STORAGE (MVP) =====
# Replace with PostgreSQL in production

watchlists: Dict[str, List[str]] = {}
signal_history: List[SignalResponse] = []

from graham import GrahamAnalyzer, ValuationEngine, SignalGenerator


# ===== ENDPOINTS =====

@app.get("/health")
def health():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/analyze")
def analyze_stock(request: AnalysisRequest) -> SignalResponse:
    """
    Analyze a stock against Graham's 7 criteria + intrinsic value.

    Returns:
        Signal (BUY/SELL/HOLD/SKIP) with confidence score
    """
    # Prepare stock data
    stock_data = {
        "symbol": request.symbol,
        "stock_price": request.current_price,
        "current_eps": request.current_eps,
        "revenue_per_share": request.revenue_per_share,
        "current_ratio": request.current_ratio,
        "net_working_capital": request.net_working_capital,
        "long_term_debt": request.long_term_debt,
        "years_of_dividends": request.years_of_dividends,
        "earnings_deficit_years": request.earnings_deficit_years,
        "eps_growth_rate": request.eps_growth_rate,
        "nav_per_share": request.nav_per_share,
        "eps_growth_pct": request.eps_growth_pct,
        "price_to_book": request.price_to_book,
    }

    # Analyze
    analyzer = GrahamAnalyzer()
    criteria, graham_score = analyzer.evaluate_stock(stock_data)

    # Valuation
    engine = ValuationEngine()
    iv = engine.calculate_intrinsic_value(
        request.current_eps,
        request.eps_growth_rate
    )

    # Signal
    gen = SignalGenerator()
    signal, ratio = gen.generate_signal(graham_score, iv, request.current_price)
    confidence = gen.calculate_confidence(graham_score, ratio, signal)

    margin_of_safety = ((iv / request.current_price) - 1) * 100 if request.current_price > 0 else 0

    response = SignalResponse(
        symbol=request.symbol,
        signal=signal,
        current_price=request.current_price,
        intrinsic_value=round(iv, 2),
        margin_of_safety=round(margin_of_safety, 2),
        graham_score=graham_score,
        confidence=confidence,
        timestamp=datetime.now().isoformat()
    )

    # Log signal
    signal_history.append(response)

    return response


@app.post("/api/watchlist/add")
def add_to_watchlist(user_id: str, symbol: str):
    """Add stock to user's watchlist"""
    if user_id not in watchlists:
        watchlists[user_id] = []

    if symbol not in watchlists[user_id]:
        watchlists[user_id].append(symbol)

    return {"status": "added", "symbol": symbol, "watchlist": watchlists[user_id]}


@app.delete("/api/watchlist/remove")
def remove_from_watchlist(user_id: str, symbol: str):
    """Remove stock from user's watchlist"""
    if user_id in watchlists and symbol in watchlists[user_id]:
        watchlists[user_id].remove(symbol)

    return {"status": "removed", "symbol": symbol}


@app.get("/api/watchlist/{user_id}")
def get_watchlist(user_id: str) -> List[str]:
    """Get user's watchlist"""
    return watchlists.get(user_id, [])


@app.get("/api/signals/recent")
def get_recent_signals(limit: int = 10) -> List[SignalResponse]:
    """Get recent signals"""
    return signal_history[-limit:]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
