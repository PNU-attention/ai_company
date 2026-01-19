"""End-to-end integration tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestE2EScenario:
    """End-to-end scenario tests."""

    @pytest.mark.asyncio
    async def test_basic_flow_initialization(self, ceo_request, mock_llm):
        """Test basic flow initialization."""
        from src.context.state import CompanyState
        from src.graph.nodes import NodeFunctions

        nodes = NodeFunctions()
        state = CompanyState(ceo_request=ceo_request)

        # Test initialization
        updates = await nodes.initialize_node(state)

        assert updates["current_phase"] == "hr_analysis"
        assert "error" not in updates

    @pytest.mark.asyncio
    async def test_flow_without_ceo_request(self):
        """Test flow fails without CEO request."""
        from src.context.state import CompanyState
        from src.graph.nodes import NodeFunctions

        nodes = NodeFunctions()
        state = CompanyState()

        updates = await nodes.initialize_node(state)

        assert "error" in updates
        assert updates["should_continue"] is False

    @pytest.mark.asyncio
    async def test_hr_agent_creates_agents(
        self, company_state, mock_llm, mock_hr_analysis
    ):
        """Test HR agent creates appropriate agents."""
        from src.agents.hr import HRAgent

        hr_agent = HRAgent()

        # Mock the structured output
        with patch.object(hr_agent, 'invoke_llm_with_structured_output', new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_hr_analysis

            updates = await hr_agent.process(company_state)

            # Should create agents
            assert "agents" in updates
            assert len(updates["agents"]) >= 2

            # Check agent properties
            agent_names = [a.role_name for a in updates["agents"].values()]
            assert "이커머스 전문가" in agent_names
            assert "마케팅 전문가" in agent_names

    @pytest.mark.asyncio
    async def test_rm_agent_creates_projects(
        self, company_state, sample_agent_definition, mock_llm, mock_rm_analysis
    ):
        """Test RM agent creates projects and tasks."""
        from src.agents.rm import RMAgent

        # Add agents to state
        company_state.agents["expert-test"] = sample_agent_definition

        rm_agent = RMAgent()

        with patch.object(rm_agent, 'invoke_llm_with_structured_output', new_callable=AsyncMock) as mock_invoke:
            mock_invoke.return_value = mock_rm_analysis

            updates = await rm_agent.process(company_state)

            # Should create projects
            assert "projects" in updates
            assert len(updates["projects"]) >= 1

            # Should create tasks
            assert "tasks" in updates

            # Should identify required tools
            if "pending_interrupts" in updates:
                # Should request tool connection
                assert any(
                    i.interrupt_type.value == "tool_connection"
                    for i in updates["pending_interrupts"]
                )

    @pytest.mark.asyncio
    async def test_expert_requests_missing_inputs(
        self, company_state, sample_task, sample_agent_definition
    ):
        """Test expert agent requests missing inputs."""
        from src.agents.expert_factory import ExpertFactory

        # Setup state
        company_state.agents[sample_agent_definition.agent_id] = sample_agent_definition
        company_state.tasks[sample_task.task_id] = sample_task

        # Create expert
        expert = ExpertFactory.create_expert(sample_agent_definition)

        # Execute without inputs
        result, interrupt = await expert.execute_task(sample_task, company_state)

        # Should request inputs
        assert result.status.value == "INPUT_REQUIRED"
        assert interrupt is not None
        assert interrupt.interrupt_type.value == "info_request"
        assert len(interrupt.required_inputs) > 0

    @pytest.mark.asyncio
    async def test_expert_requests_approval(
        self, company_state, sample_task, sample_agent_definition
    ):
        """Test expert agent requests approval."""
        from src.agents.expert_factory import ExpertFactory

        # Provide required inputs
        company_state.collected_inputs = {
            "business_number": "123-45-67890",
            "bank_account": "110-1234-5678"
        }
        company_state.agents[sample_agent_definition.agent_id] = sample_agent_definition
        company_state.tasks[sample_task.task_id] = sample_task

        expert = ExpertFactory.create_expert(sample_agent_definition)

        result, interrupt = await expert.execute_task(sample_task, company_state)

        # Should request approval
        assert result.status.value == "APPROVAL_WAIT"
        assert interrupt is not None
        assert interrupt.interrupt_type.value == "approval_request"


class TestEdgeConditions:
    """Test edge routing conditions."""

    def test_after_initialize_routes_to_hr(self, company_state):
        """Test routing after initialization."""
        from src.graph.edges import EdgeConditions

        company_state.current_phase = "hr_analysis"
        result = EdgeConditions.after_initialize(company_state)

        assert result == "hr"

    def test_after_initialize_routes_to_end_on_error(self, company_state):
        """Test routing to end on error."""
        from src.graph.edges import EdgeConditions

        company_state.error = "Some error occurred"
        result = EdgeConditions.after_initialize(company_state)

        assert result == "end"

    def test_after_hr_routes_to_human_input(self, company_state):
        """Test routing to human input when interrupt pending."""
        from src.graph.edges import EdgeConditions
        from src.context.state import HumanInterrupt, InterruptType

        company_state.pending_interrupts = [
            HumanInterrupt(
                interrupt_type=InterruptType.INFO_REQUEST,
                from_agent="hr-agent",
                message="Need more info"
            )
        ]

        result = EdgeConditions.after_hr(company_state)

        assert result == "human_input"

    def test_after_executor_routes_to_completion(self, company_state, sample_task):
        """Test routing to completion when all tasks done."""
        from src.graph.edges import EdgeConditions
        from src.schemas.task import TaskStatus

        sample_task.status = TaskStatus.COMPLETED
        company_state.tasks[sample_task.task_id] = sample_task

        result = EdgeConditions.after_executor(company_state)

        assert result == "completion"


class TestHumanInterface:
    """Test human interface functionality."""

    def test_interrupt_handler(self):
        """Test interrupt handling."""
        from src.communication.human_interface import InterruptHandler
        from src.context.state import InterruptType

        handler = InterruptHandler()

        # Create interrupt
        interrupt = handler.create_interrupt(
            interrupt_type=InterruptType.INFO_REQUEST,
            from_agent="test-agent",
            message="Need input",
            required_inputs=[
                {"key": "email", "label": "Email", "type": "string", "required": True}
            ]
        )

        # Get pending
        pending = handler.get_pending()
        assert len(pending) == 1

        # Submit response
        interrupt_id = str(interrupt.created_at)
        response = handler.submit_response(
            interrupt_id=interrupt_id,
            inputs={"email": "test@example.com"}
        )

        assert response is not None
        assert response.inputs["email"] == "test@example.com"

        # Pending should be empty
        pending = handler.get_pending()
        assert len(pending) == 0

    def test_human_interface_session(self):
        """Test human interface session management."""
        from src.communication.human_interface import HumanInterface

        interface = HumanInterface()

        # Get session
        session1 = interface.session_id
        assert session1 is not None

        # Start new session
        session2 = interface.start_new_session()
        assert session2 != session1

    def test_conversation_history(self):
        """Test conversation history tracking."""
        from src.communication.human_interface import HumanInterface

        interface = HumanInterface()

        interface.add_to_history("ceo", "목표를 설정합니다")
        interface.add_to_history("system", "목표가 설정되었습니다")

        history = interface.get_history()
        assert len(history) == 2
        assert history[0]["role"] == "ceo"
