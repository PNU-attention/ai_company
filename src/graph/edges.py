"""Edge conditions for the company graph."""

from typing import Literal

from src.context.state import CompanyState
from src.schemas.task import TaskStatus


class EdgeConditions:
    """Collection of edge condition functions for routing."""

    @staticmethod
    def after_initialize(
        state: CompanyState
    ) -> Literal["hr", "end"]:
        """Route after initialization."""
        if state.error or not state.should_continue:
            return "end"
        return "hr"

    @staticmethod
    def after_hr(
        state: CompanyState
    ) -> Literal["rm", "human_input", "end"]:
        """Route after HR node."""
        if state.error:
            return "end"

        # Check for pending interrupts (need CEO input)
        if state.pending_interrupts:
            return "human_input"

        # If agents created, proceed to RM
        if len(state.agents) > 1:  # More than just HR
            return "rm"

        return "end"

    @staticmethod
    def after_rm(
        state: CompanyState
    ) -> Literal["executor", "hr", "human_input", "end"]:
        """Route after RM node."""
        if state.error:
            return "end"

        # Check for pending interrupts
        if state.pending_interrupts:
            return "human_input"

        # Check for agent requests
        if state.agent_requests:
            return "hr"

        # If tasks are pending, go to executor
        if state.pending_tasks:
            return "executor"

        # If all done
        if not state.should_continue:
            return "end"

        return "end"

    @staticmethod
    def after_executor(
        state: CompanyState
    ) -> Literal["executor", "rm", "human_input", "completion", "end"]:
        """Route after executor node."""
        if state.error:
            return "end"

        # Check for pending interrupts
        if state.pending_interrupts:
            return "human_input"

        # Check for escalations
        if state.escalations:
            return "rm"

        # Check for more pending tasks
        if state.pending_tasks:
            return "executor"

        # Check if all tasks are complete
        all_complete = all(
            task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
            for task in state.tasks.values()
        )

        if all_complete:
            return "completion"

        # Some tasks might be waiting for dependencies
        return "rm"

    @staticmethod
    def after_human_input(
        state: CompanyState
    ) -> Literal["hr", "rm", "executor", "end"]:
        """Route after human input is collected."""
        phase = state.current_phase

        if phase == "hr_analysis":
            return "hr"
        elif phase == "planning":
            return "rm"
        elif phase in ["executing", "planning_complete"]:
            return "executor"

        # Default: go back to RM for coordination
        return "rm"

    @staticmethod
    def should_interrupt(state: CompanyState) -> bool:
        """Check if we should interrupt for human input."""
        return bool(state.pending_interrupts)

    @staticmethod
    def get_interrupt_data(state: CompanyState) -> dict:
        """Get data to present during interrupt."""
        if not state.pending_interrupts:
            return {}

        interrupt = state.pending_interrupts[0]
        return {
            "type": interrupt.interrupt_type.value,
            "message": interrupt.message,
            "required_inputs": interrupt.required_inputs,
            "options": interrupt.options,
            "context": interrupt.context,
            "from_agent": interrupt.from_agent
        }
