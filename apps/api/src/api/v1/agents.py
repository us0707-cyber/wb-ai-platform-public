from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.deps import get_current_user
from src.database.session import get_db
from src.models import AgentRun, Product, User
from src.schemas.agents import AdsRequest, CompetitorRequest, KeywordRequest, QuestionReplyRequest, ReviewReplyRequest, SEORequest
from src.services.agent_service import ads_recommendation, competitor_analysis, keyword_analysis, question_reply, review_reply
from src.services.ai_service import ai_service

router = APIRouter(prefix="/agents", tags=["AI Agents"])


def _product(db: Session, product_id: int, user_id: int) -> Product:
    product = db.get(Product, product_id)
    if not product or product.store.owner_id != user_id:
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product


def _save(db: Session, user_id: int, agent_type: str, input_data: dict, output_data: dict) -> AgentRun:
    run = AgentRun(user_id=user_id, agent_type=agent_type, input_data=input_data, output_data=output_data)
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


@router.post("/seo")
async def seo(payload: SEORequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = _product(db, payload.product_id, user.id)
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

    db.commit()
    db.refresh(product)

    response = {
        **result,
        "product_id": product.id,
        "applied": payload.apply_changes,
        "seo_updated_at": product.seo_updated_at.isoformat() if product.seo_updated_at else None,
    }
    run = _save(db, user.id, "seo", payload.model_dump(), response)
    response["run_id"] = run.id
    return response


@router.post("/seo/{product_id}/apply")
def apply_seo(product_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = _product(db, product_id, user.id)
    if not product.seo_title and not product.seo_description:
        raise HTTPException(status_code=400, detail="Сначала запустите SEO-анализ")

    if product.seo_title:
        product.title = product.seo_title
    if product.seo_description:
        product.description = product.seo_description
    product.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(product)

    result = {"ok": True, "product_id": product.id, "title": product.title, "description": product.description}
    _save(db, user.id, "seo_apply", {"product_id": product.id}, result)
    return result


@router.get("/runs")
def runs(
    agent_type: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(AgentRun).where(AgentRun.user_id == user.id)
    if agent_type:
        query = query.where(AgentRun.agent_type == agent_type)
    items = list(db.scalars(query.order_by(AgentRun.id.desc()).limit(limit)))
    return [
        {
            "id": item.id,
            "agent_type": item.agent_type,
            "status": item.status,
            "input_data": item.input_data,
            "output_data": item.output_data,
            "created_at": item.created_at.isoformat(),
        }
        for item in items
    ]


@router.post("/keywords")
def keywords(payload: KeywordRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = _product(db, payload.product_id, user.id)
    result = keyword_analysis(product, payload.seed_keywords)
    product.keywords = result["recommended_core"]
    db.commit()
    _save(db, user.id, "keywords", payload.model_dump(), result)
    return result


@router.post("/competitors")
def competitors(payload: CompetitorRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = _product(db, payload.product_id, user.id)
    result = competitor_analysis(product, payload.competitors)
    _save(db, user.id, "competitors", payload.model_dump(), result)
    return result


@router.post("/review-reply")
def review(payload: ReviewReplyRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = review_reply(payload.rating, payload.review_text, payload.product_name)
    _save(db, user.id, "review_reply", payload.model_dump(), result)
    return result


@router.post("/question-reply")
def question(payload: QuestionReplyRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    result = question_reply(payload.question, payload.product_name)
    _save(db, user.id, "question_reply", payload.model_dump(), result)
    return result


@router.post("/ads")
def ads(payload: AdsRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    product = _product(db, payload.product_id, user.id)
    result = ads_recommendation(product, payload.daily_budget, payload.current_cpc, payload.conversion_rate, payload.margin_percent)
    _save(db, user.id, "ads", payload.model_dump(), result)
    return result
