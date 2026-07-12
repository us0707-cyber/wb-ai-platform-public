from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.database.session import Base
from src.models import MarketplaceStore, Product, Recommendation, User
from src.schemas.autopilot import AutopilotRuleCreate
from src.services.autopilot_service import AutopilotService

def make_db():
    e=create_engine("sqlite:///:memory:"); Base.metadata.create_all(e); return sessionmaker(bind=e)()
def test_low_stock_rule_creates_one_open_recommendation():
    db=make_db(); u=User(email="a@x.com",username="a2",hashed_password="x",role="admin"); db.add(u); db.flush()
    s=MarketplaceStore(owner_id=u.id,name="store",api_token=""); db.add(s); db.flush()
    p=Product(store_id=s.id,title="Product",stock=2); db.add(p); db.commit()
    svc=AutopilotService(db); svc.create(u.id,AutopilotRuleCreate(name="Low stock",rule_type="low_stock",threshold=5))
    first=svc.evaluate(u.id); second=svc.evaluate(u.id)
    assert first["created_recommendations"]==1 and second["created_recommendations"]==0
    assert len(list(db.scalars(select(Recommendation))))==1
