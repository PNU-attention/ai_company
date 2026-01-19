"""Tool Registry for managing available tools."""

from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel, Field


class ToolStatus(str, Enum):
    """Tool connection status."""
    AVAILABLE = "available"  # Tool is ready to use
    CONNECTED = "connected"  # External service connected
    NOT_CONNECTED = "not_connected"  # Needs connection
    ERROR = "error"  # Connection error
    DISABLED = "disabled"  # Manually disabled


class ToolDefinition(BaseModel):
    """Definition of a tool in the registry."""
    tool_id: str = Field(..., description="Unique tool identifier")
    name: str = Field(..., description="Human-readable name")
    description: str = Field(..., description="What this tool does")
    category: str = Field(default="general", description="Tool category")
    type: str = Field(default="internal", description="internal, mcp, api")

    # Connection info
    status: ToolStatus = Field(default=ToolStatus.AVAILABLE)
    connection_url: Optional[str] = Field(default=None)
    requires_auth: bool = Field(default=False)

    # Capabilities
    capabilities: list[str] = Field(default_factory=list)
    input_schema: Optional[dict[str, Any]] = Field(default=None)
    output_schema: Optional[dict[str, Any]] = Field(default=None)

    # Metadata
    registered_at: datetime = Field(default_factory=datetime.utcnow)
    last_used: Optional[datetime] = Field(default=None)
    usage_count: int = Field(default=0)


class ToolRegistry:
    """
    Central registry for all tools available to the AI Company.

    Manages:
    - Internal tools (Python functions)
    - MCP tools (via MCP protocol)
    - External API tools
    """

    _instance: Optional["ToolRegistry"] = None
    _tools: dict[str, ToolDefinition] = {}
    _tool_implementations: dict[str, BaseTool] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tools = {}
            cls._instance._tool_implementations = {}
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ToolRegistry":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_tool(
        self,
        tool_id: str,
        name: str,
        description: str,
        func: Callable,
        category: str = "general",
        tool_type: str = "internal",
        capabilities: list[str] = None,
        input_schema: dict[str, Any] = None,
        requires_auth: bool = False,
        connection_url: str = None,
    ) -> ToolDefinition:
        """
        Register a new tool.

        Args:
            tool_id: Unique identifier
            name: Human-readable name
            description: What the tool does
            func: The actual function to execute
            category: Tool category (e.g., "ecommerce", "communication")
            tool_type: "internal", "mcp", or "api"
            capabilities: List of capabilities
            input_schema: JSON schema for inputs
            requires_auth: Whether authentication is required
            connection_url: URL for external services

        Returns:
            ToolDefinition
        """
        # Create tool definition
        definition = ToolDefinition(
            tool_id=tool_id,
            name=name,
            description=description,
            category=category,
            type=tool_type,
            capabilities=capabilities or [],
            input_schema=input_schema,
            requires_auth=requires_auth,
            connection_url=connection_url,
            status=ToolStatus.AVAILABLE if not requires_auth else ToolStatus.NOT_CONNECTED
        )

        # Create LangChain tool
        lc_tool = StructuredTool.from_function(
            func=func,
            name=tool_id,
            description=description,
        )

        self._tools[tool_id] = definition
        self._tool_implementations[tool_id] = lc_tool

        return definition

    def register_langchain_tool(
        self,
        tool: BaseTool,
        category: str = "general",
        tool_type: str = "internal",
        capabilities: list[str] = None,
    ) -> ToolDefinition:
        """Register an existing LangChain tool."""
        definition = ToolDefinition(
            tool_id=tool.name,
            name=tool.name,
            description=tool.description,
            category=category,
            type=tool_type,
            capabilities=capabilities or [],
            status=ToolStatus.AVAILABLE
        )

        self._tools[tool.name] = definition
        self._tool_implementations[tool.name] = tool

        return definition

    def get_tool(self, tool_id: str) -> Optional[BaseTool]:
        """Get a tool implementation by ID."""
        return self._tool_implementations.get(tool_id)

    def get_definition(self, tool_id: str) -> Optional[ToolDefinition]:
        """Get tool definition by ID."""
        return self._tools.get(tool_id)

    def get_tools_by_category(self, category: str) -> list[BaseTool]:
        """Get all tools in a category."""
        tools = []
        for tool_id, definition in self._tools.items():
            if definition.category == category:
                tool = self._tool_implementations.get(tool_id)
                if tool:
                    tools.append(tool)
        return tools

    def get_tools_by_capability(self, capability: str) -> list[BaseTool]:
        """Get all tools with a specific capability."""
        tools = []
        for tool_id, definition in self._tools.items():
            if capability in definition.capabilities:
                tool = self._tool_implementations.get(tool_id)
                if tool:
                    tools.append(tool)
        return tools

    def get_available_tools(self) -> list[BaseTool]:
        """Get all available (connected) tools."""
        tools = []
        for tool_id, definition in self._tools.items():
            if definition.status in [ToolStatus.AVAILABLE, ToolStatus.CONNECTED]:
                tool = self._tool_implementations.get(tool_id)
                if tool:
                    tools.append(tool)
        return tools

    def update_status(self, tool_id: str, status: ToolStatus) -> bool:
        """Update tool connection status."""
        if tool_id in self._tools:
            self._tools[tool_id].status = status
            return True
        return False

    def mark_connected(self, tool_id: str) -> bool:
        """Mark a tool as connected."""
        return self.update_status(tool_id, ToolStatus.CONNECTED)

    def mark_error(self, tool_id: str) -> bool:
        """Mark a tool as having an error."""
        return self.update_status(tool_id, ToolStatus.ERROR)

    def record_usage(self, tool_id: str) -> None:
        """Record tool usage."""
        if tool_id in self._tools:
            self._tools[tool_id].last_used = datetime.utcnow()
            self._tools[tool_id].usage_count += 1

    def list_all(self) -> list[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def list_by_status(self, status: ToolStatus) -> list[ToolDefinition]:
        """List tools by status."""
        return [t for t in self._tools.values() if t.status == status]

    def clear(self) -> None:
        """Clear all tools (for testing)."""
        self._tools.clear()
        self._tool_implementations.clear()

    def to_state_dict(self) -> dict[str, dict[str, Any]]:
        """Convert to state dict for CompanyState."""
        return {
            tool_id: {
                "name": definition.name,
                "status": definition.status.value,
                "type": definition.type,
                "capabilities": definition.capabilities
            }
            for tool_id, definition in self._tools.items()
        }
