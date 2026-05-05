# 💡 Idea Engine v2.0 + v1.1

> **BLUE JEANS PICTURES · Creative Discovery & Triage Engine**
>
> v2.0 HUNTER 트랙(아이디어 발굴) + v1.1 패치(Creator Engine v2.5.2 정합)
>
> 최종 업데이트: 2026-05-05

---

## 무엇이 바뀌었는가

이번 릴리스는 두 개의 변화를 동시에 담는다.

**v2.0 — HUNTER 트랙 (아이디어 발굴)**
HOME 진입 화면에서 HUNTER(발굴) / TRIAGE(진단) 두 트랙을 선택할 수 있다. HUNTER는 작가의 5가지 영감 유형(욕망·시대·트렌드·What if·사실)에 맞춘 사고 확장 엔진으로, 카탈로그 조립이 아니라 작가 안에 잠재된 답을 끌어내는 입구 시스템이다. 현재 골격(모드 분기 + 사이드바 전환 + 시드 인계 구조)이 완성되어 있으며, 5개 입구 페이지의 본 구현은 후속 사이클에 채운다.

**v1.1 — Creator Engine v2.5.2 정합 (5개 신규 LOCKED 키)**
「오랜만에」 검증에서 발견된 핵심 모티프 휘발(18개 중 11개, 61%) 문제를 시드 출력 단계에서 차단한다. Creator Engine v2.5.2가 직접 흡수하는 5개 신규 LOCKED 영역을 `locked_seed_package`에 명시 출력하도록 Stage 7 프롬프트와 시드 빌더를 확장했다.

---

## 모드 분기 구조 (v2.0)

```
HOME (모드 선택)
 ├─ HUNTER 트랙 (아이디어 발굴) ─→ 시드 자동 생성 ─┐
 └─ TRIAGE 트랙 (7단계 진단·판정) ←──────────────┘
                  │
                  └─→ LOCKED 시드 JSON ─→ Creator Engine v2.5.2
```

사이드바에서 언제든 모드 전환 가능. HUNTER에서 시드가 준비되면 사이드바에 "→ TRIAGE로 전송" 버튼이 노출되어 한 번에 인계된다.

## 5개 입구 (HUNTER 트랙 — 후속 구현 예정)

| 입구 | 트리거 | 예시 |
|---|---|---|
| 1 | 욕망 | "로맨스 만들고 싶다" → 작가 안의 답을 캐묻는 질문 5개 |
| 2 | 시대 | "IMF 때 이야기" → period_pack 10시대 활용 시점·공간·사건 |
| 3 | 트렌드 | "회빙환 해야 하나" → 추종/변주/회피 3길 제시 |
| 4 | What if | "로또+일주일 반복" → 가설 확장 + 함정 경고 + 톤 분기 |
| 5 | 사실 | "1945.8.15. 일본인" → 역사 디테일 펼침 + 5시점 시드 |
| 0 | 자유 텍스트 | 입력만 던지면 5개 입구 중 하나로 자동 분류 |

## v1.1 신규 LOCKED 키 5종

| 키 | 용도 | 빈 값 |
|---|---|---|
| `locked_core_decisions` | 포맷·결말·음악·스타일 작품 본질 LOCK | `[]` |
| `locked_music_rules` | 음악·노래·OST 사용 규약 (장르 특화) | `{}` |
| `locked_visual_motifs` | 두 타임라인·두 세계 연결 시각 오브제 | `[]` |
| `locked_ending_form` | 결말 형식의 본질 (헤어짐·결합·모호 등) | `{}` |
| `locked_creator_questions` | Creator Engine이 답해야 할 미해결 질문 | `[]` |

각 키의 필드명·타입은 Creator Engine v2.5.2 main.py(line 3777~3860)와 1:1 정합된다.

### 빈 값 처리 원칙

작품 특성상 적용되지 않는 키는 **키 자체를 생략하지 않고** 빈 배열/빈 객체로 명시 출력한다. 이는 Creator Engine 측에 "Idea Engine이 의식적으로 비웠다"는 신호로 해석되어, 누락 디버깅과 fallback 작동에 유리하다.

## 「오랜만에」 케이스 효과 예측

| 측정 지점 | v1.0 + Creator v2.5.1 | v1.1 + Creator v2.5.2 |
|---|---|---|
| LOCKED 등록 라인 수 | 약 11라인 | 약 34라인 (+23) |
| 핵심 모티프 휘발률 | 약 61% | ≤ 10% (차단) |
| 음악 규약 위반 | 발생 가능 | 차단 (노래방·LP 코스프레 등) |
| 시각 모티프 누락 | 발생 가능 | 차단 (중정·수강증·통화연결음) |
| 결말 형식 약화 | 발생 가능 | 차단 (헤어짐 + 수용 LOCK) |
| Rewrite 점수 (예상) | 7.1점 | 7.7~8.0점 |

## 7단계 파이프라인 (TRIAGE 트랙)

| Stage | 단계 | 모델 | 비고 |
|---|---|---|---|
| ① | 아이디어 입력 | — | HUNTER 시드 자동 입력 가능 |
| ② | 로그라인 정제 | Sonnet 4.6 | |
| ③ | Hook 진단 (Gate 0) | Sonnet 4.6 | 5축 채점 |
| ④ | Format 추천 | Sonnet 4.6 | 영화/시리즈/미니/숏폼/소설 |
| ⑤ | Reference 매핑 | Sonnet 4.6 | 치명적 유사작 경고 |
| ⑥ | Market 진단 | Sonnet 4.6 | 한국·글로벌·OTT 별점 |
| ⑦ | **최종 판정** | **Opus 4.7** | GO/CONDITIONAL/NOGO + LOCKED 시드 (v1.1 5키 포함) |
| ⑧ | Export | — | DOCX 보고서 + JSON 시드 |

## Gate 0 통과 기준

Hook Score 5축 × 10점 = 50점 만점

| 점수대 | 판정 |
|---|---|
| 45~50 | 🟢 즉시 GO (희귀) |
| 35~44 | 🟢 GO (대다수의 좋은 기획) |
| 25~34 | 🟡 CONDITIONAL (조건부 진행) |
| 0~24 | 🔴 NOGO (재고 권장) |

## 산출물

### 1. 진단 보고서 DOCX

- 7단계 모든 진단 결과
- LOCKED 시드 패키지 본문
- **v1.1 신규 5개 LOCKED 영역 섹션**
- 파일명: `IdeaDiagnostic_{제목}_{날짜}.docx`

### 2. LOCKED 시드 JSON (v1.1)

기존 v1.0 13개 키 + 신규 5개 키 = 총 18개 키. Creator Engine v2.5.2가 그대로 흡수.

```json
{
  "_idea_engine_meta": {
    "version": "v2.0",
    "patch": "v1.1 (Creator Engine v2.5.2 정합 5키)",
    ...
  },
  "locked_seed": {
    // 기존 v1.0 키 (13개)
    "locked_logline": "...",
    "locked_genre": { "primary": "...", "secondary": "...", "tertiary": "..." },
    "locked_format": { ... },
    "locked_target": { "domestic": "...", "global": "..." },
    "locked_theme": { ... },
    "locked_references": [ ... ],
    "locked_hook_score": 40,
    "locked_market_stars": { ... },
    "locked_distribution_priority": "...",
    "locked_risks_to_address": [ ... ],

    // v1.1 신규 키 (5개)
    "locked_core_decisions": [
      { "category": "포맷", "rule": "장편 극영화 LOCK...", "rationale": "..." }
    ],
    "locked_music_rules": {
      "기본 원칙": "...",
      "금지 사항": [ ... ],
      "권장 사항": [ ... ],
      "의도": "..."
    },
    "locked_visual_motifs": [
      { "motif": "건물의 중정 구조", "function": "두 타임라인 연결핀..." }
    ],
    "locked_ending_form": {
      "type": "헤어짐 + 각자의 수용",
      "emotional_resolution": "...",
      "final_image": "...",
      "forbidden": "결합·재결합 금지"
    },
    "locked_creator_questions": [
      {
        "question": "노트 발견 씬의 정확한 위치",
        "options": ["2막 후반", "3막 진입점"],
        "importance": "high"
      }
    ]
  }
}
```

## Creator Engine 연동

Creator Engine ① 화면 상단의 "Idea Engine JSON 업로드" 버튼으로 위 JSON을 업로드하면, v2.5.2 흡수 로직이 18개 키 전부를 `locked_seed`에 등록한다. 신규 5개 영역은 Creator Engine 모든 단계(Brainstorm/Core/Character/Structure/Treatment)에서 작품 본질로 절대 보존된다.

### 하위 호환성

- v1.0 시드(13키만)도 Creator Engine v2.5.2가 fallback으로 정상 흡수
- 기존 프로젝트 100% 호환
- 신규 5개 키 중 일부만 출력해도 부분 추출 동작

## 듀얼 모델 정책

- 진단 (②~⑥): **Sonnet 4.6** — 빠르고 저렴 (입구 게이트)
- 최종 판정 (⑦): **Opus 4.7** — 6개 진단 종합 + v1.1 신규 5개 영역 산출
- HUNTER 발굴 (예정): **Sonnet 4.6**

## 디자인 시스템

| 요소 | 값 |
|---|---|
| Primary | `#FFCB05` (BLUE JEANS Yellow) |
| Background | `#F7F7F5` |
| Text | `#1A1A2E` |
| Navy | `#191970` |
| Display Font | Playfair Display |
| Body Font | Pretendard / Noto Sans KR |

Writer Engine v3.1 디자인 시스템 100% 동일.

## 설치 및 실행

```bash
streamlit run main.py
```

Streamlit Cloud Secrets에 `ANTHROPIC_API_KEY` 추가 필수.

## 사용 케이스

### Case 1 — 본인 아이디어 스크리닝

머릿속 아이디어 → TRIAGE 트랙 → 35점 이상만 Creator Engine으로

### Case 2 — 외부 작가 입구 게이트

신인 작가 아이디어 → 5분 진단 → "받을 만한 소재인가" 판정

### Case 3 — 발굴부터 시작 (HUNTER 트랙, 예정)

머릿속에 아무것도 없을 때 → HUNTER 5개 입구 → 시드 발굴 → TRIAGE 인계 → Creator Engine

### Case 4 — 이미 확정된 IP

「물귀신」, 「왕게임」 같이 이미 LOCKED가 확정된 IP는 Idea Engine을 거치지 않고 Creator Engine에 바로 입력 가능.

## 버전 이력

| 버전 | 변경 사항 |
|---|---|
| v2.0 + v1.1 (2026-05-05) | HUNTER 트랙 골격 + Creator v2.5.2 정합 5개 LOCKED 키 출력 |
| v1.0 (2026-04-25) | TRIAGE 트랙 7단계 완성. 「만물탐정」(34/50) · 「오랜만에」(40/50) 검증 |

## 라이선스

© 2026 BLUE JEANS PICTURES · Internal Use Only
