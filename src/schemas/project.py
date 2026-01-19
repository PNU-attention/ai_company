"""Project schemas for AI Company."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    """Project status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class Project(BaseModel):
    """Project definition."""
    project_id: str = Field(..., description="Unique project identifier")
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")

    # Goal reference
    goal_description: str = Field(..., description="CEO's original goal this project addresses")

    # Status
    status: ProjectStatus = Field(default=ProjectStatus.PENDING)
    priority: str = Field(default="medium", description="high, medium, low")

    # Deliverables
    deliverables: list[str] = Field(default_factory=list, description="Expected deliverables")

    # Dependencies
    dependencies: list[str] = Field(default_factory=list, description="Dependent project IDs")

    # Tasks (will be populated by RM)
    task_ids: list[str] = Field(default_factory=list, description="Task IDs in this project")

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    # Metadata
    created_by: str = Field(default="rm-agent")


class ExecutionGraph(BaseModel):
    """Execution graph for tasks within a project."""
    project_id: str
    nodes: list[dict] = Field(default_factory=list, description="Task nodes")
    edges: list[dict] = Field(default_factory=list, description="Dependencies between tasks")
    parallel_groups: list[list[str]] = Field(default_factory=list, description="Tasks that can run in parallel")
