# CLAUDE.md - AI Company Project Guide

이 파일은 Claude Code가 ai_company 프로젝트를 이해하고 작업하는 데 필요한 핵심 정보를 담고 있습니다.

## 프로젝트 개요

**ai_company**는 AI 에이전트들이 협업하여 회사처럼 운영되는 시스템입니다.

- CEO(사용자)가 목표를 입력하면
- RM 에이전트가 프로젝트/태스크로 분해하고
- Tool Agent가 필요한 도구를 검증하며
- HR 에이전트가 전문가를 채용하고
- Expert 에이전트들이 실제 업무를 수행합니다

### 핵심 원칙

1. **Tool-Aware 워크플로우**: CEO가 Tool을 직접 선택하고 사전 검증
2. **Rube MCP 기반 외부 서비스 통합**: 500+ 비즈니스 앱 연동으로 에이전트가 실제 외부 업무 수행
3. **Subagent 아키텍처**: 독립 컨텍스트에서 실행되는 에이전트
4. **Spec-Driven Development**: 코드 작성 전 요구사항/스펙 정의 필수
5. **파일 기반 결과물**: 모든 산출물은 JSON/Markdown으로 저장

---

## 디렉토리 구조

```
ai_company/
├── .mcp.json                    # 프로젝트 레벨 MCP 설정 (Rube 기본 포함)
├── .claude/
│   ├── agents/                  # Subagent 정의 (독립 컨텍스트 실행)
│   │   ├── ceo-agent.md         # CEO 역할 에이전트
│   │   ├── rm-agent.md          # RM(Resource Manager) 에이전트
│   │   ├── tool-agent.md        # Tool 검증 에이전트
│   │   ├── hr-agent.md          # HR 에이전트
│   │   └── expert-agent.md      # Expert 에이전트
│   │
│   ├── skills/                  # 유틸리티 스킬 (지침/도구)
│   │   ├── ai-company/          # 메인 오케스트레이터
│   │   ├── frontend-design/     # 웹 UI 디자인 스킬
│   │   ├── mcp-builder/         # MCP 서버 빌더
│   │   └── skill-creator/       # 스킬 생성기
│   │
│   └── CLAUDE.md                # 이 파일
│
├── company/
│   ├── state/                   # 상태 파일 (JSON)
│   │   ├── session.json         # 현재 세션 정보
│   │   ├── ceo_goal.json        # CEO 목표
│   │   ├── backlog.json         # RM 백로그
│   │   ├── tool_selections.json # CEO Tool 선택
│   │   ├── tool_validations.json# Tool 검증 결과
│   │   ├── hired_agents.json    # 고용된 에이전트
│   │   ├── task_assignments.json# 태스크 할당
│   │   └── execution_log.json   # 실행 로그
│   │
│   ├── outputs/                 # 실행 결과물
│   └── assets/                  # 리소스 파일
│
├── docs/
│   ├── specs/                   # 기술 스펙 문서
│   │   ├── tool-aware-workflow-v2.md   # Tool-Aware 워크플로우 설계
│   │   ├── agentic-ai-architecture.md  # Agentic AI 아키텍처
│   │   └── e2e-test-scenarios.md       # E2E 테스트 시나리오
│   └── reports/                 # 보고서
│
└── README.md
```

---

## Skill vs Subagent

| 구분 | Skill | Subagent |
|------|-------|----------|
| **위치** | `.claude/skills/` | `.claude/agents/` |
| **형태** | 지침서/프롬프트 | 독립 AI 엔티티 |
| **컨텍스트** | 메인 세션과 공유 | **별도 컨텍스트** |
| **실행** | Claude가 역할 연기 | 독립적으로 작동 |
| **용도** | 도구/작업방식 지침 | 복잡한 작업 위임 |

**본 프로젝트의 5개 핵심 에이전트는 Subagent로 구현되어 있습니다.**

---

## 핵심 에이전트 (Subagent)

| 에이전트 | 역할 | 도구 | 모델 |
|----------|------|------|------|
| **ceo-agent** | 목표 정의, Tool 선택, 의사결정 | Read, Write, WebSearch, Glob | sonnet |
| **rm-agent** | 백로그 생성, 태스크 분해/할당 | Read, Write, Glob, Grep | sonnet |
| **tool-agent** | Tool 가용성 검증, 대안 제시 | Read, Glob, Grep, Bash, WebSearch, WebFetch | haiku |
| **hr-agent** | 전문가 에이전트 고용, Tool 배정 | Read, Write, Glob | sonnet |
| **expert-agent** | 할당된 태스크 실행, 결과 보고 | Read, Write, Edit, Bash, WebSearch, WebFetch, Glob, Grep | sonnet |

---

## 워크플로우 (v2)

```
Phase 1: 계획 수립
──────────────────────────────────────────────────
① CEO 목표 입력     → ceo_goal.json
② RM 백로그 생성    → backlog.json
③ CEO Tool 선택     → tool_selections.json
④ Tool Agent 검증   → tool_validations.json
⑤ HR 에이전트 고용  → hired_agents.json
⑥ RM 태스크 할당    → task_assignments.json

Phase 2: 실행
──────────────────────────────────────────────────
⑦ CEO 프로젝트 선택
⑧ Expert 태스크 수행
⑨ 결과 보고         → execution_log.json
```

---

## 에이전트 호출 방법

### Subagent 호출 (Task tool을 통해)
```
# 명시적 호출
"ceo-agent를 사용해서 목표를 입력해줘"
"rm-agent로 백로그를 생성해줘"
"tool-agent로 Tool을 검증해줘"
"hr-agent로 에이전트를 고용해줘"
"expert-agent로 태스크를 실행해줘"

# Claude가 description을 보고 자동 위임할 수도 있음
```

### Skill 호출 (슬래시 명령어)
```bash
/ai-company           # 전체 시스템 오케스트레이션
/frontend-design      # 웹 UI 디자인
/mcp-builder          # MCP 서버 생성
```

---

## 사용 가능한 Tool 카테고리

### Built-in (항상 사용 가능)
- `WebSearch` - 웹 검색
- `WebFetch` - 웹 페이지 가져오기
- `Read/Write/Edit` - 파일 조작
- `Bash` - 명령어 실행
- `Glob/Grep` - 파일/텍스트 검색

### Skills (설치된 스킬)
- `/frontend-design` - 웹 UI 코드 생성
- `/mcp-builder` - MCP 서버 생성

### MCP (프로젝트 레벨 설정 - `.mcp.json`)
- **`rube` - 외부 서비스 통합 허브** (아래 상세 설명 참조) **[기본 설정됨]**
- `figma` - Figma 디자인 연동
- `github` - GitHub 연동

---

## Rube MCP - 외부 서비스 통합

### 개요

[Rube](https://rube.app)는 Composio 기반 MCP 서버로, **500개 이상의 외부 비즈니스 앱**을 AI 에이전트에 연결합니다. 본 프로젝트에서 **Expert 에이전트가 실제 외부 업무를 수행하기 위한 핵심 인프라**입니다.

### 왜 Rube가 핵심인가?

AI 에이전트가 "회사 직원"처럼 일하려면, 단순 검색/파일 작업을 넘어 **이메일 발송, 스프레드시트 작성, 이슈 생성, Slack 알림** 같은 외부 서비스 조작이 필수입니다. Rube는 이 모든 외부 서비스를 **하나의 MCP 엔드포인트**로 통합합니다.

```
Built-in 도구만으로는 부족한 영역:
──────────────────────────────────
✅ 정보 검색 (WebSearch, WebFetch)
✅ 파일 작업 (Read, Write, Edit)
✅ 코드 실행 (Bash)
❌ 이메일 발송, 캘린더 관리
❌ Slack/Discord 메시지
❌ Google Sheets/Notion 데이터 조작
❌ Jira/Linear 이슈 관리
❌ CRM/결제 시스템 연동

→ Rube MCP가 이 모든 ❌ 영역을 ✅로 전환
```

### 주요 지원 앱 카테고리

| 카테고리 | 앱 예시 | Expert 활용 시나리오 |
|----------|---------|---------------------|
| 커뮤니케이션 | Gmail, Slack, Discord | 리서치 결과 이메일 발송, 팀 채널 알림 |
| 프로젝트 관리 | Jira, Asana, Linear | 태스크 이슈 생성, 진행 상황 업데이트 |
| 문서/노트 | Notion, Google Docs | 분석 보고서 작성, 위키 페이지 생성 |
| 스프레드시트 | Google Sheets, Airtable | 경쟁사 분석 데이터 정리, 가격 모니터링 |
| CRM | HubSpot, Salesforce | 고객 데이터 관리, 리드 추적 |
| 코드 저장소 | GitHub, GitLab | PR 생성, 코드 리뷰 코멘트 |
| 결제/이커머스 | Stripe, Shopify | 주문 관리, 결제 데이터 조회 |

### 워크플로우에서의 역할

```
③ CEO Tool 선택 시:
   CEO: "리서치 결과를 Google Sheets에 정리하고, 완료되면 Slack으로 알려줘"
        → Tool Agent가 Rube를 통해 Sheets, Slack 사용 가능 여부 검증

⑤ HR 에이전트 고용 시:
   Rube 앱 접근 권한을 Expert에게 Tool로 할당

⑧ Expert 실행 시:
   Expert가 Rube MCP를 통해 외부 앱에 직접 액션 수행
```

### Tool Agent의 Rube 검증 로직

Tool Agent는 CEO가 선택한 외부 서비스가 Rube를 통해 사용 가능한지 검증합니다:

```
CEO 요청: "Gmail로 보고서 발송"
     │
     ▼
Tool Agent 검증:
  1. Rube MCP 서버 연결 상태 확인
  2. Rube Marketplace에서 Gmail 앱 연결 여부 확인
  3. 필요 권한(scope) 충족 여부 확인
     │
     ├── ✅ 사용 가능 → HR에게 Tool 정보 전달
     └── ❌ 미연결 → CEO에게 앱 연결 안내
         "rube.app/marketplace에서 Gmail을 연결해주세요"
```

### Rube 선택 근거 (대안 비교)

| 도구 | 앱 수 | 특징 | 선택하지 않은 이유 |
|------|-------|------|-------------------|
| **Rube (Composio)** | 500+ | Claude Code 네이티브, 노코드, 무료 | **채택** |
| ACI.dev | 500+ | 오픈소스, 자체 호스팅 | Claude Code MCP 네이티브 지원 부족 |
| Pipedream | 10,000+ | 앱 수 최대, 코드 작성 필요 | 에이전트 프롬프트 기반과 맞지 않음 |
| n8n | 400+ | 오픈소스, 비주얼 빌더 | MCP 지원 미흡, 비주얼 빌더 중심 |
| Arcade.dev | - | 보안 특화 | 앱 수 제한적 |

**채택 이유 요약:**
1. Claude Code `.mcp.json` 프로젝트 설정으로 즉시 사용 가능 (클론 후 바로 동작)
2. 자연어 기반 → Expert 에이전트가 코드 없이 외부 앱 조작
3. Composio 인프라 (SOC 2 Type II, OAuth 자동 관리, 토큰 격리)
4. 무료 + MCP 표준 기반 (향후 교체 용이)

### 프로젝트 레벨 설정 (`.mcp.json`)

Rube는 프로젝트 루트의 `.mcp.json`에 기본 설정되어 있습니다. 프로젝트를 클론하면 별도 설치 없이 사용 가능합니다.

```json
// .mcp.json (프로젝트 루트, git에 포함)
{
  "mcpServers": {
    "rube": {
      "type": "http",
      "url": "https://rube.app/mcp"
    }
  }
}
```

**최초 사용 시 필요한 작업:**
1. Claude Code에서 Rube MCP 서버 연결 승인
2. [rube.app/marketplace](https://rube.app/marketplace)에서 사용할 앱 OAuth 연결

> API Key/시크릿은 `.mcp.json`에 포함되지 않음. 인증은 Rube가 OAuth로 처리하며 토큰은 Composio에서 관리.

### 관련 상태 파일

Rube를 통한 외부 서비스 사용은 다음 상태 파일에 기록됩니다:
- `tool_selections.json` - CEO가 선택한 외부 서비스 (예: `["gmail_via_rube", "sheets_via_rube"]`)
- `tool_validations.json` - Rube를 통한 사용 가능 여부 검증 결과
- `hired_agents.json` - Expert에게 할당된 Rube 앱 목록
- `execution_log.json` - Rube를 통해 수행한 외부 액션 로그

---

## 상태 파일 스키마

### session.json
```json
{
  "session_id": "ses_YYYYMMDD_NNN",
  "phase": "goal_input | backlog_creation | tool_selection | tool_validation | hiring | assignment | ready_to_execute | executing | completed",
  "created_at": "ISO-8601"
}
```

### backlog.json (핵심 구조)
```json
{
  "backlog_id": "bl_YYYYMMDD_NNN",
  "goal": "CEO 목표 텍스트",
  "projects": [
    {
      "id": "proj-001",
      "name": "프로젝트명",
      "tasks": [
        {
          "id": "task-001",
          "name": "태스크명",
          "type": "RESEARCH | ACTION | DOCUMENT | APPROVAL",
          "suggested_tool_categories": ["web_search", "design"]
        }
      ]
    }
  ]
}
```

### hired_agents.json
```json
{
  "agents": [
    {
      "agent_id": "expert-001",
      "role_name": "역할명",
      "assigned_tools": ["WebSearch", "WebFetch"],
      "specialties": ["market_research"],
      "assigned_tasks": ["task-001"]
    }
  ]
}
```

---

## 개발 시 주의사항

### 1. 파일 수정 규칙
- 상태 파일(`company/state/*.json`)은 에이전트 실행을 통해서만 수정
- 스펙 문서(`docs/specs/`)는 구현 전 반드시 정의
- Subagent 정의는 YAML frontmatter에 `name`, `description`, `tools`, `model` 필수

### 2. 코드 스타일
- 한국어 주석/문서화 권장 (사용자 대상)
- JSON 파일은 한글 포함 시 UTF-8 인코딩 유지
- 날짜/시간은 ISO-8601 형식 (`YYYY-MM-DDTHH:mm:ssZ`)

### 3. 새 Subagent 추가 시
1. `.claude/agents/<agent-name>.md` 생성
2. YAML frontmatter에 `name`, `description`, `tools`, `model` 정의
3. 본문에 시스템 프롬프트 작성

### 4. 상태 관리
- `session.json`의 `phase`로 현재 단계 파악
- 각 단계 완료 시 다음 상태 파일 생성
- 오류 시 이전 상태 파일은 보존 (롤백 가능)

---

## 참고 문서

| 문서 | 경로 | 설명 |
|------|------|------|
| README | `README.md` | 프로젝트 전체 개요 |
| Tool-Aware 워크플로우 | `docs/specs/tool-aware-workflow-v2.md` | v2 워크플로우 상세 설계 |
| Agentic AI 아키텍처 | `docs/specs/agentic-ai-architecture.md` | 시스템 아키텍처 스펙 |
| E2E 테스트 시나리오 | `docs/specs/e2e-test-scenarios.md` | 통합 테스트 시나리오 |
| 구현 보고서 | `docs/reports/implementation-report.md` | 구현 결과 및 기술 스택 |

---

## 빠른 시작 예시

```
1. "ceo-agent로 목표를 입력해줘"     → 새 세션 시작, 목표 입력
2. "rm-agent로 백로그를 생성해줘"    → 프로젝트/태스크 분해
3. "ceo-agent로 Tool을 선택해줘"     → 각 태스크에 Tool 선택
4. "tool-agent로 검증해줘"           → Tool 사용 가능 여부 검증
5. "hr-agent로 에이전트를 고용해줘"  → 전문가 에이전트 생성
6. "rm-agent로 태스크를 할당해줘"    → 태스크 할당
7. "expert-agent로 태스크를 실행해줘" → 태스크 수행
```
