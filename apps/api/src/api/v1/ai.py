from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.ai import ai_engine
from src.api.deps import get_current_user, require_min_role
from src.core.config import settings
from src.database.session import get_db
from src.models import AgentRun, User
from src.repositories.product_repository import ProductRepository
from src.schemas.ai import AIApplyRequest, AIProductRequest, AIProviderInfo
from src.services.audit_service import write_audit_log

router = APIRouter(prefix="/ai", tags=["AI Engine"])


async def _run(task: str, payload: AIProductRequest, user: User, db: Session):
    try:
        result = await ai_engine.run(db, task=task, product_id=payload.product_id, user_id=user.id, extra=payload.model_dump(exclude={"product_id"}))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    db.add(AgentRun(user_id=user.id, agent_type=f"ai_{task}", input_data=payload.model_dump(), output_data=result))
    db.commit()
    return result


@router.get("/provider", response_model=AIProviderInfo)
def provider_info(user: User = Depends(get_current_user)):
    active = ai_engine.provider().name
    return AIProviderInfo(
        configured_provider=settings.ai_provider,
        active_provider=active,
        model=settings.openai_model if active == "openai" else "deterministic-v1",
        openai_configured=bool(settings.openai_api_key),
    )


@router.post("/title")
async def generate_title(payload: AIProductRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await _run("title", payload, user, db)


@router.post("/description")
async def generate_description(payload: AIProductRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await _run("description", payload, user, db)


@router.post("/keywords")
async def generate_keywords(payload: AIProductRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await _run("keywords", payload, user, db)


@router.post("/improve-card")
async def improve_card(payload: AIProductRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await _run("improve-card", payload, user, db)


@router.post("/analyze-product")
async def analyze_product(payload: AIProductRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return await _run("analyze-product", payload, user, db)


@router.post("/apply")
def apply_ai_result(
    payload: AIApplyRequest,
    request: Request,
    user: User = Depends(require_min_role("manager")),
    db: Session = Depends(get_db),
):
    product = ProductRepository(db).get_owned(payload.product_id, user.id)
    if not product:
        raise HTTPException(status_code=404, detail="Товар не найден")
    changed: list[str] = []
    if payload.title is not None:
        product.title = payload.title.strip()
        changed.append("title")
    if payload.description is not None:
        product.description = payload.description.strip()
        changed.append("description")
    if payload.keywords is not None:
        product.keywords = payload.keywords[:50]
        changed.append("keywords")
    if not changed:
        raise HTTPException(status_code=400, detail="Нет изменений для применения")
    db.commit()
    write_audit_log(db, action="ai.apply", user=user, request=request, entity_type="product", entity_id=product.id, details={"fields": changed})
    return {"ok": True, "product_id": product.id, "changed": changed}
