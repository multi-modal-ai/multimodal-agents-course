from typing import Optional

import pixeltable as pxt
from core.base import BaseAgent
from utils import functions, queries

try:
    from pixeltable.functions.openai import chat_completions
except ImportError:
    raise ImportError("openai not found; run `pip install openai`")


class Agent(BaseAgent):
    """
    OpenAI-specific implementation of the BaseAgent.

    This agent uses OpenAI's chat completion API for generating responses and
        handling tools.
    It inherits common functionality from BaseAgent including:
    - Table setup and management
    - Memory persistence
    - Base chat and tool call implementations
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        model: str = "gpt-4o-mini",
        n_latest_messages: Optional[int] = 10,
        tools: Optional[pxt.tools] = None,
        reset: bool = False,
        chat_kwargs: Optional[dict] = None,
        tool_kwargs: Optional[dict] = None,
    ):
        # Initialize the base agent with all common parameters
        super().__init__(
            name=name,
            system_prompt=system_prompt,
            model=model,
            n_latest_messages=n_latest_messages,  # None for unlimited history
            tools=tools,
            reset=reset,
            chat_kwargs=chat_kwargs,
            tool_kwargs=tool_kwargs,
        )

    def _setup_chat_pipeline(self):
        """
        Configure the chat completion pipeline using Pixeltable's computed columns.
        This method implements the abstract method from BaseAgent.

        The pipeline consists of 4 steps:
        1. Retrieve recent messages from memory
        2. Format messages with system prompt
        3. Get completion from OpenAI
        4. Extract the response text
        """

        # Step 1: Define a query to get recent messages

        # Step 2: Add computed columns to process the conversation
        # First, get the conversation history
        self.agent.add_computed_column(
            memory_context=queries.get_recent_memory(
                self.agent.timestamp, self.agent.memory_table, self.n_latest_messages
            ),
            if_exists="ignore",
        )

        # Format messages for OpenAI with system prompt
        self.agent.add_computed_column(
            prompt=functions.create_messages_text(
                self.agent.system_prompt,
                self.agent.memory_context,
                self.agent.user_message,
            ),
            if_exists="ignore",
        )

        # Get OpenAI's API response
        self.agent.add_computed_column(
            response=chat_completions(messages=self.agent.prompt, model=self.model, **self.chat_kwargs),
            if_exists="ignore",
        )

        # Extract the final response text
        self.agent.add_computed_column(
            agent_response=self.agent.response.choices[0].message.content,
            if_exists="ignore",
        )
