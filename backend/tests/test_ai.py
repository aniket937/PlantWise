"""Tests for the hosted AI assistant service (OpenRouter, OpenAI-compatible).

The real backend talks to https://openrouter.ai/api/v1. These tests never touch
the network: every HTTP path is exercised through ``httpx.MockTransport``, and
the unconfigured paths short-circuit before any client is built.
"""

from __future__ import annotations

import asyncio
import inspect

import httpx
import pytest

from app.core.config import settings
from app.models import Plant
from app.schemas.assistant import ChatMessage

TEST_KEY = "sk-test-not-a-real-key"
BASE_URL = "https://openrouter.ai/api/v1"


def run(coro):
    return asyncio.run(coro)


def reply_json(text: str = "Sow in early spring.", choices: int = 1) -> dict:
    return {
        "id": "gen-test-1",
        "choices": [
            {"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}
            for _ in range(choices)
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


def error_response(status: int, message: str) -> httpx.Response:
    return httpx.Response(status, json={"error": {"code": status, "message": message}})


@pytest.fixture(autouse=True)
def _configured_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "openrouter_api_key", TEST_KEY)


def test_is_configured_flips_with_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services import ai

    monkeypatch.setattr(settings, "openrouter_api_key", "")
    assert ai.is_configured() is False
    monkeypatch.setattr(settings, "openrouter_api_key", TEST_KEY)
    assert ai.is_configured() is True


@pytest.mark.parametrize("function", ["chat", "check_availability"])
def test_short_circuits_without_api_key(
    function: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Startup/paths without a key never try to build an HTTP client."""
    from app.services import ai

    monkeypatch.setattr(settings, "openrouter_api_key", "")
    if function == "chat":
        outcome = run(
            ai.chat([ChatMessage(role="user", content="Hello")], plant=None, location_label=None)
        )
        assert outcome.available is False
        assert outcome.reply is None
        assert "API key" in (outcome.unavailable_reason or "")
    else:
        available, detail = run(ai.check_availability())
        assert available is False
        assert "API key" in detail
    assert ai.status_checked_at() is not None


def test_build_messages_includes_plant_context() -> None:
    from app.services import ai

    plant = Plant(
        slug="tomato",
        common_name="Tomato",
        scientific_name="Solanum lycopersicum",
        lifecycle="annual",
    )
    messages = ai.build_messages(
        [ChatMessage(role="user", content="When do I sow?")],
        plant=plant,
        location_label="Nairobi, Kenya",
    )
    system = messages[0]["content"]
    assert "Selected plant: Tomato (Solanum lycopersicum)" in system
    assert "Selected location: Nairobi, Kenya" in system
    assert messages[-1] == {"role": "user", "content": "When do I sow?"}


def test_build_messages_trims_to_max_history(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services import ai

    monkeypatch.setattr(settings, "ai_max_history_messages", 2)
    history = [ChatMessage(role="user", content=str(i)) for i in range(4)]
    messages = ai.build_messages(history, plant=None, location_label=None)
    assert len(messages) == 3  # one system prompt + the two most recent turns
    assert [m["content"] for m in messages[1:]] == ["2", "3"]


def test_chat_success_sends_openai_compatible_request(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services import ai

    monkeypatch.setattr(settings, "openrouter_model", "google/gemma-4-26b-a4b-it:free")
    monkeypatch.setattr(
        settings, "openrouter_fallback_models", ["nvidia/nemotron-3-super-120b-a12b:free"]
    )
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json=reply_json())

    transport = httpx.MockTransport(handler)
    outcome = run(
        ai.chat(
            [ChatMessage(role="user", content="When do I sow tomatoes?")],
            plant=None,
            location_label=None,
            transport=transport,
        )
    )

    assert len(captured) == 1
    request = captured[0]
    assert str(request.url) == f"{BASE_URL}/chat/completions"
    assert request.headers["authorization"] == f"Bearer {TEST_KEY}"
    assert request.headers["x-openrouter-title"] == settings.openrouter_site_title

    body = request.read().decode()
    assert '"models":["google/gemma-4-26b-a4b-it:free","nvidia/nemotron-3-super-120b-a12b:free"]' in body
    assert '"model":' not in body  # OpenRouter picks from the models array

    assert outcome.available is True
    assert outcome.reply == "Sow in early spring."
    assert outcome.unavailable_reason is None
    assert outcome.model == settings.openrouter_model
    assert outcome.latency_ms is not None


def test_model_chain_orders_and_dedupes(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services import ai

    monkeypatch.setattr(settings, "openrouter_model", "a:free")
    monkeypatch.setattr(
        settings, "openrouter_fallback_models", ["b:free", "a:free", " c:free "]
    )
    assert ai._model_chain() == ["a:free", "b:free", "c:free"]


def test_list_settings_accept_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """A comma separated env value must load, not blow up on JSON decoding."""
    from app.core.config import Settings

    monkeypatch.setenv("OPENROUTER_FALLBACK_MODELS", "a:free, b:free")
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test, http://b.test")
    loaded = Settings()
    assert loaded.openrouter_fallback_models == ["a:free", "b:free"]
    assert loaded.cors_origins == ["http://a.test", "http://b.test"]


def test_chat_reports_the_model_actually_used() -> None:
    """When OpenRouter falls back, the response names the model that answered."""
    from app.services import ai

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "nvidia/nemotron-3-super-120b-a12b:free",
                "choices": [
                    {"message": {"role": "assistant", "content": "Answered by the fallback."}}
                ],
            },
        )

    outcome = run(
        ai.chat(
            [ChatMessage(role="user", content="Question")],
            plant=None,
            location_label=None,
            transport=httpx.MockTransport(handler),
        )
    )
    assert outcome.available is True
    assert outcome.model == "nvidia/nemotron-3-super-120b-a12b:free"


def test_chat_sends_single_model_when_no_fallbacks(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.services import ai

    monkeypatch.setattr(settings, "openrouter_model", "google/gemma-4-26b-a4b-it:free")
    monkeypatch.setattr(settings, "openrouter_fallback_models", [])
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json=reply_json())

    run(
        ai.chat(
            [ChatMessage(role="user", content="Question")],
            plant=None,
            location_label=None,
            transport=httpx.MockTransport(handler),
        )
    )
    body = captured[0].read().decode()
    assert '"model":"google/gemma-4-26b-a4b-it:free"' in body
    assert '"models":' not in body


def test_chat_works_without_plant_context() -> None:
    from app.services import ai

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=reply_json("Sure, ask away."))

    outcome = run(
        ai.chat(
            [ChatMessage(role="user", content="General question")],
            plant=None,
            location_label=None,
            transport=httpx.MockTransport(handler),
        )
    )
    assert outcome.available is True
    assert outcome.reply == "Sure, ask away."


def test_chat_timeout_is_graceful() -> None:
    from app.services import ai

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    outcome = run(
        ai.chat(
            [ChatMessage(role="user", content="Slow question")],
            plant=None,
            location_label=None,
            transport=httpx.MockTransport(handler),
        )
    )
    assert outcome.available is False
    assert outcome.reply is None
    assert "time" in (outcome.unavailable_reason or "").lower()


@pytest.mark.parametrize(
    ("status", "expected_substring"),
    [
        (401, "key"),
        (403, "could not"),
        (429, "rate"),
        (503, "error"),
    ],
)
def test_chat_http_failures_are_user_presentable(
    status: int, expected_substring: str
) -> None:
    from app.services import ai

    def handler(request: httpx.Request) -> httpx.Response:
        return error_response(status, "provider failure detail")

    outcome = run(
        ai.chat(
            [ChatMessage(role="user", content="Question")],
            plant=None,
            location_label=None,
            transport=httpx.MockTransport(handler),
        )
    )
    assert outcome.available is False
    assert expected_substring in (outcome.unavailable_reason or "").lower()


def test_chat_malformed_payload_is_graceful() -> None:
    from app.services import ai

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []})

    outcome = run(
        ai.chat(
            [ChatMessage(role="user", content="Question")],
            plant=None,
            location_label=None,
            transport=httpx.MockTransport(handler),
        )
    )
    assert outcome.available is False
    assert "unexpected" in (outcome.unavailable_reason or "")


def test_chat_connect_error_is_graceful() -> None:
    from app.services import ai

    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route to host")

    outcome = run(
        ai.chat(
            [ChatMessage(role="user", content="Question")],
            plant=None,
            location_label=None,
            transport=httpx.MockTransport(handler),
        )
    )
    assert outcome.available is False
    assert "reach" in (outcome.unavailable_reason or "")


def test_check_availability_ok_with_live_probe() -> None:
    from app.services import ai

    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200, json={"data": {"label": TEST_KEY, "is_free_tier": True}}
        )

    available, detail = run(ai.check_availability(transport=httpx.MockTransport(handler)))
    assert available is True
    assert settings.openrouter_model in detail
    assert str(captured[0].url) == f"{BASE_URL}/auth/key"


def test_check_availability_401_reports_rejected_key() -> None:
    from app.services import ai

    def handler(request: httpx.Request) -> httpx.Response:
        return error_response(401, "invalid api key")

    available, detail = run(ai.check_availability(transport=httpx.MockTransport(handler)))
    assert available is False
    assert "key" in detail.lower()


def test_suitability_engine_never_imports_llm_service() -> None:
    """Non-AI features stay independent of the hosted model service."""
    from app.services import suitability as engine

    source = inspect.getsource(engine)
    assert "app.services.ai" not in source
    assert "ollama" not in source