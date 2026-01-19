"""Human Interface for CEO interaction."""

from datetime import datetime
from typing import Any, Callable, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from src.context.state import HumanInterrupt, HumanResponse, InterruptType


class InterruptHandler:
    """
    Handler for processing human interrupts.

    Manages the workflow of:
    1. Presenting interrupts to CEO
    2. Collecting responses
    3. Validating inputs
    4. Routing responses back to the graph
    """

    def __init__(self):
        self._pending_interrupts: dict[str, HumanInterrupt] = {}
        self._responses: dict[str, HumanResponse] = {}
        self._callbacks: dict[str, Callable] = {}

    def create_interrupt(
        self,
        interrupt_type: InterruptType,
        from_agent: str,
        message: str,
        required_inputs: list[dict] = None,
        options: list[str] = None,
        context: dict = None,
        task_id: str = None,
        project_id: str = None,
        callback: Callable = None,
    ) -> HumanInterrupt:
        """Create and register an interrupt."""
        interrupt = HumanInterrupt(
            interrupt_type=interrupt_type,
            from_agent=from_agent,
            message=message,
            required_inputs=required_inputs or [],
            options=options or [],
            context=context or {},
            task_id=task_id,
            project_id=project_id,
        )

        interrupt_id = str(interrupt.created_at)
        self._pending_interrupts[interrupt_id] = interrupt

        if callback:
            self._callbacks[interrupt_id] = callback

        return interrupt

    def get_pending(self) -> list[HumanInterrupt]:
        """Get all pending interrupts."""
        return list(self._pending_interrupts.values())

    def get_interrupt(self, interrupt_id: str) -> Optional[HumanInterrupt]:
        """Get a specific interrupt by ID."""
        return self._pending_interrupts.get(interrupt_id)

    def submit_response(
        self,
        interrupt_id: str,
        approved: bool = None,
        inputs: dict[str, Any] = None,
        message: str = None,
    ) -> Optional[HumanResponse]:
        """Submit a response to an interrupt."""
        if interrupt_id not in self._pending_interrupts:
            return None

        interrupt = self._pending_interrupts[interrupt_id]

        # Validate required inputs
        if interrupt.required_inputs:
            missing = []
            for inp in interrupt.required_inputs:
                if inp.get("required", True) and inp["key"] not in (inputs or {}):
                    missing.append(inp["key"])
            if missing:
                raise ValueError(f"Missing required inputs: {missing}")

        response = HumanResponse(
            interrupt_id=interrupt_id,
            approved=approved,
            inputs=inputs or {},
            message=message,
        )

        self._responses[interrupt_id] = response

        # Remove from pending
        del self._pending_interrupts[interrupt_id]

        # Call callback if registered
        if interrupt_id in self._callbacks:
            self._callbacks[interrupt_id](response)
            del self._callbacks[interrupt_id]

        return response

    def get_response(self, interrupt_id: str) -> Optional[HumanResponse]:
        """Get a submitted response."""
        return self._responses.get(interrupt_id)

    def format_for_display(self, interrupt: HumanInterrupt) -> dict[str, Any]:
        """Format an interrupt for display to CEO."""
        display = {
            "type": interrupt.interrupt_type.value,
            "from": interrupt.from_agent,
            "message": interrupt.message,
            "timestamp": interrupt.created_at.isoformat(),
        }

        if interrupt.required_inputs:
            display["inputs_needed"] = [
                {
                    "name": inp["key"],
                    "label": inp.get("label", inp["key"]),
                    "type": inp.get("type", "text"),
                    "description": inp.get("description", ""),
                    "example": inp.get("example", ""),
                }
                for inp in interrupt.required_inputs
            ]

        if interrupt.options:
            display["options"] = interrupt.options

        if interrupt.context:
            display["context"] = interrupt.context

        if interrupt.task_id:
            display["task_id"] = interrupt.task_id

        if interrupt.project_id:
            display["project_id"] = interrupt.project_id

        return display


class HumanInterface:
    """
    Interface for human (CEO) interaction with the AI Company.

    Provides methods for:
    - Submitting goals and requests
    - Responding to interrupts
    - Viewing status and progress
    - Approving or rejecting actions
    """

    def __init__(self):
        self.interrupt_handler = InterruptHandler()
        self._session_id: str = str(uuid4())
        self._conversation_history: list[dict] = []

    @property
    def session_id(self) -> str:
        """Get current session ID."""
        return self._session_id

    def start_new_session(self) -> str:
        """Start a new session."""
        self._session_id = str(uuid4())
        self._conversation_history = []
        return self._session_id

    def add_to_history(
        self,
        role: str,
        content: str,
        metadata: dict = None
    ) -> None:
        """Add an entry to conversation history."""
        self._conversation_history.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_history(self) -> list[dict]:
        """Get conversation history."""
        return self._conversation_history

    def get_pending_interrupts(self) -> list[dict]:
        """Get all pending interrupts formatted for display."""
        return [
            self.interrupt_handler.format_for_display(i)
            for i in self.interrupt_handler.get_pending()
        ]

    def respond_to_interrupt(
        self,
        interrupt_id: str,
        approved: bool = None,
        inputs: dict[str, Any] = None,
        message: str = None,
    ) -> HumanResponse:
        """Respond to a pending interrupt."""
        response = self.interrupt_handler.submit_response(
            interrupt_id=interrupt_id,
            approved=approved,
            inputs=inputs,
            message=message,
        )

        if not response:
            raise ValueError(f"Interrupt {interrupt_id} not found")

        # Log to history
        self.add_to_history(
            role="ceo",
            content=f"Responded to interrupt: approved={approved}",
            metadata={"interrupt_id": interrupt_id, "inputs": inputs}
        )

        return response

    def approve(self, interrupt_id: str, message: str = None) -> HumanResponse:
        """Approve an action."""
        return self.respond_to_interrupt(
            interrupt_id=interrupt_id,
            approved=True,
            message=message
        )

    def reject(self, interrupt_id: str, message: str = None) -> HumanResponse:
        """Reject an action."""
        return self.respond_to_interrupt(
            interrupt_id=interrupt_id,
            approved=False,
            message=message
        )

    def provide_inputs(
        self,
        interrupt_id: str,
        inputs: dict[str, Any]
    ) -> HumanResponse:
        """Provide requested inputs."""
        return self.respond_to_interrupt(
            interrupt_id=interrupt_id,
            inputs=inputs
        )
