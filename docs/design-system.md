# Design System — AI Company

> **용도**: 디자인 작업을 수행하는 모든 에이전트와 QA 에이전트가 공통으로 참조하는 시각 디자인 규칙 문서입니다.
>
> - **디자인 에이전트** (expert, 디자인 담당): 작업 전 이 문서를 읽고 규칙을 적용합니다.
> - **QA 에이전트**: ACTION_VISUAL 태스크 검증 시 이 문서의 기준을 적용합니다.

---

## 규칙의 두 레이어

```
┌─────────────────────────────────────────────────────────────┐
│  Layer A: 절대 규칙 (Non-Negotiable)                         │
│  레퍼런스가 있어도, CEO 지시가 있어도 반드시 지켜야 하는 것   │
│  → 글자 겹침 없음, 최소 폰트 크기, 텍스트 잘림 없음, 대비 등  │
├─────────────────────────────────────────────────────────────┤
│  Layer B: 스타일 결정 (우선순위 순서로 적용)                  │
│  1순위: ceo_references.analyzed_content.style_elements       │
│  2순위: ceo_instructions 명시적 지시                         │
│  3순위: 디자인 시스템 기본값 (없을 때만)                      │
└─────────────────────────────────────────────────────────────┘
```

---

## ★ Layer A: 절대 규칙

어떤 디자인 스타일을 따르든 **예외 없이** 지켜야 합니다.

### ① 텍스트 겹침 금지
```css
/* 모든 텍스트 컨테이너에 적용 */
overflow: hidden;
position: relative;  /* absolute 자식이 부모를 벗어나지 못하도록 */
```
- `position: absolute` 요소가 다른 텍스트 위에 겹치지 않는지 반드시 확인

### ② 텍스트 슬라이드 밖으로 잘림 금지
```css
.slide {
  overflow: hidden;
}
.text-block {
  word-break: keep-all;
  overflow-wrap: break-word;
  overflow: hidden;
}
```

### ③ 최소 폰트 크기 — 플랫폼별 기준

| 용도 | 일반 슬라이드 | **Instagram 카드뉴스** |
|------|-------------|----------------------|
| 본문 | 16px 이상 | **28px 이상** |
| 보조(캡션/번호) | 14px 이상 | **20px 이상** |
| 페이지 번호 | 12px 이상 | **16px 이상** |

> Instagram 카드뉴스는 스마트폰에서 1080px 이미지를 축소해서 봅니다.
> 실질적 표시 크기는 원본의 35~40% → **28px이 실제로는 약 10px로 보입니다.**

레퍼런스 이미지가 작은 텍스트를 쓰더라도 Instagram 카드뉴스 기준 이하는 금지.

### ④ 슬라이드 가장자리 최소 여백: 40px
```css
.slide {
  padding: 64px;  /* 기본값 */
}
/* 최소 40px는 유지 */
```

### ⑤ 텍스트-배경 최소 대비
- 본문 텍스트: 배경과 대비 4.5:1 이상
- 헤딩: 3:1 이상

### ⑥ 하단 회색 띠 금지 (body background 일치)
```css
/* body와 .slide의 background는 항상 동일 */
body { background: [배경색]; }
.slide { background: [배경색]; }  /* 동일한 값 */
```

### ⑦ 시리즈 전체 동일 폰트
- 같은 시리즈의 모든 슬라이드에 동일한 `font-family` 선언

---

## Layer B: 스타일 결정 (우선순위)

```
1순위: ceo_references.analyzed_content.style_elements  ← 레퍼런스 있으면 이것을 따름
       배경색, 폰트 패밀리, 색상 팔레트, 레이아웃 방식, 분위기

2순위: ceo_instructions 명시적 지시
       "다크 테마로", "민트 계열", "더 모던하게" 등

3순위: 디자인 시스템 기본값  ← 레퍼런스도 지시도 없을 때만
       라이트 에디토리얼 (크림 배경, Pretendard, 그린+앰버)
```

---

## 디자인 시스템

### 1. 컬러 시스템

**60-30-10 규칙**: 배경 60% + 서피스 30% + 강조 10%

**다크 테마 기본값:**
```css
--bg:             #0f0f17;
--surface:        #1a1a2e;
--surface-2:      #252540;
--primary:        #2563EB;
--accent:         #F59E0B;
--text:           #F0F0F0;
--text-secondary: #9090AA;
--border:         rgba(255,255,255,0.08);
```

**라이트 에디토리얼 (한국 카드뉴스 권장 — 기본값):**
```css
--bg:             #FAF7F3;
--surface:        #FFFFFF;
--surface-2:      #F5F2EC;
--primary:        #3D7A4D;
--accent:         #C96B1A;
--text:           #1A1A1A;
--text-secondary: #888888;
--border:         rgba(0,0,0,0.08);
--card-radius:    16px;
--card-shadow:    0 2px 12px rgba(0,0,0,0.06);
```

**컬러 사용 규칙:**
- 시리즈 전체에 동일한 `--primary`, `--accent` 사용
- 한 디자인에 최대 4가지 색상
- 그라데이션은 배경에만, 텍스트에는 금지
- 순수 #000000, #FFFFFF는 배경으로 사용 금지

---

### 2. 타이포그래피 시스템

**기본 폰트: Pretendard**

```html
<link rel="stylesheet" as="style" crossorigin
  href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
```

```css
font-family: 'Pretendard Variable', Pretendard, 'Noto Sans KR', sans-serif;
```

**크기 스케일 — Instagram 카드뉴스 기준:**
```
96px — 히어로
80px — Display XL
72px — Display L  (커버 타이틀 권장)
56px — Display M
48px — H1
40px — H2
32px — H3
28px — Body L     ★ Instagram 카드뉴스 본문 최솟값 ★
24px — Body M
20px — Caption L  (페이지 번호, 레이블)
16px — Caption S  (절대 최솟값)
```

**타이포그래피 규칙 (Instagram 카드뉴스):**
```css
/* 슬라이드 제목 */
font-size: 56px;
font-weight: 900;
line-height: 1.1;
letter-spacing: -0.03em;

/* 본문 — 반드시 28px 이상 */
font-size: 28px;
font-weight: 400;
line-height: 1.6;

/* 캡션 */
font-size: 20px;
font-weight: 500;
```

**★ 문장 내 bold/regular 혼합 패턴 (필수 기법):**
```html
<li><strong>터미널 기반</strong>으로 개발 환경에 직접 통합</li>
```
```css
li strong { font-weight: 700; color: inherit; }
li strong.accent { color: var(--primary); }
```

**계층 간격 규칙:** 인접한 두 폰트 크기의 비율은 **최소 1.25x**
- 나쁨: 28px, 32px (1.14x)
- 좋음: 28px, 40px (1.43x)

---

### 3. 레이아웃 & 간격 (8px 그리드)

```
4px  — 아이콘 내부
8px  — 인라인 요소 간격
16px — 컴포넌트 내부 패딩
24px — 컴포넌트 간 기본 간격
32px — 섹션 내 간격
48px — 섹션 간 간격
64px — 대형 섹션 간격
```

**카드/슬라이드 패딩:**
- 1080px 이상: 60-80px 사방
- **절대 금지**: 텍스트가 가장자리에서 24px 이하

---

### 4. HTML/CSS 구현 표준

**기본 HTML 구조 (라이트 에디토리얼):**
```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<link rel="stylesheet" as="style" crossorigin
  href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; }

/* ★ body background = slide background 반드시 일치 ★ */
body {
  width: 1080px;
  height: 1350px;
  overflow: hidden;
  background: #FAF7F3;
  font-family: 'Pretendard Variable', Pretendard, 'Noto Sans KR', sans-serif;
}
.slide {
  width: 1080px;
  height: 1350px;
  background: #FAF7F3;  /* body와 동일 */
  padding: 72px 64px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}
.section-last { flex: 1; }
</style>
</head>
<body>
<div class="slide"><!-- 내용 --></div>
</body>
</html>
```

---

### 5. Chrome Headless PNG 렌더링

```bash
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --no-sandbox --disable-gpu \
  --screenshot="/path/to/output.png" \
  --window-size=1080,1350 \
  --hide-scrollbars \
  "file:///path/to/input.html" 2>/dev/null

# 렌더링 후 확인
ls -lh output.png  # 파일 크기 > 30KB여야 정상
```

**폴백 체인 (렌더링 실패 시):**
```
[Level 1] Chrome headless → 실패 시 Level 2
[Level 2] html2image (Python): pip install html2image
[Level 3] PIL/Pillow로 직접 이미지 생성
Level 3도 실패 시 → TOOL_ERROR 인터럽트
```

---

### 6. ❌ 절대 금지 패턴

**[패턴 1] 하단 회색 띠**
```
원인: body background ≠ .slide background
✅ 수정: body background = 마지막 섹션 배경과 일치, .section-last { flex: 1; }
```

**[패턴 2] 슬라이드 간 폰트 불일치**
```
✅ 수정: 시리즈의 모든 슬라이드에 동일한 <link> 복사
```

**[패턴 3] 폰트 3종 이상 혼용**
```
✅ 수정: 본문 폰트 1종 + 코드 폰트 1종만
```

**[패턴 4] 빈 공간을 억지로 채움**
```
✅ 수정: 하단 여백은 의도적 디자인 요소 (breathing room)
```

---

## ★ Design Brief (코드 작성 전 필수 작성)

**모든 디자인 작업을 시작하기 전에 아래 형식으로 Brief를 작성합니다.**
Brief 없이 코딩을 시작하면 일관성 없는 결과물이 나옵니다.

```
## Design Brief — [태스크명]

포맷: [가로×세로px] / 플랫폼: [Instagram 카드뉴스 / 포스터 / 웹]
총 슬라이드 수: [N장]

스타일 (Layer B 우선순위 적용):
  - 배경 톤: [라이트 에디토리얼 / 다크 / 기타]
  - 분위기: [미니멀 / 플레이풀 / 프로페셔널]
  - 레이아웃: [여백 기반 / 카드 박스 / 기타]

컬러 팔레트:
  - bg:       #_______
  - primary:  #_______
  - accent:   #_______
  - text:     #_______

타이포그래피 (Instagram 기준):
  - 제목:   폰트 56-72px / 900
  - 본문:   폰트 28-32px / 400  ← 최솟값 28px
  - 캡션:   폰트 20px / 500

슬라이드별 구성:
  [슬라이드 1]: Cover — [제목, 서브, 시각적 앵커]
  [슬라이드 2]: Body  — [시각적 앵커, 소제목, 항목]
  [마지막]:     Ending — [요약, CTA]
```

---

## ★ Self-Check Checklist (렌더링 전 필수)

```
[절대] 텍스트 안전:
  ☐ Instagram 카드뉴스 본문 28px 이상, 캡션 20px 이상
  ☐ 텍스트 겹침 없음: position:absolute 요소 확인
  ☐ 텍스트 잘림 없음: overflow:hidden + word-break:keep-all
  ☐ 슬라이드 가장자리 여백 40px 이상

[절대] 배경/렌더링:
  ☐ body background = .slide background (하단 회색 띠 방지)
  ☐ .slide에 overflow:hidden 설정
  ☐ Pretendard CDN 링크 존재

[절대] 대비:
  ☐ 본문 텍스트: 배경과 4.5:1 이상
  ☐ 헤딩: 3:1 이상

[절대] 완성도:
  ☐ placeholder 텍스트 없음 ("내용", "텍스트", "..." 등)

[품질] 타이포그래피:
  ☐ 계층 비율 1.25x 이상
  ☐ bold/regular 혼합 적용
  ☐ 폰트 크기 4종류 이하

[품질] 레이아웃:
  ☐ 슬라이드마다 시각적 앵커 1개 (아이콘/대형숫자/이모지)
  ☐ 간격이 8의 배수
  ☐ 흰 카드 박스 과사용 없음

[품질] 시리즈 일관성:
  ☐ 모든 슬라이드 동일 font-family
  ☐ --primary, --accent 전 슬라이드 동일
```

---

## 텍스트 오버플로우 방지 패턴

```css
/* 한 줄 텍스트 */
.title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 멀티라인 텍스트 */
.body-text {
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  word-break: keep-all;
}
```

---

## ACTION_VISUAL 태스크 완료 기준

| 산출물 | 완료 조건 |
|--------|---------|
| PNG 이미지 | `company/outputs/`에 PNG 존재 + 크기 > 30KB |
| HTML 슬라이드 | `company/outputs/`에 HTML 존재 + 크기 > 1KB |

❌ HTML만 있고 PNG 없음 (PNG가 요구된 경우) → 완료 아님
❌ 빈 파일(0 bytes) → 완료 아님

---

---

# @cs_student_tips 브랜드 아이덴티티 및 디자인 시스템

**프로젝트**: 백엔드 개발자 취업 준비생 인스타그램 계정 (@cs_student_tips)
**작성일**: 2026-03-06
**작성자**: expert-002 (UI/UX 디자이너)
**기반 자료**: CEO 레퍼런스 카드뉴스 이미지 2종 분석 결과, task003 콘텐츠 전략

> 이 섹션은 @cs_student_tips 계정의 모든 카드뉴스 콘텐츠에 적용되는 브랜드 고유 디자인 시스템입니다.
> 이하의 규격은 위 Layer A 절대 규칙을 모두 준수하는 상태에서 추가로 적용합니다.

---

## 1. 브랜드 컬러 팔레트

### 1-1. 코어 팔레트

| 역할 | 이름 | HEX | 사용 위치 |
|------|------|-----|---------|
| **Primary** | 메인 초록 | `#3B7A57` | 제목, 배지, 아이콘 박스, 불릿, 강조 |
| **Accent** | 따뜻한 오렌지 | `#C8722A` | 보조 강조, 비교 카드 우측, 번호 배지 교대 |
| **Background Cover** | 크림 베이지 시작 | `#F8F5ED` | 표지 배경 그라디언트 시작점 |
| **Background Cover End** | 크림 베이지 끝 | `#EDE8DC` | 표지 배경 그라디언트 끝점 |
| **Background Content** | 순백 | `#FFFFFF` | 본문 슬라이드 배경 |
| **Dark** | 차콜 다크 | `#2D2D2D` | VS 배지, 아웃트로 강조 박스, 다크 카드 |
| **Text Primary** | 거의 검정 | `#1C1C1C` | 기본 텍스트 |
| **Text Secondary** | 회색 | `#888888` | 슬라이드 번호, 보조 설명 텍스트 |

### 1-2. CSS 변수 선언

```css
:root {
  /* 브랜드 코어 */
  --cs-primary:        #3B7A57;   /* 메인 초록 */
  --cs-accent:         #C8722A;   /* 오렌지 */
  --cs-dark:           #2D2D2D;   /* 차콜 */

  /* 배경 */
  --cs-bg-cover-start: #F8F5ED;   /* 표지 그라디언트 시작 */
  --cs-bg-cover-end:   #EDE8DC;   /* 표지 그라디언트 끝 */
  --cs-bg-content:     #FFFFFF;   /* 본문 슬라이드 배경 */
  --cs-bg-cover: linear-gradient(180deg, #F8F5ED 0%, #EDE8DC 100%);

  /* 텍스트 */
  --cs-text:           #1C1C1C;   /* 기본 텍스트 */
  --cs-text-sub:       #888888;   /* 보조 텍스트 */
  --cs-text-white:     #FFFFFF;   /* 역색 텍스트 */

  /* 하단 강조선 */
  --cs-line: linear-gradient(90deg, #3B7A57, #C8722A);
}
```

### 1-3. 컬러 사용 규칙

- Primary(#3B7A57)와 Accent(#C8722A)는 항상 쌍으로 사용 (듀얼 팔레트 원칙)
- 한 슬라이드에 Primary + Accent 두 컬러가 모두 등장해야 시리즈 통일감 유지
- Dark(#2D2D2D)는 강조/대비가 필요한 포인트에만 제한 사용
- 배경에 순수 흰색(#FFFFFF)은 본문 슬라이드에서만, 표지는 반드시 크림 그라디언트 사용

---

## 2. 폰트 시스템

### 2-1. 기본 폰트: Noto Sans KR

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
```

```css
font-family: 'Noto Sans KR', sans-serif;
```

### 2-2. 타이포그래피 스케일 (1080x1080px 기준)

| 레벨 | 용도 | 크기 | 굵기 | 색상 | 비고 |
|------|------|------|------|------|------|
| **대형 타이틀 (표지)** | 커버 메인 제목 | 48~56px | 800 | #3B7A57 또는 #C8722A 교대 | 두 색상 교대 강조 |
| **슬라이드 제목** | 본문 슬라이드 H1 | 28~32px | 700 | #3B7A57 | 초록 고정 |
| **소제목** | 섹션 헤딩 | 20~24px | 600 | #1C1C1C | 필요시 강조 |
| **본문** | 불릿 리스트, 설명 | 16~18px | 400 | #1C1C1C | ★ Instagram 최솟값 준수 |
| **캡션 / 슬라이드 번호** | 보조 레이블 | 12~13px | 400 | #888888 | '01 / 08' 형식 |

> ★ 주의: Layer A 규칙에 따라 Instagram 카드뉴스 본문은 실제 CSS 값 기준 28px 이상이어야 합니다.
> 위 표의 16~18px은 참고 레퍼런스 수치이며, 렌더링 시 28px 이상으로 적용합니다.

### 2-3. 타이포그래피 적용 예시

```css
/* 표지 대형 타이틀 (첫 줄: 초록) */
.cover-title-primary {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 52px;
  font-weight: 800;
  color: #3B7A57;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

/* 표지 대형 타이틀 (둘째 줄: 오렌지 강조) */
.cover-title-accent {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 52px;
  font-weight: 800;
  color: #C8722A;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

/* 본문 슬라이드 제목 */
.slide-title {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 32px;
  font-weight: 700;
  color: #3B7A57;
  line-height: 1.3;
}

/* 본문 텍스트 */
.body-text {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 28px;
  font-weight: 400;
  color: #1C1C1C;
  line-height: 1.6;
  word-break: keep-all;
}

/* 슬라이드 번호 */
.slide-number {
  font-family: 'Noto Sans KR', sans-serif;
  font-size: 20px;
  font-weight: 400;
  color: #888888;
}
```

---

## 3. 컴포넌트 스펙

### 3-1. 카드 (Card)

```css
.card {
  background: #FFFFFF;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* 다크 카드 (아웃트로 강조 박스) */
.card-dark {
  background: #2D2D2D;
  border-radius: 16px;
  padding: 24px;
  color: #FFFFFF;
}
```

### 3-2. 배지 (Badge)

```css
/* 초록 배지 (카테고리 레이블, 카버 상단) */
.badge-green {
  background: #3B7A57;
  color: #FFFFFF;
  border-radius: 20px;
  padding: 6px 16px;
  font-size: 20px;
  font-weight: 600;
  display: inline-block;
}

/* 다크 배지 (VS, 비교 레이블) */
.badge-dark {
  background: #2D2D2D;
  color: #FFFFFF;
  border-radius: 8px;
  padding: 4px 12px;
  font-size: 18px;
  font-weight: 600;
  display: inline-block;
}

/* 오렌지 배지 (번호 배지 교대 - 짝수) */
.badge-orange {
  background: #C8722A;
  color: #FFFFFF;
  border-radius: 20px;
  padding: 6px 16px;
  font-size: 20px;
  font-weight: 600;
  display: inline-block;
}
```

### 3-3. 아이콘 박스 (Icon Box)

```css
/* 초록 아이콘 박스 */
.icon-box {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: #3B7A57;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* 오렌지 아이콘 박스 */
.icon-box-orange {
  width: 80px;
  height: 80px;
  border-radius: 20px;
  background: #C8722A;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
```

### 3-4. 하단 강조선 (Bottom Line)

```css
/* 본문 슬라이드 하단 고정 그라디언트 선 */
.bottom-line {
  height: 4px;
  background: linear-gradient(90deg, #3B7A57, #C8722A);
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}
```

### 3-5. 불릿 리스트 (Bullet List)

```css
/* 초록 원형 불릿 */
.bullet-list {
  list-style: disc;
  padding-left: 24px;
  color: #3B7A57;  /* 불릿 색상 */
}

.bullet-list li {
  color: #1C1C1C;  /* 텍스트는 기본 다크 */
  font-size: 28px;
  line-height: 1.6;
  margin-bottom: 12px;
  word-break: keep-all;
}
```

### 3-6. 점 네비게이터 (Dot Navigator)

```css
/* 표지 하단 슬라이드 위치 표시 점 */
.dot-nav {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3B7A57;
  opacity: 0.3;
}

.dot.active {
  opacity: 1;
  width: 24px;
  border-radius: 4px;
}
```

---

## 4. 레이아웃 그리드

### 4-1. 캔버스 기준

| 항목 | 값 |
|------|-----|
| 캔버스 크기 | 1080 x 1080 px |
| 외부 패딩 | 48px (사방) |
| 안전 영역 | 좌우 48px, 상하 48px 이내 |
| 슬라이드 번호 위치 | 좌상단, top: 40px, left: 48px |
| 하단 강조선 위치 | bottom: 0, 전체 너비 |

### 4-2. 기본 HTML 구조

```html
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; }

/* body background = slide background (하단 회색 띠 방지) */
body {
  width: 1080px;
  height: 1080px;
  overflow: hidden;
  background: [슬라이드 배경과 동일];
  font-family: 'Noto Sans KR', sans-serif;
}

.slide {
  width: 1080px;
  height: 1080px;
  padding: 48px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}
</style>
</head>
<body>
<div class="slide">
  <!-- 슬라이드 내용 -->
  <div class="bottom-line"></div>
</div>
</body>
</html>
```

### 4-3. 그리드 간격 규칙 (8px 기준)

| 용도 | 값 |
|------|-----|
| 슬라이드 외부 패딩 | 48px |
| 카드 내부 패딩 | 24px |
| 컴포넌트 간 간격 | 24~32px |
| 불릿 아이템 간격 | 12~16px |
| 배지와 제목 간격 | 24px |
| 제목과 본문 간격 | 32px |
| 아이콘 박스와 텍스트 간격 | 16~20px |

---

## 5. 슬라이드 유형별 레이아웃 규격

### 5-1. Cover (표지)

**용도**: 카드뉴스 첫 장, 주제 소개

**구성 요소 (위에서 아래 순서):**

```
[상단 공간]
[초록 카테고리 배지]      ← badge-green, 좌정렬 또는 중앙정렬
[gap: 24px]
[대형 타이틀 줄 1]        ← 48~56px, weight 800, #3B7A57
[대형 타이틀 줄 2 (강조)] ← 48~56px, weight 800, #C8722A
[gap: 16px]
[서브 텍스트]             ← 28px, weight 400, #888888
[하단 공간]
[점 네비게이터]           ← 하단, 중앙 정렬
```

**배경**: `linear-gradient(180deg, #F8F5ED 0%, #EDE8DC 100%)`
**정렬**: 중앙 정렬 (text-align: center)
**하단 강조선**: 없음 (표지에는 미사용)

```css
/* Cover 슬라이드 */
body, .slide.cover {
  background: linear-gradient(180deg, #F8F5ED 0%, #EDE8DC 100%);
}

.slide.cover {
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 0;
}

.cover-badge-area { margin-bottom: 32px; }
.cover-title-area { margin-bottom: 24px; }
.cover-sub        { margin-bottom: 48px; }
.cover-dots       { position: absolute; bottom: 48px; left: 50%; transform: translateX(-50%); }
```

---

### 5-2. Content-Text (본문 텍스트형)

**용도**: 정보 전달, 불릿 리스트, 설명

**구성 요소 (위에서 아래 순서):**

```
[슬라이드 번호]           ← 좌상단, top:40px left:48px, 13px, #888
[gap: 24px]
[초록 굵은 슬라이드 제목] ← 28~32px, weight 700, #3B7A57
[gap: 24px]
[아이콘 박스 + 설명 행]   ← 80x80px 아이콘박스, 우측에 텍스트
[gap: 24px]
[불릿 리스트 항목들]      ← disc bullet, #3B7A57, 본문 28px
[flex: 1 — 남은 공간]
[하단 강조선 4px]         ← position: absolute, bottom: 0
```

**배경**: `#FFFFFF`
**정렬**: 좌정렬

```css
body, .slide.content-text {
  background: #FFFFFF;
}

.slide.content-text {
  align-items: flex-start;
  padding-top: 40px;  /* 슬라이드 번호 공간 확보 */
}

.slide-number-label {
  position: absolute;
  top: 40px;
  left: 48px;
  font-size: 20px;
  color: #888888;
}
```

---

### 5-3. Content-Compare (비교형)

**용도**: 두 가지 선택지 비교 (Before/After, A vs B)

**구성 요소:**

```
[슬라이드 번호]           ← 좌상단
[비교 제목]               ← 28~32px, weight 700, #3B7A57
[gap: 32px]
[2컬럼 비교 레이아웃]
  ┌──────────────┬──────────────┐
  │ 초록 카드     │ 오렌지 카드   │
  │ (좋은 예)    │ (나쁜 예)    │
  └──────────────┴──────────────┘
[하단 강조선]
```

**2컬럼 카드 규격:**

```css
.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  width: 100%;
}

.compare-card-left {
  background: rgba(59, 122, 87, 0.08);   /* 초록 연한 배경 */
  border: 2px solid #3B7A57;
  border-radius: 16px;
  padding: 24px;
}

.compare-card-right {
  background: rgba(200, 114, 42, 0.08);  /* 오렌지 연한 배경 */
  border: 2px solid #C8722A;
  border-radius: 16px;
  padding: 24px;
}

.compare-card-header-green { color: #3B7A57; font-weight: 700; font-size: 24px; }
.compare-card-header-orange { color: #C8722A; font-weight: 700; font-size: 24px; }
```

---

### 5-4. Content-Tip (팁/번호형)

**용도**: 단계별 가이드, 번호 매긴 팁 목록

**구성 요소:**

```
[슬라이드 번호]              ← 좌상단
[제목]                       ← 28~32px, #3B7A57
[gap: 24px]
[번호 아이템 1] (초록 배지 #1 + 카드)
[번호 아이템 2] (오렌지 배지 #2 + 카드)
[번호 아이템 3] (초록 배지 #3 + 카드)
... (초록/오렌지 교대)
[하단 강조선]
```

**번호 배지 교대 패턴:**

```css
/* 홀수: 초록 */
.tip-item:nth-child(odd)  .tip-number { background: #3B7A57; color: #FFF; }
/* 짝수: 오렌지 */
.tip-item:nth-child(even) .tip-number { background: #C8722A; color: #FFF; }

.tip-number {
  width: 40px;
  height: 40px;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  flex-shrink: 0;
}

.tip-item {
  display: flex;
  gap: 16px;
  align-items: flex-start;
  background: #FFFFFF;
  border-radius: 16px;
  padding: 20px 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
}
```

---

### 5-5. Outro (마무리/아웃트로)

**용도**: 요약, CTA, 팔로우 유도

**구성 요소:**

```
[슬라이드 번호]              ← 좌상단
[요약 제목]                  ← 28~32px, #3B7A57
[gap: 24px]
[2컬럼 요약 카드들]
  ┌────────────┬────────────┐
  │ 요약카드 1  │ 요약카드 2  │
  │ (흰 배경)  │ (흰 배경)  │
  └────────────┴────────────┘
[gap: 24px]
[다크 강조 박스]             ← #2D2D2D 배경, 흰 텍스트, CTA 문구
[하단 강조선]
```

**다크 강조 박스 (CTA):**

```css
.cta-box {
  background: #2D2D2D;
  border-radius: 16px;
  padding: 24px 32px;
  color: #FFFFFF;
  text-align: center;
  width: 100%;
}

.cta-box .cta-text {
  font-size: 28px;
  font-weight: 700;
  color: #FFFFFF;
  margin-bottom: 8px;
}

.cta-box .cta-sub {
  font-size: 22px;
  font-weight: 400;
  color: rgba(255, 255, 255, 0.75);
}
```

---

## 6. 콘텐츠 카테고리별 컬러 배정

task003 콘텐츠 전략의 5개 카테고리에 Primary/Accent 조합을 배정합니다.
기본 팔레트(초록+오렌지)를 유지하되, 아이콘 박스 색상으로 카테고리를 시각적으로 구분합니다.

| 카테고리 | 아이콘 박스 색상 | 배지 색상 | 강조 포인트 | 대표 이모지 |
|---------|--------------|---------|-----------|-----------|
| **서류 작성** (자소서·이력서) | `#3B7A57` (초록) | badge-green | 체크리스트 불릿 | 📄 |
| **면접 준비** (기술·인성) | `#C8722A` (오렌지) | badge-orange | 번호 배지 교대 | 💬 |
| **프로젝트 팁** (GitHub) | `#3B7A57` (초록) | badge-green | 코드 블록 다크 | 💻 |
| **취업 전략** (기업 분석) | `#C8722A` (오렌지) | badge-orange | 비교형 2컬럼 | 🎯 |
| **전공 지식** (CS·알고리즘) | `#2D2D2D` (다크) | badge-dark | 다크 카드 강조 | 🧠 |

### 카테고리별 슬라이드 유형 권장

| 카테고리 | 권장 슬라이드 유형 | 이유 |
|---------|----------------|------|
| 서류 작성 | content-compare + content-tip | 탈락/합격 비교, 체크리스트 적합 |
| 면접 준비 | content-text + content-tip | Q&A 형식, 단계별 답변법 적합 |
| 프로젝트 팁 | content-text | 코드 예시, 설명형 콘텐츠 적합 |
| 취업 전략 | content-compare + outro | 기업 비교, 결론 요약 적합 |
| 전공 지식 | content-text + content-tip | CS 개념 설명, 핵심 정리 적합 |

---

## 7. 브랜드 톤앤매너 (시각적 표현)

task003 콘텐츠 전략의 톤앤매너 가이드를 시각 디자인에 반영합니다.

### 7-1. 전체 시각 무드

| 항목 | 방향 |
|------|------|
| **전반적 무드** | 미니멀 교육 카드뉴스 — 깔끔하고 신뢰감 있음 |
| **배경 톤** | 크림(표지) + 흰색(본문) — 고급스러움과 가독성 동시 |
| **강조 방식** | 색상 대비 (초록/오렌지) + 굵기 대비 (800/400) |
| **여백 활용** | 충분한 여백으로 "숨 쉬는" 레이아웃 유지 |

### 7-2. 금지 시각 패턴

| 금지 패턴 | 이유 |
|---------|------|
| 빨강/파랑 계열 사용 | 브랜드 팔레트(초록+오렌지) 훼손 |
| 그림자 과다 적용 | 미니멀 스타일과 충돌 |
| 배경에 패턴/텍스처 추가 | 크림+흰 배경 원칙 위반 |
| 3가지 이상 폰트 혼용 | Noto Sans KR 단일 패밀리 원칙 |
| 테두리 반경 통일 미준수 | 카드 16px / 배지 20px(초록), 8px(다크) 고정 |

### 7-3. 권장 시각 패턴

| 권장 패턴 | 효과 |
|---------|------|
| 타이틀 두 줄 이상 시 초록/오렌지 교대 | 시각적 리듬감 + 브랜드 아이덴티티 강화 |
| 불릿 리스트에 bold 키워드 혼합 | 스캔 가독성 향상 |
| 아이콘 박스 옆 텍스트 배치 | 단조로운 불릿 리스트보다 풍부한 레이아웃 |
| 하단 그라디언트 선 항상 포함 (본문) | 시리즈 일관성 표식 |

---

## 8. Design Brief 템플릿 (@cs_student_tips 전용)

카드뉴스 제작 전 아래 Brief를 먼저 작성합니다.

```
## Design Brief — [카드뉴스 제목]

포맷: 1080x1080px / Instagram 카드뉴스
총 슬라이드 수: [N장]
카테고리: [서류작성 / 면접준비 / 프로젝트팁 / 취업전략 / 전공지식]

스타일:
  - 표지 배경: linear-gradient(180deg, #F8F5ED 0%, #EDE8DC 100%)
  - 본문 배경: #FFFFFF
  - 분위기: 미니멀 교육 카드뉴스

컬러 팔레트:
  - Primary: #3B7A57
  - Accent:  #C8722A
  - Dark:    #2D2D2D
  - Text:    #1C1C1C

타이포그래피 (Instagram 기준):
  - 커버 타이틀: 52px / 800 (초록+오렌지 교대)
  - 슬라이드 제목: 32px / 700 / #3B7A57
  - 본문: 28px / 400 / #1C1C1C  ← 최솟값 28px 준수
  - 슬라이드 번호: 20px / 400 / #888888

슬라이드 구성:
  [1] Cover  — [제목 줄1(초록), 줄2(오렌지), 배지, 서브텍스트, 점 네비게이터]
  [2] [유형] — [...]
  ...
  [N] Outro  — [요약 카드 2컬럼, 다크 CTA 박스, 하단 강조선]
```

---

## 9. Self-Check Checklist (@cs_student_tips 전용)

```
[브랜드 일관성]
  ☐ 배경: 표지 크림 그라디언트, 본문 #FFFFFF
  ☐ Primary #3B7A57 + Accent #C8722A 모두 사용됨
  ☐ 폰트: Noto Sans KR 단일 패밀리
  ☐ 하단 강조선 (4px 그라디언트) 본문 전 슬라이드에 포함

[레이아웃 규격]
  ☐ 캔버스 1080x1080px 정확히 준수
  ☐ 외부 패딩 48px (사방)
  ☐ 슬라이드 번호 좌상단 (top: 40px, left: 48px)
  ☐ 아이콘 박스 80x80px, border-radius 20px

[컴포넌트 스펙]
  ☐ 카드 border-radius 16px 준수
  ☐ 초록 배지 border-radius 20px 준수
  ☐ 다크 배지 border-radius 8px 준수
  ☐ 불릿 color #3B7A57 적용

[Layer A 절대 규칙 준수]
  ☐ Instagram 본문 텍스트 28px 이상
  ☐ 텍스트 겹침 없음
  ☐ 슬라이드 밖 텍스트 잘림 없음
  ☐ body background = .slide background (하단 회색 띠 방지)
  ☐ 텍스트-배경 대비 4.5:1 이상 (본문)
```
