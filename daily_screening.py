"""
Daily Screening Job - Runs at 5 PM UTC
Fetches data, analyzes all watched stocks, generates signals
"""

import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import numpy as np

from graham import GrahamAnalyzer, ValuationEngine, SignalGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StockDataFetcher:
    """Fetch stock data from yfinance"""

    @staticmethod
    def fetch_stock_data(symbol: str) -> Dict:
        """
        Fetch comprehensive stock data for analysis

        Returns:
            Dict with all data needed for Graham analysis
        """
        try:
            # Download price history (for CAGR calculation)
            hist = yf.download(symbol, period="10y", progress=False)

            if hist.empty:
                logger.warning(f"No data for {symbol}")
                return None

            # Get stock info
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Extract relevant fields
            current_price = info.get("currentPrice") or hist['Close'].iloc[-1]

            # EPS data
            eps_current = info.get("trailingEps", 0)
            eps_history = info.get("epsCurrentYear", eps_current)

            # Historical EPS for 10-year CAGR
            try:
                earnings_dates = ticker.earnings_dates
                if earnings_dates is not None and len(earnings_dates) >= 2:
                    # Use earnings data to estimate EPS history
                    eps_10y_ago = eps_current * 0.7  # Rough estimate
                else:
                    eps_10y_ago = eps_current * 0.7
            except:
                eps_10y_ago = eps_current * 0.7

            # Financial metrics
            market_cap = info.get("marketCap", 0)
            shares_outstanding = info.get("sharesOutstanding", 1)
            revenue = info.get("totalRevenue", 0)
            revenue_per_share = revenue / shares_outstanding if shares_outstanding > 0 else 0

            # Balance sheet
            current_assets = info.get("currentAssets", 0)
            current_liabilities = info.get("currentLiabilities", 1)
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0

            total_assets = info.get("totalAssets", 0)
            total_liabilities = info.get("totalLiab", 0)
            current_debt = info.get("shortTermDebt", 0)
            long_term_debt = info.get("longTermDebt", 0)

            nwc = current_assets - current_liabilities

            # Book value
            book_value = info.get("bookValue", 0)
            nav_per_share = book_value

            # Dividend data
            try:
                dividends = ticker.dividends
                years_of_dividends = len(dividends) // 4 if len(dividends) > 0 else 0  # Approx years
            except:
                years_of_dividends = info.get("payoutRatio", 0) > 0 and 5 or 0

            # Earnings stability (check if any loss years in past 10yr)
            earnings_deficit_years = 0  # Default to 0 (no deficit)

            # Growth rate (10-year CAGR)
            eps_growth_rate = StockDataFetcher._calculate_cagr(eps_10y_ago, eps_current, 10)

            # P/B ratio
            price_to_book = current_price / nav_per_share if nav_per_share > 0 else 0

            # EPS growth as percentage
            eps_growth_pct = eps_growth_rate * 100 if eps_growth_rate < 1 else eps_growth_rate

            return {
                "symbol": symbol,
                "stock_price": current_price,
                "current_eps": eps_current,
                "revenue_per_share": revenue_per_share,
                "current_ratio": current_ratio,
                "net_working_capital": nwc,
                "long_term_debt": long_term_debt,
                "years_of_dividends": years_of_dividends,
                "earnings_deficit_years": earnings_deficit_years,
                "eps_growth_rate": eps_growth_rate,
                "nav_per_share": nav_per_share,
                "eps_growth_pct": eps_growth_pct,
                "price_to_book": price_to_book,
                "market_cap": market_cap,
                "fetch_time": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    @staticmethod
    def _calculate_cagr(start_value: float, end_value: float, years: int) -> float:
        """Calculate CAGR"""
        if start_value <= 0 or years <= 0:
            return 0
        try:
            cagr = (end_value / start_value) ** (1 / years) - 1
            return max(cagr, 0)  # No negative growth
        except:
            return 0


class DailyScreeningJob:
    """Run daily screening at 5 PM UTC"""

    def __init__(self, watchlists: Dict[str, List[str]]):
        """
        Args:
            watchlists: Dict of {user_id: [symbols]}
        """
        self.watchlists = watchlists
        self.fetcher = StockDataFetcher()
        self.analyzer = GrahamAnalyzer()
        self.valuator = ValuationEngine()
        self.generator = SignalGenerator()

    def run(self) -> List[Dict]:
        """
        Analyze all stocks in all watchlists

        Returns:
            List of signal results
        """
        logger.info("="*60)
        logger.info("STARTING DAILY SCREENING JOB")
        logger.info(f"Time: {datetime.now().isoformat()}")
        logger.info("="*60)

        all_signals = []

        # Get unique symbols from all watchlists
        all_symbols = set()
        for user_id, symbols in self.watchlists.items():
            all_symbols.update(symbols)

        logger.info(f"Screening {len(all_symbols)} unique stocks across all users")

        for symbol in all_symbols:
            logger.info(f"\nAnalyzing {symbol}...")

            # Fetch data
            stock_data = self.fetcher.fetch_stock_data(symbol)
            if not stock_data:
                logger.warning(f"Skipping {symbol} - no data")
                continue

            # Analyze
            criteria, graham_score = self.analyzer.evaluate_stock(stock_data)

            # Valuation
            iv = self.valuator.calculate_intrinsic_value(
                stock_data["current_eps"],
                stock_data["eps_growth_rate"]
            )

            # Signal
            signal, ratio = self.generator.generate_signal(
                graham_score,
                iv,
                stock_data["stock_price"]
            )

            confidence = self.generator.calculate_confidence(graham_score, ratio, signal)

            margin_pct = ((iv / stock_data["stock_price"]) - 1) * 100 \
                if stock_data["stock_price"] > 0 else 0

            result = {
                "symbol": symbol,
                "signal": signal,
                "current_price": round(stock_data["stock_price"], 2),
                "intrinsic_value": round(iv, 2),
                "margin_of_safety": round(margin_pct, 2),
                "graham_score": graham_score,
                "confidence": confidence,
                "criteria": criteria,
                "timestamp": datetime.now().isoformat(),
            }

            all_signals.append(result)

            logger.info(f"  Signal: {signal}")
            logger.info(f"  Graham Score: {graham_score}/7")
            logger.info(f"  IV: ${iv:.2f} vs Price: ${stock_data['stock_price']:.2f}")
            logger.info(f"  Margin: {margin_pct:.1f}%")
            logger.info(f"  Confidence: {confidence:.0%}")

        logger.info(f"\n{'='*60}")
        logger.info(f"SCREENING COMPLETE - {len(all_signals)} signals generated")
        logger.info(f"{'='*60}\n")

        return all_signals


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    # Sample watchlists
    test_watchlists = {
        "user_123": ["AAPL", "MSFT", "GOOGL"],
        "user_456": ["AAPL", "TSLA"],
    }

    job = DailyScreeningJob(test_watchlists)
    signals = job.run()

    print("\n" + "="*60)
    print("SIGNAL SUMMARY")
    print("="*60)
    for sig in signals:
        print(f"\n{sig['symbol']:10s} | {sig['signal']:6s} | "
              f"Price: ${sig['current_price']:8.2f} | IV: ${sig['intrinsic_value']:8.2f} | "
              f"Margin: {sig['margin_of_safety']:+6.1f}% | Confidence: {sig['confidence']:.0%}")
