"""HR Agent for AI Company - handles agent creation and management."""

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.context.state import CompanyState, HumanInterrupt, InterruptType
from src.schemas.agent import AgentDefinition, AgentRole, AgentStatus


class AgentProposal(BaseModel):
    """Proposed agent to create."""
    role_name: str = Field(..., description="Human-readable role name (e.g., '풀스택 개발자')")
    description: str = Field(..., description="Role description and responsibilities")
    specialties: list[str] = Field(..., description="Areas of expertise")
    required_tools: list[str] = Field(default_factory=list, description="Tools this agent needs")
    limitations: list[str] = Field(default_factory=list, description="What this agent cannot do")
    reason: str = Field(..., description="Why this agent is needed for the goal")


class HRAnalysis(BaseModel):
    """HR's analysis of required agents."""
    analysis: str = Field(..., description="Analysis of the goal and required expertise")
    proposed_agents: list[AgentProposal] = Field(..., description="Agents to create")
    missing_information: list[str] = Field(
        default_factory=list,
        description="Information needed from CEO to better define agents"
    )


class HRAgent(BaseAgent):
    """
    HR Agent - Responsible for analyzing goals and creating appropriate agents.

    The HR agent:
    1. Analyzes CEO's goals and KPIs
    2. Determines what expertise is needed
    3. Proposes and creates expert agents dynamically
    4. Manages agent lifecycle
    """

    def __init__(self, model: Optional[str] = None):
        super().__init__(
            agent_id="hr-agent",
            role_name="HR Manager",
            model=model
        )

    def get_system_prompt(self) -> str:
        return """당신은 AI 회사의 HR(인사) 매니저입니다.

## 역할
- CEO의 목표와 KPI를 분석하여 필요한 전문가 에이전트를 파악합니다
- 각 목표 달성에 필요한 역할과 전문성을 정의합니다
- 적절한 에이전트를 제안하고 생성합니다

## 에이전트 생성 원칙
1. **최소 필요 원칙**: 목표 달성에 필수적인 역할만 생성
2. **명확한 역할 정의**: 각 에이전트의 책임과 한계를 명확히
3. **전문성 기반**: 각 에이전트는 특정 분야의 전문가여야 함
4. **도구 매핑**: 필요한 외부 도구/API를 명확히 정의

## 출력 형식
분석 결과와 제안하는 에이전트 목록을 구조화된 형태로 제공합니다.

## 중요
- 실제로 작업을 수행할 수 있는 에이전트만 제안하세요
- 추상적인 역할이 아닌 구체적인 전문가를 정의하세요
- 필요한 도구가 연결되지 않으면 RM에게 알려야 합니다"""

    async def process(self, state: CompanyState) -> dict[str, Any]:
        """
        Process state and determine agent needs.

        Returns state updates with new agents or interrupt requests.
        """
        updates: dict[str, Any] = {}

        # Check if we have a CEO request to analyze
        if not state.ceo_request:
            return {"error": "No CEO request to analyze"}

        # Check if agents already exist (avoid re-creation)
        if state.agents and len(state.agents) > 1:  # More than just HR
            return {}

        # Analyze goal and propose agents
        analysis = await self._analyze_goal(state)

        # If missing information, create interrupt
        if analysis.missing_information:
            interrupt = HumanInterrupt(
                interrupt_type=InterruptType.INFO_REQUEST,
                from_agent=self.agent_id,
                message="에이전트 구성을 위해 추가 정보가 필요합니다.",
                required_inputs=[
                    {
                        "key": f"hr_info_{i}",
                        "label": info,
                        "type": "string",
                        "description": info
                    }
                    for i, info in enumerate(analysis.missing_information)
                ],
                context={"analysis": analysis.analysis}
            )
            updates["pending_interrupts"] = state.pending_interrupts + [interrupt]
            return updates

        # Create proposed agents
        new_agents = {}
        for proposal in analysis.proposed_agents:
            agent_def = self._create_agent_definition(proposal)
            new_agents[agent_def.agent_id] = agent_def

        updates["agents"] = {**state.agents, **new_agents}
        updates["current_phase"] = "agents_created"

        return updates

    async def _analyze_goal(self, state: CompanyState) -> HRAnalysis:
        """Analyze CEO's goal and determine required agents."""
        ceo_request = state.ceo_request

        prompt = f"""CEO의 목표를 분석하고 필요한 전문가 에이전트를 제안해주세요.

## CEO 요청
**목표**: {ceo_request.goal}
**KPIs**: {', '.join(ceo_request.kpis) if ceo_request.kpis else '정의되지 않음'}
**제약조건**: {', '.join(ceo_request.constraints) if ceo_request.constraints else '없음'}
**추가 컨텍스트**: {ceo_request.context or '없음'}
**예산**: {ceo_request.budget or '정의되지 않음'}
**타임라인**: {ceo_request.timeline or '정의되지 않음'}

## 분석 요청
1. 이 목표를 달성하기 위해 어떤 전문성이 필요한지 분석하세요
2. 각 전문성에 맞는 에이전트를 제안하세요
3. 각 에이전트가 사용해야 할 도구를 명시하세요
4. 추가로 필요한 정보가 있다면 나열하세요

구체적이고 실행 가능한 에이전트를 제안해주세요."""

        return await self.invoke_llm_with_structured_output(
            prompt=prompt,
            output_schema=HRAnalysis
        )

    def _create_agent_definition(self, proposal: AgentProposal) -> AgentDefinition:
        """Create an AgentDefinition from a proposal."""
        agent_id = f"expert-{uuid.uuid4().hex[:8]}"

        return AgentDefinition(
            agent_id=agent_id,
            role=AgentRole.EXPERT,
            role_name=proposal.role_name,
            description=proposal.description,
            specialties=proposal.specialties,
            tools=proposal.required_tools,
            limitations=proposal.limitations,
            status=AgentStatus.ACTIVE,
            created_by=self.agent_id
        )

    async def handle_agent_request(
        self,
        request: Any,  # AgentRequest
        state: CompanyState
    ) -> AgentDefinition:
        """Handle a request for a new agent from RM."""
        prompt = f"""RM으로부터 새로운 에이전트 생성 요청을 받았습니다.

## 요청 내용
**역할**: {request.role_name}
**이유**: {request.reason}
**필요 전문성**: {', '.join(request.required_specialties)}
**필요 도구**: {', '.join(request.required_tools)}
**추가 컨텍스트**: {request.context or '없음'}

## 현재 에이전트 현황
{self._format_existing_agents(state)}

이 요청에 맞는 에이전트 정의를 생성해주세요."""

        proposal = await self.invoke_llm_with_structured_output(
            prompt=prompt,
            output_schema=AgentProposal
        )

        return self._create_agent_definition(proposal)

    def _format_existing_agents(self, state: CompanyState) -> str:
        """Format existing agents for context."""
        if not state.agents:
            return "현재 생성된 에이전트 없음"

        lines = []
        for agent in state.agents.values():
            lines.append(f"- {agent.role_name}: {agent.description[:100]}...")
        return "\n".join(lines)
