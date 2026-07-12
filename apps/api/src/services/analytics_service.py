from __future__ import annotations

import math
import random
from collections import defaultdict
from datetime import date, timedelta
from statistics import mean, pstdev

from sqlalchemy.orm import Session

from src.models import AnalyticsDaily, Product
from src.repositories.analytics_repository import AnalyticsRepository
from src.services.business_service import product_profit


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AnalyticsRepository(db)

    def seed_demo(self, user_id: int, days: int = 60) -> int:
        products = self.repo.products_for_user(user_id)
        today = date.today()
        facts: list[AnalyticsDaily] = []
        for product in products:
            seed = (product.id * 1009) + user_id
            rng = random.Random(seed)
            baseline = max(1.0, float(product.sales_30d or 0) / 30 or rng.uniform(0.5, 5.0))
            for offset in range(days - 1, -1, -1):
                day = today - timedelta(days=offset)
                weekly = 1.15 if day.weekday() in (4, 5, 6) else 0.92
                trend = 1 + ((days - offset) / max(days, 1)) * rng.uniform(-0.12, 0.2)
                units = max(0, round(baseline * weekly * trend + rng.uniform(-1.2, 1.2)))
                orders = units + (1 if units and rng.random() > 0.75 else 0)
                returns = 1 if units >= 3 and rng.random() < 0.08 else 0
                price = float(product.price or rng.uniform(500, 2500))
                revenue = round(units * price, 2)
                commission = revenue * float(product.commission_percent or 15) / 100
                cost = units * float(product.cost_price or price * 0.35)
                logistics = units * float(product.logistics_cost or 60)
                ad_spend = round(revenue * rng.uniform(0.04, 0.13), 2)
                profit = round(revenue - commission - cost - logistics - ad_spend, 2)
                views = max(orders * 30, round(rng.uniform(100, 1500)))
                clicks = min(views, max(orders, round(views * rng.uniform(0.015, 0.06))))
                facts.append(
                    AnalyticsDaily(
                        user_id=user_id,
                        product_id=product.id,
                        day=day,
                        orders=orders,
                        sales=units,
                        returns=returns,
                        revenue=revenue,
                        profit=profit,
                        ad_spend=ad_spend,
                        views=views,
                        clicks=clicks,
                        stock=max(0, int(product.stock or 0) - units),
                    )
                )
        self.repo.replace_demo_facts(user_id, facts)
        return len(facts)

    def _window(self, days: int):
        end = date.today()
        return end - timedelta(days=days - 1), end

    def overview(self, user_id: int, days: int = 30) -> dict:
        start, end = self._window(days)
        facts = self.repo.facts(user_id, start, end)
        products = self.repo.products_for_user(user_id)
        if facts:
            revenue = sum(x.revenue for x in facts)
            profit = sum(x.profit for x in facts)
            orders = sum(x.orders for x in facts)
            sales = sum(x.sales for x in facts)
            returns = sum(x.returns for x in facts)
            ad_spend = sum(x.ad_spend for x in facts)
            views = sum(x.views for x in facts)
        else:
            factor = days / 30
            revenue = sum(float(p.revenue_30d or 0) for p in products) * factor
            profit = sum(product_profit(p) for p in products) * factor
            orders = round(sum(int(p.orders_30d or 0) for p in products) * factor)
            sales = round(sum(int(p.sales_30d or 0) for p in products) * factor)
            returns = round(sum(int(p.returns_30d or 0) for p in products) * factor)
            ad_spend = sum(float(p.ad_spend_30d or 0) for p in products) * factor
            views = 0
        return {
            "revenue": round(revenue, 2),
            "profit": round(profit, 2),
            "orders": int(orders),
            "sales": int(sales),
            "returns": int(returns),
            "ad_spend": round(ad_spend, 2),
            "margin_percent": round(profit / revenue * 100, 2) if revenue else 0,
            "romi_percent": round((profit - ad_spend) / ad_spend * 100, 2) if ad_spend else 0,
            "conversion_percent": round(orders / views * 100, 2) if views else 0,
            "average_order_value": round(revenue / orders, 2) if orders else 0,
            "stock_units": sum(int(p.stock or 0) for p in products),
            "products_count": len(products),
        }

    def trends(self, user_id: int, days: int = 30) -> list[dict]:
        start, end = self._window(days)
        facts = self.repo.facts(user_id, start, end)
        by_day: dict[date, dict] = {}
        cursor = start
        while cursor <= end:
            by_day[cursor] = {"day": cursor, "revenue": 0.0, "profit": 0.0, "orders": 0, "sales": 0, "ad_spend": 0.0}
            cursor += timedelta(days=1)
        for fact in facts:
            row = by_day[fact.day]
            row["revenue"] += fact.revenue
            row["profit"] += fact.profit
            row["orders"] += fact.orders
            row["sales"] += fact.sales
            row["ad_spend"] += fact.ad_spend
        for row in by_day.values():
            row["revenue"] = round(row["revenue"], 2)
            row["profit"] = round(row["profit"], 2)
            row["ad_spend"] = round(row["ad_spend"], 2)
        return list(by_day.values())

    def abc_xyz(self, user_id: int, days: int = 30) -> list[dict]:
        start, end = self._window(days)
        products = self.repo.products_for_user(user_id)
        facts = self.repo.facts(user_id, start, end)
        by_product: dict[int, list[AnalyticsDaily]] = defaultdict(list)
        for fact in facts:
            by_product[fact.product_id].append(fact)
        revenues = {p.id: sum(x.revenue for x in by_product[p.id]) if facts else float(p.revenue_30d or 0) for p in products}
        total = sum(revenues.values()) or 1
        cumulative = 0.0
        result = []
        for product in sorted(products, key=lambda p: revenues[p.id], reverse=True):
            revenue = revenues[product.id]
            previous_cumulative = cumulative
            cumulative += revenue / total * 100
            abc = "A" if previous_cumulative < 80 else "B" if previous_cumulative < 95 else "C"
            daily_sales = [float(x.sales) for x in by_product[product.id]]
            avg = mean(daily_sales) if daily_sales else float(product.sales_30d or 0) / 30
            cv = (pstdev(daily_sales) / avg * 100) if len(daily_sales) > 1 and avg > 0 else 0
            xyz = "X" if cv <= 20 else "Y" if cv <= 50 else "Z"
            result.append({
                "product_id": product.id,
                "title": product.title,
                "revenue": round(revenue, 2),
                "revenue_share_percent": round(revenue / total * 100, 2),
                "abc_class": abc,
                "xyz_class": xyz,
                "coefficient_of_variation": round(cv, 2),
            })
        return result

    def forecast(self, user_id: int, history_days: int = 30) -> list[dict]:
        start, end = self._window(history_days)
        products = self.repo.products_for_user(user_id)
        facts = self.repo.facts(user_id, start, end)
        by_product: dict[int, list[AnalyticsDaily]] = defaultdict(list)
        for fact in facts:
            by_product[fact.product_id].append(fact)
        result = []
        for product in products:
            rows = by_product[product.id]
            values = [x.sales for x in rows]
            avg = mean(values) if values else float(product.sales_30d or 0) / 30
            recent = mean(values[-7:]) if len(values) >= 7 else avg
            weighted = max(0.0, recent * 0.65 + avg * 0.35)
            stock = int(product.stock or 0)
            days_of_stock = round(stock / weighted, 1) if weighted > 0 else None
            forecast_7 = max(0, math.ceil(weighted * 7))
            forecast_30 = max(0, math.ceil(weighted * 30))
            safety_stock = math.ceil(weighted * 14)
            reorder = max(0, forecast_30 + safety_stock - stock)
            confidence = "high" if len(values) >= 30 else "medium" if len(values) >= 14 else "low"
            result.append({
                "product_id": product.id,
                "title": product.title,
                "average_daily_sales": round(weighted, 2),
                "forecast_sales_7d": forecast_7,
                "forecast_sales_30d": forecast_30,
                "days_of_stock": days_of_stock,
                "suggested_reorder": reorder,
                "confidence": confidence,
            })
        return sorted(result, key=lambda x: (x["days_of_stock"] is None, x["days_of_stock"] or 999999))
