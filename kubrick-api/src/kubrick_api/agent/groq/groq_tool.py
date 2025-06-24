from typing import Any, Dict, Optional
from pydantic import BaseModel


class GroqParameter(BaseModel):
    """Represents a parameter in a Groq tool definition."""

    type: str
    description: str
    default: Optional[Any] = None


class GroqParameters(BaseModel):
    """Represents the parameters object in a Groq tool definition."""

    type: str = "object"
    properties: Dict[str, GroqParameter]
    required: Optional[list[str]] = None


class GroqFunction(BaseModel):
    """Represents a function in a Groq tool definition."""

    name: str
    description: str
    parameters: GroqParameters


class GroqTool(BaseModel):
    """Represents a Groq tool definition."""

    type: str = "function"
    function: GroqFunction

    @classmethod
    def from_mcp_tool(cls, tool) -> "GroqTool":
        """Create a GroqTool instance from an MCP Tool."""
        properties = {}

        for field_name, field_info in tool.inputSchema["properties"].items():
            properties[field_name] = GroqParameter(
                type=field_info["type"],
                description=field_info["title"],
                default=field_info.get("default"),
            )

        parameters = GroqParameters(
            properties=properties, required=tool.inputSchema.get("required")
        )

        function = GroqFunction(
            name=tool.name, description=tool.description, parameters=parameters
        )

        return cls(function=function)


def transform_tool_definition(tool) -> dict:
    """Transform an MCP tool into a Groq tool definition dictionary."""
    return GroqTool.from_mcp_tool(tool).model_dump()
