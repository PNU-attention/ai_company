"""Tests for state management."""

import pytest
from datetime import datetime


class TestCEORequest:
    """Tests for CEORequest."""

    def test_create_ceo_request(self, ceo_request):
        """Test CEO request creation."""
        assert ceo_request.goal == "쿠팡에 입점하여 월 매출 1000만원 달성"
        assert len(ceo_request.kpis) == 3
        assert ceo_request.budget == "500만원"

    def test_ceo_request_defaults(self):
        """Test CEO request with defaults."""
        from src.context.state import CEORequest

        request = CEORequest(goal="테스트 목표")
        assert request.kpis == []
        assert request.constraints == []
        assert request.context is None


class TestCompanyState:
    """Tests for CompanyState."""

    def test_create_company_state(self, ceo_request):
        """Test company state creation."""
        from src.context.state import CompanyState

        state = CompanyState(ceo_request=ceo_request)
        assert state.ceo_request == ceo_request
        assert state.current_phase == "initialization"
        assert state.should_continue is True

    def test_state_agent_management(self, company_state, sample_agent_definition):
        """Test agent management in state."""
        # Add agent
        company_state.agents[sample_agent_definition.agent_id] = sample_agent_definition

        # Get agent
        agent = company_state.get_agent_by_role("이커머스 전문가")
        assert agent is not None
        assert agent.agent_id == sample_agent_definition.agent_id

    def test_state_task_management(self, company_state, sample_task):
        """Test task management in state."""
        company_state.tasks[sample_task.task_id] = sample_task
        company_state.pending_tasks.append(sample_task.task_id)

        tasks = company_state.get_tasks_for_project("proj-test123")
        assert len(tasks) == 1
        assert tasks[0].task_id == sample_task.task_id


class TestHumanInterrupt:
    """Tests for HumanInterrupt."""

    def test_create_info_request(self):
        """Test creating info request interrupt."""
        from src.context.state import HumanInterrupt, InterruptType

        interrupt = HumanInterrupt(
            interrupt_type=InterruptType.INFO_REQUEST,
            from_agent="rm-agent",
            message="추가 정보가 필요합니다",
            required_inputs=[
                {"key": "email", "label": "이메일", "type": "string"}
            ]
        )

        assert interrupt.interrupt_type == InterruptType.INFO_REQUEST
        assert len(interrupt.required_inputs) == 1

    def test_create_approval_request(self):
        """Test creating approval request interrupt."""
        from src.context.state import HumanInterrupt, InterruptType

        interrupt = HumanInterrupt(
            interrupt_type=InterruptType.APPROVAL_REQUEST,
            from_agent="expert-123",
            message="계정 생성을 승인해주세요",
            options=["승인", "거부", "수정"],
            task_id="task-123"
        )

        assert interrupt.interrupt_type == InterruptType.APPROVAL_REQUEST
        assert "승인" in interrupt.options
        assert interrupt.task_id == "task-123"


class TestHumanResponse:
    """Tests for HumanResponse."""

    def test_create_approval_response(self):
        """Test creating approval response."""
        from src.context.state import HumanResponse

        response = HumanResponse(
            interrupt_id="int-123",
            approved=True,
            message="승인합니다"
        )

        assert response.approved is True
        assert response.interrupt_id == "int-123"

    def test_create_input_response(self):
        """Test creating input response."""
        from src.context.state import HumanResponse

        response = HumanResponse(
            interrupt_id="int-456",
            inputs={"email": "ceo@company.com", "phone": "010-1234-5678"}
        )

        assert response.inputs["email"] == "ceo@company.com"
        assert "phone" in response.inputs
