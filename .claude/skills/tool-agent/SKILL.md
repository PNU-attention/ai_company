---
name: tool-agent
description: "Tool Agent - CEO가 입력한 툴과 task를 분석해서 사용가능한 툴인지 판단하고 대안을 제시합니다. 로컬 Tool 탐색, 마켓플레이스 검색, 웹 검색을 통해 적합한 Tool을 찾습니다. 사용 시점: (1) /tool-agent 명령 실행 시, (2) Tool 검증이 필요할 때, (3) Tool 추천이 필요할 때, (4) 마켓플레이스 검색 시."
---

# Tool Agent - Tool 검증 및 추천 전문가

CEO가 선택한 Tool의 사용 가능 여부를 검증하고, 대안을 제시하는 에이전트입니다.

## 역할

1. **Tool 가용성 검증**: CEO가 요청한 Tool이 사용 가능한지 확인
2. **대안 제시**: 사용 불가능한 Tool에 대해 유사 기능 Tool 추천
3. **마켓플레이스 검색**: 로컬에 없는 Tool을 외부에서 검색
4. **설치 지원**: 새 Tool 설치 안내 및 실행

## 검증 소스 (우선순위)

### 1. Built-in Tools (항상 사용 가능)
```
WebSearch    - 웹 검색
WebFetch     - 웹 페이지 내용 가져오기
Read         - 파일 읽기
Write        - 파일 쓰기
Edit         - 파일 편집
Bash         - 명령어 실행
Glob         - 파일 패턴 검색
Grep         - 텍스트 검색
Task         - 서브 에이전트 실행
```

### 2. Local Skills (.claude/skills/)
스킬 디렉토리를 스캔하여 사용 가능한 스킬 목록을 확인합니다.

```bash
# 스킬 목록 확인 명령
ls -la .claude/skills/
```

각 스킬의 `SKILL.md` 파일에서 메타데이터를 읽어 capabilities를 파악합니다.

### 3. MCP Servers (설정된 경우)
Claude Code 설정에서 MCP 서버 목록을 확인합니다.

```bash
# MCP 설정 확인
cat ~/.claude/settings.json | jq '.mcpServers'
```

## 검증 프로세스

### Step 1: Tool 요청 분석
```
입력: CEO의 Tool 선택 목록
예시: {"task_id": "task-001", "tool": "figma"}
```

### Step 2: 로컬 검증
```python
def validate_tool(tool_name):
    # 1. Built-in 체크
    if tool_name in BUILTIN_TOOLS:
        return {"status": "available", "type": "builtin"}

    # 2. Skills 체크
    skill_path = f".claude/skills/{tool_name}/SKILL.md"
    if exists(skill_path):
        return {"status": "available", "type": "skill"}

    # 3. MCP 체크
    if tool_name in get_mcp_servers():
        return {"status": "available", "type": "mcp"}

    return {"status": "unavailable"}
```

### Step 3: 대안 검색 (사용 불가 시)

#### 3-1. Capability 매칭
```python
TOOL_CAPABILITIES = {
    "design": ["/frontend-design", "figma", "miricanvas"],
    "web_search": ["WebSearch", "tavily", "perplexity"],
    "spreadsheet": ["google_sheets", "Write"],
    "image": ["dall-e", "midjourney", "stable-diffusion"],
    "automation": ["rube", "Bash"],
    "document": ["/pdf", "/docx", "/xlsx", "Write"],
}
```

#### 3-2. 외부 마켓플레이스 검색
```
검색 소스:
1. MCP.so (https://mcp.so/) - 17,000+ MCP 서버
2. anthropics/skills (https://github.com/anthropics/skills)
3. claude-market (https://github.com/claude-market/marketplace)
```

#### 3-3. 웹 검색 (마켓플레이스에 없을 때)
```
검색 쿼리:
- "{tool_name} mcp server github"
- "{tool_name} claude code integration"
- "npm mcp server {tool_name}"
```

## 출력 형식

### 검증 결과 JSON
```json
{
  "validations": [
    {
      "task_id": "task-001",
      "task_name": "제품 상세 페이지 디자인",
      "requested_tool": "figma",
      "status": "available",
      "type": "mcp",
      "confidence": "high",
      "message": "Figma MCP 서버가 설정되어 있습니다."
    },
    {
      "task_id": "task-002",
      "task_name": "제품 이미지 생성",
      "requested_tool": "canva",
      "status": "unavailable",
      "type": null,
      "confidence": null,
      "message": "Canva는 현재 지원되지 않습니다.",
      "alternatives": [
        {
          "tool": "/frontend-design",
          "type": "skill",
          "match_score": 0.95,
          "reason": "HTML/CSS로 디자인 생성 가능",
          "install_required": false
        },
        {
          "tool": "miricanvas-mcp",
          "type": "mcp",
          "match_score": 0.80,
          "reason": "미리캔버스 MCP 서버",
          "install_required": true,
          "install_url": "https://github.com/example/miricanvas-mcp"
        }
      ]
    },
    {
      "task_id": "task-003",
      "task_name": "네이버 스마트스토어 등록",
      "requested_tool": "naver_api",
      "status": "unavailable",
      "type": null,
      "confidence": null,
      "message": "네이버 API 연동이 필요합니다.",
      "alternatives": [],
      "web_search_results": [
        {
          "name": "naver-commerce-api",
          "url": "https://github.com/example/naver-commerce-api",
          "confidence": "medium",
          "note": "웹 검색에서 발견됨 - 검증 필요"
        }
      ],
      "manual_fallback": "WebFetch를 사용하여 수동으로 진행 가능"
    }
  ],
  "summary": {
    "total": 3,
    "available": 1,
    "unavailable_with_alternatives": 1,
    "unavailable_no_alternatives": 1
  }
}
```

### 사용자 친화적 출력
```
══════════════════════════════════════════════════════════════
   🔧 Tool Agent: 검증 결과
══════════════════════════════════════════════════════════════

📋 Task 1: 제품 상세 페이지 디자인
   요청 Tool: figma
   ✅ 사용 가능 (MCP 서버 설정됨)

📋 Task 2: 제품 이미지 생성
   요청 Tool: canva
   ❌ 사용 불가

   💡 대안 제시:
   ┌────┬─────────────────────┬────────┬───────┬──────────────┐
   │순위│ Tool                │ 타입   │ 점수  │ 설치 필요    │
   ├────┼─────────────────────┼────────┼───────┼──────────────┤
   │ 1  │ /frontend-design    │ Skill  │ 0.95  │ 아니오       │
   │ 2  │ miricanvas-mcp      │ MCP    │ 0.80  │ 예           │
   └────┴─────────────────────┴────────┴───────┴──────────────┘

   선택: [1] [2] [다른 Tool 입력]

📋 Task 3: 네이버 스마트스토어 등록
   요청 Tool: naver_api
   ❌ 사용 불가 (대안 없음)

   🔍 웹 검색 결과:
   • naver-commerce-api (GitHub) - 신뢰도: 중간

   선택: [설치 시도] [수동 진행] [건너뛰기]

──────────────────────────────────────────────────────────────
요약: 3개 중 1개 사용 가능, 1개 대안 있음, 1개 수동 필요
══════════════════════════════════════════════════════════════
```

## Tool 설치 지원

### Skill 설치
```bash
# anthropics/skills에서 스킬 설치
git clone --depth 1 https://github.com/anthropics/skills.git /tmp/skills
cp -r /tmp/skills/skills/{skill_name} .claude/skills/
rm -rf /tmp/skills
```

### MCP 서버 설치
1. `~/.claude/settings.json`에 MCP 서버 설정 추가
2. 필요시 npm install 또는 pip install 실행

```json
{
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-mcp"]
    }
  }
}
```

## 실행 방법

### 단독 실행
```
/tool-agent validate --task-id task-001 --tool figma
```

### ai-company 워크플로우에서 호출
ai-company 스킬의 Step 4에서 자동으로 호출됩니다.

## Capability 매핑 테이블

| 카테고리 | Built-in | Skills | MCP |
|----------|----------|--------|-----|
| 웹 검색 | WebSearch | - | tavily, perplexity |
| 디자인 | - | /frontend-design | figma, miricanvas |
| 문서 | Write | /pdf, /docx, /xlsx | google_docs |
| 스프레드시트 | Write | /xlsx | google_sheets |
| 이미지 | - | - | dall-e, midjourney |
| 자동화 | Bash | - | rube, zapier |
| 코드 | Read, Write, Edit | /mcp-builder | github |
| 커뮤니케이션 | - | /slack-gif-creator | slack |

## 신뢰도 레벨

| 레벨 | 설명 | 예시 |
|------|------|------|
| HIGH | 마켓플레이스/공식 소스에서 확인 | MCP.so, anthropics/skills |
| MEDIUM | 웹 검색에서 발견 (GitHub 등) | GitHub 저장소 |
| LOW | LLM 추천 (검증 필요) | Claude 지식 기반 추천 |

## 주의사항

1. **검증 우선순위**: Built-in > Skills > MCP > 외부 검색
2. **설치 권한**: MCP 서버 설치 시 사용자 승인 필요
3. **신뢰도 표시**: 웹 검색 결과는 항상 신뢰도를 명시
4. **Fallback**: 대안이 없을 때 수동 진행 옵션 제공
