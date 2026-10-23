# Creator Engine 제안서 — Market Lens VN 인계 정합

- 발신: Idea Engine v2.3.5 (Market Lens VN)
- 수신: Creator Engine (현행 v2.7.2 기준)
- 작성일: 2026-10-23
- 관련 브랜치: `cinepark-1974/idea-engine` · `vn-market-lens-v2.3.5`

---

## 0. 요약

Idea Engine v2.3.5가 베트남(VN) 시장 프로필과 Stage 6 「VN 8축 평가」를 추가했다.
그런데 현재 시드 JSON은 시장 정보를 `target_market` **자유 서술 한 줄**(`locked_target.domestic`)로만 넘긴다.
시장 코드(KR·JP·ID·VN), 일본 진입 트랙, VN 8축 평가, 현지화 조건, 예상 등급은 Creator Engine에 **하나도 도달하지 않는다.**

이 제안서는 두 부분으로 나뉜다.

| 구분 | 내용 | 담당 |
|---|---|---|
| A | 시장 정보를 구조화해 `_idea_engine_meta.market_lens`로 인계 (LOCKED 키 아님, 24키 유지) | Idea Engine v2.3.6 |
| B | Creator Engine이 그 정보를 읽고, 한국 기준 룰이 베트남 작품에 잘못 적용되지 않도록 막는 장치 | Creator Engine |

원칙은 하나다. **시장 렌즈는 참고 정보이며, LOCKED 설정을 바꾸는 근거가 아니다.**

---

## A. Idea Engine 측 선행 작업 (v2.3.6 예정)

### A-1. 신규 메타 `_idea_engine_meta.market_lens`

LOCKED 키가 아니므로 Creator의 24키 흡수 로직에는 영향이 없다. 키가 없으면 v2.3.5 이전 시드로 간주한다.

```json
"_idea_engine_meta": {
  "market_lens": {
    "schema": "market_lens_v1",
    "target_market_raw": "베트남 + 한국 공동제작",
    "primary": "VN",
    "secondary": "KR",
    "japan_doc_mode": false,
    "japan_track": "",
    "vietnam_lens_mode": true,
    "lens_data_as_of": "2026-10-23",
    "vn_evaluation": {
      "axes": [
        {
          "axis": "regulatory_risk",
          "label": "규제 위험",
          "stars": 3,
          "verdict": "판정 1~2문장",
          "evidence": [
            {"type": "VERIFIED", "text": "근거", "source": "S6"},
            {"type": "CREATIVE_JUDGMENT", "text": "근거", "source": ""}
          ]
        }
      ],
      "expected_rating": "T16 — 근거 1문장",
      "primary_window": "극장→OTT — 근거 1문장",
      "localization_conditions": ["현지 제작 서비스 업체 계약", "현지 공동 작가 또는 자문 어태치"],
      "verification_required": ["원작 판권 이전 절차"]
    },
    "sources": [
      {"id": "S5", "name": "베트남 영화법 05/2022/QH15", "as_of": "2023-01-01 시행", "url": "..."}
    ]
  }
}
```

| 필드 | 값 | 비고 |
|---|---|---|
| `primary` / `secondary` | `KR` `JP` `ID` `VN` / `null` | `market_lens_pack.resolve_market_lens()` 결과 그대로 |
| `japan_doc_mode` · `japan_track` | bool · `INDIE_ARTHOUSE` `KR_REMAKE_TARGET` `COPROD_VIPO` `NONE` | 기존 Stage 6 출력에서 가져옴 (그동안 미인계) |
| `vn_evaluation` | Stage 6 `vn_market_evaluation`에서 `applied` 제외 | VN이 없으면 빈 객체 `{}` |
| `evidence[].type` | `VERIFIED` `INFERENCE` `CREATIVE_JUDGMENT` `VERIFICATION_REQUIRED` | 4종 고정 |
| `sources` | VN 렌즈 출처 S1~S10 | VN이 없으면 빈 배열 `[]` |

### A-2. 유지하는 것

- LOCKED 24키, `target_market` 최상위 필드, `locked_target` 문면은 그대로 둔다.
- 기존 KR·JP·ID 시드는 `market_lens`가 추가될 뿐 나머지는 바뀌지 않는다.

---

## B. Creator Engine 측 제안

우선순위: **P1** 인계 정합에 필수 · **P2** 오적용 방지 · **P3** 품질 향상

> Creator Engine 현행 코드를 이쪽에서 열람하지 못했다. 아래 "확인 필요" 항목은 Creator 측에서 현행 코드와 대조한 뒤 적용 여부를 판단해 주기 바란다.

### B-1. [P1] 시장 코드 수신 — 자유 서술 파싱 금지

- `_idea_engine_meta.market_lens.primary` / `secondary`를 시장 판단의 유일한 근거로 쓴다.
- `target_market` 문자열을 부분 문자열로 매칭해 시장을 추정하지 않는다.
  - 이유: 미해결 이슈 #3(「미니시리즈」가 「시리즈」로 오인)과 같은 구조의 오류가 시장에서도 생긴다. 예) "베트남 + Netflix SEA"를 인도네시아로 읽는 문제. Idea Engine은 v2.3.5에서 이 문제를 상류에서 처리했다.
- `market_lens` 키가 없으면 현행 동작(한국 기준)을 유지한다.

### B-2. [P1] LOCKED 불변 — 현지화 조건은 의제로만

- `vn_evaluation.localization_conditions`는 Creator 의제(작가 결정 대기 항목)로 표시한다. 인물·배경·결말을 자동으로 고치지 않는다.
- `VERIFICATION_REQUIRED` 항목은 Creator가 사실로 단정하지 않는다. 그대로 의제로 넘기거나 Creator 웹 리서치로 확인한 뒤 출처를 달아 쓴다.
- `expected_rating`은 Idea Engine의 창작적 판단(`CREATIVE_JUDGMENT`)이다. 확정 등급으로 표기하지 않는다.

### B-3. [P1] 하위 호환

| 시드 | Creator 동작 |
|---|---|
| `market_lens` 없음 (v2.3.5 이전) | 현행 그대로 |
| `primary` = KR | 현행 그대로 |
| `primary` = JP / ID | 현행 그대로 + `japan_track` 표시 (선택) |
| `primary` 또는 `secondary` = VN | B-4 ~ B-8 적용 |

### B-4. [P2] 장르 룰팩 — 한국 10분류 유지, VN 장르군은 룰팩 키로 쓰지 않음

- 룰팩 호출 키는 지금처럼 `locked_genre_primary`(한국 10분류)만 쓴다.
- VN 렌즈의 8개 장르군(가족·휴먼 / 코미디·로코 / 로맨스·멜로 / 액션·범죄·스릴러 / 역사·전쟁 / 공포·미스터리 / 판타지·SF·애니 / 독립·예술)은 시장 분석 축이다. 신규 룰팩을 만들거나 장르 키를 바꾸지 않는다.
- 단, 아래 두 장르는 VN 작품에 한국 룰을 그대로 얹으면 오류가 난다. 경고 플래그를 권한다.

| 장르 | 한국 룰팩의 전제 | VN 작품에서의 문제 | 제안 |
|---|---|---|---|
| HORROR | 오컬트·무속 (〈곡성〉〈파묘〉 계열) | 베트남 민속 신앙을 한국 무속으로 대체할 위험. 2026-06 베트남 영화국 공문이 과도한 유혈·미신 요소에 신중을 권고 (규정이 아닌 권고) | 한국 무속 장치 자동 적용 금지 + "현지 민속 고증 필요" 의제 |
| PERIOD | 사극·일제강점기·한국 현대사 | 베트남 현대사·전쟁사를 한국사 시대 규칙으로 처리할 위험. 베트남 영화법 제9조가 역사 왜곡·혁명 성과 부정·영웅 모욕을 금지 | 한국 시대 팩 비적용 + 제9조 점검 의제 |

### B-5. [P2] 시대 팩 · 직업 팩 오적용 차단 (확인 필요)

- 「period_pack」의 한국 시대 규칙(SAGEUK·COLONIAL·MODERN_HIST)은 무대가 베트남인 장면에 적용하지 않는다.
- 「profession_pack」의 직업·제도 현실은 한국 제도 기준이다. 베트남 경찰·법원·행정 등 현지 기관에 속한 인물에는 적용하지 않고, "현지 제도 고증 필요"로 표시한다.
- 한국인 인물이 베트남에 있는 경우(주재원·유학생·교민 등)는 한국 쪽 직업 현실을 그대로 적용해도 된다. 판정 기준은 "그 인물이 어느 나라 제도 안에서 일하는가"다.

### B-6. [P2] Reality Gate 점검 항목 추가

VN이 포함된 시드에서는 Reality Gate에 아래 사실을 점검 기준으로 추가한다. 모두 Idea Engine 렌즈에서 `VERIFIED`로 확인된 항목이다.

| 항목 | 근거 |
|---|---|
| 외국 제작사가 베트남에서 촬영하려면 베트남 영화 제작 서비스 업체와 계약하고 문화체육관광부 허가(베트남어 상세 촬영 대본 제출)를 받아야 한다 | 영화법 제13조 (S5) |
| 상영 금지 내용 — 국가 통합 훼손, 역사 왜곡, 종교 모욕, 아동 권리 침해, 성차별 등 | 영화법 제9조 (S5) |
| 등급 6종 P · K · T13 · T16 · T18 · C, 평가 기준 7가지(주제, 폭력, 노출·성, 마약, 공포, 언어, 위험 모방 행동) | 영화법 제32조 (S5) · 시행규칙 05/2023 (S6) |

작품 속 플롯이 "외국 촬영팀이 현지에서 허가 없이 촬영한다" 같은 설정이라면 그것은 **사실 오류가 아니라 극적 장치**다. 오탐으로 처리하지 않는다.

### B-7. [P3] 수위 가이드 — `expected_rating` 연동 (선택)

- `primary` = VN이고 작가가 목표 등급을 정했다면, 장면 설계 단계에서 시행규칙 05/2023의 7가지 기준으로 수위 체크리스트를 띄운다.
- 예: 목표 T16이면 자해·자살은 간접·짧게, 공포는 강도 높되 짧게. 목표 T18이어도 노골적 성행위는 원칙적으로 불가.
- 강제 차단이 아니라 표시만 한다. 수위 결정은 작가 몫이다.

### B-8. [P3] 수치 생성 금지 전파 · 리서치 출처

- 시장 섹션(피칭 요약 등)을 쓸 때 VN 제작비·손익분기점·관객 수 예측·미래 개봉 일정·특정 배급사의 선택 가능성을 새로 만들지 않는다. Idea Engine 렌즈도 이 수치들을 생성하지 않는다.
- 렌즈의 `VERIFIED` 수치를 인용할 때는 출처 번호와 기준일(`lens_data_as_of`)을 함께 표기한다.
- Creator 웹 리서치 화이트리스트에 베트남 시장·법령 확인용 도메인 추가를 권한다. 확인 필요: 현행 화이트리스트 구성.
  - 시장: `acfm.kr`, `kobiz.or.kr`
  - 법령: `thuvienphapluat.vn`, `vbpl.moj.gov.vn`

---

## C. 엔진 간 미결 의제

| # | 의제 | 관련 엔진 |
|---|---|---|
| 1 | 베트남어 대사 표기 규칙 — 한국어 번역 대사로 쓰고 언어를 표기할지, 원어 병기할지 | Creator · Writer |
| 2 | 한·베 공동제작 시드의 `locked_target.domestic` 표기 — 1차 시장명을 문면에 고정할지 | Idea · Creator |
| 3 | 기존 미해결 이슈 3건(`episodes`/`episode_count`, `platform`·`confidence`·`rationale` 소비부, 미니시리즈 오인) — 이번 제안과 별개로 유지 | Creator |

---

## D. 검증 계획 (양측 공통)

| 시드 | `target_market` | 확인할 것 |
|---|---|---|
| 1 | 한국 + 글로벌 | 현행과 동일하게 동작 (회귀) |
| 2 | 한국 + 베트남 | `secondary` = VN 인식, 의제 생성, LOCKED 불변 |
| 3 | 베트남 + 한국 공동제작 | `primary` = VN, B-4 장르 경고 · B-5 팩 오적용 차단 · B-6 Reality Gate 항목 작동 |

1번 시드는 이미 검증된 「클레어의 서울 수비니어샵」을 타겟 시장만 바꿔 재사용하면 LOCKED 47키 비교가 바로 가능하다.

---

## E. 일정 제안

1. Idea Engine v2.3.5 main 병합 (베트남 렌즈 운영 개시)
2. Idea Engine v2.3.6 — A-1 `market_lens` 메타 인계 구현
3. Creator Engine — B-1 · B-2 · B-3 (P1) 우선 반영
4. D 검증 3건 후 B-4 ~ B-8 순차 반영
