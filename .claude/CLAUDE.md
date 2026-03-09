# CLAUDE.md - AI Company Project Guide

이 파일은 Claude Code가 ai_company 프로젝트를 이해하고 작업하는 데 필요한 핵심 정보를 담고 있습니다.

## 프로젝트 개요

**ai_company**는 AI 에이전트들이 협업하여 회사처럼 운영되는 시스템입니다.

- CEO(사용자)가 목표를 입력하면
- RM 에이전트가 프로젝트/태스크로 분해하고
- Tool Agent가 **사용 가능한 Tool 인벤토리를 생성**하며
- HR 에이전트가 **역량 기반으로** 전문가를 채용하고
- CEO가 **프로젝트 실행 전 태스크별로 Tool/레퍼런스/지시사항을 검토·승인**한 뒤
- Expert 에이전트들이 **승인된 계획에 따라** 실제 업무를 수행합니다

### 핵심 원칙

1. **Interactive Execution**: 태스크 실행 전 CEO가 "누가, 어떤 Tool로, 어떻게"를 검토·승인
2. **Task-Level Approval**: 태스크 단위로 Tool 변경, 레퍼런스 추가, 지시사항 부여 가능
3. **Just-In-Time Reference**: 레퍼런스는 실행 직전에 해당 태스크에 대해서만 수집
4. **Analyze Once, Use Everywhere**: 레퍼런스를 1번만 깊게 분석하고 결과를 공유
5. **Auto-Parallel Execution**: 의존성 그래프 기반 자동 병렬 실행
6. **Rube MCP 기반 외부 서비스 통합**: 500+ 비즈니스 앱 연동
7. **Subagent 아키텍처**: 독립 컨텍스트에서 실행되는 에이전트
8. **Spec-Driven Development**: 코드 작성 전 요구사항/스펙 정의 필수
9. **파일 기반 결과물**: 모든 산출물은 JSON/Markdown으로 저장

---

## 디렉토리 구조

```
ai_company/
├── .mcp.json                    # 프로젝트 레벨 MCP 설정 (Rube 기본 포함)
├── .claude/
│   ├── agents/                  # Subagent 정의 (독립 컨텍스트 실행)
│   │   ├── ceo-agent.md         # CEO 역할 에이전트
│   │   ├── rm-agent.md          # RM(Resource Manager) 에이전트
│   │   ├── tool-agent.md        # Tool 컨설턴트 에이전트
│   │   ├── hr-agent.md          # HR 에이전트
│   │   ├── expert-agent.md      # Expert 에이전트 (기본 템플릿)
│   │   └── expert-00N.md        # HR이 생성한 전문가 에이전트 파일
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
│   │   ├── backlog.json         # RM 백로그 (dependency_graph 포함)
│   │   ├── tool_inventory.json  # Tool Agent 인벤토리 (v4)
│   │   ├── hired_agents.json    # 고용된 에이전트 (역량 기반)
│   │   ├── task_assignments.json# 태스크 할당 + CEO 승인/레퍼런스/지시사항
│   │   └── execution_log.json   # 실행 로그
│   │
│   ├── outputs/                 # 실행 결과물
│   └── assets/                  # 리소스 파일
│
├── docs/
│   ├── specs/                   # 기술 스펙 문서
│   │   ├── interactive-execution-workflow-v4.md  # v4 워크플로우 설계 (최신)
│   │   ├── reference-driven-workflow-v3.md       # v3 워크플로우 (레거시)
│   │   ├── tool-aware-workflow-v2.md             # v2 워크플로우 (레거시)
│   │   ├── agentic-ai-architecture.md            # 시스템 아키텍처 스펙
│   │   └── e2e-test-scenarios.md                 # E2E 테스트 시나리오
│   └── reports/                 # 보고서
│
└── README.md
```

### v3 → v4 상태 파일 변경

| v3 | v4 | 비고 |
|----|----|------|
| `task_references.json` | **제거** | 레퍼런스는 `task_assignments.json` 내 per-task 저장 |
| `tool_recommendations.json` | `tool_inventory.json` | 역할 변경: 추천 → 인벤토리 |
| `tool_selections.json` | **제거** | CEO 승인은 Phase 2 Task Briefing에서 per-task 처리 |

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
| **ceo-agent** | 목표 정의, 프로젝트 선택, **태스크별 Briefing 승인/수정** | Read, Write, WebSearch, Glob | sonnet |
| **rm-agent** | 백로그 생성 (**dependency_graph 포함**), 태스크 할당 | Read, Write, Glob, Grep | sonnet |
| **tool-agent** | **Phase 1: Tool 인벤토리 생성** / **Phase 2: 레퍼런스 분석 + Tool 조정** | Read, Glob, Grep, Bash, WebSearch, WebFetch | sonnet |
| **hr-agent** | **Tool 인벤토리 참고하여 역량 기반** 전문가 고용 + agent 파일 생성 | Read, Write, Glob | sonnet |
| **expert-agent** | **analyzed_content + ceo_instructions** 기반 태스크 실행 | Read, Write, Edit, Bash, WebSearch, WebFetch, Glob, Grep | sonnet |
| **qa-agent** | **Expert 결과물 품질 검증** (0~100점), 70점 미만 시 반려+피드백 → 재시도 (최대 3회). ACTION_VISUAL 태스크는 `docs/design-system.md` 기준으로 디자인 품질 검증 | Read, Glob, Grep, Bash, WebFetch | sonnet |

---

## 워크플로우 (v4 - Interactive Execution)

```
Phase 1: 계획 수립
──────────────────────────────────────────────────
① CEO 목표 입력              → ceo_goal.json
② RM 백로그 생성             → backlog.json (dependency_graph 포함)
③ Tool Agent 인벤토리 생성   → tool_inventory.json
④ HR 에이전트 고용           → hired_agents.json (역량 기반)
⑤ RM 태스크 할당             → task_assignments.json

Phase 2: 프로젝트 실행 (프로젝트 단위 반복)
──────────────────────────────────────────────────
⑥ CEO 프로젝트 선택
⑦ 태스크별 실행 계획 보고 (Task Briefing)
⑧ CEO 태스크별 승인/수정/레퍼런스 추가
⑨ (필요시) Tool Agent 레퍼런스 분석 + Tool 조정
⑩ 태스크 실행 (dependency_graph 기반 자동 병렬)
⑪ 결과 보고                 → execution_log.json
⑫ 다음 프로젝트 → ⑥으로
```

### Phase 1 흐름 (순차)

```
① CEO 목표 입력
     ↓
② RM 백로그 생성 (dependency_graph 포함)
     ↓
③ Tool Agent: Tool 인벤토리 생성 (3-tier 검증 + 웹 검색 + 마켓플레이스)
     ↓
④ HR: 인벤토리 참고하여 역량 기반 Expert 생성
     ↓
⑤ RM: Expert 할당 + 기본 Tool 배정
```

> ③→④는 순차 실행. HR이 에이전트를 만들 때 어떤 Tool이 사용 가능한지 알아야 실현 가능한 역량을 부여할 수 있기 때문.

### Phase 2 흐름: Task Briefing Loop (v4 핵심)

```
⑥ CEO가 프로젝트 선택
     ↓
⑦ 태스크별 실행 계획 보고:
   "task-010: 밈 콘텐츠 제작"
   "담당: 디자이너 에이전트"
   "Tool: Gemini API로 이미지 생성"
   "괜찮으신가요? 레퍼런스나 변경사항 있으시면 말씀해주세요"
     ↓
⑧ CEO 개입 (태스크별):
   ├─ 승인: "OK 그대로 진행해"
   ├─ Tool 변경: "Imgflip API 써줘"
   ├─ 레퍼런스 추가: "이 이미지 참고해" (파일/URL/메모)
   ├─ 지시사항: "PNG로 출력, AI 티 내지 마"
   └─ 일괄 승인: "전부 OK"
     ↓
⑨ (레퍼런스/Tool 변경 시만) Tool Agent 분석:
   레퍼런스 → analyzed_content 저장
   태스크 description 구체화 (enriched_description)
   방향성 도출 (direction)
     ↓
⑩ 실행 (dependency_graph 기반 자동 병렬)
     ↓
⑪ 결과 보고
```

### v3 → v4 핵심 변경점

| 항목 | v3 | v4 |
|------|----|----|
| **패러다임** | Reference-Driven (일괄 레퍼런스) | **Interactive Execution (태스크별 승인)** |
| **레퍼런스 수집 시점** | Phase 1 (전체 태스크 한번에) | **Phase 2 (실행 직전, 태스크별)** |
| **Tool 확정 시점** | Phase 1 (1회 확정) | **Phase 2 (태스크별, 동적)** |
| **CEO 개입 시점** | 레퍼런스 1회 + 승인 1회 | **태스크별 Briefing + 개입** |
| **실행 투명성** | 실행 후 결과만 확인 | **실행 전 계획 확인 → 승인 → 실행** |
| **병렬 실행** | 수동 판단 | **dependency_graph 기반 자동** |
| **HR 에이전트** | Tool 종속적 | **역량 기반 (feasible_tools)** |
| **Tool Agent 역할** | 레퍼런스 분석 + Tool 추천 | **인벤토리 생성 + Just-In-Time 분석** |

---

## 에이전트 호출 방법

### Subagent 호출 (Task tool을 통해)
```
# Phase 1: 계획 수립
"ceo-agent로 목표를 입력해줘"
"rm-agent로 백로그를 생성해줘"
"tool-agent로 Tool 인벤토리를 생성해줘"
"hr-agent로 에이전트를 고용해줘"
"rm-agent로 태스크를 할당해줘"

# Phase 2: 프로젝트 실행
(CEO가 프로젝트 선택 → Task Briefing → CEO 승인/수정)
"tool-agent로 레퍼런스 분석해줘"          # CEO가 레퍼런스 첨부 시
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

## Task Briefing 시스템 (v4 핵심)

### Task Briefing이란?

CEO가 프로젝트를 선택하면, 각 태스크별로 **"누가, 어떤 Tool로, 어떻게 할 건지"** 실행 계획을 보고받고 승인/수정하는 단계입니다. 이를 통해 CEO는 실행 전에 계획을 검토하고 개입할 수 있습니다.

### Briefing 인터페이스 예시

```
══════════════════════════════════════════════════════════════
  프로젝트 4: 초기 콘텐츠 제작 및 론칭
  실행 계획 (3 tasks)
══════════════════════════════════════════════════════════════

  [1] Task 010: 론칭용 밈 콘텐츠 30개 제작
      담당: 밈 콘텐츠 제작 전문가 (expert-004)
      Tool: Gemini 이미지 생성 + Imgflip API + PIL
      출력: PNG 30개 (1080x1080)

  [2] Task 011: 캡션 및 해시태그 작성
      담당: 밈 콘텐츠 제작 전문가 (expert-004)
      Tool: Read + Write
      출력: Markdown 문서

──────────────────────────────────────────────────────────────
  수정하실 태스크가 있으면 번호를 말씀해주세요.
  전체 OK면 "승인" 또는 "실행"
══════════════════════════════════════════════════════════════
```

### CEO 개입 유형

| 유형 | 예시 | 결과 |
|------|------|------|
| **승인** | "OK", "전부 승인" | 모든 태스크 승인 → 실행 |
| **Tool 변경** | "task-010은 Imgflip API 써줘" | ceo_tools 업데이트 |
| **레퍼런스 추가** | "이 이미지 참고해" (파일/URL/메모) | Tool Agent 분석 → analyzed_content 저장 |
| **지시사항** | "PNG 출력, AI 티 내지 마" | ceo_instructions 업데이트 |
| **일괄 승인** | "전부 OK" | 모든 태스크 한번에 승인 |

---

## 레퍼런스 시스템 (v4 - Just-In-Time)

### 레퍼런스란?

CEO가 **Task Briefing 시 태스크별로** 첨부하는 참고 자료입니다. Expert가 "어떤 결과물을 만들지" 구체적으로 파악할 수 있게 합니다.

v3에서는 Phase 1에서 모든 태스크에 일괄 수집했지만, v4에서는 **실행 직전에 해당 태스크에 대해서만** 수집합니다.

### 레퍼런스 타입

| 타입 | 형태 | 예시 | 용도 |
|------|------|------|------|
| `url` | 웹 주소 | 경쟁사 사이트, 참고 디자인 | "이런 느낌으로" |
| `image` | 이미지 파일 경로 | 목업, 스크린샷, 로고 | "이렇게 생긴 것" |
| `file` | 로컬 파일 경로 | 기존 보고서, 템플릿, 데이터셋 | "이 포맷 따라서" |
| `note` | 텍스트 메모 | 스타일 가이드, 톤앤매너, 브랜드 컬러 | "이런 방향으로" |

### 레퍼런스 의도 (intent)

| Intent | 의미 |
|--------|------|
| `style` | "이런 스타일/느낌으로 만들어줘" |
| `content` | "이 내용을 참고해서 작성해줘" |
| `template` | "이 형식/구조를 따라줘" |
| `data` | "이 데이터를 활용해줘" |
| `competitor` | "이 경쟁사를 분석해줘" |

### 레퍼런스 분석 흐름 (Analyze Once, Use Everywhere)

CEO가 Task Briefing에서 레퍼런스를 첨부하면, Tool Agent가 **1번만 깊게 분석**하고 `analyzed_content`에 저장합니다. Expert는 이 분석 결과를 **읽기만** 하고 레퍼런스를 다시 접속/분석하지 않습니다.

```
⑧ CEO: Task Briefing에서 레퍼런스 첨부
     │
     ▼
⑨ Tool Agent 깊은 분석 (1번만):
  1. 레퍼런스 타입 + 의도 분석
  2. URL → WebFetch로 실제 내용 확인
  3. analyzed_content에 분석 결과 저장 (스타일, 구조, 핵심 발견)
  4. direction(방향성) 도출
  5. enriched_description(상세 태스크 설명) 생성
  6. 필요 Tool 조정 + 가용성 검증
     │
     ▼
task_assignments.json 업데이트
     │
     ▼
⑩ Expert: analyzed_content 읽기 → 바로 작업 수행 (재분석 불필요)
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
- `/pollinations-ai` - 무료 이미지 생성 (API 키 불필요, flux/turbo/stable-diffusion 모델)
- `/image-generation-mcp` - Gemini MCP 기반 고품질 이미지 생성 (gemini-cli 필요)
- `/ecosystem` - Claude Code 생태계 대시보드 (stats/trends)
- `/vibeindex` - 프로젝트 분석 + 스킬/MCP/플러그인 추천
- `/rising` - GitHub 트렌딩 Claude Code 리소스 탐색
- `/new` - Vibe Index 최신 리소스 탐색
- `/versus` - Claude Code 리소스 비교

### MCP (프로젝트 레벨 설정 - `.mcp.json`)
- **`rube` - 외부 서비스 통합 허브** (아래 상세 설명 참조) **[기본 설정됨]**
- `figma` - Figma 디자인 연동
- `github` - GitHub 연동

---

## Rube MCP - 외부 서비스 통합

### 개요

[Rube](https://rube.app)는 Composio 기반 MCP 서버로, **500개 이상의 외부 비즈니스 앱**을 AI 에이전트에 연결합니다. 본 프로젝트에서 **Expert 에이전트가 실제 외부 업무를 수행하기 위한 핵심 인프라**입니다.

### 왜 Rube가 핵심인가?

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
| 이미지 생성 | Gemini, Canva | 밈 이미지, 디자인 에셋 생성 |
| SNS | Instagram, Twitter | 콘텐츠 업로드, 계정 관리 |
| 코드 저장소 | GitHub, GitLab | PR 생성, 코드 리뷰 코멘트 |

### 워크플로우에서의 역할 (v4)

```
③ Tool Agent 인벤토리 생성 시:
   RUBE_SEARCH_TOOLS로 필요 카테고리별 Tool 검색
   RUBE_MANAGE_CONNECTIONS로 연결 상태 확인
   → 인벤토리에 사용 가능 Tool + 연결 상태 기록

④ HR 에이전트 고용 시:
   인벤토리에서 Rube 앱 확인 → 역량에 반영
   예: Instagram active → "SNS 운영" 역량 부여

⑧ Task Briefing 시:
   CEO가 Rube 앱 Tool 사용을 지시 가능
   "Gemini로 이미지 생성해줘" → ceo_tools에 추가

⑩ Expert 실행 시:
   Expert가 Rube MCP를 통해 외부 앱에 직접 액션 수행
```

### Tool Agent의 Rube 검증 로직

Tool Agent는 인벤토리 생성 시 Rube를 통한 가용성을 검증합니다:

```
Tool Agent: "이미지 생성, Instagram 업로드 필요"
     │
     ▼
Rube 검증:
  1. RUBE_SEARCH_TOOLS로 관련 Tool 검색
  2. RUBE_MANAGE_CONNECTIONS로 연결 상태 확인
     │
     ├── ✅ ACTIVE → 인벤토리에 "active"로 등록
     └── ❌ 미연결 → "not_connected" + CEO 안내
         "rube.app/marketplace에서 연결해주세요"
```

### 프로젝트 레벨 설정 (`.mcp.json`)

```json
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

### 관련 상태 파일

- `tool_inventory.json` - Tool Agent가 Rube 앱 인벤토리에 포함
- `hired_agents.json` - Expert의 feasible_tools에 Rube 앱 포함
- `task_assignments.json` - CEO가 승인한 Rube 앱 (ceo_tools)
- `execution_log.json` - Rube를 통해 수행한 외부 액션 로그

---

## 상태 파일 스키마

### session.json
```json
{
  "session_id": "ses_YYYYMMDD_NNN",
  "phase": "goal_input | backlog_creation | tool_inventory | hiring | assignment | ready_to_execute | project_selection | task_briefing | ceo_review | executing | project_completed | all_completed",
  "execution_mode": "production | dry_run",
  "dry_run_config": {
    "mock_external_apis": true,
    "generate_files": true,
    "web_search": true
  },
  "current_project": "proj-001",
  "current_task": "task-001",
  "created_at": "ISO-8601"
}
```

**execution_mode 값:**
- `production`: 실제 외부 서비스 연동, 실제 API 호출
- `dry_run`: 외부 API를 mock 처리, 전체 흐름 검증용 (기본값 권장)

**dry_run_config:**
- `mock_external_apis`: Rube/외부 API 호출을 mock 응답으로 대체 (기본: true)
- `generate_files`: 로컬 파일은 실제로 생성 (기본: true)
- `web_search`: 웹 검색은 실제로 수행 (기본: true)

### backlog.json (dependency_graph 포함)
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
          "suggested_tool_categories": ["web_search", "design"],
          "dependencies": [],
          "required_inputs": []
        }
      ]
    }
  ],
  "dependency_graph": {
    "task-001": [],
    "task-002": ["task-001"],
    "task-003": ["task-001", "task-002"]
  }
}
```

### tool_inventory.json (v4 신규)

Tool Agent가 3-tier 검증 + 웹 검색 + 마켓플레이스 검색으로 생성합니다.

```json
{
  "inventory_id": "inv_YYYYMMDD_NNN",
  "created_at": "ISO-8601",
  "verification_sources": ["builtin_check", "local_skills_scan", "mcp_json_check", "rube_search_tools", "rube_manage_connections", "web_search", "vibeindex_search", "marketplace_search"],
  "available_tools": {
    "builtin": [
      {"tool": "WebSearch", "status": "available"}
    ],
    "skills": [
      {"tool": "/frontend-design", "status": "available"}
    ],
    "mcp_rube": [
      {"tool": "instagram", "status": "active", "account": "@cs_student_tips"},
      {"tool": "gemini", "status": "active"},
      {"tool": "google_sheets", "status": "not_connected"}
    ],
    "external_api": [
      {"tool": "imgflip_api", "status": "available", "confidence": "HIGH", "source": "web_search"}
    ]
  },
  "task_tool_defaults": {
    "task-001": {
      "recommended_tools": ["WebSearch", "WebFetch"],
      "combination_note": "경쟁사 분석 후 인사이트 정리"
    }
  }
}
```

### hired_agents.json (v4 - 역량 기반)
```json
{
  "agents": [
    {
      "agent_id": "expert-001",
      "role_name": "역할명",
      "capabilities": ["research", "data_analysis"],
      "feasible_tools": ["WebSearch", "WebFetch", "INSTAGRAM_GET_USER_INFO"],
      "base_tools": ["Read", "Write", "WebSearch"],
      "dynamic_tools": [],
      "assigned_tasks": ["task-001"],
      "status": "active"
    }
  ]
}
```

### task_assignments.json (v4 - Task Briefing 결과 포함)
```json
{
  "assignments_id": "asgn_YYYYMMDD_NNN",
  "assignments": [
    {
      "task_id": "task-010",
      "task_name": "론칭용 밈 콘텐츠 30개 제작",
      "task_type": "ACTION_FILE",
      "agent_id": "expert-004",
      "project_id": "proj-004",
      "default_tools": ["Read", "Write", "Bash", "GEMINI_GENERATE_IMAGE"],
      "ceo_tools": ["imgflip_api"],
      "ceo_references": [
        {
          "type": "image",
          "value": "/path/to/reference.png",
          "intent": "style",
          "note": "이런 느낌으로",
          "analyzed_content": {
            "fetched_summary": "클립아트 + 차트 조합 밈",
            "key_findings": ["심플한 일러스트", "데이터 시각화 유머"],
            "style_elements": {"illustration": "clipart", "colors": "pastel"},
            "actionable_insights": "matplotlib 차트 + 클립아트 합성"
          }
        }
      ],
      "ceo_instructions": "PNG 출력. AI 만든 티 내지 마. 클래식 밈 템플릿 활용.",
      "enriched_description": "클립아트+차트 스타일로 개발자 공감 밈 제작...",
      "direction": "개발자 공감 소재를 클립아트+차트 스타일로, AI 느낌 최소화",
      "completion_criteria": {
        "type": "ACTION_FILE",
        "expected_outputs": [
          {"type": "file", "pattern": "company/outputs/task010_*", "min_count": 30}
        ],
        "forbidden": ["설명 문서만 생성", "Tool 호출 없이 텍스트만 작성"]
      },
      "status": "pending",
      "briefing_approved": true
    }
  ]
}
```

---

## 자동 병렬 실행

dependency_graph를 기반으로 독립 태스크를 자동 병렬 실행합니다:

```
의존성이 없는 태스크들 → 자동 병렬:
  task-004 (독립) ─┐
  task-006 (독립) ─┤ 동시 실행!
                    ↓
  task-005 (task-004 의존) → task-004 완료 후 순차
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
- Phase 1: goal_input → backlog_creation → tool_inventory → hiring → assignment → ready_to_execute
- Phase 2: project_selection → task_briefing → ceo_review → executing → project_completed
- 각 단계 완료 시 다음 상태 파일 생성
- 오류 시 이전 상태 파일은 보존 (롤백 가능)

---

## 참고 문서

| 문서 | 경로 | 설명 |
|------|------|------|
| README | `README.md` | 프로젝트 전체 개요 |
| Interactive Execution 워크플로우 | `docs/specs/interactive-execution-workflow-v4.md` | **v4 워크플로우 상세 설계 (최신)** |
| Reference-Driven 워크플로우 | `docs/specs/reference-driven-workflow-v3.md` | v3 워크플로우 (레거시) |
| Tool-Aware 워크플로우 | `docs/specs/tool-aware-workflow-v2.md` | v2 워크플로우 (레거시) |
| Agentic AI 아키텍처 | `docs/specs/agentic-ai-architecture.md` | 시스템 아키텍처 스펙 |
| E2E 테스트 시나리오 | `docs/specs/e2e-test-scenarios.md` | 통합 테스트 시나리오 |

---

## 빠른 시작 예시

```
# Phase 1: 계획 수립
1. "ceo-agent로 목표를 입력해줘"                → ceo_goal.json
2. "rm-agent로 백로그를 생성해줘"               → backlog.json
3. "tool-agent로 Tool 인벤토리를 생성해줘"      → tool_inventory.json
4. "hr-agent로 에이전트를 고용해줘"             → hired_agents.json
5. "rm-agent로 태스크를 할당해줘"               → task_assignments.json

# Phase 2: 프로젝트 실행
6. "프로젝트 1번 실행해줘"                      → Task Briefing 보고
7. (CEO가 태스크별로 Tool 변경/레퍼런스 추가/지시사항 추가 또는 "전부 승인")
8. "expert-agent로 태스크를 실행해줘"           → 자동 병렬 실행 + 결과 보고
9. "다음 프로젝트 실행해줘"                     → 6번으로 반복
```
