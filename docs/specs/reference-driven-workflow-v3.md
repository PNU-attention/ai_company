# Reference-Driven Workflow v3 설계서

## 1. 개요

### 1.1 v2의 문제점 (테스트에서 발견)

v2(Tool-Aware Workflow)는 CEO가 Tool을 직접 선택하고, Tool Agent가 검증하는 구조였다. 실제 테스트를 통해 다음 문제들이 드러났다.

#### 문제 1: CEO에게 Tool 지식을 요구함

```
v2 Phase 1-③: CEO Tool 선택

CEO에게 이런 질문을 던짐:
  "Task 3.1 (제품 상세 페이지 디자인)에 어떤 Tool을 쓰시겠습니까?"
  • /frontend-design (Skill)
  • figma (MCP)
  • canva (외부 - 미지원)

→ CEO는 /frontend-design이 뭔지, figma MCP가 뭔지 모름
→ "그냥 예쁘게 만들어줘"가 CEO의 실제 의도
→ Tool 선택은 전문가(Tool Agent)가 해야 할 일
```

**핵심**: CEO는 "무엇을 원하는지"를 알지, "어떤 도구로 만들지"는 모른다.

#### 문제 2: Expert가 결과물의 방향성을 모름

```
v2 Phase 2-⑧: Expert 태스크 실행

Expert가 받는 정보:
  - task_id: "task-001"
  - name: "제품 상세 페이지 디자인"
  - assigned_tools: ["/frontend-design"]

→ "디자인"이라는 단어만으로는 어떤 스타일인지 알 수 없음
→ 미니멀? 화려? 쿠팡 스타일? 네이버 스타일?
→ Expert가 추측으로 만듦 → CEO 마음에 안 듦 → 재작업
→ 토큰 낭비 + 사용자 불만족
```

**핵심**: "어떻게 만들지"에 대한 레퍼런스가 없으면, Expert는 추측할 수밖에 없다.

#### 문제 3: Tool 선택 → Tool 검증, 2단계 비효율

```
v2 흐름:
  ③ CEO가 Tool 선택 (CEO의 시간 소모)
       ↓
  ④ Tool Agent가 검증 (자주 "사용 불가" 판정)
       ↓
  CEO에게 다시 물어봄 ("대안 A로 할까요?")

→ CEO 인터랙션이 2~3회 발생
→ CEO는 처음부터 "알아서 해줘"를 원함
```

**핵심**: CEO ↔ Tool Agent 핑퐁이 너무 많다.

#### 문제 4: 레퍼런스 없는 태스크의 품질 편차

```
같은 "경쟁사 분석" 태스크라도:
  - 레퍼런스 없음: Expert가 임의로 형식/깊이 결정 → 품질 불안정
  - 레퍼런스 있음: "이 보고서처럼 만들어줘" → 일관된 품질

→ v2는 레퍼런스를 전달할 구조가 없음
```

---

### 1.2 해결 방향: Reference-Driven Workflow

**패러다임 전환:**

```
v2: CEO가 "어떤 도구로 만들지" 결정 (Tool-Driven)
v3: CEO가 "어떤 결과물을 원하는지" 보여줌 (Reference-Driven)
```

**핵심 원칙:**

1. **CEO는 레퍼런스를 준다** — URL, 이미지, 파일, 스타일 메모
2. **Tool Agent가 최적 Tool을 찾는다** — 레퍼런스를 분석하고 Tool 추천
3. **Expert는 레퍼런스를 보고 만든다** — 방향성이 명확해서 한 번에 높은 품질

---

## 2. 새로운 워크플로우

### 2.1 전체 흐름도

```
┌─────────────────────────────────────────────────────────────────┐
│                        Phase 1: 계획 수립                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ① CEO 목표 입력                                                │
│       ↓                                                         │
│  ② RM: 백로그 생성 (프로젝트/태스크 목록)                        │
│       ↓                                                         │
│  ③ CEO: 레퍼런스 첨부 (URL, 이미지, 파일, 메모)        [신규]   │
│       ↓                                                         │
│  ④ Tool Agent: 레퍼런스 분석 → Tool 추천 + 검증        [변경]   │
│       ↓                                                         │
│  ⑤ CEO: Tool 추천 승인/수정                             [변경]   │
│       ↓                                                         │
│  ⑥ HR: 에이전트 고용 + Tool/레퍼런스 할당               [변경]   │
│       ↓                                                         │
│  ⑦ RM: 에이전트에 태스크 할당                                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                        Phase 2: 실행                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ⑧ CEO: 실행할 프로젝트 선택                                    │
│       ↓                                                         │
│  ⑨ Expert: 레퍼런스 참조하며 태스크 수행                [변경]   │
│       ↓                                                         │
│  ⑩ 결과 보고 → CEO 검토                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 v2 → v3 변경 비교

| 항목 | v2 | v3 |
|------|----|----|
| 순서 | 백로그 → CEO Tool 선택 → Tool 검증 | 백로그 → **CEO 레퍼런스** → Tool 추천/검증 |
| CEO 역할 | Tool을 직접 고름 | **레퍼런스를 제공**하고 추천을 승인 |
| Tool Agent 역할 | CEO 선택을 **검증** | 레퍼런스를 **분석해서 추천** |
| Expert 입력 | 태스크 설명 + Tool만 | 태스크 설명 + Tool + **레퍼런스** |
| CEO 인터랙션 | Tool 선택 + 재선택 (2~3회) | 레퍼런스 첨부 + 승인 (1~2회) |
| 결과물 품질 | Expert 추측 의존 | **레퍼런스 기반** 일관된 품질 |

---

## 3. 단계별 상세

### Phase 1-①: CEO 목표 입력 (변경 없음)

기존 v2와 동일.

```json
{
  "goal": "달성하고자 하는 목표",
  "kpis": ["측정 가능한 성과 지표"],
  "constraints": ["제약조건"],
  "context": "추가 배경 정보"
}
```

### Phase 1-②: RM 백로그 생성 (변경 없음)

기존 v2와 동일. CEO 목표를 프로젝트/태스크로 분해.

출력: `company/state/backlog.json`

### Phase 1-③: CEO 레퍼런스 첨부 [신규]

CEO가 백로그를 보고, 각 태스크(또는 프로젝트)에 레퍼런스를 첨부한다.

#### 레퍼런스 타입

| 타입 | 형태 | 예시 | 용도 |
|------|------|------|------|
| `url` | 웹 주소 | 경쟁사 사이트, 참고 디자인 | "이런 느낌으로" |
| `image` | 이미지 파일 경로 | 목업, 스크린샷, 로고 | "이렇게 생긴 것" |
| `file` | 로컬 파일 경로 | 기존 보고서, 템플릿, 데이터셋 | "이 포맷/내용 참고" |
| `note` | 텍스트 메모 | 스타일 가이드, 톤앤매너, 브랜드 컬러 | "이런 방향으로" |

#### 레퍼런스의 의도 (intent)

같은 URL이라도 의도가 다를 수 있으므로, 의도를 명시한다:

| Intent | 의미 | 예시 |
|--------|------|------|
| `style` | "이런 스타일/느낌으로 만들어줘" | 참고 디자인 URL |
| `content` | "이 내용을 참고해서 작성해줘" | 경쟁사 분석 보고서 |
| `template` | "이 형식/구조를 따라줘" | 기존 보고서 템플릿 |
| `data` | "이 데이터를 활용해줘" | CSV, 스프레드시트 |
| `competitor` | "이 경쟁사를 분석해줘" | 경쟁사 사이트 URL |

#### CEO 인터랙션 흐름

```
══════════════════════════════════════════════════════════════
   📎 CEO: 레퍼런스 첨부
══════════════════════════════════════════════════════════════

백로그를 확인하고, 참고 자료를 첨부해주세요.
URL, 이미지, 파일, 또는 텍스트 메모를 태스크에 연결할 수 있습니다.
레퍼런스가 없는 태스크는 건너뛰어도 됩니다.

─────────────────────────────────────────────────────────────
📁 프로젝트 1: 쿠팡 입점 준비

  📋 Task 1.1: 시장 트렌드 조사
     레퍼런스: (없으면 Enter)
     > https://datalab.naver.com/keyword/trendSearch.naver
       → 의도: [content] "이 사이트의 데이터를 참고해서 분석"

  📋 Task 1.2: 경쟁사 분석
     레퍼런스:
     > https://www.coupang.com/np/search?q=반려동물
       → 의도: [competitor] "이 카테고리의 경쟁 상황 분석"
     > /Users/ceo/reports/competitor_template.xlsx
       → 의도: [template] "이 엑셀 형식으로 정리해줘"

  📋 Task 1.3: 제품 카테고리 선정
     레퍼런스: (건너뛰기)

─────────────────────────────────────────────────────────────
📁 프로젝트 3: 상품 등록

  📋 Task 3.1: 제품 상세 페이지 디자인
     레퍼런스:
     > https://www.coupang.com/vp/products/1234567890
       → 의도: [style] "이 페이지의 레이아웃 참고"
     > /Users/ceo/design/brand_color.png
       → 의도: [style] "이 브랜드 컬러 적용"
     > 미니멀하고 깔끔한 디자인. 흰 배경에 제품 사진 크게.
       → 의도: [note] 스타일 가이드
─────────────────────────────────────────────────────────────
```

#### 상태 파일: `task_references.json`

```json
{
  "references_id": "ref_20260206_001",
  "created_at": "2026-02-06T10:00:00Z",
  "task_references": {
    "task-001": {
      "references": [
        {
          "ref_id": "ref-001",
          "type": "url",
          "value": "https://datalab.naver.com/keyword/trendSearch.naver",
          "intent": "content",
          "note": "이 사이트의 데이터를 참고해서 분석"
        }
      ]
    },
    "task-002": {
      "references": [
        {
          "ref_id": "ref-002",
          "type": "url",
          "value": "https://www.coupang.com/np/search?q=반려동물",
          "intent": "competitor",
          "note": "이 카테고리의 경쟁 상황 분석"
        },
        {
          "ref_id": "ref-003",
          "type": "file",
          "value": "/Users/ceo/reports/competitor_template.xlsx",
          "intent": "template",
          "note": "이 엑셀 형식으로 정리"
        }
      ]
    },
    "task-006": {
      "references": [
        {
          "ref_id": "ref-004",
          "type": "url",
          "value": "https://www.coupang.com/vp/products/1234567890",
          "intent": "style",
          "note": "이 페이지의 레이아웃 참고"
        },
        {
          "ref_id": "ref-005",
          "type": "image",
          "value": "/Users/ceo/design/brand_color.png",
          "intent": "style",
          "note": "이 브랜드 컬러 적용"
        },
        {
          "ref_id": "ref-006",
          "type": "note",
          "value": "미니멀하고 깔끔한 디자인. 흰 배경에 제품 사진 크게.",
          "intent": "style",
          "note": null
        }
      ]
    }
  },
  "project_references": {
    "proj-001": {
      "references": []
    }
  }
}
```

**설계 포인트:**
- `task_references`: 특정 태스크에 연결되는 레퍼런스
- `project_references`: 프로젝트 전체에 적용되는 레퍼런스 (선택)
- 레퍼런스 없는 태스크는 빈 배열 (Optional)

### Phase 1-④: Tool Agent 레퍼런스 분석 + Tool 추천 [변경]

v2에서 Tool Agent는 "CEO가 고른 Tool을 검증"하는 **수동적 검증자**였다.
v3에서 Tool Agent는 "레퍼런스를 분석하고 최적 Tool을 추천"하는 **능동적 컨설턴트**로 역할이 바뀐다.

#### Tool Agent의 새로운 역할

```
v2: CEO 선택 → Tool Agent 검증 (패스/실패)
v3: 레퍼런스 → Tool Agent 분석 → Tool 추천 리스트 생성
```

#### 분석 로직 (Analyze Once, Use Everywhere)

Tool Agent가 레퍼런스를 **1번만 깊게 분석**하고, 그 결과를 `tool_recommendations.json`의 `analyzed_content`에 저장한다.
이후 HR과 Expert는 이 분석 결과를 **읽기만** 하고, 레퍼런스를 다시 접속/분석하지 않는다.

```
[기존 문제: 3중 분석]
Tool Agent: URL 접속 → 분석 → Tool 추천
HR Agent:   URL 접속 → 분석 → 전문가 구체화    ← 중복
Expert:     URL 접속 → 분석 → 작업 수행         ← 중복

[해결: Analyze Once, Use Everywhere]
Tool Agent: URL 접속 → 깊은 분석 → analyzed_content에 저장 (1번만)
HR Agent:   analyzed_content 읽기 → 전문가 구체화   ← 재분석 불필요
Expert:     analyzed_content 읽기 → 바로 작업 수행   ← 재분석 불필요
```

```
[입력]
- backlog.json (태스크 목록)
- task_references.json (레퍼런스)

[분석 과정]
1. 태스크 유형 분석 (RESEARCH / ACTION / DOCUMENT / APPROVAL)
2. 레퍼런스 깊은 분석 + 결과 저장
   - URL → WebFetch로 내용 확인 → 페이지 구조/내용 요약을 analyzed_content에 저장
   - 이미지 → 이미지 분석 → 색상/레이아웃/분위기를 analyzed_content에 저장
   - 파일 → 확장자 + 내용 분석 → 구조/필드를 analyzed_content에 저장
   - 메모 → 키워드 추출 → 핵심 요구사항을 analyzed_content에 저장
3. CEO의 의도(intent) 해석 → direction(방향성) 도출
4. 레퍼런스 의도 기반 Tool 매핑
5. 사용 가능 여부 검증 (기존 3-tier 검색)
6. Tool 추천 리스트 생성

[출력]
- tool_recommendations.json (analyzed_content 포함)
```

#### 레퍼런스 → Tool 매핑 로직

```
[URL + intent:style]
  → WebFetch로 페이지 분석
  → 웹 디자인 관련? → /frontend-design, figma
  → 문서 형식 관련? → Write, google_docs

[URL + intent:competitor]
  → WebFetch + WebSearch
  → 데이터 정리 필요? → google_sheets via rube, Write
  → 시각화 필요? → /frontend-design (차트)

[이미지 + intent:style]
  → 디자인 작업 → /frontend-design, figma
  → 이미지 편집 → image_editor

[파일(xlsx) + intent:template]
  → 스프레드시트 작업 → google_sheets via rube
  → 파일 직접 편집 → Write + Bash (openpyxl 등)

[메모 + intent:style]
  → 키워드 분석: "미니멀" "깔끔" → /frontend-design
  → 키워드 분석: "자동화" "스케줄" → rube, Bash

[레퍼런스 없는 태스크]
  → 태스크 유형과 이름 기반으로 추천
  → RESEARCH → WebSearch, WebFetch
  → DOCUMENT → Write
  → ACTION → Bash, rube
```

#### Tool Agent 모델 변경

```
v2: haiku (단순 검증이므로 경량 모델)
v3: sonnet (레퍼런스 분석 + 추천에 더 높은 추론력 필요)
```

#### 상태 파일: `tool_recommendations.json`

`reference_analysis` 내에 `analyzed_content` 배열을 두어, 각 레퍼런스의 깊은 분석 결과를 저장한다.
이 필드가 핵심이다 — HR과 Expert는 이 분석 결과만 읽으면 레퍼런스를 다시 접속할 필요가 없다.

```json
{
  "recommendations_id": "rec_20260206_001",
  "created_at": "2026-02-06T10:05:00Z",
  "task_recommendations": [
    {
      "task_id": "task-001",
      "task_name": "시장 트렌드 조사",
      "reference_analysis": {
        "analyzed_refs": ["ref-001"],
        "ref_summary": "네이버 데이터랩 기반 트렌드 분석 필요",
        "detected_needs": ["web_data_extraction", "data_analysis"],
        "direction": "네이버 데이터랩의 키워드 트렌드 데이터를 활용하여 2026년 상반기 카테고리별 성장률 분석",
        "analyzed_content": [
          {
            "ref_id": "ref-001",
            "type": "url",
            "original_value": "https://datalab.naver.com/keyword/trendSearch.naver",
            "fetched_summary": "네이버 데이터랩 키워드 트렌드 검색 페이지. 카테고리별/기간별 검색량 추이를 그래프와 수치로 제공. 주요 기능: 검색어 비교, 기간 설정(1일~5년), 기기별 분류(PC/모바일), 성별/연령별 필터.",
            "key_findings": [
              "카테고리별 검색 트렌드 비교 가능",
              "최대 5개 키워드 동시 비교",
              "CSV 다운로드 기능 지원"
            ],
            "style_elements": null,
            "structure_elements": null,
            "actionable_insights": "데이터랩에서 직접 데이터 추출 후, 반려동물/건강식품/생활용품 등 카테고리별 검색량 추이를 비교 분석하면 유망 카테고리 식별 가능"
          }
        ]
      },
      "recommended_tools": [
        {
          "tool": "WebSearch",
          "type": "builtin",
          "match_score": 0.95,
          "reason": "트렌드 키워드 검색 및 시장 데이터 수집",
          "status": "available"
        },
        {
          "tool": "WebFetch",
          "type": "builtin",
          "match_score": 0.90,
          "reason": "레퍼런스 URL(네이버 데이터랩) 데이터 추출",
          "status": "available"
        }
      ],
      "combination_note": "WebSearch로 트렌드 키워드 수집 → WebFetch로 상세 데이터 추출"
    },
    {
      "task_id": "task-006",
      "task_name": "제품 상세 페이지 디자인",
      "reference_analysis": {
        "analyzed_refs": ["ref-004", "ref-005", "ref-006"],
        "ref_summary": "쿠팡 스타일 상품 페이지, 특정 브랜드 컬러, 미니멀 디자인 요구",
        "detected_needs": ["web_design", "brand_styling", "responsive_layout"],
        "direction": "쿠팡 상품 상세 페이지의 레이아웃 구조를 따르되, 미니멀하고 깔끔한 스타일로 제작. 흰 배경에 제품 사진을 크게 배치하고 브랜드 컬러를 포인트로 활용",
        "analyzed_content": [
          {
            "ref_id": "ref-004",
            "type": "url",
            "original_value": "https://www.coupang.com/vp/products/1234567890",
            "fetched_summary": "쿠팡 상품 상세 페이지. 상단에 대형 제품 이미지 캐러셀, 우측에 가격/배송 정보, 하단에 상세 설명 영역.",
            "key_findings": [
              "이미지 캐러셀이 페이지 좌측 60% 차지",
              "가격, 배송, 판매자 정보가 우측 사이드바에 고정",
              "상세 설명은 이미지 기반 (긴 세로 이미지)"
            ],
            "style_elements": {
              "layout": "2컬럼 (이미지 60% + 정보 40%), 하단 풀폭 상세 설명",
              "colors": "흰 배경, 쿠팡 블루(#346aff) 포인트, 로켓배송 그린",
              "typography": "본문 14px, 가격 24px 볼드, 깔끔한 산세리프",
              "spacing": "넉넉한 여백, 섹션 간 구분선"
            },
            "structure_elements": {
              "header": "브레드크럼 네비게이션",
              "hero": "이미지 캐러셀 + 썸네일",
              "sidebar": "가격, 수량, 장바구니 버튼",
              "body": "탭 구조 (상품상세/리뷰/문의)",
              "footer": "관련 상품 추천"
            },
            "actionable_insights": "2컬럼 레이아웃을 유지하되 브랜드 컬러로 교체. 이미지 캐러셀 + 사이드바 구조를 재사용"
          },
          {
            "ref_id": "ref-005",
            "type": "image",
            "original_value": "/Users/ceo/design/brand_color.png",
            "fetched_summary": "브랜드 컬러 팔레트 이미지",
            "key_findings": [
              "메인 컬러: #2D5016 (딥 그린)",
              "서브 컬러: #F5F0E8 (웜 베이지)",
              "액센트: #D4A574 (테라코타)"
            ],
            "style_elements": {
              "primary_color": "#2D5016",
              "secondary_color": "#F5F0E8",
              "accent_color": "#D4A574",
              "mood": "자연친화적, 프리미엄, 따뜻한 느낌"
            },
            "structure_elements": null,
            "actionable_insights": "쿠팡 블루 대신 딥 그린(#2D5016)을 포인트 컬러로 사용. 배경은 웜 베이지(#F5F0E8) 또는 흰색"
          },
          {
            "ref_id": "ref-006",
            "type": "note",
            "original_value": "미니멀하고 깔끔한 디자인. 흰 배경에 제품 사진 크게.",
            "fetched_summary": null,
            "key_findings": [
              "미니멀 스타일 요구",
              "흰 배경 선호",
              "제품 사진 강조 (대형 이미지)"
            ],
            "style_elements": {
              "aesthetic": "미니멀, 깔끔",
              "background": "흰색 (#FFFFFF)",
              "image_treatment": "제품 사진을 크고 깨끗하게",
              "overall_feel": "군더더기 없는 깔끔함"
            },
            "structure_elements": null,
            "actionable_insights": "불필요한 장식 요소 배제. 여백을 넉넉히 사용. 제품 이미지가 시선을 끌도록 대형 배치"
          }
        ]
      },
      "recommended_tools": [
        {
          "tool": "/frontend-design",
          "type": "skill",
          "match_score": 0.95,
          "reason": "레퍼런스 URL의 레이아웃을 분석하여 프로덕션급 HTML/CSS 코드 생성 가능",
          "status": "available"
        },
        {
          "tool": "WebFetch",
          "type": "builtin",
          "match_score": 0.70,
          "reason": "레퍼런스 URL(쿠팡 상품 페이지)의 구조 분석용",
          "status": "available"
        }
      ],
      "combination_note": "WebFetch로 레퍼런스 페이지 구조 분석 → /frontend-design으로 브랜드 컬러 적용한 페이지 생성"
    }
  ]
}
```

#### `analyzed_content` 필드 상세

| 필드 | 타입 | 설명 | 소비자 |
|------|------|------|--------|
| `ref_id` | string | 원본 레퍼런스 ID | 전체 |
| `type` | string | 레퍼런스 타입 | 전체 |
| `original_value` | string | 원본 URL/경로/텍스트 | Expert (원본 접근 필요시) |
| `fetched_summary` | string | URL/파일/이미지 분석 요약 | HR, Expert |
| `key_findings` | string[] | 핵심 발견 사항 | HR (역할 도출), Expert (작업 방향) |
| `style_elements` | object/null | 색상, 레이아웃, 타이포그래피 등 | Expert (디자인 작업) |
| `structure_elements` | object/null | 페이지/문서 구조 분석 | Expert (구조 재현) |
| `actionable_insights` | string | 이 레퍼런스를 어떻게 활용할지 구체적 지침 | Expert (실행 계획) |

#### `direction` 필드

`reference_analysis` 레벨에 추가되는 `direction`은 해당 태스크의 **전체 방향성을 한 문장으로 요약**한 것이다.
Tool Agent가 모든 레퍼런스를 종합하여 작성하며, HR이 전문가 역할명을 구체화하고 Expert가 실행 계획을 세울 때 가장 먼저 읽는 필드이다.

```
direction 예시:
"쿠팡 상품 상세 페이지의 레이아웃 구조를 따르되,
 미니멀하고 깔끔한 스타일로 제작.
 흰 배경에 제품 사진을 크게 배치하고
 브랜드 컬러(딥 그린 #2D5016)를 포인트로 활용"
```

### Phase 1-⑤: CEO Tool 추천 승인 [변경]

v2에서는 CEO가 Tool을 직접 선택했다면, v3에서는 Tool Agent의 추천을 **승인/수정**만 한다.

```
══════════════════════════════════════════════════════════════
   🤖 Tool Agent: 레퍼런스 기반 Tool 추천
══════════════════════════════════════════════════════════════

레퍼런스를 분석하여 각 태스크에 최적 Tool을 추천합니다.

─────────────────────────────────────────────────────────────
📋 Task 1.1: 시장 트렌드 조사
   📎 레퍼런스: 네이버 데이터랩 URL
   🔧 추천 Tool: WebSearch + WebFetch
   💡 이유: 레퍼런스 URL의 데이터 추출 + 추가 트렌드 검색

   [✅ 승인]  [✏️ 수정]
─────────────────────────────────────────────────────────────
📋 Task 3.1: 제품 상세 페이지 디자인
   📎 레퍼런스: 쿠팡 상품 페이지 URL + 브랜드 컬러 이미지 + 스타일 메모
   🔧 추천 Tool: /frontend-design + WebFetch
   💡 이유: 레퍼런스 페이지 구조 분석 후 브랜드 컬러 적용한 HTML/CSS 생성
   💡 조합: WebFetch → 레퍼런스 분석, /frontend-design → 코드 생성

   [✅ 승인]  [✏️ 수정]
─────────────────────────────────────────────────────────────

[전체 승인] [선택 수정]
```

**CEO가 수정하고 싶을 때:**
```
CEO: "Task 3.1은 figma도 추가해줘"
→ Tool Agent가 figma 가용성 즉시 검증
→ 가능하면 추가, 불가능하면 사유 + 대안 제시
```

#### 상태 파일: `tool_selections.json` (v3 수정)

```json
{
  "selections_id": "sel_20260206_001",
  "created_at": "2026-02-06T10:10:00Z",
  "approval_mode": "reference_based",
  "task_tool_mapping": {
    "task-001": {
      "tools": ["WebSearch", "WebFetch"],
      "source": "tool_agent_recommendation",
      "ceo_modified": false
    },
    "task-006": {
      "tools": ["/frontend-design", "WebFetch"],
      "source": "tool_agent_recommendation",
      "ceo_modified": false
    }
  }
}
```

### Phase 1-⑥: HR 에이전트 고용 [변경]

HR이 에이전트를 고용할 때, Tool Agent가 분석한 `analyzed_content`와 `direction`을 참조하여 더 적합한 전문가를 구성한다.
**HR은 레퍼런스 원본을 직접 접속/분석하지 않는다.** `tool_recommendations.json`의 분석 결과만 읽는다.

```
[입력]
- backlog.json
- tool_recommendations.json ← analyzed_content, direction 포함
- tool_selections.json

[HR이 읽는 정보]
- direction: "미니멀하고 깔끔한 스타일로 제작" → "미니멀 UI 전문 디자이너" 역할명 도출
- key_findings: ["미니멀 스타일 요구", "흰 배경 선호"] → specialties에 "minimal_ui" 추가
- style_elements: {aesthetic: "미니멀"} → 전문가 설명에 반영

[HR이 하지 않는 것]
- ❌ 레퍼런스 URL 직접 접속
- ❌ 이미지/파일 직접 분석
- ❌ Tool Agent가 이미 한 분석 반복
```

#### 상태 파일: `hired_agents.json` (v3 수정)

```json
{
  "agents": [
    {
      "agent_id": "expert-001",
      "role_name": "트렌드 리서처",
      "description": "네이버 데이터랩 등 데이터 소스 기반 시장 트렌드 분석 전문가",
      "specialties": ["market_research", "data_analysis", "trend_forecasting"],
      "assigned_tools": ["WebSearch", "WebFetch"],
      "assigned_tasks": ["task-001", "task-002"],
      "reference_context": "네이버 데이터랩, 쿠팡 카테고리 분석 레퍼런스 참고",
      "status": "active"
    },
    {
      "agent_id": "expert-002",
      "role_name": "미니멀 UI 디자이너",
      "description": "쿠팡 스타일 상품 페이지에 특화된 미니멀 웹 디자인 전문가",
      "specialties": ["web_design", "minimal_ui", "ecommerce_page"],
      "assigned_tools": ["/frontend-design", "WebFetch"],
      "assigned_tasks": ["task-006"],
      "reference_context": "쿠팡 상품 페이지 레이아웃, 브랜드 컬러, 미니멀 스타일 가이드 참고",
      "status": "active"
    }
  ]
}
```

**변경 포인트:**
- `reference_context`: 이 에이전트가 참고해야 할 레퍼런스 요약
- `role_name`이 더 구체적 (기존: "디자인 전문가" → v3: "미니멀 UI 디자이너")

### Phase 1-⑦: RM 태스크 할당 (변경 없음)

기존 v2와 동일. 에이전트에게 태스크를 할당.

출력: `company/state/task_assignments.json`

### Phase 2-⑧: CEO 프로젝트 선택 (변경 없음)

기존 v2와 동일.

### Phase 2-⑨: Expert 태스크 수행 [변경]

**v3의 가장 큰 변화.** Expert가 태스크를 실행할 때 레퍼런스를 직접 참조한다.

#### Expert 실행 흐름 (v3)

Expert는 레퍼런스 원본을 다시 분석하지 않는다. Tool Agent가 저장한 `analyzed_content`를 읽고 바로 작업에 착수한다.
단, 실제 작업 수행 중 원본에 접근이 필요한 경우(예: URL의 특정 데이터 추출)에만 원본을 참조한다.

```
1. 태스크 정보 로드 (task_assignments.json)
      ↓
2. 분석된 레퍼런스 로드 (tool_recommendations.json)  ← [변경: 분석 결과를 읽음]
      ├─ direction → 전체 작업 방향성 파악
      ├─ analyzed_content → 각 레퍼런스의 분석 결과 확인
      │   ├─ style_elements → 적용할 스타일 확인
      │   ├─ structure_elements → 따를 구조 확인
      │   └─ actionable_insights → 구체적 활용 방법 확인
      └─ (원본 접근이 필요한 경우에만 task_references.json 참조)
      ↓
3. 의존성 확인
      ↓
4. 실행 계획 수립 (analyzed_content 기반)          ← [변경: 재분석 불필요]
      └─ "ref-004의 2컬럼 레이아웃 + ref-005의 딥그린(#2D5016) + ref-006의 미니멀 스타일"
      ↓
5. Tool 사용하여 태스크 실행
      └─ 원본 접근이 필요한 경우만 WebFetch/Read 사용
      ↓
6. 결과물이 direction/style_elements와 부합하는지 자체 검증
      ↓
7. 결과 저장 + 로그 기록
```

#### Expert에게 전달되는 정보 (v2 vs v3)

```
[v2] Expert가 받는 정보:
  - task_id: "task-006"
  - name: "제품 상세 페이지 디자인"
  - tools: ["/frontend-design"]
  → "디자인 해"라고만 지시받음. 어떤 스타일인지 모름.

[v3] Expert가 받는 정보 (analyzed_content 기반):
  - task_id: "task-006"
  - name: "제품 상세 페이지 디자인"
  - tools: ["/frontend-design", "WebFetch"]
  - direction: "쿠팡 스타일 레이아웃 + 미니멀 + 브랜드 컬러(딥그린)"
  - analyzed_content 요약:
    - ref-004: 2컬럼 레이아웃(이미지 60%+정보 40%), 탭 구조
    - ref-005: 메인 컬러 #2D5016, 서브 #F5F0E8, 액센트 #D4A574
    - ref-006: 미니멀, 흰 배경, 제품 사진 대형 배치

  → Expert는 URL을 다시 접속할 필요 없이,
    "2컬럼 레이아웃에 딥 그린(#2D5016) 포인트,
     흰 배경에 제품 사진 크게, 미니멀 스타일"
    이라는 구체적이고 즉시 실행 가능한 지시를 받음
```

### Phase 2-⑩: 결과 보고 (변경 없음)

기존 v2와 동일.

---

## 4. Tool Agent 역할 재설계

### 4.1 v2 → v3 역할 변화

```
v2 Tool Agent: 검증자 (Validator)
─────────────────────────────────
입력: CEO가 선택한 Tool 목록
처리: 가용성 체크 (있다/없다)
출력: 검증 결과 + 대안

v3 Tool Agent: 컨설턴트 (Consultant)
─────────────────────────────────
입력: 백로그 + 레퍼런스
처리: 레퍼런스 분석 → 필요 Tool 도출 → 가용성 검증 → 조합 추천
출력: Tool 추천 리스트 + 사용 전략
```

### 4.2 레퍼런스 분석 능력

Tool Agent가 레퍼런스를 분석하여 Tool을 추천하는 핵심 로직:

```python
class ReferenceAnalyzer:
    """레퍼런스를 분석하여 필요 Tool을 도출"""

    def analyze(self, task: Task, references: list[Reference]) -> ToolNeeds:
        needs = ToolNeeds()

        for ref in references:
            if ref.type == "url":
                # URL 내용을 WebFetch로 확인
                content = self.fetch_url(ref.value)
                needs.merge(self._analyze_url_content(content, ref.intent))

            elif ref.type == "image":
                # 이미지 분석 (멀티모달)
                needs.merge(self._analyze_image(ref.value, ref.intent))

            elif ref.type == "file":
                # 파일 확장자 + 내용 분석
                needs.merge(self._analyze_file(ref.value, ref.intent))

            elif ref.type == "note":
                # 키워드 기반 분석
                needs.merge(self._analyze_note(ref.value, ref.intent))

        return needs

    def _analyze_url_content(self, content: str, intent: str) -> ToolNeeds:
        """URL 내용 기반 Tool 필요성 분석"""
        if intent == "style":
            # 웹 디자인 레퍼런스 → 디자인 Tool 필요
            return ToolNeeds(
                primary=["frontend-design"],
                support=["WebFetch"]  # 레퍼런스 구조 분석용
            )
        elif intent == "competitor":
            # 경쟁사 분석 → 리서치 + 데이터 정리 Tool
            return ToolNeeds(
                primary=["WebSearch", "WebFetch"],
                support=["Write"]  # 보고서 작성용
            )
        elif intent == "data":
            # 데이터 소스 → 데이터 수집 + 정리 Tool
            return ToolNeeds(
                primary=["WebFetch"],
                support=["google_sheets_via_rube"]
            )
```

### 4.3 레퍼런스가 없는 태스크 처리

모든 태스크에 레퍼런스가 있진 않다. 레퍼런스 없는 태스크의 Tool 추천:

```
레퍼런스가 없는 경우:
  1. 태스크 유형 (RESEARCH/ACTION/DOCUMENT/APPROVAL) 기반 추천
  2. 태스크 이름의 키워드 분석
  3. 같은 프로젝트 내 다른 태스크의 레퍼런스 참고 (프로젝트 컨텍스트)

예:
  Task: "제품 카테고리 선정" (레퍼런스 없음)
  같은 프로젝트 내 Task 1.1에 네이버 데이터랩 URL 있음
  → "시장 데이터 기반 분석이 필요할 수 있음"
  → 추천: WebSearch + Write
```

### 4.4 하이브리드 모드

CEO가 레퍼런스 대신 직접 Tool을 지정하고 싶은 경우도 지원한다 (v2 호환).

```
CEO 입력 시 선택지:
  1. 레퍼런스 첨부 → Tool Agent가 추천 (v3 기본 모드)
  2. Tool 직접 지정 → Tool Agent가 검증 (v2 호환 모드)
  3. 혼합 → 일부 태스크는 레퍼런스, 일부는 직접 지정
```

---

## 5. 수정된 그래프 구조

### 5.1 Phase 구조

```python
class CompanyPhase(Enum):
    # Phase 1: 계획 수립
    INITIALIZATION = "initialization"
    BACKLOG_CREATION = "backlog_creation"
    REFERENCE_COLLECTION = "reference_collection"    # [신규]
    TOOL_RECOMMENDATION = "tool_recommendation"      # [변경: tool_selection → tool_recommendation]
    TOOL_APPROVAL = "tool_approval"                  # [변경: tool_validation → tool_approval]
    AGENT_HIRING = "agent_hiring"
    TASK_ASSIGNMENT = "task_assignment"
    PLANNING_COMPLETE = "planning_complete"

    # Phase 2: 실행
    AWAITING_EXECUTION = "awaiting_execution"
    EXECUTING = "executing"
    COMPLETED = "completed"
```

### 5.2 그래프 흐름

```
           ┌──────────────────┐
           │   initialize     │
           └────────┬─────────┘
                    ↓
           ┌──────────────────┐
           │   rm_backlog     │ ← RM이 백로그 생성
           └────────┬─────────┘
                    ↓
        ┌──────────────────────────┐
        │  ceo_reference_collect   │ ← CEO 레퍼런스 첨부 [신규]
        └──────────┬───────────────┘
                    ↓
        ┌──────────────────────────┐
        │  tool_analyze_recommend  │ ← Tool Agent 분석 + 추천 [변경]
        └──────────┬───────────────┘
                    ↓
        ┌──────────────────────────┐
        │  ceo_tool_approve        │ ← CEO 추천 승인/수정 [변경]
        └──────────┬───────────────┘
                    │
          ┌────────┴────────┐
          ↓                 ↓
     [전체 승인]      [수정 요청]
          ↓                 ↓
          │     ┌──────────────────────────┐
          │     │  tool_analyze_recommend  │ ← 수정분 재분석
          │     └──────────────────────────┘
          ↓
        ┌──────────────────────────┐
        │      hr_hire             │ ← HR 에이전트 고용 (+레퍼런스 컨텍스트)
        └──────────┬───────────────┘
                    ↓
        ┌──────────────────────────┐
        │      rm_assign           │ ← RM 태스크 할당
        └──────────┬───────────────┘
                    ↓
        ┌──────────────────────────┐
        │    ceo_execute           │ ← CEO 프로젝트 선택
        └──────────┬───────────────┘
                    ↓
        ┌──────────────────────────┐
        │     executor             │ ← Expert 실행 (+레퍼런스 참조)
        └──────────┬───────────────┘
                    │
          ┌────────┴────────┐
          ↓                 ↓
     [태스크 남음]    [프로젝트 완료]
          ↓                 ↓
     ← executor 반복  ┌──────────────┐
                      │  ceo_execute │ or completion
                      └──────────────┘
```

---

## 6. 상태 파일 전체 구조 (v3)

```
company/state/
├── session.json              # 세션 정보
├── ceo_goal.json             # CEO 목표 (변경 없음)
├── backlog.json              # RM 백로그 (변경 없음)
├── task_references.json      # [신규] CEO 레퍼런스
├── tool_recommendations.json # [신규] Tool Agent 추천 결과
├── tool_selections.json      # CEO 승인된 최종 Tool 선택 (스키마 변경)
├── hired_agents.json         # HR 고용 에이전트 (스키마 변경)
├── task_assignments.json     # 태스크 할당 (변경 없음)
└── execution_log.json        # 실행 로그 (변경 없음)
```

**v2 대비 변경:**
- `task_references.json` 신규 추가
- `tool_recommendations.json` 신규 추가
- `tool_validations.json` → `tool_recommendations.json`으로 대체
- `tool_selections.json` 스키마 변경 (approval_mode 추가)
- `hired_agents.json` 스키마 변경 (reference_context 추가)

---

## 7. 에이전트 변경 사항

### 7.1 변경 요약

| 에이전트 | 변경 | 상세 |
|----------|------|------|
| **ceo-agent** | 역할 변경 | Tool 선택자 → 레퍼런스 제공자 + 승인자 |
| **rm-agent** | 변경 없음 | 백로그 생성, 태스크 할당 |
| **tool-agent** | 역할 확장 + 모델 변경 | 검증자 → 컨설턴트, haiku → sonnet |
| **hr-agent** | 입력 추가 | task_references.json 참조하여 더 구체적 전문가 고용 |
| **expert-agent** | 실행 방식 변경 | 레퍼런스 참조하며 태스크 수행 |

### 7.2 Tool Agent 변경 상세

```yaml
# v2
name: tool-agent
description: "CEO가 선택한 Tool의 사용 가능 여부를 검증하고 대안을 제시합니다."
model: haiku

# v3
name: tool-agent
description: "레퍼런스를 분석하여 최적의 Tool 조합을 추천하고 검증합니다.
              CEO가 직접 Tool을 지정한 경우 가용성을 검증합니다."
model: sonnet
```

**핵심 변경:**
- `description` 변경: "검증" → "분석 + 추천"
- `model` 변경: haiku → sonnet (분석 능력 필요)

### 7.3 CEO Agent 변경 상세

```yaml
# v2 Phase별 액션
| Phase | CEO 액션 |
| tool_selection | Tool 직접 선택 |

# v3 Phase별 액션
| Phase | CEO 액션 |
| reference_collection | 레퍼런스 첨부 |
| tool_approval | Tool 추천 승인/수정 |
```

### 7.4 Expert Agent 변경 상세

```yaml
# v2 실행 흐름
1. 태스크 정보 로드
2. 할당된 Tool 확인
3. 태스크 실행
4. 결과 저장

# v3 실행 흐름
1. 태스크 정보 로드
2. 레퍼런스 로드 + 분석        ← [신규]
3. 할당된 Tool 확인
4. 레퍼런스 기반 실행 계획 수립  ← [신규]
5. 태스크 실행
6. 레퍼런스 대비 결과 검증      ← [신규]
7. 결과 저장
```

---

## 8. 예상 사용자 경험 (v3)

```
[CEO] 목표: 쿠팡 입점하고 월 매출 1000만원 달성

[RM] 백로그를 생성했습니다:
  📁 프로젝트 1: 쿠팡 입점 준비
    📋 Task 1.1: 시장 트렌드 조사
    📋 Task 1.2: 경쟁사 분석
    📋 Task 1.3: 제품 카테고리 선정
  📁 프로젝트 3: 상품 등록
    📋 Task 3.1: 제품 상세 페이지 디자인
    ...

[System] 각 태스크에 참고할 자료가 있으면 첨부해주세요.
         URL, 이미지, 파일, 또는 메모를 입력하실 수 있습니다.
         없으면 건너뛰어도 됩니다.

[CEO]
  Task 1.2에 https://www.coupang.com/np/search?q=반려동물 (경쟁사 분석용)
  Task 3.1에 https://www.coupang.com/vp/products/1234567890 (이런 스타일로)
  Task 3.1에 "미니멀하고 깔끔하게, 흰 배경에 제품 사진 크게"

[Tool Agent] 레퍼런스를 분석하여 Tool을 추천합니다:

  📋 Task 1.1: 시장 트렌드 조사
     📎 레퍼런스 없음 → 태스크 유형 기반 추천
     🔧 추천: WebSearch
     ✅ 사용 가능

  📋 Task 1.2: 경쟁사 분석
     📎 쿠팡 검색 URL (경쟁사 분석용)
     🔧 추천: WebSearch + WebFetch + Write
     ✅ 모두 사용 가능
     💡 WebFetch로 쿠팡 카테고리 데이터 수집 → Write로 분석 보고서 작성

  📋 Task 3.1: 제품 상세 페이지 디자인
     📎 쿠팡 상품 페이지 URL + 스타일 메모
     🔧 추천: /frontend-design + WebFetch
     ✅ 모두 사용 가능
     💡 WebFetch로 레퍼런스 페이지 구조 분석 → /frontend-design으로 미니멀 스타일 코드 생성

  모두 승인하시겠습니까?

[CEO] OK, 전체 승인

[HR] 에이전트를 고용했습니다:
  👤 트렌드 리서처 (Tools: WebSearch, WebFetch)
  👤 미니멀 UI 디자이너 (Tools: /frontend-design, WebFetch)
     ↑ 레퍼런스의 "미니멀" 키워드 반영

[Expert - 미니멀 UI 디자이너] Task 3.1 시작
  📎 레퍼런스 확인:
    - 쿠팡 상품 페이지 구조 분석 중... (WebFetch)
    - 스타일 가이드: "미니멀, 깔끔, 흰 배경, 제품 사진 크게"
  🔧 /frontend-design 실행:
    - 쿠팡 스타일 레이아웃 적용
    - 미니멀 디자인 반영
    - 흰 배경 + 대형 제품 이미지

  ✅ 결과: company/outputs/product_page_task006.html
```

**v2 대비 개선점:**
- CEO는 Tool 이름을 몰라도 됨 (URL과 메모만 제공)
- Expert는 "어떤 스타일로 만들지" 명확히 앎
- Tool Agent가 알아서 최적 Tool 조합을 찾아줌

---

## 9. 변경 요약

| 항목 | v2 | v3 |
|------|----|----|
| 패러다임 | Tool-Driven | **Reference-Driven** |
| CEO 역할 | Tool 선택자 | **레퍼런스 제공자** |
| Tool Agent 역할 | 검증자 (Validator) | **컨설턴트 (Consultant)** |
| Tool Agent 모델 | haiku | **sonnet** |
| Expert 입력 | 태스크 + Tool | 태스크 + Tool + **레퍼런스** |
| CEO 인터랙션 | 2~3회 (선택+재선택) | **1~2회** (레퍼런스+승인) |
| 결과물 품질 | Expert 추측 의존 | **레퍼런스 기반** |
| 새 상태 파일 | - | `task_references.json`, `tool_recommendations.json` |
| 삭제 상태 파일 | - | `tool_validations.json` → `tool_recommendations.json`으로 대체 |

---

## 10. 구현 우선순위

### Phase 1: 핵심 구조 변경
1. `task_references.json` 스키마 정의 및 CEO 레퍼런스 수집 흐름
2. Tool Agent 역할 확장 (레퍼런스 분석 + Tool 추천)
3. `tool_recommendations.json` 스키마 정의
4. CEO 승인 흐름 구현

### Phase 2: 에이전트 업데이트
1. `tool-agent.md` 프롬프트 재작성 (컨설턴트 역할)
2. `ceo-agent.md` 프롬프트 수정 (레퍼런스 제공자 역할)
3. `expert-agent.md` 프롬프트 수정 (레퍼런스 참조 실행)
4. `hr-agent.md` 프롬프트 수정 (레퍼런스 컨텍스트 반영)

### Phase 3: SKILL.md + CLAUDE.md 업데이트
1. `ai-company/SKILL.md` 워크플로우 반영
2. `CLAUDE.md` 프로젝트 가이드 업데이트
