# 🔧 Creator Engine v1.2 패치 가이드 — Idea Engine 연동

> Creator Engine ① 아이디어 입력 화면에 **"Idea Engine JSON 업로드"** 버튼을 추가하는 가이드입니다.
> 이 패치는 기존 사용 흐름을 100% 보존합니다 — JSON 업로드는 **선택사항**이며, 미사용 시 기존과 동일하게 작동합니다.

---

## 패치 요약

Creator Engine ① 화면 최상단에 다음 UI 요소를 추가합니다:

```
┌─────────────────────────────────────────────────┐
│  🔑 Idea Engine 시드 업로드 (선택)               │
│  [파일 선택]  ✓ 업로드 시 아래 필드 자동 채움      │
└─────────────────────────────────────────────────┘
              ↓ (기존 입력 폼)
┌─────────────────────────────────────────────────┐
│  제목: [____________]                            │
│  아이디어: [____________]                        │
│  장르: [선택]                                    │
│  타겟 시장: [선택]                               │
│  포맷: [선택]                                    │
└─────────────────────────────────────────────────┘
```

---

## 수정 위치

`main.py`에서 **Stage 1 (아이디어 입력) 페이지 함수** 위쪽에 추가합니다.

함수명은 Creator Engine v1.2 기준 `page_stage_1_idea()` 또는 유사한 이름일 것입니다.

---

## 수정 코드 (Drop-in Patch)

### 1) Import 추가 (파일 상단)

```python
import json
```
(이미 있으면 생략)

### 2) Idea Engine 시드 로더 함수 추가 (utility 영역)

```python
def load_idea_seed(uploaded_file) -> dict:
    """Idea Engine JSON 시드를 파싱하여 Creator Engine 입력 형식으로 변환"""
    try:
        data = json.load(uploaded_file)
        
        # Idea Engine 메타 검증
        if "_idea_engine_meta" not in data:
            return {"_error": "올바른 Idea Engine JSON이 아닙니다."}
        
        return {
            "title": data.get("title", ""),
            "raw_idea": data.get("raw_idea", ""),
            "genre": data.get("genre", ""),
            "target_market": data.get("target_market", ""),
            "format": data.get("format", ""),
            "_locked_seed": data.get("locked_seed", {}),
            "_executive_summary": data.get("executive_summary", ""),
            "_pending_decisions": data.get("pending_decisions", []),
            "_meta": data["_idea_engine_meta"],
        }
    except Exception as e:
        return {"_error": f"파일 파싱 실패: {str(e)}"}
```

### 3) Stage 1 페이지 함수 시작 부분에 추가

기존 Stage 1 페이지 함수의 **`with st.form(...)` 블록 직전에** 다음 코드를 삽입합니다:

```python
def page_stage_1_idea():
    section_header("① 아이디어 입력", "INPUT")
    
    # ───────────────────────────────────────────────────────
    # ★ NEW: Idea Engine 시드 업로드 (선택)
    # ───────────────────────────────────────────────────────
    with st.expander("🔑 Idea Engine 시드 JSON 업로드 (선택)", expanded=False):
        st.caption(
            "Idea Engine에서 생성한 LOCKED 시드 JSON을 업로드하면 "
            "아래 입력 필드가 자동으로 채워집니다."
        )
        
        uploaded = st.file_uploader(
            "Idea Engine JSON 파일",
            type=["json"],
            key="idea_engine_seed_upload",
            label_visibility="collapsed",
        )
        
        if uploaded is not None:
            seed = load_idea_seed(uploaded)
            
            if seed.get("_error"):
                st.error(seed["_error"])
            else:
                # 세션에 저장
                st.session_state["idea_seed_loaded"] = seed
                
                meta = seed.get("_meta", {})
                st.success(
                    f"✓ Idea Engine 시드 로드 완료 — "
                    f"Project: {meta.get('project_id', '')} · "
                    f"Verdict: {meta.get('verdict', '')} · "
                    f"Hook Score: {meta.get('hook_score', 0)}/50"
                )
                
                # 임원 요약 표시
                if seed.get("_executive_summary"):
                    st.info(f"**Executive Summary**\n\n{seed['_executive_summary']}")
                
                # Creator Engine에서 결정할 펜딩 질문 표시
                if seed.get("_pending_decisions"):
                    st.markdown("**Creator Engine에서 결정할 사항**")
                    for q in seed["_pending_decisions"]:
                        st.markdown(f"- {q}")
    
    # ───────────────────────────────────────────────────────
    # 기존 입력 폼 (시드가 로드되어 있으면 자동 채움)
    # ───────────────────────────────────────────────────────
    seed_loaded = st.session_state.get("idea_seed_loaded", {})
    
    with st.form("stage_1_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            title = st.text_input(
                "제목",
                value=seed_loaded.get("title", ""),
                placeholder="작품 제목 (가제)"
            )
        with col2:
            genre_default = seed_loaded.get("genre", "미지정")
            # ... (기존 장르 선택 로직)
        
        raw_idea = st.text_area(
            "아이디어",
            value=seed_loaded.get("raw_idea", ""),
            height=200,
        )
        
        # ... (이하 기존 코드 동일)
        
        submitted = st.form_submit_button("Brainstorm으로 →")
        
        if submitted:
            st.session_state["stage_1_input"] = {
                "title": title.strip(),
                "genre": genre,
                "target_market": target_market,
                "format": format_pref,
                "raw_idea": raw_idea.strip(),
            }
            
            # ★ NEW: LOCKED 시드를 별도로 보존
            if seed_loaded:
                st.session_state["locked_seed"] = seed_loaded.get("_locked_seed", {})
            
            st.session_state["current_stage"] = 2
            st.rerun()
```

---

## LOCKED 시드 활용 (Stage ②~⑦)

후속 Stage에서 LOCKED 항목을 변경하지 않도록 활용합니다.

### Stage ② Brainstorm

```python
locked_seed = st.session_state.get("locked_seed", {})

if locked_seed:
    # Brainstorm 프롬프트에 LOCKED 컨텍스트 주입
    locked_context = f"""
[LOCKED CONTEXT - 아래 항목은 변경하지 말 것]
- Logline: {locked_seed.get('locked_logline', '')}
- Genre: {locked_seed.get('locked_genre', {}).get('primary', '')}
- Format: {locked_seed.get('locked_format', {}).get('primary', '')}
- Target: {locked_seed.get('locked_target', {}).get('domestic', '')}
- Theme: {locked_seed.get('locked_theme', {}).get('surface', '')}

위 LOCKED 항목들은 이미 Idea Engine에서 확정되었다.
컨셉 카드 10개를 생성할 때 이 LOCKED 항목들을 존중한다.
"""
else:
    locked_context = ""

# 기존 Brainstorm 프롬프트에 locked_context를 prepend
brainstorm_prompt = locked_context + EXISTING_BRAINSTORM_PROMPT
```

### Stage ③ Core Build

LOCKED 로그라인이 있는 경우, Logline Pack 5종 중 "Original"을 LOCKED 로그라인으로 강제 설정:

```python
locked_seed = st.session_state.get("locked_seed", {})

if locked_seed.get("locked_logline"):
    # Original logline을 LOCKED로 고정
    core_prompt += f"\n\n[LOCKED LOGLINE - Original 항목은 이 문장으로 고정]\n"
    core_prompt += locked_seed["locked_logline"]
```

### Stage ⑦ Treatment

LOCKED 위험 요소를 Treatment 작성 시 반영:

```python
locked_seed = st.session_state.get("locked_seed", {})
risks = locked_seed.get("locked_risks_to_address", [])

if risks:
    treatment_prompt += f"""

[REQUIRED: 다음 위험 요소를 Treatment에서 다룰 것]
"""
    for r in risks:
        treatment_prompt += f"- {r}\n"
```

---

## 사이드바 표시 (선택)

LOCKED 시드가 로드되어 있으면 사이드바에 표시:

```python
with st.sidebar:
    locked_seed = st.session_state.get("locked_seed", {})
    if locked_seed:
        st.markdown("### 🔑 Idea Engine 시드")
        st.caption(f"Project: {locked_seed.get('project_id', '')}")
        st.caption(f"Hook: {locked_seed.get('locked_hook_score', 0)}/50")
        ms = locked_seed.get("locked_market_stars", {})
        st.caption(f"Market: 🇰🇷{'★' * ms.get('domestic', 0)} 🌏{'★' * ms.get('global', 0)} 📺{'★' * ms.get('ott', 0)}")
        
        if st.button("시드 제거"):
            del st.session_state["locked_seed"]
            del st.session_state["idea_seed_loaded"]
            st.rerun()
```

---

## DOCX 보고서 헤더에 시드 정보 추가 (선택)

기획개발보고서 DOCX 첫 페이지에 Idea Engine 시드 출처 표시:

```python
locked_seed = st.session_state.get("locked_seed", {})
if locked_seed:
    seed_p = doc.add_paragraph()
    seed_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = seed_p.add_run(
        f"※ Idea Engine 진단 통과 — Hook {locked_seed.get('locked_hook_score', 0)}/50"
    )
    run.font.size = Pt(9)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
```

---

## 호환성

이 패치는 **하위 호환**됩니다:

| 시나리오 | 동작 |
|---------|------|
| Idea Engine JSON 업로드 안 함 | 기존과 100% 동일하게 작동 |
| Idea Engine JSON 업로드 함 | 입력 필드 자동 채움 + LOCKED 컨텍스트 주입 |
| 잘못된 JSON 파일 업로드 | 에러 메시지 표시 후 기존 폼 유지 |

---

## 테스트 시나리오

1. **Idea Engine 미사용**: Creator Engine을 평소처럼 사용 → 정상 작동 확인
2. **Idea Engine 시드 사용**: Idea Engine에서 〈만물트럭 탐정〉 진단 → JSON 다운로드 → Creator Engine ① 업로드 → 자동 채움 확인 → ② Brainstorm 실행 → LOCKED 항목 유지되는지 확인

---

© 2026 BLUE JEANS PICTURES · Idea Engine v1.0 / Creator Engine v1.2 Integration Guide
