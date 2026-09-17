"""
Graham's 7 Criteria + Intrinsic Value Calculator
Core analysis logic for trading signals
"""

from typing import Dict, Tuple
import math


class GrahamAnalyzer:
    """Evaluate stock against Benjamin Graham's 7 criteria"""

    def __init__(self):
        self.criteria_weights = {
            "adequate_size": 1,
            "financial_strength": 1,
            "dividend_history": 1,
            "earnings_stability": 1,
            "ten_year_growth": 1,
            "price_nav_ratio": 1,
            "pb_multiple": 1,
        }

    def check_adequate_size(self, revenue_per_share: float) -> bool:
        """Criterion 1: Revenue per share > $5 (or ₦2.5M for NSE)"""
        threshold = 5.0  # USD for US equities
        return revenue_per_share > threshold

    def check_financial_strength(
        self,
        current_ratio: float,
        net_working_capital: float,
        long_term_debt: float
    ) -> bool:
        """Criterion 2: Current ratio >= 2 AND NWC > Long-term debt"""
        return (current_ratio >= 2.0) and (net_working_capital > long_term_debt)

    def check_dividend_history(self, years_of_dividends: int) -> bool:
        """Criterion 3: Continuous dividends for at least 5 years"""
        return years_of_dividends >= 5

    def check_earnings_stability(self, earnings_deficit_years: int) -> bool:
        """Criterion 4: No earnings deficit in past 10 years"""
        return earnings_deficit_years == 0

    def check_ten_year_growth(self, eps_growth_rate: float) -> bool:
        """Criterion 5: 10-year EPS growth of at least 33% (1/3)"""
        return eps_growth_rate >= 0.33

    def check_price_nav_ratio(self, stock_price: float, nav_per_share: float) -> bool:
        """Criterion 6: Stock price <= 1.5x Net Asset Value (NAV)"""
        if nav_per_share <= 0:
            return False
        ratio = stock_price / nav_per_share
        return ratio <= 1.5

    def check_pb_multiple(self, eps_growth_pct: float, price_to_book: float) -> bool:
        """Criterion 7: (EPS Growth % × Price/Book) <= 22.5"""
        # Convert growth from decimal (0.08) to percentage (8)
        growth_pct = eps_growth_pct * 100 if eps_growth_pct < 1 else eps_growth_pct
        multiple = growth_pct * price_to_book
        return multiple <= 22.5

    def evaluate_stock(self, stock_data: Dict) -> Tuple[Dict, int]:
        """
        Evaluate stock against all 7 criteria.

        Args:
            stock_data: Dict with keys:
                - revenue_per_share
                - current_ratio
                - net_working_capital
                - long_term_debt
                - years_of_dividends
                - earnings_deficit_years
                - eps_growth_rate (0.33 = 33%)
                - stock_price
                - nav_per_share
                - eps_growth_pct
                - price_to_book

        Returns:
            (criteria_dict, score) where criteria_dict has pass/fail per criterion
            and score is 0-7 (number of criteria passed)
        """
        criteria_results = {
            "adequate_size": self.check_adequate_size(
                stock_data.get("revenue_per_share", 0)
            ),
            "financial_strength": self.check_financial_strength(
                stock_data.get("current_ratio", 0),
                stock_data.get("net_working_capital", 0),
                stock_data.get("long_term_debt", 0),
            ),
            "dividend_history": self.check_dividend_history(
                stock_data.get("years_of_dividends", 0)
            ),
            "earnings_stability": self.check_earnings_stability(
                stock_data.get("earnings_deficit_years", 0)
            ),
            "ten_year_growth": self.check_ten_year_growth(
                stock_data.get("eps_growth_rate", 0)
            ),
            "price_nav_ratio": self.check_price_nav_ratio(
                stock_data.get("stock_price", 0),
                stock_data.get("nav_per_share", 1),
            ),
            "pb_multiple": self.check_pb_multiple(
                stock_data.get("eps_growth_pct", 0),
                stock_data.get("price_to_book", 1),
            ),
        }

        score = sum(criteria_results.values())
        return criteria_results, score


class ValuationEngine:
    """Calculate intrinsic value using Graham's formula"""

    @staticmethod
    def calculate_intrinsic_value(
        current_eps: float,
        expected_growth_rate: float
    ) -> float:
        """
        Graham's intrinsic value formula:
        IV = Current EPS × (8.5 + 2 × Expected Annual Growth Rate)

        Args:
            current_eps: Current earnings per share
            expected_growth_rate: Expected annual growth rate (as decimal, e.g., 0.08 = 8%)

        Returns:
            Intrinsic value per share
        """
        if current_eps <= 0:
            return 0

        # Convert growth to percentage if needed
        growth_pct = expected_growth_rate * 100 if expected_growth_rate < 1 else expected_growth_rate

        iv = current_eps * (8.5 + 2 * growth_pct)
        return round(iv, 2)

    @staticmethod
    def calculate_cagr(start_value: float, end_value: float, years: int) -> float:
        """
        Calculate Compound Annual Growth Rate (CAGR)

        Args:
            start_value: Starting value (e.g., EPS 10 years ago)
            end_value: Ending value (e.g., current EPS)
            years: Number of years

        Returns:
            CAGR as decimal (e.g., 0.08 = 8%)
        """
        if start_value <= 0 or years <= 0:
            return 0

        try:
            cagr = (end_value / start_value) ** (1 / years) - 1
            return round(cagr, 4)
        except:
            return 0

    @staticmethod
    def margin_of_safety(intrinsic_value: float, market_price: float) -> float:
        """
        Calculate margin of safety as percentage.

        Args:
            intrinsic_value: Calculated intrinsic value
            market_price: Current market price

        Returns:
            Margin of safety as decimal (e.g., 0.25 = 25%)
            Positive = undervalued, Negative = overvalued
        """
        if market_price <= 0:
            return 0

        margin = (intrinsic_value / market_price) - 1
        return round(margin, 4)


class SignalGenerator:
    """Generate BUY/SELL/HOLD/SKIP signals"""

    BUY_THRESHOLD = 1.25      # IV/MP > 1.25 = BUY (25% margin)
    SELL_THRESHOLD = 0.80     # IV/MP < 0.80 = SELL (20% overvalued)
    GRAHAM_PASS_THRESHOLD = 5  # Must pass 5/7 criteria

    @staticmethod
    def generate_signal(
        graham_score: int,
        intrinsic_value: float,
        market_price: float
    ) -> Tuple[str, float]:
        """
        Generate signal based on Graham criteria + valuation.

        Args:
            graham_score: Number of Graham criteria passed (0-7)
            intrinsic_value: Calculated intrinsic value
            market_price: Current market price

        Returns:
            (signal, margin) where signal is BUY/SELL/HOLD/SKIP
            and margin is IV/MP ratio
        """
        if graham_score < SignalGenerator.GRAHAM_PASS_THRESHOLD:
            return "SKIP", 0

        if market_price <= 0:
            return "SKIP", 0

        ratio = intrinsic_value / market_price

        if ratio > SignalGenerator.BUY_THRESHOLD:
            return "BUY", ratio
        elif ratio < SignalGenerator.SELL_THRESHOLD:
            return "SELL", ratio
        else:
            return "HOLD", ratio

    @staticmethod
    def calculate_confidence(
        graham_score: int,
        margin_ratio: float,
        signal_type: str
    ) -> float:
        """
        Calculate confidence score (0-1) for the signal.
        Higher when more Graham criteria pass and margin is wider.
        """
        if signal_type == "SKIP":
            return 0.0

        # Base confidence from Graham score
        graham_confidence = graham_score / 7.0  # 0-1

        # Margin confidence
        if signal_type == "BUY":
            margin_conf = min((margin_ratio - 1.25) / 0.25, 1.0)  # 0-1
        elif signal_type == "SELL":
            margin_conf = min((0.80 - margin_ratio) / 0.20, 1.0)  # 0-1
        else:  # HOLD
            margin_conf = 0.5

        # Weighted average
        confidence = (graham_confidence * 0.7) + (margin_conf * 0.3)
        return round(min(confidence, 1.0), 2)


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    # Sample stock data
    test_stock = {
        "symbol": "AAPL",
        "stock_price": 150.00,
        "current_eps": 6.05,
        "revenue_per_share": 30.5,
        "current_ratio": 1.1,
        "net_working_capital": 35e9,
        "long_term_debt": 106e9,
        "years_of_dividends": 12,
        "earnings_deficit_years": 0,
        "eps_growth_rate": 0.08,  # 8% expected growth
        "nav_per_share": 125.0,
        "eps_growth_pct": 8,  # 8%
        "price_to_book": 1.2,
    }

    # Analyze
    analyzer = GrahamAnalyzer()
    criteria, score = analyzer.evaluate_stock(test_stock)

    # Valuation
    engine = ValuationEngine()
    iv = engine.calculate_intrinsic_value(
        test_stock["current_eps"],
        test_stock["eps_growth_rate"]
    )
    margin = engine.margin_of_safety(iv, test_stock["stock_price"])

    # Signal
    gen = SignalGenerator()
    signal, ratio = gen.generate_signal(score, iv, test_stock["stock_price"])
    confidence = gen.calculate_confidence(score, ratio, signal)

    print(f"\n{'='*60}")
    print(f"ANALYSIS: {test_stock['symbol']}")
    print(f"{'='*60}")
    print(f"\nGraham's 7 Criteria: {score}/7")
    for criterion, passed in criteria.items():
        print(f"  {'✓' if passed else '✗'} {criterion}")

    print(f"\nValuation:")
    print(f"  Current Price: ${test_stock['stock_price']:.2f}")
    print(f"  Intrinsic Value: ${iv:.2f}")
    print(f"  Margin of Safety: {margin*100:+.1f}%")

    print(f"\nSignal: {signal}")
    print(f"  Confidence: {confidence:.0%}")
    print(f"{'='*60}\n")
