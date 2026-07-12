from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field

RuleType = Literal["low_stock", "low_seo", "negative_profit"]
ActionType = Literal["recommendation"]

class AutopilotRuleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    rule_type: RuleType
    threshold: float = 0
    action_type: ActionType = "recommendation"
    config: dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True

class AutopilotRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    threshold: float | None = None
    config: dict[str, Any] | None = None
    enabled: bool | None = None

class AutopilotRuleRead(BaseModel):
    id: int
    user_id: int
    name: str
    rule_type: RuleType
    threshold: float
    action_type: ActionType
    config: dict[str, Any]
    enabled: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}

class AutopilotRuleList(BaseModel):
    items: list[AutopilotRuleRead]
    total: int

class AutopilotEvaluationRead(BaseModel):
    checked_products: int
    matched_rules: int
    created_recommendations: int
