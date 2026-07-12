from types import SimpleNamespace

from src.ai.engine import AIEngine
from src.ai.providers.local import LocalAIProvider
from src.ai.prompt_builder import PromptBuilder


def product():
    return SimpleNamespace(
        id=1,
        title="Щетка для уборки",
        description="Удобная щетка для кухни и ванной комнаты",
        brand="CleanHome",
        category="Товары для дома",
        price=499,
        rating=4.8,
        reviews_count=120,
    )


def test_local_keywords_are_deterministic():
    provider = LocalAIProvider()
    first = provider.keywords("Щетка для уборки кухни щетка")
    second = provider.keywords("Щетка для уборки кухни щетка")
    assert first == second
    assert first[0] == "щетка"


def test_prompt_builder_contains_product_data():
    prompt = PromptBuilder.product_payload(product(), task="title")
    assert "Щетка для уборки" in prompt
    assert '"task": "title"' in prompt


def test_local_improve_card_has_structured_output():
    result = AIEngine._local_result("improve-card", product(), {})
    assert result["title"].startswith("CleanHome")
    assert isinstance(result["keywords"], list)
    assert isinstance(result["recommendations"], list)


def test_local_analysis_score_range():
    result = AIEngine._local_result("analyze-product", product(), {})
    assert 0 <= result["score"] <= 100
