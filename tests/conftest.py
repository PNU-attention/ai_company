"""Pytest fixtures for AI Company tests."""

import os
from datetime import datetime
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Set test environment
os.environ["ANTHROPIC_API_KEY"] = "test-api-key"
os.environ["DATABASE_URL"] = "sqlite:///./test_data/test.db"
os.environ["CHROMA_PERSIST_DIR"] = "./test_data/chroma"


@pytest.fixture
def ceo_request():
    """Sample CEO request for testing."""
    from src.context.state import CEORequest

    return CEORequest(
        goal="쿠팡에 입점하여 월 매출 1000만원 달성",
        kpis=["월 매출 1000만원", "리뷰 평점 4.5 이상", "반품률 5% 이하"],
        constraints=["초기 투자 500만원 이내", "1인 운영"],
        context="패션 액세서리 판매 예정, 대학생 타겟",
        budget="500만원",
        timeline="3개월 내"
    )


@pytest.fixture
def company_state(ceo_request):
    """Sample company state for testing."""
    from src.context.state import CompanyState

    return CompanyState(ceo_request=ceo_request)


@pytest.fixture
def sample_agent_definition():
    """Sample agent definition for testing."""
    from src.schemas.agent import AgentDefinition, AgentRole, AgentStatus

    return AgentDefinition(
        agent_id="expert-test123",
        role=AgentRole.EXPERT,
        role_name="이커머스 전문가",
        description="온라인 쇼핑몰 입점 및 운영 전문가",
        specialties=["쿠팡 입점", "상품 등록", "재고 관리"],
        tools=["coupang_api", "inventory_manager"],
        limitations=["결제 시스템 개발 불가", "법률 자문 불가"],
        status=AgentStatus.ACTIVE,
    )


@pytest.fixture
def sample_task():
    """Sample task for testing."""
    from src.schemas.task import (
        Task, TaskType, TaskStatus,
        RequiredInput, ToolRequirement, ApprovalPoint, ExecutionStep
    )

    return Task(
        task_id="task-test123",
        project_id="proj-test123",
        name="쿠팡 셀러 계정 생성",
        description="쿠팡 마켓플레이스에 판매자 계정을 생성합니다",
        type=TaskType.ACTION,
        priority="high",
        required_inputs=[
            RequiredInput(
                key="business_number",
                label="사업자등록번호",
                type="string",
                required=True,
                description="10자리 사업자등록번호",
                example="123-45-67890"
            ),
            RequiredInput(
                key="bank_account",
                label="정산 계좌",
                type="string",
                required=True,
                description="정산금 입금 계좌",
            ),
        ],
        tools=[
            ToolRequirement(
                tool_id="coupang_api",
                name="쿠팡 API",
                type="api",
                required=True,
                status="not_connected"
            )
        ],
        approval_points=[
            ApprovalPoint(
                point="before_execution",
                description="계정 생성 전 정보 확인",
                approval_type="explicit"
            )
        ],
        execution_steps=[
            ExecutionStep(
                step=1,
                action="validate_inputs",
                description="입력 정보 검증",
            ),
            ExecutionStep(
                step=2,
                action="create_account",
                description="쿠팡 셀러 계정 생성",
                tool="coupang_api",
                approval_point="before_execution"
            ),
        ],
        status=TaskStatus.PENDING,
    )


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls."""
    with patch("langchain_anthropic.ChatAnthropic") as mock:
        mock_instance = MagicMock()
        mock_instance.ainvoke = AsyncMock(return_value=MagicMock(content="Mock response"))
        mock_instance.with_structured_output = MagicMock(return_value=mock_instance)
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_hr_analysis():
    """Mock HR analysis response."""
    from src.agents.hr import HRAnalysis, AgentProposal

    return HRAnalysis(
        analysis="쿠팡 입점을 위해 이커머스 전문가와 마케팅 전문가가 필요합니다.",
        proposed_agents=[
            AgentProposal(
                role_name="이커머스 전문가",
                description="온라인 쇼핑몰 입점 및 운영을 담당",
                specialties=["쿠팡 입점", "상품 등록", "재고 관리"],
                required_tools=["coupang_api"],
                limitations=["결제 시스템 개발 불가"],
                reason="쿠팡 입점 및 상품 관리에 필요"
            ),
            AgentProposal(
                role_name="마케팅 전문가",
                description="상품 마케팅 및 프로모션 담당",
                specialties=["키워드 광고", "프로모션 기획"],
                required_tools=["analytics_tool"],
                limitations=["대규모 광고 집행 불가"],
                reason="매출 목표 달성을 위한 마케팅 전략 수립에 필요"
            ),
        ],
        missing_information=[]
    )


@pytest.fixture
def mock_rm_analysis():
    """Mock RM analysis response."""
    from src.agents.rm import RMAnalysis, ProjectProposal, TaskProposal

    return RMAnalysis(
        analysis="쿠팡 입점 및 매출 달성을 위해 3단계 프로젝트를 수행합니다.",
        projects=[
            ProjectProposal(
                name="쿠팡 입점 프로젝트",
                description="쿠팡 마켓플레이스 입점 완료",
                priority="high",
                deliverables=["셀러 계정", "상품 등록 완료"],
                tasks=[
                    TaskProposal(
                        name="셀러 계정 생성",
                        description="쿠팡 셀러 계정을 생성합니다",
                        type="ACTION",
                        assigned_role="이커머스 전문가",
                        required_inputs=[
                            {"key": "business_number", "label": "사업자등록번호", "type": "string"}
                        ],
                        required_tools=[
                            {"tool_id": "coupang_api", "name": "쿠팡 API", "type": "api"}
                        ],
                        approval_points=[
                            {"point": "before_execution", "description": "계정 생성 전 확인", "approval_type": "explicit"}
                        ],
                        execution_steps=[
                            {"step": "1", "action": "create_account", "description": "계정 생성"}
                        ]
                    )
                ]
            )
        ],
        missing_expertise=[],
        required_tools=["coupang_api"]
    )


@pytest.fixture
def tool_registry():
    """Clean tool registry for testing."""
    from src.tools.registry import ToolRegistry

    registry = ToolRegistry.get_instance()
    registry.clear()
    yield registry
    registry.clear()


@pytest.fixture
def memory_manager():
    """Memory manager for testing."""
    from src.context.memory import MemoryManager

    manager = MemoryManager()
    yield manager
    manager.clear()


@pytest.fixture
def temp_db(tmp_path):
    """Temporary database for testing."""
    db_path = str(tmp_path / "test.db")
    return db_path
