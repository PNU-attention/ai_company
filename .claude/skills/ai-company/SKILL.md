---
name: ai-company
description: "AI Company 멀티 에이전트 시스템 시뮬레이션. CEO가 목표를 입력하면, Tool Agent가 인벤토리를 생성하고 HR이 역량 기반으로 Expert를 고용합니다. 프로젝트 실행 전 태스크별 Task Briefing으로 CEO가 Tool/레퍼런스/지시사항을 검토·승인한 뒤, Expert가 자동 병렬로 실행합니다."
---

# AI Company v4 - Interactive Execution Multi-Agent System

CEO(사용자)가 목표를 입력하면, 에이전트들이 협업하여 목표를 달성하는 시스템입니다.
v4의 핵심은 **Task Briefing** — 태스크 실행 전에 CEO가 "누가, 어떤 Tool로, 어떻게"를 검토하고 승인합니다.

## 워크플로우 (v4)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 1: 계획 수립                            │
├─────────────────────────────────────────────────────────────────┤
│  ① CEO 목표 입력                                                │
│       ↓                                                         │
│  ② RM: 백로그 생성 (dependency_graph 포함)                      │
│       ↓                                                         │
│  ③ Tool Agent: Tool 인벤토리 생성 (3-tier 검증)                 │
│       ↓                                                         │
│  ④ HR: 인벤토리 참고하여 역량 기반 Expert 생성                  │
│       ↓                                                         │
│  ⑤ RM: Expert 할당 + 기본 Tool 배정                             │
├─────────────────────────────────────────────────────────────────┤
│                    Phase 2: 프로젝트 실행 (반복)                 │
├─────────────────────────────────────────────────────────────────┤
│  ⑥ CEO: 실행할 프로젝트 선택                                    │
│       ↓                                                         │
│  ⑦ 태스크별 실행 계획 보고 (Task Briefing)                      │
│       ↓                                                         │
│  ⑧ CEO: 태스크별 승인 / Tool 변경 / 레퍼런스 추가 / 지시사항    │
│       ↓                                                         │
│  ⑨ (필요시) Tool Agent 레퍼런스 분석 + Tool 조정                │
│       ↓                                                         │
│  ⑩ 태스크 실행 + QA 검증 (dependency_graph 기반 자동 병렬)      │
│      expert(background) → 완료 즉시 qa-agent → 병렬 QA 실행    │
│       ↓                                                         │
│  ⑪ 결과 보고 (QA 통과한 결과물만) → 다음 프로젝트 ⑥으로        │
└─────────────────────────────────────────────────────────────────┘
```

## 실행 방법

### 명령어
- `/ai-company` - 현재 상태 확인 및 계속 진행
- `/ai-company init` - 새 세션 시작
- `/ai-company status` - 현재 상태 요약
- `/ai-company reset` - 모든 상태 초기화

## Step-by-Step 가이드

### Phase 0: 환경 확인 (시작 전 필수)

**`/ai-company init` 실행 시 가장 먼저 수행합니다.**

```
1. company/state/ 폴더 존재 여부 확인 → 없으면 생성

2. .mcp.json 확인 → Rube 설정 여부 확인
   - Rube 설정 있음 → 5번 단계(Rube 모니터링)로 진행
   - Rube 설정 없음 → "외부 서비스(이미지 생성, SNS 등)가 필요하면 .mcp.json에 Rube를 추가하세요."

3. 기존 session.json 확인
   - 있음 → "진행 중인 세션이 있습니다. 이어서 진행하시겠습니까? (Y/N)"
   - 없음 → 새 세션 시작

4. 실행 모드 선택 (새 세션 시작 시)
   ┌─────────────────────────────────────────────────────┐
   │  실행 모드를 선택해주세요:                            │
   │                                                     │
   │  [1] dry_run  — 외부 API 없이 전체 흐름만 검증 (권장) │
   │       외부 서비스(SNS, 이메일 등) 실제 호출 없음       │
   │       파일 생성, 웹 검색은 정상 작동                  │
   │                                                     │
   │  [2] production — 실제 외부 서비스 연동               │
   │       Rube/API를 통해 실제 게시/발송 등 수행           │
   └─────────────────────────────────────────────────────┘

   → session.json에 execution_mode 저장
   → dry_run 선택 시 dry_run_config: {mock_external_apis: true, generate_files: true, web_search: true}

5. Rube 연결 상태 모니터링 (Rube 설정 있는 경우 항상 실행)
   ┌──────────────────────────────────────────────────────────────┐
   │  Rube 연결 상태 자동 확인                                     │
   │                                                              │
   │  ⚠️ IMPORTANT: Subagent는 MCP 툴에 접근할 수 없습니다.       │
   │  Rube 호출은 반드시 오케스트레이터(메인 Claude)가 직접 수행   │
   │  합니다. tool-agent에 위임하지 마세요.                        │
   │                                                              │
   │  [기존 인벤토리 있는 경우]                                    │
   │  1. tool_inventory.json의 mcp_rube 목록 읽기                 │
   │  2. 오케스트레이터가 직접 RUBE_MANAGE_CONNECTIONS 호출        │
   │     (toolkits: 인벤토리에 있는 toolkit 이름 목록)             │
   │  3. 변경 감지 → tool_inventory.json 직접 패치                │
   │   ✅ 새로 연결된 앱 → 인벤토리 자동 갱신 + CEO 알림          │
   │   ⚠️ 연결이 끊긴 앱 → 인벤토리 자동 갱신 + CEO 경고         │
   │                                                              │
   │  [인벤토리 없는 경우]                                        │
   │  → 건너뜀 (Step 3에서 신규 생성 시 오케스트레이터가 직접 확인)│
   └──────────────────────────────────────────────────────────────┘

   오케스트레이터가 RUBE_MANAGE_CONNECTIONS를 직접 호출하고
   tool_inventory.json을 직접 Edit 툴로 패치합니다.

   연결 상태 변경 보고 형식:
   ══════════════════════════════════════════════════════════════
     Rube 연결 상태 갱신 완료
   ══════════════════════════════════════════════════════════════
     변경 감지:
       ✅ slack    : not_connected → ACTIVE  (새로 연결됨)
       ⚠️ gemini  : ACTIVE → not_connected  (연결 끊김 — 주의!)

     영향받는 태스크:
       task-007 (이미지 생성): gemini가 필요합니다. 재연결 후 실행하세요.

     변경 없음: instagram, canva
   ══════════════════════════════════════════════════════════════

   연결 끊긴 앱이 있는 경우 CEO에게 rube.app/marketplace에서 재연결 안내.
   변경 없으면 조용히 진행.
```

### Step 1: CEO 목표 입력

사용자에게 목표를 입력받습니다:

```
══════════════════════════════════════════════════════════════
   AI Company v4 - Interactive Execution Multi-Agent System
══════════════════════════════════════════════════════════════

안녕하세요, CEO님! 회사의 목표를 입력해주세요.

예시:
- "신규 SaaS 제품의 랜딩 페이지와 마케팅 자료 제작"
- "경쟁사 분석 후 블로그 콘텐츠 20개 작성 및 발행"
- "고객 응대 자동화 시스템 구축"
- "유튜브 채널 기획부터 첫 영상 10개 업로드까지"

목표:
```

**ceo-agent 호출**: 목표와 실행 모드를 JSON으로 저장

```bash
# company/state/session.json
{
  "session_id": "ses_YYYYMMDD_NNN",
  "phase": "goal_input",
  "execution_mode": "dry_run",
  "dry_run_config": {
    "mock_external_apis": true,
    "generate_files": true,
    "web_search": true
  },
  "created_at": "ISO-8601"
}

# company/state/ceo_goal.json
{
  "goal": "입력받은 목표",
  "created_at": "ISO-8601"
}
```

### Step 2: RM 백로그 생성

**rm-agent 호출**: 목표를 프로젝트/태스크로 분해 + **dependency_graph 생성**

분석 시 고려사항:
1. 목표 달성에 필요한 프로젝트 식별
2. 각 프로젝트를 구체적 태스크로 분해
3. **태스크 간 의존성을 명시적 dependency_graph로 표현**
4. 각 태스크에 필요한 Tool 카테고리 제안

```
══════════════════════════════════════════════════════════════
   RM: 백로그 생성 완료
══════════════════════════════════════════════════════════════

프로젝트 1: 시장 조사 및 경쟁사 분석
   ├─ Task 001: 경쟁사 리서치        [RESEARCH] 의존: 없음
   ├─ Task 002: 타겟 페르소나 정의   [DOCUMENT] 의존: task-001
   └─ Task 003: 차별화 전략 수립     [DOCUMENT] 의존: task-001, task-002

프로젝트 2: 콘텐츠 전략
   ├─ Task 004: 콘텐츠 소재 수집     [RESEARCH] 의존: 없음
   ├─ Task 005: 콘텐츠 캘린더 수립   [DOCUMENT] 의존: task-004
   └─ Task 006: 해시태그 전략        [RESEARCH] 의존: task-001

의존성 그래프:
  task-001: []  ←── 독립 (병렬 가능)
  task-004: []  ←── 독립 (병렬 가능)
  task-002: [task-001]
  task-006: [task-001]
  task-003: [task-001, task-002]
  task-005: [task-004]
```

저장: `company/state/backlog.json` (dependency_graph 포함)

### Step 3: Tool Agent 인벤토리 생성

⚠️ **IMPORTANT: Rube 연결 확인은 오케스트레이터가 직접 수행합니다.**
Subagent(tool-agent)는 MCP 툴에 접근할 수 없으므로, Step 3는 다음 순서로 진행합니다:

**Step 3-A (오케스트레이터 직접 실행): Rube 연결 상태 사전 확인**
1. 백로그의 `suggested_tool_categories`를 분석하여 필요한 Rube 앱 카테고리 파악
2. 오케스트레이터가 직접 `RUBE_SEARCH_TOOLS` 호출 (필요한 카테고리별 검색)
3. 오케스트레이터가 직접 `RUBE_MANAGE_CONNECTIONS` 호출 (연결 상태 확인)
4. 확인된 연결 상태 결과를 변수로 저장

**Step 3-B (tool-agent 호출): 나머지 인벤토리 생성**
- tool-agent에게 Step 3-A에서 확인한 Rube 연결 상태를 프롬프트에 직접 포함하여 전달:
  ```
  "다음 Rube 앱 연결 상태를 오케스트레이터가 사전 확인했습니다.
   이 값을 그대로 인벤토리에 기록하세요 (재확인 불필요):
   instagram: ACTIVE (account: @cs_student_tips, id: 12345)
   gemini: ACTIVE
   canva: not_connected
   ..."
  ```
- tool-agent는 Built-in/Skills 체크 + 외부 API 웹 검색만 수행
- Rube 연결 상태는 오케스트레이터가 전달한 값을 그대로 사용

```
══════════════════════════════════════════════════════════════
   Tool Agent: Tool 인벤토리 생성 완료
══════════════════════════════════════════════════════════════

Built-in (8): WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep
Skills: /frontend-design, /mcp-builder, /pollinations-ai, /image-generation-mcp
        + .claude/skills/ 스캔으로 추가 스킬 자동 발견
MCP/Rube (오케스트레이터 사전 확인 결과):
  - gemini: ACTIVE
  - instagram: ACTIVE (@계정명)
  - slack: not_connected
Vibe Index 검색 (Built-in/Rube로 커버 안 되는 카테고리):
  API: https://vibeindex.ai/api/resources?ref=skill-vibeindex&search={키워드}&pageSize=10
  발견된 추가 툴: [검색 결과 기반]

태스크별 기본 Tool 추천:
  [각 태스크 ID]: [백로그 suggested_tool_categories 기반 추천 도구]
```

저장: `company/state/tool_inventory.json`

### Step 4: HR 에이전트 고용

**hr-agent 호출**: Tool 인벤토리를 참고하여 **역량 기반** Expert 생성

```
══════════════════════════════════════════════════════════════
   HR: 에이전트 고용 완료
══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────┐
│ Expert 1: 시장 조사 전문가                                    │
├──────────────────────────────────────────────────────────────┤
│ 역량: research, data_analysis                                │
│ 실현 가능 Tool: WebSearch, WebFetch, INSTAGRAM_GET_USER_INFO │
│ 기본 Tool: Read, Write, WebSearch                            │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Expert 4: 밈 콘텐츠 제작 전문가                               │
├──────────────────────────────────────────────────────────────┤
│ 역량: image_creation, meme_design, copywriting               │
│ 실현 가능 Tool: GEMINI_GENERATE_IMAGE, imgflip_api, PIL      │
│ 기본 Tool: Read, Write, WebSearch, Bash                      │
└──────────────────────────────────────────────────────────────┘
```

저장: `company/state/hired_agents.json`

### Step 5: RM 태스크 할당

**rm-agent 호출**: Expert에 태스크 할당 + 인벤토리의 task_tool_defaults 기반 기본 Tool 배정

저장: `company/state/task_assignments.json`

session.json → phase: `ready_to_execute`

### Step 6: CEO 프로젝트 선택

```
══════════════════════════════════════════════════════════════
   실행 준비 완료!
══════════════════════════════════════════════════════════════

실행할 프로젝트를 선택해주세요:

  [1] 시장 조사 및 경쟁사 분석 (3 tasks)
  [2] 콘텐츠 전략 및 소재 준비 (3 tasks)
  [3] 계정 설정 및 브랜딩 (3 tasks)
  [4] 초기 콘텐츠 제작 및 론칭 (3 tasks)
  [5] 성장 전략 및 커뮤니티 빌딩 (3 tasks)
  [6] 운영 자동화 및 분석 시스템 (3 tasks)

선택:
```

### Step 7: Task Briefing (v4 핵심)

CEO가 프로젝트를 선택하면, **각 태스크별로 실행 계획을 보고**합니다.

```
══════════════════════════════════════════════════════════════
  프로젝트 N: [프로젝트명]
  실행 계획 (K tasks)
══════════════════════════════════════════════════════════════

  [1] Task XXX: [태스크명]
      담당: [역할명] (expert-00N)
      Tool: [task_assignments.json의 default_tools 기반]
      출력: [expected_outputs]
      의존: [선행 태스크]

  [2] Task XXX: [태스크명]
      ...

──────────────────────────────────────────────────────────────
  수정하실 태스크가 있으면 번호를 말씀해주세요.
  레퍼런스를 첨부하시려면 "task-XXX에 [URL/파일/메모] 추가"
  Tool을 변경하시려면 "task-XXX는 [다른 Tool] 써줘"
  전체 OK면 "승인" 또는 "실행"
══════════════════════════════════════════════════════════════
```

### Step 8: CEO 태스크별 승인/수정

CEO의 개입 유형:

| 유형 | 예시 | 결과 |
|------|------|------|
| **승인** | "OK", "전부 승인" | briefing_approved = true → 실행 |
| **Tool 변경** | "task-010은 Imgflip API 써줘" | ceo_tools 업데이트 |
| **레퍼런스 추가** | "이 이미지 참고해" (파일/URL/메모) | → Step 9 분석 |
| **지시사항** | "PNG 출력, AI 티 내지 마" | ceo_instructions 업데이트 |
| **일괄 승인** | "전부 OK" | 모든 태스크 한번에 승인 |

CEO 개입 예시:
```
CEO: "task-XXX는 [특정 Tool]로 해줘.
      이거 참고해" (URL/이미지/파일 첨부)
      "[구체적 지시사항]"

→ 업데이트:
  [N] Task XXX: [태스크명]  [수정됨]
      담당: [역할명]
      Tool: [변경된 Tool]    ← 변경
      레퍼런스: CEO 제공 자료  ← 추가
      지시: [CEO 지시사항]    ← 추가

CEO: "OK 승인"
→ 실행 시작
```

저장: `company/state/task_assignments.json` (ceo_tools, ceo_references, ceo_instructions 업데이트)

### Step 9: 레퍼런스 분석 + Tool 조정 (필요시만)

CEO가 레퍼런스를 첨부한 경우에만 **tool-agent 호출**.
"Analyze Once, Use Everywhere" 원칙에 따라 분석합니다.

분석 프로세스:
1. 레퍼런스 타입 + 의도(intent) 분석
2. URL → WebFetch / 이미지 → Read / 파일 → Read / 메모 → 키워드 추출
3. analyzed_content에 저장 (fetched_summary, key_findings, style_elements, actionable_insights)
4. direction(방향성) 도출
5. enriched_description(상세 태스크 설명) 생성
6. CEO 요청 Tool 가용성 확인 (인벤토리에서 조회)

저장: `company/state/task_assignments.json` 내 해당 태스크의 ceo_references.analyzed_content, enriched_description, direction

### Step 10: 태스크 실행 + QA 검증 (자동 병렬)

**전용 expert-{id} 에이전트 호출 → qa-agent 검증** 사이클을 dependency_graph 기반으로 자동 병렬 실행합니다.

#### 10-1. 실행 준비: 에이전트 파일 + Rube 연결 확인

실행 전 `task_assignments.json`에서 태스크별 `agent_id`를 조회하고, 해당 에이전트 파일 존재 + Rube 연결 상태를 확인합니다.

```
task_assignments.json 읽기
  → task-010.agent_id = "expert-004"
  → .claude/agents/expert-004.md 존재 확인
    (agent_id가 이미 "expert-004" 형식이므로 파일명은 expert-004.md)

  에이전트 파일 없는 경우:
    → hr-agent를 재호출하여 해당 에이전트 파일 생성 후 재시도

Rube Tool 사용 여부 확인 (ceo_tools + default_tools):
  → Rube 앱이 포함된 경우: RUBE_MANAGE_CONNECTIONS 실시간 확인
    ├─ 모든 필요 앱 ACTIVE → 실행 진행
    ├─ 일부 앱 not_connected → CEO 인터럽트:
    │   "task-010에서 {tool}이 필요한데 연결이 끊겼습니다.
    │    rube.app/marketplace에서 재연결 후 실행하세요."
    └─ 재연결 후 CEO가 승인하면 → tool_inventory.json 갱신 후 실행
  → Rube 앱 없으면 → 확인 생략 (Built-in만 사용)
```

#### 10-2. 병렬 실행 그룹 추출

dependency_graph에서 현재 실행 가능한 태스크 그룹을 추출합니다.

```
dependency_graph 분석:
  "task-001": []        → 즉시 실행 가능 (독립)
  "task-004": []        → 즉시 실행 가능 (독립)
  "task-002": ["task-001"] → task-001 완료 후 실행 가능
  "task-005": ["task-004"] → task-004 완료 후 실행 가능

현재 실행 가능 그룹:
  Round 1: [task-001, task-004]  ← 동시 실행
  Round 2: [task-002, task-005]  ← 각 선행 태스크 완료 후
```

#### 10-3. 병렬 실행 (핵심 — Background + 즉시 QA)

**독립 태스크는 `run_in_background=true`로 실행하고, 각 expert 완료 시 즉시 qa-agent를 띄웁니다.**
Expert와 QA가 파이프라인처럼 연결되어, 다른 expert가 아직 실행 중이어도 완료된 태스크의 QA가 즉시 시작됩니다.

```
[단일 응답에서 background로 동시 시작 — 즉시 반환]

  Agent(subagent_type: "expert-001", run_in_background: true)
    "company/state/task_assignments.json의 task-001 태스크를 실행하세요"

  Agent(subagent_type: "expert-002", run_in_background: true)
    "company/state/task_assignments.json의 task-004 태스크를 실행하세요"

  → 두 expert가 백그라운드에서 독립적으로 실행됨
  → 오케스트레이터는 즉시 반환 (블로킹 없음)
  → 각 expert 완료 시 시스템이 오케스트레이터에게 알림(notification) 전송
```

**호출 규칙:**
- `agent_id`를 `task_assignments[task_id].agent_id`에서 조회 (예: "expert-001")
- 에이전트 파일: `.claude/agents/{agent_id}.md` (HR이 생성한 파일)
- 호출: `Agent(subagent_type: "{agent_id}", run_in_background: true, prompt: "task_assignments.json의 {task_id} 태스크를 실행하세요")`
- 독립 태스크는 **반드시 단일 메시지에서 여러 Agent 호출 (background)** (순차 호출 금지)

#### 10-4. 즉시 QA 파이프라인 (핵심 개선)

각 expert 완료 알림을 받는 즉시 qa-agent를 호출합니다. **다른 expert의 완료를 기다리지 않습니다.**
QA 에이전트는 여러 인스턴스가 동시에 실행될 수 있습니다.

```
[파이프라인 실행 흐름]

  T+0:   expert-001 background 시작 (task-001)  ─┐ 동시 시작
         expert-002 background 시작 (task-004)  ─┘

  T+10분: expert-001 완료 알림 수신
         → Agent("qa-agent", "task-001 QA 검증해줘")  ← 즉시! expert-002 기다리지 않음

  T+15분: expert-002 완료 알림 수신
         → Agent("qa-agent", "task-004 QA 검증해줘")  ← 즉시! qa-001과 병렬 실행

  ✅ task-001 QA → score 82 → 승인 → task-002 unlock → expert-001 background 재시작
  ✅ task-004 QA → score 75 → 승인 → task-005 unlock → expert-002 background 재시작
```
══════════════════════════════════════════════════════════════
  프로젝트 4: 초기 콘텐츠 제작 및 론칭
  실행 계획 (3 tasks)
══════════════════════════════════════════════════════════════

  [1] Task 010: 론칭용 밈 콘텐츠 30개 제작
      담당: 밈 콘텐츠 제작 전문가 (expert-004)
      Tool: Gemini 이미지 생성 + Imgflip API + PIL
      출력: PNG 30개 (1080x1080)
      의존: task-004 (밈 소재), task-009 (비주얼 가이드라인)

  [2] Task 011: 캡션 및 해시태그 작성
      담당: 밈 콘텐츠 제작 전문가 (expert-004)
      Tool: Read + Write
      출력: Markdown 문서
      의존: task-010, task-006

  [3] Task 012: 론칭 체크리스트 (CEO 승인 필요)
      담당: 밈 콘텐츠 제작 전문가 (expert-004)
      Tool: Read + Write + Glob
      출력: 체크리스트 문서
      의존: task-007, task-008, task-011

──────────────────────────────────────────────────────────────
  수정하실 태스크가 있으면 번호를 말씀해주세요.
  레퍼런스를 첨부하시려면 "task-010에 [URL/파일/메모] 추가"
  Tool을 변경하시려면 "task-010은 Imgflip API 써줘"
  전체 OK면 "승인" 또는 "실행"
══════════════════════════════════════════════════════════════
```

### Step 8: CEO 태스크별 승인/수정

CEO의 개입 유형:

| 유형 | 예시 | 결과 |
|------|------|------|
| **승인** | "OK", "전부 승인" | briefing_approved = true → 실행 |
| **Tool 변경** | "task-010은 Imgflip API 써줘" | ceo_tools 업데이트 |
| **레퍼런스 추가** | "이 이미지 참고해" (파일/URL/메모) | → Step 9 분석 |
| **지시사항** | "PNG 출력, AI 티 내지 마" | ceo_instructions 업데이트 |
| **일괄 승인** | "전부 OK" | 모든 태스크 한번에 승인 |

CEO 개입 예시:
```
CEO: "task-010은 Imgflip API로 클래식 밈 만들고,
      Gemini로 커스텀 일러스트도 만들어줘.
      이 이미지들 참고해" (이미지 첨부)
      "PNG로 출력해줘. AI 만든 티 나면 안 돼."

→ 업데이트:
  [1] Task 010: 론칭용 밈 콘텐츠 30개 제작  [수정됨]
      담당: 밈 콘텐츠 제작 전문가
      Tool: Imgflip API + Gemini 이미지 생성 + PIL    ← 변경
      레퍼런스: CEO 제공 이미지 (style)                 ← 추가
      지시: PNG 출력, AI 티 제거                        ← 추가

CEO: "OK 승인"
→ 실행 시작
```

저장: `company/state/task_assignments.json` (ceo_tools, ceo_references, ceo_instructions 업데이트)

### Step 9: 레퍼런스 분석 + Tool 조정 (필요시만)

CEO가 레퍼런스를 첨부한 경우에만 **tool-agent 호출**.
"Analyze Once, Use Everywhere" 원칙에 따라 분석합니다.

분석 프로세스:
1. 레퍼런스 타입 + 의도(intent) 분석
2. URL → WebFetch / 이미지 → Read / 파일 → Read / 메모 → 키워드 추출
3. analyzed_content에 저장 (fetched_summary, key_findings, style_elements, actionable_insights)
4. direction(방향성) 도출
5. enriched_description(상세 태스크 설명) 생성
6. CEO 요청 Tool 가용성 확인 (인벤토리에서 조회)

**QA 실패 시 재시도 흐름:**
```
[1] expert-{agent_id} background 실행 (태스크 실행)
      ↓ 완료 알림 수신
[2] Agent("qa-agent", "task-XXX QA 검증해줘")  ← 즉시 호출
      ↓ score ≥ 70
[3] ✅ 승인 → task status = "qa_approved" → 다음 의존 태스크 unlock
      ↓ score < 70 (qa_round < 3)
[4] ❌ 반려 → qa_rejection_feedback 포함하여 expert-{agent_id} background 재호출
      ↓ 완료 알림 → qa-agent 즉시 재호출 (반복)
      ↓ qa_round ≥ 3
[5] 🚨 CEO 인터럽트 (qa_escalation) → 대기
```

**오케스트레이터의 역할:**
1. `task_assignments.json`에서 `agent_id` 조회 → 해당 expert-{id} 에이전트 특정
2. 독립 태스크: **단일 메시지에서 여러 Agent(background) 동시 시작**
3. 각 expert 완료 알림 수신 즉시 → qa-agent 호출 (다른 expert 완료 대기 금지)
4. QA 반려 시 → `retry_instructions`와 함께 동일 expert-{id} background 재호출
5. QA 승인 시 → dependency_graph에서 해당 태스크를 "완료"로 표시 → 다음 가능한 태스크 unlock
6. QA가 통과된 태스크만 최종 완료로 처리

```
══════════════════════════════════════════════════════════════
   실행 중: 프로젝트 N - [프로젝트명]
══════════════════════════════════════════════════════════════

의존성 분석 결과:
  Round 1 (병렬): task-001 (agent_id: expert-001), task-004 (agent_id: expert-002)
  Round 2 (순차): task-002 (task-001 완료 후), task-005 (task-004 완료 후)

[Round 1 - Background 병렬 시작]
  → Agent("expert-001", background=true, "task-001 실행") ─┐ 동시 시작, 즉시 반환
  → Agent("expert-002", background=true, "task-004 실행") ─┘

  [expert-001 완료 알림 수신 → 즉시 QA]
  → Agent("qa-agent", "task-001 QA")  ← expert-002 기다리지 않고 즉시!
  ✅ task-001 QA score 82 → 승인 → task-002 unlock

  [expert-002 완료 알림 수신 → 즉시 QA]  (qa-001과 병렬 실행 가능)
  → Agent("qa-agent", "task-004 QA")  ← 즉시!
  ✅ task-004 QA score 75 → 승인 → task-005 unlock

[Round 2 - unlock 후 즉시 background 시작]
  → Agent("expert-001", background=true, "task-002 실행") ─┐ 동시 시작
  → Agent("expert-002", background=true, "task-005 실행") ─┘
  (이하 동일 패턴 반복)
```

독립 태스크가 여러 개인 경우 자동 병렬:
```
[병렬 실행]
  task-004 (독립) ──┐
  task-006 (독립) ──┤ 동시 실행!
                    ↓
  task-005 (task-004 의존) → 순차
```

저장: `company/state/execution_log.json`

### Step 11: 결과 보고

```
══════════════════════════════════════════════════════════════
   프로젝트 완료 보고서
══════════════════════════════════════════════════════════════

프로젝트: 초기 콘텐츠 제작 및 론칭
상태: 완료

결과물:
  1. 밈 이미지 30개 (PNG 1080x1080)
     → company/outputs/memes/
  2. 캡션 및 해시태그 목록
     → company/outputs/task011_captions.md
  3. 론칭 체크리스트
     → company/outputs/task012_checklist.md

다음 프로젝트:
  [5] 성장 전략 및 커뮤니티 빌딩 (3 tasks)
  [6] 운영 자동화 및 분석 시스템 (3 tasks)

계속하시겠습니까? [다음 프로젝트] [종료]
```

## 상태 파일 구조 (v4)

```
company/state/
├── session.json              # 세션 정보 (phase, current_project)
├── ceo_goal.json             # CEO 목표
├── backlog.json              # RM 백로그 + dependency_graph
├── tool_inventory.json       # Tool 인벤토리
├── hired_agents.json         # 역량 기반 에이전트
├── task_assignments.json     # 할당 + CEO 승인/레퍼런스/지시사항
└── execution_log.json        # 실행 로그
```

## 상태 전이 (Phase)

```
Phase 1:
  goal_input → backlog_creation → tool_inventory → hiring → assignment → ready_to_execute

Phase 2 (프로젝트 단위 반복):
  project_selection → task_briefing → ceo_review → executing → project_completed
  → project_selection (다음 프로젝트)

전체 완료:
  all_completed
```

## 사용 가능한 Tool 목록

### Built-in (항상 사용 가능)
- `WebSearch` - 웹 검색
- `WebFetch` - 웹 페이지 내용 가져오기
- `Read` - 파일 읽기
- `Write` - 파일 쓰기
- `Edit` - 파일 편집
- `Bash` - 명령어 실행
- `Glob` - 파일 검색
- `Grep` - 텍스트 검색

### Skills (설치된 경우)
- `/frontend-design` - 웹 UI 코드 생성
- `/mcp-builder` - MCP 서버 생성
- `/pollinations-ai` - 무료 이미지 생성 (API 키 불필요, flux/turbo/stable-diffusion)
- `/image-generation-mcp` - Gemini MCP 기반 고품질 이미지 생성 (gemini-cli 필요)
- 기타 `.claude/skills/` 디렉토리의 스킬들

### MCP (설정된 경우)
- `rube` - 외부 서비스 통합 허브 (500+ 앱: Instagram, Gemini, Canva, Gmail, Slack 등)
- `figma` - Figma 디자인 연동
- `github` - GitHub 연동
- 기타 설정된 MCP 서버들

## 레퍼런스 시스템 (Just-In-Time)

v4에서 레퍼런스는 Phase 1이 아닌 **Phase 2 Task Briefing에서 태스크별로** 수집합니다.

**레퍼런스 타입:**
- URL: 웹 주소 (경쟁사, 참고 디자인 등)
- 이미지: 이미지 파일 경로 (목업, 스크린샷 등)
- 파일: 로컬 파일 경로 (보고서 템플릿, 데이터셋 등)
- 메모: 텍스트 메모 (스타일 가이드, 톤앤매너 등)

**레퍼런스 의도(intent):**
- `style`: "이런 스타일로 만들어줘"
- `content`: "이 내용을 참고해줘"
- `template`: "이 형식을 따라줘"
- `data`: "이 데이터를 활용해줘"
- `competitor`: "이 경쟁사를 분석해줘"

**분석 원칙 (Analyze Once, Use Everywhere):**
Tool Agent가 1번만 깊게 분석 → analyzed_content에 저장 → Expert가 읽기만

## 주의사항

1. 이 스킬은 **Claude Code 환경**에서만 동작합니다
2. MCP 서버 사용 시 사전 설정이 필요합니다 (`.mcp.json`)
3. 상태 파일은 `company/state/` 폴더에 JSON으로 저장됩니다
4. 세션 종료 후에도 상태가 유지되어 계속 진행 가능합니다
5. 레퍼런스는 **Task Briefing 시점에** 태스크별로 제공합니다 (Phase 1에서 일괄 수집하지 않음)
6. dependency_graph 기반 자동 병렬 실행을 위해 독립 태스크를 최대한 식별합니다
