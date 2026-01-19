# AI Company 구현 결과 보고서

**작성일**: 2026-01-19
**버전**: 0.1.0

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [핵심 컴포넌트 상세](#3-핵심-컴포넌트-상세)
4. [데이터 흐름](#4-데이터-흐름)
5. [웹 UI 구현](#5-웹-ui-구현)
6. [실행 방법](#6-실행-방법)
7. [테스트 방법](#7-테스트-방법)
8. [기술 스택](#8-기술-스택)
9. [파일 구조](#9-파일-구조)
10. [향후 개선 사항](#10-향후-개선-사항)

---

## 1. 프로젝트 개요

### 1.1 목적

CEO가 목표를 입력하면 AI 에이전트들이 자율적으로 협업하여 목표를 달성하는 **Agentic AI 시스템**을 구현합니다.

### 1.2 AI Agent vs Agentic AI

| 구분 | AI Agent | Agentic AI |
|------|----------|------------|
| 판단 | 규칙 기반 | 목표 기반 자율 판단 |
| 행동 | 단일 태스크 | 다단계 추론 |
| 도구 | 고정 | 동적 선택 |
| 소통 | 단방향 | 양방향 (인간 개입) |
| 학습 | 없음 | 컨텍스트 기반 적응 |

### 1.3 핵심 특징

1. **동적 에이전트 생성**: HR이 목표에 맞는 전문가를 실시간 생성
2. **자율 태스크 분해**: RM이 목표를 실행 가능한 태스크로 분해
3. **Human-in-the-Loop**: CEO 승인/입력이 필요한 지점에서 자동 인터럽트
4. **도구 통합**: MCP 프로토콜을 통한 외부 도구 연동

---

## 2. 시스템 아키텍처

### 2.1 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                         CEO (사용자)                             │
│                    Web UI / CLI / Claude Code                   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                            │
│                   (REST API + WebSocket)                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LangGraph Orchestrator                       │
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌───────────┐  │
│  │  Init   │───▶│   HR    │───▶│    RM    │───▶│  Executor │  │
│  └─────────┘    └─────────┘    └──────────┘    └───────────┘  │
│       │              │              │               │          │
│       └──────────────┴──────────────┴───────────────┘          │
│                             │                                   │
│                             ▼                                   │
│                    ┌─────────────────┐                         │
│                    │  Human Input    │◀─── interrupt_before    │
│                    │    (CEO)        │                         │
│                    └─────────────────┘                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   Expert Agent   │ │   Expert Agent   │ │   Expert Agent   │
│  (이커머스 전문가)  │ │  (마케팅 전문가)   │ │  (개발자)        │
│                  │ │                  │ │                  │
│  ┌────────────┐  │ │  ┌────────────┐  │ │  ┌────────────┐  │
│  │  Tools     │  │ │  │  Tools     │  │ │  │  Tools     │  │
│  │  (MCP)     │  │ │  │  (MCP)     │  │ │  │  (MCP)     │  │
│  └────────────┘  │ │  └────────────┘  │ │  └────────────┘  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

### 2.2 LangGraph 상태 머신

```
                    ┌─────────────┐
                    │   START     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ initialize  │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
        ┌─────────┐              ┌─────────────┐
        │   hr    │◀─────────────│ human_input │
        └────┬────┘              └──────▲──────┘
             │                          │
             ▼                          │ (interrupt)
        ┌─────────┐                     │
        │   rm    │─────────────────────┤
        └────┬────┘                     │
             │                          │
             ▼                          │
        ┌──────────┐                    │
        │ executor │────────────────────┘
        └────┬─────┘
             │
             ▼
        ┌────────────┐
        │ completion │
        └─────┬──────┘
              │
              ▼
        ┌─────────┐
        │   END   │
        └─────────┘
```

---

## 3. 핵심 컴포넌트 상세

### 3.1 CompanyState (src/context/state.py)

전체 시스템의 상태를 관리하는 중앙 데이터 구조입니다.

```python
class CompanyState(BaseModel):
    # CEO 입력
    ceo_request: Optional[CEORequest]

    # 에이전트
    agents: dict[str, AgentDefinition]
    agent_requests: list[AgentRequest]  # HR에게 요청

    # 프로젝트/태스크
    projects: dict[str, Project]
    tasks: dict[str, Task]
    task_results: dict[str, TaskResult]

    # 실행 큐
    pending_tasks: list[str]
    executing_tasks: list[str]

    # Human-in-the-Loop
    pending_interrupts: list[HumanInterrupt]
    human_responses: list[HumanResponse]
    collected_inputs: dict[str, Any]

    # 실행 제어
    current_phase: str
    should_continue: bool
```

**상태 전이**:
```
initialization → hr_analysis → agents_created → planning
→ planning_complete → executing → completed
```

### 3.2 HR Agent (src/agents/hr.py)

CEO 목표를 분석하고 필요한 전문가 에이전트를 생성합니다.

**동작 흐름**:
1. CEO 요청 분석 (`_analyze_goal`)
2. 필요한 전문가 역할 도출 (LLM 추론)
3. 추가 정보 필요 시 → 인터럽트 생성
4. 에이전트 정의 생성 (`AgentDefinition`)
5. 시스템 프롬프트 자동 생성 (`to_system_prompt`)

**출력 스키마**:
```python
class HRAnalysis(BaseModel):
    analysis: str                         # 분석 결과
    proposed_agents: list[AgentProposal]  # 제안 에이전트
    missing_information: list[str]        # 추가 필요 정보
```

### 3.3 RM Agent (src/agents/rm.py)

프로젝트/태스크를 계획하고 실행을 관리하는 슈퍼바이저입니다.

**동작 흐름**:
1. 목표와 에이전트 현황 분석
2. 프로젝트 분해 (LLM 추론)
3. 태스크 분해 (실행 가능한 단위)
4. 태스크별 필수 요소 정의:
   - `required_inputs`: CEO에게 받을 정보
   - `tools`: 필요한 외부 도구
   - `approval_points`: CEO 승인 필요 지점
   - `execution_steps`: 구체적 실행 단계
5. 태스크를 적합한 에이전트에 할당
6. 의존성 기반 실행 순서 결정

**태스크 타입**:
- `ACTION`: 외부 시스템 변경 (계정 생성, 결제 등)
- `DOCUMENT`: 문서/보고서 작성
- `RESEARCH`: 정보 수집 및 분석
- `APPROVAL`: CEO 의사결정 필요

### 3.4 Expert Factory (src/agents/expert_factory.py)

동적으로 전문가 에이전트를 생성하고 관리합니다.

**동작 흐름**:
1. `AgentDefinition`으로부터 `ExpertAgent` 생성
2. 도구가 있으면 `create_react_agent`로 ReAct 에이전트 생성
3. 태스크 실행 시:
   ```python
   async def execute_task(task, state):
       # 1. 입력 확인
       missing = task.has_missing_inputs(state.collected_inputs)
       if missing:
           return (INPUT_REQUIRED, interrupt)

       # 2. 승인 확인
       if task.has_approval_before_execution():
           if not approved:
               return (APPROVAL_WAIT, interrupt)

       # 3. 도구 확인
       missing_tools = check_tool_availability(task, state)
       if missing_tools:
           return (AWAITING_TOOL, interrupt)

       # 4. 실행
       result = await execute_steps(task, state)
       return (COMPLETED, result)
   ```

### 3.5 Tool Registry (src/tools/registry.py)

모든 도구를 중앙에서 관리합니다.

```python
class ToolRegistry:
    def register_tool(tool_id, name, func, ...)
    def get_tool(tool_id) -> BaseTool
    def get_tools_by_category(category) -> list[BaseTool]
    def get_available_tools() -> list[BaseTool]
    def mark_connected(tool_id)
```

### 3.6 MCP Adapter (src/tools/mcp_adapter.py)

Model Context Protocol로 외부 도구를 연동합니다.

```python
class MCPAdapter:
    def register_server(config: MCPServerConfig)
    async def connect_server(server_name) -> bool
    async def call_tool(server, tool_name, arguments) -> Any
```

**지원 서버**:
- Figma: 디자인 파일 접근
- GitHub: 저장소 관리
- Slack: 메시지 전송

---

## 4. 데이터 흐름

### 4.1 CEO 목표 입력 → 에이전트 생성

```
CEO 목표 입력
     │
     ▼
┌─────────────────────────────────────┐
│           CompanyState              │
│  ceo_request: {                     │
│    goal: "쿠팡 입점...",            │
│    kpis: [...],                     │
│    constraints: [...]               │
│  }                                  │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│            HR Agent                 │
│                                     │
│  1. 목표 분석 (LLM)                  │
│  2. 필요 역할 도출                   │
│  3. AgentDefinition 생성            │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│           CompanyState              │
│  agents: {                          │
│    "expert-001": {                  │
│      role_name: "이커머스 전문가",   │
│      specialties: [...],            │
│      tools: ["coupang_api"]         │
│    },                               │
│    ...                              │
│  }                                  │
└─────────────────────────────────────┘
```

### 4.2 태스크 실행 → 인터럽트 처리

```
RM: 태스크 할당
     │
     ▼
Expert: 태스크 실행 시도
     │
     ├─── 입력 부족? ─────────────────┐
     │                                │
     ▼                                ▼
┌──────────────┐            ┌─────────────────────────┐
│ 실행 계속    │            │     HumanInterrupt      │
└──────────────┘            │  type: info_request     │
                            │  message: "정보 필요"    │
                            │  required_inputs: [     │
                            │    {key: "biz_num"...}  │
                            │  ]                      │
                            └───────────┬─────────────┘
                                        │
                                        ▼
                            ┌─────────────────────────┐
                            │      CEO 응답           │
                            │  (Web UI / CLI)         │
                            └───────────┬─────────────┘
                                        │
                                        ▼
                            ┌─────────────────────────┐
                            │     HumanResponse       │
                            │  inputs: {              │
                            │    biz_num: "123-..."   │
                            │  }                      │
                            └───────────┬─────────────┘
                                        │
                                        ▼
                            ┌─────────────────────────┐
                            │  graph.resume(response) │
                            │    → 태스크 실행 재개    │
                            └─────────────────────────┘
```

---

## 5. 웹 UI 구현

### 5.1 구조

```
frontend/
├── src/
│   ├── components/
│   │   ├── flow/              # n8n 스타일 노드 그래프
│   │   │   ├── AgentNode.tsx  # 에이전트 노드
│   │   │   ├── TaskNode.tsx   # 태스크 노드
│   │   │   └── WorkflowCanvas.tsx
│   │   ├── layout/
│   │   │   └── Layout.tsx     # 사이드바 + 헤더
│   │   └── ui/                # 공통 UI 컴포넌트
│   ├── pages/
│   │   ├── Dashboard.tsx      # 대시보드
│   │   ├── Setup.tsx          # 회사 설정
│   │   ├── Workflow.tsx       # 워크플로우 시각화
│   │   └── Chat.tsx           # 에이전트 채팅
│   └── store/
│       └── useStore.ts        # Zustand 상태 관리
```

### 5.2 페이지별 기능

| 페이지 | 기능 |
|--------|------|
| Dashboard | 통계, 현황, 대기 액션 표시 |
| Setup | CEO 목표/KPI/제약조건 입력 |
| Workflow | React Flow로 에이전트-태스크 그래프 시각화 |
| Chat | 에이전트와 대화, 인터럽트 응답 |

### 5.3 API 연동

```typescript
// Store Actions
createSession()      // POST /api/sessions
setupCompany(req)    // POST /api/sessions/{id}/setup
respondToInterrupt() // POST /api/sessions/{id}/respond
fetchGraph()         // GET /api/sessions/{id}/graph

// WebSocket
ws://{host}/ws/{session_id}
- 실시간 상태 업데이트
- 채팅 메시지
```

---

## 6. 실행 방법

### 6.1 환경 설정

```bash
# 1. 저장소 클론
git clone <repository>
cd ai_company

# 2. 환경 설정 (Python + Node.js)
./scripts/setup.sh

# 3. .env 파일 설정
cp .env.example .env
# ANTHROPIC_API_KEY 입력 (console.anthropic.com에서 발급)
```

### 6.2 개발 서버 실행

```bash
# 방법 1: 스크립트 사용
./scripts/run_dev.sh

# 방법 2: 수동 실행
# 터미널 1 - Backend
python -m uvicorn src.api.server:app --reload --port 8000

# 터미널 2 - Frontend
cd frontend && npm run dev
```

### 6.3 접속

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 7. 테스트 방법

### 7.1 API 키 없이 테스트 (Claude Code)

Claude Code만으로 시스템 로직을 시뮬레이션할 수 있습니다.

```bash
# Claude Code에서 실행
/ai-company run
```

**스킬 목록**:
| 스킬 | 설명 |
|------|------|
| `/ai-company` | 전체 시스템 시뮬레이션 |
| `/ceo` | CEO 역할 수행 |
| `/hr` | HR Agent 역할 수행 |
| `/rm` | RM Agent 역할 수행 |
| `/expert <id>` | 전문가 에이전트 역할 수행 |

**시뮬레이션 흐름**:
```
/ai-company init
    ↓
/ceo start → 목표 입력
    ↓
/hr analyze → 에이전트 제안
/hr create → 에이전트 생성
    ↓
/rm plan → 프로젝트/태스크 계획
/rm assign → 에이전트 할당
    ↓
/expert <id> execute <task_id> → 태스크 실행
    ↓
(인터럽트 발생 시)
/ceo approve/input → 응답
    ↓
/ai-company status → 상태 확인
```

### 7.2 pytest 테스트

```bash
# 전체 테스트
pytest tests/ -v

# 특정 테스트
pytest tests/test_state.py -v
pytest tests/test_e2e.py -v

# 커버리지
pytest tests/ --cov=src --cov-report=html
```

### 7.3 수동 API 테스트

```bash
# 세션 생성
curl -X POST http://localhost:8000/api/sessions

# 회사 설정
curl -X POST http://localhost:8000/api/sessions/{session_id}/setup \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "쿠팡 입점하여 월 매출 1000만원 달성",
    "kpis": ["월 매출 1000만원"],
    "constraints": ["초기 투자 500만원 이내"]
  }'

# 상태 확인
curl http://localhost:8000/api/sessions/{session_id}

# 에이전트 목록
curl http://localhost:8000/api/sessions/{session_id}/agents

# 태스크 목록
curl http://localhost:8000/api/sessions/{session_id}/tasks
```

---

## 8. 기술 스택

### 8.1 Backend

| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.11+ | 런타임 |
| LangGraph | 0.2.61+ | 에이전트 오케스트레이션 |
| LangChain | 0.3.14+ | LLM 인터페이스 |
| Claude API | - | LLM (Anthropic) |
| FastAPI | 0.109+ | REST API |
| Pydantic | 2.10+ | 데이터 검증 |
| SQLite | - | 체크포인팅 |
| ChromaDB | 0.5+ | 벡터 저장소 |

### 8.2 Frontend

| 기술 | 버전 | 용도 |
|------|------|------|
| React | 18.2+ | UI 프레임워크 |
| TypeScript | 5.3+ | 타입 안전성 |
| Vite | 5.0+ | 빌드 도구 |
| React Flow | 12.0+ | 노드 그래프 시각화 |
| Tailwind CSS | 3.4+ | 스타일링 |
| Zustand | 4.5+ | 상태 관리 |

---

## 9. 파일 구조

```
ai_company/
├── .claude/
│   └── skills/              # Claude Code 스킬
│       ├── ai-company.md    # 통합 시뮬레이션
│       ├── ceo-agent.md
│       ├── hr-agent.md
│       ├── rm-agent.md
│       └── expert-agent.md
│
├── company/
│   ├── state/               # 시뮬레이션 상태 파일
│   └── agents/              # 에이전트 시스템 프롬프트
│
├── src/
│   ├── __init__.py
│   ├── config.py            # 환경 설정
│   ├── main.py              # 메인 엔트리포인트
│   ├── cli.py               # CLI 인터페이스
│   │
│   ├── api/                 # FastAPI 백엔드
│   │   ├── __init__.py
│   │   └── server.py
│   │
│   ├── schemas/             # Pydantic 스키마
│   │   ├── task.py          # Task, RequiredInput, ...
│   │   ├── agent.py         # AgentDefinition, ...
│   │   └── project.py       # Project, ExecutionGraph
│   │
│   ├── context/             # 상태 관리
│   │   ├── state.py         # CompanyState
│   │   ├── memory.py        # ChromaDB 메모리
│   │   └── checkpointer.py  # SQLite 체크포인팅
│   │
│   ├── agents/              # 에이전트 구현
│   │   ├── base.py          # BaseAgent
│   │   ├── hr.py            # HRAgent
│   │   ├── rm.py            # RMAgent
│   │   └── expert_factory.py # ExpertFactory
│   │
│   ├── graph/               # LangGraph
│   │   ├── company_graph.py # 메인 그래프
│   │   ├── nodes.py         # 노드 함수
│   │   └── edges.py         # 라우팅 조건
│   │
│   ├── tools/               # 도구 관리
│   │   ├── registry.py      # ToolRegistry
│   │   └── mcp_adapter.py   # MCP 어댑터
│   │
│   └── communication/       # 통신
│       ├── a2a_protocol.py  # A2A 프로토콜
│       └── human_interface.py # CEO 인터페이스
│
├── frontend/                # React 프론트엔드
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   │   ├── flow/        # React Flow
│   │   │   ├── layout/
│   │   │   └── ui/
│   │   ├── pages/
│   │   ├── store/
│   │   └── types/
│   └── ...
│
├── tests/                   # 테스트
│   ├── conftest.py
│   ├── test_state.py
│   ├── test_schemas.py
│   ├── test_tools.py
│   ├── test_memory.py
│   └── test_e2e.py
│
├── scripts/
│   ├── setup.sh             # 환경 설정
│   └── run_dev.sh           # 개발 서버 실행
│
├── docs/
│   ├── specs/
│   │   └── agentic-ai-architecture.md  # 설계 문서
│   └── reports/
│       └── implementation-report.md     # 구현 보고서 (이 문서)
│
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 10. 향후 개선 사항

### 10.1 단기 (1-2주)

- [ ] 실제 MCP 서버 연결 구현
- [ ] 에러 핸들링 강화
- [ ] 로깅 및 모니터링 추가
- [ ] 웹 UI 반응형 개선

### 10.2 중기 (1-2개월)

- [ ] 다중 사용자 지원 (인증/인가)
- [ ] 에이전트 학습 (피드백 반영)
- [ ] 더 많은 MCP 도구 통합
- [ ] 성능 최적화 (병렬 실행)

### 10.3 장기

- [ ] 에이전트 자율 협업 강화
- [ ] 멀티모달 지원 (이미지, 문서)
- [ ] 분산 실행 환경
- [ ] A2A 프로토콜 완전 구현

---

## 부록: API 키 발급 안내

### Anthropic API

1. https://console.anthropic.com 접속
2. 계정 생성 또는 로그인
3. API Keys 메뉴에서 키 생성
4. `.env` 파일에 `ANTHROPIC_API_KEY=sk-...` 추가

**요금 (2024년 기준)**:
- Claude 3.5 Sonnet: $3 / 1M input tokens, $15 / 1M output tokens
- 사용량 기반 과금 (구독과 별개)

### MCP 토큰 (선택)

- **Figma**: figma.com > Settings > Personal Access Tokens
- **GitHub**: github.com > Settings > Developer settings > Personal access tokens
- **Slack**: api.slack.com에서 App 생성 후 Bot Token 발급
