# ai_company

> **AI 에이전트로 구성된 회사**
> Spec-Driven, Agent-Oriented AI Organization Prototype

---

## 1. 프로젝트 개요

**ai_company** 프로젝트는
AI를 단순한 도구가 아닌 **조직의 구성원(직원)**으로 정의하고,
AI 에이전트들이 역할을 나누어 협업하며 하나의 회사를 운영하는 모델을 실험하는 프로젝트입니다.

본 프로젝트의 핵심 가설:

> CEO(사용자)가 회사의 목표를 정의하면,
> **RM 에이전트가 프로젝트를 분해**하고,
> **Tool Agent가 필요한 도구를 검증**하며,
> **HR 에이전트가 전문가를 채용**하고,
> **Expert 에이전트들이 실제 업무를 수행**하여 목표를 달성할 수 있다.

---

## 2. 핵심 에이전트 구조 (v2)

```
                        CEO (사용자)
                            │
                            │ ① 목표 입력
                            ▼
                    ┌───────────────┐
                    │  RM 에이전트    │ ② 백로그 생성
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  CEO          │ ③ Tool 선택
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Tool 에이전트   │ ④ Tool 검증 + 대안 제시
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  HR 에이전트    │ ⑤ 에이전트 고용 + Tool 할당
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  RM 에이전트    │ ⑥ 태스크 할당
                    └───────┬───────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Expert Agent 1│   │ Expert Agent 2│   │ Expert Agent N│
│  (트렌드 리서처) │   │  (디자인 전문가) │   │  (이커머스 전문가)│
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  CEO          │ 결과 검토 및 다음 프로젝트
                    └───────────────┘
```

### 역할 분담

| 에이전트 | 역할 | 책임 |
|----------|------|------|
| **CEO** | 의사결정자 | 목표 정의, Tool 선택, 프로젝트 선택, 인터럽트 응답 |
| **RM** | 프로젝트 매니저 | 백로그 생성, 태스크 분해, 에이전트에 태스크 할당 |
| **Tool Agent** | 도구 검증자 | Tool 가용성 검증, 대안 제시, 마켓플레이스 검색 |
| **HR** | 에이전트 팩토리 | 전문가 에이전트 고용, Tool 배정 |
| **Expert** | 실무자 | 할당된 Tool로 태스크 수행, 결과 보고 |

---

## 3. 워크플로우 (v2 - Tool-Aware)

### 3.1 전체 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                        Phase 1: 계획 수립                        │
├─────────────────────────────────────────────────────────────────┤
│  ① CEO 목표 입력                                                │
│       ↓                                                         │
│  ② RM: 백로그 생성 (프로젝트/태스크)                            │
│       ↓                                                         │
│  ③ CEO: 각 태스크에 Tool 지정                                   │
│       ↓                                                         │
│  ④ Tool Agent: Tool 검증 + 대안 제시                            │
│       ↓                                                         │
│  ⑤ HR: 에이전트 고용 + Tool 할당                                │
│       ↓                                                         │
│  ⑥ RM: 에이전트에 태스크 할당                                   │
├─────────────────────────────────────────────────────────────────┤
│                        Phase 2: 실행                            │
├─────────────────────────────────────────────────────────────────┤
│  ⑦ CEO: 실행할 프로젝트 선택                                    │
│       ↓                                                         │
│  ⑧ Expert: 태스크 수행                                          │
│       ↓                                                         │
│  ⑨ 결과 보고                                                    │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 v1 → v2 핵심 변경사항

| 항목 | v1 (기존) | v2 (신규) |
|------|----------|----------|
| 순서 | HR → RM → Expert | RM(백로그) → **Tool** → HR → RM(할당) → Expert |
| Tool 선택 | 시스템 자동 | **CEO가 직접 지정** |
| Tool 검증 | 실행 시점 | **계획 단계 (사전 검증)** |
| 기본 에이전트 | CEO, HR, RM | CEO, RM, **Tool Agent**, HR |

### 3.3 각 단계 상세

| 단계 | 주체 | 설명 | 출력 |
|------|------|------|------|
| ① | CEO | 회사 목표/KPI/제약조건 입력 | `ceo_goal.json` |
| ② | RM | 목표를 프로젝트/태스크로 분해, Tool 카테고리 제안 | `backlog.json` |
| ③ | CEO | 각 태스크에 사용할 Tool 선택 | `tool_selections.json` |
| ④ | Tool Agent | Tool 가용성 검증, 대안 제시 | `tool_validations.json` |
| ⑤ | HR | 검증된 Tool 기반 Expert 에이전트 고용 | `hired_agents.json` |
| ⑥ | RM | 각 태스크에 적합한 에이전트 할당 | `task_assignments.json` |
| ⑦ | CEO | 실행할 프로젝트 선택 | - |
| ⑧ | Expert | 할당된 Tool로 태스크 실행 | `execution_log.json` |
| ⑨ | RM | 최종 결과 보고 | 결과 파일들 |

---

## 4. Tool 시스템

### 4.1 Tool 카테고리

| 타입 | 설명 | 예시 |
|------|------|------|
| **Built-in** | Claude Code 내장 도구 | WebSearch, WebFetch, Read, Write, Edit, Bash |
| **Skills** | 설치된 스킬 | /frontend-design, /mcp-builder |
| **MCP** | 외부 서비스 연동 | figma, rube, github |

### 4.2 Tool Agent의 검증 프로세스

```
CEO 요청 Tool
     │
     ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Built-in   │ ──► │   Skills    │ ──► │    MCP      │
│   검증      │     │   검증       │     │   검증       │
└─────────────┘     └─────────────┘     └─────────────┘
     │                   │                   │
     └───────────────────┴───────────────────┘
                         │
                    사용 불가 시
                         ▼
              ┌─────────────────────┐
              │  대안 검색           │
              │  - 유사 Tool 추천    │
              │  - 마켓플레이스 검색  │
              │  - 웹 검색          │
              └─────────────────────┘
```

### 4.3 외부 마켓플레이스 검색

Tool Agent는 로컬에 없는 Tool을 외부에서 검색할 수 있습니다:

| 소스 | URL | 신뢰도 |
|------|-----|--------|
| MCP.so | https://mcp.so/ | HIGH |
| anthropics/skills | https://github.com/anthropics/skills | HIGH |
| claude-market | https://github.com/claude-market/marketplace | HIGH |
| 웹 검색 | GitHub 등 | MEDIUM |

---

## 5. 실행 방법 (Claude Code)

### 5.1 시작하기

```bash
# 새 세션 시작
/ai-company init

# 현재 상태 확인
/ai-company status

# 상태 초기화
/ai-company reset
```

### 5.2 개별 에이전트 명령어

```bash
# CEO 명령어
/ceo-agent goal        # 목표 입력
/ceo-agent tools       # Tool 선택
/ceo-agent execute     # 프로젝트 선택
/ceo-agent status      # 상태 확인

# RM 명령어
/rm-agent backlog      # 백로그 생성
/rm-agent assign       # 태스크 할당
/rm-agent status       # 실행 상태

# Tool Agent 명령어
/tool-agent validate   # Tool 검증

# HR 명령어
/hr-agent hire         # 에이전트 고용
/hr-agent list         # 고용 목록

# Expert 명령어
/expert-agent execute <task_id>   # 태스크 실행
/expert-agent list                # 할당된 태스크
```

---

## 6. 디렉토리 구조

```
ai_company/
├── .claude/
│   └── skills/
│       ├── ai-company/           # 메인 오케스트레이터
│       ├── ceo-agent/            # CEO 역할
│       ├── rm-agent/             # RM 역할
│       ├── tool-agent/           # Tool 검증
│       ├── hr-agent/             # HR 역할
│       ├── expert-agent/         # Expert 역할
│       ├── frontend-design/      # 디자인 스킬
│       ├── mcp-builder/          # MCP 빌더
│       └── skill-creator/        # 스킬 생성기
│
├── company/
│   ├── state/                    # 상태 파일
│   │   ├── session.json          # 세션 정보
│   │   ├── ceo_goal.json         # CEO 목표
│   │   ├── backlog.json          # RM 백로그
│   │   ├── tool_selections.json  # CEO Tool 선택
│   │   ├── tool_validations.json # Tool 검증 결과
│   │   ├── hired_agents.json     # 고용된 에이전트
│   │   ├── task_assignments.json # 태스크 할당
│   │   └── execution_log.json    # 실행 로그
│   │
│   ├── outputs/                  # 실행 결과물
│   └── assets/                   # 리소스 파일
│
├── docs/
│   ├── specs/                    # 기술 스펙
│   │   └── tool-aware-workflow-v2.md
│   └── reports/                  # 보고서
│
└── README.md
```

---

## 7. 상태 파일 스키마

### session.json
```json
{
  "session_id": "ses_20250119_001",
  "phase": "execution",
  "created_at": "2025-01-19T10:00:00Z",
  "version": "v2"
}
```

### backlog.json (일부)
```json
{
  "backlog_id": "bl_20250119_001",
  "goal": "쿠팡 입점 및 월 매출 1000만원",
  "projects": [
    {
      "id": "proj-001",
      "name": "쿠팡 입점 준비",
      "tasks": [
        {
          "id": "task-001",
          "name": "시장 트렌드 조사",
          "type": "RESEARCH",
          "suggested_tool_categories": ["web_search"]
        }
      ]
    }
  ]
}
```

### hired_agents.json (일부)
```json
{
  "agents": [
    {
      "agent_id": "expert-001",
      "role_name": "트렌드 리서처",
      "assigned_tools": ["WebSearch", "WebFetch"],
      "assigned_tasks": ["task-001", "task-002"]
    }
  ]
}
```

---

## 8. 핵심 개념

| 개념 | 설명 |
|------|------|
| **Tool-Aware** | CEO가 Tool을 직접 선택하고, 사전에 검증받는 방식 |
| **Backlog** | RM이 목표를 분해한 프로젝트/태스크 목록 |
| **Tool Validation** | Tool Agent가 수행하는 가용성 검증 |
| **Interrupt** | Expert가 CEO에게 정보/승인을 요청하는 메커니즘 |
| **Phase** | 워크플로우의 현재 단계 (goal_input → execution → completed) |

---

## 9. 개발 철학

### Spec-Driven Development (SDD)

코드는 다음이 준비되기 전까지 작성되지 않습니다:

- 요구사항 명세
- 유저 스토리
- 기술 스펙
- 테스트 케이스

### 파일 기반 결과물

- 모든 산출물은 파일로 저장 (JSON, Markdown)
- Database 불필요
- Git으로 버전 관리

---

## 10. 차별점

- **Tool-Aware 워크플로우**: CEO가 직접 Tool을 선택하고 검증받음
- **사전 검증**: 실행 전에 모든 Tool 가용성 확인
- **마켓플레이스 연동**: 없는 Tool은 외부에서 검색 및 추천
- **동적 에이전트 생성**: 검증된 Tool 기반으로 전문가 자동 생성
- **Human-in-the-loop**: CEO의 의사결정이 핵심 지점에서 개입

---

## 11. 프로젝트 상태

**v2 구현 완료 (Claude Code 버전)**

- [x] ai-company 메인 스킬
- [x] CEO Agent 스킬
- [x] RM Agent 스킬
- [x] Tool Agent 스킬
- [x] HR Agent 스킬
- [x] Expert Agent 스킬
- [x] 상태 파일 구조
- [ ] Web API 버전 (예정)

---

## 12. 참고 문서

- `docs/specs/tool-aware-workflow-v2.md`: Tool-Aware 워크플로우 상세 스펙
- `docs/specs/agentic-ai-architecture.md`: Agentic AI 아키텍처 스펙
- `.claude/skills/*/SKILL.md`: 각 에이전트 스킬 문서

---

## 13. 안내

본 프로젝트는
AI가 인간을 대체하는 것이 아니라,
**인간과 AI의 협업 방식을 재정의하기 위한 실험적 프로젝트**입니다.
