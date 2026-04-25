# 📖 Idea Engine v1.0 — 운영 매뉴얼

> BLUE JEANS PICTURES · Creative Triage Engine
>
> 최종 업데이트: 2026-04-25

---

## 목차

1. 개요
2. 7단계 파이프라인 상세
3. 각 단계별 사용법
4. DOCX 진단보고서 / JSON 시드 패키지
5. Creator Engine 연동
6. 에러 대응
7. 커스터마이징

---

## 1. 개요

Idea Engine은 모호한 아이디어를 입력받아, 7단계 진단을 거쳐 GO/CONDITIONAL/NOGO 판정과 Creator Engine 입력용 LOCKED 시드 패키지를 생성하는 **입구 게이트 엔진**입니다.

### 핵심 원칙

- **듀얼 모델 정책**:
  - 진단 (Stage ②~⑥): Claude **Sonnet 4.6** (max_tokens=16000)
  - 최종 판정 (Stage ⑦): Claude **Opus 4.7** (max_tokens=16000)
- **Gate 0 통과 기준**: Hook Score 35점 이상 (50점 만점)
- **Gate 미통과 시 Override 가능**
- **선택적 사용**: Creator Engine을 거치지 않고 바로 입력하는 것도 OK
- **Creator Engine과 100% 동일 디자인**: 노란 하이라이트 + 한글/ENGLISH 병기

### Creator Engine과의 관계

```
[A 경로 - Idea Engine 사용]
  모호한 아이디어 → Idea Engine → JSON 시드 → Creator Engine ①
  
[B 경로 - 직접 입력]
  확정된 아이디어 → Creator Engine ① 직접 입력 (현행과 동일)
```

Idea Engine은 **필수 게이트가 아닙니다**. 이미 LOCKED 항목이 명확한 IP는 직접 Creator Engine에 입력해도 됩니다.

---

## 2. 7단계 파이프라인

```
┌─────────────────────────────────────────────────────┐
│  ① 아이디어 입력  자유 텍스트 1줄~1단락               │
│      ↓                                               │
│  ② 로그라인 정제 (Sonnet)                            │
│     산업 표준 로그라인 3개 변형 + 추천안               │
│      ↓                                               │
│  ③ Hook 진단 (Sonnet) — Gate 0                       │
│     5축 채점: 구체성/갈등/장르/판돈/독창성            │
│     35점 이상 PASS / 25~34 CONDITIONAL / 24 이하 FAIL│
│      ↓                                               │
│  ④ Format 추천 (Sonnet)                              │
│     영화/시리즈/미니/숏폼/소설 5개 적합도 + 1순위 추천 │
│      ↓                                               │
│  ⑤ Reference 매핑 (Sonnet)                           │
│     유사작 5편 + 차별점 + 치명적 유사작 경고           │
│      ↓                                               │
│  ⑥ Market 진단 (Sonnet)                              │
│     한국·글로벌·OTT 3개 시장 별점 + 위험 신호          │
│      ↓                                               │
│  ⑦ 최종 판정 (Opus 4.7)                              │
│     6개 진단 종합 → GO/CONDITIONAL/NOGO              │
│     + LOCKED 시드 패키지 확정                        │
│      ↓                                               │
│  ⑧ Export                                            │
│     - 진단보고서 DOCX                                 │
│     - LOCKED 시드 JSON (Creator Engine 입력용)        │
└─────────────────────────────────────────────────────┘
```

---

## 3. 각 단계별 사용법

### ① 아이디어 입력

홈 화면에서 다음을 입력합니다:

| 필드 | 설명 | 예시 |
|------|------|------|
| 제목 | 가제 (필수) | "만물트럭 탐정" |
| 장르 | 14개 옵션 또는 직접 입력 (선택) | 코지 미스터리 |
| 타겟 시장 | 한국/글로벌/일본/동남아 등 | 한국 + 글로벌 |
| 선호 포맷 | 7개 옵션 (Idea Engine이 추천하길 원하면 "미정") | OTT 시리즈 |
| 원본 아이디어 | 자유 텍스트 (필수) | (한 줄~한 단락) |

**Tip**: 원본 아이디어는 한 줄도 가능하지만, **장르·배경·주인공·갈등이 한 단락에 들어가면** 진단 정확도가 올라갑니다.

### ② 로그라인 정제

3가지 의도로 변형된 로그라인을 생성합니다:

- **A안 (기본 구도)**: 산업 표준 안전형
- **B안 (후크 강조)**: 캐릭터 매력·아이러니 부각
- **C안 (주제 강조)**: 사회·시대·인간 본질의 울림

각 변형마다 **강점·약점**이 명시됩니다. 추천안이 자동으로 표시되지만, **대표님께서 최종 선택**하실 수 있습니다.

### ③ Hook 진단 (Gate 0)

5축 × 10점 = 50점 만점 채점:

| 축 | 의미 |
|----|------|
| Specificity | 즉시 시각화되는 고유 후크인가 |
| Conflict Visibility | 한 줄에 갈등이 보이는가 |
| Genre Clarity | 장르가 명확한가 |
| Stakes | 주인공이 잃을 게 큰가 |
| Originality | 본 적 없는 신선한 조합인가 |

**판정**:
- 45~50: 즉시 GO (희귀)
- 35~44: GO (대다수 좋은 기획)
- 25~34: CONDITIONAL (조건부)
- 0~24: NOGO (재고 권장)

레이더 차트 + 점수 카드 + 강점/약점/보강 제안이 표시됩니다.

**FAIL 시 Override**: "⚠ Override하고 Format 추천으로 →" 버튼으로 강제 진행 가능.

### ④ Format 추천

5개 포맷 적합도 동시 판정:

- 장편 영화 (90~120분)
- OTT 시리즈 (6~16화)
- 미니시리즈 (4~6화)
- 숏폼 드라마 (1~2분 × 80~100화)
- 웹소설 / 노벨

각 포맷별 점수와 근거가 표시되며, **1순위 포맷이 자동 추천**됩니다.

추가로:
- IP 빌딩 전략 (1차→2차→3차 미디어 확장 순서)
- 부적합 포맷 명시 (왜 안 되는지)

### ⑤ Reference 매핑

유사작 5편을 다음 차원에서 매핑:
- 다양한 시장 (한국 / 일본 / 미국 / 글로벌)
- 다양한 시기 (최근 3년 / 5년 / 클래식)
- 다양한 차원 (소재 / 톤 / 캐릭터 / 구조)

**치명적 유사작 경고**: 최근 3년 내 동일 소재가 만들어졌는지 검증 (있으면 빨간 플래그).

**투자자 미팅 답변용 문장 자동 생성**: "이거 [어떤 작품] 같은 건가요?" 질문에 답변할 문장.

### ⑥ Market 진단

3개 시장 동시 진단 (각 ★1~★5):

**한국 시장**
- 타겟 (성별/연령/취향)
- 예상 예산 (저예산/중예산/대작)
- 유통 경로 (극장/Tving/Wavve/Coupang Play/Netflix Korea/지상파)
- IP 확장 가능성

**글로벌 시장**
- 1차 타겟 국가
- 글로벌 어필 강도
- 진입 경로 (영화제/공동제작/플랫폼)
- 약점 (한국적 맥락 의존도)

**OTT 시장**
- 1순위/2순위 플랫폼 + 이유
- 최적 회차/분량
- 동시기 경쟁작 분석

**추가**:
- 시기적 적합성 (★1~★5)
- 위험 신호 2~3개

### ⑦ 최종 판정 (Opus)

지금까지의 6개 진단 결과를 **Opus 4.7**이 종합합니다 (60~90초 소요).

**판정 기준**:
- **GO**: 후크 35+ + 시장성 ★3+ + 치명적 유사작 없음 + 위험 적음
- **CONDITIONAL**: 일부 약점 있으나 보강 시 진행 가능
- **NOGO**: 본질적 약점 (후크 25 미만 OR 치명적 유사작 OR 시장 부적합)

**산출물**:
- 판정 사유 (4~6문장)
- 충족 조건 (CONDITIONAL의 경우)
- 대안 제시 (NOGO의 경우)
- 확정된 핵심 결정 3개
- Creator Engine에서 결정할 펜딩 질문 3개
- **임원 요약 (Executive Summary)**: 한 페이지 설명용
- **LOCKED 시드 패키지**: Creator Engine 자동 입력용

### ⑧ Export

두 가지 산출물 다운로드:

1. **진단보고서 DOCX**
   - `IdeaDiagnostic_{제목}_{날짜}.docx`
   - 7단계 모든 진단 결과 + LOCKED 시드 패키지 본문
   - Creator Engine과 동일 디자인 (노란 헤더 + 병기)

2. **LOCKED 시드 JSON**
   - `IdeaSeed_{project_id}_{날짜}.json`
   - Creator Engine ① 화면 자동 입력용

---

## 4. DOCX 진단보고서 구조

```
Cover (IDEA DIAGNOSTIC REPORT + 제목 + 메타)
  ↓
1. 원본 아이디어 ORIGINAL IDEA
  ↓
2. 로그라인 정제 LOGLINE REFINEMENT (3개 변형 + 추천)
  ↓
3. 후크 진단 HOOK DIAGNOSTIC (5축 점수 테이블 + 강점/약점/보강)
  ↓
4. 포맷 추천 FORMAT RECOMMENDATION (5개 포맷 점수 + 1순위)
  ↓
5. 레퍼런스 매핑 REFERENCE MAPPING (5편 + 차별화 + 투자자 답변)
  ↓
6. 시장성 진단 MARKET DIAGNOSTIC (한국/글로벌/OTT 3개 시장)
  ↓
7. 최종 판정 FINAL VERDICT (GO/CONDITIONAL/NOGO + 사유)
  ↓
임원 요약 EXECUTIVE SUMMARY
  ↓
LOCKED 시드 패키지 LOCKED SEED PACKAGE (전체 LOCKED 항목)
  ↓
Footer (© 2026 BLUE JEANS PICTURES · Idea Engine v1.0)
```

## JSON 시드 패키지 구조

```json
{
  "_idea_engine_meta": {
    "version": "1.0",
    "generated_at": "ISO timestamp",
    "project_id": "프로젝트 식별자",
    "verdict": "GO | CONDITIONAL | NOGO",
    "hook_score": 39
  },
  "title": "한글 제목",
  "raw_idea": "LOCKED 로그라인",
  "genre": "메인 장르",
  "target_market": "국내 타겟",
  "format": "주력 포맷",
  "locked_seed": {
    "project_id": "...",
    "title_kr": "...",
    "title_en": "...",
    "locked_logline": "...",
    "locked_genre": { "primary": "...", "secondary": "...", "tertiary": "..." },
    "locked_format": { "primary": "...", "episode_count": "...", "runtime": "...", "ip_strategy": "..." },
    "locked_target": { "domestic": "...", "global": "..." },
    "locked_theme": { "surface": "...", "deep": "..." },
    "locked_references": [...],
    "locked_hook_score": 39,
    "locked_market_stars": { "domestic": 4, "global": 3, "ott": 4 },
    "locked_distribution_priority": "...",
    "locked_risks_to_address": [...]
  },
  "executive_summary": "임원 요약",
  "pending_decisions": ["Creator Engine에서 결정할 질문 3개"]
}
```

---

## 5. Creator Engine 연동

`CREATOR_ENGINE_PATCH.md` 참조.

요약:
1. Creator Engine ① 화면 상단에 "Idea Engine JSON 업로드" expander 추가
2. JSON 업로드 시 입력 필드 자동 채움
3. `st.session_state["locked_seed"]`에 LOCKED 데이터 보관
4. Stage ②~⑦에서 LOCKED 항목을 변경하지 않도록 프롬프트에 컨텍스트 주입

---

## 6. 에러 대응

### JSON 파싱 에러

`safe_json_loads`가 4단계 자동 복구를 수행합니다 (Creator Engine과 동일):
1. 그대로 파싱
2. 첫 `{` 부터 마지막 `}` 까지
3. 에러 위치 반복 수정 (30회)
4. 모든 값 내부 쌍따옴표 강제 치환

실패 시 "Raw 응답 보기" expander에서 원본 확인 가능.

### Gate 미통과 (FAIL)

- Override 버튼으로 강제 진행 가능
- 또는 해당 단계를 재실행
- 보강 제안을 참고하여 ① 입력 단계로 돌아가 아이디어 보강

### API 타임아웃

- 각 Stage가 독립적이므로 실패한 Stage만 재실행 가능
- 사이드바에서 이전 완료 단계로 이동 가능

### Opus 최종 판정 실패

- 6개 진단 데이터가 모두 있어야 Stage ⑦ 진행 가능
- Opus가 응답 못 하는 경우 모델 정책을 모두 Sonnet으로 변경 (커스터마이징 참조)

---

## 7. 커스터마이징

### 모델 변경

`main.py` 상단:

```python
ANTHROPIC_MODEL_SONNET = "claude-sonnet-4-6"
ANTHROPIC_MODEL_OPUS = "claude-opus-4-7"
```

전체를 Sonnet으로 통일하려면:

```python
ANTHROPIC_MODEL_OPUS = "claude-sonnet-4-6"
```

### Gate 통과 기준 변경

`prompt.py`의 `HOOK_DIAGNOSTIC_PROMPT` 내부 [총점 해석] 섹션 수정.

### 디자인 변경

- **CSS**: `main.py` 상단 `CSS` 변수
- **테마**: `.streamlit/config.toml`
- **노란색**: `--yellow: #FFCB05` 변경
- **네이비**: `--navy: #191970` 변경

### 5축 진단 축 변경

`prompt.py`의 `HOOK_DIAGNOSTIC_PROMPT`에서 5축 정의 수정.
`main.py`의 `axis_kr` 딕셔너리도 함께 수정 필요.

### 포맷 추가 / 변경

`prompt.py`의 `FORMAT_RECOMMEND_PROMPT`에 포맷 추가.
`main.py`의 `format_kr` 딕셔너리도 함께 수정 필요.

---

© 2026 BLUE JEANS PICTURES · Idea Engine v1.0
