# 💡 BLUE JEANS · Idea Engine

**Version: v2.0** · Patch: v2.3 · Build: 2026-08-03 · Status: Production

> **모호한 아이디어 한 줄 → Creator Engine이 그대로 받아먹는 LOCKED 시드 패키지**
>
> BLUE JEANS PICTURES · Creative Discovery & Triage Engine

> ⚠️ **버전 확인 방법**: `main.py` 상단 `ENGINE_PATCH_LEVEL` / Streamlit 사이드바 Engine Info / 이 README 최상단 — 세 곳의 버전이 일치해야 정상이다. 불일치 시 최신 파일로 덮어쓸 것.

> 📌 **이 엔진의 존재 이유**: 시나리오를 다 쓴 뒤에 "애초에 콘셉트가 틀렸다"를 발견하는 일을 막는다. 아이디어 단계에서 걸러내는 비용이 가장 싸다.

---

## v2.3 패치 (2026-08-03) — 포맷 구조화 · 인계 메타데이터

Creator Engine v2.7.2 업그레이드 요청서(주문 2·3·6) 대응.

### [1] `locked_format` 구조화 단일화 — 중복 기재 종결

**진단** — 포맷이 **두 곳에 항상 이중 기재**되고 있었다. `locked_format` 구조화 필드와, `locked_core_decisions`의 `category: "포맷"` 자유 서술이다.

원인은 Stage 7 프롬프트의 한 줄이었다.

> `- 모든 작품에 최소 2개 이상 (포맷 결정은 항상 있음).`

매 시드마다 포맷 항목을 생성하라는 명시 지시였다. 「클레어의 서울 수비니어샵」 시드에서도 `locked_core_decisions[0]`이 정확히 포맷 항목이다. 하류에서 작가가 포맷을 바꾸려면 손댈 지점이 두 곳 이상으로 흩어진다.

**변경** — `category "포맷"` 생성을 금지하고, 허용 category를 결말 / 음악 / 스타일 / 구조 / 톤 / 캐릭터 / 유통으로 재정의했다. 구조 결정도 총 회차 수를 전제하지 않도록 했다.

| | 서술 방식 |
|---|---|
| ✗ | "8부작 중 1~6화는 옴니버스, 7~8화는 빌런 트랙으로 LOCK" |
| ○ | "전반부는 독립 옴니버스, 후반부는 시즌 빌런 트랙 전면화로 LOCK" |

**`locked_format` 스키마 확장** — 4필드 → 8필드.

| 필드 | 상태 | 내용 |
|---|---|---|
| `primary` | 열거값 제약 | 9개 값 중 하나. 자유 서술 차단 |
| `confidence` | **신설** | 확정 / 잠정 / 미정 |
| `episode_count` | 유지 | Creator Engine이 실제로 읽는 키 |
| `episodes` | **신설** | `episode_count`와 동일 값. 하류 필드명 호환용 병행 출력 |
| `runtime` | 유지 | |
| `platform` | **신설** | 미정이면 빈 문자열 |
| `rationale` | **신설** | 사건 밀도·인물 수 근거 1~2문장 |
| `ip_strategy` | 유지 | 삭제 금지 원칙에 따라 존치 |

### [2] 포맷 미확정 시 "미지정" 출력 — 조기 확정 방지

**진단** — STEP 1에는 "미정 (Idea Engine이 추천)" 선택지가 있었으나, Stage 4는 5개 포맷에 점수를 매겨 **반드시 1개를 확정**하는 구조였다. 미배정으로 빠져나갈 출구가 설계에 없었다.

**변경** — 확신도 3단 판정을 신설했다.

| 확신도 | 기준 |
|---|---|
| 확정 | 1순위 8점 이상 & 2순위와 2점 이상 격차 |
| 잠정 | 1순위 6~7점, 또는 1·2순위 1점 이내 |
| 미정 | 최고점 6점 미만, 또는 사건 밀도·인물 수 판단 근거 부재 |

`미정`이면 `primary`를 `"미지정"`으로 두고 회차·분량·플랫폼을 빈 문자열 처리한다.

**상호 잠금** — 시드 조립 시 `primary`와 `confidence`가 서로를 잠근다. 한쪽이 미지정/미정이면 다른 쪽도 그에 맞춘다. 확신 없는 포맷이 배정된 채로 하류에 도달하는 경로를 코드 수준에서 차단했다.

**포맷 명칭 9열거값** — Creator Engine v2.7.2 STEP 1 selectbox와 동일하게 맞췄다.

```
미지정 / 영화 / 시리즈 / 미니시리즈 / 웹툰 / 웹소설 / 숏폼 / 다큐멘터리 / 애니메이션
```

`normalize_format_primary()`가 자유 서술을 열거값으로 정규화한다. `"OTT 시리즈 (시즌제)"` → `시리즈`, `"장편 영화 (120분)"` → `영화`. 별칭 매칭 순서는 긴 표현 우선이다(`미니시리즈`가 `시리즈`보다 앞).

### [3] 인계 메타데이터 확장 — `_idea_engine_meta`

| 필드 | 상태 | 내용 |
|---|---|---|
| `idea_engine_version` | **신설** | 엔진 버전 + 패치 레벨 전체 문자열 |
| `format_confidence` | **신설** | 포맷 확신도 승계 표기 |
| `reality_precheck` | **신설** | `performed` / `verdict` / `issues_found` / `note` — v2.4 적용 전까지 `performed=false`와 Reality Gate 실행 권고문 명시 출력 |
| `locked_source` | **신설** | 24개 LOCKED 항목별 출처 3분류 |
| `patch` | **버그 수정** | 하드코딩 → 상수 참조 |

**`locked_source` 3분류**

| 값 | 의미 | 해당 항목 |
|---|---|---|
| `writer` | 작가가 STEP 1에서 직접 입력·선택 | `title_kr` / `locked_genre` / `locked_target` / `locked_format`(선호 포맷 지정 시) |
| `engine_writer_selected` | 엔진이 후보 생성 → 작가 채택 | `locked_logline` (3안 중 선택) |
| `engine` | 진단 결과로 엔진이 생성 | 나머지 전부 |

Creator Engine은 현재 전 항목을 동일 강도로 보존한다. 이 필드가 있으면 보존 강도를 차등화할 수 있다.

**함께 수정한 버그** — 시드의 `meta.patch`가 하드코딩되어 실제 엔진이 v2.1인데도 **v1.6으로 기록**되고 있었다. 하류에서 버전 기반 결함 패턴 대응을 할 경우 한 세대 낮은 버전으로 오판할 수 있는 상태였다.

### 하위 호환성

- **LOCKED 키 24개 불변.** 필드 내부 확장이므로 키 개수 증감 없음
- 기존 시드로 진행 중인 프로젝트 **100% 무영향**. 상류 변경은 신규 시드 생성 시점부터 적용
- 최상위 `format` · `locked_format.episode_count` · `episodes` **3중 병행 출력**
- 값이 없어도 키를 생략하지 않고 빈 문자열로 명시 출력
- v1.1~v2.1 구버전 시드를 로드해도 `normalize_locked_format()`이 정규화 후 통과 (검증 완료)

---

## v2.2 패치 (2026-08-03) — 로그라인 포맷 어휘 차단 · 직업 역할 확인

Creator Engine v2.7.2 요청서(주문 1·5) 대응.

### [1] 로그라인 포맷 어휘 금지 — 최우선 결함

**진단** — 로그라인에 `"티빙 오리지널 6부작 미니시리즈."` 같은 매체 표현이 혼입되는 문제. 원인은 Stage 2 프롬프트의 표준 포맷 정의였다.

```
"[주인공]이 [목표]를 위해 [장애물]에 맞서는 [장르][형식]"
                                              ↑ 이것
```

`[형식]`이 문자 그대로 매체·회차를 넣으라는 지시였다. 아울러 프롬프트 입력부에 포맷 값이 그대로 주입되고 있었다. **모델의 일탈이 아니라 프롬프트 준수의 결과였다.**

로그라인은 하류의 `logline_pack` · `pitch` · `signature_moment`로 증폭되므로, 여기서 새면 전 단계가 오염된다. 하류에서 기계적 제거도 불가능하다 — 통째로 지우면 로그라인 본문까지 사라지기 때문이다.

**변경**

- 표준 포맷에서 `[형식]` 제거. "누가 / 무엇을 원하는데 / 무엇이 막는가" 구성 원칙 명시
- 포맷 입력 라벨을 "참고 정보 — 로그라인 본문에 절대 반영하지 않는다"로 격하
- 금지 어휘 명기 — 미니시리즈 / 시리즈 / N부작 / 회차 / 회당 / 시즌 / EP / 에피소드 / 옴니버스 / 러닝타임 / 넷플릭스 / 티빙 / 디즈니+ / 웨이브 / 쿠팡플레이 / OTT 오리지널
- Stage 7 시드 조립 시점에도 재적용. 포맷 어휘가 남아 있으면 **그 어휘만 제거하고 본문은 보존**

**범위 조정** — 장르 명칭(범죄 스릴러·로맨틱 코미디·사회파 드라마)은 한국 산업 관행상 로그라인에 붙는 것이 정상이므로 존치했다. 금지 대상은 매체·회차·러닝타임·플랫폼뿐이다.

**포맷 분리 원칙** — 시드 전체에 적용되는 블록을 신설했다. 아래 8개 항목 본문에 포맷 어휘를 쓰지 않는다.

```
locked_logline / locked_core_decisions / locked_visual_motifs /
locked_creator_questions / locked_hook_signature / locked_punch_scene /
locked_ending_form / locked_theme
```

### [2] 직업 역할 분담 확인

`SHARED_RULES`에 확인 지침을 추가했다. **26개 프롬프트 전체에 공통 적용**되므로 TRIAGE·HUNTER 양쪽에서 동시에 작동한다.

적출 유형 3종:

| 유형 | 예시 |
|---|---|
| 여러 직업의 업무를 한 인물에게 몰아줌 | 결혼식 사회자가 주례의 혼인서약을 낭독 / 형사가 검사의 영장 청구 권한 행사 |
| 해당 직위에 없는 권한 행사 | 판사가 수사를 지휘 |
| 분리된 절차를 한 인물이 전부 수행 | — |

판타지·SF 설정, 장르 관습상의 과장, 작가가 의도적으로 비튼 설정은 제외한다. **확신이 없으면 핵심 업무만 쓰고 주변 업무는 부여하지 않는다.** 억지로 교정 의견을 내지 않는다.

---

## 이전 패치 요약

| 패치 | 날짜 | 내용 |
|---|---|---|
| **v2.1** | 2026-07 | 3-C+ Hook 약점 보완 게이트 (객관식 · 선택 진입). Hook 점수가 낮을 때 개방형 질문 대신 다지선다 보강안 제시 |
| **v1.6.1** | 2026-06 | 진행 백업 JSON과 시드 JSON의 파일명·버튼 라벨 명확화. 잘못된 JSON 업로드로 인한 Creator Engine 거부 오류 차단 |
| **v1.6** | 2026-06 | Story Core 5원칙 진단(3-A) 도입 |
| **v1.5** | 2026-06 | 3-A+ 5원칙 보강 발굴 단계. 3-A가 YELLOW·RED면 자동 진입 |
| **v1.4.1** | 2026-06 | Market Lens Pack — KR / JP / ID 3개 시장 프로파일 구조 주입 |
| **v1.3** | 2026-05 | 장르 10분류 + 시장 좌표 4분류 (LOCKED 22 → 24) |
| **v1.2** | 2026-05 | Story Core + Hook & Punch (LOCKED 18 → 22) |
| **v1.1** | 2026-05 | Creator Engine v2.5.2 정합 5개 LOCKED 키 (13 → 18) |
| **v1.0** | 2026-04 | TRIAGE 7단계 완성 |

---

## 구조

```
HOME (모드 선택)
 ├─ HUNTER 트랙 (아이디어 발굴) ─→ 시드 자동 생성 ─┐
 └─ TRIAGE 트랙 (7단계 진단·판정) ←──────────────┘
                  │
                  └─→ LOCKED 시드 JSON (24키)
                          │
                          └─→ Creator Engine v2.7.2 → Writer Engine v3.1.1
```

사이드바에서 언제든 모드 전환이 가능하다. HUNTER에서 시드가 준비되면 "→ TRIAGE로 전송" 버튼이 노출된다.

### 파일 구성

| 파일 | 역할 |
|---|---|
| `main.py` | UI · 라우팅 · 시드 빌더 · 헬퍼 (Streamlit) |
| `prompt.py` | 26개 프롬프트 정의 |
| `market_lens_pack.py` | KR / JP / ID 시장 프로파일 주입 |

---

## HUNTER 트랙 — 5개 입구

작가 안에 잠재된 답을 끌어내는 발굴 엔진. 카탈로그 조립이 아니다.

| 입구 | 트리거 | 동작 |
|---|---|---|
| 1 | 욕망 | "로맨스 만들고 싶다" → 작가 안의 답을 캐묻는 질문 |
| 2 | 시대 | "IMF 때 이야기" → 시점·공간·사건 펼침 |
| 3 | 트렌드 | "회빙환 해야 하나" → 추종 / 변주 / 회피 3길 |
| 4 | What if | "로또 + 일주일 반복" → 가설 확장 + 함정 경고 + 톤 분기 |
| 5 | 사실 | "1945.8.15. 일본인" → 역사 디테일 + 5시점 시드 |
| 0 | 자유 텍스트 | 입력만 던지면 5개 입구 중 하나로 자동 분류 |

---

## TRIAGE 트랙 — 7단계 파이프라인

| Stage | 단계 | 모델 |
|---|---|---|
| ① | 아이디어 입력 | — |
| ② | 로그라인 정제 (3안 생성 → 작가 채택) | Sonnet 4.6 |
| ③ | Hook 진단 (Gate 0) — 4~5개 하위 단계 | Sonnet 4.6 |
| ④ | Format + 장르 + 시장 좌표 | Sonnet 4.6 |
| ⑤ | Reference 매핑 (치명적 유사작 경고) | Sonnet 4.6 |
| ⑥ | Market 진단 (한국·글로벌·OTT 별점) | Sonnet 4.6 |
| ⑦ | **최종 판정** — GO / CONDITIONAL / NOGO + LOCKED 시드 | **Opus 4.7** |
| ⑧ | Export — DOCX 보고서 + 시드 JSON | — |

### Stage 3 하위 흐름

```
3-A  Story Core 5원칙 진단
      │
      ├─ GREEN ─────────────────┐
      └─ YELLOW · RED → 3-A+ 보강 발굴 ─┤
                                        ▼
3-B  Hook & Punch 발굴 (질문지 → 답변 → 빌드)
      ▼
3-C  5축 채점
      │
      └─ (선택) 3-C+ Hook 약점 보완 ─→ Stage 4
```

**3-A+ 와 3-C+ 는 모두 선택 게이트다.** 콘셉트에 확신이 있으면 우회할 수 있고, 출력 스키마는 표준 경로와 동일하다. 진행 중인 세션이 깨지지 않는다.

### Gate 0 통과 기준

Hook Score 5축 × 10점 = 50점 만점

| 점수대 | 판정 |
|---|---|
| 45~50 | 🟢 즉시 GO (희귀) |
| 35~44 | 🟢 GO |
| 25~34 | 🟡 CONDITIONAL |
| 0~24 | 🔴 NOGO |

---

## LOCKED 시드 24키

| 도입 | 개수 | 키 |
|---|---|---|
| v1.0 | 13 | `project_id` `title_kr` `title_en` `locked_logline` `locked_genre` `locked_format` `locked_target` `locked_theme` `locked_references` `locked_hook_score` `locked_market_stars` `locked_distribution_priority` `locked_risks_to_address` |
| v1.1 | +5 | `locked_core_decisions` `locked_music_rules` `locked_visual_motifs` `locked_ending_form` `locked_creator_questions` |
| v1.2 | +4 | `locked_empathy_anchor` `locked_hook_signature` `locked_punch_scene` `locked_ending_promise` |
| v1.3 | +2 | `locked_genre_primary` `locked_market_position` |

### 빈 값 처리 원칙

작품 특성상 적용되지 않는 키도 **키 자체를 생략하지 않고** 빈 배열 `[]` / 빈 객체 `{}`로 명시 출력한다. 하류에서 "Idea Engine이 의식적으로 비웠다"는 신호로 해석되어 누락 디버깅과 fallback에 유리하다.

### 시드 JSON 구조 (v2.3)

```json
{
  "_idea_engine_meta": {
    "version": "v2.0",
    "idea_engine_version": "v2.0 · v2.3 (포맷 구조화 · 인계 메타데이터) + ...",
    "patch": "v2.3 (포맷 구조화 · 인계 메타데이터) + v2.2 (...) + v2.1 (...)",
    "generated_at": "2026-08-03T06:30:48",
    "project_id": "...",
    "verdict": "GO | CONDITIONAL | NOGO",
    "hook_score": 40,
    "format_confidence": "확정 | 잠정 | 미정",
    "reality_precheck": {
      "performed": false,
      "verdict": null,
      "issues_found": 0,
      "note": "Reality Pre-Check는 v2.4 신설 예정. Creator Engine의 Reality Gate를 반드시 실행할 것."
    },
    "locked_source": {
      "title_kr": "writer",
      "locked_logline": "engine_writer_selected",
      "locked_format": "engine",
      "...": "engine"
    }
  },
  "title": "...",
  "raw_idea": "...",
  "genre": "...",
  "target_market": "...",
  "format": "시리즈",
  "locked_seed": {
    "locked_logline": "결혼식 사회를 맡은 남자가...",
    "locked_format": {
      "primary": "시리즈",
      "confidence": "잠정",
      "episode_count": "시즌1 8부작",
      "episodes": "시즌1 8부작",
      "runtime": "회당 45~55분",
      "platform": "Netflix",
      "rationale": "옴니버스 이중 구조가 시즌제 문법에 정렬",
      "ip_strategy": "OTT 1차 론칭 → 웹소설 연재 → 시즌2 그린라이트 시 웹툰"
    },
    "...": "나머지 22키"
  },
  "executive_summary": "...",
  "pending_decisions": []
}
```

---

## Market Lens Pack

`target_market` 문자열을 파싱해 시장 프로파일을 **구조적으로 주입**한다. 주입이 없으면 엔진은 인도네시아·일본 타겟에도 한국 시장 기준으로 판정한다.

| 코드 | 시장 | 특성 |
|---|---|---|
| KR | 한국 | 기본 프로파일 |
| JP | 일본 | **3개 진입 트랙만 유효** — `INDIE_ARTHOUSE` / `KR_REMAKE_TARGET` / `COPROD_VIPO`. 그 외 경로는 0점 처리 |
| ID | 인도네시아 | LSF 심의 · 라마단 개봉 타이밍 · JAFF Market · Joko Anwar 계보 등 문화·규제·산업 제약 반영 |

복합 시장(`"한국 + 일본 공동제작"`)은 primary / secondary 2단으로 해석한다.

---

## 하류 엔진 연동

### Creator Engine v2.7.2

STEP 1의 "Idea Engine JSON 업로드"에 시드를 올리면 24키 전부를 흡수한다. `_idea_engine_meta` 키가 없으면 거부되므로, **진행 백업 JSON을 이 자리에 올리지 않도록** 주의한다 (v1.6.1에서 파일명·라벨을 분리한 이유).

### 미해결 정합 이슈 3건 (2026-08-03 회신 발송)

| # | 내용 | 상태 |
|---|---|---|
| 1 | 요청서는 `episodes`를 요구했으나 Creator 코드는 `episode_count`만 읽음 | 병행 출력으로 우회. 정본 필드명 회신 대기 |
| 2 | `platform` · `confidence` · `rationale` 소비부가 Creator 측에 없음 | 하류 구현 요청 |
| 3 | **미니시리즈 시드가 반드시 시리즈로 오인됨** — 부분 문자열 매칭이 순회 순서대로 첫 히트에서 break. `"시리즈"`가 `"미니시리즈"`보다 앞에 있어 상류에서 회피 불가 | 하류 2단 매칭 교정 요청 |

상세는 `IdeaEngine_회신서_v2.3.docx` 참조.

### Writer Engine v3.1.1

Creator Engine을 거쳐 룰팩 호출 정합을 유지한다. Idea Engine이 직접 인계하지 않는다.

---

## 듀얼 모델 정책

| 용도 | 모델 |
|---|---|
| 진단 (②~⑥) · HUNTER 발굴 | **Sonnet 4.6** — 빠르고 저렴한 입구 게이트 |
| 최종 판정 (⑦) | **Opus 4.7** — 6개 진단 종합 + LOCKED 24키 산출 |

---

## 세션 관리

Streamlit Cloud는 재배포 시 세션이 휘발된다. 각 Stage 완료 후 **진행 백업 JSON**을 다운로드해 두면 STEP 1에서 복원할 수 있다.

| 파일 종류 | 스키마 | 업로드 위치 |
|---|---|---|
| 진행 백업 | `triage_progress_v1` | Idea Engine STEP 1 |
| LOCKED 시드 | `_idea_engine_meta` 포함 | Creator Engine STEP 1 |

두 파일은 이름과 버튼 라벨이 분리되어 있다. 혼동이 실제 거부 오류를 일으킨 이력이 있다 (v1.6.1).

---

## 검증된 작품

| 작품 | 분류 | Hook | 결과 |
|---|---|---|---|
| 「오랜만에」 | MELO · 단일 영화 | 40/50 | CONDITIONAL |
| 「클레어의 서울 수비니어샵」 | SOCIAL + FANTASY · 시리즈 | 35/50 | CONDITIONAL → Creator Engine 풀 파이프라인 통과 (47 LOCKED) |
| 「상속」 (w.t.) | CRIME · 사회파 스릴러 | 진행 중 | STEP 1 진행 백업 생성. 법률·타이밍 정합 확인 중 |
| 「만물탐정」 | — | 34/50 | v1.0 검증분 |

---

## 다음 사이클 — v2.4 예정

**Reality Pre-Check (제도 사실성 사전 점검)**

Creator Engine v2.7.0이 신설한 Reality Gate가 상류 LOCKED에서 사실 오류를 적출하고 있다. 「연애의 끝」에서는 혼인서약서의 법적 효력에 관한 잘못된 전제가 LOCKED 42개 중 4곳에 박혀 하류 전 단계를 오염시켰다. **하류가 걸러내는 것보다 상류가 내보내지 않는 편이 싸다.**

| 항목 | 계획 |
|---|---|
| 신규 파일 | `institutional_reality_pack.py` (약 750행) — Creator `profession_pack.py`에서 `INSTITUTIONAL_REALITY`(20직군 9,929자) · `PROFESSION_KEYWORDS`(376키워드) · `detect_profession_category()`만 추림 |
| 신규 프롬프트 | `SYSTEM_REALITY_PRECHECK` — Creator `SYSTEM_REALITY_GATE`에서 Core Build 참조부만 교체. 적출 대상 5종 · 금지 5항 · severity 3단 · 오탐 회피 원칙은 문면 그대로 유지 |
| 배치 | Stage 6 ↔ Stage 7 사이 (LOCKED 확정 직전). 3-C+ 와 동일한 선택 게이트 구조로 하류 스키마 동일 보장 |
| 시드 반영 | `_idea_engine_meta.reality_precheck` 실값 기입 |

양측 판정 기준이 어긋나면 "Reality Gate CRITICAL 적출 0건" 목표 자체가 측정 불가능해지므로, 프롬프트 문면을 그대로 이식하는 것이 전제다.

착수 시점은 v2.3 적용분이 신규 프로젝트 2~3건으로 검증된 이후.

---

## 디자인 시스템

| 요소 | 값 |
|---|---|
| Primary | `#FFCB05` (BLUE JEANS Yellow) |
| Background | `#F7F7F5` |
| Text | `#1A1A2E` |
| Navy | `#191970` |
| Display Font | Playfair Display |
| Body Font | Pretendard / Noto Sans KR |

Writer Engine v3.1 디자인 시스템과 동일.

---

## 설치 및 실행

```bash
streamlit run main.py
```

Streamlit Cloud Secrets에 `ANTHROPIC_API_KEY` 필수. GitHub 푸시 시 1~2분 내 자동 재배포된다.

---

## 사용 케이스

**Case 1 — 본인 아이디어 스크리닝**
머릿속 아이디어 → TRIAGE → 35점 이상만 Creator Engine으로.

**Case 2 — 외부 작가 입구 게이트**
신인 작가 아이디어 → 5분 진단 → "받을 만한 소재인가" 판정.

**Case 3 — 발굴부터 시작**
머릿속에 아무것도 없을 때 → HUNTER 5개 입구 → 시드 발굴 → TRIAGE 인계.

**Case 4 — 이미 확정된 IP**
「물귀신」 「왕게임」처럼 LOCKED가 이미 확정된 IP는 Idea Engine을 거치지 않고 Creator Engine에 직접 입력한다.

---

## 버전 이력

| 버전 | 날짜 | 변경 사항 |
|---|---|---|
| v2.3 | 2026-08-03 | 포맷 구조화 단일화 · 미지정 경로 · 인계 메타데이터 · `meta.patch` 하드코딩 버그 수정 |
| v2.2 | 2026-08-03 | 로그라인 포맷 어휘 차단 · 직업 역할 확인 지침 |
| v2.1 | 2026-07 | 3-C+ Hook 약점 보완 게이트 (객관식 · 선택 진입) |
| v1.6.1 | 2026-06 | 진행 백업 / 시드 JSON 파일명·라벨 분리 |
| v1.6 | 2026-06 | Story Core 5원칙 진단 (3-A) |
| v1.5 | 2026-06 | 3-A+ 5원칙 보강 발굴 |
| v1.4.1 | 2026-06 | Market Lens Pack (KR · JP · ID) |
| v1.3 | 2026-05 | 장르 10분류 + 시장 좌표 (LOCKED 24) |
| v1.2 | 2026-05 | Story Core + Hook & Punch (LOCKED 22) |
| v1.1 | 2026-05-05 | Creator Engine v2.5.2 정합 5키 (LOCKED 18) |
| v2.0 | 2026-05-05 | HUNTER 트랙 |
| v1.0 | 2026-04-25 | TRIAGE 7단계 완성 |

---

## 라이선스

© 2026 BLUE JEANS PICTURES · Internal Use Only
