"""Main entry point for AI Company."""

import asyncio
from typing import Optional

from src.context.state import CEORequest, HumanResponse
from src.context.checkpointer import create_checkpointer
from src.graph.company_graph import create_company_graph
from src.tools.mcp_adapter import create_mcp_adapter
from src.tools.registry import ToolRegistry


async def run_company(
    goal: str,
    kpis: list[str] = None,
    constraints: list[str] = None,
    context: str = None,
    budget: str = None,
    timeline: str = None,
    thread_id: str = "default"
) -> dict:
    """
    Run the AI Company with a CEO request.

    Args:
        goal: The company's goal/objective
        kpis: Key performance indicators
        constraints: Business constraints
        context: Additional context
        budget: Budget constraints
        timeline: Expected timeline
        thread_id: Session thread ID

    Returns:
        Final state as dictionary
    """
    # Create CEO request
    ceo_request = CEORequest(
        goal=goal,
        kpis=kpis or [],
        constraints=constraints or [],
        context=context,
        budget=budget,
        timeline=timeline
    )

    # Create checkpointer for state persistence
    checkpointer = create_checkpointer()

    # Create the company graph
    graph = create_company_graph(checkpointer=checkpointer)

    # Run the graph
    final_state = await graph.run(ceo_request, thread_id=thread_id)

    return final_state.model_dump()


async def resume_with_response(
    interrupt_id: str,
    approved: bool = None,
    inputs: dict = None,
    message: str = None,
    thread_id: str = "default"
) -> dict:
    """
    Resume execution after human input.

    Args:
        interrupt_id: ID of the interrupt being responded to
        approved: Approval status (if applicable)
        inputs: Input values provided
        message: Optional message
        thread_id: Session thread ID

    Returns:
        Updated state as dictionary
    """
    # Create response
    response = HumanResponse(
        interrupt_id=interrupt_id,
        approved=approved,
        inputs=inputs or {},
        message=message
    )

    # Create checkpointer and graph
    checkpointer = create_checkpointer()
    graph = create_company_graph(checkpointer=checkpointer)

    # Resume execution
    final_state = await graph.resume(response, thread_id=thread_id)

    return final_state.model_dump()


def get_pending_interrupts(thread_id: str = "default") -> Optional[dict]:
    """
    Get pending interrupts for a session.

    Args:
        thread_id: Session thread ID

    Returns:
        Interrupt data if any pending, None otherwise
    """
    checkpointer = create_checkpointer()
    graph = create_company_graph(checkpointer=checkpointer)

    return graph.get_pending_interrupt(thread_id)


async def setup_mcp_tools() -> dict:
    """
    Setup and connect MCP tools.

    Returns:
        Dictionary of connected tools and their status
    """
    adapter = create_mcp_adapter()
    registry = ToolRegistry.get_instance()

    # Try to connect to available servers
    connected = {}
    for server_name in adapter.servers:
        try:
            success = await adapter.connect_server(server_name)
            connected[server_name] = {
                "connected": success,
                "tools": len(adapter.get_server_tools(server_name)) if success else 0
            }
        except Exception as e:
            connected[server_name] = {
                "connected": False,
                "error": str(e)
            }

    return {
        "servers": connected,
        "total_tools": len(registry.get_available_tools())
    }


# Example usage
if __name__ == "__main__":
    async def main():
        # Example: Run with a goal
        result = await run_company(
            goal="쿠팡에 입점하여 월 매출 1000만원 달성",
            kpis=["월 매출 1000만원", "리뷰 평점 4.5 이상"],
            constraints=["초기 투자 500만원 이내"],
            context="패션 액세서리 판매 예정",
            budget="500만원",
            timeline="3개월"
        )

        print("Final State:")
        print(f"Phase: {result.get('current_phase')}")
        print(f"Projects: {len(result.get('projects', {}))}")
        print(f"Tasks: {len(result.get('tasks', {}))}")

        # Check for pending interrupts
        interrupt = get_pending_interrupts()
        if interrupt:
            print(f"\nPending Interrupt: {interrupt.get('type')}")
            print(f"Message: {interrupt.get('message')}")

    asyncio.run(main())
