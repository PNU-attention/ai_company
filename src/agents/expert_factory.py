"""Expert Agent Factory for dynamic agent creation."""

from typing import Any, Callable, Optional

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from src.config import get_settings
from src.context.state import CompanyState, HumanInterrupt, InterruptType
from src.schemas.agent import AgentDefinition, EscalationRequest
from src.schemas.task import Task, TaskResult, TaskStatus


class ExpertAgent:
    """
    Dynamically created expert agent.

    Each expert agent is created based on an AgentDefinition and can:
    1. Execute assigned tasks
    2. Use available tools
    3. Request information from CEO
    4. Escalate when expertise is exceeded
    """

    def __init__(
        self,
        definition: AgentDefinition,
        tools: list[Any] = None,
        model: Optional[str] = None
    ):
        self.definition = definition
        self.tools = tools or []
        settings = get_settings()
        self.model_name = model or settings.default_model

        self.llm = ChatAnthropic(
            model=self.model_name,
            api_key=settings.anthropic_api_key,
            max_tokens=4096,
        )

        # Create ReAct agent if tools are available
        if self.tools:
            self.react_agent = create_react_agent(
                model=self.llm,
                tools=self.tools,
                state_modifier=self.definition.to_system_prompt()
            )
        else:
            self.react_agent = None

    @property
    def agent_id(self) -> str:
        return self.definition.agent_id

    @property
    def role_name(self) -> str:
        return self.definition.role_name

    async def execute_task(
        self,
        task: Task,
        state: CompanyState
    ) -> tuple[TaskResult, Optional[HumanInterrupt]]:
        """
        Execute a task and return the result.

        Returns:
            Tuple of (TaskResult, Optional[HumanInterrupt])
            If interrupt is returned, execution should pause for human input.
        """
        # Check for missing inputs
        missing_inputs = task.has_missing_inputs(state.collected_inputs)
        if missing_inputs:
            interrupt = self._create_input_request(task, missing_inputs)
            return (
                TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.INPUT_REQUIRED,
                    interrupt=True,
                    request={"missing_inputs": [inp.key for inp in missing_inputs]}
                ),
                interrupt
            )

        # Check for approval requirement
        if task.has_approval_before_execution():
            if not self._has_approval(task.task_id, state):
                interrupt = self._create_approval_request(task)
                return (
                    TaskResult(
                        task_id=task.task_id,
                        status=TaskStatus.APPROVAL_WAIT,
                        interrupt=True,
                        request={"approval_point": "before_execution"}
                    ),
                    interrupt
                )

        # Check tool availability
        missing_tools = self._check_tool_availability(task, state)
        if missing_tools:
            interrupt = self._create_tool_request(task, missing_tools)
            return (
                TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.AWAITING_TOOL,
                    interrupt=True,
                    request={"missing_tools": missing_tools}
                ),
                interrupt
            )

        # Execute the task
        try:
            result = await self._execute_task_steps(task, state)
            return result, None
        except ExpertiseExceededException as e:
            # Create escalation
            escalation = EscalationRequest(
                task_id=task.task_id,
                from_agent=self.agent_id,
                reason=str(e),
                escalation_type="expertise_exceeded",
                required_expertise=e.required_expertise,
                suggestion=e.suggestion
            )
            return (
                TaskResult(
                    task_id=task.task_id,
                    status=TaskStatus.FAILED,
                    error=str(e),
                    output={"escalation": escalation.model_dump()}
                ),
                None
            )

    async def _execute_task_steps(
        self,
        task: Task,
        state: CompanyState
    ) -> TaskResult:
        """Execute task steps."""
        outputs = {}
        collected_inputs = state.collected_inputs

        for step in task.execution_steps:
            # Check for step-level approval
            if step.approval_point:
                # This would need to interrupt and wait for approval
                pass

            if step.tool and self.react_agent:
                # Use ReAct agent for tool-based steps
                step_result = await self._execute_with_react(step, task, collected_inputs)
                outputs[f"step_{step.step}"] = step_result
            else:
                # Use direct LLM for reasoning steps
                step_result = await self._execute_reasoning_step(step, task, collected_inputs)
                outputs[f"step_{step.step}"] = step_result

        return TaskResult(
            task_id=task.task_id,
            status=TaskStatus.COMPLETED,
            output=outputs
        )

    async def _execute_with_react(
        self,
        step: Any,
        task: Task,
        inputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a step using ReAct agent."""
        prompt = f"""## 태스크
{task.name}: {task.description}

## 현재 단계
단계 {step.step}: {step.description}

## 사용 가능한 입력
{self._format_inputs(inputs)}

## 지시사항
위 단계를 실행하고 결과를 보고해주세요.
필요한 도구를 사용하여 실제 액션을 수행하세요."""

        if self.react_agent:
            result = await self.react_agent.ainvoke({
                "messages": [HumanMessage(content=prompt)]
            })
            return {"messages": result.get("messages", []), "step": step.step}

        return {"error": "No ReAct agent available", "step": step.step}

    async def _execute_reasoning_step(
        self,
        step: Any,
        task: Task,
        inputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a reasoning step without tools."""
        prompt = f"""## 태스크
{task.name}: {task.description}

## 현재 단계
단계 {step.step}: {step.description}

## 입력 데이터
{self._format_inputs(inputs)}

## 지시사항
위 단계를 분석하고 결과를 제공해주세요."""

        messages = [
            SystemMessage(content=self.definition.to_system_prompt()),
            HumanMessage(content=prompt)
        ]

        response = await self.llm.ainvoke(messages)
        return {"response": response.content, "step": step.step}

    def _create_input_request(
        self,
        task: Task,
        missing_inputs: list[Any]
    ) -> HumanInterrupt:
        """Create interrupt for missing inputs."""
        return HumanInterrupt(
            interrupt_type=InterruptType.INFO_REQUEST,
            from_agent=self.agent_id,
            message=f"'{task.name}' 실행을 위해 다음 정보가 필요합니다.",
            required_inputs=[
                {
                    "key": inp.key,
                    "label": inp.label,
                    "type": inp.type,
                    "description": inp.description or inp.label,
                    "example": inp.example
                }
                for inp in missing_inputs
            ],
            task_id=task.task_id,
            project_id=task.project_id
        )

    def _create_approval_request(self, task: Task) -> HumanInterrupt:
        """Create interrupt for approval."""
        approval_points = [ap for ap in task.approval_points if ap.approval_type == "explicit"]

        return HumanInterrupt(
            interrupt_type=InterruptType.APPROVAL_REQUEST,
            from_agent=self.agent_id,
            message=f"'{task.name}' 실행 전 승인이 필요합니다.",
            required_inputs=[],
            options=["승인", "거부", "수정 요청"],
            context={
                "task_description": task.description,
                "approval_points": [ap.description for ap in approval_points],
                "execution_steps": [
                    {"step": s.step, "description": s.description}
                    for s in task.execution_steps
                ]
            },
            task_id=task.task_id,
            project_id=task.project_id
        )

    def _create_tool_request(
        self,
        task: Task,
        missing_tools: list[str]
    ) -> HumanInterrupt:
        """Create interrupt for missing tools."""
        return HumanInterrupt(
            interrupt_type=InterruptType.TOOL_CONNECTION,
            from_agent=self.agent_id,
            message=f"'{task.name}' 실행을 위해 다음 도구 연결이 필요합니다.",
            required_inputs=[
                {
                    "key": f"tool_{tool}",
                    "label": f"{tool} 연결",
                    "type": "connection",
                    "description": f"{tool} 서비스를 연결해주세요"
                }
                for tool in missing_tools
            ],
            task_id=task.task_id,
            project_id=task.project_id
        )

    def _check_tool_availability(
        self,
        task: Task,
        state: CompanyState
    ) -> list[str]:
        """Check which required tools are not available."""
        missing = []
        for tool_req in task.tools:
            if not tool_req.required:
                continue
            if tool_req.tool_id not in state.connected_tools:
                missing.append(tool_req.tool_id)
            elif state.connected_tools[tool_req.tool_id].get("status") != "connected":
                missing.append(tool_req.tool_id)
        return missing

    def _has_approval(self, task_id: str, state: CompanyState) -> bool:
        """Check if task has been approved."""
        for response in state.human_responses:
            if response.approved and task_id in str(response.interrupt_id):
                return True
        return False

    def _format_inputs(self, inputs: dict[str, Any]) -> str:
        """Format inputs for prompt."""
        if not inputs:
            return "입력 없음"
        lines = [f"- {k}: {v}" for k, v in inputs.items()]
        return "\n".join(lines)


class ExpertiseExceededException(Exception):
    """Exception when task exceeds expert's capabilities."""

    def __init__(
        self,
        message: str,
        required_expertise: Optional[str] = None,
        suggestion: Optional[str] = None
    ):
        super().__init__(message)
        self.required_expertise = required_expertise
        self.suggestion = suggestion


class ExpertFactory:
    """Factory for creating expert agents dynamically."""

    _instances: dict[str, ExpertAgent] = {}
    _tool_registry: dict[str, Callable] = {}

    @classmethod
    def register_tool(cls, tool_id: str, tool: Callable) -> None:
        """Register a tool that can be used by experts."""
        cls._tool_registry[tool_id] = tool

    @classmethod
    def create_expert(
        cls,
        definition: AgentDefinition,
        model: Optional[str] = None
    ) -> ExpertAgent:
        """
        Create an expert agent from a definition.

        Args:
            definition: AgentDefinition specifying the expert's capabilities
            model: Optional model override

        Returns:
            ExpertAgent instance
        """
        # Check if already created
        if definition.agent_id in cls._instances:
            return cls._instances[definition.agent_id]

        # Get tools for this agent
        tools = []
        for tool_id in definition.tools:
            if tool_id in cls._tool_registry:
                tools.append(cls._tool_registry[tool_id])

        # Create agent
        expert = ExpertAgent(
            definition=definition,
            tools=tools,
            model=model
        )

        cls._instances[definition.agent_id] = expert
        return expert

    @classmethod
    def get_expert(cls, agent_id: str) -> Optional[ExpertAgent]:
        """Get an existing expert by ID."""
        return cls._instances.get(agent_id)

    @classmethod
    def get_all_experts(cls) -> list[ExpertAgent]:
        """Get all created experts."""
        return list(cls._instances.values())

    @classmethod
    def clear(cls) -> None:
        """Clear all instances (for testing)."""
        cls._instances.clear()
