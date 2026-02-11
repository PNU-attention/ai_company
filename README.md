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
> **Tool Agent가 사용 가능한 도구를 인벤토리로 정리**하며,
> **HR 에이전트가 역량 기반으로 전문가를 채용**하고,
> CEO가 **태스크별로 실행 계획을 검토·승인**한 뒤,
> **Expert 에이전트들이 승인된 계획에 따라 실제 업무를 수행**하여 목표를 달성할 수 있다.

---

## 2. 핵심 에이전트 구조 (v4)

```
                        CEO (사용자)
                            │
                  Phase 1   │ ① 목표 입력
                            ▼
                    ┌───────────────┐
                    │  RM 에이전트    │ ② 백로그 생성 (dependency_graph 포함)
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Tool 에이전트   │ ③ Tool 인벤토리 생성
                    └───────┬───────┘   (3-tier 검증 + 웹 검색 + 마켓플레이스)
                            │
                            ▼
                    ┌───────────────┐
                    │  HR 에이전트    │ ④ 역량 기반 Expert 고용
                    └───────┬───────┘   (인벤토리 참고)
                            │
                            ▼
                    ┌───────────────┐
                    │  RM 에이전트    │ ⑤ 태스크 할당 + 기본 Tool 배정
                    └───────┬───────┘
                            │
                  Phase 2   │ ⑥ CEO가 프로젝트 선택
                            ▼
                    ┌───────────────┐
                    │ Task Briefing  │ ⑦ 태스크별 실행 계획 보고
                    │               │   "task-010: Gemini로 밈 제작"
                    │               │   "괜찮으신가요?"
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  CEO          │ ⑧ 태스크별 승인/수정/레퍼런스/지시사항
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ Tool 에이전트   │ ⑨ (필요시) 레퍼런스 분석 + Tool 조정
                    └───────┬───────┘   (Analyze Once, Use Everywhere)
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ Expert Agent 1│   │ Expert Agent 2│   │ Expert Agent N│
│ (시장 조사)    │   │ (밈 제작)      │   │ (SNS 운영)    │
└───────────────┘   └───────────────┘   └───────────────┘
  ⑩ 자동 병렬 실행    (dependency_graph     기반)
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  CEO          │ ⑪ 결과 검토 → 다음 프로젝트
                    └───────────────┘
```

### 역할 분담

| 에이전트 | 역할 | 책임 | 모델 |
|----------|------|------|------|
| **CEO** | 의사결정자 | 목표 정의, 프로젝트 선택, **태스크별 Briefing 승인/수정** | sonnet |
| **RM** | 프로젝트 매니저 | 백로그 생성 (**dependency_graph**), 태스크 할당 | sonnet |
| **Tool Agent** | 도구 컨설턴트 | **Phase 1: Tool 인벤토리** / **Phase 2: 레퍼런스 분석 + Tool 조정** | sonnet |
| **HR** | 에이전트 팩토리 | **Tool 인벤토리 참고, 역량 기반** Expert 고용 | sonnet |
| **Expert** | 실무자 | **analyzed_content + ceo_instructions** 기반 태스크 수행 | sonnet |

---

## 3. 워크플로우 (v4 - Interactive Execution)

### 3.1 전체 워크플로우

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 1: 계획 수립                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ① CEO 목표 입력                                                │
│       ↓                                                         │
│  ② RM: 백로그 생성 (dependency_graph 포함)                      │
│       ↓                                                         │
│  ③ Tool Agent: Tool 인벤토리 생성 (3-tier 검증)                 │
│       ↓                                                         │
│  ④ HR: 인벤토리 참고하여 역량 기반 Expert 생성                  │
│       ↓                                                         │
│  ⑤ RM: Expert 할당 + 기본 Tool 배정                             │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Phase 2: 프로젝트 실행 (반복)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⑥ CEO: 실행할 프로젝트 선택                                    │
│       ↓                                                         │
│  ⑦ 태스크별 실행 계획 보고 (Task Briefing)                      │
│       ↓                                                         │
│  ⑧ CEO: 태스크별 승인 / Tool 변경 / 레퍼런스 추가 / 지시사항    │
│       ↓                                                         │
│  ⑨ (필요시) Tool Agent 레퍼런스 분석 + Tool 조정                │
│       ↓                                                         │
│  ⑩ 태스크 실행 (dependency_graph 기반 자동 병렬)                │
│       ↓                                                         │
│  ⑪ 결과 보고 → 다음 프로젝트 ⑥으로                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 각 단계 상세

| 단계 | 주체 | 설명 | 출력 |
|------|------|------|------|
| ① | CEO | 회사 목표/KPI/제약조건 입력 | `ceo_goal.json` |
| ② | RM | 목표를 프로젝트/태스크로 분해 + **dependency_graph 생성** | `backlog.json` |
| ③ | Tool Agent | 사용 가능 Tool 전체 인벤토리 (3-tier 검증 + 웹 검색 + 마켓플레이스) | `tool_inventory.json` |
| ④ | HR | 인벤토리 참고하여 **역량 기반** Expert 생성 | `hired_agents.json` |
| ⑤ | RM | Expert에 태스크 할당 + 기본 Tool 배정 | `task_assignments.json` |
| ⑥ | CEO | 실행할 프로젝트 선택 | - |
| ⑦ | 시스템 | **태스크별 실행 계획 보고** (담당 Agent, Tool, 산출물) | Task Briefing UI |
| ⑧ | CEO | **태스크별** 승인/Tool 변경/레퍼런스 추가/지시사항 | `task_assignments.json` 업데이트 |
| ⑨ | Tool Agent | 레퍼런스 분석 → `analyzed_content` 저장 → enriched_description 생성 | `task_assignments.json` 업데이트 |
| ⑩ | Expert | dependency_graph 기반 **자동 병렬** 태스크 실행 | `execution_log.json` |
| ⑪ | 시스템 | 결과 보고 | 결과 파일들 |

### 3.3 v2 → v3 → v4 핵심 변경점

| 항목 | v2 (Tool-Aware) | v3 (Reference-Driven) | v4 (Interactive Execution) |
|------|-----------------|----------------------|---------------------------|
| 패러다임 | CEO가 Tool 선택 | CEO가 레퍼런스 일괄 제공 | **태스크별 Briefing + 승인** |
| 레퍼런스 수집 | 없음 | Phase 1 전체 한번에 | **Phase 2 태스크별 Just-In-Time** |
| Tool 확정 | CEO가 직접 선택 | Tool Agent 추천 → CEO 1회 승인 | **태스크별 동적 확정** |
| CEO 개입 | 2~3회 | 1~2회 | **태스크별 Briefing + 개입** |
| 실행 투명성 | 낮음 | 낮음 | **실행 전 계획 확인 → 승인 → 실행** |
| 병렬 실행 | 없음 | 수동 판단 | **dependency_graph 기반 자동** |
| HR 에이전트 | Tool 종속적 | Tool 종속적 | **역량 기반 (feasible_tools)** |

---

## 4. Task Briefing (v4 핵심)

v4의 가장 중요한 혁신입니다. CEO가 프로젝트를 선택하면, **각 태스크별로 실행 계획을 보고**받고 검토할 수 있습니다.

### Briefing 인터페이스

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

| 유형 | 예시 | 효과 |
|------|------|------|
| **승인** | "OK", "전부 승인" | 모든 태스크 승인 → 실행 |
| **Tool 변경** | "task-010은 Imgflip API 써줘" | `ceo_tools` 업데이트 |
| **레퍼런스 추가** | "이 이미지 참고해" (파일/URL/메모) | Tool Agent 분석 → `analyzed_content` 저장 |
| **지시사항** | "PNG 출력, AI 티 내지 마" | `ceo_instructions` 업데이트 |
| **일괄 승인** | "전부 OK" | 모든 태스크 한번에 승인 |

---

## 5. 아키텍처: Skill vs Subagent

본 프로젝트는 Claude Code의 **Subagent** 아키텍처를 사용합니다.

| 구분 | Skill | Subagent |
|------|-------|----------|
| **위치** | `.claude/skills/` | `.claude/agents/` |
| **형태** | 지침서/프롬프트 | 독립 AI 엔티티 |
| **컨텍스트** | 메인 세션과 공유 | **별도 컨텍스트** |
| **실행** | Claude가 역할 연기 | 독립적으로 작동 |
| **용도** | 도구/작업방식 지침 | 복잡한 작업 위임 |

### 왜 Subagent인가?

- **독립 컨텍스트**: 각 에이전트가 자신만의 메모리와 상태를 가짐
- **Tool 격리**: 에이전트별로 사용 가능한 Tool을 명시적으로 제한
- **모델 최적화**: 역할에 따라 적합한 모델 사용
- **확장성**: 새 에이전트 추가가 용이

### Spec-Driven Development (SDD)

코드는 다음이 준비되기 전까지 작성되지 않습니다:

- 요구사항 명세
- 유저 스토리
- 기술 스펙
- 테스트 케이스

---

## 6. 핵심 개념: Analyze Once, Use Everywhere

v3에서 도입되어 v4에서도 계승된 핵심 설계 원칙입니다. v4에서는 **Phase 2 Task Briefing 시점**에 적용됩니다.

### 문제 (v2)

같은 레퍼런스를 3번 분석하는 비효율:

```
Tool Agent: URL 접속 → 분석 → Tool 추천
HR Agent:   URL 접속 → 분석 → 전문가 구체화    ← 중복
Expert:     URL 접속 → 분석 → 작업 수행         ← 중복
```

### 해결 (v3 → v4 계승)

Tool Agent가 1번만 깊게 분석하고, `analyzed_content`에 결과 저장:

```
v4 Phase 2:
  CEO: Task Briefing에서 레퍼런스 첨부
       ↓
  Tool Agent: 깊은 분석 → analyzed_content에 저장 (1번만)
              + enriched_description 생성
              + direction 도출
       ↓
  Expert: analyzed_content 읽기 → 바로 작업 수행
```

### `analyzed_content` 구조

| 필드 | 설명 | 주 소비자 |
|------|------|----------|
| `direction` | 모든 레퍼런스를 종합한 태스크 방향성 | Expert |
| `fetched_summary` | URL/파일/이미지 분석 요약 | Expert |
| `key_findings` | 핵심 발견 사항 | Expert |
| `style_elements` | 색상, 레이아웃, 타이포그래피 | Expert (디자인 작업) |
| `structure_elements` | 페이지/문서 구조 분석 | Expert (구조 재현) |
| `actionable_insights` | 구체적 활용 지침 | Expert (실행 계획) |

---

## 7. 레퍼런스 시스템 (v4 - Just-In-Time)

### 레퍼런스 수집 시점

| 버전 | 수집 시점 | 문제점 |
|------|----------|--------|
| v3 | Phase 1에서 전체 태스크 한번에 | 아직 실행하지 않은 태스크에 레퍼런스를 줄 수 없음 |
| **v4** | **Phase 2 Task Briefing에서 태스크별** | 실행 직전에 필요한 태스크에만 레퍼런스 제공 |

### 레퍼런스 타입

| 타입 | 형태 | 예시 | 용도 |
|------|------|------|------|
| `url` | 웹 주소 | 경쟁사 사이트, 참고 디자인 | "이런 느낌으로" |
| `image` | 이미지 파일 경로 | 목업, 스크린샷, 로고 | "이렇게 생긴 것" |
| `file` | 로컬 파일 경로 | 기존 보고서, 템플릿, 데이터셋 | "이 포맷 따라서" |
| `note` | 텍스트 메모 | 스타일 가이드, 톤앤매너 | "이런 방향으로" |

### 레퍼런스 의도 (intent)

| Intent | 의미 |
|--------|------|
| `style` | "이런 스타일/느낌으로 만들어줘" |
| `content` | "이 내용을 참고해서 작성해줘" |
| `template` | "이 형식/구조를 따라줘" |
| `data` | "이 데이터를 활용해줘" |
| `competitor` | "이 경쟁사를 분석해줘" |

---

## 8. Tool 시스템

### 8.1 Tool 카테고리

| 타입 | 설명 | 예시 |
|------|------|------|
| **Built-in** | Claude Code 내장 도구 | WebSearch, WebFetch, Read, Write, Edit, Bash |
| **Skills** | 설치된 스킬 | /frontend-design, /mcp-builder |
| **MCP** | 외부 서비스 연동 | figma, **rube**, github |

### 8.2 Tool 인벤토리 (v4 신규)

v4에서 Tool Agent는 Phase 1에서 **사용 가능한 Tool 전체를 인벤토리로 정리**합니다.

```
검증 프로세스 (3-tier + 외부 탐색):
  1. Built-in 체크 → 항상 사용 가능
  2. Local Skills 스캔 → .claude/skills/
  3. MCP 서버 + Rube 마켓플레이스 → RUBE_SEARCH_TOOLS + RUBE_MANAGE_CONNECTIONS
  4. 외부 API 웹 검색 → "meme generator API" 등
  5. 마켓플레이스 검색 → MCP.so, anthropics/skills
```

### 8.3 Rube MCP - 외부 서비스 통합의 핵심

> **Rube**는 본 프로젝트에서 **외부 서비스 연동의 중심축** 역할을 합니다.

#### Rube란?

[Rube](https://rube.app)는 Composio 기반의 MCP 서버로, AI 에이전트가 **500개 이상의 외부 비즈니스 앱**에 자연어로 접근할 수 있게 해주는 통합 플랫폼입니다.

#### 왜 Rube가 핵심인가?

```
Without Rube                          With Rube
─────────────────                     ─────────────────
Expert Agent                          Expert Agent
    │                                     │
    ├── WebSearch ✅                      ├── WebSearch ✅
    ├── WebFetch ✅                       ├── WebFetch ✅
    ├── Read/Write ✅                     ├── Read/Write ✅
    │                                     │
    ├── Gmail 전송 ❌                     ├── Gmail 전송 ✅ (via Rube)
    ├── Slack 메시지 ❌                   ├── Slack 메시지 ✅ (via Rube)
    ├── Google Sheets ❌                  ├── Google Sheets ✅ (via Rube)
    ├── Instagram 업로드 ❌               ├── Instagram 업로드 ✅ (via Rube)
    ├── Gemini 이미지 생성 ❌             ├── Gemini 이미지 생성 ✅ (via Rube)
    └── Canva 디자인 ❌                   └── Canva 디자인 ✅ (via Rube)
```

#### Rube가 지원하는 주요 앱 카테고리

| 카테고리 | 대표 앱 | 활용 예시 |
|----------|---------|----------|
| **커뮤니케이션** | Gmail, Slack, Discord, Teams | 이메일 발송, 채널 메시지, 알림 |
| **프로젝트 관리** | Jira, Asana, Trello, Linear | 이슈 생성, 태스크 관리 |
| **문서/노트** | Notion, Google Docs, Confluence | 문서 작성, 위키 업데이트 |
| **데이터/스프레드시트** | Google Sheets, Airtable | 데이터 입력, 분석 결과 저장 |
| **이미지 생성** | Gemini, Canva | 밈 이미지, 디자인 에셋 |
| **SNS** | Instagram, Twitter | 콘텐츠 업로드, 계정 관리 |
| **저장소/코드** | GitHub, GitLab, Bitbucket | PR 생성, 이슈 관리 |
| **결제/이커머스** | Stripe, Shopify | 결제 처리, 주문 관리 |

#### 워크플로우에서의 Rube 위치 (v4)

```
Phase 1 (계획)                           Phase 2 (실행)
─────────────────────────────────────    ─────────────────────────────────────
③ Tool Agent 인벤토리 생성               ⑧ CEO가 Task Briefing에서 Rube Tool 지시
   RUBE_SEARCH_TOOLS로 앱 검색               "Gemini로 이미지 만들어줘"
   RUBE_MANAGE_CONNECTIONS로 연결 확인           │
         │                               ⑩ Expert 태스크 수행
   인벤토리에 기록:                              │
   "instagram: active"                          ├── Built-in Tool 직접 사용
   "gemini: active"                             └── Rube MCP 경유 사용
   "google_sheets: not_connected"                    (Instagram, Gemini, ...)
```

#### 왜 Rube인가? (대안 비교)

| 도구 | 방식 | 앱 수 | 특징 | 오픈소스 |
|------|------|-------|------|----------|
| **Rube (Composio)** | MCP 서버 | 500+ | Claude Code 네이티브 지원, 노코드, 무료 | X |
| ACI.dev | MCP / Function Calling | 500+ | 오픈소스, 자체 호스팅 가능 | O |
| Pipedream | MCP + 워크플로우 빌더 | 10,000+ | 코드 작성 가능, 앱 수 최대 | X |
| n8n | 워크플로우 자동화 | 400+ | 오픈소스, 비주얼 빌더 | O |

**Rube를 선택한 이유:**

1. **Claude Code 네이티브 호환**: `.mcp.json` 한 줄 설정으로 즉시 사용 가능
2. **노코드/자연어 기반**: Expert가 자연어로 "이메일 보내줘"라고 하면 Rube가 처리
3. **Composio 인프라**: SOC 2 Type II, 토큰 격리, OAuth 자동 관리
4. **무료 제공**: 실험 프로젝트 단계에서 비용 부담 없음
5. **MCP 표준**: 향후 다른 MCP 서버로 교체/병행 가능

#### Rube 설정

```json
// .mcp.json (프로젝트 루트에 포함됨)
{
  "mcpServers": {
    "rube": {
      "type": "http",
      "url": "https://rube.app/mcp"
    }
  }
}
```

**초기 설정 (최초 1회):**

1. 프로젝트 클론 후 Claude Code 실행
2. Rube MCP 서버 연결 승인
3. [rube.app/marketplace](https://rube.app/marketplace)에서 사용할 앱 연결 (OAuth 인증)
4. 연결 완료 후 Expert 에이전트가 해당 앱을 바로 사용 가능

---

## 9. 실행 방법 (Claude Code)

### 9.1 Subagent 호출 (Task tool)

```bash
# Phase 1: 계획 수립
"ceo-agent로 목표를 입력해줘"
"rm-agent로 백로그를 생성해줘"
"tool-agent로 Tool 인벤토리를 생성해줘"
"hr-agent로 에이전트를 고용해줘"
"rm-agent로 태스크를 할당해줘"

# Phase 2: 프로젝트 실행
"프로젝트 1번 실행해줘"                        → Task Briefing 보고
(CEO가 태스크별로 승인/수정/레퍼런스/지시사항)
"expert-agent로 태스크를 실행해줘"             → 자동 병렬 실행
"다음 프로젝트 실행해줘"                       → 반복
```

### 9.2 Skill 호출 (슬래시 명령어)

```bash
/ai-company           # 전체 시스템 오케스트레이션
/frontend-design      # 웹 UI 디자인
/mcp-builder          # MCP 서버 생성
```

---

## 10. 디렉토리 구조

```
ai_company/
├── .mcp.json                      # 프로젝트 레벨 MCP 설정 (Rube 포함)
├── .claude/
│   ├── agents/                    # Subagent 정의 (독립 컨텍스트)
│   │   ├── ceo-agent.md           # CEO: 목표 정의, Task Briefing 승인
│   │   ├── rm-agent.md            # RM: 백로그 + dependency_graph, 할당
│   │   ├── tool-agent.md          # Tool: 인벤토리 생성, 레퍼런스 분석
│   │   ├── hr-agent.md            # HR: 역량 기반 Expert 고용
│   │   └── expert-agent.md        # Expert: 태스크 실행
│   │
│   ├── skills/                    # 유틸리티 스킬
│   │   ├── ai-company/            # 메인 오케스트레이터
│   │   ├── frontend-design/       # 디자인 스킬
│   │   ├── mcp-builder/           # MCP 빌더
│   │   └── skill-creator/         # 스킬 생성기
│   │
│   └── CLAUDE.md                  # Claude Code 가이드
│
├── company/
│   ├── state/                     # 상태 파일 (JSON)
│   │   ├── session.json           # 세션 정보
│   │   ├── ceo_goal.json          # CEO 목표
│   │   ├── backlog.json           # RM 백로그 (dependency_graph 포함)
│   │   ├── tool_inventory.json    # Tool 인벤토리 (v4)
│   │   ├── hired_agents.json      # 역량 기반 에이전트
│   │   ├── task_assignments.json  # 할당 + CEO 승인/레퍼런스/지시사항
│   │   └── execution_log.json     # 실행 로그
│   │
│   ├── outputs/                   # 실행 결과물
│   └── assets/                    # 리소스 파일
│
├── docs/
│   ├── specs/                     # 기술 스펙
│   │   ├── interactive-execution-workflow-v4.md  # v4 워크플로우 (최신)
│   │   ├── reference-driven-workflow-v3.md       # v3 (레거시)
│   │   ├── tool-aware-workflow-v2.md             # v2 (레거시)
│   │   ├── agentic-ai-architecture.md
│   │   └── e2e-test-scenarios.md
│   └── reports/                   # 보고서
│
└── README.md
```

---

## 11. 상태 파일 스키마

### session.json
```json
{
  "session_id": "ses_20260208_001",
  "phase": "task_briefing",
  "current_project": "proj-004",
  "created_at": "2026-02-08T10:00:00Z",
  "version": "v4"
}
```

### backlog.json (dependency_graph 포함)
```json
{
  "backlog_id": "bl_20260208_001",
  "dependency_graph": {
    "task-001": [],
    "task-002": ["task-001"],
    "task-004": [],
    "task-006": ["task-001"]
  }
}
```

### tool_inventory.json (v4 신규)
```json
{
  "inventory_id": "inv_20260208_001",
  "available_tools": {
    "builtin": [{"tool": "WebSearch", "status": "available"}],
    "skills": [{"tool": "/frontend-design", "status": "available"}],
    "mcp_rube": [{"tool": "instagram", "status": "active", "account": "@cs_student_tips"}],
    "external_api": [{"tool": "imgflip_api", "status": "available", "confidence": "HIGH"}]
  },
  "task_tool_defaults": {
    "task-010": {
      "recommended_tools": ["Bash", "GEMINI_GENERATE_IMAGE", "imgflip_api"],
      "combination_note": "Gemini 커스텀 + Imgflip 클래식 + PIL 후처리"
    }
  }
}
```

### hired_agents.json (v4 - 역량 기반)
```json
{
  "agents": [{
    "agent_id": "expert-004",
    "role_name": "밈 콘텐츠 제작 전문가",
    "capabilities": ["image_creation", "meme_design"],
    "feasible_tools": ["GEMINI_GENERATE_IMAGE", "imgflip_api", "PIL/matplotlib"],
    "base_tools": ["Read", "Write", "WebSearch", "Bash"],
    "dynamic_tools": []
  }]
}
```

### task_assignments.json (v4 - Task Briefing 결과)
```json
{
  "assignments": [{
    "task_id": "task-010",
    "agent_id": "expert-004",
    "default_tools": ["Bash", "GEMINI_GENERATE_IMAGE"],
    "ceo_tools": ["imgflip_api"],
    "ceo_references": [{
      "type": "image",
      "value": "/path/to/ref.png",
      "intent": "style",
      "analyzed_content": {
        "fetched_summary": "클립아트 + 차트 조합 밈",
        "style_elements": {"illustration": "clipart"},
        "actionable_insights": "matplotlib 차트 + 클립아트 합성"
      }
    }],
    "ceo_instructions": "PNG 출력. AI 티 내지 마.",
    "enriched_description": "클립아트+차트 스타일로 개발자 밈 제작...",
    "direction": "개발자 공감 소재를 클립아트+차트로, AI 느낌 최소화",
    "briefing_approved": true
  }]
}
```

---

## 12. 핵심 개념

| 개념 | 설명 |
|------|------|
| **Interactive Execution** | 실행 전 CEO가 태스크별로 계획을 검토·승인하는 워크플로우 |
| **Task Briefing** | 태스크별 "누가, 어떤 Tool로, 어떻게" 보고하는 단계 |
| **Just-In-Time Reference** | 레퍼런스를 실행 직전 해당 태스크에만 수집 |
| **Analyze Once, Use Everywhere** | Tool Agent가 1번 분석한 결과를 Expert가 재활용 |
| **dependency_graph** | 태스크 간 의존성을 명시하여 자동 병렬 실행 지원 |
| **analyzed_content** | 레퍼런스 깊은 분석 결과 (스타일, 구조, 핵심 발견, 활용 지침) |
| **enriched_description** | 레퍼런스 분석 후 상세해진 태스크 설명 |
| **feasible_tools** | Expert가 사용 가능한 Tool 후보 목록 (인벤토리 기반) |
| **Subagent** | 독립 컨텍스트에서 실행되는 AI 에이전트 |

---

## 13. 차별점

- **Interactive Execution**: CEO가 실행 전에 계획을 검토하고 태스크별로 개입 가능
- **Just-In-Time Reference**: 필요한 시점에 필요한 태스크에만 레퍼런스 제공
- **Analyze Once, Use Everywhere**: 레퍼런스 1회 분석으로 전체 파이프라인 동작
- **Auto-Parallel Execution**: dependency_graph 기반 자동 병렬 실행
- **역량 기반 에이전트**: Tool에 종속되지 않는 유연한 Expert 시스템
- **Subagent 아키텍처**: 독립 컨텍스트의 진정한 멀티 에이전트 시스템
- **Rube MCP 통합**: 500+ 비즈니스 앱과 AI-Native 연동
- **Human-in-the-loop**: CEO가 핵심 의사결정 지점마다 개입

---

## 14. 프로젝트 상태

**v4 Interactive Execution 아키텍처 완료**

- [x] v4 설계 스펙 작성 (`interactive-execution-workflow-v4.md`)
- [x] Subagent 구조 v4 업데이트
  - [x] ceo-agent.md (Task Briefing 승인자)
  - [x] rm-agent.md (dependency_graph, 기본 Tool 배정)
  - [x] tool-agent.md (인벤토리 + Just-In-Time 분석)
  - [x] hr-agent.md (역량 기반 고용)
  - [x] expert-agent.md (analyzed_content + ceo_instructions 기반 실행)
- [x] CLAUDE.md v4 업데이트
- [x] README.md v4 업데이트
- [ ] ai-company 오케스트레이터 스킬 v4 업데이트
- [ ] 실제 E2E 테스트 수행

---

## 15. 참고 문서

| 문서 | 경로 | 설명 |
|------|------|------|
| CLAUDE.md | `.claude/CLAUDE.md` | Claude Code 가이드 |
| Interactive Execution 워크플로우 | `docs/specs/interactive-execution-workflow-v4.md` | **v4 워크플로우 상세 설계 (최신)** |
| Reference-Driven 워크플로우 | `docs/specs/reference-driven-workflow-v3.md` | v3 워크플로우 (레거시) |
| Tool-Aware 워크플로우 | `docs/specs/tool-aware-workflow-v2.md` | v2 워크플로우 (레거시) |
| Agentic AI 아키텍처 | `docs/specs/agentic-ai-architecture.md` | 시스템 아키텍처 스펙 |
| E2E 테스트 시나리오 | `docs/specs/e2e-test-scenarios.md` | 통합 테스트 시나리오 |

---

## 16. 안내

본 프로젝트는
AI가 인간을 대체하는 것이 아니라,
**인간과 AI의 협업 방식을 재정의하기 위한 실험적 프로젝트**입니다.
