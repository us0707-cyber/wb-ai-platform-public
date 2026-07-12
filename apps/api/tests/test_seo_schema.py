from src.schemas.agents import SEORequest


def test_seo_request_defaults_to_preview():
    payload = SEORequest(product_id=1)
    assert payload.apply_changes is False
    assert payload.target_audience == "покупатели Wildberries"


def test_seo_request_can_apply_changes():
    payload = SEORequest(product_id=1, apply_changes=True, tone="экспертный")
    assert payload.apply_changes is True
    assert payload.tone == "экспертный"
