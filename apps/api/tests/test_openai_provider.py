import pytest

from src.ai.providers.openai import OpenAIProvider


def test_openai_schema_is_strict_and_known():
    schema = OpenAIProvider._schema("title")
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["title", "rationale"]


def test_openai_unknown_schema_is_rejected():
    with pytest.raises(ValueError, match="Неизвестная AI-схема"):
        OpenAIProvider._schema("unknown")


def test_openai_output_text_collects_response_chunks():
    payload = {
        "output": [
            {
                "content": [
                    {"type": "output_text", "text": '{"title":"Товар"}'},
                ]
            }
        ]
    }
    assert OpenAIProvider._output_text(payload) == '{"title":"Товар"}'


def test_openai_refusal_is_rejected():
    payload = {"output": [{"content": [{"type": "refusal", "refusal": "Нет"}]}]}
    with pytest.raises(ValueError, match="отказался"):
        OpenAIProvider._output_text(payload)
