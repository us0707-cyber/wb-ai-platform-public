from __future__ import annotations

from datetime import datetime
from statistics import mean
from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.models import Product, Recommendation


def product_profit(product: Product) -> float:
    revenue = float(product.revenue_30d or 0)
    if revenue <= 0:
        revenue = float(product.price or 0) * int(product.sales_30d or 0)
    commission = revenue * float(product.commission_percent or 0) / 100
    cost = float(product.cost_price or 0) * int(product.sales_30d or 0)
    logistics = float(product.logistics_cost or 0) * int(product.sales_30d or 0)
    return round(revenue - commission - cost - logistics - float(product.ad_spend_30d or 0), 2)


def _ad_cost_per_unit(product: Product, explicit: float | None = None) -> float:
    if explicit is not None:
        return max(0.0, float(explicit))
    sales = int(product.sales_30d or 0)
    return round(float(product.ad_spend_30d or 0) / sales, 2) if sales > 0 else 0.0


def pricing_analysis(
    product: Product,
    target_margin_percent: float = 30,
    *,
    current_price: float | None = None,
    cost_price: float | None = None,
    logistics_cost: float | None = None,
    commission_percent: float | None = None,
    ad_cost_per_unit: float | None = None,
    tax_percent: float = 6,
    market_price: float | None = None,
) -> dict:
    current = float(product.price or 0) if current_price is None else float(current_price)
    cost = float(product.cost_price or 0) if cost_price is None else float(cost_price)
    logistics = float(product.logistics_cost or 0) if logistics_cost is None else float(logistics_cost)
    commission = float(product.commission_percent or 0) if commission_percent is None else float(commission_percent)
    market = float(product.competitor_avg_price or 0) if market_price is None else float(market_price)
    ads = _ad_cost_per_unit(product, ad_cost_per_unit)
    tax = float(tax_percent)

    target_margin = float(target_margin_percent) / 100
    commission_rate = commission / 100
    tax_rate = tax / 100
    fixed_per_unit = cost + logistics + ads
    denominator = 1 - commission_rate - tax_rate - target_margin

    warnings: list[str] = []
    if current <= 0:
        warnings.append("Укажите текущую цену товара")
    if cost <= 0:
        warnings.append("Укажите себестоимость товара")
    if market <= 0:
        warnings.append("Укажите рыночную цену или выполните анализ конкурентов")
    if denominator <= 0.01:
        warnings.append("Сумма комиссии, налога и целевой маржи слишком высокая")
        denominator = 0.01

    cost_based = fixed_per_unit / denominator if fixed_per_unit > 0 else 0.0
    if cost_based > 0 and market > 0:
        recommended = cost_based * 0.7 + market * 0.3
    elif cost_based > 0:
        recommended = cost_based
    elif market > 0:
        recommended = market
    else:
        recommended = current

    break_even_denominator = max(0.01, 1 - commission_rate - tax_rate)
    break_even = fixed_per_unit / break_even_denominator if fixed_per_unit > 0 else 0.0
    net_profit = recommended * (1 - commission_rate - tax_rate) - fixed_per_unit
    net_margin = (net_profit / recommended * 100) if recommended > 0 else 0.0

    if current <= 0 or recommended <= 0:
        action = "needs_data"
    elif recommended > current * 1.03:
        action = "increase"
    elif recommended < current * 0.97:
        action = "decrease"
    else:
        action = "hold"

    rationale: list[str] = []
    if cost > 0:
        rationale.append("Учтена себестоимость")
    if logistics > 0:
        rationale.append("Учтена логистика")
    if ads > 0:
        rationale.append("Учтены рекламные расходы на единицу")
    if market > 0:
        rationale.append("Учтена средняя цена рынка")
    rationale.append(f"Целевая маржа: {target_margin_percent:.1f}%")

    return {
        "product_id": product.id,
        "current_price": round(current, 2),
        "cost_price": round(cost, 2),
        "logistics_cost": round(logistics, 2),
        "ad_cost_per_unit": round(ads, 2),
        "commission_percent": round(commission, 2),
        "tax_percent": round(tax, 2),
        "market_price": round(market, 2),
        "cost_based_price": round(cost_based, 2),
        "break_even_price": round(break_even, 2),
        "recommended_price": round(recommended, 2),
        "target_margin_percent": round(float(target_margin_percent), 2),
        "estimated_profit_per_unit": round(net_profit, 2),
        "estimated_margin_percent": round(net_margin, 2),
        "action": action,
        "warnings": warnings,
        "rationale": rationale,
        "data_complete": not warnings,
    }


def seed_demo_metrics(product: Product, index: int = 0) -> None:
    base_orders = max(3, 18 + index * 7)
    product.orders_30d = base_orders
    product.sales_30d = max(1, base_orders - (index % 4 + 1))
    product.returns_30d = max(0, index % 3)
    product.revenue_30d = round(product.price * product.sales_30d, 2)
    product.ad_spend_30d = round(product.revenue_30d * (0.08 + (index % 3) * 0.02), 2)
    product.ctr = round(2.4 + (index % 5) * 0.7, 2)
    product.conversion_rate = round(3.8 + (index % 4) * 0.9, 2)
    if product.price <= 0:
        product.price = 990 + index * 250
    if product.cost_price <= 0:
        product.cost_price = round(product.price * 0.42, 2)
    if product.logistics_cost <= 0:
        product.logistics_cost = round(max(25, product.price * 0.04), 2)
    product.profit_30d = product_profit(product)


def competitor_analysis(product: Product, competitors: list[dict]) -> dict:
    anchor = float(product.price or 0) or float(product.competitor_avg_price or 0)
    if not competitors and anchor > 0:
        competitors = [
            {
                "title": f"Аналог {i + 1}",
                "price": round(anchor * factor, 2),
                "rating": round(4.3 + i * 0.15, 2),
                "reviews": 120 + i * 190,
            }
            for i, factor in enumerate((0.91, 0.97, 1.04, 1.12, 0.88))
        ]

    prices = [float(x.get("price", 0)) for x in competitors if float(x.get("price", 0)) > 0]
    avg_price = mean(prices) if prices else anchor
    if avg_price > 0:
        product.competitor_avg_price = round(avg_price, 2)

    return {
        "product_id": product.id,
        "competitors_count": len(competitors),
        "average_price": round(avg_price, 2),
        "min_price": round(min(prices), 2) if prices else 0,
        "max_price": round(max(prices), 2) if prices else 0,
        "price_gap_percent": round(((float(product.price or 0) - avg_price) / avg_price * 100), 2) if avg_price else 0,
        "recommended_price": round(avg_price * 0.99, 2) if avg_price else 0,
        "content_gaps": ["Добавьте 5–7 преимуществ", "Усилите первое фото", "Уточните размеры и материалы"],
        "competitors": competitors,
        "warnings": [] if avg_price else ["Укажите текущую или рыночную цену для анализа"],
    }


def create_autopilot_recommendations(db: Session, user_id: int, products: list[Product]) -> list[Recommendation]:
    db.execute(delete(Recommendation).where(Recommendation.user_id == user_id, Recommendation.status == "open"))
    items: list[Recommendation] = []
    for product in products:
        product.profit_30d = product_profit(product)
        if product.stock <= max(3, product.sales_30d // 4):
            items.append(Recommendation(user_id=user_id, product_id=product.id, kind="stock", title="Низкий остаток", message=f"У товара «{product.title}» осталось {product.stock} шт.", priority="high", action_data={"suggested_stock": max(20, product.sales_30d)}))
        if product.seo_score < 65:
            items.append(Recommendation(user_id=user_id, product_id=product.id, kind="seo", title="Улучшить SEO", message=f"SEO-оценка товара «{product.title}» — {product.seo_score:.1f}/100.", priority="medium", action_data={"agent": "seo"}))
        if product.price <= 0 or product.cost_price <= 0:
            items.append(Recommendation(user_id=user_id, product_id=product.id, kind="data", title="Заполнить финансовые данные", message=f"Для товара «{product.title}» укажите цену и себестоимость, чтобы включить AI Pricing.", priority="high", action_data={"open_page": "pricing"}))
        else:
            pricing = pricing_analysis(product)
            product.recommended_price = pricing["recommended_price"]
            if pricing["action"] not in {"hold", "needs_data"}:
                items.append(Recommendation(user_id=user_id, product_id=product.id, kind="pricing", title="Изменить цену", message=f"Рекомендуемая цена для «{product.title}»: {pricing['recommended_price']:.2f} ₽.", priority="medium", action_data={"recommended_price": pricing["recommended_price"]}))
        if product.ad_spend_30d > 0 and product.conversion_rate < 4:
            items.append(Recommendation(user_id=user_id, product_id=product.id, kind="ads", title="Оптимизировать рекламу", message=f"Конверсия товара «{product.title}» ниже 4%. Снизьте ставки и отключите запросы без заказов.", priority="high", action_data={"reduce_cpc_percent": 15}))
    db.add_all(items)
    db.commit()
    for item in items:
        db.refresh(item)
    return items
