# E2E 테스트 시나리오

> **Version**: 1.0.0
> **Last Updated**: 2025-02-06
> **구조**: Subagent 기반 멀티 에이전트 시스템

---

## 1. 테스트 개요

### 1.1 테스트 목적

Subagent 기반 AI Company 시스템의 End-to-End 동작을 검증합니다.

### 1.2 테스트 범위

```
┌─────────────────────────────────────────────────────────────────┐
│                      E2E 테스트 범위                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Phase 1: 계획]                                                │
│  ① ceo-agent: 목표 입력                                        │
│  ② rm-agent: 백로그 생성                                       │
│  ③ ceo-agent: Tool 선택                                        │
│  ④ tool-agent: Tool 검증                                       │
│  ⑤ hr-agent: 에이전트 고용                                     │
│  ⑥ rm-agent: 태스크 할당                                       │
│                                                                 │
│  [Phase 2: 실행]                                                │
│  ⑦ ceo-agent: 프로젝트 선택                                    │
│  ⑧ expert-agent: 태스크 실행                                   │
│  ⑨ 결과 보고                                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 테스트 환경

- **Subagent 위치**: `.claude/agents/`
- **상태 파일 위치**: `company/state/`
- **결과물 위치**: `company/outputs/`

---

## 2. 사전 조건

### 2.1 상태 초기화

```bash
# 상태 파일 초기화 (테스트 전 실행)
rm -f company/state/*.json
rm -rf company/outputs/*

# 초기 세션 파일 생성
echo '{"session_id": "test_session_001", "phase": "init", "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}' > company/state/session.json
```

### 2.2 Subagent 파일 확인

```bash
# 필수 에이전트 파일 존재 확인
ls -la .claude/agents/
# 예상 출력:
# ceo-agent.md
# rm-agent.md
# tool-agent.md
# hr-agent.md
# expert-agent.md
```

---

## 3. 테스트 시나리오

### 시나리오 1: Happy Path (정상 흐름)

**목표**: "쿠팡 입점하여 월 매출 500만원 달성"

#### Step 1: CEO 목표 입력

**입력**:
```
ceo-agent를 사용해서 다음 목표를 입력해줘:
- 목표: 쿠팡 입점하여 월 매출 500만원 달성
- KPI: 월 매출 500만원, 리뷰 평점 4.5 이상
- 제약조건: 초기 투자 300만원 이내, 2개월 내 런칭
```

**예상 결과**:
- `company/state/ceo_goal.json` 생성
- `session.json`의 phase가 `goal_input` → `backlog_creation`으로 변경

**검증 포인트**:
```json
// company/state/ceo_goal.json
{
  "goal": "쿠팡 입점하여 월 매출 500만원 달성",
  "kpis": ["월 매출 500만원", "리뷰 평점 4.5 이상"],
  "constraints": ["초기 투자 300만원 이내", "2개월 내 런칭"],
  "created_at": "ISO-8601 형식"
}
```

---

#### Step 2: RM 백로그 생성

**입력**:
```
rm-agent를 사용해서 백로그를 생성해줘
```

**예상 결과**:
- `company/state/backlog.json` 생성
- 최소 2개 이상의 프로젝트 포함
- 각 프로젝트에 2개 이상의 태스크 포함
- 태스크별 `suggested_tool_categories` 포함

**검증 포인트**:
```json
// company/state/backlog.json
{
  "backlog_id": "bl_YYYYMMDD_NNN",
  "goal": "쿠팡 입점하여 월 매출 500만원 달성",
  "projects": [
    {
      "id": "proj-001",
      "name": "시장 조사",
      "tasks": [
        {
          "id": "task-001",
          "name": "트렌드 분석",
          "type": "RESEARCH",
          "suggested_tool_categories": ["web_search"]
        }
      ]
    }
  ]
}
```

---

#### Step 3: CEO Tool 선택

**입력**:
```
ceo-agent를 사용해서 각 태스크에 Tool을 선택해줘.
가능하면 Built-in Tool을 우선 사용해줘.
```

**예상 결과**:
- `company/state/tool_selections.json` 생성
- 각 태스크에 최소 1개 이상의 Tool 선택됨

**검증 포인트**:
```json
// company/state/tool_selections.json
{
  "selection_id": "sel_YYYYMMDD_NNN",
  "selections": [
    {
      "task_id": "task-001",
      "task_name": "트렌드 분석",
      "selected_tool": "WebSearch",
      "category": "web_search"
    }
  ]
}
```

---

#### Step 4: Tool Agent 검증

**입력**:
```
tool-agent를 사용해서 선택된 Tool들을 검증해줘
```

**예상 결과**:
- `company/state/tool_validations.json` 생성
- 각 Tool의 가용성 상태 (`available` / `unavailable`)
- 사용 불가 시 대안 제시

**검증 포인트**:
```json
// company/state/tool_validations.json
{
  "validations": [
    {
      "task_id": "task-001",
      "requested_tool": "WebSearch",
      "status": "available",
      "type": "builtin"
    }
  ],
  "summary": {
    "total": 5,
    "available": 5,
    "unavailable_with_alternatives": 0,
    "unavailable_no_alternatives": 0
  }
}
```

---

#### Step 5: HR 에이전트 고용

**입력**:
```
hr-agent를 사용해서 필요한 전문가 에이전트를 고용해줘
```

**예상 결과**:
- `company/state/hired_agents.json` 생성
- 태스크 유형에 맞는 전문가 역할 생성
- 각 에이전트에 Tool 할당

**검증 포인트**:
```json
// company/state/hired_agents.json
{
  "agents": [
    {
      "agent_id": "expert-001",
      "role_name": "트렌드 리서처",
      "assigned_tools": ["WebSearch", "WebFetch"],
      "assigned_tasks": ["task-001", "task-002"],
      "status": "active"
    }
  ],
  "summary": {
    "total_agents": 2,
    "coverage": "100%"
  }
}
```

---

#### Step 6: RM 태스크 할당

**입력**:
```
rm-agent를 사용해서 태스크를 에이전트에 할당해줘
```

**예상 결과**:
- `company/state/task_assignments.json` 생성
- 모든 태스크가 에이전트에 할당됨
- `session.json`의 phase가 `ready_to_execute`로 변경

**검증 포인트**:
```json
// company/state/task_assignments.json
{
  "assignments": [
    {
      "task_id": "task-001",
      "assigned_agent_id": "expert-001",
      "assigned_agent_name": "트렌드 리서처",
      "status": "ready"
    }
  ],
  "summary": {
    "total_tasks": 5,
    "assigned": 5,
    "unassigned": 0
  }
}
```

---

#### Step 7: Expert 태스크 실행

**입력**:
```
expert-agent를 사용해서 task-001을 실행해줘
```

**예상 결과**:
- `company/state/execution_log.json` 업데이트
- `company/outputs/` 디렉토리에 결과물 생성
- 태스크 상태가 `completed`로 변경

**검증 포인트**:
```json
// company/state/execution_log.json
{
  "logs": [
    {
      "log_id": "log_001",
      "task_id": "task-001",
      "agent_id": "expert-001",
      "status": "completed",
      "tools_used": ["WebSearch"],
      "outputs": ["company/outputs/trend_report.md"],
      "summary": "2025년 쿠팡 트렌드 분석 완료"
    }
  ]
}
```

---

### 시나리오 2: 인터럽트 처리 (INFO_REQUEST)

**목표**: Expert가 정보 부족으로 CEO에게 요청하는 상황

#### Setup

Task 6 (제품 상세 페이지 디자인)은 `required_inputs`가 있는 태스크:
```json
{
  "id": "task-006",
  "name": "제품 상세 페이지 디자인",
  "required_inputs": [
    {"key": "product_images", "description": "제품 이미지"},
    {"key": "product_specs", "description": "제품 사양"}
  ]
}
```

#### 테스트 흐름

**Step 1: 태스크 실행 시도**
```
expert-agent를 사용해서 task-006을 실행해줘
```

**예상 결과**:
- INFO_REQUEST 인터럽트 발생
- 필요한 입력 목록 제시

**검증 포인트**:
```
인터럽트 발생:
- type: info_request
- task_id: task-006
- required_inputs: [product_images, product_specs]
```

**Step 2: CEO 정보 제공**
```
제품 이미지는 https://example.com/product.jpg 이고,
제품 사양은 "USB 충전 손풍기, 3단 풍속, 2000mAh 배터리" 야
```

**예상 결과**:
- 태스크 실행 재개
- 결과물 생성

---

### 시나리오 3: 인터럽트 처리 (APPROVAL_REQUEST)

**목표**: APPROVAL 타입 태스크에서 CEO 승인 요청

#### Setup

Task 3 (제품 카테고리 선정)은 APPROVAL 타입:
```json
{
  "id": "task-003",
  "name": "제품 카테고리 선정",
  "type": "APPROVAL"
}
```

#### 테스트 흐름

**Step 1: 태스크 실행**
```
expert-agent를 사용해서 task-003을 실행해줘
```

**예상 결과**:
- 이전 태스크 결과 기반 분석 수행
- 선택지 제시
- APPROVAL_REQUEST 인터럽트 발생

**검증 포인트**:
```
인터럽트 발생:
- type: approval_request
- task_id: task-003
- options: [반려동물 용품, 건강식품, 생활용품]
```

**Step 2: CEO 승인**
```
1번 반려동물 용품으로 선택할게
```

**예상 결과**:
- 선택 결과 저장
- 태스크 완료 처리

---

### 시나리오 4: Tool 사용 불가 상황

**목표**: 요청한 Tool이 사용 불가능할 때 대안 제시

#### Setup

CEO가 `canva`를 선택했지만 사용 불가능한 상황

#### 테스트 흐름

**Step 1: Tool 선택**
```
task-006에는 canva를 사용하고 싶어
```

**Step 2: Tool 검증**
```
tool-agent를 사용해서 검증해줘
```

**예상 결과**:
- `canva`: status = `unavailable`
- 대안 제시:
  - `/frontend-design` (Skill, match_score: 0.95)
  - `figma` (MCP, match_score: 0.85)

**검증 포인트**:
```json
{
  "task_id": "task-006",
  "requested_tool": "canva",
  "status": "unavailable",
  "alternatives": [
    {
      "tool": "/frontend-design",
      "type": "skill",
      "match_score": 0.95,
      "install_required": false
    }
  ]
}
```

---

### 시나리오 5: 의존성 있는 태스크

**목표**: 선행 태스크가 완료되지 않은 상태에서 실행 시도

#### Setup

```json
{
  "id": "task-002",
  "dependencies": ["task-001"]
}
```

#### 테스트 흐름

**Step 1: 의존성 있는 태스크 실행 시도**
```
expert-agent를 사용해서 task-002를 실행해줘
(task-001이 아직 완료되지 않은 상태)
```

**예상 결과**:
- 의존성 체크
- "task-001이 먼저 완료되어야 합니다" 메시지
- 또는 task-001 먼저 실행 제안

---

## 4. 검증 체크리스트

### 4.1 상태 파일 생성 확인

| 단계 | 파일 | 필수 필드 |
|------|------|----------|
| Step 1 | ceo_goal.json | goal, kpis, constraints |
| Step 2 | backlog.json | projects, tasks |
| Step 3 | tool_selections.json | selections |
| Step 4 | tool_validations.json | validations, summary |
| Step 5 | hired_agents.json | agents |
| Step 6 | task_assignments.json | assignments |
| Step 7 | execution_log.json | logs |

### 4.2 에이전트 동작 확인

| 에이전트 | 검증 항목 |
|----------|----------|
| ceo-agent | 목표 입력, Tool 선택, 인터럽트 응답 |
| rm-agent | 백로그 생성, 태스크 할당 |
| tool-agent | Tool 검증, 대안 제시 |
| hr-agent | 에이전트 고용, Tool 배정 |
| expert-agent | 태스크 실행, 인터럽트 생성 |

### 4.3 인터럽트 처리 확인

| 인터럽트 타입 | 트리거 조건 | 예상 동작 |
|--------------|------------|----------|
| INFO_REQUEST | required_inputs 부족 | 정보 요청 후 대기 |
| APPROVAL_REQUEST | APPROVAL 타입 태스크 | 선택지 제시 후 대기 |
| TOOL_ERROR | Tool 실행 실패 | 대안 제시 또는 건너뛰기 |

---

## 5. 테스트 실행 스크립트

```bash
#!/bin/bash
# test_e2e.sh

echo "=== E2E 테스트 시작 ==="

# 1. 환경 초기화
echo "[1/7] 환경 초기화..."
rm -f company/state/*.json
rm -rf company/outputs/*
mkdir -p company/outputs

# 2. 상태 파일 확인
check_file() {
    if [ -f "$1" ]; then
        echo "  ✅ $1 생성됨"
        return 0
    else
        echo "  ❌ $1 없음"
        return 1
    fi
}

# 3. 테스트 후 검증 (수동 실행 후 확인)
echo "[7/7] 상태 파일 검증..."
check_file "company/state/ceo_goal.json"
check_file "company/state/backlog.json"
check_file "company/state/tool_selections.json"
check_file "company/state/tool_validations.json"
check_file "company/state/hired_agents.json"
check_file "company/state/task_assignments.json"
check_file "company/state/execution_log.json"

echo "=== E2E 테스트 완료 ==="
```

---

## 6. 예상 이슈 및 해결 방안

### 6.1 Subagent 호출 실패

**증상**: "에이전트를 찾을 수 없습니다"

**원인**:
- `.claude/agents/` 디렉토리에 파일 없음
- 파일 이름 불일치

**해결**:
```bash
ls -la .claude/agents/
# 파일 존재 및 이름 확인
```

### 6.2 상태 파일 불일치

**증상**: 이전 단계 파일이 없어서 다음 단계 실행 불가

**원인**:
- 이전 단계가 정상 완료되지 않음
- 파일 경로 오류

**해결**:
```bash
# 상태 파일 확인
cat company/state/session.json | jq '.phase'
```

### 6.3 Tool 검증 오류

**증상**: 모든 Tool이 `unavailable`로 표시

**원인**:
- Built-in Tool 목록 누락
- MCP 설정 오류

**해결**:
- tool-agent.md의 Built-in Tool 목록 확인
- `~/.claude/settings.json` MCP 설정 확인

---

## 7. 테스트 결과 템플릿

```markdown
# E2E 테스트 결과

- **테스트 일시**: YYYY-MM-DD HH:MM
- **테스터**:
- **테스트 환경**:

## 시나리오 1: Happy Path

| 단계 | 결과 | 비고 |
|------|------|------|
| Step 1: CEO 목표 입력 | ✅/❌ | |
| Step 2: RM 백로그 생성 | ✅/❌ | |
| Step 3: CEO Tool 선택 | ✅/❌ | |
| Step 4: Tool 검증 | ✅/❌ | |
| Step 5: HR 에이전트 고용 | ✅/❌ | |
| Step 6: RM 태스크 할당 | ✅/❌ | |
| Step 7: Expert 태스크 실행 | ✅/❌ | |

## 시나리오 2: INFO_REQUEST

| 항목 | 결과 | 비고 |
|------|------|------|
| 인터럽트 발생 | ✅/❌ | |
| 정보 제공 후 재개 | ✅/❌ | |

## 발견된 이슈

1. [이슈 제목]
   - 증상:
   - 원인:
   - 해결 방안:

## 결론

- 전체 통과율: X/Y (Z%)
- 권장 사항:
```
