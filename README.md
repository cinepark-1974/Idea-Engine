# 💡 Idea Engine v1.0

> **BLUE JEANS PICTURES · Creative Triage Engine**
>
> Creator Engine 입구의 진단·판정 엔진
>
> 최종 업데이트: 2026-04-25

---

## 무엇인가

Idea Engine은 **모호한 아이디어를 Creator Engine이 받아먹을 수 있는 LOCKED 시드 패키지로 변환**하는 진단 엔진입니다.

```
[모호한 아이디어]
    ↓
Idea Engine (Hook 진단 + Format 추천 + Reference 매핑 + Market 진단)
    ↓
[GO / CONDITIONAL / NOGO 판정] + [LOCKED 시드 JSON]
    ↓
Creator Engine ① 화면 → JSON 업로드 → 자동 입력
    ↓
Creator Engine ② Brainstorm 진행
```

## 왜 만들었는가

Creator Engine v1.2는 **어떤 입력이든 그럴듯한 기획서로 만들어버립니다**. 즉 나쁜 소재도 좋은 기획서로 포장됩니다.

Idea Engine은 입구에 게이트를 두어:
1. **나쁜 소재는 Creator Engine을 돌리지 않게 막음** (시간·비용 절약)
2. **좋은 소재는 LOCKED 항목을 미리 확정**해서 Creator Engine 파이프라인의 드리프트 방지
3. **외부 작가가 가져온 아이디어를 5분 안에 진단** (BLUE JEANS PICTURES IP 입수 게이트)

## 7단계 파이프라인

| Stage | 단계 | 모델 | 설명 |
|-------|------|------|------|
| ① | 아이디어 입력 | - | 1줄~1단락 자유 텍스트 |
| ② | 로그라인 정제 | Sonnet 4.6 | 산업 표준 로그라인 3개 변형 + 추천 |
| ③ | Hook 진단 (Gate 0) | Sonnet 4.6 | 5축 채점 (구체성/갈등/장르/판돈/독창성) |
| ④ | Format 추천 | Sonnet 4.6 | 영화/시리즈/미니/숏폼/소설 5개 적합도 |
| ⑤ | Reference 매핑 | Sonnet 4.6 | 유사작 5편 + 차별점 + 치명적 유사작 경고 |
| ⑥ | Market 진단 | Sonnet 4.6 | 한국·글로벌·OTT 3개 시장 별점 평가 |
| ⑦ | **최종 판정** | **Opus 4.7** | GO/CONDITIONAL/NOGO + LOCKED 시드 패키지 |
| ⑧ | Export | - | DOCX 보고서 + JSON 시드 |

### 듀얼 모델 정책

- **진단 (②~⑥)**: Sonnet 4.6 — 빠르고 저렴 (입구 게이트)
- **최종 판정 (⑦)**: Opus 4.7 — 6개 진단을 종합한 최종 결정은 가장 정확한 모델로

## Gate 0 통과 기준

Hook Score 5축 × 10점 = **50점 만점**

| 점수대 | 판정 |
|--------|------|
| 45~50 | 🟢 즉시 GO (희귀) |
| 35~44 | 🟢 GO (대다수의 좋은 기획) |
| 25~34 | 🟡 CONDITIONAL (조건부 진행) |
| 0~24 | 🔴 NOGO (재고 권장) |

Override 버튼으로 강제 진행 가능.

## 산출물

### 1. 진단 보고서 DOCX
- 노란 하이라이트 섹션 헤더 + 한글/ENGLISH 병기 (Creator Engine과 동일 디자인)
- 7단계 모든 진단 결과
- LOCKED 시드 패키지 본문 포함
- 파일명: `IdeaDiagnostic_{제목}_{날짜}.docx`

### 2. LOCKED 시드 JSON
- Creator Engine ① 화면 자동 입력용
- 다음 6개 LOCKED 항목 확정:
  - `locked_logline`
  - `locked_genre` (primary/secondary/tertiary)
  - `locked_format` (primary/episode_count/runtime/ip_strategy)
  - `locked_target` (domestic/global)
  - `locked_theme` (surface/deep)
  - `locked_references`
- 파일명: `IdeaSeed_{project_id}_{날짜}.json`

## Creator Engine 연동

Creator Engine ① 화면 상단에 **"Idea Engine JSON 업로드"** 버튼이 추가됩니다 (Creator Engine 별도 패치 필요).

업로드 시 다음이 자동으로 채워집니다:
- 제목
- 원본 아이디어 (LOCKED 로그라인으로 채워짐)
- 장르 (LOCKED genre.primary)
- 타겟 시장 (LOCKED target.domestic)
- 포맷 (LOCKED format.primary)

또한 `locked_seed` 데이터가 Creator Engine session_state에 저장되어, 이후 Stage들에서 이 LOCKED 항목들을 변경하지 않습니다.

## 설치 및 실행

### 로컬

```bash
pip install -r requirements.txt
streamlit run main.py
```

### Streamlit Cloud

1. GitHub repo에 푸시
2. Streamlit Cloud에서 새 앱 생성
3. Secrets에 `ANTHROPIC_API_KEY` 추가

## 디자인 시스템 (Creator Engine과 100% 동일)

| 요소 | 값 |
|------|---|
| Primary | `#FFCB05` (BLUE JEANS Yellow) |
| Background | `#F7F7F5` |
| Text | `#1A1A2E` |
| Navy | `#191970` |
| Display Font | Playfair Display |
| Body Font | Noto Sans KR |
| 섹션 헤더 | 노란 하이라이트 + 한글/ENGLISH 병기 |

## 사용 케이스

### Case 1 — 본인 아이디어 스크리닝 (선택)

대표님 머릿속 50개 아이디어 → Idea Engine 통과 → 35점 이상만 Creator Engine으로

### Case 2 — 외부 작가 입구 게이트 (필수)

신인 작가가 가져온 아이디어 → 5분 진단 → "받을 만한 소재인가" 판정

### Case 3 — 이미 확정된 IP (불필요)

〈물귀신〉, 〈왕게임〉 같이 이미 LOCKED가 확정된 IP는 Idea Engine을 거치지 않고 Creator Engine에 바로 입력 가능. **Idea Engine은 필수 게이트가 아닙니다.**

## 라이선스

© 2026 BLUE JEANS PICTURES · Internal Use Only
