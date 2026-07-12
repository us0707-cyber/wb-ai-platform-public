from pydantic import BaseModel, Field


class SEORequest(BaseModel):
    product_id: int
    target_audience: str = "покупатели Wildberries"
    tone: str = "продающий и информативный"
    apply_changes: bool = False


class KeywordRequest(BaseModel):
    product_id: int
    seed_keywords: list[str] = Field(default_factory=list)


class CompetitorRequest(BaseModel):
    product_id: int
    competitors: list[dict] = Field(default_factory=list)


class ReviewReplyRequest(BaseModel):
    rating: int = Field(ge=1, le=5)
    review_text: str
    product_name: str = "товар"


class QuestionReplyRequest(BaseModel):
    question: str
    product_name: str = "товар"


class AdsRequest(BaseModel):
    product_id: int
    daily_budget: float = Field(gt=0)
    current_cpc: float = Field(gt=0)
    conversion_rate: float = Field(ge=0, le=1)
    margin_percent: float = Field(ge=0, le=100)
