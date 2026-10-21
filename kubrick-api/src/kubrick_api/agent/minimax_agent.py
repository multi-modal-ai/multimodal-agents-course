"""MiniMax-backed agent using the existing tool and memory flow."""

from typing import Any
from uuid import uuid4

import instructor
from openai import OpenAI

from kubrick_api.agent.base_agent import BaseAgent
from kubrick_api.agent.groq.groq_agent import GroqAgent
from kubrick_api.agent.memory import Memory
from kubrick_api.config import get_settings
from kubrick_api.minimax import minimax_completion_kwargs, resolve_minimax_base_url

settings = get_settings()


class MiniMaxAgent(GroqAgent):
    """Use MiniMax Chat Completions while retaining Kubrick's tool flow."""

    def __init__(
        self,
        name: str,
        mcp_server: str,
        memory: Memory | None = None,
        disable_tools: list | None = None,
    ):
        BaseAgent.__init__(self, name, mcp_server, memory, disable_tools)
        if not settings.MINIMAX_API_KEY:
            raise ValueError("MINIMAX_API_KEY is required when LLM_PROVIDER=minimax")

        self.client = OpenAI(
            api_key=settings.MINIMAX_API_KEY,
            base_url=resolve_minimax_base_url(settings.MINIMAX_REGION, settings.MINIMAX_BASE_URL),
        )
        self.instructor_client = instructor.from_openai(self.client, mode=instructor.Mode.JSON)
        self.routing_model = settings.MINIMAX_ROUTING_MODEL or settings.MINIMAX_MODEL
        self.tool_use_model = settings.MINIMAX_TOOL_USE_MODEL or settings.MINIMAX_MODEL
        self.general_model = settings.MINIMAX_GENERAL_MODEL or settings.MINIMAX_MODEL
        self.reasoning_effort = settings.MINIMAX_REASONING_EFFORT
        self.thread_id = str(uuid4())

    def _completion_kwargs(self, model: str, **kwargs: Any) -> dict[str, Any]:
        """Serialize only the supported Flash reasoning option."""
        options = minimax_completion_kwargs(
            model,
            [],
            reasoning_effort=self.reasoning_effort,
        )
        return {"reasoning_effort": options["reasoning_effort"]} if "reasoning_effort" in options else {}
