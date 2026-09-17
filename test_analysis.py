"""
Unit tests for Graham analysis engine
"""

import pytest
from graham import GrahamAnalyzer, ValuationEngine, SignalGenerator


class TestGrahamAnalyzer:
    """Test Graham's 7 criteria checker"""

    def test_adequate_size(self):
        analyzer = GrahamAnalyzer()
        assert analyzer.check_adequate_size(6.0) == True
        assert analyzer.check_adequate_size(3.0) == False

    def test_financial_strength(self):
        analyzer = GrahamAnalyzer()
        # Good: current_ratio >= 2, NWC > debt
        assert analyzer.check_financial_strength(2.5, 100, 50) == True
        # Bad: current_ratio < 2
        assert analyzer.check_financial_strength(1.5, 100, 50) == False
        # Bad: NWC < debt
        assert analyzer.check_financial_strength(2.5, 40, 100) == False

    def test_dividend_history(self):
        analyzer = GrahamAnalyzer()
        assert analyzer.check_dividend_history(5) == True
        assert analyzer.check_dividend_history(4) == False

    def test_earnings_stability(self):
        analyzer = GrahamAnalyzer()
        assert analyzer.check_earnings_stability(0) == True
        assert analyzer.check_earnings_stability(1) == False

    def test_ten_year_growth(self):
        analyzer = GrahamAnalyzer()
        # 33% growth = 0.33
        assert analyzer.check_ten_year_growth(0.33) == True
        assert analyzer.check_ten_year_growth(0.32) == False

    def test_evaluate_stock(self):
        stock = {
            "revenue_per_share": 10.0,
            "current_ratio": 2.5,
            "net_working_capital": 100,
            "long_term_debt": 50,
            "years_of_dividends": 10,
            "earnings_deficit_years": 0,
            "eps_growth_rate": 0.08,
            "stock_price": 100,
            "nav_per_share": 80,
            "eps_growth_pct": 8,
            "price_to_book": 1.2,
        }

        analyzer = GrahamAnalyzer()
        criteria, score = analyzer.evaluate_stock(stock)

        assert score >= 5  # At least 5/7 pass
        assert criteria["adequate_size"] == True
        assert criteria["financial_strength"] == True


class TestValuationEngine:
    """Test intrinsic value calculator"""

    def test_calculate_intrinsic_value(self):
        engine = ValuationEngine()

        # Example: EPS=$2, growth=8%
        # IV = 2 * (8.5 + 2*8) = 2 * 24.5 = $49
        iv = engine.calculate_intrinsic_value(2.0, 0.08)
        assert iv == 49.0

    def test_calculate_cagr(self):
        engine = ValuationEngine()

        # EPS goes from 3 to 4 over 10 years
        # CAGR = (4/3)^(1/10) - 1 ≈ 0.0292 ≈ 2.92%
        cagr = engine.calculate_cagr(3.0, 4.0, 10)
        assert 0.02 < cagr < 0.03

    def test_margin_of_safety(self):
        engine = ValuationEngine()

        # IV = 100, Price = 80 → 25% margin (undervalued)
        margin = engine.margin_of_safety(100, 80)
        assert margin == 0.25

        # IV = 100, Price = 120 → -16.7% margin (overvalued)
        margin = engine.margin_of_safety(100, 120)
        assert -0.20 < margin < -0.16


class TestSignalGenerator:
    """Test signal generation logic"""

    def test_generate_signal_buy(self):
        gen = SignalGenerator()

        # Graham score 6/7, IV/MP = 1.3 (30% margin) → BUY
        signal, ratio = gen.generate_signal(6, 130, 100)
        assert signal == "BUY"
        assert ratio == 1.3

    def test_generate_signal_sell(self):
        gen = SignalGenerator()

        # Graham score 6/7, IV/MP = 0.75 (25% overvalued) → SELL
        signal, ratio = gen.generate_signal(6, 75, 100)
        assert signal == "SELL"

    def test_generate_signal_hold(self):
        gen = SignalGenerator()

        # Graham score 6/7, IV/MP = 1.1 (10% margin) → HOLD
        signal, ratio = gen.generate_signal(6, 110, 100)
        assert signal == "HOLD"

    def test_generate_signal_skip(self):
        gen = SignalGenerator()

        # Graham score 4/7 (< 5) → SKIP
        signal, ratio = gen.generate_signal(4, 130, 100)
        assert signal == "SKIP"

    def test_calculate_confidence(self):
        gen = SignalGenerator()

        # Strong BUY: 7/7 criteria, wide margin
        confidence = gen.calculate_confidence(7, 1.4, "BUY")
        assert confidence > 0.8

        # Skip: no signal
        confidence = gen.calculate_confidence(4, 0, "SKIP")
        assert confidence == 0.0

        # Weak hold: 5/7 criteria, no margin
        confidence = gen.calculate_confidence(5, 1.0, "HOLD")
        assert confidence > 0.3


# ===== RUN TESTS =====
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
