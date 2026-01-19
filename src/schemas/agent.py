"""Agent schemas for AI Company."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentRole(str, Enum):
    """Agent role types."""
    HR = "hr"
    RM = "rm"
    EXPERT = "expert"


class AgentStatus(str, Enum):
    """Agent status."""
    ACTIVE = "active"
    BUSY = "busy"
    INACTIVE = "inactive"


class AgentDefinition(BaseModel):
    """Definition for dynamically created agents."""
    agent_id: str = Field(..., description="Unique agent identifier")
    role: AgentRole = Field(..., description="Agent role type")
    role_name: str = Field(..., description="Human-readable role name (e.g., '풀스택 개발자')")
    description: str = Field(..., description="Role description")

    # Capabilities
    specialties: list[str] = Field(default_factory=list, description="Areas of expertise")
    tools: list[str] = Field(default_factory=list, description="Tools this agent can use")
    limitations: list[str] = Field(default_factory=list, description="What this agent cannot do")

    # Status
    status: AgentStatus = Field(default=AgentStatus.ACTIVE)
    assigned_tasks: list[str] = Field(default_factory=list)

    # System prompt for the agent
    system_prompt: Optional[str] = Field(default=None)

    # Metadata
    created_by: str = Field(default="hr-agent")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_system_prompt(self) -> str:
        """Generate system prompt for this agent."""
        if self.system_prompt:
            return self.system_prompt

        specialties_str = ", ".join(self.specialties) if self.specialties else "일반"
        limitations_str = "\n".join(f"- {l}" for l in self.limitations) if self.limitations else "없음"
        tools_str = ", ".join(self.tools) if self.tools else "기본 도구만 사용"

        return f"""당신은 {self.role_name} 전문가입니다.

## 역할
{self.description}

## 전문 분야
{specialties_str}

## 사용 가능한 도구
{tools_str}

## 역할 한계
{limitations_str}

위 한계를 초과하는 작업이 필요한 경우, RM에게 Escalation하세요.

## 작업 수행 원칙
1. 필요한 정보가 부족하면 명확히 요청하세요
2. 도구를 사용하여 실제 액션을 수행하세요
3. 결과를 검증하고 보고하세요
4. 확실하지 않은 것은 가정하지 말고 확인하세요
"""


class AgentRequest(BaseModel):
    """Request for new agent creation (RM -> HR)."""
    requested_by: str = Field(default="rm-agent")
    role_name: str = Field(..., description="Desired role name")
    reason: str = Field(..., description="Why this agent is needed")
    required_specialties: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    context: Optional[str] = Field(default=None, description="Additional context")


class EscalationRequest(BaseModel):
    """Escalation request from Expert to RM."""
    task_id: str
    from_agent: str
    reason: str = Field(..., description="Why escalation is needed")
    escalation_type: str = Field(..., description="expertise_exceeded, unclear_requirements, dependency_issue, technical_limitation")
    required_expertise: Optional[str] = Field(default=None)
    suggestion: Optional[str] = Field(default=None, description="Suggested resolution")
    context: dict[str, Any] = Field(default_factory=dict)
