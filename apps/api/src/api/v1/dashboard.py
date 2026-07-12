from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database.session import get_db
from src.models import AgentRun, MarketplaceStore, Product, User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stores = db.scalar(select(func.count()).select_from(MarketplaceStore).where(MarketplaceStore.owner_id == user.id)) or 0
    products = db.scalar(select(func.count()).select_from(Product).join(MarketplaceStore).where(MarketplaceStore.owner_id == user.id)) or 0
    runs = db.scalar(select(func.count()).select_from(AgentRun).where(AgentRun.user_id == user.id)) or 0
    avg_seo = db.scalar(select(func.avg(Product.seo_score)).join(MarketplaceStore).where(MarketplaceStore.owner_id == user.id)) or 0
    stock = db.scalar(select(func.sum(Product.stock)).join(MarketplaceStore).where(MarketplaceStore.owner_id == user.id)) or 0
    return {"stores": stores, "products": products, "agent_runs": runs, "average_seo_score": round(float(avg_seo), 1), "total_stock": int(stock)}
