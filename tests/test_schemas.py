"""Tests for Pydantic schemas."""

import pytest
from datetime import datetime


class TestTaskSchema:
    """Tests for Task schema."""

    def test_task_creation(self, sample_task):
        """Test task creation."""
        assert sample_task.task_id == "task-test123"
        assert sample_task.type.value == "ACTION"
        assert len(sample_task.required_inputs) == 2

    def test_task_missing_inputs(self, sample_task):
        """Test checking for missing inputs."""
        # No collected inputs
        missing = sample_task.has_missing_inputs({})
        assert len(missing) == 2
        assert missing[0].key == "business_number"

        # Partial inputs
        missing = sample_task.has_missing_inputs({"business_number": "123-45-67890"})
        assert len(missing) == 1
        assert missing[0].key == "bank_account"

        # All inputs provided
        missing = sample_task.has_missing_inputs({
            "business_number": "123-45-67890",
            "bank_account": "110-1234-5678"
        })
        assert len(missing) == 0

    def test_task_approval_check(self, sample_task):
        """Test approval requirement check."""
        assert sample_task.has_approval_before_execution() is True

    def test_task_without_approval(self):
        """Test task without approval points."""
        from src.schemas.task import Task, TaskType

        task = Task(
            task_id="task-no-approval",
            project_id="proj-123",
            name="간단한 작업",
            description="승인 필요 없는 작업",
            type=TaskType.DOCUMENT
        )

        assert task.has_approval_before_execution() is False


class TestAgentSchema:
    """Tests for Agent schema."""

    def test_agent_creation(self, sample_agent_definition):
        """Test agent definition creation."""
        assert sample_agent_definition.role_name == "이커머스 전문가"
        assert "쿠팡 입점" in sample_agent_definition.specialties

    def test_agent_system_prompt_generation(self, sample_agent_definition):
        """Test system prompt generation."""
        prompt = sample_agent_definition.to_system_prompt()

        assert "이커머스 전문가" in prompt
        assert "쿠팡 입점" in prompt
        assert "결제 시스템 개발 불가" in prompt

    def test_agent_custom_system_prompt(self, sample_agent_definition):
        """Test custom system prompt."""
        sample_agent_definition.system_prompt = "커스텀 프롬프트입니다."
        prompt = sample_agent_definition.to_system_prompt()

        assert prompt == "커스텀 프롬프트입니다."


class TestProjectSchema:
    """Tests for Project schema."""

    def test_project_creation(self):
        """Test project creation."""
        from src.schemas.project import Project, ProjectStatus

        project = Project(
            project_id="proj-123",
            name="쿠팡 입점",
            description="쿠팡 마켓플레이스 입점 프로젝트",
            goal_description="월 매출 1000만원 달성",
            deliverables=["셀러 계정", "상품 등록"],
            priority="high"
        )

        assert project.status == ProjectStatus.PENDING
        assert len(project.deliverables) == 2
        assert project.created_by == "rm-agent"


class TestEscalationSchema:
    """Tests for Escalation schema."""

    def test_escalation_creation(self):
        """Test escalation request creation."""
        from src.schemas.agent import EscalationRequest

        escalation = EscalationRequest(
            task_id="task-123",
            from_agent="expert-456",
            reason="이 작업은 제 전문 분야를 벗어납니다",
            escalation_type="expertise_exceeded",
            required_expertise="법률 자문",
            suggestion="법률 전문가 에이전트가 필요합니다"
        )

        assert escalation.escalation_type == "expertise_exceeded"
        assert escalation.required_expertise == "법률 자문"
