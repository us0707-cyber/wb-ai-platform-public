from __future__ import annotations

from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.integrations.wildberries import WildberriesClient
from src.models import MarketplaceStore, Product
from src.services.business_service import seed_demo_metrics
from src.services.token_service import decrypt_token


def _card_image(card: dict) -> str:
    photos = card.get("photos") or []
    if not photos:
        return ""
    photo = photos[0] or {}
    return photo.get("big") or photo.get("c516x688") or photo.get("square") or ""


def _card_category(card: dict) -> str:
    return card.get("subjectName") or card.get("object") or card.get("subject") or ""


async def sync_store_catalog(db: Session, store: MarketplaceStore, demo_mode: bool = False) -> dict:
    store.sync_status = "running"
    store.sync_error = ""
    db.commit()
    try:
        token = decrypt_token(store.api_token)
        client = WildberriesClient(token)
        cards = [] if demo_mode or not token else await client.fetch_cards(limit=100)
        mode = "wb"
        if not cards:
            mode = "demo"
            cards = [
                {"nmID": 900000001, "vendorCode": "DEMO-001", "title": "Демонстрационный товар WB", "brand": "DemoBrand", "subjectName": "Товары для дома", "description": "Товар для проверки аналитики и AI-функций.", "photos": []},
                {"nmID": 900000002, "vendorCode": "DEMO-002", "title": "Тестовый аксессуар", "brand": "DemoBrand", "subjectName": "Аксессуары", "description": "Второй товар демонстрационного каталога.", "photos": []},
            ]
        stocks = []
        if mode == "wb":
            try:
                stocks = await client.fetch_stocks()
            except Exception:
                stocks = []
        stock_by_nm: dict[int, int] = {}
        for item in stocks:
            nm = int(item.get("nmId") or item.get("nmID") or 0)
            stock_by_nm[nm] = stock_by_nm.get(nm, 0) + int(item.get("quantity") or 0)

        created = 0
        updated = 0
        for index, card in enumerate(cards):
            nm_id = int(card.get("nmID") or card.get("nmId") or 0) or None
            product = None
            if nm_id:
                product = db.scalar(select(Product).where(Product.store_id == store.id, Product.nm_id == nm_id))
            if not product:
                product = Product(store_id=store.id, nm_id=nm_id, title=card.get("title") or card.get("vendorCode") or f"Товар {index+1}")
                db.add(product)
                created += 1
            else:
                updated += 1
            product.vendor_code = card.get("vendorCode") or product.vendor_code
            product.title = card.get("title") or product.title
            product.description = card.get("description") or product.description
            product.brand = card.get("brand") or product.brand
            product.category = _card_category(card) or product.category
            product.image_url = _card_image(card) or product.image_url
            product.status = "active"
            if nm_id in stock_by_nm:
                product.stock = stock_by_nm[nm_id]
            if mode == "demo":
                if product.price <= 0:
                    product.price = 1490 + index * 700
                if product.stock <= 0:
                    product.stock = 12 + index * 9
                seed_demo_metrics(product, index)

        store.last_sync_at = datetime.utcnow()
        store.sync_status = "completed"
        store.products_synced = len(cards)
        db.commit()
        return {"ok": True, "mode": mode, "created": created, "updated": updated, "total": len(cards), "last_sync_at": store.last_sync_at.isoformat()}
    except Exception as exc:
        store.sync_status = "error"
        store.sync_error = str(exc)[:1000]
        db.commit()
        return {"ok": False, "message": store.sync_error}
