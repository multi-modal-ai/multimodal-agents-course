import importlib.util
import json
from pathlib import Path

import httpx
from openai import OpenAI

_MINIMAX_PATH = Path(__file__).parents[1] / "src" / "kubrick_api" / "minimax.py"
_MINIMAX_SPEC = importlib.util.spec_from_file_location("kubrick_minimax", _MINIMAX_PATH)
_MINIMAX = importlib.util.module_from_spec(_MINIMAX_SPEC)
_MINIMAX_SPEC.loader.exec_module(_MINIMAX)

DEFAULT_MINIMAX_MODEL = _MINIMAX.DEFAULT_MINIMAX_MODEL
minimax_completion_kwargs = _MINIMAX.minimax_completion_kwargs
resolve_minimax_base_url = _MINIMAX.resolve_minimax_base_url


class FakeCompletions:
    def __init__(self):
        self.requests = []

    def create(self, **payload):
        self.requests.append(payload)
        return {"id": "mock-response", "choices": [{"message": {"content": "ok"}}]}


class FakeOpenAIClient:
    def __init__(self):
        self.chat = type("Chat", (), {"completions": FakeCompletions()})()


def test_direct_region_urls_are_stable():
    assert resolve_minimax_base_url("global_en") == "https://api.minimax.io/v1"
    assert resolve_minimax_base_url("cn_zh") == "https://api.minimaxi.com/v1"
    assert resolve_minimax_base_url("global_en", "https://mock.invalid/v1/") == "https://mock.invalid/v1"


def test_flash_payload_reaches_mocked_sdk_boundary_with_effort_and_multimodal_content():
    client = FakeOpenAIClient()
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": "Describe this"},
            {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,AA=="}},
        ],
    }]
    payload = minimax_completion_kwargs(
        DEFAULT_MINIMAX_MODEL,
        messages,
        tools=[{"type": "function", "function": {"name": "lookup"}}],
        tool_choice="auto",
        max_completion_tokens=128,
        reasoning_effort="max",
    )

    response = client.chat.completions.create(**payload)

    assert response["id"] == "mock-response"
    assert client.chat.completions.requests == [payload]
    assert payload["model"] == "MiniMax-M3.1-Flash"
    assert payload["reasoning_effort"] == "max"
    assert payload["messages"] == messages
    assert payload["tools"][0]["function"]["name"] == "lookup"


def test_openai_sdk_sends_flash_payload_over_mocked_http_transport():
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        requests.append({"url": str(request.url), "body": body})
        return httpx.Response(
            200,
            json={
                "id": "chatcmpl-mock",
                "object": "chat.completion",
                "created": 0,
                "model": DEFAULT_MINIMAX_MODEL,
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "ok"},
                    "finish_reason": "stop",
                }],
                "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
            },
        )

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http_client:
        client = OpenAI(api_key="test-only", base_url="https://mock.minimax.invalid/v1", http_client=http_client)
        response = client.chat.completions.create(
            **minimax_completion_kwargs(
                DEFAULT_MINIMAX_MODEL,
                [{"role": "user", "content": "hello"}],
                reasoning_effort="max",
            )
        )

    assert response.id == "chatcmpl-mock"
    assert requests[0]["url"] == "https://mock.minimax.invalid/v1/chat/completions"
    assert requests[0]["body"]["model"] == DEFAULT_MINIMAX_MODEL
    assert requests[0]["body"]["reasoning_effort"] == "max"


def test_m3_omits_unsupported_effort_field():
    payload = minimax_completion_kwargs(
        "MiniMax-M3",
        [{"role": "user", "content": "hello"}],
        reasoning_effort="max",
    )

    assert payload == {
        "model": "MiniMax-M3",
        "messages": [{"role": "user", "content": "hello"}],
    }
