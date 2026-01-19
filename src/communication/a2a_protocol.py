"""Agent-to-Agent (A2A) Communication Protocol.

Based on Google's A2A Protocol concepts for standardized agent communication.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of A2A messages."""
    REQUEST = "request"  # Request action/information
    RESPONSE = "response"  # Response to a request
    NOTIFICATION = "notification"  # One-way notification
    ESCALATION = "escalation"  # Escalation to supervisor
    DELEGATION = "delegation"  # Task delegation
    STATUS = "status"  # Status update
    ERROR = "error"  # Error notification


class A2AMessage(BaseModel):
    """
    Standardized message format for agent-to-agent communication.

    Based on A2A Protocol for interoperability.
    """
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    message_type: MessageType = Field(..., description="Type of message")

    # Routing
    from_agent: str = Field(..., description="Sender agent ID")
    to_agent: str = Field(..., description="Recipient agent ID")

    # Content
    action: str = Field(..., description="Requested action or response type")
    payload: dict[str, Any] = Field(default_factory=dict, description="Message payload")

    # Context
    context: dict[str, Any] = Field(default_factory=dict, description="Execution context")
    correlation_id: Optional[str] = Field(default=None, description="For request-response correlation")
    reply_to: Optional[str] = Field(default=None, description="Message ID this is replying to")

    # Metadata
    priority: str = Field(default="normal", description="high, normal, low")
    timeout_seconds: Optional[int] = Field(default=None, description="Response timeout")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def create_response(
        self,
        payload: dict[str, Any],
        message_type: MessageType = MessageType.RESPONSE
    ) -> "A2AMessage":
        """Create a response to this message."""
        return A2AMessage(
            message_type=message_type,
            from_agent=self.to_agent,
            to_agent=self.from_agent,
            action=f"{self.action}_response",
            payload=payload,
            context=self.context,
            correlation_id=self.correlation_id or self.message_id,
            reply_to=self.message_id,
        )

    def create_error(self, error: str, details: dict = None) -> "A2AMessage":
        """Create an error response to this message."""
        return A2AMessage(
            message_type=MessageType.ERROR,
            from_agent=self.to_agent,
            to_agent=self.from_agent,
            action="error",
            payload={"error": error, "details": details or {}},
            context=self.context,
            correlation_id=self.correlation_id or self.message_id,
            reply_to=self.message_id,
        )


class A2AProtocol:
    """
    Handler for A2A protocol communication.

    Manages message routing, delivery, and response tracking.
    """

    def __init__(self):
        self._message_queue: dict[str, list[A2AMessage]] = {}  # agent_id -> messages
        self._pending_responses: dict[str, A2AMessage] = {}  # correlation_id -> original message
        self._message_handlers: dict[str, callable] = {}  # agent_id -> handler

    def register_agent(self, agent_id: str, handler: callable = None) -> None:
        """Register an agent with optional message handler."""
        if agent_id not in self._message_queue:
            self._message_queue[agent_id] = []
        if handler:
            self._message_handlers[agent_id] = handler

    def send_message(self, message: A2AMessage) -> str:
        """
        Send a message to another agent.

        Returns the message ID.
        """
        # Ensure recipient is registered
        if message.to_agent not in self._message_queue:
            self._message_queue[message.to_agent] = []

        self._message_queue[message.to_agent].append(message)

        # Track if expecting response
        if message.message_type == MessageType.REQUEST:
            correlation_id = message.correlation_id or message.message_id
            self._pending_responses[correlation_id] = message

        # Call handler if registered
        if message.to_agent in self._message_handlers:
            handler = self._message_handlers[message.to_agent]
            try:
                handler(message)
            except Exception as e:
                # Send error back
                error_msg = message.create_error(str(e))
                self.send_message(error_msg)

        return message.message_id

    def get_messages(self, agent_id: str, clear: bool = True) -> list[A2AMessage]:
        """Get pending messages for an agent."""
        messages = self._message_queue.get(agent_id, [])
        if clear:
            self._message_queue[agent_id] = []
        return messages

    def get_message_by_id(self, message_id: str, agent_id: str) -> Optional[A2AMessage]:
        """Get a specific message by ID."""
        for msg in self._message_queue.get(agent_id, []):
            if msg.message_id == message_id:
                return msg
        return None

    def send_request(
        self,
        from_agent: str,
        to_agent: str,
        action: str,
        payload: dict[str, Any] = None,
        context: dict[str, Any] = None,
        priority: str = "normal",
        timeout_seconds: int = None,
    ) -> A2AMessage:
        """Helper to send a request message."""
        message = A2AMessage(
            message_type=MessageType.REQUEST,
            from_agent=from_agent,
            to_agent=to_agent,
            action=action,
            payload=payload or {},
            context=context or {},
            priority=priority,
            timeout_seconds=timeout_seconds,
        )
        self.send_message(message)
        return message

    def send_delegation(
        self,
        from_agent: str,
        to_agent: str,
        task_id: str,
        task_details: dict[str, Any],
        context: dict[str, Any] = None,
    ) -> A2AMessage:
        """Helper to send a task delegation message."""
        message = A2AMessage(
            message_type=MessageType.DELEGATION,
            from_agent=from_agent,
            to_agent=to_agent,
            action="delegate_task",
            payload={"task_id": task_id, "task_details": task_details},
            context=context or {},
        )
        self.send_message(message)
        return message

    def send_escalation(
        self,
        from_agent: str,
        to_agent: str,
        reason: str,
        task_id: str = None,
        context: dict[str, Any] = None,
    ) -> A2AMessage:
        """Helper to send an escalation message."""
        message = A2AMessage(
            message_type=MessageType.ESCALATION,
            from_agent=from_agent,
            to_agent=to_agent,
            action="escalate",
            payload={"reason": reason, "task_id": task_id},
            context=context or {},
            priority="high",
        )
        self.send_message(message)
        return message

    def send_status_update(
        self,
        from_agent: str,
        to_agent: str,
        status: str,
        details: dict[str, Any] = None,
        task_id: str = None,
    ) -> A2AMessage:
        """Helper to send a status update."""
        message = A2AMessage(
            message_type=MessageType.STATUS,
            from_agent=from_agent,
            to_agent=to_agent,
            action="status_update",
            payload={"status": status, "details": details or {}, "task_id": task_id},
        )
        self.send_message(message)
        return message

    def check_response(self, correlation_id: str) -> Optional[A2AMessage]:
        """Check if a response has been received for a request."""
        original = self._pending_responses.get(correlation_id)
        if not original:
            return None

        # Look for response in sender's queue
        for msg in self._message_queue.get(original.from_agent, []):
            if msg.reply_to == original.message_id or msg.correlation_id == correlation_id:
                return msg

        return None

    def clear_pending(self, correlation_id: str) -> None:
        """Clear a pending response tracker."""
        if correlation_id in self._pending_responses:
            del self._pending_responses[correlation_id]
