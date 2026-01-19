"""RM (Resource Manager) Agent for AI Company."""

import uuid
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.agents.base import BaseAgent
from src.context.state import CompanyState, HumanInterrupt, InterruptType
from src.schemas.agent import AgentRequest
from src.schemas.project import ExecutionGraph, Project, ProjectStatus
from src.schemas.task import (
    ApprovalPoint,
    ExecutionStep,
    RequiredInput,
    Task,
    TaskStatus,
    TaskType,
    ToolRequirement,
)


class TaskProposal(BaseModel):
    """Proposed task within a project."""
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Detailed task description")
    type: str = Field(..., description="ACTION, DOCUMENT, RESEARCH, or APPROVAL")
    priority: str = Field(default="medium", description="high, medium, low")
    assigned_role: str = Field(..., description="Role name to assign this task to")
    dependencies: list[str] = Field(default_factory=list, description="Names of dependent tasks")
    required_inputs: list[dict[str, str]] = Field(
        default_factory=list,
        description="Inputs needed: [{key, label, type, description, source}]"
    )
    required_tools: list[dict[str, str]] = Field(
        default_factory=list,
        description="Tools needed: [{tool_id, name, type}]"
    )
    approval_points: list[dict[str, str]] = Field(
        default_factory=list,
        description="Approval needed: [{point, description, approval_type}]"
    )
    execution_steps: list[dict[str, str]] = Field(
        default_factory=list,
        description="Steps: [{step, action, description, tool}]"
    )


class ProjectProposal(BaseModel):
    """Proposed project to achieve a goal."""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    priority: str = Field(default="medium")
    deliverables: list[str] = Field(..., description="Expected deliverables")
    tasks: list[TaskProposal] = Field(..., description="Tasks in this project")


class RMAnalysis(BaseModel):
    """RM's analysis and project plan."""
    analysis: str = Field(..., description="Analysis of how to achieve the goal")
    projects: list[ProjectProposal] = Field(..., description="Projects to create")
    missing_expertise: list[str] = Field(
        default_factory=list,
        description="Expertise not available in current agents"
    )
    required_tools: list[str] = Field(
        default_factory=list,
        description="External tools/connections needed"
    )


class RMAgent(BaseAgent):
    """
    RM (Resource Manager) Agent - The supervisor of the company.

    The RM agent:
    1. Analyzes CEO goals and breaks them into projects
    2. Creates actionable tasks with proper schemas
    3. Assigns tasks to appropriate expert agents
    4. Monitors execution and handles escalations
    5. Requests new agents from HR when needed
    """

    def __init__(self, model: Optional[str] = None):
        super().__init__(
            agent_id="rm-agent",
            role_name="Resource Manager",
            model=model
        )

    def get_system_prompt(self) -> str:
        return """당신은 AI 회사의 RM(Resource Manager)입니다. 회사의 두뇌 역할을 합니다.

## 역할
- CEO의 목표를 실행 가능한 프로젝트와 태스크로 분해
- 각 태스크에 적합한 전문가 에이전트 배정
- 작업 진행 상황 모니터링 및 조율
- 문제 발생 시 에스컬레이션 처리

## 태스크 생성 원칙
1. **실행 가능성**: 각 태스크는 구체적이고 실행 가능해야 함
2. **필수 입력 정의**: CEO로부터 받아야 할 정보를 명확히 정의
3. **도구 명시**: 필요한 외부 도구/API를 명확히 지정
4. **승인 포인트**: 중요 결정에 대한 CEO 승인 포인트 정의
5. **실행 단계**: 구체적인 실행 단계 정의

## 태스크 타입
- ACTION: 외부 시스템에 실제 변경을 가하는 작업 (계정 생성, 결제 등)
- DOCUMENT: 문서/보고서 작성 작업
- RESEARCH: 정보 수집 및 분석 작업
- APPROVAL: CEO 승인이 필요한 의사결정

## 중요
- 추상적인 태스크가 아닌 구체적인 액션을 정의하세요
- 필요한 입력이 없으면 실행할 수 없습니다 - 반드시 정의하세요
- 도구가 연결되지 않으면 CEO에게 연결을 요청해야 합니다"""

    async def process(self, state: CompanyState) -> dict[str, Any]:
        """
        Process state and create/manage projects and tasks.
        """
        updates: dict[str, Any] = {}

        if not state.ceo_request:
            return {"error": "No CEO request available"}

        # Check if we have agents to work with
        if len(state.agents) < 2:  # Need more than just HR/RM
            return {}  # Wait for HR to create agents

        # Check if projects already exist
        if state.projects:
            # Handle ongoing execution
            return await self._manage_execution(state)

        # Create initial project plan
        analysis = await self._analyze_and_plan(state)

        # Check for missing expertise
        if analysis.missing_expertise:
            agent_requests = [
                AgentRequest(
                    requested_by=self.agent_id,
                    role_name=expertise,
                    reason=f"목표 달성을 위해 {expertise} 전문가가 필요합니다",
                    required_specialties=[expertise],
                )
                for expertise in analysis.missing_expertise
            ]
            updates["agent_requests"] = state.agent_requests + agent_requests

        # Check for required tools not connected
        missing_tools = self._check_missing_tools(analysis.required_tools, state)
        if missing_tools:
            interrupt = HumanInterrupt(
                interrupt_type=InterruptType.TOOL_CONNECTION,
                from_agent=self.agent_id,
                message="프로젝트 실행을 위해 다음 도구/서비스 연결이 필요합니다.",
                required_inputs=[
                    {
                        "key": f"tool_{tool}",
                        "label": f"{tool} 연결",
                        "type": "connection",
                        "description": f"{tool} 서비스를 연결해주세요"
                    }
                    for tool in missing_tools
                ],
                context={"required_tools": missing_tools}
            )
            updates["pending_interrupts"] = state.pending_interrupts + [interrupt]

        # Create projects and tasks
        new_projects, new_tasks, pending_tasks = await self._create_projects_and_tasks(
            analysis, state
        )

        updates["projects"] = {**state.projects, **new_projects}
        updates["tasks"] = {**state.tasks, **new_tasks}
        updates["pending_tasks"] = state.pending_tasks + pending_tasks
        updates["current_phase"] = "planning_complete"

        return updates

    async def _analyze_and_plan(self, state: CompanyState) -> RMAnalysis:
        """Analyze goal and create project plan."""
        ceo_request = state.ceo_request
        agents_info = self._format_available_agents(state)

        prompt = f"""CEO의 목표를 분석하고 실행 계획을 수립해주세요.

## CEO 요청
**목표**: {ceo_request.goal}
**KPIs**: {', '.join(ceo_request.kpis) if ceo_request.kpis else '정의되지 않음'}
**제약조건**: {', '.join(ceo_request.constraints) if ceo_request.constraints else '없음'}
**추가 컨텍스트**: {ceo_request.context or '없음'}
**예산**: {ceo_request.budget or '정의되지 않음'}
**타임라인**: {ceo_request.timeline or '정의되지 않음'}

## 사용 가능한 에이전트
{agents_info}

## 분석 및 계획 요청
1. 목표 달성을 위한 프로젝트들을 정의하세요
2. 각 프로젝트 내에 구체적인 태스크들을 정의하세요
3. 각 태스크에는 반드시 다음을 포함하세요:
   - required_inputs: CEO로부터 필요한 정보 (예: 사업자번호, 계정정보 등)
   - required_tools: 필요한 외부 도구/API
   - approval_points: CEO 승인이 필요한 시점
   - execution_steps: 구체적인 실행 단계

## 중요
- 실제로 실행 가능한 태스크만 정의하세요
- "문서 작성" 같은 추상적 태스크가 아닌 "셀러 계정 생성" 같은 구체적 액션을 정의하세요
- CEO에게 요청해야 할 정보를 빠짐없이 정의하세요"""

        return await self.invoke_llm_with_structured_output(
            prompt=prompt,
            output_schema=RMAnalysis
        )

    async def _create_projects_and_tasks(
        self,
        analysis: RMAnalysis,
        state: CompanyState
    ) -> tuple[dict[str, Project], dict[str, Task], list[str]]:
        """Create Project and Task objects from analysis."""
        projects = {}
        tasks = {}
        pending_task_ids = []
        task_name_to_id = {}  # For dependency resolution

        for proj_proposal in analysis.projects:
            project_id = f"proj-{uuid.uuid4().hex[:8]}"

            task_ids = []
            for task_proposal in proj_proposal.tasks:
                task_id = f"task-{uuid.uuid4().hex[:8]}"
                task_name_to_id[task_proposal.name] = task_id
                task_ids.append(task_id)

                # Convert task proposal to Task schema
                task = self._create_task_from_proposal(
                    task_id=task_id,
                    project_id=project_id,
                    proposal=task_proposal,
                    state=state,
                    task_name_to_id=task_name_to_id
                )
                tasks[task_id] = task

                # Add to pending if no dependencies
                if not task.dependencies:
                    pending_task_ids.append(task_id)

            project = Project(
                project_id=project_id,
                name=proj_proposal.name,
                description=proj_proposal.description,
                goal_description=state.ceo_request.goal,
                priority=proj_proposal.priority,
                deliverables=proj_proposal.deliverables,
                task_ids=task_ids,
                status=ProjectStatus.PENDING,
                created_by=self.agent_id
            )
            projects[project_id] = project

        return projects, tasks, pending_task_ids

    def _create_task_from_proposal(
        self,
        task_id: str,
        project_id: str,
        proposal: TaskProposal,
        state: CompanyState,
        task_name_to_id: dict[str, str]
    ) -> Task:
        """Create a Task from a TaskProposal."""
        # Convert required inputs
        required_inputs = [
            RequiredInput(
                key=inp.get("key", f"input_{i}"),
                label=inp.get("label", ""),
                type=inp.get("type", "string"),
                source=inp.get("source", "ceo_input"),
                description=inp.get("description"),
                required=inp.get("required", True)
            )
            for i, inp in enumerate(proposal.required_inputs)
        ]

        # Convert tools
        tools = [
            ToolRequirement(
                tool_id=tool.get("tool_id", tool.get("name", "")),
                name=tool.get("name", ""),
                type=tool.get("type", "mcp"),
                status=self._get_tool_status(tool.get("tool_id", ""), state)
            )
            for tool in proposal.required_tools
        ]

        # Convert approval points
        approval_points = [
            ApprovalPoint(
                point=ap.get("point", f"approval_{i}"),
                description=ap.get("description", ""),
                approval_type=ap.get("approval_type", "explicit")
            )
            for i, ap in enumerate(proposal.approval_points)
        ]

        # Convert execution steps
        execution_steps = [
            ExecutionStep(
                step=int(step.get("step", i + 1)),
                action=step.get("action", ""),
                description=step.get("description", ""),
                tool=step.get("tool"),
                approval_point=step.get("approval_point")
            )
            for i, step in enumerate(proposal.execution_steps)
        ]

        # Resolve dependencies
        dependencies = [
            task_name_to_id[dep_name]
            for dep_name in proposal.dependencies
            if dep_name in task_name_to_id
        ]

        # Find assigned agent
        assigned_agent = self._find_agent_for_role(proposal.assigned_role, state)

        return Task(
            task_id=task_id,
            project_id=project_id,
            name=proposal.name,
            description=proposal.description,
            type=TaskType(proposal.type),
            priority=proposal.priority,
            required_inputs=required_inputs,
            tools=tools,
            approval_points=approval_points,
            execution_steps=execution_steps,
            assigned_to=assigned_agent,
            dependencies=dependencies,
            status=TaskStatus.PENDING
        )

    def _get_tool_status(self, tool_id: str, state: CompanyState) -> str:
        """Get connection status of a tool."""
        if tool_id in state.connected_tools:
            return state.connected_tools[tool_id].get("status", "unknown")
        return "not_connected"

    def _find_agent_for_role(self, role_name: str, state: CompanyState) -> Optional[str]:
        """Find an agent that can handle the given role."""
        for agent in state.agents.values():
            if role_name.lower() in agent.role_name.lower():
                return agent.agent_id
            for specialty in agent.specialties:
                if role_name.lower() in specialty.lower():
                    return agent.agent_id
        return None

    def _format_available_agents(self, state: CompanyState) -> str:
        """Format available agents for prompt."""
        if not state.agents:
            return "사용 가능한 에이전트 없음"

        lines = []
        for agent in state.agents.values():
            if agent.agent_id in ["hr-agent", "rm-agent"]:
                continue
            specialties = ", ".join(agent.specialties) if agent.specialties else "일반"
            tools = ", ".join(agent.tools) if agent.tools else "없음"
            lines.append(
                f"- **{agent.role_name}** ({agent.agent_id})\n"
                f"  전문분야: {specialties}\n"
                f"  도구: {tools}"
            )
        return "\n".join(lines) if lines else "전문가 에이전트 없음"

    def _check_missing_tools(
        self,
        required_tools: list[str],
        state: CompanyState
    ) -> list[str]:
        """Check which required tools are not connected."""
        return [
            tool for tool in required_tools
            if tool not in state.connected_tools
            or state.connected_tools[tool].get("status") != "connected"
        ]

    async def _manage_execution(self, state: CompanyState) -> dict[str, Any]:
        """Manage ongoing execution of tasks."""
        updates: dict[str, Any] = {}

        # Handle escalations
        if state.escalations:
            await self._handle_escalations(state, updates)

        # Check for completed tasks and update dependencies
        self._update_task_dependencies(state, updates)

        # Check if all projects are complete
        if self._all_projects_complete(state):
            updates["current_phase"] = "completed"
            updates["should_continue"] = False

        return updates

    async def _handle_escalations(
        self,
        state: CompanyState,
        updates: dict[str, Any]
    ) -> None:
        """Handle escalation requests from experts."""
        for escalation in state.escalations:
            if escalation.escalation_type == "expertise_exceeded":
                # Request new agent from HR
                agent_request = AgentRequest(
                    requested_by=self.agent_id,
                    role_name=escalation.required_expertise or "전문가",
                    reason=escalation.reason,
                    context=str(escalation.context)
                )
                if "agent_requests" not in updates:
                    updates["agent_requests"] = list(state.agent_requests)
                updates["agent_requests"].append(agent_request)

    def _update_task_dependencies(
        self,
        state: CompanyState,
        updates: dict[str, Any]
    ) -> None:
        """Update pending tasks based on completed dependencies."""
        new_pending = list(state.pending_tasks)

        for task in state.tasks.values():
            if task.task_id in state.pending_tasks:
                continue
            if task.status != TaskStatus.PENDING:
                continue

            # Check if all dependencies are complete
            deps_complete = all(
                dep_id in state.task_results
                and state.task_results[dep_id].status == TaskStatus.COMPLETED
                for dep_id in task.dependencies
            )

            if deps_complete and task.task_id not in new_pending:
                new_pending.append(task.task_id)

        if new_pending != state.pending_tasks:
            updates["pending_tasks"] = new_pending

    def _all_projects_complete(self, state: CompanyState) -> bool:
        """Check if all projects are complete."""
        for project in state.projects.values():
            if project.status != ProjectStatus.COMPLETED:
                return False
        return True
