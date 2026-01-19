"""MCP (Model Context Protocol) Adapter for external tool integration."""

import asyncio
import json
from typing import Any, Callable, Optional

from langchain_core.tools import BaseTool, ToolException
from pydantic import BaseModel, Field

from src.config import get_settings
from src.tools.registry import ToolRegistry, ToolStatus


class MCPServerConfig(BaseModel):
    """Configuration for an MCP server."""
    name: str = Field(..., description="Server name")
    command: str = Field(..., description="Command to start the server")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] = Field(default_factory=dict, description="Environment variables")


class MCPToolWrapper(BaseTool):
    """Wrapper to make MCP tools compatible with LangChain."""

    name: str = ""
    description: str = ""
    mcp_server: str = ""
    mcp_tool_name: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)
    _adapter: Optional["MCPAdapter"] = None

    def __init__(
        self,
        name: str,
        description: str,
        mcp_server: str,
        mcp_tool_name: str,
        input_schema: dict[str, Any] = None,
        adapter: "MCPAdapter" = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.mcp_server = mcp_server
        self.mcp_tool_name = mcp_tool_name
        self.input_schema = input_schema or {}
        self._adapter = adapter

    def _run(self, **kwargs) -> str:
        """Sync execution (not recommended for MCP)."""
        return asyncio.run(self._arun(**kwargs))

    async def _arun(self, **kwargs) -> str:
        """Async execution of MCP tool."""
        if not self._adapter:
            raise ToolException("MCP adapter not configured")

        try:
            result = await self._adapter.call_tool(
                server=self.mcp_server,
                tool_name=self.mcp_tool_name,
                arguments=kwargs
            )
            return json.dumps(result) if isinstance(result, dict) else str(result)
        except Exception as e:
            raise ToolException(f"MCP tool execution failed: {str(e)}")


class MCPAdapter:
    """
    Adapter for integrating MCP (Model Context Protocol) servers.

    This adapter:
    1. Discovers available MCP servers
    2. Lists tools from each server
    3. Wraps MCP tools for LangChain compatibility
    4. Handles tool execution via MCP protocol
    """

    def __init__(self):
        self.servers: dict[str, MCPServerConfig] = {}
        self.connected_servers: set[str] = set()
        self._tool_cache: dict[str, list[dict]] = {}
        self.registry = ToolRegistry.get_instance()

    def register_server(self, config: MCPServerConfig) -> None:
        """Register an MCP server configuration."""
        self.servers[config.name] = config

    async def connect_server(self, server_name: str) -> bool:
        """
        Connect to an MCP server and discover its tools.

        In a real implementation, this would:
        1. Start the MCP server process
        2. Establish stdio/SSE connection
        3. Call tools/list to get available tools
        4. Register tools with the ToolRegistry
        """
        if server_name not in self.servers:
            return False

        config = self.servers[server_name]

        # TODO: Implement actual MCP connection
        # For now, this is a placeholder that simulates connection

        # Simulate tool discovery
        # In real implementation, this would come from MCP tools/list
        discovered_tools = await self._discover_tools(server_name)

        for tool_info in discovered_tools:
            wrapper = MCPToolWrapper(
                name=f"{server_name}_{tool_info['name']}",
                description=tool_info.get("description", ""),
                mcp_server=server_name,
                mcp_tool_name=tool_info["name"],
                input_schema=tool_info.get("inputSchema", {}),
                adapter=self
            )

            self.registry.register_langchain_tool(
                tool=wrapper,
                category="mcp",
                tool_type="mcp",
                capabilities=tool_info.get("capabilities", [])
            )
            self.registry.mark_connected(wrapper.name)

        self.connected_servers.add(server_name)
        self._tool_cache[server_name] = discovered_tools
        return True

    async def disconnect_server(self, server_name: str) -> bool:
        """Disconnect from an MCP server."""
        if server_name in self.connected_servers:
            self.connected_servers.remove(server_name)

            # Update tool statuses
            for tool_info in self._tool_cache.get(server_name, []):
                tool_id = f"{server_name}_{tool_info['name']}"
                self.registry.update_status(tool_id, ToolStatus.NOT_CONNECTED)

            return True
        return False

    async def _discover_tools(self, server_name: str) -> list[dict]:
        """
        Discover tools from an MCP server.

        This is a placeholder - real implementation would use MCP protocol.
        """
        # Placeholder tool definitions based on common MCP servers
        predefined_tools = {
            "figma": [
                {
                    "name": "get_file",
                    "description": "Get a Figma file by key",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_key": {"type": "string", "description": "Figma file key"}
                        },
                        "required": ["file_key"]
                    },
                    "capabilities": ["design", "figma", "read"]
                },
                {
                    "name": "get_components",
                    "description": "Get components from a Figma file",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "file_key": {"type": "string"}
                        },
                        "required": ["file_key"]
                    },
                    "capabilities": ["design", "figma", "components"]
                }
            ],
            "github": [
                {
                    "name": "create_repository",
                    "description": "Create a new GitHub repository",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "private": {"type": "boolean"}
                        },
                        "required": ["name"]
                    },
                    "capabilities": ["github", "repository", "create"]
                },
                {
                    "name": "create_issue",
                    "description": "Create a GitHub issue",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "owner": {"type": "string"},
                            "repo": {"type": "string"},
                            "title": {"type": "string"},
                            "body": {"type": "string"}
                        },
                        "required": ["owner", "repo", "title"]
                    },
                    "capabilities": ["github", "issue", "create"]
                }
            ],
            "slack": [
                {
                    "name": "send_message",
                    "description": "Send a message to a Slack channel",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "channel": {"type": "string"},
                            "text": {"type": "string"}
                        },
                        "required": ["channel", "text"]
                    },
                    "capabilities": ["slack", "message", "send"]
                }
            ]
        }

        return predefined_tools.get(server_name, [])

    async def call_tool(
        self,
        server: str,
        tool_name: str,
        arguments: dict[str, Any]
    ) -> Any:
        """
        Call an MCP tool.

        In real implementation, this would:
        1. Send tools/call request via MCP protocol
        2. Wait for response
        3. Return result
        """
        if server not in self.connected_servers:
            raise Exception(f"Server {server} is not connected")

        # TODO: Implement actual MCP tool call
        # This is a placeholder
        return {
            "status": "success",
            "message": f"Called {tool_name} on {server}",
            "arguments": arguments,
            "note": "This is a placeholder response. Implement actual MCP call."
        }

    def get_server_tools(self, server_name: str) -> list[BaseTool]:
        """Get all tools from a specific server."""
        tools = []
        for tool_info in self._tool_cache.get(server_name, []):
            tool_id = f"{server_name}_{tool_info['name']}"
            tool = self.registry.get_tool(tool_id)
            if tool:
                tools.append(tool)
        return tools

    def list_servers(self) -> dict[str, dict[str, Any]]:
        """List all registered servers and their status."""
        return {
            name: {
                "config": config.model_dump(),
                "connected": name in self.connected_servers,
                "tools_count": len(self._tool_cache.get(name, []))
            }
            for name, config in self.servers.items()
        }


# Pre-configured MCP servers
DEFAULT_MCP_SERVERS = [
    MCPServerConfig(
        name="figma",
        command="npx",
        args=["-y", "@anthropic/mcp-server-figma"],
        env={"FIGMA_ACCESS_TOKEN": ""}
    ),
    MCPServerConfig(
        name="github",
        command="npx",
        args=["-y", "@anthropic/mcp-server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": ""}
    ),
    MCPServerConfig(
        name="slack",
        command="npx",
        args=["-y", "@anthropic/mcp-server-slack"],
        env={"SLACK_BOT_TOKEN": "", "SLACK_TEAM_ID": ""}
    ),
]


def create_mcp_adapter() -> MCPAdapter:
    """Factory function to create configured MCP adapter."""
    adapter = MCPAdapter()
    settings = get_settings()

    # Register default servers with tokens from settings
    for config in DEFAULT_MCP_SERVERS:
        if config.name == "figma" and settings.mcp_figma_token:
            config.env["FIGMA_ACCESS_TOKEN"] = settings.mcp_figma_token
        elif config.name == "github" and settings.mcp_github_token:
            config.env["GITHUB_PERSONAL_ACCESS_TOKEN"] = settings.mcp_github_token
        elif config.name == "slack" and settings.mcp_slack_token:
            config.env["SLACK_BOT_TOKEN"] = settings.mcp_slack_token

        adapter.register_server(config)

    return adapter
