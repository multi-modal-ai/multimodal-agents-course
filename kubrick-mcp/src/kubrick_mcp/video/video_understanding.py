from pathlib import Path
from typing import Any

import httpx

from kubrick_mcp.config import get_settings


def _openai_base_url(settings) -> str:
    if settings.MINIMAX_REGION == "cn_zh":
        return settings.MINIMAX_OPENAI_BASE_URL_CN.rstrip("/")
    return settings.MINIMAX_OPENAI_BASE_URL_GLOBAL.rstrip("/")


def _protocol_base_url(settings) -> str:
    if settings.MINIMAX_PROTOCOL == "openai":
        return _openai_base_url(settings)
    if settings.MINIMAX_REGION == "cn_zh":
        return settings.MINIMAX_ANTHROPIC_BASE_URL_CN.rstrip("/")
    return settings.MINIMAX_ANTHROPIC_BASE_URL_GLOBAL.rstrip("/")


def _auth_headers(settings) -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.MINIMAX_API_KEY}"}


def _upload_video(video_path: str, settings) -> str:
    path = Path(video_path)
    if not path.is_file():
        raise ValueError(f"Video file not found: {video_path}")

    with path.open("rb") as video_file:
        response = httpx.post(
            f"{_openai_base_url(settings)}/files/upload",
            headers=_auth_headers(settings),
            data={"purpose": "video_understanding"},
            files={"file": (path.name, video_file, "video/mp4")},
            timeout=settings.MINIMAX_REQUEST_TIMEOUT_SECONDS,
        )

    if not response.is_success:
        raise RuntimeError(f"Video upload failed with status {response.status_code}")

    file_id = response.json().get("file", {}).get("file_id")
    if not file_id:
        raise RuntimeError("Video upload response did not include a file ID")
    return file_id


def _delete_video(file_id: str, settings) -> None:
    try:
        httpx.delete(
            f"{_openai_base_url(settings)}/files/{file_id}",
            headers=_auth_headers(settings),
            timeout=settings.MINIMAX_REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError:
        pass


def _thinking(settings) -> dict[str, dict[str, str]]:
    return {"thinking": {"type": settings.MINIMAX_THINKING}}


def _video_content(file_id: str, protocol: str) -> dict[str, Any]:
    file_url = f"mm_file://{file_id}"
    if protocol == "openai":
        return {"type": "video_url", "video_url": {"url": file_url}}
    return {"type": "video", "source": {"type": "url", "url": file_url}}


def _response_text(payload: dict[str, Any], protocol: str) -> str:
    if protocol == "openai":
        content = payload["choices"][0]["message"].get("content")
        if isinstance(content, str):
            return content
        blocks = content or []
    else:
        blocks = payload.get("content", [])

    return "\n".join(block.get("text", "") for block in blocks if block.get("type") == "text").strip()


def understand_video(video_path: str, user_query: str) -> str:
    """Answer a question by sending a local video to the configured multimodal model."""
    settings = get_settings()
    if not settings.MINIMAX_API_KEY:
        raise ValueError("MINIMAX_API_KEY is required to understand a video")
    if not user_query.strip():
        raise ValueError("A video question is required")

    file_id = _upload_video(video_path, settings)
    try:
        content = [{"type": "text", "text": user_query}, _video_content(file_id, settings.MINIMAX_PROTOCOL)]
        if settings.MINIMAX_PROTOCOL == "openai":
            request = {
                "model": settings.MINIMAX_VIDEO_MODEL,
                "messages": [{"role": "user", "content": content}],
                "max_completion_tokens": settings.MINIMAX_MAX_COMPLETION_TOKENS,
                **_thinking(settings),
            }
            url = f"{_protocol_base_url(settings)}/chat/completions"
        else:
            request = {
                "model": settings.MINIMAX_VIDEO_MODEL,
                "messages": [{"role": "user", "content": content}],
                "max_tokens": settings.MINIMAX_MAX_COMPLETION_TOKENS,
                **_thinking(settings),
            }
            url = f"{_protocol_base_url(settings)}/v1/messages"

        response = httpx.post(
            url,
            headers={**_auth_headers(settings), "Content-Type": "application/json"},
            json=request,
            timeout=settings.MINIMAX_REQUEST_TIMEOUT_SECONDS,
        )
        if not response.is_success:
            raise RuntimeError(f"Video understanding failed with status {response.status_code}")

        answer = _response_text(response.json(), settings.MINIMAX_PROTOCOL)
        if not answer:
            raise RuntimeError("Video understanding response did not include text")
        return answer
    finally:
        _delete_video(file_id, settings)
