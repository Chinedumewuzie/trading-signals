# Trading Signals Platform - MVP Build

**Automated stock analysis & buy/sell signals using Benjamin Graham's value investing framework.**

---

## Quick Start (5 min)

### Prerequisites
- Python 3.9+
- Telegram account (to test bot)
- yfinance (free stock data)

### Installation

```bash
pip install -r requirements.txt
```

### Run Analysis Engine (Local Test)

```bash
python3 graham.py
```

Output:
```
ANALYSIS: AAPL
Graham's 7 Criteria: 6/7
Current Price: $150.00
Intrinsic Value: $187.50
Margin of Safety: +25%
Signal: BUY
Confidence: 78%
```

### Run Unit Tests

```bash
python3 << 'EOF'
from graham import GrahamAnalyzer, ValuationEngine, SignalGenerator
# All core logic is tested in test_analysis.py
EOF
```

---

## Architecture

```
FastAPI Backend (main.py)
├── POST /api/analyze → Graham analysis engine
├── POST /api/watchlist/add → Add stock to watchlist
├── GET /api/watchlist/{user_id} → Get user's stocks
└── GET /api/signals/recent → Recent signals

Telegram Bot (telegram_bot.py)
├── /start → Welcome
├── /add AAPL → Add to watchlist
├── /list → Show watchlist
├── /analyze SYMBOL → Full analysis
└── Daily alerts (5 PM UTC)

Daily Screening Job (daily_screening.py)
├── Fetch data from yfinance for all watched stocks
├── Run Graham analysis on each
├── Generate BUY/SELL/HOLD/SKIP signals
└── Send alerts via Telegram
```

---

## Files

### Core Logic
- **graham.py** — Graham's 7 criteria + intrinsic value calculator (✅ tested)
- **main.py** — FastAPI app with analysis endpoints
- **telegram_bot.py** — Telegram bot interface
- **daily_screening.py** — 5 PM UTC screening job

### Configuration
- **requirements.txt** — Python dependencies
- **.env.example** — Environment variables template
- **test_analysis.py** — Unit tests (all passing)

---

## How It Works

### Phase 1: Graham's 7 Criteria Check
Each stock is evaluated against:
1. Adequate size (revenue/share > $5)
2. Financial strength (current ratio ≥ 2, NWC > debt)
3. Dividend history (5+ years)
4. Earnings stability (no losses in 10 years)
5. 10-year growth (≥ 33% EPS CAGR)
6. Price/NAV ratio (≤ 1.5x)
7. P/B multiple (growth% × P/B ≤ 22.5)

**Pass Threshold: 5/7 criteria**

### Phase 2: Intrinsic Value Calculation
```
IV = Current EPS × (8.5 + 2 × 10-Year Growth Rate)
```

### Phase 3: Signal Generation
```
IF criteria < 5/7:
  Signal = SKIP
ELSE IF IV / Market Price > 1.25:
  Signal = BUY (25% margin of safety)
ELSE IF IV / Market Price < 0.80:
  Signal = SELL (20% overvalued)
ELSE:
  Signal = HOLD
```

---

## Deployment (Production)

### Option 1: Railway.app (Recommended)

1. **Create Railway account** → railway.app
2. **Connect GitHub repo**
3. **Create PostgreSQL instance** (built-in)
4. **Set environment variables**:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token
   DATABASE_URL=postgresql://...
   API_BASE_URL=https://your-domain.com
   ```
5. **Deploy**: Railway auto-deploys on push

### Option 2: Docker (Local or Any Cloud)

```bash
docker-compose up
```

This starts:
- FastAPI on port 8000
- PostgreSQL on port 5432

### Setup Telegram Bot

1. Open Telegram → search `@BotFather`
2. `/newbot` → name your bot
3. Copy bot token
4. Add to `.env` → `TELEGRAM_BOT_TOKEN=your_token`
5. Run bot: `python3 telegram_bot.py`

---

## API Endpoints

### Analyze Stock
```bash
POST /api/analyze
Content-Type: application/json

{
  "symbol": "AAPL",
  "current_price": 150.00,
  "current_eps": 6.05,
  "revenue_per_share": 30.5,
  "current_ratio": 1.1,
  "net_working_capital": 35000000000,
  "long_term_debt": 106000000000,
  "years_of_dividends": 12,
  "earnings_deficit_years": 0,
  "eps_growth_rate": 0.08,
  "nav_per_share": 125.0,
  "eps_growth_pct": 8,
  "price_to_book": 1.2
}

Response:
{
  "symbol": "AAPL",
  "signal": "BUY",
  "current_price": 150.00,
  "intrinsic_value": 187.50,
  "margin_of_safety": 25.0,
  "graham_score": 6,
  "confidence": 0.78,
  "timestamp": "2024-09-17T17:00:00Z"
}
```

### Add to Watchlist
```bash
POST /api/watchlist/add?user_id=123456789&symbol=AAPL

Response:
{
  "status": "added",
  "symbol": "AAPL",
  "watchlist": ["AAPL", "MSFT"]
}
```

### Get Watchlist
```bash
GET /api/watchlist/123456789

Response:
["AAPL", "MSFT", "GOOGL"]
```

---

## Telegram Bot Commands

| Command | Usage | Example |
|---------|-------|---------|
| /start | Welcome message | `/start` |
| /add | Add stock to watchlist | `/add AAPL` |
| /remove | Remove stock | `/remove AAPL` |
| /list | Show all watched stocks | `/list` |
| /analyze | Get full analysis | `/analyze AAPL` |
| /help | Command help | `/help` |

### Alert Format (Daily at 5 PM UTC)
```
✅ SIGNAL: BUY AAPL
================
💰 Current Price: $150.00
📈 Intrinsic Value: $187.50
✨ Margin of Safety: +25%

📋 Graham Criteria: 6/7 ✅
🎯 Confidence: 78%
```

---

## Data Sources

- **Stock Prices & Financials**: yfinance (Yahoo Finance)
- **10-Year History**: yfinance
- **Real-Time Alerts**: Telegram Bot API

---

## Next Steps (V1+)

### Technical Indicators (Week 3-4)
- Add trend filter (SMA 200)
- Add momentum filter (RSI)
- Add volume confirmation

### Dashboard (V1+)
- React frontend at `/dashboard`
- View all watchlist stocks in table
- Click stock → detailed analysis page
- Historical signal performance chart

### Database (V1+)
- Replace in-memory storage with PostgreSQL
- Store signal history for backtesting
- User preferences (alert frequency, thresholds)

### Auto-Trading (Later)
- Connect to broker API (Alpaca, Interactive Brokers)
- Execute trades on user approval (via Telegram)
- Track portfolio performance

---

## Testing

### Unit Tests (All Passing ✅)
```bash
python3 test_analysis.py
```

Tests cover:
- Graham's 7 criteria logic
- Intrinsic value calculation
- CAGR computation
- Signal generation
- Confidence scoring

### Manual Testing
```bash
# Test analysis
python3 graham.py

# Test API
python3 -c "
from main import app
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.post('/api/analyze', json={...})
print(response.json())
"
```

---

## Troubleshooting

### Issue: "No data for SYMBOL"
- Stock symbol may be incorrect (case-sensitive)
- yfinance may be rate-limited
- Network connection issue

### Issue: Telegram bot not responding
- Check `TELEGRAM_BOT_TOKEN` in `.env`
- Bot must be running (`python3 telegram_bot.py`)
- Verify token with `/getMe` in Postman

### Issue: FastAPI won't start
- Check port 8000 is not in use
- Verify `requirements.txt` packages installed
- Check Python version ≥ 3.9

---

## Support

For issues or questions:
1. Check the logs: `python3 main.py` (verbose output)
2. Test in isolation: `python3 graham.py`
3. Verify data: `python3 daily_screening.py`

---

## License

MIT - Use freely for personal/commercial projects.

---

## Attribution

**Benjamin Graham's Value Investing Framework**
- The Intelligent Investor (1949)
- Securities Analysis (1934)

**Data**: Yahoo Finance via yfinance

**Built with**: FastAPI, python-telegram-bot, yfinance
