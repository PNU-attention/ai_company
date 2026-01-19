"""Node functions for the company graph."""

from typing import Any

from src.agents.hr import HRAgent
from src.agents.rm import RMAgent
from src.agents.expert_factory import ExpertFactory
from src.context.state import CompanyState, HumanInterrupt, InterruptType
from src.schemas.agent import AgentStatus
from src.schemas.task import TaskStatus


class NodeFunctions:
    """Collection of node functions for the LangGraph."""

    def __init__(self):
        self.hr_agent = HRAgent()
        self.rm_agent = RMAgent()

    async def initialize_node(self, state: CompanyState) -> dict[str, Any]:
        """
        Initialize the company graph.
        Check for CEO request and set initial state.
        """
        if not state.ceo_request:
            return {
                "error": "CEO 요청이 없습니다. 목표를 입력해주세요.",
                "should_continue": False
            }

        return {
            "current_phase": "hr_analysis",
            "updated_at": state.updated_at
        }

    async def hr_node(self, state: CompanyState) -> dict[str, Any]:
        """
        HR Agent node - analyzes goals and creates agents.
        """
        updates = await self.hr_agent.process(state)

        # Handle agent requests from RM
        if state.agent_requests:
            new_agents = dict(state.agents)
            for request in state.agent_requests:
                agent_def = await self.hr_agent.handle_agent_request(request, state)
                new_agents[agent_def.agent_id] = agent_def
            updates["agents"] = new_agents
            updates["agent_requests"] = []  # Clear processed requests

        return updates

    async def rm_node(self, state: CompanyState) -> dict[str, Any]:
        """
        RM Agent node - creates projects and manages execution.
        """
        return await self.rm_agent.process(state)

    async def executor_node(self, state: CompanyState) -> dict[str, Any]:
        """
        Executor node - dispatches tasks to appropriate expert agents.
        """
        updates: dict[str, Any] = {}

        if not state.pending_tasks:
            return updates

        # Get next task to execute
        task_id = state.pending_tasks[0]
        task = state.tasks.get(task_id)

        if not task:
            updates["pending_tasks"] = state.pending_tasks[1:]
            return updates

        # Find assigned agent
        if not task.assigned_to:
            # Try to assign
            task.assigned_to = self._find_agent_for_task(task, state)
            if not task.assigned_to:
                # No suitable agent, create interrupt
                interrupt = HumanInterrupt(
                    interrupt_type=InterruptType.ERROR_REPORT,
                    from_agent="executor",
                    message=f"'{task.name}' 태스크를 실행할 적합한 에이전트가 없습니다.",
                    context={"task_id": task_id, "task_name": task.name}
                )
                updates["pending_interrupts"] = state.pending_interrupts + [interrupt]
                return updates

        # Get or create expert agent
        agent_def = state.agents.get(task.assigned_to)
        if not agent_def:
            return {"error": f"Agent {task.assigned_to} not found"}

        expert = ExpertFactory.create_expert(agent_def)

        # Mark task as executing
        updated_tasks = dict(state.tasks)
        task.status = TaskStatus.EXECUTING
        updated_tasks[task_id] = task

        executing = list(state.executing_tasks)
        executing.append(task_id)
        pending = [t for t in state.pending_tasks if t != task_id]

        updates["tasks"] = updated_tasks
        updates["executing_tasks"] = executing
        updates["pending_tasks"] = pending

        # Execute task
        result, interrupt = await expert.execute_task(task, state)

        # Handle result
        task_results = dict(state.task_results)
        task_results[task_id] = result
        updates["task_results"] = task_results

        # Update task status
        updated_tasks[task_id].status = result.status
        updates["tasks"] = updated_tasks

        # Remove from executing
        updates["executing_tasks"] = [t for t in executing if t != task_id]

        # Handle interrupt if any
        if interrupt:
            updates["pending_interrupts"] = state.pending_interrupts + [interrupt]

        return updates

    async def human_input_node(self, state: CompanyState) -> dict[str, Any]:
        """
        Human input node - processes CEO responses.

        This node is called after interrupt_before triggers and CEO provides input.
        """
        updates: dict[str, Any] = {}

        # Process human responses
        if state.human_responses:
            collected = dict(state.collected_inputs)

            for response in state.human_responses:
                # Merge inputs
                collected.update(response.inputs)

            updates["collected_inputs"] = collected

            # Clear pending interrupts that have been responded to
            responded_ids = {r.interrupt_id for r in state.human_responses}
            remaining_interrupts = [
                i for i in state.pending_interrupts
                if str(i.created_at) not in responded_ids
            ]
            updates["pending_interrupts"] = remaining_interrupts

        return updates

    async def completion_node(self, state: CompanyState) -> dict[str, Any]:
        """
        Completion node - finalizes execution and generates report.
        """
        # Generate completion report
        completed_tasks = [
            t for t in state.tasks.values()
            if t.status == TaskStatus.COMPLETED
        ]
        failed_tasks = [
            t for t in state.tasks.values()
            if t.status == TaskStatus.FAILED
        ]

        report = {
            "total_projects": len(state.projects),
            "total_tasks": len(state.tasks),
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "agents_used": len(state.agents),
            "task_results": {
                tid: result.output
                for tid, result in state.task_results.items()
                if result.output
            }
        }

        return {
            "current_phase": "completed",
            "should_continue": False,
            "messages": state.messages + [
                {"role": "system", "content": f"실행 완료. 결과: {report}"}
            ]
        }

    def _find_agent_for_task(self, task: Any, state: CompanyState) -> str | None:
        """Find suitable agent for a task."""
        for agent in state.agents.values():
            if agent.status != AgentStatus.ACTIVE:
                continue
            if agent.agent_id in ["hr-agent", "rm-agent"]:
                continue

            # Check if agent's specialties match task requirements
            task_keywords = task.name.lower() + " " + task.description.lower()
            for specialty in agent.specialties:
                if specialty.lower() in task_keywords:
                    return agent.agent_id

            # Check tool overlap
            task_tools = {t.tool_id for t in task.tools}
            agent_tools = set(agent.tools)
            if task_tools & agent_tools:
                return agent.agent_id

        # Return first available expert as fallback
        for agent in state.agents.values():
            if agent.agent_id not in ["hr-agent", "rm-agent"]:
                return agent.agent_id

        return None
