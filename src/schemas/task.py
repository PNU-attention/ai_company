"""Task schemas for AI Company."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Task type classification."""
    ACTION = "ACTION"  # 외부 시스템에 실제 변경을 가하는 작업
    DOCUMENT = "DOCUMENT"  # 문서/보고서 작성 작업
    RESEARCH = "RESEARCH"  # 정보 수집 및 분석 작업
    APPROVAL = "APPROVAL"  # CEO 승인 대기 작업


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "PENDING"
    INPUT_REQUIRED = "INPUT_REQUIRED"
    VALIDATING = "VALIDATING"
    TOOL_CHECK = "TOOL_CHECK"
    AWAITING_TOOL = "AWAITING_TOOL"
    APPROVAL_WAIT = "APPROVAL_WAIT"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RequiredInput(BaseModel):
    """Required input definition for a task."""
    key: str = Field(..., description="Input field key")
    label: str = Field(..., description="Human-readable label")
    type: str = Field(default="string", description="Data type: string, number, file, object")
    required: bool = Field(default=True)
    source: str = Field(default="ceo_input", description="Input source: ceo_input, previous_task, system")
    validation: Optional[str] = Field(default=None, description="Regex validation pattern")
    description: Optional[str] = Field(default=None, description="Description for CEO")
    example: Optional[str] = Field(default=None, description="Example value")


class ToolRequirement(BaseModel):
    """Tool requirement for a task."""
    tool_id: str = Field(..., description="Tool identifier")
    name: str = Field(..., description="Tool name")
    type: str = Field(default="mcp", description="Tool type: mcp, api, internal")
    required: bool = Field(default=True)
    status: str = Field(default="unknown", description="Connection status: connected, not_connected, unknown")
    fallback: Optional[str] = Field(default=None, description="Fallback tool ID if primary unavailable")
    capabilities: list[str] = Field(default_factory=list, description="Tool capabilities")


class ApprovalPoint(BaseModel):
    """Approval point requiring CEO confirmation."""
    point: str = Field(..., description="Approval point identifier")
    description: str = Field(..., description="What needs approval")
    approval_type: str = Field(default="explicit", description="explicit or notification")
    required_data: list[str] = Field(default_factory=list, description="Data to show for approval")


class ExecutionStep(BaseModel):
    """Execution step within a task."""
    step: int = Field(..., description="Step number")
    action: str = Field(..., description="Action identifier")
    description: str = Field(..., description="Step description")
    blocking: bool = Field(default=False, description="Whether this step blocks execution")
    tool: Optional[str] = Field(default=None, description="Tool to use")
    approval_point: Optional[str] = Field(default=None, description="Approval point if needed")


class Task(BaseModel):
    """Actionable Task schema."""
    task_id: str = Field(..., description="Unique task identifier")
    project_id: str = Field(..., description="Parent project ID")
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")

    type: TaskType = Field(..., description="Task type")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: str = Field(default="medium", description="high, medium, low")

    # Core fields for Agentic execution
    required_inputs: list[RequiredInput] = Field(default_factory=list)
    tools: list[ToolRequirement] = Field(default_factory=list)
    approval_points: list[ApprovalPoint] = Field(default_factory=list)
    execution_steps: list[ExecutionStep] = Field(default_factory=list)

    # Assignment
    assigned_to: Optional[str] = Field(default=None, description="Assigned agent role")
    dependencies: list[str] = Field(default_factory=list, description="Dependent task IDs")

    # Outputs
    outputs: list[dict[str, Any]] = Field(default_factory=list, description="Expected outputs")

    # Escalation
    escalation_conditions: list[dict[str, str]] = Field(default_factory=list)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    def has_missing_inputs(self, collected_inputs: dict) -> list[RequiredInput]:
        """Check for missing required inputs."""
        missing = []
        for inp in self.required_inputs:
            if inp.required and inp.key not in collected_inputs:
                missing.append(inp)
        return missing

    def has_approval_before_execution(self) -> bool:
        """Check if approval is needed before execution."""
        return any(
            ap.point == "before_execution" or ap.approval_type == "explicit"
            for ap in self.approval_points
        )


class TaskResult(BaseModel):
    """Result of task execution."""
    task_id: str
    status: TaskStatus
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    interrupt: bool = Field(default=False, description="Whether to interrupt for human input")
    request: Optional[dict[str, Any]] = Field(default=None, description="Request for CEO if interrupted")
    completed_at: Optional[datetime] = None
