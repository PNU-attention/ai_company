"""Company State definition for LangGraph."""

from datetime import datetime
from enum import Enum
from typing import Annotated, Any, Optional

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.schemas.agent import AgentDefinition, AgentRequest, EscalationRequest
from src.schemas.project import Project
from src.schemas.task import Task, TaskResult


class InterruptType(str, Enum):
    """Types of human interrupts."""
    INFO_REQUEST = "info_request"  # Need information from CEO
    APPROVAL_REQUEST = "approval_request"  # Need CEO approval
    TOOL_CONNECTION = "tool_connection"  # Need tool/MCP connection
    ERROR_REPORT = "error_report"  # Report error to CEO
    PROGRESS_REPORT = "progress_report"  # Report progress


class CEORequest(BaseModel):
    """Initial request from CEO."""
    goal: str = Field(..., description="Company goal/objective")
    kpis: list[str] = Field(default_factory=list, description="Key performance indicators")
    constraints: list[str] = Field(default_factory=list, description="Business constraints")
    context: Optional[str] = Field(default=None, description="Additional context")
    budget: Optional[str] = Field(default=None, description="Budget constraints")
    timeline: Optional[str] = Field(default=None, description="Expected timeline")


class HumanInterrupt(BaseModel):
    """Interrupt request for human input."""
    interrupt_type: InterruptType
    from_agent: str = Field(..., description="Agent requesting interrupt")
    message: str = Field(..., description="Message to show to CEO")
    required_inputs: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of required inputs with key, label, type, description"
    )
    options: list[str] = Field(default_factory=list, description="Options for approval")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context")
    task_id: Optional[str] = Field(default=None)
    project_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class HumanResponse(BaseModel):
    """Response from CEO to an interrupt."""
    interrupt_id: str
    approved: Optional[bool] = None
    inputs: dict[str, Any] = Field(default_factory=dict)
    message: Optional[str] = None
    responded_at: datetime = Field(default_factory=datetime.utcnow)


class CompanyState(BaseModel):
    """
    Central state for the AI Company graph.

    This state is shared across all nodes in the LangGraph and represents
    the complete state of the company at any point in time.
    """

    # CEO Input
    ceo_request: Optional[CEORequest] = Field(default=None)

    # Messages (LangGraph message handling)
    messages: Annotated[list[Any], add_messages] = Field(default_factory=list)

    # Agents
    agents: dict[str, AgentDefinition] = Field(
        default_factory=dict,
        description="Active agents by agent_id"
    )
    agent_requests: list[AgentRequest] = Field(
        default_factory=list,
        description="Pending agent creation requests"
    )

    # Projects & Tasks
    projects: dict[str, Project] = Field(
        default_factory=dict,
        description="Projects by project_id"
    )
    tasks: dict[str, Task] = Field(
        default_factory=dict,
        description="Tasks by task_id"
    )
    task_results: dict[str, TaskResult] = Field(
        default_factory=dict,
        description="Task results by task_id"
    )

    # Execution Queue
    pending_tasks: list[str] = Field(
        default_factory=list,
        description="Task IDs ready for execution"
    )
    executing_tasks: list[str] = Field(
        default_factory=list,
        description="Currently executing task IDs"
    )

    # Human-in-the-Loop
    pending_interrupts: list[HumanInterrupt] = Field(
        default_factory=list,
        description="Pending interrupts waiting for CEO"
    )
    human_responses: list[HumanResponse] = Field(
        default_factory=list,
        description="Responses from CEO"
    )
    collected_inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="All collected inputs from CEO"
    )

    # Escalations
    escalations: list[EscalationRequest] = Field(
        default_factory=list,
        description="Escalation requests from experts"
    )

    # Tool Status
    connected_tools: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Connected tools and their status"
    )

    # Execution Control
    current_phase: str = Field(
        default="initialization",
        description="Current execution phase"
    )
    error: Optional[str] = Field(default=None)
    should_continue: bool = Field(default=True)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    def get_agent_by_role(self, role_name: str) -> Optional[AgentDefinition]:
        """Get agent by role name."""
        for agent in self.agents.values():
            if agent.role_name == role_name:
                return agent
        return None

    def get_available_agents(self) -> list[AgentDefinition]:
        """Get all available (not busy) agents."""
        from src.schemas.agent import AgentStatus
        return [
            agent for agent in self.agents.values()
            if agent.status == AgentStatus.ACTIVE
        ]

    def get_tasks_for_project(self, project_id: str) -> list[Task]:
        """Get all tasks for a project."""
        return [
            task for task in self.tasks.values()
            if task.project_id == project_id
        ]

    def get_pending_tasks_for_agent(self, agent_id: str) -> list[Task]:
        """Get pending tasks assigned to an agent."""
        from src.schemas.task import TaskStatus
        return [
            self.tasks[task_id]
            for task_id in self.pending_tasks
            if task_id in self.tasks
            and self.tasks[task_id].assigned_to == agent_id
            and self.tasks[task_id].status == TaskStatus.PENDING
        ]
