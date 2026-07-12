from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database.session import get_db
from src.models import MarketplaceStore, Product, Recommendation, User
from src.schemas.business import BulkSEORequest, CompetitorAnalyzeRequest, DemoAnalyticsRequest, PricingRequest, RecommendationAction, StoreSyncRequest
from src.services.ai_service import ai_service
from src.services.business_service import competitor_analysis, create_autopilot_recommendations, pricing_analysis, product_profit, seed_demo_metrics
from src.services.sync_service import sync_store_catalog

router = APIRouter(tags=["Business Suite"])


def _product(db: Session, product_id: int, user_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product or product.store.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


@router.post("/stores/{store_id}/sync")
async def sync_store(store_id: int, payload: StoreSyncRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    store = db.get(MarketplaceStore, store_id)
    if not store or store.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Магазин не найден")
    return await sync_store_catalog(db, store, payload.demo_mode)


@router.post("/agents/seo/bulk")
async def bulk_seo(payload: BulkSEORequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = []
    for product_id in payload.product_ids:
        product = _product(db, product_id, user.id)
        result = await ai_service.seo(product, payload.target_audience, payload.tone)
        product.seo_score = result["seo_score"]
        product.keywords = result.get("keywords", [])
        product.seo_title = result.get("title", "")
        product.seo_description = result.get("description", "")
        product.seo_recommendations = result.get("recommendations", [])
        product.seo_updated_at = datetime.utcnow()
        if payload.apply_changes:
            product.title = product.seo_title or product.title
            product.description = product.seo_description or product.description
        results.append({"product_id": product.id, "seo_score": product.seo_score})
    db.commit()
    return {"ok": True, "processed": len(results), "results": results}


@router.post("/analytics/demo")
def demo_analytics(payload: DemoAnalyticsRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = select(Product).join(MarketplaceStore).where(MarketplaceStore.owner_id == user.id)
    if payload.product_ids:
        query = query.where(Product.id.in_(payload.product_ids))
    products = list(db.scalars(query))
    for index, product in enumerate(products):
        seed_demo_metrics(product, index)
    db.commit()
    return {"ok": True, "updated": len(products)}


@router.get("/analytics/summary")
def analytics_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    products = list(db.scalars(select(Product).join(MarketplaceStore).where(MarketplaceStore.owner_id == user.id)))
    revenue = sum(float(p.revenue_30d or 0) for p in products)
    profit = sum(product_profit(p) for p in products)
    orders = sum(int(p.orders_30d or 0) for p in products)
    sales = sum(int(p.sales_30d or 0) for p in products)
    ad_spend = sum(float(p.ad_spend_30d or 0) for p in products)
    return {
        "revenue_30d": round(revenue, 2), "profit_30d": round(profit, 2), "orders_30d": orders,
        "sales_30d": sales, "ad_spend_30d": round(ad_spend, 2),
        "romi_percent": round((profit / ad_spend * 100), 1) if ad_spend else 0,
        "average_conversion": round(sum(float(p.conversion_rate or 0) for p in products) / len(products), 2) if products else 0,
    }


@router.get("/analytics/products")
def analytics_products(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    products = list(db.scalars(select(Product).join(MarketplaceStore).where(MarketplaceStore.owner_id == user.id).order_by(Product.revenue_30d.desc())))
    return [{"id": p.id, "title": p.title, "revenue": p.revenue_30d, "profit": product_profit(p), "orders": p.orders_30d, "sales": p.sales_30d, "stock": p.stock, "ctr": p.ctr, "conversion_rate": p.conversion_rate} for p in products]


@router.post("/competitors/analyze")
def analyze_competitors(payload: CompetitorAnalyzeRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = _product(db, payload.product_id, user.id)
    result = competitor_analysis(product, payload.competitors)
    product.recommended_price = result["recommended_price"]
    db.commit()
    return result


@router.post("/pricing/analyze")
def analyze_pricing(payload: PricingRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = _product(db, payload.product_id, user.id)

    if payload.save_inputs:
        if payload.current_price is not None:
            product.price = payload.current_price
        if payload.cost_price is not None:
            product.cost_price = payload.cost_price
        if payload.logistics_cost is not None:
            product.logistics_cost = payload.logistics_cost
        if payload.commission_percent is not None:
            product.commission_percent = payload.commission_percent
        if payload.market_price is not None:
            product.competitor_avg_price = payload.market_price

    result = pricing_analysis(
        product,
        payload.target_margin_percent,
        current_price=payload.current_price,
        cost_price=payload.cost_price,
        logistics_cost=payload.logistics_cost,
        commission_percent=payload.commission_percent,
        ad_cost_per_unit=payload.ad_cost_per_unit,
        tax_percent=payload.tax_percent,
        market_price=payload.market_price,
    )
    price = result["recommended_price"]
    if payload.min_price is not None:
        price = max(price, payload.min_price)
    if payload.max_price is not None:
        price = min(price, payload.max_price)
    result["recommended_price"] = round(price, 2)

    if result["recommended_price"] > 0:
        product.recommended_price = result["recommended_price"]
    db.commit()
    return result


@router.post("/pricing/{product_id}/apply")
def apply_price(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = _product(db, product_id, user.id)
    if product.recommended_price <= 0:
        raise HTTPException(status_code=400, detail="Сначала выполните анализ цены")
    old_price = product.price
    product.price = product.recommended_price
    db.commit()
    return {"ok": True, "old_price": old_price, "new_price": product.price}


@router.post("/autopilot/run")
def run_autopilot(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    products = list(db.scalars(select(Product).join(MarketplaceStore).where(MarketplaceStore.owner_id == user.id)))
    items = create_autopilot_recommendations(db, user.id, products)
    return {"ok": True, "created": len(items)}


@router.get("/autopilot/recommendations")
def recommendations(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = list(db.scalars(select(Recommendation).where(Recommendation.user_id == user.id).order_by(Recommendation.id.desc())))
    return [{"id": x.id, "product_id": x.product_id, "kind": x.kind, "title": x.title, "message": x.message, "priority": x.priority, "status": x.status, "action_data": x.action_data, "created_at": x.created_at.isoformat()} for x in items]


@router.post("/autopilot/recommendations/{recommendation_id}")
def recommendation_action(recommendation_id: int, payload: RecommendationAction, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.get(Recommendation, recommendation_id)
    if not item or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Рекомендация не найдена")
    if payload.action == "apply" and item.product_id:
        product = _product(db, item.product_id, user.id)
        if item.kind == "pricing" and item.action_data.get("recommended_price"):
            product.price = float(item.action_data["recommended_price"])
        elif item.kind == "stock" and item.action_data.get("suggested_stock"):
            product.stock = int(item.action_data["suggested_stock"])
        item.status = "applied"
    else:
        item.status = "dismissed"
    item.resolved_at = datetime.utcnow()
    db.commit()
    return {"ok": True, "status": item.status}
