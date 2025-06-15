import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import instructor
import opik
from groq import Groq
from loguru import logger
from opik import opik_context

from agent_api.agent.base_agent import BaseAgent
from agent_api.agent.groq.groq_tool import transform_tool_definition
from agent_api.agent.groq.models import (
    GeneralResponseModel,
    RoutingResponseModel,
    VideoClipResponseModel,
)
from agent_api.agent.memory import Memory, MemoryRecord
from agent_api.config import settings

logger.bind(name="GroqAgent")


class GroqAgent(BaseAgent):
    def __init__(
        self,
        name: str,
        mcp_server: str,
        memory: Optional[Memory] = None,
        active_tools: list = None,
    ):
        super().__init__(
            name,
            mcp_server,
            memory,
            active_tools,
        )
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.instructor_client = instructor.from_groq(
            self.client, mode=instructor.Mode.JSON
        )
        self.thread_id = str(uuid.uuid4())

    async def _get_tools(self) -> List[Dict[str, Any]]:
        tools = await self.discover_tools()
        return [transform_tool_definition(tool) for tool in tools]

    @opik.track(name="build-chat-history")
    def _build_chat_history(
        self, system_prompt: str, message: str, image_base64: str | None = None
    ) -> List[Dict[str, Any]]:
        history = [
            {"role": "system", "content": system_prompt},
            *[
                {"role": record.role, "content": record.content}
                for record in self.memory.get_latest(n=settings.AGENT_MEMORY_SIZE)
            ],
        ]

        if image_base64:
            history.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                            },
                        },
                    ],
                }
            )
        else:
            history.append({"role": "user", "content": message})
        return history

    @opik.track(name="router", type="llm")
    def _route_query(self, message: str, video_path: str) -> bool:
        response = self.instructor_client.chat.completions.create(
            model=settings.GROQ_ROUTING_MODEL,
            response_model=RoutingResponseModel,
            messages=[
                {"role": "system", "content": self.routing_system_prompt},
                {"role": "user", "content": message},
            ],
            max_completion_tokens=20,
        )
        return response.tool_use

    @opik.track(name="tool-use", type="tool")
    async def _run_with_tool(self, message: str, video_path: str, image_base64: str | None = None) -> str:
        """Execute chat completion with tool usage."""
        tool_use_system_prompt = self.tool_use_system_prompt.format(
            video_path=video_path
        )
        chat_history = self._build_chat_history(tool_use_system_prompt, message)

        response = self.client.chat.completions.create(
            model=settings.GROQ_TOOL_USE_MODEL,
            messages=chat_history,
            tools=self.tools,
            tool_choice="auto",
            max_completion_tokens=4096,
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            return response_message.content

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            try:
                async with self.mcp_client as _:
                    mcp_response = await self.mcp_client.call_tool(
                        function_name, function_args
                    )
                    function_response = mcp_response[0].text
            except Exception as e:
                logger.error(f"Error calling tool {function_name}: {str(e)}")
                function_response = f"Error executing tool {function_name}: {str(e)}"

            chat_history.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        if function_name == "get_video_clip_from_user_query":
            second_response = self.instructor_client.chat.completions.create(
                model=settings.GROQ_TOOL_USE_MODEL,
                messages=chat_history,
                response_model=VideoClipResponseModel,
            )
        else:
            second_response = self.instructor_client.chat.completions.create(
                model=settings.GROQ_TOOL_USE_MODEL,
                messages=chat_history,
                response_model=GeneralResponseModel,
            )
        logger.info(f"Second response: {second_response}")
        return second_response

    @opik.track(name="general-response-with-image", type="llm")
    def _run_with_image(self, message: str, image_base64: str) -> str:
        """Execute chat completion with image usage."""
        chat_history = self._build_chat_history(
            self.general_system_prompt, message, image_base64
        )

        response = self.client.chat.completions.create(
            model=settings.GROQ_IMAGE_MODEL,
            messages=chat_history,
        )
        return response.choices[0].message.content

    @opik.track(name="generate-response", type="llm")
    def _run_general(self, message: str) -> str:
        """Execute general chat completion without tool usage."""
        chat_history = self._build_chat_history(self.general_system_prompt, message)

        response = self.instructor_client.chat.completions.create(
            model=settings.GROQ_GENERAL_MODEL,
            messages=chat_history,
            response_model=GeneralResponseModel,
        )
        return response

    @opik.track(name="memory-insertion", type="general")
    def _add_to_memory(self, role: str, content: str) -> None:
        """Add a message to the agent's memory."""
        self.memory.insert(
            MemoryRecord(
                message_id=str(uuid.uuid4()),
                role=role,
                content=content,
                timestamp=datetime.now(),
            )
        )

    @opik.track(name="chat", type="general")
    async def chat(
        self,
        message: str,
        video_path: str | None = None,
        image_base64: str | None = None,
    ) -> str:
        """Process a chat message and return the response."""
        opik_context.update_current_trace(thread_id=self.thread_id)

        if image_base64:
            tool_use = self._route_query(message, video_path)
            logger.info(f"Tool use: {tool_use}")
            response = (
                await self._run_with_tool(message, video_path)
                if tool_use
                else self._run_with_image(message, image_base64)
            )
            self._add_to_memory("user", message)
            self._add_to_memory("assistant", response.content)
            return response

        if video_path:
            tool_use = self._route_query(message, video_path)
            logger.info(f"Tool use: {tool_use}")
            response = (
                await self._run_with_tool(message, video_path)
                if tool_use
                else self._run_general(message)
            )
            self._add_to_memory("user", message)
            self._add_to_memory("assistant", response.content)
            return response

        response = self._run_general(message)
        
        self._add_to_memory("user", message)
        self._add_to_memory("assistant", response.content)
        
        return response
