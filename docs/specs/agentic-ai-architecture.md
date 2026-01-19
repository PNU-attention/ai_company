# Agentic AI Architecture Specification

> **Version**: 1.0.0
> **Status**: Draft
> **Last Updated**: 2025-01-19

---

## 1. 개요

### 1.1 목적

본 문서는 ai_company 프로젝트의 Agentic AI 아키텍처를 정의합니다. 기존 "AI Agent" 개념에서 한 단계 발전한 **Agentic AI** 패러다임을 적용하여, 자율적 추론과 도구 사용 능력을 갖춘 AI 시스템을 설계합니다.

### 1.2 AI Agent vs Agentic AI

| 구분 | AI Agent | Agentic AI |
|------|----------|------------|
| **자율성** | 주어진 명령 실행 | 목표 기반 자율 판단 및 계획 |
| **추론** | 단순 응답 생성 | 다단계 추론, 계획 수립, 자기 반성 |
| **도구 사용** | 정해진 도구만 사용 | 필요한 도구 동적 선택 및 조합 |
| **협업** | 단방향 지시 수행 | 양방향 소통, Escalation, 협상 |
| **적응성** | 정적 행동 | 피드백 기반 전략 수정 |

### 1.3 핵심 원칙

1. **Goal-Oriented**: 명령이 아닌 목표 기반 동작
2. **Reasoning-First**: 모든 행동 전 추론 단계 필수
3. **Tool-Augmented**: 외부 도구를 통한 능력 확장
4. **Context-Aware**: 풍부한 컨텍스트 기반 의사결정
5. **Collaborative**: 에이전트 간 효과적인 협업

---

## 2. 시스템 아키텍처

### 2.1 레이어 구조

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CEO Interface                               │
│                    (Human-in-the-Loop Layer)                        │
└─────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                        Context Layer                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ Shared      │  │ Conversation│  │ Task        │  │ Knowledge  │ │
│  │ Memory      │  │ History     │  │ State       │  │ Base       │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              RM (Supervisor / Orchestrator)                  │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │   │
│  │  │ Planner │  │ Router  │  │ Monitor │  │ State Manager   │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                    Communication Layer                              │
│                  (Agent-to-Agent Protocol)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ Message     │  │ Handshake   │  │ Event       │                 │
│  │ Queue       │  │ Protocol    │  │ Bus         │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│  Agentic AI   │         │  Agentic AI   │         │  Agentic AI   │
│   (Expert)    │         │   (Expert)    │         │     (HR)      │
│ ┌───────────┐ │         │ ┌───────────┐ │         │ ┌───────────┐ │
│ │ Reasoning │ │         │ │ Reasoning │ │         │ │ Reasoning │ │
│ │ Engine    │ │         │ │ Engine    │ │         │ │ Engine    │ │
│ └───────────┘ │         │ └───────────┘ │         │ └───────────┘ │
│ ┌───────────┐ │         │ ┌───────────┐ │         │ ┌───────────┐ │
│ │ Tool      │ │         │ │ Tool      │ │         │ │ Tool      │ │
│ │ Interface │ │         │ │ Interface │ │         │ │ Interface │ │
│ └───────────┘ │         │ └───────────┘ │         │ └───────────┘ │
└───────────────┘         └───────────────┘         └───────────────┘
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  │
┌─────────────────────────────────────────────────────────────────────┐
│                        Tool Layer                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ MCP Tools   │  │ Internal    │  │ External    │  │ Custom     │ │
│  │ (Figma,etc) │  │ Tools       │  │ APIs        │  │ Functions  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 레이어별 책임

| 레이어 | 책임 | 구현 기술 |
|--------|------|-----------|
| **CEO Interface** | 사용자 입력, 최종 승인, 피드백 | CLI / Web UI |
| **Context Layer** | 상태 관리, 메모리, 지식 저장 | LangGraph State |
| **Orchestration** | 작업 분배, 라우팅, 모니터링 | LangGraph Supervisor |
| **Communication** | 에이전트 간 메시지 교환 | A2A Protocol |
| **Agentic AI** | 추론, 실행, 도구 사용 | LangGraph Node + Claude |
| **Tool Layer** | 외부 시스템 연동 | MCP, APIs |

---

## 3. Supervisor Design Pattern

### 3.1 패턴 개요

Supervisor 패턴은 중앙 조율자(RM)가 작업을 분배하고 결과를 취합하는 구조입니다.

```
                    ┌─────────────┐
                    │     RM      │
                    │ (Supervisor)│
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐    ┌───────────┐    ┌───────────┐
    │  Worker 1 │    │  Worker 2 │    │  Worker N │
    └───────────┘    └───────────┘    └───────────┘
```

### 3.2 RM (Supervisor) 역할

```python
# LangGraph 기반 Supervisor 구현 예시
class RMSupervisor:
    """
    RM Supervisor의 핵심 역할:
    1. 작업 분해 (Task Decomposition)
    2. 에이전트 선택 (Agent Selection)
    3. 작업 라우팅 (Task Routing)
    4. 상태 모니터링 (State Monitoring)
    5. 결과 취합 (Result Aggregation)
    """

    def plan(self, goal: str) -> List[Task]:
        """목표를 세부 작업으로 분해"""
        pass

    def route(self, task: Task) -> Agent:
        """작업에 적합한 에이전트 선택"""
        pass

    def monitor(self, execution: Execution) -> Status:
        """실행 상태 모니터링"""
        pass

    def aggregate(self, results: List[Result]) -> FinalResult:
        """결과 취합 및 보고서 생성"""
        pass
```

### 3.3 Supervisor 결정 로직

```
┌─────────────────────────────────────────────────────────────┐
│                    Supervisor Decision Flow                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: Task/Message                                        │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │ Analyze Context │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐    ┌──────────────┐                   │
│  │ Need more info? │───▶│ Ask Clarify  │                   │
│  └────────┬────────┘    └──────────────┘                   │
│           │ No                                              │
│           ▼                                                 │
│  ┌─────────────────┐    ┌──────────────┐                   │
│  │ Need new agent? │───▶│ Request HR   │                   │
│  └────────┬────────┘    └──────────────┘                   │
│           │ No                                              │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │ Select Agent(s) │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │ Dispatch Task   │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐    ┌──────────────┐                   │
│  │ Task Complete?  │───▶│ Continue     │                   │
│  └────────┬────────┘ No └──────────────┘                   │
│           │ Yes                                             │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │ Report to CEO   │                                       │
│  └─────────────────┘                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Agent-to-Agent (A2A) Protocol

### 4.1 프로토콜 개요

Google의 Agent-to-Agent Protocol을 기반으로 에이전트 간 통신을 표준화합니다.

### 4.2 메시지 포맷

```json
{
  "protocol": "a2a/1.0",
  "message_id": "uuid-v4",
  "timestamp": "ISO-8601",
  "sender": {
    "agent_id": "rm-001",
    "agent_type": "supervisor",
    "capabilities": ["planning", "routing", "monitoring"]
  },
  "receiver": {
    "agent_id": "expert-fe-001",
    "agent_type": "expert"
  },
  "message_type": "task_assignment | task_result | escalation | query | response",
  "payload": {
    "task_id": "task-uuid",
    "content": {},
    "context": {},
    "constraints": {},
    "expected_output": {}
  },
  "metadata": {
    "priority": "high | medium | low",
    "deadline": "ISO-8601 | null",
    "retry_count": 0
  }
}
```

### 4.3 메시지 타입

| 타입 | 방향 | 용도 |
|------|------|------|
| `task_assignment` | Supervisor → Worker | 작업 할당 |
| `task_result` | Worker → Supervisor | 작업 결과 보고 |
| `escalation` | Worker → Supervisor | 문제 에스컬레이션 |
| `query` | Any → Any | 정보 요청 |
| `response` | Any → Any | 정보 응답 |
| `handshake` | Any → Any | 연결 확인 |
| `capability_check` | Supervisor → Worker | 능력 확인 |

### 4.4 핸드셰이크 프로토콜

```
Supervisor                          Worker
    │                                  │
    │──── handshake_request ──────────▶│
    │                                  │
    │◀─── handshake_response ─────────│
    │     (capabilities, status)       │
    │                                  │
    │──── capability_check ───────────▶│
    │                                  │
    │◀─── capability_response ─────────│
    │                                  │
    │──── task_assignment ────────────▶│
    │                                  │
```

---

## 5. Context Engineering

### 5.1 컨텍스트 구조

```
┌─────────────────────────────────────────────────────────────┐
│                      Context Store                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Global Context                      │   │
│  │  - Company Mission & Goals                          │   │
│  │  - Active Agents Registry                           │   │
│  │  - System Configuration                             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Project Context                      │   │
│  │  - Project Goals & Constraints                      │   │
│  │  - Task Graph & Dependencies                        │   │
│  │  - Progress & Status                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Agent Context                       │   │
│  │  - Agent Identity & Role                            │   │
│  │  - Conversation History                             │   │
│  │  - Working Memory                                   │   │
│  │  - Tool Execution History                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Task Context                        │   │
│  │  - Task Description & Requirements                  │   │
│  │  - Input Data & Constraints                         │   │
│  │  - Previous Attempts & Feedback                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 컨텍스트 전달 전략

```python
class ContextManager:
    """컨텍스트 엔지니어링 관리자"""

    def build_context(self, agent: Agent, task: Task) -> Context:
        """에이전트와 작업에 맞는 컨텍스트 구성"""
        return Context(
            global_ctx=self.get_relevant_global(task),
            project_ctx=self.get_project_context(task.project_id),
            agent_ctx=self.get_agent_context(agent.id),
            task_ctx=self.get_task_context(task.id),
            # 컨텍스트 윈도우 최적화
            compressed=self.compress_if_needed(...)
        )

    def update_context(self, agent: Agent, action: Action, result: Result):
        """액션 결과로 컨텍스트 업데이트"""
        pass

    def share_context(self, from_agent: Agent, to_agent: Agent, scope: str):
        """에이전트 간 컨텍스트 공유"""
        pass
```

### 5.3 메모리 타입

| 메모리 타입 | 용도 | 지속성 |
|-------------|------|--------|
| **Working Memory** | 현재 작업 관련 임시 정보 | 작업 종료 시 삭제 |
| **Episodic Memory** | 과거 대화/작업 이력 | 프로젝트 기간 |
| **Semantic Memory** | 학습된 지식, 패턴 | 영구 |
| **Procedural Memory** | 작업 수행 방법 | 영구 |

---

## 6. Agentic AI 구성요소

### 6.1 Reasoning Engine

각 Agentic AI는 독립적인 추론 엔진을 갖습니다.

```
┌─────────────────────────────────────────────────────────────┐
│                    Reasoning Engine                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input: Task + Context                                      │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │   1. Perceive   │  입력 이해 및 분석                      │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │   2. Reason     │  추론 및 계획 수립                      │
│  │   (CoT/ReAct)   │                                       │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │   3. Decide     │  행동 결정 (도구 선택 포함)              │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │   4. Act        │  행동 실행                             │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  ┌─────────────────┐                                       │
│  │   5. Reflect    │  결과 평가 및 자기 반성                  │
│  └────────┬────────┘                                       │
│           │                                                 │
│           ▼                                                 │
│  Output: Result + Updated Context                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 추론 전략

| 전략 | 용도 | 적용 상황 |
|------|------|-----------|
| **Chain-of-Thought (CoT)** | 단계별 논리적 추론 | 복잡한 문제 분석 |
| **ReAct** | 추론 + 행동 반복 | 도구 사용이 필요한 작업 |
| **Reflection** | 자기 평가 및 수정 | 품질 검증 필요 시 |
| **Tree-of-Thought** | 여러 경로 탐색 | 창의적 문제 해결 |

### 6.3 Tool Interface

```python
class ToolInterface:
    """Agentic AI의 도구 사용 인터페이스"""

    def __init__(self, agent: Agent):
        self.agent = agent
        self.available_tools = self.load_tools()
        self.tool_history = []

    def select_tool(self, task: Task, context: Context) -> Tool:
        """작업에 적합한 도구 선택 (추론 기반)"""
        # LLM이 도구 선택을 추론
        pass

    def execute_tool(self, tool: Tool, params: dict) -> Result:
        """도구 실행"""
        pass

    def evaluate_result(self, result: Result) -> Evaluation:
        """도구 실행 결과 평가"""
        pass
```

### 6.4 Tool Registry

```json
{
  "tools": [
    {
      "id": "figma-mcp",
      "name": "Figma MCP",
      "type": "mcp",
      "capabilities": ["design_read", "design_create", "export"],
      "required_permissions": ["figma:read", "figma:write"],
      "applicable_agents": ["ui-designer", "frontend-developer"]
    },
    {
      "id": "github-mcp",
      "name": "GitHub MCP",
      "type": "mcp",
      "capabilities": ["repo_read", "repo_write", "pr_create"],
      "required_permissions": ["github:repo"],
      "applicable_agents": ["developer", "devops"]
    }
  ]
}
```

---

## 7. Actionable Task Schema

> **핵심**: Task가 실제로 실행 가능하려면 "무엇이 필요한지", "어떤 도구로 수행할지", "언제 사람 확인이 필요한지"가 명시되어야 합니다.

### 7.1 Task 타입 분류

| 타입 | 설명 | 예시 |
|------|------|------|
| **ACTION** | 외부 시스템에 실제 변경을 가하는 작업 | 계정 생성, 결제 처리, API 호출 |
| **DOCUMENT** | 문서/보고서 작성 작업 | 가이드 작성, 분석 보고서 |
| **RESEARCH** | 정보 수집 및 분석 작업 | 시장 조사, 경쟁사 분석 |
| **APPROVAL** | CEO 승인 대기 작업 | 예산 승인, 계약 검토 |

### 7.2 확장된 Task 스키마

```json
{
  "taskId": "task_001",
  "name": "쿠팡 윙 계정 개설",
  "description": "쿠팡 윙 셀러 계정을 생성하고 사업자 인증 완료",

  "type": "ACTION",

  "requiredInputs": [
    {
      "key": "business_registration_number",
      "label": "사업자등록번호",
      "type": "string",
      "required": true,
      "source": "ceo_input",
      "validation": "^[0-9]{3}-[0-9]{2}-[0-9]{5}$"
    },
    {
      "key": "representative_name",
      "label": "대표자명",
      "type": "string",
      "required": true,
      "source": "ceo_input"
    },
    {
      "key": "business_registration_cert",
      "label": "사업자등록증 파일",
      "type": "file",
      "required": true,
      "source": "ceo_input",
      "acceptedFormats": ["pdf", "jpg", "png"]
    },
    {
      "key": "bank_account",
      "label": "정산 계좌 정보",
      "type": "object",
      "required": true,
      "source": "ceo_input",
      "schema": {
        "bank_name": "string",
        "account_number": "string",
        "account_holder": "string"
      }
    },
    {
      "key": "contact_phone",
      "label": "담당자 연락처",
      "type": "string",
      "required": true,
      "source": "ceo_input"
    },
    {
      "key": "contact_email",
      "label": "담당자 이메일",
      "type": "string",
      "required": true,
      "source": "ceo_input",
      "validation": "email"
    }
  ],

  "tools": [
    {
      "toolId": "coupang-wing-api",
      "name": "쿠팡 윙 API",
      "type": "external_api",
      "required": true,
      "status": "not_connected",
      "connectionGuide": "https://wing.coupang.com/developer",
      "capabilities": ["seller_registration", "product_management"],
      "fallback": "web_automation"
    },
    {
      "toolId": "web-automation",
      "name": "웹 자동화 (Playwright)",
      "type": "mcp",
      "required": false,
      "status": "available",
      "note": "API 미연결 시 대체 수단"
    }
  ],

  "approvalPoints": [
    {
      "point": "before_submission",
      "description": "계정 정보 제출 전 CEO 확인",
      "requiredData": ["all_inputs"],
      "approvalType": "explicit"
    },
    {
      "point": "after_creation",
      "description": "계정 생성 완료 후 결과 확인",
      "requiredData": ["seller_id", "store_url"],
      "approvalType": "notification"
    }
  ],

  "executionSteps": [
    {
      "step": 1,
      "action": "collect_inputs",
      "description": "CEO에게 필요 정보 요청",
      "blocking": true
    },
    {
      "step": 2,
      "action": "validate_inputs",
      "description": "입력 데이터 유효성 검증"
    },
    {
      "step": 3,
      "action": "check_tool_availability",
      "description": "쿠팡 API 연결 상태 확인"
    },
    {
      "step": 4,
      "action": "request_approval",
      "description": "CEO에게 제출 전 승인 요청",
      "approvalPoint": "before_submission",
      "blocking": true
    },
    {
      "step": 5,
      "action": "execute_registration",
      "description": "계정 등록 API 호출 또는 웹 자동화 실행",
      "tool": "coupang-wing-api"
    },
    {
      "step": 6,
      "action": "verify_result",
      "description": "등록 결과 확인 및 검증"
    },
    {
      "step": 7,
      "action": "notify_completion",
      "description": "CEO에게 완료 알림",
      "approvalPoint": "after_creation"
    }
  ],

  "outputs": [
    {
      "key": "seller_id",
      "label": "셀러 ID",
      "type": "string"
    },
    {
      "key": "store_url",
      "label": "스토어 URL",
      "type": "string"
    },
    {
      "key": "api_credentials",
      "label": "API 인증 정보",
      "type": "object",
      "sensitive": true
    }
  ],

  "escalationConditions": [
    {
      "condition": "tool_not_available",
      "action": "request_tool_connection",
      "message": "쿠팡 윙 API 연결이 필요합니다. CEO에게 MCP 연결을 요청합니다."
    },
    {
      "condition": "input_missing",
      "action": "request_input",
      "message": "작업 수행에 필요한 정보가 부족합니다."
    },
    {
      "condition": "registration_failed",
      "action": "report_error",
      "message": "계정 등록 중 오류가 발생했습니다."
    }
  ],

  "assignedTo": "agent_ecommerce_ops_20250113",
  "dependencies": [],
  "status": "pending",
  "priority": "high"
}
```

### 7.3 정보 요청 플로우 (Human-in-the-Loop)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Information Request Flow                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Agentic AI receives Task                                           │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────────┐                                           │
│  │ Check requiredInputs │                                          │
│  └──────────┬──────────┘                                           │
│             │                                                       │
│             ▼                                                       │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐   │
│  │ All inputs present? │─No─▶│ Generate Input Request Message │   │
│  └──────────┬──────────┘    └──────────────┬──────────────────┘   │
│             │ Yes                           │                       │
│             │                               ▼                       │
│             │                    ┌─────────────────────────────┐   │
│             │                    │ Send to CEO via A2A         │   │
│             │                    │ (message_type: query)       │   │
│             │                    └──────────────┬──────────────┘   │
│             │                                   │                   │
│             │                                   ▼                   │
│             │                    ┌─────────────────────────────┐   │
│             │                    │ WAIT for CEO Response       │   │
│             │                    │ (interrupt_before)          │   │
│             │                    └──────────────┬──────────────┘   │
│             │                                   │                   │
│             │◀──────────────────────────────────┘                   │
│             │                                                       │
│             ▼                                                       │
│  ┌─────────────────────┐                                           │
│  │ Validate Inputs     │                                           │
│  └──────────┬──────────┘                                           │
│             │                                                       │
│             ▼                                                       │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐   │
│  │ Validation passed?  │─No─▶│ Request correction from CEO   │   │
│  └──────────┬──────────┘    └─────────────────────────────────┘   │
│             │ Yes                                                   │
│             ▼                                                       │
│  ┌─────────────────────┐                                           │
│  │ Proceed to execution│                                           │
│  └─────────────────────┘                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.4 정보 요청 메시지 예시

```json
{
  "protocol": "a2a/1.0",
  "message_id": "msg-uuid-001",
  "message_type": "query",
  "sender": {
    "agent_id": "agent_ecommerce_ops_20250113",
    "agent_type": "expert"
  },
  "receiver": {
    "agent_id": "ceo",
    "agent_type": "human"
  },
  "payload": {
    "task_id": "task_001",
    "query_type": "input_request",
    "title": "쿠팡 윙 계정 개설을 위한 정보가 필요합니다",
    "required_inputs": [
      {
        "key": "business_registration_number",
        "label": "사업자등록번호",
        "format": "000-00-00000",
        "example": "123-45-67890"
      },
      {
        "key": "representative_name",
        "label": "대표자명"
      },
      {
        "key": "business_registration_cert",
        "label": "사업자등록증 파일",
        "acceptedFormats": ["pdf", "jpg", "png"],
        "uploadRequired": true
      },
      {
        "key": "bank_account",
        "label": "정산 계좌 정보",
        "fields": ["은행명", "계좌번호", "예금주"]
      },
      {
        "key": "contact_phone",
        "label": "담당자 연락처"
      },
      {
        "key": "contact_email",
        "label": "담당자 이메일"
      }
    ],
    "context": "쿠팡 윙 셀러 계정을 생성하기 위해 위 정보가 필요합니다. 사업자등록증은 쿠팡 측에 제출되며, 계좌 정보는 정산금 입금에 사용됩니다."
  },
  "metadata": {
    "priority": "high",
    "blocking": true,
    "timeout": null
  }
}
```

### 7.5 Tool Availability Check

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Tool Availability Flow                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Before Task Execution                                              │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────────┐                                           │
│  │ List required tools │                                           │
│  └──────────┬──────────┘                                           │
│             │                                                       │
│             ▼                                                       │
│  ┌─────────────────────┐                                           │
│  │ For each tool:      │                                           │
│  │ Check connection    │                                           │
│  └──────────┬──────────┘                                           │
│             │                                                       │
│     ┌───────┴───────┐                                              │
│     │               │                                               │
│     ▼               ▼                                               │
│ Connected?       Not Connected                                      │
│     │               │                                               │
│     │               ▼                                               │
│     │    ┌─────────────────────┐                                   │
│     │    │ Has fallback tool?  │                                   │
│     │    └──────────┬──────────┘                                   │
│     │        │             │                                        │
│     │       Yes           No                                        │
│     │        │             │                                        │
│     │        ▼             ▼                                        │
│     │    Use fallback   Escalate to CEO                            │
│     │        │          "MCP 연결 필요"                              │
│     │        │             │                                        │
│     └────────┴─────────────┘                                        │
│             │                                                       │
│             ▼                                                       │
│  ┌─────────────────────┐                                           │
│  │ All tools ready?    │                                           │
│  └──────────┬──────────┘                                           │
│             │ Yes                                                   │
│             ▼                                                       │
│  ┌─────────────────────┐                                           │
│  │ Proceed to execution│                                           │
│  └─────────────────────┘                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.6 Task 실행 상태 머신

```
                    ┌─────────────┐
                    │   PENDING   │
                    └──────┬──────┘
                           │ start
                           ▼
                    ┌─────────────┐
              ┌────▶│INPUT_REQUIRED│◀────┐
              │     └──────┬──────┘      │
              │            │ inputs_received
              │            ▼             │
              │     ┌─────────────┐      │
              │     │ VALIDATING  │      │
              │     └──────┬──────┘      │
              │            │             │
              │     invalid│    valid    │
              │            │             │
              └────────────┤             │
                           ▼             │
                    ┌─────────────┐      │
              ┌────▶│TOOL_CHECK   │      │
              │     └──────┬──────┘      │
              │            │             │
         tool │   tool_ok  │  tool_missing
        retry │            │             │
              │            │             ▼
              │            │      ┌─────────────┐
              │            │      │AWAITING_TOOL│──────┐
              │            │      └─────────────┘      │
              │            │             │ tool_connected
              │            │◀────────────┘
              │            │
              │            ▼
              │     ┌─────────────┐
              │     │APPROVAL_WAIT│ (if approval required)
              │     └──────┬──────┘
              │            │ approved
              │            ▼
              │     ┌─────────────┐
              └────▶│  EXECUTING  │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │             │
                success        failure
                    │             │
                    ▼             ▼
             ┌───────────┐  ┌───────────┐
             │ COMPLETED │  │  FAILED   │
             └───────────┘  └───────────┘
```

### 7.7 기존 Task 마이그레이션 가이드

기존 Task 구조를 새 스키마로 변환하는 방법:

**Before (기존):**
```json
{
  "taskId": "task_001",
  "name": "쿠팡 윙 계정 개설",
  "description": "쿠팡 윙 셀러 계정을 생성하고 사업자 인증 완료",
  "outputs": ["쿠팡 윙 계정 정보", "쿠팡 수수료 정책 문서"]
}
```

**After (신규):**
```json
{
  "taskId": "task_001",
  "name": "쿠팡 윙 계정 개설",
  "description": "쿠팡 윙 셀러 계정을 생성하고 사업자 인증 완료",
  "type": "ACTION",
  "requiredInputs": [ /* CEO에게 요청할 정보 */ ],
  "tools": [ /* 필요한 도구 목록 */ ],
  "approvalPoints": [ /* CEO 승인 필요 지점 */ ],
  "executionSteps": [ /* 단계별 실행 계획 */ ],
  "outputs": [ /* 구조화된 출력 정의 */ ],
  "escalationConditions": [ /* 에스컬레이션 조건 */ ]
}
```

---

## 8. LangGraph 통합

### 8.1 왜 LangGraph인가?

| 요구사항 | LangGraph 지원 |
|----------|---------------|
| Supervisor 패턴 | 네이티브 지원 (langgraph-supervisor) |
| 상태 관리 | StateGraph로 선언적 정의 |
| 조건부 라우팅 | Conditional Edges |
| 순환 워크플로우 | Cycles 지원 |
| 체크포인팅 | 내장 Checkpointer |
| Human-in-the-loop | interrupt_before/after |
| 스트리밍 | 내장 지원 |

### 8.2 시스템 그래프 구조

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_supervisor

# 상태 정의
class CompanyState(TypedDict):
    messages: Annotated[list, add_messages]
    current_task: Optional[Task]
    context: Context
    agent_outputs: dict
    final_output: Optional[str]

# 그래프 생성
def create_company_graph():
    graph = StateGraph(CompanyState)

    # 노드 추가
    graph.add_node("rm_supervisor", rm_supervisor_node)
    graph.add_node("hr_agent", hr_agent_node)
    graph.add_node("expert_pool", expert_pool_node)
    graph.add_node("context_manager", context_manager_node)

    # 엣지 정의
    graph.add_edge(START, "rm_supervisor")
    graph.add_conditional_edges(
        "rm_supervisor",
        route_task,
        {
            "need_expert": "expert_pool",
            "need_hire": "hr_agent",
            "complete": END
        }
    )
    graph.add_edge("hr_agent", "rm_supervisor")
    graph.add_edge("expert_pool", "rm_supervisor")

    return graph.compile(checkpointer=MemorySaver())
```

### 8.3 Supervisor 노드 구현

```python
from langchain_anthropic import ChatAnthropic
from langgraph_supervisor import create_supervisor

# Claude를 LLM 백엔드로 사용
llm = ChatAnthropic(model="claude-sonnet-4-20250514")

# Supervisor 생성
rm_supervisor = create_supervisor(
    agents=[hr_agent, *expert_agents],
    model=llm,
    prompt="""당신은 ai_company의 RM(Resource Manager)입니다.

    역할:
    1. CEO의 목표를 분석하고 작업으로 분해합니다
    2. 적절한 Expert 에이전트에게 작업을 할당합니다
    3. 필요시 HR에게 새로운 에이전트 생성을 요청합니다
    4. 작업 진행을 모니터링하고 결과를 취합합니다

    현재 컨텍스트: {context}
    """,
    output_mode="full_history"
)
```

### 8.4 Expert 노드 구현

```python
from langgraph.prebuilt import create_react_agent

def create_expert_agent(role: str, tools: list, system_prompt: str):
    """Expert Agentic AI 생성"""

    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=f"""당신은 {role} 전문가입니다.

        {system_prompt}

        추론 과정:
        1. 작업을 이해하고 분석합니다
        2. 필요한 도구를 선택합니다
        3. 단계별로 실행합니다
        4. 결과를 검증합니다
        5. 완료 또는 Escalation을 보고합니다
        """
    )
```

### 8.5 Human-in-the-Loop 통합

```python
# CEO 승인이 필요한 지점에서 중단
graph = StateGraph(CompanyState)
graph.add_node("await_ceo_approval", await_approval_node)

# 컴파일 시 interrupt 지정
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["await_ceo_approval"]
)

# 실행
for event in app.stream(initial_state, config):
    if event.get("__interrupt__"):
        # CEO 입력 대기
        user_input = get_ceo_input()
        # 재개
        app.stream(Command(resume=user_input), config)
```

---

## 9. 동적 실행 메커니즘

> **핵심**: 모든 것이 동적이어야 합니다. CEO의 입력에 따라 HR이 에이전트를 추론하여 생성하고, RM이 프로젝트/Task를 추론하여 생성합니다.

### 9.1 현재 구조의 한계

| 구분 | 현재 (정적) | 필요 (동적) |
|------|------------|------------|
| **HR Agent** | `.md` 파일 정의 → Claude Code가 흉내 | LLM 추론 → 그래프 노드 동적 생성 |
| **RM Agent** | `.md` 파일 정의 → JSON 파일 생성 | LLM 추론 → Task 동적 생성 및 라우팅 |
| **Expert 생성** | `experts/*.md` 파일 생성 | `create_react_agent()` 실행 가능한 AI 인스턴스 |
| **Task 실행** | JSON 문서로만 존재 | 실제 실행 엔진이 Task 처리 |

### 9.2 동적 실행 흐름

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Dynamic Execution Flow                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CEO Input: "온라인 쿠폰 비즈니스, 월 매출 1억 목표"                    │
│           │                                                         │
│           ▼                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  RM Agentic AI (LLM 추론)                                    │   │
│  │                                                              │   │
│  │  1. 목표 분석: "쿠폰 플랫폼 + 판매 채널 + 마케팅 필요"          │   │
│  │  2. 필요 전문가 추론: 개발자, 마케터, 운영 담당자               │   │
│  │  3. HR에게 전문가 생성 요청                                   │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  HR Agentic AI (LLM 추론)                                    │   │
│  │                                                              │   │
│  │  1. 역할 정의: 풀스택 개발자, 디지털 마케터, 이커머스 운영       │   │
│  │  2. 각 역할의 전문성, 도구 권한, 한계 정의                     │   │
│  │  3. 그래프에 Expert 노드 동적 추가                            │   │
│  │     → create_react_agent(role, tools, prompt)               │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  RM Agentic AI (Task 생성)                                   │   │
│  │                                                              │   │
│  │  Project 1: 쿠폰 플랫폼 개발                                  │   │
│  │    Task 1.1: 요구사항 정의 (type: DOCUMENT)                  │   │
│  │    Task 1.2: 서버 구축 (type: ACTION)                        │   │
│  │      - requiredInputs: [AWS 계정, 도메인]  ← CEO에게 요청     │   │
│  │      - tools: [aws-mcp, github-mcp]                         │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                              │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  [INTERRUPT] CEO에게 정보 요청                               │   │
│  │                                                              │   │
│  │  "서버 구축을 위해 다음 정보가 필요합니다:                      │   │
│  │   1. AWS 계정 정보                                           │   │
│  │   2. 사용할 도메인                                           │   │
│  │   3. 예상 트래픽 규모"                                        │   │
│  └──────────────────────────┬──────────────────────────────────┘   │
│                              │                                      │
│                     CEO 입력 │                                      │
│                              ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Expert (풀스택 개발자) - 실제 액션 수행                       │   │
│  │                                                              │   │
│  │  → AWS MCP 호출 → 실제 EC2 인스턴스 생성                      │   │
│  │  → GitHub MCP 호출 → 실제 레포지토리 생성                     │   │
│  │  → 결과 보고 → RM에게 전달                                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.3 동적 에이전트 생성 (HR)

```python
class HRAgenticAI:
    """HR Agentic AI - 동적 에이전트 생성"""

    def __init__(self, llm, graph_builder):
        self.llm = llm
        self.graph_builder = graph_builder
        self.agent_registry = {}

    async def analyze_and_create_agents(self, company_goal: str, rm_request: dict) -> List[Agent]:
        """목표 분석 후 필요한 에이전트 동적 생성"""

        # 1. LLM 추론: 어떤 역할이 필요한가?
        analysis_prompt = f"""
        회사 목표: {company_goal}
        RM 요청: {rm_request}

        이 목표를 달성하기 위해 필요한 전문가 역할을 분석하세요.
        각 역할에 대해 정의하세요:
        - role_name: 역할 이름
        - description: 역할 설명
        - specialties: 전문 분야 목록
        - required_tools: 필요한 도구 목록
        - limitations: 역할 한계
        """

        roles = await self.llm.ainvoke(analysis_prompt)

        # 2. 각 역할에 대해 실제 Agentic AI 생성
        created_agents = []
        for role in roles:
            agent = self._create_expert_agent(role)
            created_agents.append(agent)

            # 3. 그래프에 노드로 추가
            self.graph_builder.add_node(
                role['role_name'],
                agent.invoke
            )

            self.agent_registry[role['role_name']] = agent

        return created_agents

    def _create_expert_agent(self, role: dict) -> Agent:
        """역할 정의로부터 실제 동작하는 Expert 에이전트 생성"""

        # 역할에 맞는 도구 바인딩
        tools = self._get_tools_for_role(role['required_tools'])

        # ReAct 에이전트 생성
        return create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=f"""당신은 {role['role_name']} 전문가입니다.

            전문 분야: {role['specialties']}

            역할 한계: {role['limitations']}
            → 한계를 초과하는 작업은 RM에게 Escalation하세요.

            작업 수행 시:
            1. 필요한 정보가 부족하면 명확히 요청하세요
            2. 도구를 사용하여 실제 액션을 수행하세요
            3. 결과를 검증하고 보고하세요
            """
        )
```

### 9.4 동적 Task 생성 (RM)

```python
class RMAgenticAI:
    """RM Agentic AI - 동적 Task 생성 및 오케스트레이션"""

    def __init__(self, llm, hr_agent, agent_registry):
        self.llm = llm
        self.hr_agent = hr_agent
        self.agent_registry = agent_registry

    async def plan_and_execute(self, company_goal: str) -> dict:
        """목표 분석 → 프로젝트/Task 생성 → 실행"""

        # 1. 목표 분석 및 필요 전문가 파악
        planning_prompt = f"""
        회사 목표: {company_goal}

        이 목표를 달성하기 위한 계획을 수립하세요:

        1. 필요한 전문가 역할 목록
        2. 프로젝트 분해 (목표 → 프로젝트들)
        3. 각 프로젝트의 Task 분해

        각 Task에 대해 다음을 정의하세요:
        - type: ACTION | DOCUMENT | RESEARCH | APPROVAL
        - requiredInputs: CEO에게 요청해야 할 정보 (있는 경우)
        - tools: 필요한 도구 목록
        - assignedRole: 담당 역할
        - approvalPoints: CEO 승인 필요 지점
        """

        plan = await self.llm.ainvoke(planning_prompt)

        # 2. HR에게 필요한 에이전트 생성 요청
        if plan['required_roles']:
            await self.hr_agent.analyze_and_create_agents(
                company_goal,
                {'required_roles': plan['required_roles']}
            )

        # 3. Task 스키마 동적 생성
        tasks = []
        for project in plan['projects']:
            for task_def in project['tasks']:
                task = self._create_actionable_task(task_def)
                tasks.append(task)

        return {
            'projects': plan['projects'],
            'tasks': tasks,
            'execution_graph': self._build_execution_graph(tasks)
        }

    def _create_actionable_task(self, task_def: dict) -> Task:
        """실행 가능한 Task 스키마 생성"""

        return Task(
            task_id=generate_uuid(),
            name=task_def['name'],
            type=task_def['type'],  # ACTION, DOCUMENT, etc.

            # 핵심: 필요한 입력 정의
            required_inputs=[
                RequiredInput(
                    key=inp['key'],
                    label=inp['label'],
                    type=inp['type'],
                    source='ceo_input',  # CEO에게 요청
                    required=inp.get('required', True)
                )
                for inp in task_def.get('requiredInputs', [])
            ],

            # 핵심: 필요한 도구 정의
            tools=[
                ToolRequirement(
                    tool_id=tool['id'],
                    required=tool.get('required', True),
                    fallback=tool.get('fallback')
                )
                for tool in task_def.get('tools', [])
            ],

            # 핵심: 승인 포인트 정의
            approval_points=[
                ApprovalPoint(
                    point=ap['point'],
                    description=ap['description'],
                    approval_type=ap['type']
                )
                for ap in task_def.get('approvalPoints', [])
            ],

            assigned_to=task_def['assignedRole'],
            execution_steps=self._infer_execution_steps(task_def)
        )
```

### 9.5 정보 요청 메커니즘 (Human-in-the-Loop)

```python
class TaskExecutor:
    """Task 실행기 - 정보 요청 및 도구 실행"""

    async def execute_task(self, task: Task, state: CompanyState) -> TaskResult:
        """Task 실행 - 필요시 CEO에게 정보 요청"""

        # 1. 필요한 입력 체크
        missing_inputs = self._check_required_inputs(task, state)

        if missing_inputs:
            # 2. CEO에게 정보 요청 (interrupt)
            return TaskResult(
                status='INPUT_REQUIRED',
                interrupt=True,
                request=InputRequest(
                    task_id=task.task_id,
                    title=f"{task.name}을(를) 위한 정보가 필요합니다",
                    required_inputs=missing_inputs,
                    context=self._build_request_context(task)
                )
            )

        # 3. 필요한 도구 체크
        missing_tools = self._check_required_tools(task)

        if missing_tools:
            # 4. CEO에게 도구 연결 요청
            return TaskResult(
                status='TOOL_REQUIRED',
                interrupt=True,
                request=ToolRequest(
                    task_id=task.task_id,
                    title=f"{task.name} 수행을 위해 도구 연결이 필요합니다",
                    required_tools=missing_tools
                )
            )

        # 5. 승인 포인트 체크
        if task.has_approval_before_execution():
            return TaskResult(
                status='APPROVAL_REQUIRED',
                interrupt=True,
                request=ApprovalRequest(
                    task_id=task.task_id,
                    title=f"{task.name} 실행 전 승인이 필요합니다",
                    data_to_review=self._gather_approval_data(task, state)
                )
            )

        # 6. 실제 실행
        agent = self.agent_registry[task.assigned_to]
        result = await agent.ainvoke({
            'task': task,
            'context': state.context,
            'inputs': state.collected_inputs
        })

        return TaskResult(
            status='COMPLETED',
            output=result
        )
```

### 9.6 LangGraph 통합 구현

```python
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

def create_dynamic_company_graph():
    """동적 회사 그래프 생성"""

    # 상태 정의
    class CompanyState(TypedDict):
        messages: Annotated[list, add_messages]
        company_goal: str
        available_agents: dict
        current_project: Optional[dict]
        current_task: Optional[Task]
        collected_inputs: dict
        execution_results: list

    # 그래프 빌더
    graph = StateGraph(CompanyState)

    # 핵심 노드들
    graph.add_node("rm_supervisor", rm_supervisor_node)
    graph.add_node("hr_agent", hr_agent_node)
    graph.add_node("task_executor", task_executor_node)
    graph.add_node("input_collector", input_collector_node)
    graph.add_node("tool_checker", tool_checker_node)

    # 동적 Expert 노드는 HR이 런타임에 추가
    # graph.add_node("expert_XXX", ...) ← HR이 동적 추가

    # 엣지 정의
    graph.add_edge(START, "rm_supervisor")

    graph.add_conditional_edges(
        "rm_supervisor",
        route_rm_decision,
        {
            "need_agents": "hr_agent",
            "execute_task": "task_executor",
            "complete": END
        }
    )

    graph.add_edge("hr_agent", "rm_supervisor")

    graph.add_conditional_edges(
        "task_executor",
        route_task_result,
        {
            "input_required": "input_collector",
            "tool_required": "tool_checker",
            "approval_required": "input_collector",  # CEO 입력 대기
            "completed": "rm_supervisor",
            "failed": "rm_supervisor"
        }
    )

    graph.add_edge("input_collector", "task_executor")
    graph.add_edge("tool_checker", "task_executor")

    # 체크포인터로 상태 저장
    checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["input_collector"]  # CEO 입력 전 중단
    )
```

---

## 10. 기술 스택

### 10.1 필수 구성요소

| 구성요소 | 기술 | 용도 | 필수 여부 |
|----------|------|------|----------|
| **오케스트레이션** | LangGraph | 상태 관리, 워크플로우, 동적 라우팅 | ⭐⭐⭐ 필수 |
| **LLM 통합** | LangChain | LLM 호출, 도구 바인딩, 프롬프트 관리 | ⭐⭐⭐ 필수 |
| **LLM 백엔드** | Claude API | Agentic AI의 두뇌 | ⭐⭐⭐ 필수 |
| **외부 도구** | MCP | Figma, GitHub, Slack 등 연동 | ⭐⭐⭐ 필수 |

### 10.2 권장 구성요소

| 구성요소 | 기술 선택지 | 용도 | 필수 여부 |
|----------|------------|------|----------|
| **벡터 DB** | Chroma / Qdrant / Pinecone | 장기 메모리, Knowledge Base | ⭐⭐ 권장 |
| **상태 저장소** | SQLite / PostgreSQL / Redis | 체크포인팅, 세션 복원 | ⭐⭐ 권장 |
| **모니터링** | LangSmith | 실행 추적, 디버깅 | ⭐ 선택 |

### 10.3 기술 스택 다이어그램

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ai_company Tech Stack                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     CEO Interface Layer                      │   │
│  │              CLI / Web UI (Future)                          │   │
│  └─────────────────────────────┬───────────────────────────────┘   │
│                                │                                    │
│  ┌─────────────────────────────┴───────────────────────────────┐   │
│  │                    Application Layer                         │   │
│  │                                                              │   │
│  │   ┌──────────────────────────────────────────────────────┐  │   │
│  │   │                    LangGraph                          │  │   │
│  │   │  - StateGraph (상태 관리)                             │  │   │
│  │   │  - Checkpointer (체크포인팅)                          │  │   │
│  │   │  - Interrupt (Human-in-the-loop)                     │  │   │
│  │   │  - Dynamic Node Addition (동적 노드 추가)             │  │   │
│  │   └──────────────────────────────────────────────────────┘  │   │
│  │                              │                               │   │
│  │   ┌──────────────────────────┴──────────────────────────┐   │   │
│  │   │                    LangChain                         │   │   │
│  │   │  - ChatAnthropic (Claude 연동)                       │   │   │
│  │   │  - Tool Binding (도구 바인딩)                        │   │   │
│  │   │  - create_react_agent (ReAct 에이전트)               │   │   │
│  │   └──────────────────────────────────────────────────────┘   │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│       ┌────────────────────────┼────────────────────────┐          │
│       │                        │                        │          │
│       ▼                        ▼                        ▼          │
│  ┌─────────────┐        ┌─────────────┐        ┌─────────────┐    │
│  │   LLM       │        │   Memory    │        │   Tools     │    │
│  │   Layer     │        │   Layer     │        │   Layer     │    │
│  │             │        │             │        │             │    │
│  │ ┌─────────┐ │        │ ┌─────────┐ │        │ ┌─────────┐ │    │
│  │ │ Claude  │ │        │ │ Vector  │ │        │ │   MCP   │ │    │
│  │ │  API    │ │        │ │   DB    │ │        │ │ Servers │ │    │
│  │ │         │ │        │ │(Chroma) │ │        │ │         │ │    │
│  │ └─────────┘ │        │ └─────────┘ │        │ │ Figma   │ │    │
│  │             │        │             │        │ │ GitHub  │ │    │
│  │             │        │ ┌─────────┐ │        │ │ Slack   │ │    │
│  │             │        │ │ State   │ │        │ │ AWS     │ │    │
│  │             │        │ │ Store   │ │        │ │ ...     │ │    │
│  │             │        │ │(SQLite) │ │        │ └─────────┘ │    │
│  │             │        │ └─────────┘ │        │             │    │
│  └─────────────┘        └─────────────┘        └─────────────┘    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Observability Layer (선택)                │   │
│  │                        LangSmith                            │   │
│  │  - 실행 추적 / 디버깅 / 프롬프트 최적화                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 10.4 Python 의존성

```toml
# pyproject.toml

[project]
name = "ai-company"
version = "0.1.0"
requires-python = ">=3.11"

dependencies = [
    # Core
    "langgraph>=0.2.0",
    "langchain>=0.3.0",
    "langchain-anthropic>=0.2.0",

    # Memory & Storage
    "chromadb>=0.5.0",           # 벡터 DB
    "sqlalchemy>=2.0.0",         # 상태 저장소 ORM

    # MCP Integration
    "mcp>=1.0.0",                # MCP 클라이언트

    # Utilities
    "pydantic>=2.0.0",           # 데이터 검증
    "python-dotenv>=1.0.0",      # 환경 변수
]

[project.optional-dependencies]
dev = [
    "langsmith>=0.1.0",          # 모니터링 (선택)
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]
```

### 10.5 환경 구성

```bash
# .env

# LLM
ANTHROPIC_API_KEY=sk-ant-...

# Vector DB (Chroma - 로컬은 설정 불필요)
# PINECONE_API_KEY=...         # Pinecone 사용 시

# State Store
DATABASE_URL=sqlite:///./data/state.db

# MCP Servers
MCP_FIGMA_TOKEN=...
MCP_GITHUB_TOKEN=...

# Observability (선택)
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=ai-company
```

---

## 11. 디렉토리 구조 (업데이트)

```
ai_company/
├── .claude/
│   ├── agents/
│   │   ├── core/
│   │   │   ├── hr-agent.md
│   │   │   └── rm-agent.md
│   │   ├── experts/
│   │   └── templates/
│   └── skills/
│
├── src/                              # LangGraph 구현 코드
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                   # Agentic AI 베이스 클래스
│   │   ├── hr.py                     # HR Agent
│   │   ├── rm.py                     # RM Supervisor
│   │   └── expert_factory.py         # Expert 동적 생성
│   │
│   ├── context/
│   │   ├── __init__.py
│   │   ├── manager.py                # Context Manager
│   │   ├── memory.py                 # Memory Store
│   │   └── state.py                  # State Definitions
│   │
│   ├── communication/
│   │   ├── __init__.py
│   │   ├── a2a_protocol.py           # A2A Protocol 구현
│   │   └── message_queue.py          # Message Queue
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── registry.py               # Tool Registry
│   │   ├── mcp_adapter.py            # MCP 어댑터
│   │   └── tool_selector.py          # Tool Selection Logic
│   │
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── company_graph.py          # Main LangGraph
│   │   ├── nodes.py                  # Graph Nodes
│   │   └── edges.py                  # Conditional Edges
│   │
│   └── main.py                       # Entry Point
│
├── company/
│   ├── context.json
│   └── agents.json
│
├── projects/
├── docs/
│   └── specs/
│       └── agentic-ai-architecture.md  # 본 문서
│
└── README.md
```

---

## 12. 구현 로드맵

### Phase 0: 환경 설정
- [ ] Python 프로젝트 초기화 (pyproject.toml)
- [ ] 의존성 설치 (LangGraph, LangChain, langchain-anthropic)
- [ ] 환경 변수 설정 (.env)
- [ ] 디렉토리 구조 생성 (src/)

### Phase 1: 핵심 그래프 구축
- [ ] CompanyState 정의 (상태 스키마)
- [ ] RM Supervisor 노드 구현 (LLM 추론 기반)
- [ ] HR Agent 노드 구현 (동적 에이전트 생성)
- [ ] 기본 그래프 구조 생성 및 연결

### Phase 2: 동적 실행 메커니즘
- [ ] 동적 Expert 노드 생성 로직 (HR → create_react_agent)
- [ ] 동적 Task 생성 로직 (RM → Task 스키마)
- [ ] Task Executor 구현
- [ ] Conditional Edges (라우팅 로직)

### Phase 3: Human-in-the-Loop
- [ ] 정보 요청 메커니즘 (INPUT_REQUIRED → interrupt)
- [ ] 도구 연결 요청 (TOOL_REQUIRED → interrupt)
- [ ] CEO 승인 요청 (APPROVAL_REQUIRED → interrupt)
- [ ] 입력 수집 및 검증 노드

### Phase 4: 도구 통합
- [ ] Tool Registry 구현
- [ ] MCP Adapter 구현 (Figma, GitHub 등)
- [ ] Tool Availability Check 로직
- [ ] Fallback Tool 처리

### Phase 5: 컨텍스트 & 메모리
- [ ] Context Manager 구현
- [ ] 벡터 DB 연동 (Chroma)
- [ ] 상태 저장소 연동 (SQLite/PostgreSQL)
- [ ] 체크포인팅 설정

### Phase 6: 통합 테스트
- [ ] 단위 테스트 (각 노드)
- [ ] 통합 테스트 (전체 그래프)
- [ ] End-to-end 시나리오 테스트
  - [ ] CEO 목표 입력 → HR 에이전트 생성 → RM Task 생성 → Expert 실행
  - [ ] 정보 요청 → CEO 입력 → 작업 재개
  - [ ] 도구 연결 요청 → MCP 연결 → 실제 액션 수행
- [ ] LangSmith 연동 (선택)

---

## 13. 참고 자료

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Google A2A Protocol](https://github.com/google/A2A)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)

---

## Appendix A: 용어 정의

| 용어 | 정의 |
|------|------|
| **Agentic AI** | 목표 기반 자율 추론과 도구 사용 능력을 갖춘 AI 시스템 |
| **Supervisor** | 작업 분배와 조율을 담당하는 중앙 에이전트 |
| **A2A Protocol** | Agent-to-Agent 통신 프로토콜 |
| **Context Engineering** | 에이전트에게 전달되는 컨텍스트를 설계하고 관리하는 기법 |
| **MCP** | Model Context Protocol, 외부 도구 연동 표준 |
| **StateGraph** | LangGraph의 상태 기반 그래프 정의 |
| **ReAct** | Reasoning + Acting, 추론과 행동을 반복하는 패턴 |
