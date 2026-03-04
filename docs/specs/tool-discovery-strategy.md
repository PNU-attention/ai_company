# Tool 발견 전략 설계 (Tool Discovery Strategy)

> **문서 버전**: v1.0
> **작성일**: 2026-03-05
> **관련 컴포넌트**: Tool Agent (Phase 1), tool_inventory.json

---

## 1. 배경 및 문제 의식

### 문제

AI Company 시스템에서 Expert 에이전트의 역량은 **어떤 Tool을 쓸 수 있느냐**에 달려 있다.
하지만 Phase 1에서 Tool Agent가 인벤토리를 생성할 때, 정작 **어떤 Tool이 존재하는지 알기 어렵다는 문제**가 있었다.

```
CEO 목표: "인스타그램 계정을 운영해줘"
    ↓
Tool Agent가 인벤토리를 만들려면...

  질문 1: 이미지 생성 Tool이 뭐가 있지?
    → Gemini? DALL-E? 무료 API는? 설치형은?

  질문 2: 인스타그램 업로드 Tool은?
    → MCP가 있나? 직접 API 호출해야 하나?

  질문 3: 우리가 모르는 더 좋은 Tool이 있을 수도 있잖아?
    → 어디서 찾지?
```

기존 방식은 **Tool Agent의 사전 지식에만 의존**했다. LLM의 학습 데이터에 있는 Tool만 추천할 수 있었고, 새로 나온 Tool이나 커뮤니티 스킬은 놓치기 쉬웠다.

### 이상적인 상태

> "CEO가 목표를 주면, Tool Agent가 그 목표에 맞는 **최신 Tool을 동적으로 탐색**하고,
> 그 중 실제로 사용 가능한 것만 추려서 인벤토리를 만든다."

---

## 2. 해결 방안: Vibe Index 기반 동적 Tool 발견

### Vibe Index란?

[Vibe Index](https://vibeindex.ai)는 Claude Code 생태계에 특화된 툴 디렉토리다.
- **103,000+ 개** 이상의 Skills, MCP 서버, 플러그인, 마켓플레이스 등록 (매시간 업데이트)
- **공개 REST API** 제공 — 별도 인증 없이 키워드 검색 가능
- **GitHub stars, 보안 등급, 카테고리** 등 메타데이터 포함

### 핵심 아이디어

Tool Agent가 백로그를 분석하여 필요한 Tool 카테고리를 파악한 뒤,
**Vibe Index API를 호출해서 그 카테고리에 맞는 Tool을 실시간으로 검색**한다.

```
백로그 분석 결과:
  "이미지 생성", "SNS 업로드", "밈 제작" 카테고리 필요
        ↓
Vibe Index API 호출:
  search="image generation" → flux MCP, pollinations-ai skill, ...
  search="instagram"        → instagram MCP, social media skill, ...
  search="meme"             → imgflip skill, meme generator, ...
        ↓
실제로 설치/사용 가능한 것만 필터링
        ↓
tool_inventory.json에 등록
```

---

## 3. API 사용법

### 기본 검색

```
GET https://vibeindex.ai/api/resources?ref=skill-vibeindex&search={키워드}&pageSize=10
```

**응답 구조:**
```json
{
  "data": [
    {
      "name": "pollinations-ai",
      "resource_type": "skill",
      "description": "Free image generation via Pollinations.ai URL API",
      "stars": 5930,
      "github_owner": "supercent-io",
      "github_repo": "skills-template",
      "tags": ["image-generation", "free", "no-signup"]
    }
  ],
  "total": 42
}
```

**resource_type 분류:**

| 타입 | 설명 | 설치 방법 |
|------|------|----------|
| `skill` | Claude Code 스킬 파일 | `npx skills add {owner}/{repo} --skill {name}` |
| `mcp` | MCP 서버 | `vibeindex.ai/mcp/{owner}/{repo}` 참고 |
| `plugin` | Claude Code 플러그인 | `vibeindex.ai/plugins/{owner}/{repo}/{name}` 참고 |
| `marketplace` | 큐레이션 컬렉션 | 개별 항목 참고 |

### Tool Agent의 검색 쿼리 전략

백로그의 `suggested_tool_categories`를 기반으로 키워드를 도출한다:

| 카테고리 | 검색 키워드 예시 |
|----------|----------------|
| `image_generation` | `"image generation"`, `"AI image"`, `"stable diffusion"` |
| `social_media` | `"instagram"`, `"twitter"`, `"social media post"` |
| `video_production` | `"video generation"`, `"remotion"`, `"ffmpeg"` |
| `document` | `"notion"`, `"google docs"`, `"markdown"` |
| `data_analysis` | `"python data"`, `"pandas"`, `"google sheets"` |
| `code_review` | `"code review"`, `"github"`, `"pull request"` |

### 전체 통계 조회

```
GET https://vibeindex.ai/api/stats?ref=skill-vibeindex
→ 총 등록 Tool 수 확인
```

---

## 4. Tool Agent 인벤토리 생성 프로세스에서의 위치

```
Phase 1 - Tool 인벤토리 생성 (tool-agent)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1. Built-in 체크
  → WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep
  → 항상 사용 가능, 리스트 고정

Step 2. Local Skills 스캔
  → .claude/skills/ 디렉토리 스캔
  → 설치된 스킬 자동 발견 (symlink 포함)

Step 3. Rube 마켓플레이스 확인 (오케스트레이터 직접 수행)
  → RUBE_SEARCH_TOOLS로 필요 카테고리 검색
  → RUBE_MANAGE_CONNECTIONS로 연결 상태 확인

Step 4. 외부 API 웹 검색
  → "meme generator API free", "image generation REST API" 등
  → 인증/가격/제한사항 조사

Step 5. ★ Vibe Index API 동적 검색 ★  ← 이 문서의 핵심
  → Built-in/Rube로 커버 안 되는 카테고리 발견 시 호출
  → 키워드별 병렬 API 호출
  → stars, 보안 등급 기반 필터링
  → 설치 가능한 skill/mcp 우선 추천
```

### 검색 결과 활용 판단 기준

Vibe Index 검색 결과를 인벤토리에 포함할 때 다음 기준을 적용한다:

| 기준 | 임계값 | 이유 |
|------|--------|------|
| GitHub Stars | 100+ 권장 | 커뮤니티 검증 지표 |
| resource_type | `skill` > `mcp` > `plugin` 우선 | 설치 용이성 |
| 관련성 | 태스크 카테고리와 직접 매칭 | 불필요한 Tool 제외 |
| 중복 | Rube로 이미 커버되면 생략 | 인벤토리 간소화 |

---

## 5. 실제 적용 사례

### 사례 1: 이미지 생성 Tool 발견

```
CEO 목표: "인스타그램 CS 교육 계정 운영"
백로그 카테고리: image_generation

Tool Agent 동작:
  1. Built-in → Bash(PIL 가능) ✅
  2. Local Skills → /frontend-design ✅
  3. Rube → gemini (ACTIVE) ✅
  4. 웹 검색 → imgflip_api, gemini_api_direct 발견
  5. Vibe Index 검색: search="image generation"
     → pollinations-ai (stars: 5,930) 발견!
     → image-generation-mcp (stars: N/A) 발견!
     → npx skills add 로 설치 가능 확인

결과: /pollinations-ai, /image-generation-mcp 인벤토리 추가
      이후 HR이 이미지 생성 역량 Expert에 feasible_tools로 포함
```

### 사례 2: 새로운 세션에서의 재발견

Tool Agent는 새 세션마다 인벤토리를 재생성한다.
이때 Vibe Index API를 다시 호출하면 **그 시점의 최신 Tool**을 발견할 수 있다.

```
2026년 3월 기준: pollinations-ai 발견 → 설치 → 인벤토리 등록
2026년 6월 기준: 더 좋은 무료 이미지 Tool이 등록되어 있을 수도 있음
                → 다음 세션의 Tool Agent가 자동으로 발견
```

---

## 6. 설계 결정 및 트레이드오프

### 결정: "필요할 때만 검색" (Lazy Discovery)

모든 카테고리를 항상 검색하는 대신, **백로그에서 식별된 카테고리에 대해서만** Vibe Index를 검색한다.

- **장점**: 불필요한 API 호출 감소, 인벤토리 크기 최적화
- **단점**: 예상치 못한 Tool은 발견하기 어려움
- **보완**: Tool Agent가 백로그 카테고리를 넉넉하게 해석하도록 유도

### 결정: Vibe Index를 "마지막 수단"이 아닌 "적극적 탐색 수단"으로

기존에는 Vibe Index가 "모를 때 찾아보는 곳"이었다면,
이제는 **Phase 1 인벤토리 생성의 표준 단계**로 포함한다.

```
Before: Built-in → Rube → (막히면) 웹 검색 → (그래도 모르면) Vibe Index
After:  Built-in → Local Skills → Rube → 웹 검색 → Vibe Index (항상 실행)
```

### 결정: skills add로 설치 가능한 Tool 우선

MCP 서버는 별도 설정이 필요한 반면, Skill은 `npx skills add` 한 줄로 즉시 사용 가능하다.
Vibe Index 검색 결과에서 **`resource_type: "skill"` 을 우선 추천**한다.

---

## 7. 현재 설치된 Vibe Index 발견 Tool

본 프로젝트에서 Vibe Index를 통해 발견하고 설치한 Tool 목록:

| 스킬 | 발견 경로 | 설치 경로 | 주요 용도 |
|------|----------|----------|----------|
| `pollinations-ai` | Vibe Index search="image generation" | `.claude/skills/pollinations-ai/` | 무료 이미지 생성 (API 키 불필요) |
| `image-generation-mcp` | Vibe Index search="image generation mcp" | `.claude/skills/image-generation-mcp/` | Gemini MCP 기반 고품질 이미지 생성 |

> 설치 명령어: `npx skills add https://github.com/supercent-io/skills-template --skill {name} -y`

---

## 8. 향후 계획

- [ ] Tool Agent의 Vibe Index 검색을 **카테고리별 병렬 호출**로 최적화
- [ ] 발견된 Tool의 보안 등급(Socket, Snyk) 자동 검증 후 인벤토리 포함
- [ ] 자주 사용되는 카테고리별 "기본 검색 쿼리 템플릿" 관리
- [ ] 설치된 스킬 목록을 `skills-lock.json`으로 버전 관리 (이미 존재함)

---

## 참고

- Vibe Index 공식 사이트: https://vibeindex.ai
- API 엔드포인트: `https://vibeindex.ai/api/resources?ref=skill-vibeindex&search={query}&pageSize=10`
- Tool Agent 구현: `.claude/agents/tool-agent.md`
- 인벤토리 스키마: `docs/specs/interactive-execution-workflow-v4.md`
