from types import SimpleNamespace

from src.services.business_service import competitor_analysis, pricing_analysis, product_profit


def product(**kwargs):
    values = {
        "id": 1,
        "price": 1000,
        "cost_price": 400,
        "logistics_cost": 60,
        "commission_percent": 15,
        "sales_30d": 10,
        "revenue_30d": 10000,
        "ad_spend_30d": 500,
        "competitor_avg_price": 1100,
    }
    values.update(kwargs)
    return SimpleNamespace(**values)


def test_product_profit():
    assert product_profit(product()) == 3400


def test_pricing_analysis_returns_positive_price():
    result = pricing_analysis(product(), 30, tax_percent=6)
    assert result["recommended_price"] > 0
    assert result["estimated_profit_per_unit"] > 0
    assert result["break_even_price"] > 0
    assert result["action"] in {"increase", "decrease", "hold"}


def test_pricing_analysis_accepts_manual_inputs():
    result = pricing_analysis(
        product(price=0, cost_price=0, logistics_cost=0, competitor_avg_price=0),
        30,
        current_price=1290,
        cost_price=450,
        logistics_cost=90,
        commission_percent=15,
        ad_cost_per_unit=70,
        tax_percent=6,
        market_price=1350,
    )
    assert result["current_price"] == 1290
    assert result["recommended_price"] > result["break_even_price"]
    assert result["estimated_margin_percent"] > 0
    assert result["data_complete"] is True


def test_pricing_analysis_reports_missing_data():
    result = pricing_analysis(product(price=0, cost_price=0, logistics_cost=0, competitor_avg_price=0), 30)
    assert result["action"] == "needs_data"
    assert result["data_complete"] is False
    assert result["warnings"]


def test_competitor_analysis_does_not_invent_one_ruble_price():
    item = product(price=0, competitor_avg_price=0)
    result = competitor_analysis(item, [])
    assert result["average_price"] == 0
    assert result["recommended_price"] == 0
    assert result["warnings"]
