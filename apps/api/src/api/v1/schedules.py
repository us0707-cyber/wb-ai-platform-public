from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from src.api.deps import get_current_user, require_min_role
from src.database.session import get_db
from src.models import User
from src.schemas.jobs import JobRead
from src.schemas.schedules import ScheduleCreate, ScheduleList, ScheduleRead, ScheduleUpdate
from src.services.schedule_service import ScheduleService
router=APIRouter(prefix="/schedules",tags=["Schedules"])
@router.post("",response_model=ScheduleRead,status_code=201)
def create_schedule(payload:ScheduleCreate,user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)): return ScheduleService(db).create(user.id,payload)
@router.get("",response_model=ScheduleList)
def list_schedules(limit:int=Query(100,ge=1,le=200),offset:int=Query(0,ge=0),user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    items,total=ScheduleService(db).list(user.id,limit,offset); return {"items":items,"total":total}
@router.get("/{schedule_id}",response_model=ScheduleRead)
def get_schedule(schedule_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)): return ScheduleService(db).get(user.id,schedule_id)
@router.patch("/{schedule_id}",response_model=ScheduleRead)
def update_schedule(schedule_id:int,payload:ScheduleUpdate,user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)): return ScheduleService(db).update(user.id,schedule_id,payload)
@router.delete("/{schedule_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_schedule(schedule_id:int,user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)):
    ScheduleService(db).delete(user.id,schedule_id); return Response(status_code=204)
@router.post("/{schedule_id}/trigger",response_model=JobRead,status_code=201)
def trigger_schedule(schedule_id:int,user:User=Depends(require_min_role("manager")),db:Session=Depends(get_db)): return ScheduleService(db).trigger(user.id,schedule_id)
