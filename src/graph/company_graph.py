"""Main company graph implementation using LangGraph."""

from typing import Any, Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.context.state import CEORequest, CompanyState, HumanResponse
from src.graph.edges import EdgeConditions
from src.graph.nodes import NodeFunctions


class CompanyGraph:
    """
    Main orchestration graph for the AI Company.

    This graph coordinates all agents and manages the execution flow:
    1. CEO provides goals/requests
    2. HR analyzes and creates appropriate agents
    3. RM creates projects and tasks
    4. Executor dispatches tasks to experts
    5. Human-in-the-loop for inputs/approvals
    6. Completion and reporting
    """

    def __init__(self, checkpointer: Optional[Any] = None):
        self.nodes = NodeFunctions()
        self.edges = EdgeConditions()
        self.checkpointer = checkpointer or MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph."""
        # Create graph with CompanyState
        graph = StateGraph(CompanyState)

        # Add nodes
        graph.add_node("initialize", self.nodes.initialize_node)
        graph.add_node("hr", self.nodes.hr_node)
        graph.add_node("rm", self.nodes.rm_node)
        graph.add_node("executor", self.nodes.executor_node)
        graph.add_node("human_input", self.nodes.human_input_node)
        graph.add_node("completion", self.nodes.completion_node)

        # Set entry point
        graph.set_entry_point("initialize")

        # Add conditional edges
        graph.add_conditional_edges(
            "initialize",
            self.edges.after_initialize,
            {
                "hr": "hr",
                "end": END
            }
        )

        graph.add_conditional_edges(
            "hr",
            self.edges.after_hr,
            {
                "rm": "rm",
                "human_input": "human_input",
                "end": END
            }
        )

        graph.add_conditional_edges(
            "rm",
            self.edges.after_rm,
            {
                "executor": "executor",
                "hr": "hr",
                "human_input": "human_input",
                "end": END
            }
        )

        graph.add_conditional_edges(
            "executor",
            self.edges.after_executor,
            {
                "executor": "executor",
                "rm": "rm",
                "human_input": "human_input",
                "completion": "completion",
                "end": END
            }
        )

        graph.add_conditional_edges(
            "human_input",
            self.edges.after_human_input,
            {
                "hr": "hr",
                "rm": "rm",
                "executor": "executor",
                "end": END
            }
        )

        # Completion goes to END
        graph.add_edge("completion", END)

        # Compile with checkpointer and interrupt points
        compiled = graph.compile(
            checkpointer=self.checkpointer,
            interrupt_before=["human_input"]  # Interrupt before human input for CEO
        )

        return compiled

    async def run(
        self,
        ceo_request: CEORequest,
        thread_id: str = "default"
    ) -> CompanyState:
        """
        Run the company graph with a CEO request.

        Args:
            ceo_request: The CEO's goal/request
            thread_id: Thread ID for checkpointing

        Returns:
            Final CompanyState
        """
        initial_state = CompanyState(ceo_request=ceo_request)

        config = {"configurable": {"thread_id": thread_id}}

        # Run until completion or interrupt
        result = await self.graph.ainvoke(
            initial_state.model_dump(),
            config=config
        )

        return CompanyState(**result)

    async def resume(
        self,
        human_response: HumanResponse,
        thread_id: str = "default"
    ) -> CompanyState:
        """
        Resume execution after human input.

        Args:
            human_response: CEO's response to interrupt
            thread_id: Thread ID for checkpointing

        Returns:
            Updated CompanyState
        """
        config = {"configurable": {"thread_id": thread_id}}

        # Get current state
        current_state = await self.graph.aget_state(config)

        if current_state.values:
            state_dict = dict(current_state.values)
            # Add human response
            responses = state_dict.get("human_responses", [])
            responses.append(human_response.model_dump())
            state_dict["human_responses"] = responses

            # Resume execution
            result = await self.graph.ainvoke(
                state_dict,
                config=config
            )

            return CompanyState(**result)

        return CompanyState()

    def get_state(self, thread_id: str = "default") -> Optional[CompanyState]:
        """Get current state for a thread."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if state.values:
            return CompanyState(**state.values)
        return None

    def get_pending_interrupt(self, thread_id: str = "default") -> Optional[dict]:
        """Get pending interrupt data if any."""
        state = self.get_state(thread_id)
        if state and state.pending_interrupts:
            return self.edges.get_interrupt_data(state)
        return None


def create_company_graph(checkpointer: Optional[Any] = None) -> CompanyGraph:
    """Factory function to create a CompanyGraph instance."""
    return CompanyGraph(checkpointer=checkpointer)
