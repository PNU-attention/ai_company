# Interactive Execution Workflow v4 설계서

## 1. 개요

### 1.1 v3의 문제점 (실제 사용에서 발견)

v3(Reference-Driven Workflow)는 CEO가 레퍼런스를 제공하면 Tool Agent가 분석하는 구조였다. 실제 세션을 통해 다음 문제들이 드러났다.

#### 문제 1: 모든 태스크에 한번에 레퍼런스를 넣어야 함

```
v3 Phase 1-③: CEO 레퍼런스 첨부

18개 태스크에 대해 한번에 레퍼런스를 물어봄:
  "Task 1.1: 시장 트렌드 조사 - 레퍼런스는?"
  "Task 1.2: 경쟁사 분석 - 레퍼런스는?"
  ...
  "Task 6.3: 월간 리포트 - 레퍼런스는?"

→ CEO는 아직 실행하지도 않은 태스크에 레퍼런스를 줄 수 없음
→ 대부분 "없음" / "건너뛰기"로 넘어감
→ 레퍼런스 수집의 의미가 퇴색됨
```

**핵심**: 레퍼런스는 "지금 실행할 태스크"에 대해서만 의미가 있다.

#### 문제 2: 어떤 Tool로 실행되는지 사전에 알 수 없음

```
v3 실행 흐름:
  CEO가 프로젝트 선택 → Expert가 태스크 수행 → 결과 확인

→ CEO는 Expert가 어떤 Tool을 쓰는지 실행 후에야 알게 됨
→ "Imgflip API 쓰라고 했는데 왜 HTML/CSS로 만들었어?"
→ "Gemini로 이미지 생성하면 되는데 왜 matplotlib?"
→ 한 사이클 다 돈 후에야 방향 수정 가능 → 시간 낭비
```

**핵심**: CEO가 실행 전에 "어떻게 할 건지" 확인하고 개입할 수 있어야 한다.

#### 문제 3: 병렬 실행이 수동적

```
v3에서 병렬 실행:
  task-004와 task-006이 독립적인데,
  오케스트레이터가 수동으로 판단해서 병렬 호출함

→ 의존성 분석이 체계적이지 않음
→ 어떤 태스크가 병렬 가능한지 사전에 명확하지 않음
```

#### 문제 4: Subagent 속도 이슈

```
Skill (메인 세션 공유):     빠름 (컨텍스트 공유)
Subagent (별도 컨텍스트):   느림 (매번 새 컨텍스트 빌딩, 파일 읽기)

→ Expert 한번 호출에 3~6분 소요
→ 18개 태스크를 순차 실행하면 1시간+
→ 결과물 품질은 좋아졌지만, 속도 트레이드오프
```

---

### 1.2 v4의 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **Task-Level Approval** | 태스크 실행 전에 "누가, 어떤 Tool로, 어떻게" 할 건지 보고하고 승인받음 |
| **Just-In-Time Reference** | 레퍼런스는 실행 직전에, 해당 태스크에 대해서만 수집 |
| **CEO Intervention Point** | CEO가 Tool 변경, 레퍼런스 추가, 지시사항 추가 가능 |
| **Auto-Parallel Execution** | 의존성 그래프 기반 자동 병렬 실행 |
| **Transparent Execution** | "무엇을 할 건지" 먼저 보여주고 실행 |

---

## 2. 워크플로우

### 2.1 전체 흐름

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 1: 계획 수립                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ① CEO 목표 입력                                                │
│       ↓                                                         │
│  ② RM: 백로그 생성 (프로젝트/태스크)                            │
│       ↓                                                         │
│  ③ Tool Agent: 사용 가능 Tool 전체 인벤토리 생성                │
│       ↓                                                         │
│  ④ HR: Tool 인벤토리 참고하여 Expert 에이전트 생성              │
│       ↓                                                         │
│  ⑤ RM: Expert를 프로젝트/태스크에 할당 + Tool 배정              │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    Phase 2: 프로젝트 실행                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⑥ CEO: 실행할 프로젝트 선택                                    │
│       ↓                                                         │
│  ⑦ 태스크별 실행 계획 보고 (Task Briefing)                      │
│     "task-010: 밈 콘텐츠 제작"                                  │
│     "담당: 디자이너 에이전트"                                    │
│     "Tool: Gemini API로 이미지 생성"                             │
│     "괜찮으신가요? 레퍼런스나 변경사항 있으시면 말씀해주세요"    │
│       ↓                                                         │
│  ⑧ CEO: 태스크별 승인 / 수정 / 레퍼런스 추가                    │
│     "Imgflip API로 클래식 밈 템플릿 써줘"                       │
│     "이 이미지 참고해서 만들어줘" (레퍼런스 첨부)                │
│       ↓                                                         │
│  ⑨ (필요시) 레퍼런스 분석 + Tool 조정                           │
│       ↓                                                         │
│  ⑩ 태스크 실행 (의존성 기반 자동 병렬)                          │
│       ↓                                                         │
│  ⑪ 결과 보고                                                    │
│       ↓                                                         │
│  ⑫ 다음 프로젝트 → ⑥으로                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### 2.2 Phase 1 상세

#### ① CEO 목표 입력
- v3와 동일

#### ② RM 백로그 생성
- v3와 동일
- **추가**: 태스크 간 의존성 그래프를 명시적으로 생성

```json
{
  "dependency_graph": {
    "task-001": [],
    "task-002": ["task-001"],
    "task-003": ["task-001", "task-002"],
    "task-006": ["task-001"]
  }
}
```

#### ③ Tool Agent: Tool 인벤토리 생성 (v3 검증 로직 계승)

백로그의 태스크 유형을 분석하고, **v3의 3-tier 검증 로직**을 그대로 사용하여 사용 가능한 Tool 전체를 인벤토리로 정리한다.

**검증 프로세스 (v3 tool-agent 로직 동일)**:

```
1. 백로그 태스크 유형 분석
   "RESEARCH 6개, ACTION 4개, DOCUMENT 5개, APPROVAL 3개"
   → 필요 Tool 카테고리 도출: web_search, image_creation, document, ...
      ↓
2. Built-in 체크 (항상 사용 가능)
   WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep
      ↓
3. Local Skills 스캔
   ls .claude/skills/ → /frontend-design, /mcp-builder 등
      ↓
4. MCP 서버 확인 + Rube 마켓플레이스 검색
   ├─ .mcp.json 확인 → 연결된 MCP 서버 목록
   ├─ RUBE_SEARCH_TOOLS로 필요 카테고리별 Tool 검색
   │   (예: "image generation", "instagram posting", "meme creation")
   ├─ RUBE_MANAGE_CONNECTIONS로 연결 상태 확인
   │   ├─ ✅ ACTIVE → 인벤토리에 "active"로 등록
   │   └─ ❌ 미연결 → "not_connected" + CEO 안내 메시지 포함
   └─ 각 Tool의 실제 사용 가능 여부 + 계정 정보 기록
      ↓
5. 외부 API 탐색 (WebSearch)
   ├─ "meme generator API free" 같은 키워드로 웹 검색
   ├─ 발견된 API의 무료/유료, 인증 방법, 제한사항 조사
   └─ 신뢰도 레벨 부여 (HIGH/MEDIUM/LOW)
      ↓
6. 외부 마켓플레이스 검색 (필요시)
   ├─ MCP.so (17,000+ MCP 서버)
   ├─ anthropics/skills (GitHub)
   └─ 기타 커뮤니티 소스
      ↓
7. Tool 인벤토리 생성 → tool_inventory.json
```

**태스크별 추천 Tool 매핑**: 인벤토리 생성과 함께, 각 태스크에 어떤 Tool이 적합한지 기본 추천도 포함한다 (v3의 `recommended_tools`와 동일 로직).

```json
{
  "task_tool_defaults": {
    "task-001": {
      "recommended_tools": ["WebSearch", "WebFetch", "INSTAGRAM_GET_USER_INFO"],
      "combination_note": "경쟁사 계정 분석 후 인사이트 정리"
    },
    "task-010": {
      "recommended_tools": ["Bash", "GEMINI_GENERATE_IMAGE", "imgflip_api"],
      "combination_note": "Gemini로 커스텀 이미지 + Imgflip으로 클래식 밈 템플릿"
    }
  }
}
```

#### ④ HR: Tool 인벤토리 참고하여 Expert 생성

Tool 인벤토리를 읽고, **실현 가능한 역량**을 기반으로 Expert 에이전트를 생성한다.

- Tool 인벤토리에 이미지 생성 도구가 있으므로 → "이미지 제작 가능" 역량 부여
- Tool 인벤토리에 Instagram API가 active이므로 → "SNS 운영 가능" 역량 부여
- 특정 Tool에 묶이지 않되, **어떤 Tool로 실현할 수 있는지** 인벤토리에서 확인

```json
{
  "agent_id": "expert-004",
  "role_name": "밈 콘텐츠 제작 전문가",
  "capabilities": ["image_creation", "meme_design", "copywriting"],
  "feasible_tools": ["GEMINI_GENERATE_IMAGE", "imgflip_api", "PIL/matplotlib", "/frontend-design"],
  "base_tools": ["Read", "Write", "WebSearch"],
  "dynamic_tools": []
}
```

`feasible_tools`: 이 에이전트가 사용할 수 있는 Tool 후보 목록 (인벤토리 기반). 실제 어떤 Tool을 쓸지는 Phase 2 Task Briefing에서 CEO가 결정.

#### ⑤ RM 할당
- Expert를 프로젝트/태스크에 매핑
- Tool Agent의 리스트를 기반으로 태스크별 기본 Tool 배정
- 이 배정은 "초안"이며, CEO가 ⑧에서 변경 가능

---

### 2.3 Phase 2 상세: Task Briefing Loop (v4 핵심)

#### ⑥ CEO 프로젝트 선택

```
══════════════════════════════════════════════════════════════
  실행할 프로젝트를 선택해주세요:
  [1] 시장 조사 및 경쟁사 분석 (3 tasks)
  [2] 콘텐츠 전략 및 소재 준비 (3 tasks)
  ...
══════════════════════════════════════════════════════════════
```

#### ⑦ Task Briefing (태스크별 실행 계획 보고)

CEO가 프로젝트를 선택하면, 해당 프로젝트의 **각 태스크별로** 실행 계획을 보고한다.

```
══════════════════════════════════════════════════════════════
  프로젝트 4: 초기 콘텐츠 제작 및 론칭
══════════════════════════════════════════════════════════════

  Task 010: 론칭용 밈 콘텐츠 30개 제작
  ─────────────────────────────────────────────────────────
  담당: 밈 콘텐츠 제작 전문가 (expert-004)
  Tool: Python PIL + matplotlib (차트 밈, 텍스트 밈)
  출력: PNG 파일 30개 (1080x1080)
  의존: task-004 (밈 소재), task-009 (비주얼 가이드라인)

  → 이대로 진행할까요?
  → 레퍼런스 첨부하실 게 있으면 알려주세요.
  → Tool을 변경하거나 추가하고 싶으시면 말씀해주세요.
  ─────────────────────────────────────────────────────────

  Task 011: 각 포스트별 캡션 및 해시태그 작성
  ─────────────────────────────────────────────────────────
  담당: 밈 콘텐츠 제작 전문가 (expert-004)
  Tool: Read + Write
  출력: 캡션/해시태그 목록 (Markdown)
  의존: task-010 (밈 콘텐츠), task-006 (해시태그 전략)

  → 이대로 진행할까요?
  ─────────────────────────────────────────────────────────

  Task 012: 계정 론칭 체크리스트 검토 및 승인
  ─────────────────────────────────────────────────────────
  담당: 밈 콘텐츠 제작 전문가 (expert-004)
  Tool: Read + Write + Glob
  출력: 체크리스트 문서 (Markdown)
  의존: task-007, task-008, task-011
  참고: CEO 최종 승인 필요 (APPROVAL 태스크)

  → 이대로 진행할까요?
  ─────────────────────────────────────────────────────────
```

#### ⑧ CEO 개입 (Task-Level Intervention)

CEO는 각 태스크에 대해:

**a) 승인**: "OK, 그대로 진행해"

**b) Tool 변경**:
```
CEO: "task-010은 Imgflip API로 클래식 밈 템플릿 써줘.
      그리고 Gemini API로 커스텀 일러스트도 만들어줘."
→ Tool 추가: Imgflip API, GEMINI_GENERATE_IMAGE
→ Tool 제거: (필요시)
```

**c) 레퍼런스 추가**:
```
CEO: "이 이미지들 참고해서 만들어줘" (파일/URL/메모 첨부)
→ 레퍼런스 분석 → Expert에게 전달
```

**d) 지시사항 추가**:
```
CEO: "PNG 파일로 출력해줘. HTML 말고.
      AI가 만든 티 나면 안 돼."
→ Expert 프롬프트에 지시사항 추가
```

**e) 일괄 승인**:
```
CEO: "전부 OK"
→ 모든 태스크 승인 → 실행 시작
```

#### ⑨ 레퍼런스 분석 + Tool 조정 (v3 "Analyze Once, Use Everywhere" 계승)

CEO가 레퍼런스를 첨부한 경우, **v3의 Tool Agent 분석 로직을 그대로 사용**하여 1번만 깊게 분석하고 `analyzed_content`에 저장한다. 이후 Expert는 이 분석 결과를 **읽기만** 하고 레퍼런스를 다시 접속/분석하지 않는다.

**이 단계는 CEO가 레퍼런스를 첨부하거나 Tool 변경을 요청한 경우에만 실행** (승인만 했으면 건너뜀)

```
CEO가 레퍼런스 첨부 또는 Tool 변경 요청
     │
     ▼
Tool Agent 깊은 분석 (v3 동일 프로세스):
  1. 레퍼런스 타입 + 의도(intent) 분석
     ├─ URL → WebFetch로 실제 내용 확인
     ├─ 이미지 → Read로 시각 분석 (색상, 레이아웃, 분위기)
     ├─ 파일 → 확장자 + 내용 분석 (구조, 필드)
     └─ 메모 → 키워드 추출 (핵심 요구사항)
  2. analyzed_content에 분석 결과 저장:
     ├─ fetched_summary: 분석 요약
     ├─ key_findings: 핵심 발견 사항
     ├─ style_elements: 색상, 레이아웃, 타이포그래피
     ├─ structure_elements: 페이지/문서 구조
     └─ actionable_insights: 구체적 활용 지침
  3. direction(방향성) 도출 — 레퍼런스 종합하여 한 문장 요약
  4. 태스크 description 업데이트 (더 상세한 가이드 추가)
     ├─ 기존: "론칭용 밈 콘텐츠 30개 제작"
     └─ 업데이트: "클립아트+차트 스타일, Imgflip 클래식 템플릿,
                  Gemini 커스텀 일러스트 활용. 개발자 공감 소재,
                  AI 티 최소화. PNG 1080x1080 출력."
  5. CEO 요청 Tool 가용성 확인 (인벤토리에서 조회)
  6. Expert의 dynamic_tools에 추가
  7. 실행 계획 업데이트
     │
     ▼
Expert: analyzed_content 읽기 → 바로 작업 수행 (재분석 불필요)
```

**저장 위치**: 분석 결과는 `task_assignments.json`의 해당 태스크 항목에 저장된다.

```json
{
  "task_id": "task-010",
  "ceo_references": [
    {
      "type": "image",
      "value": "/path/to/ref_clipart_chart_meme.png",
      "intent": "style",
      "note": "이런 느낌으로",
      "analyzed_content": {
        "fetched_summary": "클립아트 캐릭터 + 막대 차트 조합 밈",
        "key_findings": ["심플한 일러스트 스타일", "데이터 시각화 유머"],
        "style_elements": {"illustration": "clipart", "chart": "bar_chart", "colors": "pastel"},
        "actionable_insights": "matplotlib 차트 + 클립아트 이미지 합성, 밝은 파스텔 톤"
      }
    }
  ],
  "enriched_description": "클립아트+차트 스타일과 클래식 밈 템플릿을 혼합하여...",
  "direction": "개발자 공감 소재를 클립아트+차트 스타일로 제작, AI 느낌 최소화"
}
```

#### ⑩ 태스크 실행 (자동 병렬)

의존성 그래프를 기반으로 자동 병렬 실행:

```
의존성 분석:
  task-010: 의존 없음 (선행 태스크 모두 완료)
  task-011: task-010에 의존 → 대기
  task-012: task-011에 의존 → 대기

실행 순서:
  [병렬 가능] task-010 실행
  [대기]      task-010 완료 후 → task-011 실행
  [대기]      task-011 완료 후 → task-012 실행
```

만약 독립 태스크가 있으면 자동 병렬:
```
  task-004 (의존 없음) ─┐
  task-006 (의존 없음) ─┤ 자동 병렬!
                        ↓
  task-005 (task-004 의존) → 순차
```

#### ⑪ 결과 보고
- 태스크별 결과 요약
- 산출물 파일 경로
- 다음 프로젝트 안내

---

## 3. v3 → v4 핵심 변경점

| 항목 | v3 | v4 |
|------|----|----|
| **레퍼런스 수집 시점** | Phase 1 (백로그 직후, 전체) | **Phase 2 (프로젝트 실행 직전, 태스크별)** |
| **Tool 확정 시점** | Phase 1 (1회 확정) | **Phase 2 (태스크 실행 직전, 동적)** |
| **CEO 개입 시점** | 레퍼런스 1회 + 승인 1회 | **태스크별 Briefing + 개입** |
| **실행 투명성** | 실행 후 결과만 확인 | **실행 전 계획 확인 → 승인 → 실행** |
| **병렬 실행** | 수동 판단 | **의존성 그래프 기반 자동** |
| **HR 에이전트** | Tool 종속적 | **역량 기반 (Tool 동적 할당)** |
| **Tool Agent 역할** | 레퍼런스 분석 + Tool 추천 | **Tool 리스트업 + 실행 전 Tool 조정** |

---

## 4. 상태 파일 스키마 변경

### 4.1 변경되는 파일

#### task_references.json → **제거** (v3에서 삭제)
- 레퍼런스는 실행 시점에 수집되므로, 별도 상태 파일 불필요
- 대신 task_assignments.json 내에 per-task로 저장

#### tool_recommendations.json → **tool_inventory.json** (역할 변경)

v3의 3-tier 검증 + 웹 검색 + 마켓플레이스 검색 로직을 그대로 사용하여 생성한다.

```json
{
  "inventory_id": "inv_YYYYMMDD_NNN",
  "created_at": "ISO-8601",
  "verification_sources": [
    "builtin_check",
    "local_skills_scan",
    "mcp_json_check",
    "rube_search_tools",
    "rube_manage_connections",
    "web_search",
    "marketplace_search"
  ],
  "available_tools": {
    "builtin": [
      {"tool": "WebSearch", "status": "available"},
      {"tool": "WebFetch", "status": "available"},
      {"tool": "Read", "status": "available"},
      {"tool": "Write", "status": "available"},
      {"tool": "Edit", "status": "available"},
      {"tool": "Bash", "status": "available"},
      {"tool": "Glob", "status": "available"},
      {"tool": "Grep", "status": "available"}
    ],
    "skills": [
      {"tool": "/frontend-design", "status": "available", "description": "웹 UI 코드 생성"}
    ],
    "mcp_rube": [
      {"tool": "instagram", "status": "active", "account": "@cs_student_tips", "tools": ["INSTAGRAM_CREATE_MEDIA_CONTAINER", "INSTAGRAM_CREATE_POST", "..."]},
      {"tool": "gemini", "status": "active", "tools": ["GEMINI_GENERATE_IMAGE"]},
      {"tool": "canva", "status": "active", "tools": ["CANVA_CREATE_DESIGN"]},
      {"tool": "google_sheets", "status": "not_connected", "connect_url": "rube.app/marketplace"}
    ],
    "external_api": [
      {"tool": "imgflip_api", "status": "available", "confidence": "HIGH", "note": "무료 밈 템플릿 API, REST 호출", "source": "web_search"},
      {"tool": "kapwing_api", "status": "available", "confidence": "MEDIUM", "note": "밈/비디오 편집 API", "source": "web_search"}
    ]
  },
  "task_tool_defaults": {
    "task-001": {
      "recommended_tools": ["WebSearch", "WebFetch", "INSTAGRAM_GET_USER_INFO"],
      "combination_note": "경쟁사 계정 분석 후 인사이트 정리"
    },
    "task-010": {
      "recommended_tools": ["Bash", "GEMINI_GENERATE_IMAGE", "imgflip_api"],
      "combination_note": "Gemini 커스텀 이미지 + Imgflip 클래식 밈 + PIL 후처리"
    }
  }
}
```

#### tool_selections.json → **제거** (v3에서 삭제)
- CEO 승인은 태스크별로 Phase 2에서 처리

#### hired_agents.json (변경)

```json
{
  "agents": [
    {
      "agent_id": "expert-004",
      "role_name": "밈 콘텐츠 제작 전문가",
      "capabilities": ["image_creation", "meme_design", "copywriting"],
      "base_tools": ["Read", "Write", "WebSearch", "Bash"],
      "dynamic_tools": [],
      "assigned_tasks": ["task-010", "task-011", "task-012"]
    }
  ]
}
```

#### task_assignments.json (확장)

```json
{
  "assignments": [
    {
      "task_id": "task-010",
      "agent_id": "expert-004",
      "project_id": "proj-004",
      "default_tools": ["Read", "Write", "WebSearch", "Bash"],
      "ceo_tools": [],
      "ceo_references": [],
      "ceo_instructions": "",
      "status": "pending",
      "briefing_approved": false
    }
  ]
}
```

태스크 실행 전 CEO 개입 후 업데이트:

```json
{
  "task_id": "task-010",
  "default_tools": ["Read", "Write", "WebSearch", "Bash"],
  "ceo_tools": ["imgflip_api", "GEMINI_GENERATE_IMAGE"],
  "ceo_references": [
    {
      "type": "image",
      "value": "/path/to/reference.png",
      "intent": "style",
      "note": "이런 느낌으로 만들어줘"
    }
  ],
  "ceo_instructions": "PNG 파일로 출력. AI 만든 티 나면 안 됨. 클래식 밈 템플릿 활용.",
  "briefing_approved": true
}
```

---

## 5. 상태 전이 (Phase)

```
session.json의 phase 값:

Phase 1:
  goal_input → backlog_creation → tool_inventory → hiring → assignment → ready_to_execute

Phase 2 (프로젝트 단위 반복):
  project_selection → task_briefing → ceo_review → executing → project_completed
  → project_selection (다음 프로젝트)

전체 완료:
  all_completed
```

---

## 6. 병렬 실행 전략

### 6.1 Phase 1 순차

```
② RM 백로그 생성
     ↓
③ Tool Agent: Tool 인벤토리 생성 (3-tier 검증)
     ↓
④ HR: 인벤토리 참고하여 Expert 생성 (③ 결과 의존)
     ↓
⑤ RM 할당
```

> ③→④는 순차 실행이다. HR이 에이전트를 만들 때 어떤 Tool이 사용 가능한지 알아야
> 실현 가능한 역량을 부여할 수 있기 때문이다.

### 6.2 Phase 2 자동 병렬

의존성 그래프에서 "의존 없는 태스크"를 동시에 실행:

```python
# 의사 코드
def execute_project(tasks, dependency_graph):
    completed = set()
    while not all_completed(tasks):
        # 의존성이 모두 충족된 태스크 찾기
        ready = [t for t in tasks
                 if t.status == 'approved'
                 and all(dep in completed for dep in t.dependencies)]

        if len(ready) == 1:
            execute(ready[0])  # 단일 실행
        elif len(ready) > 1:
            parallel_execute(ready)  # 자동 병렬!

        completed.update(ready)
```

### 6.3 속도 최적화

| 전략 | 적용 대상 | 예상 효과 |
|------|----------|----------|
| 경량 모델 (haiku) | 단순 문서 작성, 목록 정리 | 2~3배 빠름 |
| 프롬프트에 요약 포함 | 이전 태스크 결과 전달 | Read 호출 감소 |
| 독립 태스크 병렬 | 의존성 없는 태스크들 | 동시 실행 |
| 메인 에이전트 직접 처리 | 단순 파일 작성 등 | Subagent 오버헤드 제거 |

---

## 7. Task Briefing 인터페이스 예시

### 7.1 기본 Briefing

```
══════════════════════════════════════════════════════════════
  프로젝트 4: 초기 콘텐츠 제작 및 론칭
  실행 계획 (3 tasks)
══════════════════════════════════════════════════════════════

  [1] Task 010: 론칭용 밈 콘텐츠 30개 제작
      담당: 밈 콘텐츠 제작 전문가
      Tool: Python PIL + matplotlib
      출력: PNG 30개 (1080x1080)

  [2] Task 011: 캡션 및 해시태그 작성
      담당: 밈 콘텐츠 제작 전문가
      Tool: Read + Write
      출력: Markdown 문서

  [3] Task 012: 론칭 체크리스트 (CEO 승인 필요)
      담당: 밈 콘텐츠 제작 전문가
      Tool: Read + Write + Glob
      출력: 체크리스트 문서

──────────────────────────────────────────────────────────────
  수정하실 태스크가 있으면 번호를 말씀해주세요.
  레퍼런스를 첨부하시려면 "task-010에 [URL/파일/메모] 추가"
  Tool을 변경하시려면 "task-010은 Imgflip API 써줘"
  전체 OK면 "승인" 또는 "실행"
══════════════════════════════════════════════════════════════
```

### 7.2 CEO 개입 예시

```
CEO: "task-010은 Imgflip API로 클래식 밈 만들고,
      Gemini로 커스텀 일러스트도 만들어줘.
      이 이미지들 참고해" (이미지 첨부)

→ 업데이트:
  [1] Task 010: 론칭용 밈 콘텐츠 30개 제작  [수정됨]
      담당: 밈 콘텐츠 제작 전문가
      Tool: Imgflip API + Gemini 이미지 생성 + PIL    ← 변경
      레퍼런스: CEO 제공 이미지 4개 (style)             ← 추가
      지시: PNG 출력, AI 티 제거, 클래식 밈 활용        ← 추가
      출력: PNG 30개 (1080x1080)

CEO: "OK 승인"
→ 실행 시작
```

---

## 8. 에이전트별 역할 변경

### 8.1 Tool Agent (v3 → v4)

| | v3 | v4 |
|---|---|---|
| 역할 | 레퍼런스 분석 + Tool 추천 | **Tool 인벤토리 관리 + 실행 전 레퍼런스 분석/Tool 조정** |
| 실행 시점 | Phase 1 (1회) | Phase 1 (인벤토리) + **Phase 2 (레퍼런스 분석 + Tool 조정)** |
| 검증 로직 | 3-tier (builtin → skills → MCP) + 웹 검색 + 마켓플레이스 | **동일** (v3 로직 계승) |
| 레퍼런스 분석 | Phase 1에서 전체 분석 | **Phase 2에서 태스크별 Just-In-Time 분석** |
| 분석 방식 | Analyze Once, Use Everywhere | **동일** (analyzed_content 저장 → Expert가 읽기만) |
| 출력 | tool_recommendations.json | Phase 1: tool_inventory.json / Phase 2: task_assignments.json 내 analyzed_content |

### 8.2 HR Agent (v3 → v4)

| | v3 | v4 |
|---|---|---|
| 에이전트 정의 | Tool 종속적 | **역량 기반** |
| Tool 할당 | 고용 시 확정 | **base_tools + dynamic_tools** |
| 유연성 | 낮음 (Tool 변경 시 재고용) | **높음 (실행 시 Tool 추가/제거)** |

### 8.3 RM Agent (v3 → v4)

| | v3 | v4 |
|---|---|---|
| 의존성 관리 | 암시적 | **명시적 dependency_graph** |
| 병렬 판단 | 오케스트레이터 수동 | **dependency_graph 기반 자동** |

---

## 9. 워크플로우 비교 요약

### v2 → v3 → v4 진화

```
v2 (Tool-Driven):
  CEO가 Tool 선택 → Agent 검증 → 실행
  문제: CEO에게 Tool 지식 요구

v3 (Reference-Driven):
  CEO가 레퍼런스 제공 → Agent 분석/추천 → CEO 승인 → 실행
  문제: 레퍼런스 일괄 수집 UX, 실행 전 투명성 부족

v4 (Interactive Execution):
  Agent가 계획 보고 → CEO가 태스크별 승인/수정/레퍼런스 → 실행
  핵심: "한 번에 좋은 결과물" = 실행 전 충분한 소통
```

---

## 10. 구현 우선순위

### Phase 1 (즉시 적용 가능)
1. Task Briefing 인터페이스 구현 (오케스트레이터 스킬 수정)
2. task_assignments.json에 ceo_tools, ceo_references, ceo_instructions 필드 추가
3. dependency_graph 기반 자동 병렬 실행

### Phase 2 (점진적 개선)
4. Tool Agent 역할을 인벤토리 관리로 변경
5. HR 에이전트 역량 기반 생성으로 변경
6. 경량 태스크 haiku 모델 자동 선택

### Phase 3 (최적화)
7. Subagent 속도 최적화 (프롬프트 요약 포함, Read 최소화)
8. 태스크 결과 캐싱 (같은 프로젝트 내 공유)
9. CEO 개입 패턴 학습 (자주 쓰는 Tool/레퍼런스 자동 추천)
