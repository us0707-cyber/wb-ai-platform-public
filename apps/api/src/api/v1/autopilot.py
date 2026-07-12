from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from src.api.deps import get_current_user, require_min_role
from src.database.session import get_db
from src.models import Job, User
from src.repositories.job_repository import JobRepository
from src.schemas.autopilot import AutopilotEvaluationRead, AutopilotRuleCreate, AutopilotRuleList, AutopilotRuleRead, AutopilotRuleUpdate
from src.schemas.jobs import JobRead
from src.services.autopilot_service import AutopilotService
router=APIRouter(prefix="/autopilot",tags=["Autopilot"])
@router.post("/rules",response_model=AutopilotRuleRead,status_code=201)
def create_rule(payload:AutopilotRuleCreate,user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)): return AutopilotService(db).create(user.id,payload)
@router.get("/rules",response_model=AutopilotRuleList)
def list_rules(limit:int=Query(100,ge=1,le=200),offset:int=Query(0,ge=0),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    items,total=AutopilotService(db).list(user.id,limit,offset); return {"items":items,"total":total}
@router.patch("/rules/{rule_id}",response_model=AutopilotRuleRead)
def update_rule(rule_id:int,payload:AutopilotRuleUpdate,user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)): return AutopilotService(db).update(user.id,rule_id,payload)
@router.delete("/rules/{rule_id}",status_code=204)
def delete_rule(rule_id:int,user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)):
    AutopilotService(db).delete(user.id,rule_id); return Response(status_code=204)
@router.post("/evaluate",response_model=JobRead,status_code=201)
def enqueue_evaluation(user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)):
    return JobRepository(db).create(Job(user_id=user.id,type="autopilot.evaluate",priority="high",payload={}))
@router.post("/evaluate-now",response_model=AutopilotEvaluationRead)
def evaluate_now(user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)): return AutopilotService(db).evaluate(user.id)
