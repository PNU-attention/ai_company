"""Tests for tool management."""

import pytest


class TestToolRegistry:
    """Tests for ToolRegistry."""

    def test_register_tool(self, tool_registry):
        """Test registering a tool."""
        def sample_tool(x: str) -> str:
            return f"Result: {x}"

        definition = tool_registry.register_tool(
            tool_id="test_tool",
            name="Test Tool",
            description="A test tool",
            func=sample_tool,
            category="test",
            capabilities=["testing"]
        )

        assert definition.tool_id == "test_tool"
        assert definition.category == "test"
        assert "testing" in definition.capabilities

    def test_get_tool(self, tool_registry):
        """Test getting a registered tool."""
        def sample_tool(x: str) -> str:
            return f"Result: {x}"

        tool_registry.register_tool(
            tool_id="get_test",
            name="Get Test",
            description="Test getting",
            func=sample_tool
        )

        tool = tool_registry.get_tool("get_test")
        assert tool is not None
        assert tool.name == "get_test"

    def test_get_tools_by_category(self, tool_registry):
        """Test getting tools by category."""
        def tool1(x: str) -> str:
            return x
        def tool2(x: str) -> str:
            return x

        tool_registry.register_tool(
            tool_id="cat_tool_1",
            name="Cat Tool 1",
            description="First category tool",
            func=tool1,
            category="ecommerce"
        )
        tool_registry.register_tool(
            tool_id="cat_tool_2",
            name="Cat Tool 2",
            description="Second category tool",
            func=tool2,
            category="ecommerce"
        )

        tools = tool_registry.get_tools_by_category("ecommerce")
        assert len(tools) == 2

    def test_tool_status_update(self, tool_registry):
        """Test updating tool status."""
        from src.tools.registry import ToolStatus

        def sample_tool(x: str) -> str:
            return x

        tool_registry.register_tool(
            tool_id="status_test",
            name="Status Test",
            description="Test status",
            func=sample_tool,
            requires_auth=True
        )

        # Initially not connected
        definition = tool_registry.get_definition("status_test")
        assert definition.status == ToolStatus.NOT_CONNECTED

        # Mark as connected
        tool_registry.mark_connected("status_test")
        definition = tool_registry.get_definition("status_test")
        assert definition.status == ToolStatus.CONNECTED

    def test_get_available_tools(self, tool_registry):
        """Test getting available tools only."""
        from src.tools.registry import ToolStatus

        def tool1(x: str) -> str:
            return x
        def tool2(x: str) -> str:
            return x

        tool_registry.register_tool(
            tool_id="available_tool",
            name="Available",
            description="Available tool",
            func=tool1
        )
        tool_registry.register_tool(
            tool_id="not_connected_tool",
            name="Not Connected",
            description="Not connected tool",
            func=tool2,
            requires_auth=True
        )

        available = tool_registry.get_available_tools()
        assert len(available) == 1
        assert available[0].name == "available_tool"


class TestMCPAdapter:
    """Tests for MCP Adapter."""

    def test_register_server(self):
        """Test registering an MCP server."""
        from src.tools.mcp_adapter import MCPAdapter, MCPServerConfig

        adapter = MCPAdapter()
        config = MCPServerConfig(
            name="test_server",
            command="test_command",
            args=["--test"]
        )

        adapter.register_server(config)
        servers = adapter.list_servers()

        assert "test_server" in servers
        assert servers["test_server"]["connected"] is False

    @pytest.mark.asyncio
    async def test_connect_server(self):
        """Test connecting to MCP server."""
        from src.tools.mcp_adapter import MCPAdapter, MCPServerConfig

        adapter = MCPAdapter()
        config = MCPServerConfig(
            name="github",
            command="npx",
            args=["-y", "@anthropic/mcp-server-github"]
        )

        adapter.register_server(config)
        result = await adapter.connect_server("github")

        assert result is True
        assert "github" in adapter.connected_servers

    @pytest.mark.asyncio
    async def test_call_tool(self):
        """Test calling an MCP tool."""
        from src.tools.mcp_adapter import MCPAdapter, MCPServerConfig

        adapter = MCPAdapter()
        config = MCPServerConfig(
            name="github",
            command="npx",
            args=["-y", "@anthropic/mcp-server-github"]
        )

        adapter.register_server(config)
        await adapter.connect_server("github")

        result = await adapter.call_tool(
            server="github",
            tool_name="create_issue",
            arguments={"owner": "test", "repo": "test", "title": "Test Issue"}
        )

        # Placeholder response
        assert result["status"] == "success"
