"""MiniMax text-model defaults and request serialization helpers."""

from typing import Any

MINIMAX_MODELS = ("MiniMax-M3.1-Flash", "MiniMax-M3")
DEFAULT_MINIMAX_MODEL = MINIMAX_MODELS[0]
MINIMAX_BASE_URLS = {
    "global_en": "https://api.minimax.io/v1",
    "cn_zh": "https://api.minimaxi.com/v1",
}


def resolve_minimax_base_url(region: str, override: str | None = None) -> str:
    """Return the configured direct MiniMax OpenAI-compatible endpoint."""
    if override:
        return override.rstrip("/")
    try:
        return MINIMAX_BASE_URLS[region]
    except KeyError as exc:
        raise ValueError(f"Unsupported MiniMax region: {region}") from exc


def minimax_completion_kwargs(
    model: str,
    messages: list[dict[str, Any]],
    *,
    tools: list[dict[str, Any]] | None = None,
    tool_choice: str | None = None,
    max_completion_tokens: int | None = None,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    """Build the OpenAI Chat Completions payload used at the SDK boundary.

    Flash supports adaptive reasoning effort. MiniMax-M3 accepts the same
    request shape but ignores effort, so the field is omitted for M3.
    """
    payload: dict[str, Any] = {"model": model, "messages": messages}
    if tools is not None:
        payload["tools"] = tools
    if tool_choice is not None:
        payload["tool_choice"] = tool_choice
    if max_completion_tokens is not None:
        payload["max_completion_tokens"] = max_completion_tokens
    if model == "MiniMax-M3.1-Flash" and reasoning_effort is not None:
        payload["reasoning_effort"] = reasoning_effort
    return payload
