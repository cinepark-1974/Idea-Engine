"""
👖 BLUE JEANS Creator Engine — Main Application

버전 정보는 prompt.py의 ENGINE_VERSION / ENGINE_BUILD_DATE를 참조한다.
(단일 소스 원칙 — 버전은 한 곳에서만 관리)

아이디어 → 기획개발 패키지
단일 페이지 · 사이드바 최소 · 2단계 Brainstorm
"""

import streamlit as st
import json
import re
from datetime import datetime
import prompt as P

# ─── 버전 정보 (prompt.py에서 단일 소스로 참조) ───
ENGINE_VERSION = P.ENGINE_VERSION
ENGINE_BUILD_DATE = P.ENGINE_BUILD_DATE
ENGINE_FOOTER = f"© 2026 BLUE JEANS PICTURES · Creator Engine {ENGINE_VERSION}"

ANTHROPIC_MODEL = "claude-sonnet-4-6"           # 구조 작업 — 비용 효율
ANTHROPIC_MODEL_OPUS = "claude-opus-4-6"        # 캐릭터 바이블 · 트리트먼트 · 톤 문서 — 최고 품질


# ─── v2.4.0: 시대극 자동 감지 컨텍스트 추출 ─────────────────────────
def _get_period_scan_context(project: dict = None) -> tuple:
    """현재 세션 상태와 프로젝트 데이터에서 시대 감지용 텍스트를 추출.
    
    Idea Engine v1.0 시드(st.session_state["locked_seed"])가 있으면 활용.
    - locked_logline, locked_references, locked_genre, locked_theme 등이
      시대(SAGEUK/COLONIAL/MODERN_HIST) 자동 감지의 결정적 시그널이 됨.
    
    Returns:
        (locked_text, idea_text) 튜플.
        둘 다 빈 문자열이면 시대 OVERRIDE·Period Pack 자동 감지가 작동하지 않으며
        v2.3.10과 동일하게 동작 (하위 호환).
    """
    try:
        locked_seed = st.session_state.get("locked_seed", {}) or {}
    except Exception:
        locked_seed = {}
    return P.build_scan_text_for_period_detection(
        project=project or {},
        locked_seed=locked_seed,
    )

# ─── Page Config ───
st.set_page_config(
    page_title="BLUE JEANS · Creator Engine",
    page_icon="👖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Sidebar: Engine Info (버전 확인용) ───
with st.sidebar:
    st.markdown(f"""
    <div style="padding:12px;background:#F0F2FF;border-radius:8px;border-left:3px solid #191970;font-family:'Pretendard',sans-serif;">
        <div style="font-size:.72rem;color:#191970;font-weight:700;letter-spacing:.05em;margin-bottom:4px;">ENGINE INFO</div>
        <div style="font-size:1.05rem;font-weight:700;color:#191970;">Creator Engine</div>
        <div style="font-size:1.25rem;font-weight:900;color:#FFCB05;background:#191970;padding:2px 8px;border-radius:4px;display:inline-block;margin-top:4px;">
            {ENGINE_VERSION}
        </div>
        <div style="font-size:.7rem;color:#666;margin-top:8px;">
            Build: {ENGINE_BUILD_DATE}<br>
            Status: {P.ENGINE_STATUS}
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("버전이 최신인지 확인하세요.")

    # ─── v2.4.2: 리서치 기준일 표시 (한국 시간) ───
    try:
        from zoneinfo import ZoneInfo
        _today = datetime.now(ZoneInfo("Asia/Seoul"))
    except Exception:
        _today = datetime.now()
    st.caption(f"📅 리서치 기준일: {_today.strftime('%Y-%m-%d')}")

    # ─── v2.4.2: 마지막 리서치 사용량 표시 ───
    _usage = st.session_state.get("last_research_usage")
    if _usage:
        st.markdown(f"""
        <div style="padding:10px;background:#FFFEF0;border-radius:6px;border-left:3px solid #FFCB05;font-family:'Pretendard',sans-serif;margin-top:8px;">
            <div style="font-size:.7rem;color:#191970;font-weight:700;letter-spacing:.05em;margin-bottom:4px;">🔍 마지막 리서치</div>
            <div style="font-size:.72rem;color:#444;line-height:1.5;">
                검색 <b>{_usage['search_count']}회</b><br>
                입력 {_usage['input_tokens']:,} 토큰<br>
                출력 {_usage['output_tokens']:,} 토큰<br>
                <span style="color:#191970;font-weight:700;">약 ${_usage['est_cost_usd']:.3f}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── Custom CSS ───
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@latest/Paperlogy.css');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

:root {
    --navy: #191970;
    --y: #FFCB05;
    --bg: #F7F7F5;
    --card: #FFFFFF;
    --card-border: #E2E2E0;
    --t: #1A1A2E;
    --r: #D32F2F;
    --g: #2EC484;
    --dim: #8E8E99;
    --light-bg: #EEEEF6;
    --serif: 'Paperlogy', 'Noto Serif KR', 'Georgia', serif;
    --display: 'Playfair Display', 'Paperlogy', 'Georgia', serif;
    --body: 'Pretendard', -apple-system, sans-serif;
    --heading: 'Paperlogy', 'Pretendard', sans-serif;
}

/* ── 기본 타이포 ── */
html, body, [class*="css"] {
    font-family: var(--body);
    color: var(--t);
    -webkit-font-smoothing: antialiased;
}

/* ══ 라이트모드 강제 (전역) ══ */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], [data-testid="stHeader"],
[data-testid="stBottom"] {
    background-color: var(--bg) !important;
    color: var(--t) !important;
}
.stMarkdown, .stText, .stCode {
    color: var(--t) !important;
}
h1, h2, h3, h4, h5, h6 { color: var(--navy) !important; font-family: var(--heading) !important; }
p, span, label, div, li { color: inherit; }

/* ── 사이드바 숨김 ── */
section[data-testid="stSidebar"] { display: none; }

/* ══ 입력 위젯 라이트 ══ */
.stTextInput input, .stTextArea textarea,
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background-color: var(--card) !important;
    color: var(--t) !important;
    border: 1.5px solid var(--card-border) !important;
    border-radius: 8px !important;
    font-family: var(--body) !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 0.8rem !important;
    transition: border-color 0.2s;
}
.stTextInput input:focus, .stTextArea textarea:focus,
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 2px rgba(25,25,112,0.08) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder,
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {
    color: var(--dim) !important;
    font-size: 0.85rem !important;
}
/* selectbox */
.stSelectbox > div > div, [data-baseweb="select"] > div, [data-baseweb="select"] input {
    background-color: var(--card) !important;
    color: var(--t) !important;
    border-color: var(--card-border) !important;
    border-radius: 8px !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"], [role="option"] {
    background-color: var(--card) !important;
    color: var(--t) !important;
}
[role="option"]:hover { background-color: var(--light-bg) !important; }
/* label */
.stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label {
    color: var(--t) !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
    margin-bottom: 0.3rem !important;
}

/* ══ 버튼 ══ */
.stButton > button {
    color: var(--t) !important;
    border: 1.5px solid var(--card-border) !important;
    background-color: var(--card) !important;
    border-radius: 8px !important;
    font-family: var(--body) !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: var(--navy) !important;
    box-shadow: 0 2px 8px rgba(25,25,112,0.08) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: var(--y) !important;
    color: var(--navy) !important;
    border-color: var(--y) !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background-color: #E8B800 !important;
    box-shadow: 0 2px 12px rgba(255,203,5,0.3) !important;
}

/* ══ Expander ══ */
.stExpander, details, details summary {
    background-color: var(--card) !important;
    color: var(--t) !important;
    border: 1px solid var(--card-border) !important;
    border-radius: 8px !important;
}
details[open] > div { background-color: var(--card) !important; }
.stExpander summary, .stExpander summary span { color: var(--t) !important; }

/* ══ Alert 박스 ══ */
.stAlert { color: var(--t) !important; border-radius: 8px !important; }

/* ══ 내부 컨테이너 투명 ══ */
[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
[data-testid="stColumn"] { background-color: transparent !important; }

/* ══ Metric ══ */
[data-testid="stMetric"] { background-color: var(--card) !important; color: var(--t) !important; }
[data-testid="stMetric"] label { color: var(--dim) !important; }
.stCaption, small { color: var(--dim) !important; }
.stCheckbox label span, .stToggle label span { color: var(--t) !important; }

/* ══ 배경색별 텍스트 강제 ══ */
[style*="background:#FFCB05"] { color: var(--navy) !important; }
[style*="background:#FFCB05"] * { color: var(--navy) !important; }
[style*="background:#2EC484"] { color: #FFFFFF !important; }
[style*="background:#2EC484"] * { color: #FFFFFF !important; }

/* ═══════════════════════════════════
   브랜딩 & 커스텀 컴포넌트
   ═══════════════════════════════════ */

.header {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--navy);
    letter-spacing: 0.2em;
    margin-top: 0.5rem;
    margin-bottom: 0.3rem;
    font-family: var(--heading);
}

.brand-title {
    font-size: 2.6rem;
    font-weight: 900;
    color: var(--navy);
    font-family: var(--display);
    letter-spacing: -0.02em;
    margin-bottom: 0.15rem;
    position: relative;
    display: inline-block;
}
.brand-title::after {
    content: '';
    position: absolute;
    bottom: 2px;
    left: 0;
    width: 100%;
    height: 4px;
    background: var(--y);
    border-radius: 2px;
}

.sub {
    font-size: 0.7rem;
    color: var(--dim);
    letter-spacing: 0.15em;
    margin-top: 0.5rem;
    margin-bottom: 1.5rem;
}

/* ── 카드 ── */
.card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.03);
    transition: all 0.2s;
}
.card:hover {
    border-color: var(--navy);
    box-shadow: 0 3px 12px rgba(25,25,112,0.07);
    transform: translateY(-1px);
}

/* ── 콜아웃 ── */
.callout {
    background: var(--light-bg);
    border-left: 4px solid var(--navy);
    padding: 0.9rem 1.1rem;
    margin: 0.5rem 0;
    border-radius: 0 8px 8px 0;
    font-size: 0.88rem;
    color: var(--t);
}

/* ── 섹션 라벨 ── */
.cl {
    color: var(--navy);
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 0.03em;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
}

/* ── 정보 블록 ── */
.ri {
    background: var(--light-bg);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    line-height: 1.6;
}
.rl {
    color: var(--navy);
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 0.02em;
}

/* ── 큰 숫자 ── */
.big {
    font-size: 2.8rem;
    font-weight: 900;
    color: var(--navy);
    text-align: center;
    font-family: var(--heading);
}
.sm {
    font-size: 0.7rem;
    color: var(--dim);
    text-align: center;
}

/* ── 뱃지 ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 5px;
    font-size: 0.7rem;
    font-weight: 600;
}
.b-done { background: var(--g); color: #fff; }
.b-run  { background: var(--y); color: var(--navy); }
.b-not  { background: #E8E8F0; color: var(--dim); }
.b-fail { background: var(--r); color: #fff; }

/* ── 노란 섹션 헤더 (웹 UI) ── */
.section-header {
    background: var(--y);
    color: var(--navy);
    padding: 0.6rem 1rem;
    border-radius: 6px;
    font-weight: 800;
    font-size: 1rem;
    font-family: var(--heading);
    margin: 1.5rem 0 0.8rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.section-header .en {
    font-family: var(--display);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    opacity: 0.7;
}

/* ══ Stepper ══ */
.stepper {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 1.5rem 0 2rem 0;
    gap: 0;
}
.step-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.step-circle {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.78rem;
    font-weight: 700;
    flex-shrink: 0;
    border: 2px solid transparent;
    transition: all 0.2s;
}
.step-circle.active {
    background: var(--y);
    color: var(--navy);
    border-color: var(--y);
    box-shadow: 0 0 0 4px rgba(255,203,5,0.2);
}
.step-circle.done {
    background: var(--g);
    color: #fff;
    border-color: var(--g);
}
.step-circle.upcoming {
    background: #EDEDF0;
    color: var(--dim);
    border-color: #D8D8E0;
}
.step-label {
    font-size: 0.6rem;
    margin-top: 0.35rem;
    text-align: center;
    width: 55px;
    font-weight: 500;
}
.step-label.active { color: var(--navy); font-weight: 700; }
.step-label.done { color: var(--g); font-weight: 600; }
.step-label.upcoming { color: var(--dim); }
.step-line {
    width: 30px;
    height: 2px;
    margin: 0 2px;
    flex-shrink: 0;
    border-radius: 1px;
}
.step-line.done { background: var(--g); }
.step-line.upcoming { background: #D8D8E0; }

/* ══ 프로그레스 바 (공통) ══ */
.progress-track {
    flex: 1;
    background: #E8E8F0;
    border-radius: 4px;
    height: 8px;
    margin: 0 0.5rem;
}
.progress-fill {
    height: 100%;
    background: var(--y);
    border-radius: 4px;
    transition: width 0.3s;
}
</style>
""", unsafe_allow_html=True)


# ─── Session State ───
defaults = {
    "view": "home",         # home | project | core | char_bible | structure | scene_design | treatment | tone_doc | export
    "projects": {},
    "cur": None,
    "last_research_raw": "",
    "last_research_usage": None,  # v2.4.2: 검색 횟수 + 토큰 + 비용 추정
    "last_cards_raw": "",
    "last_analysis_raw": "",
    "last_core_raw": "",
    "last_gate_raw": "",
    "last_char_bible_raw": "",
    "last_structure_story_raw": "",
    "last_structure_diag_raw": "",
    "last_structure_gate_raw": "",
    "last_scene_design_raw": "",
    "last_treatment_act1_raw": "",
    "last_treatment_act2_raw": "",
    "last_treatment_act3_raw": "",
    "last_tone_doc_raw": "",
    "last_error": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Stepper (9단계) ───
STEPS = [
    ("project", "아이디어"),
    ("project", "Brainstorm"),
    ("core", "Core"),
    ("char_bible", "Bible"),
    ("structure", "Structure"),
    ("scene_design", "Scene"),
    ("treatment", "Treatment"),
    ("tone_doc", "Tone"),
    ("export", "Export"),
]

def render_stepper(current_view, project_data=None):
    """상단 단계 네비게이션 바 — 완료된 단계는 클릭 이동 가능 (v2.3.4)"""
    view_to_step = {
        "project": 1 if project_data and project_data.get("brainstorm_cards") else 0,
        "core": 2,
        "char_bible": 3,
        "structure": 4,
        "scene_design": 5,
        "treatment": 6,
        "tone_doc": 7,
        "export": 8,
    }
    current_idx = view_to_step.get(current_view, 0)

    done_idx = -1
    if project_data:
        if project_data.get("brainstorm_cards"):
            done_idx = 1
        if project_data.get("brainstorm_analysis"):
            ga = project_data["brainstorm_analysis"].get("gate_a_scores", {})
            if ga.get("average", 0) >= 7.0:
                done_idx = 1
        if project_data.get("core"):
            done_idx = 2
        if project_data.get("char_bible"):
            done_idx = 3
        if project_data.get("structure_story"):
            done_idx = 4
        if project_data.get("scene_design"):
            done_idx = 5
        if project_data.get("treatment"):
            done_idx = 6
        if project_data.get("tone_doc"):
            done_idx = 7

    # 인라인 CSS — 버튼을 stepper 형태로 보이게
    st.markdown("""
    <style>
    .stepper-nav [data-testid="column"] {
        padding: 0 !important;
    }
    .stepper-nav .stButton button {
        width: 100%;
        min-height: 3.4rem;
        padding: 0.4rem 0.2rem;
        font-size: 0.72rem;
        font-weight: 600;
        line-height: 1.15;
        border-radius: 8px;
        white-space: normal;
        word-break: keep-all;
    }
    .step-done button {
        background: #191970 !important;
        color: #FFCB05 !important;
        border: 1px solid #191970 !important;
    }
    .step-done button:hover {
        background: #FFCB05 !important;
        color: #191970 !important;
        border-color: #FFCB05 !important;
    }
    .step-active button {
        background: #FFCB05 !important;
        color: #191970 !important;
        border: 2px solid #191970 !important;
        cursor: default !important;
    }
    .step-upcoming button {
        background: #F7F7F5 !important;
        color: #B0B0B0 !important;
        border: 1px dashed #D0D0D0 !important;
        cursor: not-allowed !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # 단계 버튼을 가로로 배치
    st.markdown('<div class="stepper-nav">', unsafe_allow_html=True)
    cols = st.columns(len(STEPS))

    for i, (view_key, label) in enumerate(STEPS):
        # 상태 결정
        if i < current_idx and i <= done_idx:
            state = "done"
        elif i == current_idx:
            state = "active"
        else:
            state = "upcoming"

        icon = "✓" if state == "done" else ("●" if state == "active" else str(i + 1))
        btn_label = f"{icon}\n{label}"

        with cols[i]:
            # 상태별 컨테이너 스타일 적용
            st.markdown(f'<div class="step-{state}">', unsafe_allow_html=True)

            if state == "done":
                # 완료된 단계: 클릭 시 해당 view로 점프
                if st.button(btn_label, key=f"stepper_nav_{view_key}_{i}", use_container_width=True):
                    st.session_state.view = view_key
                    st.rerun()
            elif state == "active":
                # 현재 위치: 버튼 형태로 표시되지만 클릭해도 의미 없음 (disabled)
                st.button(btn_label, key=f"stepper_nav_{view_key}_{i}", use_container_width=True, disabled=True)
            else:
                # 미완료: 비활성
                st.button(btn_label, key=f"stepper_nav_{view_key}_{i}", use_container_width=True, disabled=True)

            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ─── JSON Helpers ───
# ═══════════════════════════════════════════════════
# Project JSON Save/Load (v2.3.5 신규)
# 목적: 세션 끊김 대비한 프로젝트 상태 복구용
# 원칙: 전체 저장 / 전체 복원 — 부분 저장 금지
# ═══════════════════════════════════════════════════

def _get_project_stage(project: dict) -> str:
    """프로젝트의 현재 완료 단계 파악 — 파일명 생성용"""
    if project.get("tone_doc"):
        return "Tone완료"
    if project.get("treatment"):
        return "Treatment완료"
    if project.get("treatment_partial"):
        return "Treatment진행중"
    if project.get("scene_design"):
        return "Scene완료"
    if project.get("structure_story"):
        return "Structure완료"
    if project.get("char_bible"):
        return "Character완료"
    if project.get("core"):
        return "Core완료"
    if project.get("brainstorm_cards"):
        return "Brainstorm완료"
    return "초기"


def save_project_to_json(project: dict, engine_version: str = "v2.7.2") -> str:
    """프로젝트 전체를 JSON 문자열로 직렬화.
    
    Args:
        project: Streamlit session_state의 project dict
        engine_version: 현재 엔진 버전 (호환성 검증용)
    
    Returns:
        UTF-8 JSON 문자열
    """
    # 저장 가능한 형태로 복사
    payload = {
        "_meta": {
            "blue_jeans_engine": "Creator Engine",
            "engine_version": engine_version,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stage": _get_project_stage(project),
        },
        "project": project,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def load_project_from_json(json_str: str) -> dict:
    """JSON 문자열에서 프로젝트 복원.
    
    Args:
        json_str: save_project_to_json 으로 저장된 JSON 문자열
    
    Returns:
        {"project": {...}, "meta": {...}, "warnings": [...]} 
    
    Raises:
        ValueError: 형식이 올바르지 않을 때
    """
    try:
        payload = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"유효한 JSON 파일이 아닙니다: {e}")
    
    # 구조 검증
    if not isinstance(payload, dict):
        raise ValueError("JSON 최상위가 객체가 아닙니다.")
    if "project" not in payload:
        raise ValueError("project 필드가 없습니다. Creator Engine 프로젝트 파일이 맞는지 확인하세요.")
    
    project = payload["project"]
    meta = payload.get("_meta", {})
    warnings = []
    
    # 필수 필드 검증
    required_fields = ["project_id", "title", "idea_text", "genre", "format"]
    missing = [f for f in required_fields if f not in project]
    if missing:
        raise ValueError(f"필수 필드 누락: {', '.join(missing)}")
    
    # 엔진 버전 호환성 체크 (경고만, 실패 아님)
    saved_version = meta.get("engine_version", "unknown")
    current_version = "v2.7.2"
    if saved_version != current_version:
        warnings.append(
            f"엔진 버전 차이 — 저장 시: {saved_version} / 현재: {current_version}. "
            f"대부분 호환되지만, 이후 단계 실행 시 예상치 못한 동작이 있을 수 있습니다."
        )
    
    return {
        "project": project,
        "meta": meta,
        "warnings": warnings,
    }


def extract_json_object(text: str) -> str:
    """응답 텍스트에서 JSON 객체만 추출"""
    text = text.strip()

    # 코드블록 제거
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # 첫 { 부터 마지막 } 까지 추출
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("JSON 객체 시작/끝을 찾지 못했습니다.")

    return text[start:end + 1]


def safe_json_loads(text: str):
    """JSON 파싱 (강화된 복구 로직 — 5단계)"""
    cleaned = extract_json_object(text)
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)

    # 0단계: 문자열 값 내부의 raw 제어 문자 제거 (Invalid control character 방지)
    # JSON 문자열 안에 raw \n, \r, \t가 있으면 파싱 실패함
    def _sanitize_control_chars(s):
        """JSON 문자열 값 내부의 제어 문자를 공백으로 치환"""
        result = []
        in_string = False
        i = 0
        while i < len(s):
            c = s[i]
            if c == '"' and (i == 0 or s[i-1] != '\\'):
                in_string = not in_string
                result.append(c)
            elif in_string and c in '\n\r':
                result.append(' ')
            elif in_string and c == '\t':
                result.append(' ')
            elif in_string and ord(c) < 32 and c not in ('\n', '\r', '\t'):
                result.append(' ')  # 기타 제어 문자
            else:
                result.append(c)
            i += 1
        return ''.join(result)

    cleaned = _sanitize_control_chars(cleaned)

    # 1차: 그대로 파싱
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2차: 문자열 내부 줄바꿈 이스케이프 + 쌍따옴표 → 작은따옴표
    try:
        result = []
        i = 0
        n = len(cleaned)
        while i < n:
            ch = cleaned[i]
            if ch == '"':
                result.append(ch)
                i += 1
                str_chars = []
                while i < n:
                    c = cleaned[i]
                    if c == '\\' and i + 1 < n:
                        next_c = cleaned[i + 1]
                        if next_c == '"':
                            str_chars.append("'")
                            i += 2
                        elif next_c in ('n', 'r', 't', '\\', '/', 'b', 'f', 'u'):
                            str_chars.append(c)
                            str_chars.append(next_c)
                            i += 2
                        else:
                            str_chars.append(next_c)
                            i += 2
                    elif c == '"':
                        # 문자열 종료인지 판단 — 다음 비공백 문자 확인
                        rest = cleaned[i + 1:] if i + 1 < n else ""
                        rest_stripped = rest.lstrip()
                        if not rest_stripped:
                            break  # EOF
                        nc = rest_stripped[0]
                        if nc == ':':
                            break  # key-value 구분자 → 문자열 종료
                        elif nc == ',':
                            # 쉼표 뒤를 확인: " 또는 } 또는 ] → JSON 구조
                            after_comma = rest_stripped[1:].lstrip()
                            if not after_comma or after_comma[0] in '"{}[]0123456789tfn':
                                break  # 문자열 종료
                            else:
                                str_chars.append("'")
                                i += 1
                        elif nc in '}]':
                            break  # 객체/배열 종료
                        elif nc == '"':
                            # 다음이 곧바로 " → 이건 빈 문자열이 아니라 키 시작
                            break
                        else:
                            str_chars.append("'")
                            i += 1
                    elif c in '\n\r':
                        str_chars.append(' ')
                        i += 1
                    elif c == '\t':
                        str_chars.append(' ')
                        i += 1
                    else:
                        str_chars.append(c)
                        i += 1
                result.append(''.join(str_chars))
                result.append('"')
                i += 1
            else:
                result.append(ch)
                i += 1

        fixed = ''.join(result)
        fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
        return json.loads(fixed)
    except (json.JSONDecodeError, IndexError):
        pass

    # 3차: 에러 위치 기반 반복 수정 (최대 30회)
    current = cleaned
    for _ in range(30):
        try:
            return json.loads(current)
        except json.JSONDecodeError as e:
            pos = e.pos
            if pos is None or pos <= 0:
                break
            # 에러 위치 주변에서 문제가 되는 " 찾아서 ' 로 교체
            found = False
            for j in range(pos, max(0, pos - 100), -1):
                if j < len(current) and current[j] == '"':
                    before = current[j - 1] if j > 0 else ''
                    after_c = current[j + 1] if j + 1 < len(current) else ''
                    # 구조적 위치가 아닌 " → 내부 따옴표로 판단
                    if before not in ('{', '[', ',', ':', '\\') and after_c not in (':', ',', '}', ']'):
                        current = current[:j] + "'" + current[j + 1:]
                        found = True
                        break
                    elif before == '\\':
                        # \" → ' (이스케이프 제거)
                        current = current[:j - 1] + "'" + current[j + 1:]
                        found = True
                        break
            if not found:
                # 에러 위치 근처의 줄바꿈을 공백으로
                for j in range(max(0, pos - 5), min(len(current), pos + 5)):
                    if current[j] in '\n\r\t':
                        current = current[:j] + ' ' + current[j + 1:]
                        found = True
                        break
            if not found:
                break

    # 4차: 최후 수단 — 모든 문자열 값 내부 " → '
    try:
        aggressive = re.sub(
            r'(?<=: ")(.*?)(?="\s*[,}\]])',
            lambda m: m.group(0).replace('"', "'"),
            cleaned,
            flags=re.DOTALL
        )
        aggressive = re.sub(r",\s*([}\]])", r"\1", aggressive)
        return json.loads(aggressive)
    except json.JSONDecodeError as e:
        raise e


# ─── API Client ───
def get_client():
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic 패키지가 설치되지 않았습니다. requirements.txt를 확인하세요.")

    if "ANTHROPIC_API_KEY" not in st.secrets:
        raise RuntimeError("ANTHROPIC_API_KEY가 secrets에 설정되지 않았습니다.")

    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])


def _build_project_locked_block(project: dict) -> str:
    """프로젝트의 LOCKED 항목으로 프롬프트 주입 블록 생성.
    v2.3: OPEN 필드 폐지. LOCKED 항목이 없으면 빈 문자열 반환."""
    locked = project.get("locked_items", [])
    if not locked:
        return ""
    return P.build_locked_block(locked)


# ─── API Call: Research (v2.4.2: web_search 통합 + 최신 작품 우선 + 토큰 로깅) ───
def call_research(idea, genre, market):
    """
    v2.4.2 변경:
      - web_search 도구 활성화 (max_uses=3, 4개 도메인 화이트리스트)
      - SYSTEM_RESEARCH 함수형 호출로 동적 날짜 주입
      - existing_works 스키마에 platform 필드 추가
      - max_tokens 16000 → 8000 (토큰 절약)
      - 토큰 사용량 + 검색 횟수 세션 로깅 (사이드바 표시용)
    """
    try:
        client = get_client()

        # v2.4.2: 함수 호출로 변경 (동적 날짜 주입)
        system_prompt = P.get_system_research()

        user_prompt = f"""[입력]
아이디어: {idea}
장르: {genre}
타겟: {market}

[JSON 스키마]
{{
  "search_keywords": [],
  "real_events": [
    {{
      "id": 1,
      "title": "",
      "summary": "",
      "source": "",
      "year": "",
      "relevance": "",
      "story_potential": ""
    }}
  ],
  "existing_works": [
    {{
      "id": 1,
      "title": "",
      "type": "",
      "country": "",
      "year": "",
      "platform": "",
      "summary": "",
      "similarity": "",
      "difference_opportunity": ""
    }}
  ],
  "research_summary": {{
    "total_real_events": 0,
    "total_existing_works": 0,
    "key_insight": ""
  }}
}}

규칙:
- real_events 3~7개 (학습 데이터 우선, 검색은 최신 사건만)
- existing_works 3~7개 (검색 적극 활용 — 최신 영화·드라마 우선)
- existing_works의 70% 이상은 최근 3년 작품
- source는 가능한 한 짧게
- key_insight는 2문장 이내
- platform 필드 필수 (극장/Netflix/Wavve/Watcha/TVING/Disney+/IPTV/미상 중)
"""

        # v2.4.2: web_search 도구 추가 (max_uses=3, 5개 도메인 화이트리스트)
        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=8000,
            temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            tools=[{
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 3,
                "allowed_domains": [
                    "vkobis.or.kr",   # 영진위 온라인 통합전산망 (IPTV+OTT 박스오피스)
                    "kobis.or.kr",    # 영진위 영화 정보 DB
                    "cine21.co.kr",   # 씨네21 — 한국 영화 매체 (인터뷰·비평·라인업)
                    "cine21.com",     # 씨네21 — 같은 매체 다른 도메인
                    "imdb.com",       # 글로벌 영화·드라마 DB
                    "variety.com",    # 할리우드 산업·신작 보도
                    # v2.4.2.1: yna.co.kr 제거 — Anthropic crawler 차단 (invalid_request_error)
                ],
            }],
        )

        # v2.4.2: 토큰 사용량 + 검색 횟수 세션 로깅
        try:
            usage = getattr(response, 'usage', None)
            if usage:
                # 검색 횟수: server_tool_use.web_search_requests (모델 응답에 따라 키 다를 수 있음)
                search_count = 0
                stu = getattr(usage, 'server_tool_use', None)
                if stu:
                    search_count = getattr(stu, 'web_search_requests', 0) or 0

                input_tokens = getattr(usage, 'input_tokens', 0) or 0
                output_tokens = getattr(usage, 'output_tokens', 0) or 0

                # 비용 추정 (Sonnet 4.6 기준 입력 $3/M, 출력 $15/M, 검색 $0.01/회)
                est_cost = (
                    (input_tokens / 1_000_000) * 3.0
                    + (output_tokens / 1_000_000) * 15.0
                    + search_count * 0.01
                )

                st.session_state["last_research_usage"] = {
                    "search_count": search_count,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "est_cost_usd": round(est_cost, 4),
                }
        except Exception:
            # 사용량 로깅 실패는 본 기능에 영향 주지 않도록 무시
            pass

        # 텍스트 블록만 추출 (web_search tool_use/tool_result 블록은 자동 무시)
        txt = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()
        st.session_state["last_research_raw"] = txt

        return safe_json_loads(txt)

    except Exception as e:
        st.error(f"리서치 실패: {e}")
        raw = st.session_state.get("last_research_raw")
        if raw:
            with st.expander("🔧 Research Raw Response (디버그)"):
                st.text_area("Raw", raw, height=300)
        return None


# ─── API Call: Brainstorm Cards (1단계) ───
def call_brainstorm_cards(idea, genre, market, fmt, research=None, locked_block=""):
    """1단계: 아이디어 카드 10개 + Top 3 생성 (토큰 집중)"""
    try:
        client = get_client()

        system_prompt = P.SYSTEM_BRAINSTORM_CARDS

        research_block = ""
        if research:
            research_block = f"""
[리서치 참고]
{json.dumps(research, ensure_ascii=False)}

규칙:
- 실화/뉴스는 소재 참고용
- 기존작은 차별화 포인트 참고용
- 동일 구조/설정 반복 금지
"""

        user_prompt = f"""[입력]
아이디어: {idea}
장르: {genre}
타겟: {market}
포맷: {fmt}
{locked_block}
{research_block}

[JSON 스키마]
{{
  "idea_type": "story|mood|hybrid",
  "idea_type_diagnosis": "",
  "idea_type_action": "",
  "idea_cards": [
    {{
      "id": 1,
      "title": "10자 이내",
      "logline_seed": "",
      "protagonist": "",
      "conflict": "",
      "hook": "",
      "visual_image": "",
      "genre": "",
      "scores": {{
        "active_hero": 0.0,
        "conflict_clarity": 0.0,
        "visual_power": 0.0,
        "genre_immediacy": 0.0,
        "originality": 0.0,
        "market_fit": 0.0
      }},
      "total_score": 0.0
    }}
  ],
  "top3": [
    {{
      "rank": 1,
      "card_id": 0,
      "reason": ""
    }}
  ]
}}

규칙:
- idea_cards는 10개 (10개 초과 금지)
- top3는 3개
- total_score는 6개 점수 평균, 소수점 1자리
- scores 각 항목은 0.0~10.0
- idea_type_diagnosis: 이 아이디어의 현재 상태를 이 이야기에만 해당하는 구체적 언어로 1문장. "~이 필요하다" 같은 추상 진단 금지. 예: "주인공의 욕망은 선명하지만 적대자가 없어 갈등이 발생하지 않는다"
- idea_type_action: idea_type_diagnosis에 대한 즉각적 처방 1문장. 반드시 "~하라" 형태로. 예: "주인공이 원하는 것을 빼앗는 구체적 인물 또는 시스템을 설정하라"
- 각 카드의 logline_seed는 1문장, 50자 이내
- protagonist는 1문장, 30자 이내
- conflict는 1문장, 40자 이내
- hook는 1문장, 30자 이내
- visual_image는 1문장, 40자 이내
- reason은 1문장, 30자 이내
- 절대로 장문 서술하지 말 것. 짧고 강하게.
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=16000,
            temperature=0.35,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        # 토큰 한계 도달 감지
        if response.stop_reason == "max_tokens":
            st.warning("⚠️ 응답이 토큰 한계에서 잘렸습니다. 재시도합니다...")
            # 재시도: max_tokens 더 올리고 카드 수 줄이기
            retry_prompt = user_prompt.replace("idea_cards는 10개", "idea_cards는 7개")
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=16000,
                temperature=0.35,
                system=system_prompt,
                messages=[{"role": "user", "content": retry_prompt}]
            )

        txt = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()
        st.session_state["last_cards_raw"] = txt

        return safe_json_loads(txt)

    except Exception as e:
        st.session_state["last_error"] = str(e)
        st.error(f"카드 생성 실패: {e}")
        raw = st.session_state.get("last_cards_raw")
        if raw:
            with st.expander("🔧 Cards Raw Response (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── API Call: Brainstorm Analysis (2단계) ───
def call_brainstorm_analysis(idea, genre, market, fmt, top3_cards, research=None, locked_block=""):
    """2단계: Top 3 기반 시장분석 + 차별화 + Gate A 채점"""
    try:
        client = get_client()

        system_prompt = P.SYSTEM_BRAINSTORM_ANALYSIS

        research_block = ""
        if research:
            research_block = f"""
[리서치 참고]
{json.dumps(research, ensure_ascii=False)}
"""

        user_prompt = f"""[입력]
아이디어: {idea}
장르: {genre}
타겟: {market}
포맷: {fmt}
{locked_block}

[Top 3 컨셉 카드]
{json.dumps(top3_cards, ensure_ascii=False)}
{research_block}

[JSON 스키마]
{{
  "market_context": {{
    "target_market": "",
    "market_insight": "",
    "cultural_code": "",
    "market_risk": "",
    "reference_titles": []
  }},
  "format_context": {{
    "selected_format": "",
    "format_rationale": "",
    "structure_note": ""
  }},
  "research_applied": {{
    "real_events_used": [],
    "inspiration_note": ""
  }},
  "hook_sentence": "",
  "differentiation": ["", "", ""],
  "development_priority": {{
    "recommended_direction": "",
    "next_step": "",
    "risk": ""
  }},
  "format_fit": {{
    "current_format": "작가가 확정한 포맷을 그대로 기재",
    "recommended_format": "영화 | 시리즈 | 미니시리즈(4~8화) — 소재에 가장 맞는 것 하나",
    "match": true,
    "event_density": "이 소재가 지탱할 수 있는 주요 사건 수와 밀도 1문장",
    "character_load": "축이 되는 인물 수와 각 인물이 요구하는 분량 1문장",
    "rationale": "왜 그 포맷인지 2문장 이내. 사건 밀도와 인물 수를 근거로 제시",
    "if_forced": "작가가 확정한 포맷을 유지할 경우 무엇을 덜어내거나 늘려야 하는지 1문장"
  }},
  "gate_a_scores": {{
    "protagonist_visible": 0.0,
    "conflict_one_line": 0.0,
    "differentiation": 0.0,
    "poster_image": 0.0,
    "market_potential": 0.0,
    "average": 0.0
  }}
}}

규칙:
- gate_a_scores.average = 5개 항목의 평균, 소수점 1자리 반올림
- 모든 점수는 0.0~10.0
- hook_sentence는 1위 컨셉의 핵심을 기반으로 작성
- market_insight, cultural_code, market_risk, format_rationale, structure_note는 각 2문장 이내
- differentiation은 정확히 3개

[format_fit 작성 규칙 — v2.7.1]
- current_format에는 위 [입력]의 포맷 값을 그대로 기재한다.
- recommended_format은 소재 자체가 요구하는 포맷이다. 작가의 선택에 맞추지 마라.
- match는 두 값이 실질적으로 같으면 true, 다르면 false.
- ★ 이것은 권고이지 판정이 아니다. 작가의 선택을 바꾸라고 요구하지 마라.
  match가 false여도 if_forced에 "이 포맷을 유지하려면 무엇을 조정해야 하는지"를
  건설적으로 제시하는 것으로 끝낸다.
- 판단 근거는 사건 밀도와 인물 수여야 한다. 흥행성·플랫폼 트렌드를 근거로 들지 마라.
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2000,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        txt = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()
        st.session_state["last_analysis_raw"] = txt

        return safe_json_loads(txt)

    except Exception as e:
        st.session_state["last_error"] = str(e)
        st.error(f"분석 실패: {e}")
        raw = st.session_state.get("last_analysis_raw")
        if raw:
            with st.expander("🔧 Analysis Raw Response (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── API Call: Core Build Main (1단계) ───
def call_core_build_main(idea, genre, market, fmt, selected_concept, research=None, locked_block="",
                          fact_based=False, historical=False, film_type=""):
    """Core Build 1단계: Logline + Intent + World + Character + Goal/Need/Strategy"""
    try:
        client = get_client()

        # v2.4.0: 시대극 자동 감지 컨텍스트 추출
        _locked_text, _idea_text = _get_period_scan_context({
            "idea_text": idea or "",
            "genre": genre,
            "title": (selected_concept or {}).get("title", "") if selected_concept else "",
            "locked_items": [locked_block] if locked_block else [],
        })
        system_prompt = P.build_system_core(
            genre, fact_based=fact_based, historical=historical, film_type=film_type,
            locked_text=_locked_text, idea_text=_idea_text, fmt=fmt,
        )

        research_block = ""
        if research:
            research_block = f"\n[리서치 참고]\n{json.dumps(research, ensure_ascii=False)}"

        user_prompt = f"""[입력]
아이디어: {idea}
장르: {genre}
타겟: {market}
포맷: {fmt}

[선정 컨셉]
{json.dumps(selected_concept, ensure_ascii=False)}
{research_block}
{locked_block}

[JSON 스키마]
{{
  "logline_pack": {{
    "original": "원본 로그라인 1문장",
    "washed": "서사 불순물 제거한 정제 로그라인 1문장",
    "investor": "투자자용 1문장",
    "director": "감독용 1문장",
    "character_hook": "배우용 캐릭터 훅 1문장"
  }},
  "project_intent": {{
    "subject": "소재 기획의도 — 이 소재가 왜 지금 필요한가, 어떤 현실/감정/사회적 맥락과 연결되는가 (2~3문장)",
    "genre_approach": "장르 기획의도 — 이 장르 접근이 왜 유효한가, 관객에게 어떤 체험을 주는가 (2~3문장)",
    "market_rationale": "시장 기획의도 — 타겟 시장에서 왜 통하는가, 어떤 수요/트렌드/공백에 대응하는가 (2~3문장)",
    "pitch": "엘리베이터 피치 1문장",
    "theme": "주제 1문장",
    "tone_manner": ["톤앤매너 키워드 3~5개"]
  }},
  "goal_need_strategy": {{
    "goal": "주인공의 목적/욕망 1문장",
    "need": "진짜 결핍 (본인은 모르는 것) 1문장",
    "strategy": "해결 전략/방법 1문장",
    "risk": "실패 시 잃는 것 1문장",
    "ending_payoff": "결말에서 G/N/S가 어떻게 회수되는가 1문장"
  }},
  "narrative_drive": {{
    "desire_origin": "loss 또는 lack — 주인공의 욕망이 상실에서 시작되었는가, 결핍에서 시작되었는가",
    "origin_detail": "구체적으로 무엇을 잃었는가(loss) 또는 무엇이 없었는가(lack) 1문장",
    "arc_direction": "loss면 회복/복수/대체 중 택1, lack이면 획득/성장/증명 중 택1",
    "resolution_strategy": "이 이야기만의 독특한 해결 방식 — 기존작과 뭐가 다른가 1문장",
    "goal_need_gap": "Goal(외적 욕망)과 Need(내적 필요) 사이의 간극 1문장 — 이 간극이 이야기를 끌고 간다",
    "cost": {{
      "relation": "주인공의 Strategy가 주변 관계를 어떻게 망가뜨리는가 1문장 — 2막 후반에 누적되어 실재 손상이 될 것",
      "self": "주인공의 Strategy가 주인공 자신을 어떻게 마모시키는가 1문장 — 3막에서 자기 자신과 직면하게 할 것",
      "world": "주인공의 Strategy가 주인공이 지키려던 세계(공동체/직업/가치)를 어떻게 무너뜨리는가 1문장"
    }},
    "strategy_transformation": "3막에서 Strategy_1이 어떻게 Strategy_2로 전환되는가 1문장 — 외적 선택이 아닌 내적 전환으로 기술"
  }},
  "bjnd_four_axis_check": {{
    "necessity": {{
      "question": "이 인물이 왜 지금 이렇게 살아야만 했는가?",
      "answer": "Lack/Loss의 필연성을 입증하는 1~2문장 — 막연한 설정이 아닌 구체적 사건/기억 기반",
      "life_permeation": "이 Lack/Loss이 인물의 일상을 관통하는 3가지 방식 (각 1문장)"
    }},
    "authenticity": {{
      "question": "이 Strategy는 이 인물이 아니면 불가능한가?",
      "substitution_test": "이 Strategy를 다른 유명 작품 주인공에게 붙여도 성립하는가? PASS(다른 인물에게 붙일 수 없음) 또는 FAIL(누구나 쓸 수 있음)",
      "organic_link": "직업 + Lack + Strategy를 한 문장으로 유기적으로 연결",
      "author_justification": "왜 이 인물은 이런 방식으로 해결하려 하는가? 작가 시선이 담긴 1문장"
    }},
    "empathy": {{
      "question": "관객이 이 인물의 Cost를 보며 자기 자신을 떠올릴 것인가?",
      "universal_wound": "이 Cost가 건드리는 동시대 보편 상처 1문장",
      "audience_mirror": "관객이 이 인물에서 자기를 발견할 지점 1문장",
      "resonance_target": "특히 공감할 관객층 (예: 30대 여성 직장인, 40대 남성 아버지 등)"
    }},
    "potency": {{
      "question": "이 인물의 Strategy 전환이 관객 마음에 얼마나 큰 흔적을 남길 것인가?",
      "strategy_arc": "1막 Strategy_1 → 3막 Strategy_2, 한 문장 대비",
      "signature_moment": "변화가 완성되는 결정적 한 순간 1문장",
      "afterimage": "영화 끝난 뒤에도 관객이 떠올릴 잔상 이미지 1컷"
    }},
    "audience_scenes": {{
      "laughter_scene": "관객이 웃을 장면 1~2개 구체 (로코/코미디 아닐 경우 빈 문자열)",
      "heartache_scene": "관객이 가슴 먹먹해질 장면 1~2개 구체",
      "self_reflection_scene": "관객이 '나였다면 어떻게 했을까'를 고민할 장면 1개 구체",
      "memorable_line_or_image": "영화 끝난 후 관객 입에 남을 장면 1개"
    }}
  }},
  "genre_expectation_check": {{
    "genre_fun_alive": "true 또는 false — 이 장르의 재미 본질이 살아있는가",
    "genre_fun_diagnosis": "이 작품에서 장르 재미가 어떻게 살아있는지 3줄 진단",
    "checklist": {{
      "item_label_1": "YES 또는 NO + 1문장 근거 — 해당 장르 체크리스트 항목 1",
      "item_label_2": "YES 또는 NO + 1문장 근거 — 해당 장르 체크리스트 항목 2",
      "item_label_3": "YES 또는 NO + 1문장 근거 — 해당 장르 체크리스트 항목 3",
      "item_label_4": "YES 또는 NO + 1문장 근거 — 해당 장르 체크리스트 항목 4",
      "item_label_5": "YES 또는 NO + 1문장 근거 — 해당 장르 체크리스트 항목 5",
      "item_label_6": "YES 또는 NO + 1문장 근거 — 해당 장르 체크리스트 항목 6 (있으면)",
      "item_label_7": "YES 또는 NO + 1문장 근거 — 해당 장르 체크리스트 항목 7 (있으면)"
    }},
    "weak_zones": ["장르 기대가 약할 것으로 예상되는 비트 구간 명시 (예: '클라이맥스가 로맨스 완성 아님', '2막 Fun and Games 부족')"],
    "climax_verdict": "CLIMAX_PASS 또는 CLIMAX_FAIL — 장르 약속에 맞는 클라이맥스인가. FAIL이면 3막 전체 재설계 강제"
  }},
  "opening_strategy": {{
    "opening_type": "Action Drop / Cold Open / Tease & Reveal / In Media Res / Character Reveal Action / Hook Dialogue 중 택1 — 시스템 프롬프트의 오프닝 DNA 매핑에 따른 권장 기법을 우선하되, 작품 특성에 맞게 택1",
    "opening_intent": "이 오프닝으로 무엇을 잡는가 — 캐릭터 / 세계 / 사건 / 톤 / 테마 중 1~2개 구체화",
    "dopamine_point": "첫 3분 안에 관객이 느낄 구체적 감각 — 충격 / 웃음 / 긴장 / 경이 / 호기심 / 감정 울림 중 1개 선택 + 어떤 방식으로 터뜨리는가 1문장",
    "opening_to_act1_link": "오프닝과 1막 본편의 연결 논리 — 동일 시점 진입 / 플래시백 회수 / 톤 브리지 / 병렬 구조 중 어떤 방식인가 1문장",
    "opening_hook_line": "오프닝의 기억에 남을 한 줄 대사 또는 한 이미지 — 실제 시나리오에 쓸 수 있는 수준으로 구체적으로",
    "genre_dna_check": "이 오프닝이 장르 DNA 자가검증 질문에 어떻게 대답하는가 — 예) 호러면 '첫 3분 안에 공포의 규칙/흔적이 심어졌는가?'에 어떻게 YES인가 1문장"
  }},
  "world_build": {{
    "time": "시간 배경",
    "space": "공간 배경",
    "rules": "세계관 규칙 1문장",
    "taboo": "금기 1문장",
    "power_structure": "권력 구조 1문장",
    "visual_keywords": ["시각 이미지 키워드 3~5개"],
    "conflict_points": ["세계관 충돌 포인트 3개"]
  }},
  "characters": [
    {{
      "role": "protagonist",
      "name": "",
      "description": "인물 소개 1문장",
      "goal": "이 인물의 욕망 1문장",
      "need": "결핍 1문장",
      "strategy": "행동 방식 1문장",
      "flaw": "결점 1문장",
      "arc": "변화 1문장",
      "dialogue_tone": "대사 톤 키워드"
    }},
    {{
      "role": "antagonist",
      "name": "",
      "description": "",
      "goal": "",
      "need": "",
      "strategy": "",
      "flaw": "",
      "arc": "",
      "dialogue_tone": ""
    }},
    {{
      "role": "ally",
      "name": "",
      "description": "",
      "goal": "",
      "flaw": "",
      "dialogue_tone": ""
    }},
    {{
      "role": "mirror",
      "name": "",
      "description": "",
      "goal": "",
      "flaw": "",
      "dialogue_tone": ""
    }}
  ],
  "extended_characters": [
    {{
      "role": "역할명 (catalyst/subplot_lead/mentor/rival/informant/love_interest 등 자유)",
      "name": "",
      "description": "이 인물이 이야기에 왜 필요한가 1문장",
      "goal": "",
      "flaw": "",
      "dialogue_tone": ""
    }}
  ],
  "relationship_map": [
    "주인공↔적대자: 관계 1문장",
    "주인공↔조력자: 관계 1문장",
    "주인공↔거울: 관계 1문장",
    "확장 캐릭터 간 핵심 관계: 1문장씩"
  ],
  "attraction_design": {{
    "opening_hook": {{
      "type": "A1(In Medias Res) / A2(충격적 사건) / A3(결함 드러남) 중 선택",
      "description": "첫 장면 구체적 묘사 — 어떤 장면으로 시작하는가 2~3문장",
      "forbidden_check": "설명/일상/내레이션으로 시작하지 않는다는 확인 1문장"
    }},
    "twist_point": {{
      "expected_direction": "관객이 예상할 전개 1문장",
      "betrayal": "그 예상을 깨는 배반 포인트 1문장 — 이 이야기만의 방향",
      "why_more_true": "배반이 단순 반전이 아니라 더 진실된 방향인 이유 1문장"
    }},
    "water_cooler_moment": {{
      "scene_or_setup": "관객이 다음 날 누군가에게 말하고 싶어지는 장면 또는 설정 1문장",
      "why_memorable": "왜 기억에 남는가 1문장"
    }},
    "korean_specificity": [
      "이 이야기의 한국적 구체성 — 추상어 금지, 공간/제도/관계로 표현 (3개)"
    ],
    "villain_logic": "빌런이 자신만의 논리 안에서 옳다고 믿는 이유 1문장",
    "emotional_explosion": {{
      "suppression": "어떤 감정을 언제까지 억누르는가 1문장",
      "explosion_moment": "어느 장면에서 터지는가 1문장"
    }},
    "forbidden_directions": [
      "이 이야기가 절대 가면 안 되는 방향 3개 — 뻔해지는 순간들"
    ],
    "planting_payoff": [
      {{
        "type": "character / relationship / world 중 선택",
        "plant": "1막에 심는 것 — 대사/소품/습관/장소/이미지 1문장",
        "plant_scene": "어느 장면에서 심는가 (Beat 번호 또는 상황)",
        "payoff": "2막 후반~3막에서 회수 — 새로운 의미로 돌아오는 순간 1문장",
        "payoff_scene": "어느 장면에서 회수하는가 (Beat 번호 또는 상황)"
      }}
    ]
  }},
  "research_applied": {{
    "references_used": [
      {{
        "source_type": "real_event / existing_work",
        "source_id": 1,
        "source_title": "리서치 JSON에서 참조한 아이템의 제목",
        "applied_to": "character_background / world_rule / plot_event / motif / dialogue_reference / visual_detail 중 선택",
        "how_applied": "이 리서치 요소를 이 작품 어디에 어떻게 녹였는가 1문장 — 추상 금지, 구체적으로",
        "character_name": "해당 캐릭터 이름 (캐릭터에 적용된 경우, 아니면 빈 문자열)"
      }}
    ],
    "verisimilitude_anchors": [
      "핍진성 앵커 1 — Treatment·Scene·시나리오에서 반드시 유지할 현실 기반 디테일 1문장",
      "핍진성 앵커 2",
      "핍진성 앵커 3"
    ],
    "research_absorption_note": "리서치를 어떻게 소화했는지 작가 시점 1문장 — 단순 나열이 아닌 '이 작품만의 방식으로 어떻게 흡수되었는가'"
  }}
}}

규칙:
- logline_pack 각 버전은 관점만 다르고 같은 이야기를 가리켜야 한다.
- attraction_design은 이 이야기의 매력 설계도다. 가장 구체적으로 작성할 것.
- attraction_design.opening_hook.description은 실제 첫 장면을 그릴 수 있을 만큼 구체적으로.
- attraction_design.water_cooler_moment는 오징어게임의 달고나, 기생충의 냄새처럼 누군가에게 말하고 싶어지는 것.
- attraction_design.korean_specificity는 추상어(가난, 차별, 압박) 금지. 반드시 구체적 명사(반지하, 수능, 연습생 계약서)로.
- attraction_design.planting_payoff는 최소 3개. type별 최소 1개씩 (character/relationship/world). Plant 없는 Payoff(데우스 엑스 마키나) 금지.
- goal_need_strategy는 이 작품의 서사 엔진이다. 가장 정밀하게 작성할 것.
- narrative_drive는 BLUE JEANS 고유 서사동력 프레임워크다. desire_origin이 loss인지 lack인지를 정확히 진단하라. 이것이 이야기 전체의 방향을 결정한다.
- characters는 필수 4명(protagonist/antagonist/ally/mirror). extended_characters는 이야기가 필요로 하는 만큼 0~4명 추가 (최대 총 8명). 영화는 4~5명, 미니시리즈는 6~8명이 적정. 각 인물의 goal이 서로 달라야 한다.
- extended_characters의 role은 자유. catalyst(촉매자), subplot_lead(서브플롯 리드), mentor(멘토), rival(라이벌), informant(정보원), love_interest(연인) 등 이야기에 맞는 역할명을 직접 지정.
- world_build의 conflict_points는 세계관이 만들어내는 갈등이어야 한다.
- [v2.3.8 신규] research_applied는 '이 작품에 실제로 응용된 리서치 요소만' 선별 기록. 리서치에 있었으나 이 작품에 녹지 못한 것은 제외.
  references_used는 최소 2개, 최대 6개. 모든 항목의 how_applied는 '어디에/어떻게'가 구체적으로 드러나야 한다.
  verisimilitude_anchors는 정확히 3~5개. Treatment·시나리오에서 Writer Engine이 반드시 유지할 핵심 디테일.
  리서치가 제공되지 않은 경우에도 references_used는 빈 배열로 두되, verisimilitude_anchors는 작품 자체의 내적 설정 기반으로 3개 생성.
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=16000,
            temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        if response.stop_reason == "max_tokens":
            st.warning("⚠️ Core Build 응답 잘림. 재시도...")
            response = client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=16000,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

        txt = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()
        st.session_state["last_core_raw"] = txt

        return safe_json_loads(txt)

    except Exception as e:
        st.session_state["last_error"] = str(e)
        st.error(f"Core Build 실패: {e}")
        raw = st.session_state.get("last_core_raw", "")
        if raw:
            with st.expander("🔧 Core Build Raw Response (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── API Call: Core Gate (2단계) ───
def call_core_gate(core_data):
    """Core Build 2단계: Gate B (Drive) + Gate C (Character) 채점"""
    try:
        client = get_client()

        system_prompt = P.SYSTEM_CORE_GATE

        user_prompt = f"""[Core Build 결과]
{json.dumps(core_data, ensure_ascii=False)}

[JSON 스키마]
{{
  "gate_b_drive": {{
    "goal_clarity": 0.0,
    "need_from_loss": 0.0,
    "strategy_creative": 0.0,
    "failure_cost": 0.0,
    "average": 0.0,
    "feedback": "Gate B 종합 피드백 1문장"
  }},
  "gate_c_character": {{
    "protagonist_antagonist_logic": 0.0,
    "supporting_not_functional": 0.0,
    "relationship_produces_conflict": 0.0,
    "average": 0.0,
    "feedback": "Gate C 종합 피드백 1문장"
  }},
  "five_axis_scores": {{
    "goal": 0.0,
    "need": 0.0,
    "strategy": 0.0,
    "structure": 0.0,
    "character_concept": 0.0,
    "final_score": 0.0,
    "verdict": "개발 진행 | 개발 보류 | 구조 재설계"
  }}
}}

규칙:
- gate_b average = 4항목 평균
- gate_c average = 3항목 평균
- five_axis: structure는 아직 Structure Build 전이므로 goal/need/strategy 기반으로 잠정 추정
- final_score = 0.20*goal + 0.20*need + 0.20*strategy + 0.25*structure + 0.15*character_concept
- verdict: 8.0 이상 → 개발 진행, 6.0~7.9 → 개발 보류, 5.9 이하 → 구조 재설계
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=2000,
            temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )

        txt = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()
        st.session_state["last_gate_raw"] = txt

        return safe_json_loads(txt)

    except Exception as e:
        st.session_state["last_error"] = str(e)
        st.error(f"Gate 채점 실패: {e}")
        raw = st.session_state.get("last_gate_raw", "")
        if raw:
            with st.expander("🔧 Gate Raw Response (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── API Call: Reality Gate (v2.7.0 신규) ───
def call_reality_gate(project, core_data):
    """Core 직후 사실성 검문 — 제도·절차·직업 역할 위배 전제를 적출.

    LOCKED는 보존 대상이지 검증 대상이 아니므로, 상류(Idea Engine)가
    틀린 전제를 넘기면 하류 전 단계가 오염된다. 이 함수는 그 오염을
    Core 시점에서 한 번 걸러내기 위한 검문소다.

    엔진은 적출만 하고, 채택 여부는 전적으로 작가가 결정한다.
    """
    try:
        client = get_client()

        locked_items = project.get("locked_items", []) or []
        locked_text = "\n".join(f"- {x}" for x in locked_items) if locked_items else "(없음)"

        # 직업 감지 결과를 근거 자료로 함께 주입
        prof_block = ""
        try:
            import profession_pack as PP
            scan = " ".join(locked_items) + " " + (project.get("idea_text") or "")
            cats = PP.detect_profession_category(scan)
            irs = []
            for c in cats:
                data = PP.PROFESSION_PACK.get(c, {})
                ir = data.get("institutional_reality")
                if ir:
                    irs.append(f"[{c}]\n{ir}")
            if irs:
                prof_block = (
                    "\n\n[제도 사실성 참조 자료 — 감지된 직군]\n"
                    "아래는 판정 근거로 쓸 수 있는 확정 자료다. "
                    "여기에 없는 영역은 일반 지식으로 판단하되, 확신이 없으면 적출하지 말 것.\n\n"
                    + "\n\n".join(irs)
                )
        except Exception:
            prof_block = ""

        user_prompt = f"""[작품 기본 정보]
제목: {project.get('title', '')}
장르: {project.get('genre', '')}
포맷: {project.get('format', '')}
타겟 시장: {project.get('target_market', '')}
실화 기반: {project.get('fact_based', False)}
시대극: {project.get('historical', False)}

[아이디어 원문]
{project.get('idea_text', '')}

[LOCKED 항목 — 상류에서 확정되어 넘어온 것]
{locked_text}

[Core Build 결과]
{json.dumps(core_data, ensure_ascii=False)}
{prof_block}

[JSON 스키마]
{{
  "verdict": "CLEAR | ISSUES_FOUND",
  "scanned_domains": ["점검한 영역 1", "점검한 영역 2"],
  "issues": [
    {{
      "id": "R1",
      "severity": "CRITICAL | MAJOR | MINOR",
      "domain": "직업 역할 | 법적 효력 | 절차·기간 | 조직·권한 | 물리적 성립",
      "location": "LOCKED 항목 또는 Core 필드의 원문 일부 (40자 이내)",
      "error": "무엇이 틀렸는지 1문장",
      "reality": "실제로는 어떤지 1~2문장. 근거 조문·제도명 있으면 명시",
      "impact": "이대로 두면 Writer Engine·촬영 단계에서 무엇이 깨지는지 1문장",
      "alternatives": [
        "원 설계 의도를 보존하면서 사실만 교정한 대안 1",
        "원 설계 의도를 보존하면서 사실만 교정한 대안 2"
      ],
      "suggested_locked": "대안 1을 반영한 LOCKED 교체 문장 (원문과 같은 형식, 1줄)"
    }}
  ],
  "author_note": "작가가 의도적으로 비튼 것으로 보이는 설정이 있으면 여기에 기록. 없으면 빈 문자열."
}}

규칙:
- issues는 최대 5건. 심각도 높은 순 정렬.
- 위배 사항이 없으면 issues를 빈 배열로 두고 verdict는 "CLEAR".
- 확신이 없으면 적출하지 않는다. 오탐이 미탐보다 해롭다.
- 흥행성·완성도·취향에 대한 의견은 절대 포함하지 않는다.
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=4000,
            temperature=0.1,
            system=P.SYSTEM_REALITY_GATE,
            messages=[{"role": "user", "content": user_prompt}]
        )

        txt = "".join(
            block.text for block in response.content if hasattr(block, "text")
        ).strip()
        st.session_state["last_reality_raw"] = txt

        return safe_json_loads(txt)

    except Exception as e:
        st.session_state["last_error"] = str(e)
        st.error(f"Reality Gate 실패: {e}")
        raw = st.session_state.get("last_reality_raw", "")
        if raw:
            with st.expander("🔧 Reality Gate Raw Response (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── API Call: Character Bible ───
def call_character_bible_single(char_data, all_chars_names, core_data, genre, fmt, locked_block="",
                                 fact_based=False, historical=False, film_type="",
                                 prior_chars_block=""):
    """캐릭터 바이블 — 캐릭터 1인 단위 호출
    
    Args:
        prior_chars_block: 이미 생성된 다른 캐릭터들의 일관성 사실 블록 (v2.3.1 신규).
                          빈 문자열이면 일관성 참조 없이 생성 (첫 번째 캐릭터).
    """
    try:
        client = get_client()
        gns = core_data.get("goal_need_strategy", {})
        nd = core_data.get("narrative_drive", {})
        lp = core_data.get("logline_pack", {})
        wb = core_data.get("world_build", {})

        char_json = json.dumps(char_data, ensure_ascii=False)
        gns_json = json.dumps(gns, ensure_ascii=False)
        wb_json = json.dumps(wb, ensure_ascii=False)

        role = char_data.get("role", "")
        name = char_data.get("name", "")
        other_names = [n for n in all_chars_names if n != name]
        others_str = ", ".join(other_names) if other_names else "없음"

        # v2.4.0: 시대극 자동 감지 컨텍스트 추출
        _locked_text, _idea_text = _get_period_scan_context({
            "genre": genre,
            "core_data": core_data or {},
            "locked_items": [locked_block] if locked_block else [],
        })
        system_prompt = P.build_system_char_bible(genre, fmt, others_str,
                                                    fact_based=fact_based, historical=historical, film_type=film_type,
                                                    locked_text=_locked_text, idea_text=_idea_text)

        schema = P.CHAR_BIBLE_SCHEMA.replace("ROLE_PLACEHOLDER", role).replace("NAME_PLACEHOLDER", name)

        user_prompt = f"""[확장할 캐릭터]
{char_json}

[작품 Goal/Need/Strategy]
{gns_json}

[세계관]
{wb_json}

[로그라인]
{lp.get("washed","")}

[다른 캐릭터 이름 (관계별 태도 작성용)]
{others_str}
{locked_block}
{prior_chars_block}
[JSON 스키마 — 이 캐릭터 1인분만 출력]
{schema}

{P.CHAR_BIBLE_RULES}"""

        # ─── v2.5.3: 스트리밍 호출로 전환 (long requests 정책 대응) ───
        with client.messages.stream(
            model=ANTHROPIC_MODEL_OPUS, max_tokens=24000, temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        ) as stream:
            response = stream.get_final_message()
        # max_tokens 잘림 시 분량 줄여서 재시도 (v2.5.1: max_tokens 24000으로 상향)
        if response.stop_reason == "max_tokens":
            retry_prompt = user_prompt.replace(
                "외형·첫인상 3문장", "외형·첫인상 2문장"
            ).replace(
                "과거사 5문장", "과거사 3문장"
            ).replace(
                "1막 끝 상태 2문장", "1막 끝 상태 1문장"
            ).replace(
                "미드포인트 상태 2문장", "미드포인트 상태 1문장"
            ).replace(
                "클라이맥스 상태 2문장", "클라이맥스 상태 1문장"
            )
            with client.messages.stream(
                model=ANTHROPIC_MODEL_OPUS, max_tokens=24000, temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": retry_prompt}]
            ) as stream:
                response = stream.get_final_message()
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        st.session_state[f"last_char_bible_{role}_raw"] = txt

        # ─── v2.5.1: JSON 파싱 시도 — 실패 시 자동 재시도 2회 ───
        # 1차 실패 → temperature 0.15로 재시도 (소프트 강화)
        # 2차 실패 → temperature 0.05 + JSON_OUTPUT_RULES_STRICT 주입 (하드 강화)
        try:
            return safe_json_loads(txt)
        except json.JSONDecodeError:
            st.warning(f"⚠️ {name} JSON 파싱 실패 — 1차 재시도 중 (temp 0.15)...")
            # 1차 재시도: JSON 규칙을 더 강하게 강조 + temperature 하강
            retry_system_1 = system_prompt + "\n\n★ 최우선 규칙: 반드시 유효한 JSON만 출력. 대사 안의 따옴표는 작은따옴표만. 줄바꿈 금지. 역슬래시 금지. 후행 쉼표 금지. 코드 펜스(```) 금지. 출력 시작은 { 끝은 }. ★"
            with client.messages.stream(
                model=ANTHROPIC_MODEL_OPUS, max_tokens=24000, temperature=0.15,
                system=retry_system_1,
                messages=[{"role": "user", "content": user_prompt}]
            ) as stream:
                response2 = stream.get_final_message()
            txt2 = "".join(b.text for b in response2.content if hasattr(b, "text")).strip()
            st.session_state[f"last_char_bible_{role}_raw"] = txt2

            try:
                return safe_json_loads(txt2)
            except json.JSONDecodeError:
                st.warning(f"⚠️ {name} 1차 재시도도 실패 — 2차 재시도 중 (temp 0.05, STRICT 룰 주입)...")
                # 2차 재시도: temperature 최저 + JSON_OUTPUT_RULES_STRICT 추가 주입
                retry_system_2 = system_prompt + "\n\n" + P.JSON_OUTPUT_RULES_STRICT + "\n\n★ 절대 위반 금지: 단일 JSON 객체. 코드 펜스 금지. 설명 텍스트 금지. 첫 문자는 { 마지막 문자는 }. 대사 안의 인용은 작은따옴표만. 줄바꿈·역슬래시·후행 쉼표 모두 금지. ★"
                with client.messages.stream(
                    model=ANTHROPIC_MODEL_OPUS, max_tokens=24000, temperature=0.05,
                    system=retry_system_2,
                    messages=[{"role": "user", "content": user_prompt}]
                ) as stream:
                    response3 = stream.get_final_message()
                txt3 = "".join(b.text for b in response3.content if hasattr(b, "text")).strip()
                st.session_state[f"last_char_bible_{role}_raw"] = txt3
                return safe_json_loads(txt3)

    except Exception as e:
        st.error(f"Character Bible ({name}) 생성 실패: {e}")
        raw = st.session_state.get(f"last_char_bible_{role}_raw", "")
        if raw:
            with st.expander(f"🔧 {name} Raw (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


def call_character_bible(core_data, genre, fmt, locked_block="",
                         fact_based=False, historical=False, film_type=""):
    """캐릭터 바이블 — characters + extended_characters 모두 처리
    
    v2.3.1: 순차 생성 시 이전 캐릭터의 핵심 사실을 다음 캐릭터 생성 프롬프트에 주입하여
            가족 관계·학력·나이 등의 일관성 모순을 차단한다.
    """
    chars = core_data.get("characters", [])
    ext_chars = core_data.get("extended_characters", [])
    all_chars = chars + ext_chars
    all_names = [c.get("name", f"캐릭터{i+1}") for i, c in enumerate(all_chars)]

    result_chars = []
    prior_facts = []  # v2.3.1: 이전 캐릭터들의 일관성 사실 누적

    for i, ch in enumerate(all_chars):
        name = ch.get("name", f"캐릭터{i+1}")
        role = ch.get("role", "")

        # v2.3.1: 이전 캐릭터 맥락 블록 생성
        prior_chars_block = P.build_prior_chars_consistency_block(prior_facts)

        if i == 0:
            st.info(f"📖 {i+1}/{len(all_chars)} — {name} ({role}) 바이블 생성 중... (최초 캐릭터)")
        else:
            st.info(f"📖 {i+1}/{len(all_chars)} — {name} ({role}) 바이블 생성 중... "
                    f"(이전 {len(prior_facts)}명과 일관성 검증 중)")

        char_result = call_character_bible_single(
            ch, all_names, core_data, genre, fmt,
            locked_block=locked_block,
            fact_based=fact_based, historical=historical, film_type=film_type,
            prior_chars_block=prior_chars_block,  # v2.3.1 신규
        )

        if char_result:
            result_chars.append(char_result)
            # v2.3.1: 성공한 캐릭터의 일관성 사실을 추출하여 다음 캐릭터 생성 시 참조
            facts = P.extract_char_consistency_facts(char_result)
            prior_facts.append(facts)
        else:
            st.warning(f"⚠️ {name} 바이블 생성 실패. 건너뜁니다.")

    if result_chars:
        return {"characters": result_chars}
    return None


# ─── API Call: Structure Build Story (1단계) ───
def call_structure_story(core_data, genre, market, fmt, locked_block="",
                          fact_based=False, historical=False, film_type=""):
    """Structure 1단계: Synopsis 1P + Storyline"""
    try:
        client = get_client()
        gns = core_data.get("goal_need_strategy", {})
        nd = core_data.get("narrative_drive", {})
        lp = core_data.get("logline_pack", {})
        chars = core_data.get("characters", []) + core_data.get("extended_characters", [])

        # v2.4.0: 시대극 자동 감지 컨텍스트 추출
        _locked_text, _idea_text = _get_period_scan_context({
            "genre": genre,
            "core_data": core_data or {},
            "locked_items": [locked_block] if locked_block else [],
        })
        system_prompt = P.build_system_structure_story(
            fact_based=fact_based, historical=historical, film_type=film_type,
            locked_text=_locked_text, idea_text=_idea_text,
        )

        user_prompt = f"""[Core Build 요약]
로그라인: {lp.get("washed", lp.get("original", ""))}
장르: {genre} / 타겟: {market} / 포맷: {fmt}
{locked_block}
Goal: {gns.get("goal","")}
Need: {gns.get("need","")}
Strategy: {gns.get("strategy","")}
캐릭터: {json.dumps(chars, ensure_ascii=False)}

[JSON 스키마]
{{
  "synopsis_1p": {{
    "opening": "시작 상황",
    "catalyst": "촉발 사건",
    "development": "전개",
    "midpoint": "미드포인트 전환",
    "collapse": "붕괴/위기",
    "climax": "결전",
    "ending": "결말"
  }},
  "storyline": [
    {{
      "seq": 1,
      "label": "시퀀스 라벨 (동사→동사 형식)",
      "pages": "p.1~15",
      "summary": "이 구간 전개 요약",
      "conflict": "이 구간의 갈등",
      "emotion": "감정선 키워드",
      "hook": "다음 구간으로 당기는 힘"
    }}
  ]
}}

규칙:
- synopsis_1p 각 항목 2문장 이내
- storyline은 8개 시퀀스 (영화 기준)
- 시리즈면 시퀀스 대신 에피소드 단위 6~8개
- 각 시퀀스의 summary, conflict, hook 1문장씩
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL, max_tokens=16000, temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        if response.stop_reason == "max_tokens":
            response = client.messages.create(
                model=ANTHROPIC_MODEL, max_tokens=16000, temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        st.session_state["last_structure_story_raw"] = txt
        return safe_json_loads(txt)
    except Exception as e:
        st.error(f"Story 생성 실패: {e}")
        raw = st.session_state.get("last_structure_story_raw", "")
        if raw:
            with st.expander("🔧 Story Raw (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── API Call: Structure Build Diagnosis + Character Arcs (2단계) ───
def call_structure_diagnosis(core_data, story_data, genre, fmt, locked_block="",
                              fact_based=False, historical=False, film_type=""):
    """Structure 2단계: 3막 구조 진단 + 15비트 + 캐릭터 관계 변화표"""
    try:
        client = get_client()
        gns = core_data.get("goal_need_strategy", {})
        nd = core_data.get("narrative_drive", {})
        chars = core_data.get("characters", []) + core_data.get("extended_characters", [])

        # v2.4.0: 시대극 자동 감지 컨텍스트 추출
        _locked_text, _idea_text = _get_period_scan_context({
            "genre": genre,
            "core_data": core_data or {},
            "locked_items": [locked_block] if locked_block else [],
        })
        system_prompt = P.build_system_structure_diagnosis(
            fact_based=fact_based, historical=historical, film_type=film_type,
            locked_text=_locked_text, idea_text=_idea_text,
        )

        user_prompt = f"""[입력]
장르: {genre} / 포맷: {fmt}
{locked_block}
Goal: {gns.get("goal","")} / Need: {gns.get("need","")} / Strategy: {gns.get("strategy","")}
서사동력: {nd.get("desire_origin","")}({nd.get("origin_detail","")}) → {nd.get("arc_direction","")} / 해결전략: {nd.get("resolution_strategy","")}

[캐릭터]
{json.dumps(chars, ensure_ascii=False)}

[시놉시스]
{json.dumps(story_data.get("synopsis_1p", {}), ensure_ascii=False)}

[스토리라인]
{json.dumps(story_data.get("storyline", []), ensure_ascii=False)}

[JSON 스키마]
{{
  "three_act": {{
    "act1_end": "1막 끝 전환점",
    "act2_midpoint": "미드포인트",
    "act2_end": "2막 끝 전환점 (All Is Lost)",
    "act3_climax": "클라이맥스",
    "diagnosis": "3막 구조 종합 진단 1문장"
  }},
  "beat_sheet": [
    {{
      "beat": "Opening Image",
      "status": "있음|약함|없음",
      "note": "근거 1문장"
    }}
  ],
  "character_arcs": [
    {{
      "name": "캐릭터 이름",
      "role": "protagonist|antagonist|ally|mirror|catalyst|subplot_lead",
      "act1_state": "1막에서의 상태/태도 1문장",
      "turning_point": "변화를 촉발하는 사건 1문장",
      "act3_state": "3막에서의 변화된 상태 1문장",
      "arc_type": "성장|몰락|각성|반전|정체"
    }}
  ],
  "relationship_changes": [
    {{
      "pair": "캐릭터A ↔ 캐릭터B",
      "act1": "1막 관계 상태",
      "midpoint": "미드포인트 관계 전환",
      "act3": "3막 관계 도착점"
    }}
  ]
}}

규칙:
- beat_sheet는 15비트 전체 (Opening Image ~ Final Image)
- beat status는 반드시 있음/약함/없음 중 하나
- character_arcs는 Core Build의 캐릭터 전원
- relationship_changes는 핵심 관계 3~4쌍
- 모든 필드 1문장 이내로 압축
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL, max_tokens=16000, temperature=0.25,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        if response.stop_reason == "max_tokens":
            response = client.messages.create(
                model=ANTHROPIC_MODEL, max_tokens=16000, temperature=0.25,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        st.session_state["last_structure_diag_raw"] = txt
        return safe_json_loads(txt)
    except Exception as e:
        st.error(f"구조 진단 실패: {e}")
        raw = st.session_state.get("last_structure_diag_raw", "")
        if raw:
            with st.expander("🔧 Diagnosis Raw (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── API Call: Structure Gate D (3단계) ───
def call_structure_gate(story_data, diag_data):
    """Structure 3단계: Gate D 채점"""
    try:
        client = get_client()
        system_prompt = P.SYSTEM_STRUCTURE_GATE

        user_prompt = f"""[시놉시스]
{json.dumps(story_data.get("synopsis_1p",{}), ensure_ascii=False)}

[3막 구조]
{json.dumps(diag_data.get("three_act",{}), ensure_ascii=False)}

[15비트]
{json.dumps(diag_data.get("beat_sheet",[]), ensure_ascii=False)}

[JSON 스키마]
{{
  "gate_d_structure": {{
    "turning_points_valid": 0.0,
    "midpoint_redirects": 0.0,
    "all_is_lost_works": 0.0,
    "ending_inevitable_surprising": 0.0,
    "average": 0.0,
    "feedback": "Gate D 종합 피드백 1문장"
  }}
}}
규칙: average = 4항목 평균."""

        response = client.messages.create(
            model=ANTHROPIC_MODEL, max_tokens=1500, temperature=0.2,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        st.session_state["last_structure_gate_raw"] = txt
        return safe_json_loads(txt)
    except Exception as e:
        st.error(f"Gate D 실패: {e}")
        return None


# ─── API Call: 기승전결 1pg 줄글 ───
def call_structure_prose(core_data, story_data):
    """기승전결 구조의 1페이지 줄글 시놉시스"""
    try:
        client = get_client()
        lp = core_data.get("logline_pack", {})
        gns = core_data.get("goal_need_strategy", {})
        nd = core_data.get("narrative_drive", {})
        syn = story_data.get("synopsis_1p", {})
        storyline = story_data.get("storyline", [])

        user_prompt = f"""[작품 정보]
로그라인: {lp.get("washed", lp.get("original",""))}
Goal: {gns.get("goal","")} / Need: {gns.get("need","")} / Strategy: {gns.get("strategy","")}
서사동력: {nd.get("desire_origin","")}({nd.get("origin_detail","")}) → {nd.get("arc_direction","")} / 해결전략: {nd.get("resolution_strategy","")}

[시놉시스]
{json.dumps(syn, ensure_ascii=False)}

[스토리라인]
{json.dumps(storyline, ensure_ascii=False)}

[요청]
위 정보를 기반으로 기-승-전-결 구조의 1페이지 분량 줄글 시놉시스를 작성하라.

규칙:
- 기(起): 상황 설정과 주인공 소개
- 승(承): 사건 전개와 갈등 심화
- 전(轉): 반전과 위기
- 결(結): 해결과 마무리
- 전체 500~700자 분량
- 줄글로 작성. 번호나 구분 기호 없이 자연스러운 서술체.
- 한국어로 작성.
- JSON 형식: {{"prose": "줄글 텍스트"}}
- JSON만 출력. JSON 외 텍스트 금지."""

        response = client.messages.create(
            model=ANTHROPIC_MODEL, max_tokens=2000, temperature=0.3,
            system=P.SYSTEM_STRUCTURE_PROSE,
            messages=[{"role": "user", "content": user_prompt}]
        )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        return safe_json_loads(txt)
    except Exception as e:
        st.error(f"줄글 시놉시스 생성 실패: {e}")
        return None


# ─── API Call: Scene Design (장면화) ───
def call_scene_design(core_data, story_data, diag_data, genre, fmt, locked_block="",
                      fact_based=False, historical=False, film_type=""):
    """Scene Design: 핵심 장면 15~18개 설계 (Show, don't tell)"""
    try:
        client = get_client()
        gns = core_data.get("goal_need_strategy", {})
        nd = core_data.get("narrative_drive", {})
        lp = core_data.get("logline_pack", {})
        chars = core_data.get("characters", []) + core_data.get("extended_characters", [])
        storyline = story_data.get("storyline", [])

        # v2.4.0: 시대극 자동 감지 컨텍스트 추출
        _locked_text, _idea_text = _get_period_scan_context({
            "genre": genre,
            "core_data": core_data or {},
            "locked_items": [locked_block] if locked_block else [],
        })
        system_prompt = P.build_system_scene_design(
            genre, fact_based=fact_based, historical=historical, film_type=film_type,
            locked_text=_locked_text, idea_text=_idea_text,
        )

        chars_simple = json.dumps(
            [{"name": c.get("name",""), "role": c.get("role","")} for c in chars],
            ensure_ascii=False
        )
        storyline_json = json.dumps(storyline, ensure_ascii=False)

        # ── 매력 설계도 추출 ──
        ad = core_data.get("attraction_design", {})
        scene_attraction_block = ""
        if ad:
            oh = ad.get("opening_hook", {})
            tp = ad.get("twist_point", {})
            wc = ad.get("water_cooler_moment", {})
            ee = ad.get("emotional_explosion", {})
            fd = ad.get("forbidden_directions", [])
            scene_attraction_block = f"""
[⚡ 매력 설계도 — 장면 설계 최우선 명령]
첫 장면 유형: {oh.get("type", "")}
첫 장면 (scene_no 1 반드시 이것으로): {oh.get("description", "")}
배반 포인트: {tp.get("betrayal", "")}
Water Cooler Moment (반드시 key_scenes 안에 포함): {wc.get("scene_or_setup", "")}
감정 폭발 장면: {ee.get("explosion_moment", "")}
절대 금지 방향: {" / ".join(fd)}
"""

        # ── 오프닝 전략 추출 (v2.2 신규) ──
        os_data = core_data.get("opening_strategy", {})
        opening_strategy_block = ""
        if os_data:
            opening_strategy_block = f"""
[🎬 오프닝 전략 — S#1 절대 명령 (v2.2)]
오프닝 타입: {os_data.get("opening_type", "")}
오프닝 의도: {os_data.get("opening_intent", "")}
도파민 포인트: {os_data.get("dopamine_point", "")}
1막 연결 방식: {os_data.get("opening_to_act1_link", "")}
훅 라인/이미지: {os_data.get("opening_hook_line", "")}
장르 DNA 체크: {os_data.get("genre_dna_check", "")}

★ S#1(scene_no 1)은 반드시 위 '오프닝 타입'에 부합하는 장면이어야 한다. ★
★ S#1의 dramatic_action, visual_direction, key_line에 '훅 라인/이미지'가 구체적으로 드러나야 한다. ★
★ S#1의 emotional_beat는 '도파민 포인트'에 명시된 감각(충격/웃음/긴장/경이/호기심/감정 울림)을 만드는 방향이어야 한다. ★
★ S#1을 '평범한 일상 소개' '풍경 묘사 후 인물 줌인' '주인공 배경 설명'으로 열면 실패다. 첫 장면에서 장르 DNA가 선언되어야 한다. ★
"""

        # ── BJND 씬 레벨 집행 블록 (v2.3 신규) — Strategy/Cost를 씬에 강제 반영 ──
        bjnd_scene_block = P.build_bjnd_scene_block(core_data)

        user_prompt = f"""[Core]
로그라인: {lp.get("washed","")}
Goal: {gns.get("goal","")} / Need: {gns.get("need","")} / Strategy: {gns.get("strategy","")}
서사동력: {nd.get("desire_origin","")}({nd.get("origin_detail","")}) → {nd.get("arc_direction","")} / 해결전략: {nd.get("resolution_strategy","")}
캐릭터: {chars_simple}
{scene_attraction_block}
{opening_strategy_block}
{bjnd_scene_block}
{locked_block}
[Storyline]
{storyline_json}

[JSON 스키마]
{P.SCENE_DESIGN_SCHEMA}

{P.SCENE_DESIGN_RULES}
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL, max_tokens=16000, temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        if response.stop_reason == "max_tokens":
            retry = user_prompt.replace("15~18개", "12~15개")
            response = client.messages.create(
                model=ANTHROPIC_MODEL, max_tokens=16000, temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": retry}]
            )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        st.session_state["last_scene_design_raw"] = txt
        return safe_json_loads(txt)
    except Exception as e:
        st.error(f"Scene Design 실패: {e}")
        raw = st.session_state.get("last_scene_design_raw", "")
        if raw:
            with st.expander("🔧 Scene Design Raw (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── 16비트 구조 정의 ───
def _get_series_act_mapping(fmt):
    """미니시리즈의 에피소드를 3막에 매핑"""
    bs = P.get_beat_structure(fmt)
    eps = list(bs.keys())
    n = len(eps)
    if n <= 3:
        return {1: eps[:1], 2: eps[1:2], 3: eps[2:]}
    elif n <= 6:
        return {1: eps[:2], 2: eps[2:4], 3: eps[4:]}
    else:  # 8화
        return {1: eps[:3], 2: eps[3:6], 3: eps[6:]}


def _build_b_story_context(core_data):
    """Core Build의 세계관/GNS에서 B-Story 컨텍스트 추출"""
    wb = core_data.get("world_build", {})
    gns = core_data.get("goal_need_strategy", {})
    parts = []
    # 시간축
    time_ctx = wb.get("time", wb.get("시간", ""))
    if time_ctx:
        parts.append(f"B-Story 시간축: {time_ctx}")
    # 공간/사회
    space_ctx = wb.get("space", wb.get("공간", ""))
    if space_ctx:
        parts.append(f"B-Story 공간: {space_ctx}")
    # 권력구조
    power_ctx = wb.get("power_structure", wb.get("권력구조", ""))
    if power_ctx:
        parts.append(f"권력구조: {power_ctx}")
    # Risk (실패 시 B-Story 영향)
    risk = gns.get("risk", "")
    if risk:
        parts.append(f"실패 시 B-Story 결과: {risk}")
    return "\n".join(parts) if parts else ""


# ─── API Call: Treatment Build (16비트 줄글) ───
def call_treatment_beats(core_data, story_data, scene_data, genre, fmt, act_number, locked_block="",
                          fact_based=False, historical=False, film_type="", research=None):
    """Treatment Build: 막별 비트 줄글 생성 — 영화/시리즈 자동 분기.
    
    [v2.3.8 추가 전파 필드]
    Core Build에서 설계했지만 Treatment에서 휘발되던 4개 카테고리를 전파:
      1. project_intent (theme + pitch + tone_manner) — 주제·톤 일관성 유지
      2. world_build (time/space/rules) — 시대 고증·세계관 일관성 (생성 단계)
      3. genre_expectation_check.weak_zones — Core Build 자가 진단 경고
      4. research.real_events (상위 3~5개) + existing_works (표절 방지) — 핍진성
    """
    try:
        client = get_client()
        gns = core_data.get("goal_need_strategy", {})
        nd = core_data.get("narrative_drive", {})
        lp = core_data.get("logline_pack", {})
        chars = core_data.get("characters", []) + core_data.get("extended_characters", [])
        syn = story_data.get("synopsis_1p", {})
        storyline = story_data.get("storyline", [])
        
        # v2.3.8 신규 — 휘발되던 필드 4종 추출
        project_intent = core_data.get("project_intent", {})
        world_build = core_data.get("world_build", {})
        genre_check = core_data.get("genre_expectation_check", {})

        is_series = P.is_series_format(fmt)

        # ── 비트 목록 구성 ──
        if is_series:
            act_ep_map = _get_series_act_mapping(fmt)
            bs = P.get_beat_structure(fmt)
            all_beats = []
            for ep_key in act_ep_map.get(act_number, []):
                for beat_tuple in bs.get(ep_key, []):
                    all_beats.append((beat_tuple[0], f"[{ep_key}] {beat_tuple[1]}", beat_tuple[2] if len(beat_tuple) > 2 else ""))
            beats = all_beats
        else:
            bs = P.BEAT_STRUCTURE_FILM
            beats = bs[act_number]

        act_labels = {1: "1막", 2: "2막", 3: "3막"}
        act_label = act_labels[act_number]

        chars_simple = json.dumps(
            [{"name": c.get("name",""), "role": c.get("role",""), "goal": c.get("goal",""), "flaw": c.get("flaw","")} for c in chars],
            ensure_ascii=False
        )

        scene_ref = ""
        if scene_data:
            scenes = scene_data.get("key_scenes", [])
            if scenes:
                scene_ref = f"\n[Scene Design 참고]\n{json.dumps(scenes, ensure_ascii=False)}"

        beat_list = "\n".join([f"Beat {b[0]}. {b[1]}" + (f" — {b[2]}" if len(b) > 2 and b[2] else "") for b in beats])

        # ── B-Story 컨텍스트 구성 ──
        b_story_context = _build_b_story_context(core_data)

        # ── 매력 설계도 추출 ──
        attraction_design = core_data.get("attraction_design", {})
        attraction_block = ""
        if attraction_design:
            oh = attraction_design.get("opening_hook", {})
            tp = attraction_design.get("twist_point", {})
            wc = attraction_design.get("water_cooler_moment", {})
            ee = attraction_design.get("emotional_explosion", {})
            fd = attraction_design.get("forbidden_directions", [])
            attraction_block = f"""
[⚡ 매력 설계도 — 최우선 명령. 반드시 반영하라]
첫 장면 유형: {oh.get("type", "")}
첫 장면: {oh.get("description", "")}
배반 포인트: {tp.get("betrayal", "")} (관객 예상: {tp.get("expected_direction", "")})
Water Cooler Moment: {wc.get("scene_or_setup", "")}
감정 억압 → 폭발: {ee.get("suppression", "")} → {ee.get("explosion_moment", "")}
절대 금지 방향: {" / ".join(fd)}
"""

        # ── 오프닝 전략 블록 (v2.2 신규) — 1막일 때만 Beat 1 강제 규칙 적용 ──
        os_data = core_data.get("opening_strategy", {})
        opening_strategy_block = ""
        if os_data and act_number == 1:
            opening_strategy_block = f"""
[🎬 오프닝 전략 — Beat 1 절대 명령 (v2.2)]
오프닝 타입: {os_data.get("opening_type", "")}
오프닝 의도: {os_data.get("opening_intent", "")}
도파민 포인트: {os_data.get("dopamine_point", "")}
1막 연결 방식: {os_data.get("opening_to_act1_link", "")}
훅 라인/이미지: {os_data.get("opening_hook_line", "")}
장르 DNA 체크: {os_data.get("genre_dna_check", "")}

★ Beat 1 (1막 첫 비트) 작성 규칙 — 절대 지킬 것 ★
1. 비트의 첫 3줄 안에 오프닝 타입에 해당하는 장면이 즉시 시작되어야 한다.
   - Action Drop: 이미 진행 중인 행동으로 시작
   - Cold Open: 본편과 다른 시점/장면으로 시작
   - Tease & Reveal: 수수께끼 이미지로 시작
   - In Media Res: 미래의 결정적 순간으로 시작
   - Character Reveal Action: 주인공의 정의적 행동으로 시작
   - Hook Dialogue: 강렬한 한 줄 대사로 시작
2. '훅 라인/이미지'는 Beat 1 narrative에 구체적으로 실제 장면으로 등장해야 한다.
3. '도파민 포인트'에 명시된 감각(충격/웃음/긴장/경이/호기심/감정 울림)이 Beat 1 안에서 최소 1회 터져야 한다.
4. 절대 금지 AI 오프닝 습관:
   ❌ '서울. 2024년 봄.' 같은 배경 설명 시작
   ❌ '어느 날 아침, 주인공은 눈을 떴다.' 일상 시작
   ❌ '오늘도 ○○은 평소처럼...' 관습 서술
   ❌ 주인공의 외형·직업·가족관계를 첫 3줄에 나열
   ❌ 풍경 묘사로 시작해서 인물로 줌인하는 구조
5. Beat 1의 마지막 문장은 Beat 2로 넘어가는 연결 장치가 되어야 한다(오프닝→1막 연결 방식 준수).
"""

        # ── 시스템 프롬프트 (fmt + b_story 전달) ──
        # v2.4.0: 시대극 자동 감지 컨텍스트 추출
        _locked_text, _idea_text = _get_period_scan_context({
            "genre": genre,
            "core_data": core_data or {},
            "locked_items": [locked_block] if locked_block else [],
        })
        system_prompt = P.build_system_treatment(genre, act_label, fmt=fmt, b_story_context=b_story_context,
                                                   fact_based=fact_based, historical=historical, film_type=film_type,
                                                   locked_text=_locked_text, idea_text=_idea_text)

        # ── 시리즈용 추가 정보 ──
        series_info = ""
        if is_series:
            ep_list = act_ep_map.get(act_number, [])
            series_info = f"\n[에피소드 구성] 이 {act_label}은 {', '.join(ep_list)}에 해당합니다. 각 에피소드의 마지막 비트는 반드시 클리프행어로 끝내세요.\n"

        # ── BJND 씬 레벨 집행 블록 (v2.3 신규) — 모든 막에 주입 (막별 Cost 단계 규칙 내장) ──
        bjnd_scene_block = P.build_bjnd_scene_block(core_data)

        # ─────────────────────────────────────────────
        # v2.3.8 신규 전파 블록 4종 — Core Build에서 휘발되던 필드 주입
        # ─────────────────────────────────────────────
        
        # [1] 기획의도 + 주제 + 톤앤매너 (project_intent 전파)
        project_intent_block = ""
        if project_intent:
            theme = project_intent.get("theme", "")
            pitch = project_intent.get("pitch", "")
            tone_manner = project_intent.get("tone_manner", [])
            if theme or pitch or tone_manner:
                tone_str = " / ".join(tone_manner) if tone_manner else ""
                project_intent_block = f"""
[🎯 기획의도 — 모든 비트가 수렴해야 할 주제]
주제: {theme}
엘리베이터 피치: {pitch}
톤앤매너: {tone_str}

★ 매 비트 작성 시 이 주제에서 이탈하지 말 것. 대사·행동·디테일 모두 주제를 향해 수렴.
★ 톤앤매너 키워드를 씬 분위기·대사 결·디테일 선택에 일관되게 반영.
"""
        
        # [2] 세계관 (world_build 전파) — 시대/공간/규칙
        world_build_block = ""
        if world_build:
            wb_time = world_build.get("time", "")
            wb_space = world_build.get("space", "")
            wb_rules = world_build.get("rules", "")
            wb_taboo = world_build.get("taboo", "")
            wb_visual = world_build.get("visual_keywords", [])
            if any([wb_time, wb_space, wb_rules]):
                visual_str = " / ".join(wb_visual) if wb_visual else ""
                world_build_block = f"""
[🌍 세계관 — 시대·공간·규칙 절대 준수]
시간 배경: {wb_time}
공간 배경: {wb_space}
세계관 규칙: {wb_rules}
금기/터부: {wb_taboo}
시각 키워드: {visual_str}

★ 위 시간 배경에 존재하지 않는 기술·제도·문화·언어를 Treatment에 포함하지 말 것.
  (예: 1980년대 설정인데 스마트폰·SNS·AI, 조선시대인데 사진·기차 등)
★ 세계관 규칙은 비트 전체에 일관되게 적용.
★ 금기가 있다면 그것이 파괴되는 순간이 긴장의 축이 되어야 함.
"""
        
        # [3] 장르 자가 진단 경고 (genre_expectation_check.weak_zones 전파)
        genre_warning_block = ""
        if genre_check:
            weak_zones = genre_check.get("weak_zones", [])
            climax_verdict = genre_check.get("climax_verdict", "")
            genre_diag = genre_check.get("genre_fun_diagnosis", "")
            if weak_zones or climax_verdict == "CLIMAX_FAIL":
                weak_str = "\n".join(f"  · {w}" for w in weak_zones) if weak_zones else "  · (없음)"
                genre_warning_block = f"""
[⚠️ 장르 자가 진단 경고 — Core Build에서 식별된 약점]
장르 재미 진단: {genre_diag}
예상 약점 구간:
{weak_str}
클라이맥스 판정: {climax_verdict}

★ 위 약점 구간은 Core Build가 스스로 식별한 위험 영역. Treatment 집필 시 이 구간을 특히 강하게 설계하라.
★ CLIMAX_FAIL 판정이 있으면 3막 마지막 비트를 장르 약속에 맞게 재설계하라.
  (예: 로맨틱 코미디 CLIMAX_FAIL이면 → 부녀 화해/가족 서사 금지, 반드시 로맨스 완성 씬)
"""
        
        # [4] v2.3.8 재설계 — research_applied (Core Build 선별) 우선 + 원본 research 보조
        # Mr. MOON 원칙: "리서치 내용 전체를 받을 필요는 없고. 설정된 캐릭터에 사용할 수 있는 것만 응용"
        research_block_treatment = ""
        
        # (A) Core Build가 이미 선별한 research_applied를 최우선으로 전달
        research_applied = core_data.get("research_applied", {}) if core_data else {}
        if research_applied:
            refs = research_applied.get("references_used", [])
            anchors = research_applied.get("verisimilitude_anchors", [])
            absorption = research_applied.get("research_absorption_note", "")
            
            # references_used를 간결하게 포맷
            refs_lines = []
            for r in refs[:6]:
                src_title = r.get("source_title", "")
                applied_to = r.get("applied_to", "")
                how = r.get("how_applied", "")
                char_name = r.get("character_name", "")
                char_suffix = f" [→ {char_name}]" if char_name else ""
                refs_lines.append(f"  · [{applied_to}] {src_title}: {how}{char_suffix}")
            refs_str = "\n".join(refs_lines) if refs_lines else "  · (Core Build에서 선별한 참조 없음)"
            
            anchors_lines = [f"  {i+1}. {a}" for i, a in enumerate(anchors[:5])]
            anchors_str = "\n".join(anchors_lines) if anchors_lines else "  (없음)"
            
            if refs_lines or anchors_lines or absorption:
                research_block_treatment = f"""
[📚 리서치 선별 응용 — Core Build가 이미 이 작품에 녹인 것만 전달]
작가 흡수 노트: {absorption}

[이 작품에 응용된 리서치 요소 — 매 비트에서 유지]
{refs_str}

[핍진성 앵커 — Treatment 집필 시 반드시 유지할 현실 기반 디테일]
{anchors_str}

★ 위 요소들은 Core Build가 '이 작품의 캐릭터·설정·사건에 실제로 응용된 것'만 선별한 결과.
★ 응용된 요소는 해당 캐릭터·장면에서 구체 디테일로 드러나야 한다. 추상적 언급 금지.
★ 핍진성 앵커는 Writer Engine까지 전달될 핵심이므로 Treatment에서 휘발시키지 말 것.
★ 리서치에 있었으나 research_applied에 없는 요소는 이 작품에 해당 안 됨 — 끌어다 쓰지 말 것.
"""
        
        # (B) 원본 research는 '표절 회피 레퍼런스'로만 보조 사용 (상위 3개 existing_works만)
        if research and not research_applied:
            # research_applied가 없는 경우에만 원본 research 최소한 참고 (구버전 프로젝트 호환)
            existing_works = research.get("existing_works", [])
            existing_titles = []
            for w in existing_works[:5]:
                t = w.get("title", "")
                y = w.get("year", "")
                if t:
                    existing_titles.append(f"{t}({y})" if y else t)
            existing_str = ", ".join(existing_titles) if existing_titles else "(없음)"
            
            if existing_titles:
                research_block_treatment = f"""
[📚 리서치 — 표절 회피 참조]
유사 작품: {existing_str}
★ 위 작품들과 유사한 설정·구조·클라이맥스를 피하라. 이 작품만의 차별점을 유지.
※ Core Build의 research_applied가 비어있어 최소 참고만 제공. 다음 재생성 시 research_applied 작성 권장.
"""

        user_prompt = f"""[작품 정보]
로그라인: {lp.get("washed","")}
장르: {genre} / 포맷: {fmt}
Goal: {gns.get("goal","")} / Need: {gns.get("need","")} / Strategy: {gns.get("strategy","")}
서사동력: {nd.get("desire_origin","")}({nd.get("origin_detail","")}) → {nd.get("arc_direction","")} / 해결전략: {nd.get("resolution_strategy","")}
캐릭터: {chars_simple}
{locked_block}
{series_info}
{project_intent_block}
{world_build_block}
{genre_warning_block}
{research_block_treatment}
{attraction_block}
{opening_strategy_block}
{bjnd_scene_block}
[Synopsis]
{json.dumps(syn, ensure_ascii=False)}

[Storyline]
{json.dumps(storyline, ensure_ascii=False)}
{scene_ref}

[{act_label} — 작성할 비트]
{beat_list}

[JSON 스키마]
{P.TREATMENT_BEAT_SCHEMA_TEMPLATE.format(act_number=act_number)}

{P.TREATMENT_BEAT_RULES_TEMPLATE.format(beat_count=len(beats))}
"""

        # ─── v2.5.4: 스트리밍 호출 전환 + 2단계 자동 재시도 ───
        # ─── v2.6.4: max_tokens 16000 → 24000 (시리즈 6비트 출력량 대응, v2.5.1 캐릭터 바이블과 동일 조치) ───
        with client.messages.stream(
            model=ANTHROPIC_MODEL_OPUS, max_tokens=24000, temperature=0.4,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        ) as stream:
            response = stream.get_final_message()
        if response.stop_reason == "max_tokens":
            # v2.6.4: 축소 프롬프트를 user_prompt 자체에 반영 — 이후 JSON 파싱 재시도도
            # 축소된 프롬프트를 사용하게 함 (기존에는 재시도가 원래 긴 프롬프트로 회귀해
            # 절단이 원인일 경우 재시도가 구조적으로 성공 불가능했음)
            st.warning(f"⚠️ Treatment {act_label} 출력 절단(max_tokens) — 분량 축소 후 재시도 중...")
            user_prompt = user_prompt.replace("1500~2500자", "1200~1800자")
            with client.messages.stream(
                model=ANTHROPIC_MODEL_OPUS, max_tokens=24000, temperature=0.4,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            ) as stream:
                response = stream.get_final_message()
            if response.stop_reason == "max_tokens":
                st.warning(
                    f"⚠️ Treatment {act_label} 분량 축소 후에도 출력 절단 지속 — "
                    f"이후 파싱 실패는 JSON 문법이 아닌 출력량 초과가 원인입니다. "
                    f"비트 수·narrative 분량 스펙 조정이 필요합니다."
                )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        st.session_state[f"last_treatment_act{act_number}_raw"] = txt

        # JSON 파싱 시도 — 실패 시 자동 재시도 2회 (v2.5.4)
        # 1차 실패 → temperature 0.2로 재시도 + 강화 룰 (소프트)
        # 2차 실패 → temperature 0.05 + JSON_OUTPUT_RULES_STRICT 주입 (하드)
        try:
            return safe_json_loads(txt)
        except json.JSONDecodeError:
            st.warning(f"⚠️ Treatment {act_label} JSON 파싱 실패 — 1차 재시도 중 (temp 0.2)...")
            # 1차 재시도: 제어 문자 금지 강조
            retry_system_1 = system_prompt + "\n\n★ 최우선 규칙: 반드시 유효한 JSON만 출력. narrative 안에 줄바꿈(\\n) 절대 금지. 탭(\\t) 절대 금지. 캐리지리턴(\\r) 절대 금지. 대사 인용은 작은따옴표만. 후행 쉼표 금지. 코드 펜스(```) 금지. 출력 시작은 { 끝은 }. ★"
            with client.messages.stream(
                model=ANTHROPIC_MODEL_OPUS, max_tokens=24000, temperature=0.2,
                system=retry_system_1,
                messages=[{"role": "user", "content": user_prompt}]
            ) as stream:
                response2 = stream.get_final_message()
            txt2 = "".join(b.text for b in response2.content if hasattr(b, "text")).strip()
            st.session_state[f"last_treatment_act{act_number}_raw"] = txt2

            try:
                return safe_json_loads(txt2)
            except json.JSONDecodeError:
                st.warning(f"⚠️ Treatment {act_label} 1차 재시도도 실패 — 2차 재시도 중 (temp 0.05, STRICT 룰 주입)...")
                # 2차 재시도: temperature 최저 + STRICT 룰 주입
                retry_system_2 = system_prompt + "\n\n" + P.JSON_OUTPUT_RULES_STRICT + "\n\n★ 절대 위반 금지: 단일 JSON 객체. narrative 안에 줄바꿈/탭/캐리지리턴 모두 금지. 첫 문자는 { 마지막 문자는 }. 대사 안의 인용은 작은따옴표만. 후행 쉼표 금지. 코드 펜스 금지. ★"
                with client.messages.stream(
                    model=ANTHROPIC_MODEL_OPUS, max_tokens=24000, temperature=0.05,
                    system=retry_system_2,
                    messages=[{"role": "user", "content": user_prompt}]
                ) as stream:
                    response3 = stream.get_final_message()
                txt3 = "".join(b.text for b in response3.content if hasattr(b, "text")).strip()
                st.session_state[f"last_treatment_act{act_number}_raw"] = txt3
                # 마지막 시도: 제어 문자 사후 정리 후 파싱 시도 (v2.5.4 안전망)
                try:
                    return safe_json_loads(txt3)
                except json.JSONDecodeError:
                    # 제어 문자 사후 정리 — 마지막 안전망
                    import re
                    # JSON 문자열 안의 제어 문자(\n, \r, \t)를 공백으로 치환
                    # 단, JSON 구조의 줄바꿈은 보존하기 위해 "..." 안의 것만 처리
                    def _clean_control_chars(match):
                        s = match.group(0)
                        # 큰따옴표 안의 제어 문자를 공백으로 치환
                        return re.sub(r'[\n\r\t]+', ' ', s)
                    txt4 = re.sub(r'"(?:[^"\\]|\\.)*"', _clean_control_chars, txt3)
                    st.session_state[f"last_treatment_act{act_number}_raw"] = txt4
                    return safe_json_loads(txt4)

    except Exception as e:
        st.error(f"Treatment {act_label} 실패: {e}")
        raw = st.session_state.get(f"last_treatment_act{act_number}_raw", "")
        if raw:
            with st.expander(f"🔧 Treatment {act_label} Raw (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ═══════════════════════════════════════════════════
# v2.6.0 — 8점 진입 사전 방지 후처리 4종
# Treatment Build 완료 후 비트 JSON에서 신규 필드를 추출하여
# Writer Engine v3.7.1 인계용 4블록을 자동 생성한다.
#
# 출력 블록:
#   - cycle_design (시퀀스 사이클 분석)
#   - antagonist_actions (적대자별 비트 매핑)
#   - setup_payoff_table (회수 상태 추적)
#   - physical_cost_plan (4단계 비트 매핑)
#
# 하위 호환성: 모든 함수는 .get() 기반 fallback 사용.
# 구버전 시드(v2.5.x 이전)에 신규 필드가 없으면 빈 결과 반환.
# ═══════════════════════════════════════════════════

def _collect_all_beats(act1: dict, act2: dict, act3: dict) -> list:
    """3개 막의 비트를 단일 리스트로 합친다 (비트 번호 순)."""
    all_beats = []
    for act_data in [act1, act2, act3]:
        if act_data and isinstance(act_data, dict):
            beats = act_data.get("beats", [])
            if isinstance(beats, list):
                all_beats.extend(beats)
    # 비트 번호 기준 정렬 (안전망)
    try:
        all_beats.sort(key=lambda b: int(b.get("beat_no", 0)) if b.get("beat_no") not in (None, "") else 0)
    except Exception:
        pass
    return all_beats


def build_cycle_design_block(act1: dict, act2: dict, act3: dict) -> dict:
    """v2.6.0 ① 시퀀스 사이클 사전 설계 — Beat 6~12 action_cycle 분석.

    출력:
        {
          "beats_6_to_12": [
            {"beat": 6, "cycle": ["저택", "봉인실", "카페", "저택"], "function": "..."},
            ...
          ],
          "external_helper_meetings": [
            {"helper": "Hendra", "location": "카페", "occurrences": [10], "form": "대면"},
            ...
          ],
          "warnings": ["같은 사이클 패턴 3회 반복 감지: ...", ...]
        }
    """
    all_beats = _collect_all_beats(act1, act2, act3)
    result = {
        "beats_6_to_12": [],
        "external_helper_meetings": [],
        "warnings": []
    }

    # Beat 6~12 action_cycle 수집
    cycle_patterns = {}  # 패턴 빈도 카운트
    for beat in all_beats:
        try:
            beat_no = int(beat.get("beat_no", 0))
        except (ValueError, TypeError):
            continue
        if not (6 <= beat_no <= 12):
            continue
        cycle_str = beat.get("action_cycle", "") or ""
        if not cycle_str:
            continue
        # 공간 시퀀스 파싱 (→ 또는 -> 구분자)
        cycle_list = [s.strip() for s in cycle_str.replace("->", "→").split("→") if s.strip()]
        result["beats_6_to_12"].append({
            "beat": beat_no,
            "cycle": cycle_list,
            "function": beat.get("event_summary", "") or beat.get("beat_name", "")
        })
        # 패턴 빈도 카운트
        pattern_key = " → ".join(cycle_list)
        if pattern_key:
            cycle_patterns[pattern_key] = cycle_patterns.get(pattern_key, 0) + 1

    # 사이클 반복 경고
    for pattern, count in cycle_patterns.items():
        if count >= 3:
            result["warnings"].append(
                f"같은 사이클 패턴 {count}회 반복 감지: '{pattern}' — 변주 4기법 적용 필요 "
                f"(순서 역전 / 압축 / 차단 / 침범)"
            )

    return result


def build_antagonist_actions_block(act1: dict, act2: dict, act3: dict,
                                    char_bible: dict = None) -> dict:
    """v2.6.0 ② 적대자 능동성 설계 — 비트별 적대자 행위 매핑.

    출력:
        {
          "Reza": {
            "beat_6": "문서 파기",
            "beat_8": "Maya 감시 지시",
            "beat_10": "직접 위협"
          },
          "warnings": [...]
        }
    """
    all_beats = _collect_all_beats(act1, act2, act3)
    result = {"warnings": []}

    # 캐릭터 바이블에서 적대자 이름 추출 (가능하면)
    antagonist_names = []
    if char_bible and isinstance(char_bible, dict):
        chars = char_bible.get("characters", []) if isinstance(char_bible.get("characters"), list) else []
        for c in chars:
            if isinstance(c, dict) and c.get("role") == "antagonist":
                name = c.get("name", "")
                if name:
                    antagonist_names.append(name)

    # 비트별 antagonist_active_action 수집 (이름 매칭 불가 시 단일 antagonist로 처리)
    has_passive_only = []
    for beat in all_beats:
        try:
            beat_no = int(beat.get("beat_no", 0))
        except (ValueError, TypeError):
            continue
        action = beat.get("antagonist_active_action", "") or ""
        if not action:
            continue
        # 적대자 이름 매칭 시도 (없으면 default antagonist)
        matched_name = None
        for name in antagonist_names:
            if name and name in action:
                matched_name = name
                break
        target = matched_name or "antagonist"
        if target not in result:
            result[target] = {}
        result[target][f"beat_{beat_no}"] = action

        # 수동 회피만으로 처리된 비트 감지
        passive_keywords = ["침묵", "외면", "돌아보지 않", "대답하지 않", "자리를 뜬"]
        is_passive_only = (
            any(kw in action for kw in passive_keywords)
            and not any(active_kw in action for active_kw in [
                "파기", "지시", "위협", "차단", "감시", "조작", "공격",
                "함정", "협박", "회유", "매수", "결성", "유도", "압박"
            ])
        )
        if is_passive_only:
            has_passive_only.append(beat_no)

    if has_passive_only:
        result["warnings"].append(
            f"수동 회피만으로 처리된 적대자 비트 감지: Beat {has_passive_only} — "
            f"능동 행위(파기·지시·위협 등)로 교체 필요"
        )

    return result


def build_setup_payoff_table(act1: dict, act2: dict, act3: dict) -> list:
    """v2.6.0 ③ Setup-Payoff 의도 배치 — 도입·회수 추적 테이블.

    출력:
        [
          {"item": "Pak Wiranto", "setup_beat": 3, "payoff_beat": 10, "status": "회수 완료"},
          {"item": "검은 세단", "setup_beat": 8, "payoff_beat": None, "status": "회수 필요"},
          ...
        ]
    """
    all_beats = _collect_all_beats(act1, act2, act3)
    setup_map = {}  # item -> setup_beat
    payoff_map = {}  # item -> payoff_beat

    for beat in all_beats:
        try:
            beat_no = int(beat.get("beat_no", 0))
        except (ValueError, TypeError):
            continue
        sp_id = beat.get("setup_payoff_id", "") or ""
        if not sp_id:
            continue
        # 복수 항목 처리 (쉼표 구분)
        for entry in sp_id.split(","):
            entry = entry.strip()
            if ":" not in entry:
                continue
            kind, item = entry.split(":", 1)
            kind = kind.strip().upper()
            item = item.strip()
            if not item:
                continue
            if kind == "SETUP":
                if item not in setup_map:  # 첫 도입 비트만 기록
                    setup_map[item] = beat_no
            elif kind == "PAYOFF":
                if item not in payoff_map:  # 첫 회수 비트만 기록
                    payoff_map[item] = beat_no

    # 통합 테이블 생성
    all_items = set(setup_map.keys()) | set(payoff_map.keys())
    table = []
    for item in sorted(all_items):
        setup_beat = setup_map.get(item)
        payoff_beat = payoff_map.get(item)
        if setup_beat and payoff_beat:
            status = "회수 완료"
        elif setup_beat and not payoff_beat:
            status = "회수 필요"
        elif not setup_beat and payoff_beat:
            status = "Plant 없는 Payoff (데우스 엑스 마키나 위험)"
        else:
            continue
        table.append({
            "item": item,
            "setup_beat": setup_beat,
            "payoff_beat": payoff_beat,
            "status": status
        })
    return table


def build_physical_cost_plan_block(act1: dict, act2: dict, act3: dict,
                                    char_bible: dict = None) -> dict:
    """v2.6.0 ④ 물리적 대가 4단계 계획 — 주인공 카드 + 비트별 단계 매핑.

    출력:
        {
          "stage_1": {"beats": "1~5", "cost": "..."},
          "stage_2": {"beats": "6~8", "cost": "..."},
          "stage_3": {"beats": "9~11", "cost": "..."},
          "stage_4": {"beats": "12~", "cost": "..."},
          "beat_stages": [{"beat": 1, "stage": 1, "description": "..."}, ...],
          "warnings": [...]
        }
    """
    all_beats = _collect_all_beats(act1, act2, act3)
    result = {
        "stage_1": {"beats": "1~5", "cost": ""},
        "stage_2": {"beats": "6~8", "cost": ""},
        "stage_3": {"beats": "9~11", "cost": ""},
        "stage_4": {"beats": "12~", "cost": ""},
        "beat_stages": [],
        "warnings": []
    }

    # 캐릭터 바이블에서 주인공의 physical_cost_plan 추출
    if char_bible and isinstance(char_bible, dict):
        chars = char_bible.get("characters", []) if isinstance(char_bible.get("characters"), list) else []
        for c in chars:
            if isinstance(c, dict) and c.get("role") == "protagonist":
                plan_str = c.get("physical_cost_plan", "") or ""
                if plan_str:
                    # 'stage_1 (beats 1-5): ... / stage_2 (beats 6-8): ...' 파싱
                    import re
                    # 각 단계 패턴 추출
                    for stage_num in [1, 2, 3, 4]:
                        pattern = rf"stage_{stage_num}\s*\([^)]*\):\s*([^/]+?)(?=\s*/\s*stage_|\s*$)"
                        match = re.search(pattern, plan_str)
                        if match:
                            result[f"stage_{stage_num}"]["cost"] = match.group(1).strip()
                break

    # 비트별 단계 수집
    prev_stage = 0
    has_jump = []
    has_reset = []
    for beat in all_beats:
        try:
            beat_no = int(beat.get("beat_no", 0))
        except (ValueError, TypeError):
            continue
        try:
            stage = int(beat.get("physical_cost_stage", 0))
        except (ValueError, TypeError):
            stage = 0
        description = beat.get("physical_cost_description", "") or ""
        result["beat_stages"].append({
            "beat": beat_no,
            "stage": stage,
            "description": description
        })
        # 단계 점프 감지 (1 → 3 같은 비정상 격상)
        if prev_stage > 0 and stage > prev_stage + 1:
            has_jump.append((prev_stage, stage, beat_no))
        # 단계 리셋 감지 (대가 진행 후 0으로 회귀)
        if prev_stage > 0 and stage == 0 and beat_no >= 6:
            has_reset.append(beat_no)
        if stage > 0:
            prev_stage = max(prev_stage, stage)

    # 경고 생성
    if has_jump:
        jumps_str = ", ".join([f"Beat {b}: {a}→{c}" for a, c, b in has_jump])
        result["warnings"].append(
            f"단계 점프 감지 ({jumps_str}) — 1→2→3→4 순서대로 격상되어야 함"
        )
    if has_reset:
        result["warnings"].append(
            f"단계 리셋 의심 (Beat {has_reset}): 대가 진행 후 stage=0으로 회귀 — "
            f"이전 단계 흔적은 사라지지 않아야 함"
        )
    if prev_stage < 4:
        result["warnings"].append(
            f"최종 단계가 {prev_stage}단계 — 4단계까지 도달해야 클라이맥스의 무게가 생김"
        )

    return result


def build_writer_engine_handoff_v26(act1: dict, act2: dict, act3: dict,
                                     char_bible: dict = None) -> dict:
    """v2.6.0 통합 후처리 — Writer Engine v3.7.1 인계용 4블록 산출.

    Treatment Build 완료 후 호출. 결과는 프로젝트 JSON의
    treatment.writer_handoff_v26 필드로 저장된다.

    Args:
        act1, act2, act3: Treatment Build 3개 막 출력
        char_bible: Character Bible (적대자·주인공 이름 매칭용, 없으면 fallback)

    Returns:
        {
          "cycle_design": {...},
          "antagonist_actions": {...},
          "setup_payoff_table": [...],
          "physical_cost_plan": {...},
          "version": "v2.6.0"
        }
    """
    return {
        "cycle_design": build_cycle_design_block(act1, act2, act3),
        "antagonist_actions": build_antagonist_actions_block(act1, act2, act3, char_bible),
        "setup_payoff_table": build_setup_payoff_table(act1, act2, act3),
        "physical_cost_plan": build_physical_cost_plan_block(act1, act2, act3, char_bible),
        "version": "v2.6.0"
    }


def call_treatment_meta(act1, act2, act3, core_data):
    """Treatment 감정곡선 + 감독포인트 + 투자자요약"""
    try:
        client = get_client()
        all_beats = []
        for act_data in [act1, act2, act3]:
            if act_data:
                for b in act_data.get("beats", []):
                    all_beats.append(f"Beat {b.get('beat_no','')}. {b.get('beat_name','')}")

        # v2.1: 캐릭터 목록 추출 (이름 교차검증용)
        chars = core_data.get("characters", []) + core_data.get("extended_characters", [])
        char_registry = []
        for c in chars:
            name = c.get("name", "")
            role = c.get("role", "")
            age = c.get("age", "")
            if name:
                char_registry.append(f"{name}({age}, {role})")
        char_registry_str = " / ".join(char_registry) if char_registry else "(캐릭터 정보 없음)"

        response = client.messages.create(
            model=ANTHROPIC_MODEL, max_tokens=2000, temperature=0.3,
            system=P.SYSTEM_TREATMENT_META,
            messages=[{"role": "user", "content": f"""[트리트먼트 비트 목록]
{json.dumps(all_beats, ensure_ascii=False)}

[로그라인] {core_data.get("logline_pack",{}).get("washed","")}

[★ 등장 캐릭터 레지스트리 — 감독 포인트에서 이름을 쓸 때 반드시 이 목록의 이름만 사용할 것]
{char_registry_str}

[JSON 스키마]
{{
  "emotion_curve": [
    {{"point": "Beat 라벨", "tension": 0, "emotion": "감정"}}
  ],
  "director_notes": ["감독용 포인트 1", "감독용 포인트 2", "감독용 포인트 3"],
  "investor_summary": "투자자용 요약 3~4문장"
}}

규칙:
- emotion_curve 16개 포인트. tension 1~10. director_notes 3개.
- ★ director_notes에 캐릭터 이름을 언급할 때 반드시 위 [등장 캐릭터 레지스트리]의 이름만 사용하라.
- ★ 캐릭터의 역할(주인공/적대자/조력자 등)과 나이에 맞지 않는 연출 지시를 절대 하지 마라.
  예: 9세 아이에게 '구조적 폭탄', '위협감', '주도권' 같은 어른 연출 지시를 붙이면 안 된다.
- ★ 감독 포인트에서 특정 비트의 연출을 지시할 때는 해당 비트의 실제 주체(누가 그 행동을 하는가)와
  일치하는 이름을 써라. 비트 이름에서 임의로 인물명을 추출하면 안 된다.
- ★ 클라이맥스 질문의 주체가 누구인지(주인공인지, 적대자인지, 조력자인지) 반드시 확인한 후 이름을 지정하라.
"""}]
        )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        return safe_json_loads(txt)
    except Exception as e:
        st.error(f"Treatment 메타 생성 실패: {e}")
        return None


def call_treatment_gate(treatment_data, core_data=None, genre=""):
    """Gate E: Treatment Gate 채점 — v2.3.6 강화판.
    
    이전 문제: beat_summary에 글자 수(chars)만 전달. 실제 내용 미검증.
    v2.3.6: 각 비트의 narrative 내용 요약 + 장르 + Core Build 참조를 전달하여
           장르 기대 충족, 엔딩 정합, 논리 일관성을 실제로 검증.
    """
    try:
        client = get_client()
        
        # v2.3.6: 실제 narrative 내용도 전달 (압축 요약)
        beat_details = []
        for act_key in ["act1", "act2", "act3"]:
            act_data = treatment_data.get(act_key, {})
            if act_data:
                for b in act_data.get("beats", []):
                    narrative = b.get("narrative", "")
                    # 각 비트 narrative를 500자로 압축 (앞 400자 + 뒤 100자)
                    if len(narrative) > 500:
                        narrative_compact = narrative[:400] + " ... [중략] ... " + narrative[-100:]
                    else:
                        narrative_compact = narrative
                    beat_details.append({
                        "beat_no": b.get("beat_no"),
                        "beat_name": b.get("beat_name"),
                        "length": len(narrative),
                        "story_position": b.get("story_position", ""),  # v2.6.5: 기승전결 좌표
                        "narrative_summary": narrative_compact,
                    })
        
        # v2.3.6: Core Build 핵심 정보 전달 (엔딩 정합 검증용)
        # v2.3.7: world_build.time 등 시대 고증 검증용 정보 추가
        core_context = ""
        if core_data:
            gns = core_data.get("goal_need_strategy", {})
            lp = core_data.get("logline_pack", {})
            wb = core_data.get("world_build", {})
            ending_payoff = gns.get("ending_payoff", "")
            strategy = gns.get("strategy", "")
            
            # 시대/공간 정보 추출
            time_setting = wb.get("time", "")
            space_setting = wb.get("space", "")
            rules = wb.get("rules", "")
            
            core_context = f"""
[Core Build 참조 — 이 Treatment가 일관되게 구현해야 할 원본 설계]
장르: {genre}
로그라인: {lp.get("washed", "")}
주인공 Strategy: {strategy}
Ending Payoff: {ending_payoff}

[★ 세계관·시대 설정 — 시대 고증 검증용 ★]
시대/시간: {time_setting}
공간/장소: {space_setting}
세계관 규칙: {rules}

위 시대에 존재하지 않는 요소가 Treatment에 포함되었는지 반드시 확인하라.
(예: 1980년대 설정인데 스마트폰/SNS/AI, 1970년대인데 PC, 조선시대인데 사진기 등)
"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL, max_tokens=2500, temperature=0.2,
            system=P.SYSTEM_TREATMENT_GATE,
            messages=[{"role": "user", "content": f"""{core_context}
[Treatment 비트 구성 — 실제 내용 요약]
{json.dumps(beat_details, ensure_ascii=False)}

총 {len(beat_details)}개 비트.

[JSON 스키마]
{{
  "gate_e_treatment": {{
    "cinematic_reading": 0.0,
    "scene_emotion_match": 0.0,
    "beat_completeness": 0.0,
    "screenplay_ready": 0.0,
    "genre_expectation_alignment": 0.0,
    "ending_coherence": 0.0,
    "logic_consistency": 0.0,
    "period_consistency": 0.0,
    "average": 0.0,
    "genre_check_feedback": "장르 체크리스트 기준 충족 여부 1~2문장",
    "ending_check_feedback": "Core Build의 Ending Payoff와 실제 엔딩 비트의 정합성 1문장",
    "logic_check_feedback": "논리 비약/세계관 일관성 이슈가 있으면 구체 비트 번호와 함께 1~2문장",
    "period_check_feedback": "시대 고증 오류(작품 시대에 없던 기술/제도/문화 등) 구체 비트 번호와 함께 1~2문장 (없으면 '이슈 없음')",
    "feedback": "Gate E 종합 피드백 1문장",
    "critical_issues": ["문제가 있는 비트 번호와 짧은 진단 리스트 (없으면 빈 배열)"]
  }}
}}
규칙: average = 8항목 평균 (소수점 1자리).
특히 genre_expectation_alignment, ending_coherence, logic_consistency, period_consistency는 
Core Build 설계와 Treatment 실제 구현의 일치도를 엄격 평가."""}]
        )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        return safe_json_loads(txt)
    except Exception as e:
        st.error(f"Gate E 실패: {e}")
        return None


# ─── API Call: Tone Document ───
def call_tone_document(core_data, structure_data, scene_data, treatment_data, char_bible, genre, fmt, locked_block="",
                        fact_based=False, historical=False, film_type=""):
    """톤 & 연출 문서 — Writer Engine의 스타일 가이드"""
    try:
        client = get_client()
        lp = core_data.get("logline_pack", {})
        gns = core_data.get("goal_need_strategy", {})
        nd = core_data.get("narrative_drive", {})
        wb = core_data.get("world_build", {})

        # 캐릭터 이름/역할만 추출
        char_names = []
        if char_bible:
            for c in char_bible.get("characters", []):
                char_names.append(f"{c.get('name','')}({c.get('role','')})")
        char_str = ", ".join(char_names)

        # Treatment 요약
        treatment_summary = ""
        for act_key in ["act1", "act2", "act3"]:
            act = treatment_data.get(act_key, {})
            if act:
                for b in act.get("beats", []):
                    treatment_summary += f"Beat {b.get('beat_no','')}: {b.get('beat_name','')}. "

        # v2.4.0: 시대극 자동 감지 컨텍스트 추출
        _locked_text, _idea_text = _get_period_scan_context({
            "genre": genre,
            "core_data": core_data or {},
            "locked_items": [locked_block] if locked_block else [],
        })
        system_prompt = P.build_system_tone_document(genre, fmt,
                                                       fact_based=fact_based, historical=historical, film_type=film_type,
                                                       locked_text=_locked_text, idea_text=_idea_text)

        user_prompt = f"""[로그라인]
{lp.get("washed","")}

[캐릭터]
{char_str}

[세계관]
{json.dumps(wb, ensure_ascii=False)}

[Treatment 비트 구성]
{treatment_summary}
{locked_block}

[JSON 스키마]
{P.TONE_DOC_SCHEMA}"""

        response = client.messages.create(
            model=ANTHROPIC_MODEL_OPUS, max_tokens=16000, temperature=0.3,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        if response.stop_reason == "max_tokens":
            # 분량 줄여서 재시도
            retry_prompt = user_prompt.replace(
                "카메라 철학 2~3문장", "카메라 철학 1~2문장"
            ).replace(
                "이 작품에서 절대 하지 말아야 할 연출/톤/대사 규칙 5개",
                "이 작품에서 절대 하지 말아야 할 규칙 3개"
            )
            response = client.messages.create(
                model=ANTHROPIC_MODEL_OPUS, max_tokens=16000, temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": retry_prompt}]
            )
        txt = "".join(b.text for b in response.content if hasattr(b, "text")).strip()
        st.session_state["last_tone_doc_raw"] = txt

        # JSON 파싱 시도 — 실패 시 자동 재시도 1회
        try:
            return safe_json_loads(txt)
        except json.JSONDecodeError:
            st.warning("⚠️ Tone Document JSON 파싱 실패 — 자동 재시도 중...")
            retry_system = system_prompt + "\n\n★ 최우선: 반드시 유효한 JSON만 출력. 따옴표는 작은따옴표만. 줄바꿈·역슬래시 금지. ★"
            response2 = client.messages.create(
                model=ANTHROPIC_MODEL_OPUS, max_tokens=16000, temperature=0.2,
                system=retry_system,
                messages=[{"role": "user", "content": user_prompt}]
            )
            txt2 = "".join(b.text for b in response2.content if hasattr(b, "text")).strip()
            st.session_state["last_tone_doc_raw"] = txt2
            return safe_json_loads(txt2)

    except Exception as e:
        st.error(f"Tone Document 생성 실패: {e}")
        raw = st.session_state.get("last_tone_doc_raw", "")
        if raw:
            with st.expander("🔧 Tone Document Raw (디버그)"):
                st.text_area("Raw", raw, height=400)
        return None


# ─── DOCX 생성 ───
def generate_docx(project):
    """기획개발보고서 DOCX 생성 — BLUE JEANS 기획서 스타일"""
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor, Cm, Emu
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn, nsdecls
    from docx.oxml import parse_xml
    import io

    NAVY = RGBColor(0x19, 0x19, 0x70)
    YELLOW = RGBColor(0xFF, 0xCB, 0x05)
    DIM = RGBColor(0x88, 0x88, 0x99)
    BLACK = RGBColor(0x1A, 0x1A, 0x2E)
    WHITE = RGBColor(0xFF, 0xFF, 0xFF)

    doc = Document()

    # ── 기본 스타일 ──
    style = doc.styles['Normal']
    style.font.name = 'Pretendard'
    style.font.size = Pt(10)
    style.font.color.rgb = BLACK
    style.paragraph_format.line_spacing = 1.4
    style.paragraph_format.space_after = Pt(4)

    # 페이지 여백
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.8)
        section.right_margin = Cm(2.8)

    # ── 헬퍼 함수 ──
    def add_yellow_header(kr_text, en_text=""):
        """노란 하이라이트 섹션 헤더 (한글 + ENGLISH 병기)"""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(10)
        # 노란 배경 셰이딩
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFCB05" w:val="clear"/>')
        p.paragraph_format.element.get_or_add_pPr().append(shading)
        # 한글
        run_kr = p.add_run(f"  {kr_text}")
        run_kr.font.size = Pt(13)
        run_kr.font.bold = True
        run_kr.font.color.rgb = NAVY
        run_kr.font.name = 'Pretendard'
        # ENGLISH
        if en_text:
            run_en = p.add_run(f"  {en_text}")
            run_en.font.size = Pt(9)
            run_en.font.bold = True
            run_en.font.color.rgb = NAVY
            run_en.font.name = 'Pretendard'
        return p

    def add_sub_header(text):
        """서브 헤더 (네이비 좌측 볼드)"""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        run = p.add_run(text)
        run.font.size = Pt(11)
        run.font.bold = True
        run.font.color.rgb = NAVY
        return p

    def add_body(text, size=10):
        """본문 텍스트"""
        if not text:
            return
        p = doc.add_paragraph()
        run = p.add_run(str(text))
        run.font.size = Pt(size)
        run.font.color.rgb = BLACK
        p.paragraph_format.line_spacing = 1.5
        return p

    def add_labeled(label, text, bold_label=True):
        """라벨 + 텍스트"""
        if not text:
            return
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(3)
        run_l = p.add_run(f"[{label}]  ")
        run_l.font.size = Pt(9)
        run_l.font.bold = bold_label
        run_l.font.color.rgb = NAVY
        run_t = p.add_run(str(text))
        run_t.font.size = Pt(10)
        run_t.font.color.rgb = BLACK
        return p

    def add_quote(character, dialogue):
        """캐릭터 대사 인용구"""
        if not dialogue:
            return
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(1)
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(6)
        # 왼쪽 보더 효과: 인용부호로 대체
        run = p.add_run(f'"{dialogue}"')
        run.font.size = Pt(10)
        run.font.italic = True
        run.font.color.rgb = NAVY
        if character:
            run2 = p.add_run(f"\n— {character}")
            run2.font.size = Pt(9)
            run2.font.color.rgb = DIM

    def add_spacer(height=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(height)
        p.paragraph_format.space_after = Pt(0)

    # ═══════════════════════════════════
    #  COVER PAGE
    # ═══════════════════════════════════
    add_spacer(60)

    # "작품 기획안"
    p0 = doc.add_paragraph()
    p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r0 = p0.add_run("작 품 기 획 안")
    r0.font.size = Pt(11)
    r0.font.color.rgb = DIM
    r0.font.name = 'Pretendard'

    add_spacer(12)

    # 작품 제목 (대형)
    title_text = project.get("title", "제목 없음")
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run(title_text)
    r1.font.size = Pt(32)
    r1.font.bold = True
    r1.font.color.rgb = NAVY
    r1.font.name = 'Pretendard'

    # 장르 · 타겟 · 포맷
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta_text = f"{project.get('genre','')}  ·  {project.get('target_market','')}  ·  {project.get('format','')}"
    r2 = p2.add_run(meta_text)
    r2.font.size = Pt(10)
    r2.font.color.rgb = DIM

    add_spacer(40)

    # 노란 구분선
    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line = p_line.add_run("━" * 30)
    r_line.font.size = Pt(10)
    r_line.font.color.rgb = YELLOW

    add_spacer(12)

    # 로그라인 미리보기 (있으면)
    core = project.get("core", {})
    lp = core.get("logline_pack", {}) if core else {}
    washed = lp.get("washed", "")
    if washed:
        p_log = doc.add_paragraph()
        p_log.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_log = p_log.add_run(washed)
        r_log.font.size = Pt(10)
        r_log.font.italic = True
        r_log.font.color.rgb = BLACK

    add_spacer(50)

    # 기획/제작 크레딧
    p_credit = doc.add_paragraph()
    p_credit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_c1 = p_credit.add_run("기획 · 공동제작\n")
    r_c1.font.size = Pt(9)
    r_c1.font.color.rgb = DIM
    r_c2 = p_credit.add_run("BLUE JEANS PICTURES")
    r_c2.font.size = Pt(14)
    r_c2.font.bold = True
    r_c2.font.color.rgb = NAVY
    r_c2.font.name = 'Pretendard'

    doc.add_page_break()

    # ═══════════════════════════════════
    #  SECTION 1: 로그라인 LOGLINE
    # ═══════════════════════════════════
    if core:
        add_yellow_header("로그라인", "LOGLINE")
        for label, key in [("Original","original"),("Washed","washed"),("투자자용","investor"),("감독용","director"),("캐릭터 훅","character_hook")]:
            val = lp.get(key, "")
            if val:
                add_labeled(label, val)

        # ── 기획의도 KEY POINTS ──
        add_yellow_header("기획의도", "KEY POINTS")
        pi = core.get("project_intent", {})
        add_labeled("소재", pi.get("subject", ""))
        add_labeled("장르", pi.get("genre_approach", ""))
        add_labeled("시장", pi.get("market_rationale", ""))
        add_labeled("Pitch", pi.get("pitch", ""))
        add_labeled("Theme", pi.get("theme", ""))

        # ── G/N/S ──
        add_yellow_header("드라마 구조", "GOAL / NEED / STRATEGY")
        gns = core.get("goal_need_strategy", {})
        add_labeled("Goal", gns.get("goal", ""))
        add_labeled("Need", gns.get("need", ""))
        add_labeled("Strategy", gns.get("strategy", ""))
        add_labeled("Risk", gns.get("risk", ""))
        add_labeled("Ending Payoff", gns.get("ending_payoff", ""))

        # ── 서사동력 NARRATIVE DRIVE ──
        nd = core.get("narrative_drive", {})
        if nd:
            add_spacer(6)
            add_sub_header("▎ 서사동력  ·  Narrative Drive")
            origin = nd.get("desire_origin", "")
            origin_kr = "상실(Loss)" if origin == "loss" else "결핍(Lack)" if origin == "lack" else origin
            add_labeled("발생요인", f"{origin_kr} — {nd.get('origin_detail', '')}")
            add_labeled("아크 방향", nd.get("arc_direction", ""))
            add_labeled("해결전략", nd.get("resolution_strategy", ""))
            add_labeled("Goal↔Need 간극", nd.get("goal_need_gap", ""))

        # ── 오프닝 전략 OPENING STRATEGY (v2.2 신규) ──
        os_data = core.get("opening_strategy", {})
        if os_data:
            add_yellow_header("오프닝 전략", "OPENING STRATEGY")
            add_labeled("오프닝 타입", os_data.get("opening_type", ""))
            add_labeled("오프닝 의도", os_data.get("opening_intent", ""))
            add_labeled("도파민 포인트", os_data.get("dopamine_point", ""))
            add_labeled("1막 연결 방식", os_data.get("opening_to_act1_link", ""))
            add_labeled("훅 라인/이미지", os_data.get("opening_hook_line", ""))
            add_labeled("장르 DNA 체크", os_data.get("genre_dna_check", ""))

        # ── 세계관 WORLD ──
        add_yellow_header("세계관", "WORLD BUILDING")
        wb = core.get("world_build", {})
        for label, key in [("시간","time"),("공간","space"),("규칙","rules"),("금기","taboo"),("권력구조","power_structure")]:
            add_labeled(label, wb.get(key, ""))

        doc.add_page_break()

        # ── 캐릭터 CHARACTER ──
        add_yellow_header("캐릭터", "CHARACTER")
        role_labels = {"protagonist":"주인공","antagonist":"적대자","ally":"조력자","mirror":"거울","catalyst":"촉매자","subplot_lead":"서브플롯 리드"}
        all_core_chars = core.get("characters", []) + core.get("extended_characters", [])
        for ch in all_core_chars:
            role = role_labels.get(ch.get("role",""), ch.get("role",""))
            name = ch.get("name", "")

            # 캐릭터 이름 헤더
            add_sub_header(f"▎ {role}  ·  {name}")

            add_body(ch.get("description", ""))
            add_labeled("욕망", ch.get("goal", ""))
            add_labeled("결핍", ch.get("need", ch.get("flaw", "")))
            add_labeled("대사톤", ch.get("dialogue_tone", ""))

            # 대사 인용구 (있으면)
            key_dialogue = ch.get("key_dialogue", ch.get("signature_line", ""))
            if key_dialogue:
                add_quote(name, key_dialogue)

            add_spacer(8)

    # ── Character Bible (확장) ──
    char_bible = project.get("char_bible", {})
    if char_bible:
        doc.add_page_break()
        add_yellow_header("캐릭터 바이블", "CHARACTER BIBLE")

        for ch in char_bible.get("characters", []):
            role_kr = {"protagonist":"주인공","antagonist":"적대자","ally":"조력자","mirror":"거울","catalyst":"촉매자","subplot_lead":"서브플롯 리드"}
            role = role_kr.get(ch.get("role",""), ch.get("role",""))
            name = ch.get("name","")
            age = ch.get("age","")

            add_sub_header(f"▎ {role} · {name} ({age})")

            add_labeled("외형·첫인상", ch.get("appearance",""))
            add_labeled("직업/위치", ch.get("occupation",""))
            add_body(ch.get("backstory",""))

            add_labeled("비밀", ch.get("secret",""))
            add_labeled("신념", ch.get("belief",""))
            add_labeled("두려움", ch.get("fear",""))

            habits = ch.get("habits", [])
            if habits:
                h_str = " · ".join(habits) if isinstance(habits, list) else str(habits)
                add_labeled("반복 습관", h_str)

            sp = ch.get("speech_pattern", [])
            if sp:
                sp_list = sp if isinstance(sp, list) else [sp]
                for i, s in enumerate(sp_list, 1):
                    add_labeled(f"말투 {i}", s)

            sl = ch.get("sample_lines", {})
            if sl:
                sl_labels = {"normal":"평상시","angry":"분노","vulnerable":"취약"}
                for k, v in sl.items():
                    label = sl_labels.get(k, k)
                    add_quote(f"{name} — {label}", v)

            ra = ch.get("relationship_attitudes", [])
            if ra:
                ra_list = ra if isinstance(ra, list) else [ra]
                for r in ra_list:
                    add_labeled("관계", r)

            arc = ch.get("arc_detail", {})
            if arc:
                add_labeled("1막 끝", arc.get("act1_end",""))
                add_labeled("미드포인트", arc.get("midpoint",""))
                add_labeled("클라이맥스", arc.get("climax",""))

            add_spacer(10)

    doc.add_page_break()

    # ═══════════════════════════════════
    #  SECTION 2: 시놉시스 SYNOPSIS
    # ═══════════════════════════════════
    story = project.get("structure_story", {})
    diag = project.get("structure_diag", {})

    if story:
        add_yellow_header("시놉시스", "SYNOPSIS")
        syn = story.get("synopsis_1p", {})
        for label, key in [("시작","opening"),("촉발사건","catalyst"),("전개","development"),("미드포인트","midpoint"),("붕괴","collapse"),("결전","climax"),("결말","ending")]:
            add_labeled(label, syn.get(key, ""))

        # 줄글 시놉시스
        prose = project.get("structure_prose", {})
        if prose and prose.get("prose"):
            add_spacer(6)
            add_sub_header("기승전결 시놉시스")
            add_body(prose["prose"])

        doc.add_page_break()

        # ── 스토리라인 STORYLINE ──
        add_yellow_header("스토리라인", "STORYLINE")
        for seq in story.get("storyline", []):
            seq_no = seq.get("seq", "")
            label = seq.get("label", "")
            add_sub_header(f"SEQ {seq_no}  ·  {label}")
            add_body(seq.get("summary", ""))

    if diag:
        doc.add_page_break()

        # ── 3막 구조 진단 ──
        add_yellow_header("3막 구조 진단", "THREE-ACT STRUCTURE")
        ta = diag.get("three_act", {})
        for label, key in [("1막 끝","act1_end"),("미드포인트","act2_midpoint"),("All Is Lost","act2_end"),("클라이맥스","act3_climax")]:
            add_labeled(label, ta.get(key, ""))

        add_spacer(6)
        add_sub_header("15-Beat Sheet")
        for bt in diag.get("beat_sheet", []):
            beat = bt.get("beat", "")
            status = bt.get("status", "")
            note = bt.get("note", "")
            status_mark = "✓" if status in ["있음","O","✓"] else "△" if status in ["약함","△"] else "✗"
            add_labeled(beat, f"{status_mark} {note}")

    doc.add_page_break()

    # ═══════════════════════════════════
    #  SECTION 3: 장면 설계 SCENE DESIGN
    # ═══════════════════════════════════
    scene_design = project.get("scene_design", {})
    if scene_design:
        add_yellow_header("장면 설계", "SCENE DESIGN")
        sms = scene_design.get("scene_map_summary", {})
        if sms.get("must_see_scenes"):
            add_labeled("Must-See 장면", sms["must_see_scenes"])

        add_spacer(6)

        for sc in scene_design.get("key_scenes", []):
            scene_no = sc.get("scene_no", "")
            title = sc.get("title", "")
            add_sub_header(f"S#{scene_no}  {title}")

            add_labeled("장소", sc.get("location", ""))
            add_labeled("인물", sc.get("characters", ""))
            add_labeled("상황", sc.get("setup", ""))
            add_labeled("행동 (Show!)", sc.get("dramatic_action", ""))

            tp = sc.get("turning_point", "")
            if tp:
                add_labeled("전환", tp)
            di = sc.get("dramatic_irony", "")
            if di:
                add_labeled("극적 아이러니", di)

            add_labeled("감정 변화", sc.get("emotion_shift", ""))
            add_labeled("시각 연출", sc.get("visual_direction", ""))
            add_labeled("판돈", sc.get("stakes", ""))

            kl = sc.get("key_line", "")
            if kl:
                # 핵심 대사는 인용구 스타일
                char_name = ""
                if ":" in kl:
                    char_name, dialogue = kl.split(":", 1)
                    add_quote(char_name.strip(), dialogue.strip())
                else:
                    add_quote("", kl)

            add_spacer(4)

        doc.add_page_break()

    # ═══════════════════════════════════
    #  SECTION 4: 트리트먼트 TREATMENT
    # ═══════════════════════════════════
    treatment = project.get("treatment", {})
    if treatment:
        add_yellow_header("트리트먼트", "TREATMENT")

        p_info = doc.add_paragraph()
        r_info = p_info.add_run("16비트 줄글 트리트먼트  ·  서술체 현재형  ·  대사 포함")
        r_info.font.size = Pt(9)
        r_info.font.color.rgb = DIM
        r_info.font.italic = True

        act_headers = {
            1: ("1막 — 설정", "ACT 1: SET-UP"),
            2: ("2막 — 대결", "ACT 2: CONFRONTATION"),
            3: ("3막 — 해결", "ACT 3: RESOLUTION"),
        }

        for act_num in [1, 2, 3]:
            act_data = treatment.get(f"act{act_num}")
            if act_data:
                kr, en = act_headers[act_num]
                add_spacer(10)
                # 막 헤더 (네이비 배경)
                p_act = doc.add_paragraph()
                p_act.paragraph_format.space_before = Pt(14)
                p_act.paragraph_format.space_after = Pt(8)
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="191970" w:val="clear"/>')
                p_act.paragraph_format.element.get_or_add_pPr().append(shading)
                r_act = p_act.add_run(f"  {kr}  ·  {en}")
                r_act.font.size = Pt(12)
                r_act.font.bold = True
                r_act.font.color.rgb = WHITE

                for b in act_data.get("beats", []):
                    beat_no = b.get("beat_no", "")
                    beat_name = b.get("beat_name", "")
                    narrative = b.get("narrative", "")
                    episode = b.get("episode", "")
                    event_s = b.get("event_summary", "")
                    decision_s = b.get("decision_summary", "")
                    consequence_s = b.get("consequence_summary", "")
                    b_story = b.get("b_story_beat", "")
                    cliff = b.get("cliffhanger", "")
                    villain = b.get("villain_beat", "")
                    pp = b.get("plant_payoff", "")

                    # 비트 번호 + 에피소드 태그 + 이름
                    p_beat = doc.add_paragraph()
                    p_beat.paragraph_format.space_before = Pt(12)
                    p_beat.paragraph_format.space_after = Pt(4)
                    if episode:
                        r_ep = p_beat.add_run(f"[{episode}] ")
                        r_ep.font.size = Pt(9)
                        r_ep.font.bold = True
                        r_ep.font.color.rgb = NAVY
                    r_num = p_beat.add_run(f"Beat {beat_no}")
                    r_num.font.size = Pt(10)
                    r_num.font.bold = True
                    r_num.font.color.rgb = YELLOW
                    r_name = p_beat.add_run(f"  {beat_name}")
                    r_name.font.size = Pt(10)
                    r_name.font.bold = True
                    r_name.font.color.rgb = NAVY

                    # 사건/선택/결과 요약 블록
                    meta_parts = []
                    if event_s:
                        meta_parts.append(f"사건: {event_s}")
                    if decision_s:
                        meta_parts.append(f"선택: {decision_s}")
                    if consequence_s:
                        meta_parts.append(f"결과: {consequence_s}")
                    if b_story:
                        meta_parts.append(f"B-Story: {b_story}")
                    if villain:
                        meta_parts.append(f"빌런: {villain}")
                    if pp:
                        meta_parts.append(f"Plant/Payoff: {pp}")
                    if cliff:
                        meta_parts.append(f"CLIFFHANGER: {cliff}")
                    if meta_parts:
                        p_meta = doc.add_paragraph()
                        p_meta.paragraph_format.space_before = Pt(2)
                        p_meta.paragraph_format.space_after = Pt(4)
                        shading_meta = parse_xml(f'<w:shd {nsdecls("w")} w:fill="EEEEF6" w:val="clear"/>')
                        p_meta.paragraph_format.element.get_or_add_pPr().append(shading_meta)
                        r_meta = p_meta.add_run(" | ".join(meta_parts))
                        r_meta.font.size = Pt(8)
                        r_meta.font.color.rgb = RGBColor(0x4A, 0x4A, 0x5A)
                        r_meta.font.italic = True

                    # 줄글 narrative
                    if narrative:
                        p_n = doc.add_paragraph()
                        p_n.paragraph_format.line_spacing = 1.6
                        p_n.paragraph_format.first_line_indent = Cm(0.5)
                        r_n = p_n.add_run(narrative)
                        r_n.font.size = Pt(10)
                        r_n.font.color.rgb = BLACK

        # 투자자용 요약
        meta = treatment.get("meta", {})
        if meta.get("investor_summary"):
            doc.add_page_break()
            add_yellow_header("투자자용 요약", "INVESTOR SUMMARY")
            add_body(meta["investor_summary"])

        # 감독 포인트
        if meta.get("director_notes"):
            add_spacer(8)
            add_sub_header("감독 포인트")
            for i, note in enumerate(meta["director_notes"], 1):
                add_labeled(f"Point {i}", note)

    doc.add_page_break()

    # ═══════════════════════════════════
    #  SECTION 5: 점수 DEVELOPMENT SCORE
    # ═══════════════════════════════════
    add_yellow_header("개발 적합도", "DEVELOPMENT FIT SCORE")

    cg = project.get("core_gate", {})
    fa = cg.get("five_axis_scores", {})
    if fa:
        final = fa.get("final_score", "")
        verdict = fa.get("verdict", "")

        # 큰 점수
        p_score = doc.add_paragraph()
        p_score.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_score.paragraph_format.space_before = Pt(12)
        r_score = p_score.add_run(str(final))
        r_score.font.size = Pt(36)
        r_score.font.bold = True
        r_score.font.color.rgb = NAVY

        p_verdict = doc.add_paragraph()
        p_verdict.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_v = p_verdict.add_run(str(verdict))
        r_v.font.size = Pt(11)
        r_v.font.color.rgb = DIM

        # 5축 상세 (테이블)
        axes = ["originality","market_fit","character","structure","theme"]
        axis_kr = {"originality":"독창성","market_fit":"시장성","character":"캐릭터","structure":"구조","theme":"테마"}
        scores_exist = any(fa.get(a) for a in axes)
        if scores_exist:
            add_spacer(8)
            table = doc.add_table(rows=1, cols=3)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr = table.rows[0].cells
            for i, text in enumerate(["항목", "점수", "상태"]):
                hdr[i].text = text
                for p in hdr[i].paragraphs:
                    for r in p.runs:
                        r.font.bold = True
                        r.font.size = Pt(9)
                        r.font.color.rgb = NAVY
            for a in axes:
                sc = fa.get(a, "")
                if sc:
                    row = table.add_row().cells
                    row[0].text = axis_kr.get(a, a)
                    row[1].text = str(sc)
                    sc_val = float(sc) if sc else 0
                    row[2].text = "●" if sc_val >= 7 else "◐" if sc_val >= 5 else "○"

    # ═══════════════════════════════════
    #  SECTION 6: 톤 문서 TONE DOCUMENT
    # ═══════════════════════════════════
    tone_doc = project.get("tone_doc", {})
    if tone_doc:
        doc.add_page_break()
        add_yellow_header("톤 & 연출 문서", "TONE DOCUMENT")

        vs = tone_doc.get("visual_style", {})
        if vs:
            add_sub_header("비주얼 스타일")
            for label, key in [("카메라 철학","camera_philosophy"),("색감 팔레트","color_palette"),("조명 규칙","lighting_rule"),("시그니처 쇼트","signature_shot")]:
                add_labeled(label, vs.get(key, ""))

        pc = tone_doc.get("pacing", {})
        if pc:
            add_sub_header("페이싱")
            for label, key in [("전체","overall"),("1막","act1_tempo"),("2막","act2_tempo"),("3막","act3_tempo"),("대사 비율","dialogue_density")]:
                add_labeled(label, pc.get(key, ""))

        dr = tone_doc.get("dialogue_rules", {})
        if dr:
            add_sub_header("대사 규칙")
            for label, key in [("전체 톤","overall_tone"),("서브텍스트","subtext_rule"),("침묵 활용","silence_usage")]:
                add_labeled(label, dr.get(key, ""))
            fp = dr.get("forbidden_phrases", [])
            if fp:
                fp_list = fp if isinstance(fp, list) else [fp]
                for f in fp_list:
                    add_labeled("금지", f)

        mt = tone_doc.get("motifs", {})
        if mt:
            add_sub_header("모티프")
            for label, key in [("반복 소품","recurring_objects"),("반복 장소","recurring_locations")]:
                val = mt.get(key, [])
                if val:
                    items = val if isinstance(val, list) else [val]
                    add_labeled(label, " · ".join(items))
            add_labeled("날씨/계절", mt.get("weather_mood",""))

        forbidden = tone_doc.get("forbidden", [])
        if forbidden:
            add_sub_header("금기 사항")
            fb_list = forbidden if isinstance(forbidden, list) else [forbidden]
            for f in fb_list:
                add_labeled("🚫", f)

        refs = tone_doc.get("reference_films", [])
        if refs:
            add_sub_header("참고 작품")
            for ref in refs:
                if isinstance(ref, dict):
                    add_labeled(ref.get("title",""), ref.get("reason",""))
                else:
                    add_body(str(ref))

        wi = tone_doc.get("writer_instruction", "")
        if wi:
            add_spacer(8)
            add_sub_header("Writer Engine 최종 지시")
            add_body(wi)

    # ═══════════════════════════════════
    #  FOOTER
    # ═══════════════════════════════════
    doc.add_paragraph("")
    p_line2 = doc.add_paragraph()
    p_line2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_line2 = p_line2.add_run("━" * 20)
    r_line2.font.size = Pt(8)
    r_line2.font.color.rgb = YELLOW

    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f1 = footer.add_run("© 2026 BLUE JEANS PICTURES\n")
    r_f1.font.size = Pt(8)
    r_f1.font.color.rgb = DIM
    r_f2 = footer.add_run(f"Creator Engine {ENGINE_VERSION}")
    r_f2.font.size = Pt(7)
    r_f2.font.color.rgb = DIM

    # Save to buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer


# ═══════════════════════════════════════════════════
#  UI 렌더링
# ═══════════════════════════════════════════════════

# ─── 공통 헤더 ───
st.markdown(
    '<div style="text-align:center;padding:2rem 0 0 0">'
    '<div class="header">B L U E &nbsp; J E A N S &nbsp; P I C T U R E S</div>'
    '<div class="brand-title">CREATOR ENGINE</div>'
    '<div class="sub">Y O U N G &nbsp; · &nbsp; V I N T A G E &nbsp; · &nbsp; F R E E &nbsp; · &nbsp; I N N O V A T I V E</div>'
    '</div>',
    unsafe_allow_html=True
)

# ─── 뒤로가기 ───
if st.session_state.view in ("project", "core", "char_bible", "structure", "scene_design", "treatment", "tone_doc") and st.session_state.cur:
    if st.session_state.view == "tone_doc":
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← 프로젝트 목록"):
                st.session_state.view = "home"
                st.rerun()
        with col_nav2:
            if st.button("← Treatment"):
                st.session_state.view = "treatment"
                st.rerun()
    elif st.session_state.view == "treatment":
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← 프로젝트 목록"):
                st.session_state.view = "home"
                st.rerun()
        with col_nav2:
            if st.button("← Scene Design"):
                st.session_state.view = "scene_design"
                st.rerun()
    elif st.session_state.view == "scene_design":
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← 프로젝트 목록"):
                st.session_state.view = "home"
                st.rerun()
        with col_nav2:
            if st.button("← Structure"):
                st.session_state.view = "structure"
                st.rerun()
    elif st.session_state.view == "structure":
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← 프로젝트 목록"):
                st.session_state.view = "home"
                st.rerun()
        with col_nav2:
            if st.button("← Character Bible"):
                st.session_state.view = "char_bible"
                st.rerun()
    elif st.session_state.view == "char_bible":
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← 프로젝트 목록"):
                st.session_state.view = "home"
                st.rerun()
        with col_nav2:
            if st.button("← Core Build"):
                st.session_state.view = "core"
                st.rerun()
    elif st.session_state.view == "core":
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("← 프로젝트 목록"):
                st.session_state.view = "home"
                st.rerun()
        with col_nav2:
            if st.button("← Brainstorm"):
                st.session_state.view = "project"
                st.rerun()
    else:
        if st.button("← 프로젝트 목록"):
            st.session_state.view = "home"
            st.rerun()


# ═══════════════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════════════
if st.session_state.view == "home":

    # ═══════════════════════════════════════════════════
    # ★ v2.4.0: Idea Engine 시드 업로드 (선택)
    # ═══════════════════════════════════════════════════
    # Idea Engine v1.0에서 생성한 LOCKED 시드 JSON을 업로드하면
    # 아래 입력 필드(제목·아이디어·장르·시장·포맷·LOCKED)가 자동으로 채워지고,
    # 시드 데이터(레퍼런스·로그라인·테마)가 v2.4 시대극 자동 감지에 활용됩니다.
    with st.expander("🔑 Idea Engine 시드 업로드 (선택)", expanded=False):
        st.caption(
            "Idea Engine에서 생성한 LOCKED 시드 JSON을 업로드하면 "
            "아래 새 프로젝트 입력 필드가 자동으로 채워집니다. "
            "(이 단계는 선택입니다 — 직접 입력하셔도 됩니다.)"
        )

        idea_seed_file = st.file_uploader(
            "Idea Engine JSON 파일",
            type=["json"],
            key="idea_engine_seed_uploader",
            help="Idea Engine ⑧ Export 단계에서 다운로드한 IdeaSeed_*.json 파일"
        )

        # 파일 업로드 시 1회 파싱 → session_state에 보관
        if idea_seed_file is not None:
            try:
                seed_str = idea_seed_file.read().decode("utf-8")
                seed_data = json.loads(seed_str)

                # Idea Engine 메타 검증
                if "_idea_engine_meta" not in seed_data:
                    st.error(
                        "❌ 올바른 Idea Engine JSON이 아닙니다. "
                        "이 자리는 Idea Engine 시드 전용이며, "
                        "Creator Engine 자체 백업 JSON은 아래의 "
                        "📁 프로젝트 JSON 불러오기 (세션 복구)에 올려주세요."
                    )
                else:
                    # 시드 보관 (Stage 전체에서 활용)
                    st.session_state["locked_seed"] = seed_data.get("locked_seed", {})
                    st.session_state["idea_seed_loaded"] = seed_data

                    meta = seed_data.get("_idea_engine_meta", {})
                    project_id = meta.get("project_id", "—")
                    verdict = meta.get("verdict", "—")
                    hook_score = meta.get("hook_score", 0)

                    # Verdict별 색상
                    verdict_color = {
                        "GO": "#2EC484",
                        "CONDITIONAL": "#FFCB05",
                        "NOGO": "#D32F2F",
                    }.get(verdict, "#8E8E99")

                    st.markdown(
                        f'<div class="callout" style="border-left-color:{verdict_color};">'
                        f'<div class="cl">🔑 Idea Engine 시드 로드 완료</div>'
                        f'<b style="font-size:1rem;">{seed_data.get("title", "제목 없음")}</b><br>'
                        f'<span style="font-size:.85rem;">'
                        f'Project: <code>{project_id}</code> · '
                        f'<b style="color:{verdict_color};">{verdict}</b> · '
                        f'Hook Score <b>{hook_score}/50</b>'
                        f'</span></div>',
                        unsafe_allow_html=True
                    )

                    # 임원 요약 (있으면)
                    exec_summary = seed_data.get("executive_summary", "")
                    if exec_summary:
                        with st.expander("📋 Executive Summary 보기", expanded=False):
                            st.markdown(exec_summary)

                    # Creator Engine에서 결정할 펜딩 질문
                    pending = seed_data.get("pending_decisions", [])
                    if pending:
                        st.markdown("**📝 Creator Engine에서 결정할 사항**")
                        for q in pending:
                            st.markdown(f"- {q}")

                    # LOCKED 시드 핵심 항목 미리보기
                    locked_seed = seed_data.get("locked_seed", {})
                    if locked_seed:
                        with st.expander("🔒 LOCKED 시드 패키지 상세", expanded=False):
                            ll = locked_seed.get("locked_logline", "")
                            if ll:
                                st.markdown(f"**LOCKED 로그라인**: {ll}")
                            lg = locked_seed.get("locked_genre", {})
                            if lg:
                                st.markdown(
                                    f"**장르**: {lg.get('primary', '')}"
                                    + (f" / {lg.get('secondary', '')}" if lg.get('secondary') else "")
                                )
                            lr = locked_seed.get("locked_references", [])
                            if lr:
                                ref_titles = []
                                for r in lr:
                                    if isinstance(r, dict):
                                        ref_titles.append(r.get("title", ""))
                                    elif isinstance(r, str):
                                        ref_titles.append(r)
                                ref_titles = [t for t in ref_titles if t]
                                if ref_titles:
                                    st.markdown(f"**레퍼런스**: {' / '.join(ref_titles)}")
                            risks = locked_seed.get("locked_risks_to_address", [])
                            if risks:
                                st.markdown("**위험 요소 (Treatment 단계에서 다룰 것)**:")
                                for r in risks:
                                    st.markdown(f"- {r}")

                    st.success(
                        "✅ 아래 '➕ 새 프로젝트'에 시드 데이터가 자동 입력됩니다. "
                        "필요하면 직접 수정하실 수 있습니다."
                    )

                    # 시드 제거 버튼
                    if st.button("🗑️ 시드 제거 (직접 입력으로 전환)",
                                 key="clear_idea_seed", use_container_width=False):
                        for k in ("locked_seed", "idea_seed_loaded"):
                            if k in st.session_state:
                                del st.session_state[k]
                        st.rerun()

            except json.JSONDecodeError as e:
                st.error(f"❌ JSON 파싱 실패: {e}")
            except Exception as e:
                st.error(f"❌ 시드 로드 실패: {e}")

    # 새 프로젝트 생성
    with st.expander("➕ 새 프로젝트", expanded=not bool(st.session_state.projects)):
        # ── v2.4.0: Idea Engine 시드가 로드되어 있으면 default value 추출 ──
        _seed_full = st.session_state.get("idea_seed_loaded", {}) or {}
        _seed_locked = st.session_state.get("locked_seed", {}) or {}
        _seed_default_title = _seed_full.get("title", "")
        _seed_default_idea = _seed_full.get("raw_idea", "") or _seed_locked.get("locked_logline", "")
        _seed_default_genre = _seed_full.get("genre", "") or _seed_locked.get("locked_genre", {}).get("primary", "")
        _seed_default_market = _seed_full.get("target_market", "")
        _seed_default_format = _seed_full.get("format", "") or _seed_locked.get("locked_format", {}).get("primary", "")

        # LOCKED 자동 생성 — 시드의 핵심 항목을 한 줄씩 텍스트로
        # ─── v2.5.2: Idea Engine 시드의 핵심 결정·모티프·규약까지 확장 추출 ───
        _seed_default_locked = ""
        if _seed_locked:
            _lock_lines = []
            ll = _seed_locked.get("locked_logline", "")
            if ll:
                _lock_lines.append(f"로그라인: {ll}")
            lg = _seed_locked.get("locked_genre", {})
            if isinstance(lg, dict) and lg.get("primary"):
                gtxt = lg["primary"]
                if lg.get("secondary"):
                    gtxt += f" / {lg['secondary']}"
                if lg.get("tertiary"):
                    gtxt += f" / {lg['tertiary']}"
                _lock_lines.append(f"장르: {gtxt}")
            lt = _seed_locked.get("locked_theme", {})
            if isinstance(lt, dict):
                if lt.get("surface"):
                    _lock_lines.append(f"표면 주제: {lt['surface']}")
                if lt.get("deep"):
                    _lock_lines.append(f"심층 주제: {lt['deep']}")
            ltg = _seed_locked.get("locked_target", {})
            if isinstance(ltg, dict):
                if ltg.get("domestic"):
                    _lock_lines.append(f"국내 타겟: {ltg['domestic']}")
                if ltg.get("global"):
                    _lock_lines.append(f"글로벌 타겟: {ltg['global']}")
            lf = _seed_locked.get("locked_format", {})
            if isinstance(lf, dict):
                if lf.get("episode_count"):
                    _lock_lines.append(f"회차/분량: {lf.get('episode_count')} ({lf.get('runtime', '')})")
            lr = _seed_locked.get("locked_references", [])
            if isinstance(lr, list) and lr:
                ref_titles = []
                for r in lr:
                    if isinstance(r, dict) and r.get("title"):
                        ref_titles.append(r["title"])
                    elif isinstance(r, str):
                        ref_titles.append(r)
                if ref_titles:
                    _lock_lines.append(f"참고작: {' / '.join(ref_titles[:5])}")
            risks = _seed_locked.get("locked_risks_to_address", [])
            if isinstance(risks, list) and risks:
                _lock_lines.append("[Treatment에서 다룰 위험 요소]")
                for r in risks:
                    _lock_lines.append(f"- {r}")

            # ─── v2.5.2 신규 추출 영역 5종 ──────────────────────────
            # 1. 확정된 핵심 결정 (포맷·결말·음악·스타일 등 작품 본질 LOCK)
            core_decisions = _seed_locked.get("locked_core_decisions", [])
            if isinstance(core_decisions, list) and core_decisions:
                _lock_lines.append("")
                _lock_lines.append("[★ 확정된 핵심 결정 LOCK ★ — 절대 변경 금지]")
                for d in core_decisions:
                    if isinstance(d, dict):
                        cat = d.get("category", "")
                        rule = d.get("rule", "") or d.get("decision", "")
                        if cat and rule:
                            _lock_lines.append(f"- [{cat}] {rule}")
                        elif rule:
                            _lock_lines.append(f"- {rule}")
                    elif isinstance(d, str):
                        _lock_lines.append(f"- {d}")

            # 2. 음악 사용 규약 (장르 특화 — 멜로/음악·청춘물에서 자주 나타남)
            music_rules = _seed_locked.get("locked_music_rules", {})
            if music_rules:
                _lock_lines.append("")
                _lock_lines.append("[★ 음악 사용 규약 LOCK ★]")
                if isinstance(music_rules, dict):
                    for k, v in music_rules.items():
                        if isinstance(v, list):
                            for item in v:
                                _lock_lines.append(f"- [{k}] {item}")
                        else:
                            _lock_lines.append(f"- [{k}] {v}")
                elif isinstance(music_rules, list):
                    for r in music_rules:
                        _lock_lines.append(f"- {r}")
                elif isinstance(music_rules, str):
                    _lock_lines.append(f"- {music_rules}")

            # 3. 시각 모티프 (오브제 연결핀 — 두 타임라인/두 세계 연결의 시각 장치)
            visual_motifs = _seed_locked.get("locked_visual_motifs", [])
            if isinstance(visual_motifs, list) and visual_motifs:
                _lock_lines.append("")
                _lock_lines.append("[★ 시각 모티프 LOCK ★ — Treatment·Scene Design에서 보존]")
                for m in visual_motifs:
                    if isinstance(m, dict):
                        motif = m.get("motif", "") or m.get("name", "")
                        function = m.get("function", "") or m.get("role", "")
                        if motif and function:
                            _lock_lines.append(f"- {motif} → {function}")
                        elif motif:
                            _lock_lines.append(f"- {motif}")
                    elif isinstance(m, str):
                        _lock_lines.append(f"- {m}")

            # 4. 결말 형식 (헤어짐/결합/모호 등 결말의 본질 LOCK)
            ending_form = _seed_locked.get("locked_ending_form", {})
            if ending_form:
                _lock_lines.append("")
                _lock_lines.append("[★ 결말 형식 LOCK ★]")
                if isinstance(ending_form, dict):
                    if ending_form.get("type"):
                        _lock_lines.append(f"- 결말 유형: {ending_form['type']}")
                    if ending_form.get("emotional_resolution"):
                        _lock_lines.append(f"- 정서적 해소: {ending_form['emotional_resolution']}")
                    if ending_form.get("final_image"):
                        _lock_lines.append(f"- 마지막 이미지: {ending_form['final_image']}")
                    if ending_form.get("forbidden"):
                        _lock_lines.append(f"- 금지 패턴: {ending_form['forbidden']}")
                elif isinstance(ending_form, str):
                    _lock_lines.append(f"- {ending_form}")

            # 5. Creator Engine 결정 의제 (Idea가 미해결로 남긴 핵심 질문 — Creator가 답해야 함)
            creator_questions = _seed_locked.get("locked_creator_questions", [])
            if isinstance(creator_questions, list) and creator_questions:
                _lock_lines.append("")
                _lock_lines.append("[Creator Engine에서 답해야 할 핵심 의제]")
                for q in creator_questions:
                    if isinstance(q, dict):
                        question = q.get("question", "")
                        options = q.get("options", [])
                        if question:
                            line = f"- {question}"
                            if isinstance(options, list) and options:
                                line += f" (후보: {' / '.join(str(o) for o in options)})"
                            _lock_lines.append(line)
                    elif isinstance(q, str):
                        _lock_lines.append(f"- {q}")

            _seed_default_locked = "\n".join(_lock_lines)

        col1, col2 = st.columns([2, 1])

        with col1:
            title_input = st.text_input(
                "프로젝트 제목",
                value=_seed_default_title,
                placeholder="예: 인도네시아 물귀신 프로젝트"
            )
            idea_input = st.text_area(
                "💡 아이디어",
                value=_seed_default_idea,
                height=120,
                placeholder=(
                    "자유롭게 입력\n"
                    "예: 인도네시아용 물귀신 이야기\n"
                    "예: 은퇴한 킬러가 다시 돌아오는 이야기\n"
                    "예: 40대 여형사, 연쇄살인범이 딸의 담임교사"
                )
            )

        # ── LOCKED 설정 (v2.3: OPEN 필드 폐지) ──
        with st.expander("🔒 설정 잠금 (LOCKED)",
                          expanded=bool(_seed_default_locked)):
            st.caption(
                "LOCKED = 파이프라인 전 과정에서 절대 변경 불가. "
                "여기에 명시되지 않은 모든 디테일은 엔진이 자유롭게 창작합니다. "
                "한 줄에 하나씩 입력하세요."
            )
            locked_input = st.text_area(
                "🔒 LOCKED (반드시 지킬 것만 명시)",
                value=_seed_default_locked,
                height=180,
                placeholder=(
                    "한 줄에 하나씩:\n"
                    "장르: 로맨틱 코미디 (다른 장르 전환 금지)\n"
                    "주인공: 강유진 (여, 미혼)\n"
                    "핵심 관계: 아버지의 상속 조건\n"
                    "공간: 쿠킹 클래스 (아이반 + 성인반)\n"
                    "테마: 사람은 요리처럼 섞을 수 없다\n"
                    "엔딩 방향: 한 명 선택 아닌 자기 발견"
                )
            )
            # v2.3: OPEN 필드 폐지 — 하위 호환성을 위해 빈 리스트 유지
            open_input = ""


        with col2:
            # 장르: 시드 default를 selectbox 옵션과 매칭, 없으면 "미지정"
            _genre_options = ["미지정", "범죄/스릴러", "드라마", "액션", "로맨스", "코미디",
                              "로맨틱 코미디", "호러/공포", "SF", "판타지", "시대극/사극", "느와르",
                              "미스터리", "전쟁", "뮤지컬", "다큐/논픽션"]
            _genre_default_idx = 0
            for i, opt in enumerate(_genre_options):
                if _seed_default_genre and (_seed_default_genre == opt or opt in _seed_default_genre or _seed_default_genre in opt):
                    _genre_default_idx = i
                    break
            genre_input = st.selectbox(
                "🎬 장르",
                _genre_options,
                index=_genre_default_idx,
            )

            _market_options = ["미지정", "한국", "북미/미국", "일본", "중국",
                               "동남아", "유럽", "중동", "글로벌", "직접 입력"]
            _market_default_idx = 0
            for i, opt in enumerate(_market_options):
                if _seed_default_market and (_seed_default_market == opt or opt in _seed_default_market or _seed_default_market in opt):
                    _market_default_idx = i
                    break
            market_type = st.selectbox(
                "🌏 타겟 시장",
                _market_options,
                index=_market_default_idx,
            )

            market_custom = ""
            if market_type == "직접 입력":
                market_custom = st.text_input(
                    "시장 직접 입력",
                    value=(_seed_default_market if _seed_default_market not in _market_options else ""),
                    placeholder="예: 인도네시아+한국 공동제작"
                )

            _format_options = ["미지정", "영화", "시리즈", "미니시리즈(4~8화)",
                               "웹툰", "웹소설", "숏폼", "다큐멘터리", "애니메이션"]
            _format_default_idx = 0
            for i, opt in enumerate(_format_options):
                if _seed_default_format and (_seed_default_format == opt or opt in _seed_default_format or _seed_default_format in opt):
                    _format_default_idx = i
                    break
            format_input = st.selectbox(
                "📐 포맷",
                _format_options,
                index=_format_default_idx,
            )

            st.markdown("##### 🏛️ 특수 규칙")
            fact_based_input = st.checkbox(
                "실화 배경 작품",
                value=False,
                help="실제 사건/인물/시대를 배경으로 하는 작품. 실명 비사용 + 사실성 균형, 명예훼손·인격권 차단 규칙이 자동 적용됨."
            )
            historical_input = st.checkbox(
                "역사영화",
                value=False,
                help="시대극/사극. 시대 언어의 균형, 공간의 주인공화, 선악 이원 구도 회피 등 역사영화 전용 규칙 적용."
            )
            film_type_input = ""
            if historical_input:
                film_type_input = st.selectbox(
                    "역사영화 유형",
                    ["정통", "팩션", "퓨전"],
                    help="정통: 〈남한산성〉〈1987〉〈서울의 봄〉 / 팩션: 〈왕의 남자〉〈광해〉〈암살〉 / 퓨전: 〈조선명탐정〉〈전우치〉"
                )

        if st.button("🚀 프로젝트 생성", use_container_width=True, disabled=not idea_input.strip()):
            market_final = market_custom if market_type == "직접 입력" else market_type
            project_id = f"p_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # LOCKED 파싱 (줄 단위). v2.3: OPEN 필드는 폐지되어 빈 리스트로 유지 (하위 호환성)
            locked_list = [line.strip() for line in locked_input.strip().split("\n") if line.strip()] if locked_input.strip() else []
            open_list = []  # v2.3: OPEN 필드 폐지

            st.session_state.projects[project_id] = {
                "project_id": project_id,
                "title": title_input or "새 프로젝트",
                "idea_text": idea_input,
                "genre": genre_input,
                "target_market": market_final,
                "format": format_input,
                "fact_based": fact_based_input,
                "historical": historical_input,
                "film_type": film_type_input,
                "locked_items": locked_list,
                "open_items": open_list,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "research": None,
                "brainstorm_cards": None,
                "brainstorm_analysis": None,
                "core": None,
                "core_gate": None,
                "char_bible": None,
                "structure_story": None,
                "structure_diag": None,
                "structure_gate": None,
                "structure_prose": None,
                "scene_design": None,
                "treatment": None,
                "treatment_gate": None,
                "tone_doc": None,
                "final_score": None,
            }

            st.session_state.cur = project_id
            st.session_state.view = "project"
            st.rerun()

    # ─── 프로젝트 JSON 불러오기 (v2.3.5 신규) ───
    with st.expander("📂 프로젝트 JSON 불러오기 (세션 복구)", expanded=False):
        st.caption(
            "이전 세션에서 저장한 프로젝트 JSON 파일을 업로드하면 해당 시점으로 복원됩니다. "
            "Scene Design 완료 시점에 저장했다면 Treatment부터 이어서 진행 가능합니다."
        )
        uploaded_json = st.file_uploader(
            "프로젝트 JSON 파일 선택",
            type=["json"],
            key="project_json_uploader",
            help="Scene 완료 / Treatment 완료 / 최종완성 시점에 저장한 JSON 파일"
        )

        if uploaded_json is not None:
            try:
                json_str = uploaded_json.read().decode("utf-8")
                result = load_project_from_json(json_str)
                restored_project = result["project"]
                meta = result["meta"]
                warnings = result["warnings"]

                # 정보 표시
                st.markdown(
                    f'<div class="callout">'
                    f'<div class="cl">📋 불러올 프로젝트</div>'
                    f'<b>{restored_project.get("title", "제목 없음")}</b><br>'
                    f'{restored_project.get("genre", "")} · '
                    f'{restored_project.get("target_market", "")} · '
                    f'{restored_project.get("format", "")}<br>'
                    f'<span style="font-size:.75rem;color:var(--dim)">'
                    f'저장 시점: {meta.get("saved_at", "알 수 없음")} / '
                    f'단계: {meta.get("stage", "알 수 없음")} / '
                    f'엔진 버전: {meta.get("engine_version", "알 수 없음")}'
                    f'</span></div>',
                    unsafe_allow_html=True
                )

                # 경고 표시
                for w in warnings:
                    st.warning(w)

                # 중복 ID 체크 및 복원 버튼
                original_id = restored_project.get("project_id", "")
                id_conflict = original_id in st.session_state.projects

                if id_conflict:
                    st.info(
                        f"⚠️ 동일한 프로젝트 ID가 이미 존재합니다. "
                        f"복원 시 새 ID를 부여하여 별도 프로젝트로 추가됩니다."
                    )

                if st.button("✅ 이 프로젝트 복원하기", type="primary", use_container_width=True):
                    # 중복 방지: ID 충돌 시 새 ID 생성
                    if id_conflict:
                        new_id = f"proj_{int(datetime.now().timestamp() * 1000)}"
                        restored_project["project_id"] = new_id
                        restored_project["title"] = restored_project.get("title", "복원") + " (복원본)"
                        restored_id = new_id
                    else:
                        restored_id = original_id

                    # updated_at 갱신
                    restored_project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

                    # 세션 상태에 주입
                    st.session_state.projects[restored_id] = restored_project
                    st.session_state.cur = restored_id

                    # 단계별 적절한 view로 이동 (완료된 가장 높은 단계로)
                    if restored_project.get("tone_doc"):
                        st.session_state.view = "tone_doc"
                    elif restored_project.get("treatment"):
                        st.session_state.view = "treatment"
                    elif restored_project.get("scene_design"):
                        st.session_state.view = "scene_design"
                    elif restored_project.get("structure_story"):
                        st.session_state.view = "structure"
                    elif restored_project.get("char_bible"):
                        st.session_state.view = "char_bible"
                    elif restored_project.get("core"):
                        st.session_state.view = "core"
                    else:
                        st.session_state.view = "project"

                    st.success(f"✅ '{restored_project['title']}' 복원 완료. 해당 단계로 이동합니다.")
                    st.rerun()

            except ValueError as e:
                st.error(f"❌ 불러오기 실패: {e}")
            except Exception as e:
                st.error(f"❌ 예상치 못한 오류: {e}")

    # 프로젝트 목록
    if st.session_state.projects:
        st.markdown("---")
        st.markdown("### 📁 프로젝트")

        for project_id, project in sorted(
            st.session_state.projects.items(),
            key=lambda x: x[1]["updated_at"],
            reverse=True
        ):
            col1, col2 = st.columns([5, 1])

            with col1:
                has_cards = "✅" if project.get("brainstorm_cards") else "—"
                has_analysis = "✅" if project.get("brainstorm_analysis") else "—"

                st.markdown(
                    f'<div class="card">'
                    f'<b>{project["title"]}</b><br>'
                    f'<span style="font-size:.75rem;color:var(--dim)">'
                    f'{project["genre"]} · {project["target_market"]} · {project["format"]} · '
                    f'{project["updated_at"]}'
                    f'<br>카드 {has_cards} · 분석 {has_analysis}'
                    f'</span></div>',
                    unsafe_allow_html=True
                )

            with col2:
                if st.button("열기 →", key=f"open_{project_id}"):
                    st.session_state.cur = project_id
                    st.session_state.view = "project"
                    st.rerun()


# ═══════════════════════════════════════════════════
#  PROJECT (단일 페이지 스크롤)
# ═══════════════════════════════════════════════════
elif st.session_state.view == "project" and st.session_state.cur:

    project = st.session_state.projects[st.session_state.cur]

    # ─── 프로젝트 헤더 ───
    st.markdown(f"## {project['title']}")
    st.caption(f"{project['genre']} · {project['target_market']} · {project['format']}")

    # ─── 단계 표시 ───
    render_stepper("project", project)

    st.markdown(
        f'<div class="callout">'
        f'<div class="cl">IDEA</div>'
        f'{project["idea_text"]}'
        f'</div>',
        unsafe_allow_html=True
    )

    # ─── LOCKED 표시 + 편집 (v2.3: OPEN 필드 폐지) ───
    locked = project.get("locked_items", [])
    open_items = project.get("open_items", [])  # 하위 호환성 - 기존 프로젝트 로딩 시에만 사용

    if locked:
        locked_html = "".join(f"<li>{item}</li>" for item in locked)
        st.markdown(
            f'<div style="background:#FFF3CD;padding:8px 12px;border-radius:6px;border-left:4px solid #FFCB05;font-size:.82rem">'
            f'<b>🔒 LOCKED</b> — 변경 불가<ul style="margin:4px 0 0 0;padding-left:18px">{locked_html}</ul></div>',
            unsafe_allow_html=True
        )

    with st.expander("🔒 LOCKED 편집", expanded=False):
        st.caption("LOCKED = 반드시 지킬 것만 명시. 여기에 없는 것은 엔진이 자유롭게 창작합니다.")
        edited_locked = st.text_area(
            "🔒 LOCKED (변경 불가)",
            value="\n".join(locked),
            height=180,
            key="edit_locked",
            placeholder="한 줄에 하나씩"
        )
        if st.button("💾 LOCKED 저장", key="save_locked"):
            project["locked_items"] = [l.strip() for l in edited_locked.strip().split("\n") if l.strip()]
            project["open_items"] = []  # v2.3: OPEN 필드 폐지 - 빈 리스트 유지
            project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.success("저장 완료. 이후 생성되는 모든 단계에 반영됩니다.")
            st.rerun()

    # ─── 포맷 확정·변경 (v2.7.1 신규) ───
    # 발견 경위: Mr. MOON 질의 — "아이디어를 받아 개발하면서 포맷을 확정할 수 있나?"
    # 진단: project["format"] 대입 지점이 프로젝트 생성 시점 단 한 곳뿐이었다.
    #   포맷 판단은 Brainstorm·Core를 본 뒤에 굳는 성질인데
    #   확정 시점이 판단 시점보다 앞서 있었다.
    _FORMAT_OPTIONS = ["미지정", "영화", "시리즈", "미니시리즈(4~8화)",
                       "웹툰", "웹소설", "숏폼", "다큐멘터리", "애니메이션"]
    _cur_fmt = project.get("format", "미지정")
    _cur_idx = _FORMAT_OPTIONS.index(_cur_fmt) if _cur_fmt in _FORMAT_OPTIONS else 0

    if _cur_fmt == "미지정":
        st.warning(
            "📐 포맷이 **미지정** 상태입니다. 이대로 Structure에 진입하면 "
            "영화 구조(3막 16비트)가 적용됩니다. 아래에서 확정해 주십시오."
        )

    with st.expander(f"📐 포맷 확정·변경 — 현재: **{_cur_fmt}**", expanded=(_cur_fmt == "미지정")):
        st.caption(
            "포맷은 Brainstorm·Core를 본 뒤에 확정하는 것이 정확합니다. "
            "여기서 언제든 변경할 수 있으며, 변경 시 이후 생성되는 모든 단계에 반영됩니다."
        )

        # LOCKED 내 포맷 어휘 충돌 감지
        _FMT_TOKENS = ["부작", "회차", "시즌", "미니시리즈", "회당", "EP", "에피소드",
                       "오리지널 6부", "오리지널 8부", "러닝타임"]
        _conflicts = []
        for _li, _item in enumerate(project.get("locked_items", []) or []):
            if any(t in _item for t in _FMT_TOKENS):
                _conflicts.append((_li, _item))

        if _conflicts and _cur_fmt not in ("미지정",):
            _is_series_now = P.is_series_format(_cur_fmt)
            _mismatch = [(i, x) for i, x in _conflicts
                         if P.is_series_format(x) != _is_series_now]
            if _mismatch:
                # 제거 가능 항목 판별: '[포맷]'·'포맷:' 표식이 있는 포맷 전용 항목만.
                # 로그라인처럼 다른 내용에 포맷 어휘가 섞인 항목은 삭제하면
                # 본문까지 함께 사라지므로 제거 대상에서 제외한다.
                _fmt_only = [(i, x) for i, x in _mismatch
                             if "[포맷]" in x or x.strip().startswith("포맷:") or "포맷]" in x]
                _mixed = [(i, x) for i, x in _mismatch if (i, x) not in _fmt_only]

                st.error(
                    f"⚠️ LOCKED {len(_mismatch)}건이 확정 포맷 **{_cur_fmt}**와 충돌합니다. "
                    "상류(Idea Engine)의 잔재일 가능성이 높습니다."
                )
                if _fmt_only:
                    st.markdown("**포맷 전용 항목 — 제거 가능**")
                    for _i, _x in _fmt_only:
                        st.markdown(f"- `#{_i}` {_x[:90]}")
                if _mixed:
                    st.markdown("**혼합 항목 — 문구만 수정 필요 (자동 제거하지 않습니다)**")
                    for _i, _x in _mixed:
                        st.markdown(f"- `#{_i}` {_x[:90]}")
                    st.caption(
                        "이 항목들은 로그라인처럼 본문과 포맷 표현이 섞여 있어 통째로 지우면 내용이 함께 사라집니다. "
                        "아래 'LOCKED 편집'에서 포맷 어휘만 직접 고쳐 주십시오."
                    )

                st.caption(
                    "v2.7.1부터 포맷은 LOCKED보다 상위로 선언되므로 생성 결과는 확정 포맷을 따릅니다. "
                    "다만 LOCKED 문구 자체를 정리해 두는 것이 더 깨끗합니다."
                )
                if _fmt_only and st.button(
                    f"🧹 포맷 전용 항목 {len(_fmt_only)}건 제거", key="strip_fmt_locked"
                ):
                    _drop = {i for i, _ in _fmt_only}
                    _keep = [x for i, x in enumerate(project.get("locked_items", []))
                             if i not in _drop]
                    project["locked_items"] = _keep
                    project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                    st.success(f"{len(_fmt_only)}건 제거 완료.")
                    st.rerun()

        _new_fmt = st.selectbox(
            "📐 포맷",
            _FORMAT_OPTIONS,
            index=_cur_idx,
            key="edit_format",
        )
        if _new_fmt != _cur_fmt:
            _was_series = P.is_series_format(_cur_fmt)
            _now_series = P.is_series_format(_new_fmt)
            if _was_series != _now_series and project.get("structure_story"):
                st.warning(
                    "영화 ↔ 시리즈 전환입니다. 비트 구조 자체가 달라지므로 "
                    "**Structure부터 재실행**을 권합니다. Core와 Character Bible은 유지해도 됩니다."
                )
        if st.button("💾 포맷 저장", key="save_format"):
            project["format"] = _new_fmt
            project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.success(f"포맷 확정: {_new_fmt}. 이후 생성되는 모든 단계에 반영됩니다.")
            st.rerun()

    st.markdown("---")

    # ═══════════════════════════════════════
    # STEP 1: 리서치 (선택)
    # ═══════════════════════════════════════
    st.markdown('<div class="section-header">🔍 리서치 <span class="en">RESEARCH</span></div>', unsafe_allow_html=True)
    st.caption("실화/뉴스 + 기존 작품 정보 검색. 건너뛰어도 됩니다.")

    if st.button("🔍 리서치 실행"):
        with st.spinner("리서치 정리 중..."):
            result = call_research(
                project["idea_text"],
                project["genre"],
                project["target_market"]
            )
            if result:
                project["research"] = result
                project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.rerun()

    # 리서치 결과 표시
    if project.get("research"):
        research_data = project["research"]
        summary = research_data.get("research_summary", {})

        with st.expander(
            f"📰 리서치 결과 — "
            f"실화 {summary.get('total_real_events', 0)}건 · "
            f"작품 {summary.get('total_existing_works', 0)}건",
            expanded=True
        ):
            # 실화/뉴스
            if research_data.get("real_events"):
                st.markdown("**📰 실화 / 뉴스**")
                for event in research_data["real_events"]:
                    st.markdown(
                        f'<div class="ri">'
                        f'<div class="rl">#{event.get("id", "")} '
                        f'[{event.get("year", "")}] {event.get("source", "")}</div>'
                        f'<b>{event.get("title", "")}</b><br>'
                        f'{event.get("summary", "")}<br>'
                        f'<span style="color:var(--navy)">→ {event.get("story_potential", "")}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # 기존 작품
            if research_data.get("existing_works"):
                st.markdown("**🎬 기존 작품**")
                for work in research_data["existing_works"]:
                    st.markdown(
                        f'<div class="ri">'
                        f'<div class="rl">#{work.get("id", "")} '
                        f'{work.get("type", "")} · {work.get("country", "")} · '
                        f'{work.get("year", "")}</div>'
                        f'<b>{work.get("title", "")}</b><br>'
                        f'유사: {work.get("similarity", "")}<br>'
                        f'<span style="color:var(--navy)">→ 차별화: '
                        f'{work.get("difference_opportunity", "")}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            # 핵심 시사점
            if summary.get("key_insight"):
                st.markdown(
                    f'<div class="callout">'
                    f'<div class="cl">💡 핵심 시사점</div>'
                    f'{summary["key_insight"]}'
                    f'</div>',
                    unsafe_allow_html=True
                )

    st.markdown("---")

    # ═══════════════════════════════════════
    # STEP 2: Brainstorm (2단계 분할 호출)
    # ═══════════════════════════════════════
    st.markdown('<div class="section-header">🧠 Brainstorm <span class="en">CONCEPT IDEATION</span></div>', unsafe_allow_html=True)

    if st.button("🧠 Brainstorm 실행", type="primary"):

        # ── 1단계: 카드 생성 ──
        with st.spinner("① 컨셉 카드 생성 중... (약 20–30초)"):
            cards_result = call_brainstorm_cards(
                project["idea_text"],
                project["genre"],
                project["target_market"],
                project["format"],
                project.get("research"),
                locked_block=_build_project_locked_block(project)
            )

        if cards_result:
            project["brainstorm_cards"] = cards_result
            project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

            # Top 3 카드 추출
            all_cards = cards_result.get("idea_cards", [])
            cards_map = {c["id"]: c for c in all_cards}

            top3_data = []
            for t in cards_result.get("top3", []):
                card = cards_map.get(t["card_id"])
                if card:
                    top3_data.append(card)

            # ── 2단계: 분석 + Gate A ──
            if top3_data:
                with st.spinner("② 시장 분석 + Gate A 채점 중... (약 10–20초)"):
                    analysis_result = call_brainstorm_analysis(
                        project["idea_text"],
                        project["genre"],
                        project["target_market"],
                        project["format"],
                        top3_data,
                        project.get("research"),
                        locked_block=_build_project_locked_block(project)
                    )

                if analysis_result:
                    project["brainstorm_analysis"] = analysis_result
                    project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            else:
                st.warning("Top 3 카드를 추출하지 못했습니다. 카드만 표시합니다.")

            st.rerun()

    # ═══════════════════════════════════════
    # 결과 표시
    # ═══════════════════════════════════════
    if project.get("brainstorm_cards"):
        bc = project["brainstorm_cards"]
        ba = project.get("brainstorm_analysis", {})

        # ── 아이디어 유형 ──
        idea_type = bc.get("idea_type", "").upper()
        diagnosis = bc.get("idea_type_diagnosis", "")
        action = bc.get("idea_type_action", "")
        type_color = {"STORY": "var(--g)", "MOOD": "var(--navy)", "HYBRID": "#FF8C00"}.get(idea_type, "var(--dim)")
        action_html = (
            f'<div style="margin-top:.5rem;padding:.4rem .7rem;background:#FFF8E1;'
            f'border-radius:6px;font-size:.85rem;font-weight:700;color:#8B6914">→ {action}</div>'
        ) if action else ""
        st.markdown(
            f'<div class="callout" style="border-left:4px solid {type_color}">'
            f'<div class="cl" style="color:{type_color}">아이디어 유형: {idea_type}</div>'
            f'<div style="margin:.3rem 0;font-size:.9rem">{diagnosis}</div>'
            f'{action_html}'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── 시장 · 포맷 맥락 (분석 있을 때) ──
        if ba:
            market_ctx = ba.get("market_context", {})
            format_ctx = ba.get("format_context", {})

            col1, col2 = st.columns(2)

            with col1:
                ref_titles = ", ".join(market_ctx.get("reference_titles", []))
                st.markdown(
                    f'<div class="callout">'
                    f'<div class="cl">🌏 시장 — {market_ctx.get("target_market", "")}</div>'
                    f'기회: {market_ctx.get("market_insight", "")}<br>'
                    f'문화코드: {market_ctx.get("cultural_code", "")}<br>'
                    f'리스크: {market_ctx.get("market_risk", "")}<br>'
                    f'참고작: {ref_titles}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f'<div class="callout">'
                    f'<div class="cl">📐 포맷 — {format_ctx.get("selected_format", "")}</div>'
                    f'적합성: {format_ctx.get("format_rationale", "")}<br>'
                    f'구조: {format_ctx.get("structure_note", "")}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # ── 포맷 적합성 권고 (v2.7.1 신규) ──
            ff = ba.get("format_fit", {})
            if ff:
                _match = ff.get("match", True)
                _rec = ff.get("recommended_format", "")
                _cur = ff.get("current_format", project.get("format", ""))
                if _match:
                    st.success(
                        f"📐 포맷 적합성 — 확정 포맷 **{_cur}**이 소재와 맞습니다. "
                        f"{ff.get('rationale', '')}"
                    )
                else:
                    st.info(
                        f"📐 포맷 적합성 — 소재 자체는 **{_rec}** 쪽에 가깝습니다 "
                        f"(현재 확정: {_cur}). 참고 정보이며 판정이 아닙니다."
                    )
                with st.expander("📐 포맷 적합성 근거", expanded=(not _match)):
                    st.markdown(f"**사건 밀도** — {ff.get('event_density', '')}")
                    st.markdown(f"**인물 부하** — {ff.get('character_load', '')}")
                    st.markdown(f"**판단 근거** — {ff.get('rationale', '')}")
                    if not _match and ff.get("if_forced"):
                        st.markdown(f"**{_cur}를 유지할 경우** — {ff['if_forced']}")
                    st.caption(
                        "포맷 확정 권한은 작가에게 있습니다. 변경하려면 위 '포맷 확정·변경'에서 조정해 주십시오."
                    )

            # ── 훅 문장 ──
            hook = ba.get("hook_sentence", "")
            if hook:
                st.markdown(
                    f'<div style="text-align:center;padding:1.5rem 0">'
                    f'<div style="font-size:.7rem;color:var(--y);font-weight:600">HOOK</div>'
                    f'<div style="font-size:1.15rem;font-weight:600;color:var(--t);line-height:1.5">'
                    f'"{hook}"</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ── Top 3 컨셉 ──
        st.markdown("#### 🏆 Top 3 컨셉")

        cards_map = {c["id"]: c for c in bc.get("idea_cards", [])}

        for top_item in bc.get("top3", []):
            card = cards_map.get(top_item["card_id"], {})
            if card:
                col1, col2 = st.columns([5, 1])

                with col1:
                    st.markdown(
                        f'<div class="card">'
                        f'<span style="color:var(--navy);font-weight:700">#{top_item["rank"]}</span> '
                        f'<b>{card.get("title", "")}</b><br>'
                        f'<span style="color:#444">{card.get("logline_seed", "")}</span><br>'
                        f'<span style="font-size:.8rem;color:#666">'
                        f'👤 {card.get("protagonist", "")}<br>'
                        f'⚔️ {card.get("conflict", "")}<br>'
                        f'✨ {card.get("hook", "")}<br>'
                        f'🎬 {card.get("visual_image", "")}'
                        f'</span><br>'
                        f'<span style="font-size:.75rem;color:var(--dim)">'
                        f'이유: {top_item.get("reason", "")}</span>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                with col2:
                    st.markdown(
                        f'<div class="big">{card.get("total_score", 0.0)}</div>'
                        f'<div class="sm">{card.get("genre", "")}</div>',
                        unsafe_allow_html=True
                    )

        # ── 차별화 포인트 (분석 있을 때) ──
        if ba:
            differentiation = ba.get("differentiation", [])
            if differentiation:
                st.markdown("#### 💎 차별화 포인트")
                for idx, item in enumerate(differentiation, 1):
                    st.markdown(f"**{idx}.** {item}")

            # ── 개발 우선순위 ──
            dev_priority = ba.get("development_priority", {})
            if dev_priority:
                st.markdown("#### 🧭 개발 우선순위")
                col1, col2, col3 = st.columns(3)

                col1.markdown(
                    f'<div class="callout">'
                    f'<div class="cl">추천 방향</div>'
                    f'{dev_priority.get("recommended_direction", "")}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                col2.markdown(
                    f'<div class="callout">'
                    f'<div class="cl">Core Build 집중</div>'
                    f'{dev_priority.get("next_step", "")}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                col3.markdown(
                    f'<div class="callout" style="border-left-color:var(--r)">'
                    f'<div class="cl" style="color:var(--r)">리스크</div>'
                    f'{dev_priority.get("risk", "")}'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("---")

            # ── Gate A: Concept Gate ──
            gate = ba.get("gate_a_scores", {})
            avg = gate.get("average", 0)
            passed = avg >= 7.0

            st.markdown("#### 🚪 Gate A: Concept Gate")

            col1, col2 = st.columns([1, 2])

            with col1:
                gate_color = "var(--g)" if passed else "var(--r)"
                gate_label = "PASS" if passed else "FAIL"
                st.markdown(
                    f'<div style="text-align:center">'
                    f'<div class="big" style="color:{gate_color}">{avg}</div>'
                    f'<div class="sm" style="color:{gate_color};'
                    f'font-size:1rem;font-weight:700">{gate_label}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col2:
                gate_items = [
                    ("주인공", gate.get("protagonist_visible", 0)),
                    ("갈등", gate.get("conflict_one_line", 0)),
                    ("차별점", gate.get("differentiation", 0)),
                    ("포스터", gate.get("poster_image", 0)),
                    ("시장성", gate.get("market_potential", 0)),
                ]
                for name, score in gate_items:
                    bar_pct = score * 10
                    st.markdown(
                        f'<div style="display:flex;align-items:center;'
                        f'margin:.2rem 0;font-size:.8rem">'
                        f'<div style="width:60px;color:var(--dim)">{name}</div>'
                        f'<div style="flex:1;background:#E0E0E8;'
                        f'border-radius:4px;height:8px;margin:0 .5rem">'
                        f'<div style="width:{bar_pct}%;background:var(--y);'
                        f'height:100%;border-radius:4px"></div>'
                        f'</div>'
                        f'<div style="width:30px;text-align:right">{score}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            if passed:
                st.success("✅ Gate A 통과. Core Build 진행 가능.")

                # v2.5.3: Brainstorm 완료 시점 JSON 저장
                with st.expander("💾 프로젝트 JSON 저장 (Brainstorm 완료 시점)", expanded=False):
                    st.caption(
                        "브라우저를 닫거나 세션이 끊겨도 여기서 JSON 파일을 저장하면 "
                        "다음에 홈 화면의 '프로젝트 불러오기'로 복원 후 Core부터 이어서 진행할 수 있습니다."
                    )
                    title_safe_json = project.get("title", "프로젝트").replace(" ", "_")
                    ts_json = datetime.now().strftime("%Y%m%d_%H%M")
                    project_json_str = save_project_to_json(project)
                    st.download_button(
                        label="💾 프로젝트 저장 (Brainstorm 완료)",
                        data=project_json_str.encode("utf-8"),
                        file_name=f"{title_safe_json}_Brainstorm완료_{ts_json}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="dl_brainstorm",
                    )

                if st.button("🎯 Core Build 진행 →", type="primary", use_container_width=True):
                    project["stage"] = "core"
                    st.session_state.view = "core"
                    st.rerun()
            else:
                st.warning(
                    f"⚠️ Gate A 미통과 (평균 {avg}). "
                    f"아이디어 보강 또는 재실행 권장."
                )

                # v2.5.3: Override 전에도 JSON 저장 가능
                with st.expander("💾 프로젝트 JSON 저장 (Brainstorm 완료 시점)", expanded=False):
                    st.caption("Gate A 미통과 상태이지만 현재까지의 작업을 저장할 수 있습니다.")
                    title_safe_json = project.get("title", "프로젝트").replace(" ", "_")
                    ts_json = datetime.now().strftime("%Y%m%d_%H%M")
                    project_json_str = save_project_to_json(project)
                    st.download_button(
                        label="💾 프로젝트 저장 (Brainstorm 완료, Gate 미통과)",
                        data=project_json_str.encode("utf-8"),
                        file_name=f"{title_safe_json}_Brainstorm_{ts_json}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="dl_brainstorm_fail",
                    )

                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    if st.button("🔓 Override (강제 통과)"):
                        project["stage"] = "core"
                        st.session_state.view = "core"
                        st.rerun()
                with col_o2:
                    if st.button("🔄 Brainstorm 재실행"):
                        project["brainstorm_cards"] = None
                        project["brainstorm_analysis"] = None
                        st.rerun()

        # ── 전체 아이디어 카드 (접이식) ──
        all_cards = bc.get("idea_cards", [])
        if all_cards:
            with st.expander(f"📋 전체 아이디어 카드 ({len(all_cards)}개)"):
                for card in sorted(
                    all_cards,
                    key=lambda x: x.get("total_score", 0),
                    reverse=True
                ):
                    st.markdown(
                        f"**#{card['id']} {card.get('title', '')}** — "
                        f"{card.get('total_score', 0.0)}점 &nbsp; "
                        f"{card.get('logline_seed', '')}"
                    )

        # ── 분석 없을 때 fallback 네비게이션 ──
        if not ba:
            st.markdown("---")
            st.warning("⚠️ 시장 분석 + Gate A 채점이 아직 완료되지 않았습니다.")

            col_fb1, col_fb2 = st.columns(2)
            with col_fb1:
                if st.button("🔄 분석 재시도", use_container_width=True):
                    # 2단계만 재실행
                    cards_map = {c["id"]: c for c in bc.get("idea_cards", [])}
                    top3_data = [
                        cards_map[t["card_id"]]
                        for t in bc.get("top3", [])
                        if t["card_id"] in cards_map
                    ]
                    if top3_data:
                        with st.spinner("② 시장 분석 + Gate A 채점 중..."):
                            ar = call_brainstorm_analysis(
                                project["idea_text"],
                                project["genre"],
                                project["target_market"],
                                project["format"],
                                top3_data,
                                project.get("research"),
                                locked_block=_build_project_locked_block(project)
                            )
                        if ar:
                            project["brainstorm_analysis"] = ar
                            project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                            st.rerun()
            with col_fb2:
                if st.button("🎯 분석 건너뛰고 Core Build →", use_container_width=True):
                    project["stage"] = "core"
                    st.session_state.view = "core"
                    st.rerun()

    # ─── 푸터 ───
    st.markdown("---")
    st.caption(ENGINE_FOOTER)


# ═══════════════════════════════════════════════════
#  CORE BUILD
# ═══════════════════════════════════════════════════
elif st.session_state.view == "core" and st.session_state.cur:

    project = st.session_state.projects[st.session_state.cur]
    bc = project.get("brainstorm_cards", {})
    ba = project.get("brainstorm_analysis", {})

    st.markdown(f"## {project['title']}")
    st.caption(f"{project['genre']} · {project['target_market']} · {project['format']}")

    # ─── 단계 표시 ───
    render_stepper("core", project)

    # Brainstorm에서 인계받은 정보 표시
    selected_concept = None
    if bc:
        cards_map = {c["id"]: c for c in bc.get("idea_cards", [])}
        top3 = bc.get("top3", [])
        if top3:
            selected_concept = cards_map.get(top3[0].get("card_id"), {})
            if selected_concept:
                st.markdown(
                    f'<div class="callout">'
                    f'<div class="cl">🏆 선정 컨셉: {selected_concept.get("title", "")}</div>'
                    f'{selected_concept.get("logline_seed", "")}'
                    f'</div>',
                    unsafe_allow_html=True
                )

    if ba:
        dp = ba.get("development_priority", {})
        if dp.get("next_step"):
            st.markdown(
                f'<div class="callout">'
                f'<div class="cl">Core Build 집중 포인트</div>'
                f'{dp["next_step"]}'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")

    st.markdown('<div class="section-header">🎯 Core Build <span class="en">CORE DEVELOPMENT</span></div>', unsafe_allow_html=True)
    st.caption("로그라인 · 기획의도 · 세계관 · 캐릭터 · Goal/Need/Strategy를 고정합니다.")

    if st.button("🎯 Core Build 실행", type="primary"):
        if not selected_concept:
            st.error("선정된 컨셉이 없습니다. Brainstorm을 먼저 실행해주세요.")
        else:
            with st.spinner("① Core Build 생성 중... (약 30–40초)"):
                core_result = call_core_build_main(
                    project["idea_text"], project["genre"],
                    project["target_market"], project["format"],
                    selected_concept, project.get("research"),
                    locked_block=_build_project_locked_block(project),
                    fact_based=project.get("fact_based", False),
                    historical=project.get("historical", False),
                    film_type=project.get("film_type", ""),
                )
            if core_result:
                project["core"] = core_result
                project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                with st.spinner("② Gate B + Gate C 채점 중... (약 10–20초)"):
                    gate_result = call_core_gate(core_result)
                if gate_result:
                    project["core_gate"] = gate_result
                    project["final_score"] = gate_result.get("five_axis_scores", {}).get("final_score")
                    project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.rerun()

    # ── Core Build 결과 표시 ──
    if project.get("core"):
        core = project["core"]

        # Logline Pack
        st.markdown("#### 📝 Logline Pack")
        lp = core.get("logline_pack", {})
        for label, key in [("Original", "original"), ("Washed", "washed"),
                           ("투자자용", "investor"), ("감독용", "director"),
                           ("캐릭터 훅", "character_hook")]:
            val = lp.get(key, "")
            if val:
                st.markdown(f'<div class="callout"><div class="cl">{label}</div>{val}</div>', unsafe_allow_html=True)

        # Goal / Need / Strategy
        st.markdown("#### 🎯 Goal / Need / Strategy")
        gns = core.get("goal_need_strategy", {})
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="callout"><div class="cl">GOAL</div>{gns.get("goal","")}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="callout"><div class="cl">NEED</div>{gns.get("need","")}</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="callout"><div class="cl">STRATEGY</div>{gns.get("strategy","")}</div>', unsafe_allow_html=True)
        cr, ce = st.columns(2)
        cr.markdown(f'<div class="callout" style="border-left-color:var(--r)"><div class="cl" style="color:var(--r)">RISK</div>{gns.get("risk","")}</div>', unsafe_allow_html=True)
        ce.markdown(f'<div class="callout" style="border-left-color:var(--g)"><div class="cl" style="color:var(--g)">ENDING PAYOFF</div>{gns.get("ending_payoff","")}</div>', unsafe_allow_html=True)

        # Narrative Drive (BJND)
        nd = core.get("narrative_drive", {})
        if nd and nd.get("desire_origin"):
            origin = nd.get("desire_origin", "")
            origin_kr = "상실(Loss)" if origin == "loss" else "결핍(Lack)" if origin == "lack" else origin
            st.markdown(
                f'<div class="callout" style="border-left-color:#9B59B6">'
                f'<div class="cl" style="color:#9B59B6">🔮 서사동력 — Narrative Drive</div>'
                f'<b>{origin_kr}</b>: {nd.get("origin_detail","")}<br>'
                f'아크: {nd.get("arc_direction","")} · 해결전략: {nd.get("resolution_strategy","")}<br>'
                f'<span style="font-size:.8rem;color:#666">Goal↔Need 간극: {nd.get("goal_need_gap","")}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        # Project Intent (소재 · 장르 · 시장분석)
        st.markdown("#### 📋 기획의도 — 왜 이 작품을 기획하는가")
        pi = core.get("project_intent", {})

        if pi.get("subject"):
            st.markdown(f'<div class="callout"><div class="cl">소재 — 왜 이 소재인가</div>{pi["subject"]}</div>', unsafe_allow_html=True)

        if pi.get("genre_approach"):
            st.markdown(f'<div class="callout"><div class="cl">장르 — 왜 이 장르인가</div>{pi["genre_approach"]}</div>', unsafe_allow_html=True)

        if pi.get("market_rationale"):
            st.markdown(f'<div class="callout"><div class="cl">시장 — 왜 지금 이 시장인가</div>{pi["market_rationale"]}</div>', unsafe_allow_html=True)

        cp1, cp2 = st.columns(2)
        if pi.get("pitch"):
            cp1.markdown(f'<div class="callout"><div class="cl">Elevator Pitch</div>{pi["pitch"]}</div>', unsafe_allow_html=True)
        if pi.get("theme"):
            cp2.markdown(f'<div class="callout"><div class="cl">Theme</div>{pi["theme"]}</div>', unsafe_allow_html=True)
        if pi.get("tone_manner"):
            st.markdown(f"**Tone & Manner:** {', '.join(pi['tone_manner'])}")

        # World Build
        st.markdown("#### 🌍 세계관")
        wb = core.get("world_build", {})
        cw1, cw2 = st.columns(2)
        with cw1:
            for label, key in [("시간","time"),("공간","space"),("규칙","rules"),("금기","taboo"),("권력구조","power_structure")]:
                val = wb.get(key, "")
                if val:
                    st.markdown(f"**{label}:** {val}")
        with cw2:
            if wb.get("visual_keywords"):
                st.markdown(f"**시각 키워드:** {', '.join(wb['visual_keywords'])}")
            if wb.get("conflict_points"):
                st.markdown("**충돌 포인트:**")
                for cp in wb["conflict_points"]:
                    st.markdown(f"- {cp}")

        # Characters
        st.markdown("#### 🎭 캐릭터")
        role_labels = {"protagonist":"주인공","antagonist":"적대자","ally":"조력자","mirror":"거울","catalyst":"촉매자","subplot_lead":"서브플롯 리드"}
        all_display_chars = core.get("characters", []) + core.get("extended_characters", [])
        for ch in all_display_chars:
            role = role_labels.get(ch.get("role",""), ch.get("role",""))
            st.markdown(
                f'<div class="card"><div class="cl">{role}: {ch.get("name","")}</div>'
                f'{ch.get("description","")}<br>'
                f'<span style="font-size:.8rem;color:#666">'
                f'🎯 {ch.get("goal","")}<br>💔 {ch.get("need",ch.get("flaw",""))}<br>'
                f'⚡ {ch.get("strategy","")}<br>🗣️ {ch.get("dialogue_tone","")}</span></div>',
                unsafe_allow_html=True
            )

        # Relationship
        rel = core.get("relationship_map", [])
        if rel:
            st.markdown("#### 🔗 관계도")
            for r in rel:
                st.markdown(f"- {r}")

        # ── 매력 설계도 (Attraction Design) ──
        ad = core.get("attraction_design", {})
        if ad:
            st.markdown("---")
            st.markdown('<div class="section-header">⚡ 매력 설계도 <span class="en">ATTRACTION DESIGN</span></div>', unsafe_allow_html=True)
            st.caption("이 이야기가 멈출 수 없게 만드는 핵심 설계 — Writer/Series/Novel Engine에 자동 전달됩니다.")

            # 첫 장면
            oh = ad.get("opening_hook", {})
            if oh:
                hook_type = oh.get("type", "")
                hook_desc = oh.get("description", "")
                hook_check = oh.get("forbidden_check", "")
                st.markdown(
                    f'<div class="card" style="border-left:4px solid var(--y)">'
                    f'<div class="cl">🎬 첫 장면 — OPENING HOOK</div>'
                    f'<div style="font-size:.75rem;color:var(--navy);font-weight:700;margin-bottom:.4rem">[{hook_type}]</div>'
                    f'<p style="line-height:1.7;margin:.3rem 0">{hook_desc}</p>'
                    f'<div style="font-size:.75rem;color:var(--g);margin-top:.4rem">✓ {hook_check}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # 배반 포인트
            tp = ad.get("twist_point", {})
            if tp:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        f'<div class="ri"><div class="rl">👀 관객이 예상하는 전개</div>'
                        f'{tp.get("expected_direction", "")}</div>',
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown(
                        f'<div class="ri" style="border-left:3px solid var(--y)">'
                        f'<div class="rl">💥 배반 포인트 — 이 이야기만의 방향</div>'
                        f'{tp.get("betrayal", "")}</div>',
                        unsafe_allow_html=True
                    )
                if tp.get("why_more_true"):
                    st.markdown(
                        f'<div class="callout"><div class="cl">배반이 더 진실된 이유</div>'
                        f'{tp["why_more_true"]}</div>',
                        unsafe_allow_html=True
                    )

            # Water Cooler Moment
            wc = ad.get("water_cooler_moment", {})
            if wc:
                st.markdown(
                    f'<div class="card" style="background:var(--light-bg)">'
                    f'<div class="cl">💬 Water Cooler Moment — 말하고 싶어지는 장면</div>'
                    f'<p style="font-size:.95rem;font-weight:700;margin:.3rem 0">{wc.get("scene_or_setup","")}</p>'
                    f'<div style="font-size:.8rem;color:var(--dim)">{wc.get("why_memorable","")}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # 한국 구체성 + 빌런 논리
            c1, c2 = st.columns(2)
            with c1:
                ks = ad.get("korean_specificity", [])
                if ks:
                    ks_html = "<br>".join([f"• {k}" for k in ks])
                    st.markdown(
                        f'<div class="ri"><div class="rl">🇰🇷 한국 구체성</div>{ks_html}</div>',
                        unsafe_allow_html=True
                    )
            with c2:
                vl = ad.get("villain_logic", "")
                if vl:
                    st.markdown(
                        f'<div class="ri"><div class="rl">🖤 빌런의 논리</div>{vl}</div>',
                        unsafe_allow_html=True
                    )

            # 감정 폭발 설계
            ee = ad.get("emotional_explosion", {})
            if ee:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(
                        f'<div class="ri"><div class="rl">🔒 감정 억압 구간</div>'
                        f'{ee.get("suppression","")}</div>',
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown(
                        f'<div class="ri" style="border-left:3px solid var(--r)">'
                        f'<div class="rl">💣 폭발 장면</div>'
                        f'{ee.get("explosion_moment","")}</div>',
                        unsafe_allow_html=True
                    )

            # 금지 방향
            fd = ad.get("forbidden_directions", [])
            if fd:
                fd_html = " &nbsp;|&nbsp; ".join([f'<span style="color:var(--r)">✗ {f}</span>' for f in fd])
                st.markdown(
                    f'<div class="ri"><div class="rl">🚫 절대 가면 안 되는 방향</div>{fd_html}</div>',
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # Gate B + C
        if project.get("core_gate"):
            cg = project["core_gate"]
            gb = cg.get("gate_b_drive", {})
            gc = cg.get("gate_c_character", {})
            fa = cg.get("five_axis_scores", {})

            st.markdown("#### 🚪 Gate B: Drive Gate")
            c1, c2 = st.columns([1, 2])
            with c1:
                gb_avg = gb.get("average", 0)
                cl = "var(--g)" if gb_avg >= 7.0 else "var(--r)"
                lb = "PASS" if gb_avg >= 7.0 else "FAIL"
                st.markdown(f'<div style="text-align:center"><div class="big" style="color:{cl}">{gb_avg}</div><div class="sm" style="color:{cl};font-size:1rem;font-weight:700">{lb}</div></div>', unsafe_allow_html=True)
            with c2:
                for nm, sc in [("Goal 선명도",gb.get("goal_clarity",0)),("Need 자연스러움",gb.get("need_from_loss",0)),("Strategy 창의성",gb.get("strategy_creative",0)),("실패 대가",gb.get("failure_cost",0))]:
                    st.markdown(f'<div style="display:flex;align-items:center;margin:.2rem 0;font-size:.8rem"><div style="width:110px;color:var(--dim)">{nm}</div><div style="flex:1;background:#E0E0E8;border-radius:4px;height:8px;margin:0 .5rem"><div style="width:{sc*10}%;background:var(--y);height:100%;border-radius:4px"></div></div><div style="width:30px;text-align:right">{sc}</div></div>', unsafe_allow_html=True)
            if gb.get("feedback"):
                st.caption(gb["feedback"])

            st.markdown("#### 🚪 Gate C: Character Gate")
            c1, c2 = st.columns([1, 2])
            with c1:
                gc_avg = gc.get("average", 0)
                cl = "var(--g)" if gc_avg >= 7.0 else "var(--r)"
                lb = "PASS" if gc_avg >= 7.0 else "FAIL"
                st.markdown(f'<div style="text-align:center"><div class="big" style="color:{cl}">{gc_avg}</div><div class="sm" style="color:{cl};font-size:1rem;font-weight:700">{lb}</div></div>', unsafe_allow_html=True)
            with c2:
                for nm, sc in [("주인공/적대자 논리",gc.get("protagonist_antagonist_logic",0)),("조연 입체성",gc.get("supporting_not_functional",0)),("관계축 갈등",gc.get("relationship_produces_conflict",0))]:
                    st.markdown(f'<div style="display:flex;align-items:center;margin:.2rem 0;font-size:.8rem"><div style="width:110px;color:var(--dim)">{nm}</div><div style="flex:1;background:#E0E0E8;border-radius:4px;height:8px;margin:0 .5rem"><div style="width:{sc*10}%;background:var(--y);height:100%;border-radius:4px"></div></div><div style="width:30px;text-align:right">{sc}</div></div>', unsafe_allow_html=True)
            if gc.get("feedback"):
                st.caption(gc["feedback"])

            # 5축 스코어
            st.markdown("---")
            st.markdown("#### 📊 Development Fit Score")
            final = fa.get("final_score", 0)
            verdict = fa.get("verdict", "")
            vc = {"개발 진행":"var(--g)","개발 보류":"var(--y)","구조 재설계":"var(--r)"}.get(verdict,"var(--dim)")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f'<div style="text-align:center"><div class="big">{final}</div><div class="sm" style="color:{vc};font-size:1rem;font-weight:700">{verdict}</div></div>', unsafe_allow_html=True)
            with c2:
                for nm, sc in [("Goal",fa.get("goal",0)),("Need",fa.get("need",0)),("Strategy",fa.get("strategy",0)),("Structure",fa.get("structure",0)),("Character/Concept",fa.get("character_concept",0))]:
                    st.markdown(f'<div style="display:flex;align-items:center;margin:.2rem 0;font-size:.8rem"><div style="width:110px;color:var(--dim)">{nm}</div><div style="flex:1;background:#E0E0E8;border-radius:4px;height:8px;margin:0 .5rem"><div style="width:{sc*10}%;background:var(--y);height:100%;border-radius:4px"></div></div><div style="width:30px;text-align:right">{sc}</div></div>', unsafe_allow_html=True)

            # ═══════════════════════════════════════
            # REALITY GATE (v2.7.0 신규)
            # 위치 원칙: Core 직후 · Character Bible 이전.
            #   Core에서 로그라인·시그니처 모먼트·엔딩 이미지가 확정되므로
            #   Treatment 직전에 두면 되돌릴 비용이 너무 크다.
            # ═══════════════════════════════════════
            st.markdown("---")
            st.markdown('<div class="section-header">🔍 Reality Gate <span class="en">사실성 검문</span></div>', unsafe_allow_html=True)
            st.caption(
                "LOCKED와 Core에 현실 제도·절차·직업 역할에 위배되는 전제가 있는지 점검합니다. "
                "장르 관습·의도적 왜곡은 적출하지 않습니다. 채택 여부는 전적으로 작가가 결정합니다."
            )

            rg = project.get("reality_gate")

            if not rg:
                if st.button("🔍 Reality Gate 실행", key="run_reality_gate", use_container_width=True):
                    with st.spinner("제도·절차 사실성 점검 중..."):
                        rg_result = call_reality_gate(project, core)
                    if rg_result:
                        for _i, _iss in enumerate(rg_result.get("issues", []) or []):
                            _iss["status"] = "pending"
                        project["reality_gate"] = rg_result
                        project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.rerun()
                st.info(
                    "건너뛰어도 Character Bible로 진행할 수 있습니다. "
                    "다만 LOCKED에 사실 오류가 있으면 Treatment·Writer Engine까지 그대로 전파됩니다."
                )
            else:
                rg_issues = rg.get("issues", []) or []
                pending = [x for x in rg_issues if x.get("status", "pending") == "pending"]
                applied = [x for x in rg_issues if x.get("status") == "applied"]
                ignored = [x for x in rg_issues if x.get("status") == "ignored"]

                if rg.get("verdict") == "CLEAR" or not rg_issues:
                    st.success("✅ 사실성 위배 사항 없음. 제도·절차 층위에서 깨끗합니다.")
                else:
                    sev_color = {"CRITICAL": "var(--r)", "MAJOR": "var(--y)", "MINOR": "var(--dim)"}
                    n_crit = len([x for x in rg_issues if x.get("severity") == "CRITICAL"])
                    if n_crit:
                        st.error(
                            f"🔴 CRITICAL {n_crit}건 포함 총 {len(rg_issues)}건 적출. "
                            "CRITICAL은 작품 전제 자체가 성립하지 않는 항목입니다."
                        )
                    else:
                        st.warning(f"⚠️ {len(rg_issues)}건 적출. 미처리 {len(pending)}건.")

                    for idx, iss in enumerate(rg_issues):
                        sev = iss.get("severity", "MINOR")
                        status = iss.get("status", "pending")
                        badge = {"applied": "✅ 반영", "ignored": "⏭️ 무시", "pending": "● 미처리"}[status]
                        with st.expander(
                            f"{badge} · [{sev}] {iss.get('domain', '')} — {iss.get('error', '')[:40]}",
                            expanded=(status == "pending" and sev == "CRITICAL")
                        ):
                            st.markdown(
                                f'<div style="border-left:4px solid {sev_color.get(sev, "var(--dim)")};'
                                f'padding-left:10px;font-size:.85rem">'
                                f'<b>위치</b><br>{iss.get("location", "")}<br><br>'
                                f'<b>오류</b><br>{iss.get("error", "")}<br><br>'
                                f'<b>실제</b><br>{iss.get("reality", "")}<br><br>'
                                f'<b>방치 시 영향</b><br>{iss.get("impact", "")}'
                                f'</div>',
                                unsafe_allow_html=True
                            )
                            alts = iss.get("alternatives", []) or []
                            if alts:
                                st.markdown("**대안 (원 설계 의도 보존)**")
                                for ai, alt in enumerate(alts, 1):
                                    st.markdown(f"{ai}. {alt}")

                            sug = iss.get("suggested_locked", "")
                            if sug:
                                st.markdown("**LOCKED 교체안**")
                                st.code(sug, language=None)

                            if status == "pending":
                                cA, cB = st.columns(2)
                                with cA:
                                    if st.button("✅ 이 교체안 LOCKED에 반영", key=f"rg_apply_{idx}", use_container_width=True):
                                        loc = (iss.get("location") or "").strip()
                                        cur_locked = project.get("locked_items", []) or []
                                        hit = -1
                                        if loc:
                                            probe = loc[:20]
                                            for li, litem in enumerate(cur_locked):
                                                if probe and probe in litem:
                                                    hit = li
                                                    break
                                        if hit >= 0 and sug:
                                            cur_locked[hit] = sug
                                            project["locked_items"] = cur_locked
                                            iss["status"] = "applied"
                                            iss["applied_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                            project["updated_at"] = iss["applied_at"]
                                            st.success("LOCKED 교체 완료. Core Build를 재실행해야 하류에 반영됩니다.")
                                            st.rerun()
                                        else:
                                            iss["status"] = "applied"
                                            st.warning(
                                                "LOCKED에서 해당 항목을 자동으로 찾지 못했습니다. "
                                                "아이디어 화면의 'LOCKED 편집'에서 위 교체안을 직접 반영해 주십시오."
                                            )
                                with cB:
                                    if st.button("⏭️ 의도된 설정 — 무시", key=f"rg_ignore_{idx}", use_container_width=True):
                                        iss["status"] = "ignored"
                                        project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                                        st.rerun()

                if rg.get("author_note"):
                    st.caption(f"작가 의도로 판단된 항목: {rg['author_note']}")

                if applied:
                    st.warning(
                        f"LOCKED가 {len(applied)}건 교체되었습니다. "
                        "교체된 전제를 Core에 반영하려면 **Core Build 재실행**이 필요합니다. "
                        "재실행하지 않으면 현재 Core는 교체 전 전제 위에 남아 있습니다."
                    )

                cR1, cR2 = st.columns(2)
                with cR1:
                    if st.button("🔄 Reality Gate 재실행", key="rerun_reality_gate", use_container_width=True):
                        project["reality_gate"] = None
                        st.rerun()
                with cR2:
                    if applied and st.button("🎯 Core Build 재실행 (교체 LOCKED 반영)", key="rg_core_rebuild", use_container_width=True):
                        project["core"] = None
                        project["core_gate"] = None
                        project["reality_gate"] = None
                        st.rerun()

            st.markdown("---")

            if verdict == "개발 진행":
                st.success(f"✅ {verdict}. Character Bible 진행 가능.")

                # v2.5.3: Core 완료 시점 JSON 저장
                with st.expander("💾 프로젝트 JSON 저장 (Core 완료 시점)", expanded=False):
                    st.caption(
                        "Core Build까지 완료되었습니다. 여기서 JSON 파일을 저장하면 "
                        "Character Bible 단계에서 문제가 생겨도 Core까지의 작업을 잃지 않습니다. "
                        "다음에 홈 화면의 '프로젝트 불러오기'로 복원 후 Character Bible부터 이어서 진행할 수 있습니다."
                    )
                    title_safe_json = project.get("title", "프로젝트").replace(" ", "_")
                    ts_json = datetime.now().strftime("%Y%m%d_%H%M")
                    project_json_str = save_project_to_json(project)
                    st.download_button(
                        label="💾 프로젝트 저장 (Core 완료)",
                        data=project_json_str.encode("utf-8"),
                        file_name=f"{title_safe_json}_Core완료_{ts_json}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="dl_core",
                    )

                if st.button("📖 Character Bible 진행 →", type="primary", use_container_width=True):
                    st.session_state.view = "char_bible"
                    st.rerun()
            elif verdict == "개발 보류":
                st.warning(f"⚠️ {verdict}. Core Build 보강 필요.")

                # v2.5.3: Core 보류 상태에서도 저장 가능
                with st.expander("💾 프로젝트 JSON 저장 (Core 완료, Gate 보류)", expanded=False):
                    st.caption("Gate B+C 보류 상태이지만 현재까지의 작업을 저장할 수 있습니다.")
                    title_safe_json = project.get("title", "프로젝트").replace(" ", "_")
                    ts_json = datetime.now().strftime("%Y%m%d_%H%M")
                    project_json_str = save_project_to_json(project)
                    st.download_button(
                        label="💾 프로젝트 저장 (Core, Gate 보류)",
                        data=project_json_str.encode("utf-8"),
                        file_name=f"{title_safe_json}_Core_{ts_json}.json",
                        mime="application/json",
                        use_container_width=True,
                        key="dl_core_hold",
                    )

                col_cv1, col_cv2 = st.columns(2)
                with col_cv1:
                    if st.button("🔓 Override → Character Bible"):
                        st.session_state.view = "char_bible"
                        st.rerun()
                with col_cv2:
                    if st.button("🔄 Core Build 재실행"):
                        project["core"] = None
                        project["core_gate"] = None
                        st.rerun()
            else:
                st.error(f"🔴 {verdict}. Brainstorm 재검토 필요.")

        else:
            st.warning("⚠️ Gate B + C 채점이 완료되지 않았습니다.")
            if st.button("🔄 Gate 재시도"):
                with st.spinner("Gate B + C 채점 중..."):
                    gate_result = call_core_gate(core)
                if gate_result:
                    project["core_gate"] = gate_result
                    project["final_score"] = gate_result.get("five_axis_scores", {}).get("final_score")
                    st.rerun()

    else:
        st.markdown(
            '<div style="text-align:center;padding:3rem 0;color:var(--dim)">'
            '🎯 Core Build를 실행하면 여기에 결과가 표시됩니다.<br>'
            'Logline Pack · Project Intent · World Build · Character Build'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption(ENGINE_FOOTER)


# ═══════════════════════════════════════════════════
#  CHARACTER BIBLE
# ═══════════════════════════════════════════════════
elif st.session_state.view == "char_bible" and st.session_state.cur:

    project = st.session_state.projects[st.session_state.cur]
    core = project.get("core", {})

    st.markdown(f"## {project['title']}")
    st.caption(f"{project['genre']} · {project['target_market']} · {project['format']}")
    render_stepper("char_bible", project)

    lp = core.get("logline_pack", {})
    if lp.get("washed"):
        st.markdown(f'<div class="callout"><div class="cl">Logline</div>{lp["washed"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📖 Character Bible <span class="en">CHARACTER DESIGN BIBLE</span></div>', unsafe_allow_html=True)
    st.caption("백스토리 · 비밀 · 말투 규칙 · 대사 샘플 · 관계 태도 · 변화 궤적 — Writer Engine이 일관된 인물을 쓰기 위한 설계서")

    if not project.get("char_bible"):
        if st.button("📖 Character Bible 생성", type="primary"):
            with st.spinner("캐릭터 바이블 설계 중... (캐릭터당 약 30초, 4–8명 기준 약 2–4분)"):
                result = call_character_bible(
                    core, project["genre"], project["format"],
                    locked_block=_build_project_locked_block(project),
                    fact_based=project.get("fact_based", False),
                    historical=project.get("historical", False),
                    film_type=project.get("film_type", ""),
                )
            if result:
                project["char_bible"] = result
                project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.rerun()

    bible = project.get("char_bible", {})
    if bible:
        chars = bible.get("characters", [])
        role_labels = {"protagonist":"주인공","antagonist":"적대자","ally":"조력자","mirror":"거울","catalyst":"촉매자","subplot_lead":"서브플롯 리드"}
        role_emoji = {"protagonist":"🔥","antagonist":"🖤","ally":"💙","mirror":"🪞","catalyst":"⚡","subplot_lead":"🌐"}

        for ch in chars:
            role = role_labels.get(ch.get("role",""), ch.get("role",""))
            emoji = role_emoji.get(ch.get("role",""), "👤")
            name = ch.get("name", "")
            age = ch.get("age", "")

            st.markdown(f'<div class="section-header">{emoji} {role}: {name} ({age}) <span class="en">{ch.get("role","").upper()}</span></div>', unsafe_allow_html=True)

            # 외형 & 직업
            st.markdown(f'<div class="callout"><div class="cl">외형 · 첫인상</div>{ch.get("appearance","")}</div>', unsafe_allow_html=True)
            if ch.get("occupation"):
                st.markdown(f'<div class="ri"><div class="rl">직업/위치</div>{ch.get("occupation","")}</div>', unsafe_allow_html=True)

            # 욕망/결핍/결점
            c1, c2, c3 = st.columns(3)
            c1.markdown(f'<div class="callout"><div class="cl">GOAL</div>{ch.get("goal","")}</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="callout"><div class="cl">NEED</div>{ch.get("need","")}</div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="callout"><div class="cl">FLAW</div>{ch.get("flaw","")}</div>', unsafe_allow_html=True)

            # 백스토리
            st.markdown(f'<div class="card"><div class="cl">📜 백스토리</div><p style="line-height:1.7">{ch.get("backstory","")}</p></div>', unsafe_allow_html=True)

            # 비밀 & 신념 & 두려움
            c4, c5, c6 = st.columns(3)
            c4.markdown(f'<div class="ri"><div class="rl">🔒 비밀</div>{ch.get("secret","")}</div>', unsafe_allow_html=True)
            c5.markdown(f'<div class="ri"><div class="rl">⚖️ 신념</div>{ch.get("belief","")}</div>', unsafe_allow_html=True)
            c6.markdown(f'<div class="ri"><div class="rl">😰 두려움</div>{ch.get("fear","")}</div>', unsafe_allow_html=True)

            # 습관
            habits = ch.get("habits", [])
            if habits:
                habits_html = " · ".join(habits) if isinstance(habits, list) else str(habits)
                st.markdown(f'<div class="ri"><div class="rl">🔄 반복 습관</div>{habits_html}</div>', unsafe_allow_html=True)

            # 말투 규칙
            sp = ch.get("speech_pattern", [])
            if sp:
                sp_list = sp if isinstance(sp, list) else [sp]
                sp_html = "<br>".join([f"• {s}" for s in sp_list])
                st.markdown(f'<div class="card"><div class="cl">🗣️ 말투 규칙 (SPEECH PATTERN)</div>{sp_html}</div>', unsafe_allow_html=True)

            # 대사 샘플
            sl = ch.get("sample_lines", {})
            if sl:
                sl_labels = {"normal":"평상시","angry":"분노","vulnerable":"취약"}
                sl_html = ""
                for k, v in sl.items():
                    label = sl_labels.get(k, k)
                    sl_html += f'<div style="margin:.3rem 0"><b style="color:var(--navy);font-size:.75rem">[{label}]</b> <i>\u2018{v}\u2019</i></div>'
                st.markdown(f'<div class="card"><div class="cl">💬 대사 샘플 (SAMPLE LINES)</div>{sl_html}</div>', unsafe_allow_html=True)

            # 관계별 태도
            ra = ch.get("relationship_attitudes", [])
            if ra:
                ra_list = ra if isinstance(ra, list) else [ra]
                ra_html = "<br>".join([f"• {r}" for r in ra_list])
                st.markdown(f'<div class="card"><div class="cl">🔗 관계별 태도</div>{ra_html}</div>', unsafe_allow_html=True)

            # 변화 궤적
            arc = ch.get("arc_detail", {})
            if arc:
                st.markdown(
                    f'<div class="card"><div class="cl">📈 변화 궤적 (ARC)</div>'
                    f'<div style="margin:.3rem 0"><b style="color:var(--navy);font-size:.75rem">[1막 끝]</b> {arc.get("act1_end","")}</div>'
                    f'<div style="margin:.3rem 0"><b style="color:var(--navy);font-size:.75rem">[미드포인트]</b> {arc.get("midpoint","")}</div>'
                    f'<div style="margin:.3rem 0"><b style="color:var(--navy);font-size:.75rem">[클라이맥스]</b> {arc.get("climax","")}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            st.markdown("")  # spacer

        # ── 캐릭터 관계도 ──
        st.markdown("---")
        st.markdown('<div class="section-header">🕸️ 캐릭터 관계도 <span class="en">CHARACTER MAP</span></div>', unsafe_allow_html=True)

        def render_relationship_map(chars):
            import math, html as _html

            role_colors = {
                "protagonist": "#FFCB05",
                "antagonist":  "#D32F2F",
                "ally":        "#2EC484",
                "mirror":      "#7B68EE",
                "catalyst":    "#FF8C00",
                "subplot_lead":"#20B2AA",
            }
            role_labels_kr = {
                "protagonist":"주인공","antagonist":"적대자","ally":"조력자",
                "mirror":"거울","catalyst":"촉매자","subplot_lead":"서브플롯",
            }

            # 관계 키워드 → 유형 매핑
            def classify_rel(text):
                t = text.lower()
                if any(k in t for k in ["죽이","살해","적","증오","혐오","원수","복수","배신","이용","조종","견제"]):
                    return "hostile"
                if any(k in t for k in ["사랑","좋아","연인","설레","끌","호감","연모","연인"]):
                    return "love"
                if any(k in t for k in ["돕","협력","신뢰","지지","동료","우정","친구","함께","의지"]):
                    return "ally"
                if any(k in t for k in ["질투","경쟁","라이벌","갈등","충돌","대립"]):
                    return "rival"
                if any(k in t for k in ["가르","멘토","스승","보호","이끌","안내"]):
                    return "mentor"
                return "neutral"

            rel_style = {
                "hostile": {"color":"#D32F2F","label":"⚔️ 적대","dash":"8,4"},
                "love":    {"color":"#FF69B4","label":"❤️ 사랑","dash":"0"},
                "ally":    {"color":"#2EC484","label":"🤝 협력","dash":"0"},
                "rival":   {"color":"#FF8C00","label":"🥊 경쟁","dash":"6,3"},
                "mentor":  {"color":"#7B68EE","label":"🎓 멘토","dash":"0"},
                "neutral": {"color":"#AAAAAA","label":"— 중립","dash":"4,4"},
            }

            n = len(chars)
            if n == 0:
                return

            # 원형 배치 좌표 계산
            cx, cy, r = 400, 300, 200
            positions = []
            for i in range(n):
                angle = (2 * math.pi * i / n) - math.pi / 2
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle)
                positions.append((x, y))

            # 관계 엣지 파싱
            edges = []
            for i, ch in enumerate(chars):
                ra = ch.get("relationship_attitudes", [])
                if isinstance(ra, list):
                    for rel_text in ra:
                        for j, other in enumerate(chars):
                            if i == j:
                                continue
                            other_name = other.get("name", "")
                            if other_name and other_name in rel_text:
                                rel_type = classify_rel(rel_text)
                                short = rel_text.replace(f"→ {other_name}:", "").replace(f"→{other_name}:", "").strip()
                                short = short[:30] + "…" if len(short) > 30 else short
                                edges.append((i, j, rel_type, short))

            # SVG 생성
            svg_lines = [
                f'<svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg" '
                f'style="width:100%;max-width:800px;background:#F7F7F5;border-radius:16px;'
                f'border:1px solid #E2E2E0;font-family:Pretendard,sans-serif">',
                '<defs>',
            ]
            # 화살표 마커
            for rtype, rs in rel_style.items():
                svg_lines.append(
                    f'<marker id="arr_{rtype}" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
                    f'<path d="M0,0 L0,6 L8,3 z" fill="{rs["color"]}"/></marker>'
                )
            svg_lines.append('</defs>')

            # 엣지 선
            drawn = set()
            for (i, j, rtype, label) in edges:
                key = tuple(sorted([i, j]))
                rs = rel_style[rtype]
                x1, y1 = positions[i]
                x2, y2 = positions[j]
                # 살짝 오프셋 (양방향 선 구분)
                offset = 8 if (i, j) > (j, i) else -8
                mx = (x1 + x2) / 2 + offset * ((y2 - y1) / max(abs(x2 - x1) + abs(y2 - y1), 1))
                my = (y1 + y2) / 2 - offset * ((x2 - x1) / max(abs(x2 - x1) + abs(y2 - y1), 1))

                dash_attr = f'stroke-dasharray="{rs["dash"]}"' if rs["dash"] != "0" else ""
                svg_lines.append(
                    f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                    f'stroke="{rs["color"]}" stroke-width="2" {dash_attr} '
                    f'marker-end="url(#arr_{rtype})" opacity="0.7"/>'
                )
                # 관계 레이블
                escaped = _html.escape(label)
                svg_lines.append(
                    f'<text x="{mx:.0f}" y="{my:.0f}" text-anchor="middle" '
                    f'font-size="9" fill="{rs["color"]}" font-weight="600" '
                    f'style="paint-order:stroke" stroke="white" stroke-width="3">'
                    f'{escaped}</text>'
                )

            # 노드 원
            node_r = 44
            for i, ch in enumerate(chars):
                x, y = positions[i]
                role = ch.get("role", "neutral")
                color = role_colors.get(role, "#888888")
                name = _html.escape(ch.get("name", f"캐릭터{i+1}"))
                role_kr = role_labels_kr.get(role, role)

                # 외곽 링
                svg_lines.append(
                    f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{node_r+4}" '
                    f'fill="{color}" opacity="0.15"/>'
                )
                # 메인 원
                svg_lines.append(
                    f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{node_r}" '
                    f'fill="white" stroke="{color}" stroke-width="3"/>'
                )
                # 이름
                svg_lines.append(
                    f'<text x="{x:.0f}" y="{y-6:.0f}" text-anchor="middle" '
                    f'font-size="13" font-weight="900" fill="#191970">{name}</text>'
                )
                # 역할
                svg_lines.append(
                    f'<text x="{x:.0f}" y="{y+10:.0f}" text-anchor="middle" '
                    f'font-size="10" fill="{color}" font-weight="700">{role_kr}</text>'
                )

            svg_lines.append('</svg>')

            # 범례
            legend_items = []
            used_types = {e[2] for e in edges}
            for rtype in ["love","ally","mentor","rival","hostile","neutral"]:
                if rtype in used_types:
                    rs = rel_style[rtype]
                    legend_items.append(
                        f'<span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px;">'
                        f'<svg width="24" height="6"><line x1="0" y1="3" x2="24" y2="3" '
                        f'stroke="{rs["color"]}" stroke-width="2.5" '
                        f'stroke-dasharray="{rs["dash"] if rs["dash"] != "0" else ""}"/></svg>'
                        f'<span style="font-size:0.78rem;color:#444">{rs["label"]}</span></span>'
                    )

            svg_html = "\n".join(svg_lines)
            legend_html = "".join(legend_items)

            st.markdown(
                f'<div style="text-align:center">{svg_html}</div>'
                f'<div style="text-align:center;margin-top:8px;padding:8px 0">{legend_html}</div>',
                unsafe_allow_html=True
            )

        render_relationship_map(chars)

        # Structure 진행 버튼
        st.markdown("---")
        st.success("✅ Character Bible 완료. Structure Build 진행 가능.")

        # v2.5.3: Character Bible 완료 시점 JSON 저장
        with st.expander("💾 프로젝트 JSON 저장 (Character Bible 완료 시점)", expanded=False):
            st.caption(
                "Character Bible까지 완료되었습니다. 여기서 JSON 파일을 저장하면 "
                "Structure 단계에서 문제가 생겨도 Character Bible까지의 작업을 잃지 않습니다. "
                "다음에 홈 화면의 '프로젝트 불러오기'로 복원 후 Structure부터 이어서 진행할 수 있습니다."
            )
            title_safe_json = project.get("title", "프로젝트").replace(" ", "_")
            ts_json = datetime.now().strftime("%Y%m%d_%H%M")
            project_json_str = save_project_to_json(project)
            st.download_button(
                label="💾 프로젝트 저장 (Character Bible 완료)",
                data=project_json_str.encode("utf-8"),
                file_name=f"{title_safe_json}_Bible완료_{ts_json}.json",
                mime="application/json",
                use_container_width=True,
                key="dl_bible",
            )

        if st.button("🏗️ Structure Build 진행 →", type="primary", use_container_width=True):
            st.session_state.view = "structure"
            st.rerun()

    else:
        st.markdown(
            '<div style="text-align:center;padding:3rem 0;color:var(--dim)">'
            '📖 Character Bible을 생성하면 여기에 결과가 표시됩니다.<br>'
            '백스토리 · 비밀 · 말투 규칙 · 대사 샘플 · 관계 태도 · 변화 궤적'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption(ENGINE_FOOTER)


# ═══════════════════════════════════════════════════
#  STRUCTURE BUILD
# ═══════════════════════════════════════════════════
elif st.session_state.view == "structure" and st.session_state.cur:

    project = st.session_state.projects[st.session_state.cur]
    core = project.get("core", {})

    st.markdown(f"## {project['title']}")
    st.caption(f"{project['genre']} · {project['target_market']} · {project['format']}")
    render_stepper("structure", project)

    gns = core.get("goal_need_strategy", {})
    lp = core.get("logline_pack", {})
    if lp.get("washed"):
        st.markdown(f'<div class="callout"><div class="cl">Logline</div>{lp["washed"]}</div>', unsafe_allow_html=True)
    if gns:
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="callout"><div class="cl">GOAL</div>{gns.get("goal","")}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="callout"><div class="cl">NEED</div>{gns.get("need","")}</div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="callout"><div class="cl">STRATEGY</div>{gns.get("strategy","")}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">🏗️ Structure Build <span class="en">STORY STRUCTURE</span></div>', unsafe_allow_html=True)
    st.caption("시놉시스 · 스토리라인 · 3막 구조 · 15비트 · 캐릭터 변화표를 설계합니다.")

    # ─── 포맷 미지정 차단 (v2.7.1 신규) ───
    # 진단: get_beat_structure()는 "시리즈"·"미니"가 없으면 전부 영화 구조로 폴백한다.
    #   "미지정"은 보류가 아니라 묵시적 "영화" 확정이었다. 조용한 폴백이 가장 위험하다.
    if project.get("format", "미지정") in ("", "미지정"):
        st.error(
            "📐 **포맷이 확정되지 않았습니다.**\n\n"
            "Structure Build부터는 포맷에 따라 비트 구조 자체가 달라집니다 "
            "(영화 = 3막 16비트 / 시리즈 = 에피소드 단위). "
            "미지정 상태로 진행하면 영화 구조가 자동 적용되며, "
            "나중에 시리즈로 바꾸면 이 단계부터 전부 재실행해야 합니다."
        )
        if st.button("📐 포맷 확정하러 가기 →", type="primary", use_container_width=True):
            st.session_state.view = "project"
            st.rerun()
        st.stop()

    if st.button("🏗️ Structure Build 실행", type="primary"):
        if not core:
            st.error("Core Build가 없습니다.")
        else:
            with st.spinner("① 시놉시스 + 스토리라인... (20–30초)"):
                story = call_structure_story(
                    core, project["genre"], project["target_market"], project["format"],
                    locked_block=_build_project_locked_block(project),
                    fact_based=project.get("fact_based", False),
                    historical=project.get("historical", False),
                    film_type=project.get("film_type", ""),
                )
            if story:
                project["structure_story"] = story
                with st.spinner("② 구조 진단 + 캐릭터 변화표... (20–30초)"):
                    diag = call_structure_diagnosis(
                        core, story, project["genre"], project["format"],
                        locked_block=_build_project_locked_block(project),
                        fact_based=project.get("fact_based", False),
                        historical=project.get("historical", False),
                        film_type=project.get("film_type", ""),
                    )
                if diag:
                    project["structure_diag"] = diag
                    with st.spinner("③ Gate D 채점... (10초)"):
                        gate_d = call_structure_gate(story, diag)
                    if gate_d:
                        project["structure_gate"] = gate_d
                with st.spinner("④ 기승전결 줄글 시놉시스... (10–15초)"):
                    prose = call_structure_prose(core, story)
                if prose:
                    project["structure_prose"] = prose
                project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.rerun()

    if project.get("structure_story"):
        story = project["structure_story"]
        st.markdown("#### 📖 Synopsis 1P")
        syn = story.get("synopsis_1p", {})
        for label, key in [("시작","opening"),("촉발사건","catalyst"),("전개","development"),("미드포인트","midpoint"),("붕괴","collapse"),("결전","climax"),("결말","ending")]:
            val = syn.get(key, "")
            if val:
                st.markdown(f'<div class="callout"><div class="cl">{label}</div>{val}</div>', unsafe_allow_html=True)

        st.markdown("#### 📊 스토리라인 (시퀀스 방향)")
        for seq in story.get("storyline", []):
            st.markdown(f'<div class="card"><div class="cl">SEQ {seq.get("seq","")} · {seq.get("label","")} ({seq.get("pages","")})</div>{seq.get("summary","")}<br><span style="font-size:.8rem;color:#666">⚔️ {seq.get("conflict","")} · 💭 {seq.get("emotion","")} · → {seq.get("hook","")}</span></div>', unsafe_allow_html=True)

    if project.get("structure_diag"):
        diag = project["structure_diag"]
        st.markdown("#### 🎬 3막 구조 진단")
        ta = diag.get("three_act", {})
        for label, key in [("1막 끝","act1_end"),("미드포인트","act2_midpoint"),("All Is Lost","act2_end"),("클라이맥스","act3_climax")]:
            val = ta.get(key, "")
            if val:
                st.markdown(f'<div class="callout"><div class="cl">{label}</div>{val}</div>', unsafe_allow_html=True)
        if ta.get("diagnosis"):
            st.caption(f"진단: {ta['diagnosis']}")

        st.markdown("#### 🥁 15-Beat Sheet")
        for bt in diag.get("beat_sheet", []):
            status = bt.get("status", "")
            color = {"있음":"var(--g)","약함":"var(--y)","없음":"var(--r)"}.get(status, "var(--dim)")
            st.markdown(
                f'<div style="margin:.3rem 0;font-size:.85rem">'
                f'<span style="color:{color};font-weight:700">[{status}]</span> '
                f'<b>{bt.get("beat","")}</b> — '
                f'<span style="color:#666">{bt.get("note","")}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

        # 캐릭터 변화표
        arcs = diag.get("character_arcs", [])
        if arcs:
            st.markdown("#### 🎭 캐릭터 변화표")
            role_labels = {"protagonist":"주인공","antagonist":"적대자","ally":"조력자","mirror":"거울","catalyst":"촉매자","subplot_lead":"서브플롯 리드"}
            for arc in arcs:
                role = role_labels.get(arc.get("role",""), arc.get("role",""))
                arc_type = arc.get("arc_type", "")
                st.markdown(
                    f'<div class="card">'
                    f'<div class="cl">{role}: {arc.get("name","")} [{arc_type}]</div>'
                    f'<span style="font-size:.8rem;color:#666">'
                    f'1막: {arc.get("act1_state","")}<br>'
                    f'전환: {arc.get("turning_point","")}<br>'
                    f'3막: {arc.get("act3_state","")}'
                    f'</span></div>',
                    unsafe_allow_html=True
                )

        # 관계 변화표
        rels = diag.get("relationship_changes", [])
        if rels:
            st.markdown("#### 🔗 관계 변화표")
            for rel in rels:
                st.markdown(
                    f'<div class="card">'
                    f'<div class="cl">{rel.get("pair","")}</div>'
                    f'<span style="font-size:.8rem;color:#666">'
                    f'1막: {rel.get("act1","")} → '
                    f'미드: {rel.get("midpoint","")} → '
                    f'3막: {rel.get("act3","")}'
                    f'</span></div>',
                    unsafe_allow_html=True
                )

    # 기승전결 줄글 시놉시스
    if project.get("structure_prose"):
        prose_data = project["structure_prose"]
        if prose_data.get("prose"):
            st.markdown("#### 📝 기승전결 시놉시스 (1P 줄글)")
            st.markdown(f'<div class="callout" style="line-height:1.8;font-size:.9rem">{prose_data["prose"]}</div>', unsafe_allow_html=True)

    if project.get("structure_gate"):
        sg = project["structure_gate"]
        gd = sg.get("gate_d_structure", {})
        gd_avg = gd.get("average", 0)
        gd_ok = gd_avg >= 7.0
        st.markdown("---")
        st.markdown("#### 🚪 Gate D: Structure Gate")
        c1, c2 = st.columns([1, 2])
        with c1:
            cl = "var(--g)" if gd_ok else "var(--r)"
            st.markdown(f'<div style="text-align:center"><div class="big" style="color:{cl}">{gd_avg}</div><div class="sm" style="color:{cl};font-size:1rem;font-weight:700">{"PASS" if gd_ok else "FAIL"}</div></div>', unsafe_allow_html=True)
        with c2:
            for nm, sc in [("전환점",gd.get("turning_points_valid",0)),("Midpoint",gd.get("midpoint_redirects",0)),("All Is Lost",gd.get("all_is_lost_works",0)),("결말",gd.get("ending_inevitable_surprising",0))]:
                st.markdown(f'<div style="display:flex;align-items:center;margin:.2rem 0;font-size:.8rem"><div style="width:80px;color:var(--dim)">{nm}</div><div style="flex:1;background:#E0E0E8;border-radius:4px;height:8px;margin:0 .5rem"><div style="width:{sc*10}%;background:var(--y);height:100%;border-radius:4px"></div></div><div style="width:30px;text-align:right">{sc}</div></div>', unsafe_allow_html=True)
        if gd.get("feedback"):
            st.caption(gd["feedback"])

        if gd_ok:
            st.success("✅ Gate D 통과. Scene Design 진행 가능.")

            # v2.5.3: Structure 완료 시점 JSON 저장
            with st.expander("💾 프로젝트 JSON 저장 (Structure 완료 시점)", expanded=False):
                st.caption(
                    "Structure Build까지 완료되었습니다. 여기서 JSON 파일을 저장하면 "
                    "Scene Design 단계에서 문제가 생겨도 Structure까지의 작업을 잃지 않습니다."
                )
                title_safe_json = project.get("title", "프로젝트").replace(" ", "_")
                ts_json = datetime.now().strftime("%Y%m%d_%H%M")
                project_json_str = save_project_to_json(project)
                st.download_button(
                    label="💾 프로젝트 저장 (Structure 완료)",
                    data=project_json_str.encode("utf-8"),
                    file_name=f"{title_safe_json}_Structure완료_{ts_json}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_structure",
                )

            if st.button("🎬 Scene Design 진행 →", type="primary", use_container_width=True):
                st.session_state.view = "scene_design"
                st.rerun()
        else:
            st.warning(f"⚠️ Gate D 미통과 (평균 {gd_avg}).")

            # v2.5.3: Gate D 미통과 시에도 저장 가능
            with st.expander("💾 프로젝트 JSON 저장 (Structure 완료, Gate D 보류)", expanded=False):
                st.caption("Gate D 미통과 상태이지만 현재까지의 작업을 저장할 수 있습니다.")
                title_safe_json = project.get("title", "프로젝트").replace(" ", "_")
                ts_json = datetime.now().strftime("%Y%m%d_%H%M")
                project_json_str = save_project_to_json(project)
                st.download_button(
                    label="💾 프로젝트 저장 (Structure, Gate D 보류)",
                    data=project_json_str.encode("utf-8"),
                    file_name=f"{title_safe_json}_Structure_{ts_json}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="dl_structure_hold",
                )

            col_sd1, col_sd2 = st.columns(2)
            with col_sd1:
                if st.button("🔓 Override → Scene Design"):
                    st.session_state.view = "scene_design"
                    st.rerun()
            with col_sd2:
                if st.button("🔄 Structure 재실행"):
                    for k in ["structure_story","structure_diag","structure_gate","structure_prose"]:
                        project[k] = None
                    st.rerun()

        # DOCX 1차 다운로드
        st.markdown("---")
        st.markdown("#### 📥 기획개발보고서 [1차] 다운로드")
        st.caption("Core Build + Structure Build까지의 기획서입니다. 다운로드 후 직접 수정/보강하세요.")
        st.markdown(
            '<div class="callout">'
            '<div class="cl">💡 1차 기획서 활용법</div>'
            '다운로드한 기획서를 검토하고, 추가하고 싶은 요소(예: 사이렌, 특정 장치, 캐릭터 보강 등)를 '
            '직접 수정하세요. 수정이 끝나면 Scene Design → Treatment로 진행하여 최종 기획서를 완성합니다.'
            '</div>',
            unsafe_allow_html=True
        )
        title_safe = project.get("title", "프로젝트").replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        docx_buffer = generate_docx(project)
        st.download_button(
            label="📥 기획개발보고서 [1차] 다운로드 (.docx)",
            data=docx_buffer,
            file_name=f"기획개발보고서_{title_safe}_1차_Blue_{timestamp}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    elif not project.get("structure_story"):
        st.markdown('<div style="text-align:center;padding:3rem 0;color:var(--dim)">🏗️ Structure Build를 실행하면 여기에 결과가 표시됩니다.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.caption(ENGINE_FOOTER)


# ═══════════════════════════════════════════════════
#  SCENE DESIGN (장면화)
# ═══════════════════════════════════════════════════
elif st.session_state.view == "scene_design" and st.session_state.cur:

    project = st.session_state.projects[st.session_state.cur]
    core = project.get("core", {})
    story = project.get("structure_story", {})
    diag = project.get("structure_diag", {})

    st.markdown(f"## {project['title']}")
    st.caption(f"{project['genre']} · {project['target_market']} · {project['format']}")
    render_stepper("scene_design", project)

    gns = core.get("goal_need_strategy", {})
    lp = core.get("logline_pack", {})
    if lp.get("washed"):
        st.markdown(f'<div class="callout"><div class="cl">Logline</div>{lp["washed"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">🎬 Scene Design <span class="en">SCENE DESIGN</span></div>', unsafe_allow_html=True)
    st.caption("Show, don't tell — 핵심 장면의 극적 행동 · 반전 · 시각 연출을 설계합니다.")

    if st.button("🎬 Scene Design 실행", type="primary"):
        if not story:
            st.error("Structure Build가 없습니다.")
        else:
            with st.spinner("핵심 장면 설계 중... (약 30–40초)"):
                sd = call_scene_design(
                    core, story, diag, project["genre"], project["format"],
                    locked_block=_build_project_locked_block(project),
                    fact_based=project.get("fact_based", False),
                    historical=project.get("historical", False),
                    film_type=project.get("film_type", ""),
                )
            if sd:
                project["scene_design"] = sd
                project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.rerun()

    # ── Scene Design 결과 표시 ──
    if project.get("scene_design"):
        sd = project["scene_design"]
        scenes = sd.get("key_scenes", [])
        sms = sd.get("scene_map_summary", {})

        # 장면 맵 요약
        if sms:
            st.markdown("#### 🗺️ Scene Map")
            c1, c2, c3, c4 = st.columns(4)
            c1.markdown(f'<div class="callout"><div class="cl">1막</div>{sms.get("act1_scenes","")}</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="callout"><div class="cl">2막 전반</div>{sms.get("act2a_scenes","")}</div>', unsafe_allow_html=True)
            c3.markdown(f'<div class="callout"><div class="cl">2막 후반</div>{sms.get("act2b_scenes","")}</div>', unsafe_allow_html=True)
            c4.markdown(f'<div class="callout"><div class="cl">3막</div>{sms.get("act3_scenes","")}</div>', unsafe_allow_html=True)

            if sms.get("must_see_scenes"):
                st.markdown(f'<div class="callout" style="border-left-color:var(--y)"><div class="cl">⭐ Must-See 장면</div>{sms["must_see_scenes"]}</div>', unsafe_allow_html=True)

        # 핵심 장면 카드
        st.markdown(f"#### 🎬 핵심 장면 ({len(scenes)}개)")
        for sc in scenes:
            tp = sc.get("turning_point", "")
            tp_html = f'<br>🔄 <b>전환:</b> {tp}' if tp else ""
            di = sc.get("dramatic_irony", "")
            di_html = f'<br>👁️ <b>아이러니:</b> <i>{di}</i>' if di else ""
            kl = sc.get("key_line", "")
            kl_html = f'<br><span style="color:var(--navy);font-weight:600">💬 "{kl}"</span>' if kl else ""
            st.markdown(
                f'<div class="card">'
                f'<div class="cl">S#{sc.get("scene_no","")} · {sc.get("sequence","")} · {sc.get("location","")}</div>'
                f'<b>{sc.get("title","")}</b> — {sc.get("characters","")}<br>'
                f'<span style="font-size:.85rem">'
                f'📍 {sc.get("setup","")}<br>'
                f'🎭 <b>행동:</b> {sc.get("dramatic_action","")}'
                f'{tp_html}'
                f'{di_html}<br>'
                f'💭 {sc.get("emotion_shift","")}<br>'
                f'🎥 {sc.get("visual_direction","")}<br>'
                f'⚡ 판돈: {sc.get("stakes","")}'
                f'{kl_html}<br>'
                f'→ {sc.get("connection","")}'
                f'</span></div>',
                unsafe_allow_html=True
            )

        st.markdown("---")

        # JSON 프로젝트 저장 (세션 끊김 대비)
        st.markdown("#### 💾 프로젝트 JSON 저장 (세션 복구용)")
        st.caption(
            "브라우저를 닫거나 세션이 끊겨도 여기서 JSON 파일을 저장하면 "
            "다음에 홈 화면의 '프로젝트 불러오기'로 복원 후 Treatment부터 이어서 진행할 수 있습니다."
        )
        title_safe_json = project.get("title", "프로젝트").replace(" ", "_")
        ts_json = datetime.now().strftime("%Y%m%d_%H%M")
        project_json_str = save_project_to_json(project)
        st.download_button(
            label="💾 프로젝트 저장 (Scene 완료 시점)",
            data=project_json_str.encode("utf-8"),
            file_name=f"{title_safe_json}_Scene완료_{ts_json}.json",
            mime="application/json",
            use_container_width=True,
        )

        st.markdown("---")

        # Treatment 진행
        st.success("✅ Scene Design 완료. Treatment Build 진행 가능.")
        if st.button("📝 Treatment Build 진행 →", type="primary", use_container_width=True):
            st.session_state.view = "treatment"
            st.rerun()

    else:
        st.markdown(
            '<div style="text-align:center;padding:3rem 0;color:var(--dim)">'
            '🎬 Scene Design을 실행하면 여기에 핵심 장면이 표시됩니다.<br>'
            'Show, don\'t tell — 행동 · 반전 · 시각 연출'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption(ENGINE_FOOTER)


# ═══════════════════════════════════════════════════
#  TREATMENT BUILD
# ═══════════════════════════════════════════════════
elif st.session_state.view == "treatment" and st.session_state.cur:

    project = st.session_state.projects[st.session_state.cur]
    core = project.get("core", {})
    story = project.get("structure_story", {})
    diag = project.get("structure_diag", {})

    st.markdown(f"## {project['title']}")
    st.caption(f"{project['genre']} · {project['target_market']} · {project['format']}")
    render_stepper("treatment", project)

    # 요약 정보
    gns = core.get("goal_need_strategy", {})
    lp = core.get("logline_pack", {})
    if lp.get("washed"):
        st.markdown(f'<div class="callout"><div class="cl">Logline</div>{lp["washed"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">📝 Treatment Build <span class="en">16-BEAT TREATMENT</span></div>', unsafe_allow_html=True)
    st.caption("16비트 구조 × 줄글 트리트먼트. 1막(6비트) + 2막(6비트) + 3막(4비트) = 약 40–50페이지")

    scene_data = project.get("scene_design", {})

    # ── v2.6.3: 막별 독립 실행 버튼 (Mr. MOON 요청) ──
    # v2.6.2의 막별 증분 저장(treatment_partial) 위에 실행 단위를 분리.
    #   ①②③ 각 막을 독립 버튼으로 생성 — 한 클릭 = Opus 호출 1회 (재시도 포함 최대 3회)
    #   ④ 3개 막이 모이면 '확정' 버튼 등장 — 메타 + Writer 인계 + Gate E 실행 후 확정
    # 효과: JSON 파싱 실패·연결 끊김이 발생해도 피해 범위가 막 1개로 한정.
    _partial = project.get("treatment_partial", {})

    def _run_treatment_act(act_n, spinner_label):
        """v2.6.3: 해당 막 1개만 생성하고 완성 즉시 저장 후 화면 갱신."""
        if not story:
            st.error("Structure Build가 없습니다.")
            return
        with st.spinner(spinner_label):
            result = call_treatment_beats(
                core, story, scene_data, project["genre"], project["format"], act_n,
                locked_block=_build_project_locked_block(project),
                fact_based=project.get("fact_based", False),
                historical=project.get("historical", False),
                film_type=project.get("film_type", ""),
                research=project.get("research"),
            )
        if result:
            project.setdefault("treatment_partial", {})[f"act{act_n}"] = result
            project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.rerun()

    _act_specs = [
        (1, "1막", "Beat 1~6", "약 1~3분"),
        (2, "2막", "Beat 7~12", "약 1~3분"),
        (3, "3막", "Beat 13~16", "약 1~2분"),
    ]
    _cols = st.columns(3)
    for _col, (_n, _name, _beats_label, _tip) in zip(_cols, _act_specs):
        with _col:
            _done = bool(_partial.get(f"act{_n}"))
            if _done:
                st.caption(f"✅ {_name} 저장됨 · 비트 {len(_partial[f'act{_n}'].get('beats', []))}개")
            _btn_label = f"🔄 {_name} 재생성" if _done else f"📝 {_name} 생성 ({_beats_label})"
            if st.button(_btn_label, key=f"treat_act{_n}_btn"):
                _run_treatment_act(_n, f"{_name} Treatment ({_beats_label})... ({_tip})")

    # 저장된 막 미리보기 — 확정 전 검토용
    for _n, _name, _beats_label, _tip in _act_specs:
        _act_data = _partial.get(f"act{_n}")
        if _act_data:
            with st.expander(f"📖 {_name} 미리보기 (확정 전 · {_beats_label})"):
                for _b in _act_data.get("beats", []):
                    st.markdown(f"**Beat {_b.get('beat_no', '')}. {_b.get('beat_name', '')}** · {len(_b.get('narrative', ''))}자")
                    st.write(_b.get("narrative", ""))

    # ── v2.6.6: 확정 전 중간 저장 (Mr. MOON 운영 중 발견) ──
    # v2.6.3 막별 독립 실행 개편 때 Treatment 페이지의 JSON 저장 버튼이
    # 확정 이후 블록(if project.get("treatment"))에만 남아, 확정 전에는
    # 저장 수단이 화면에 없었음. treatment_partial은 세션 메모리에만 있어
    # 확정 전 세션 끊김 시 생성된 막이 유실 — v2.6.2~v2.6.3의 피해 범위
    # 한정 취지와 어긋나는 공백. save_project_to_json은 project 전체를
    # 직렬화하므로 treatment_partial도 포함 → 버튼만 노출하면 복원 작동.
    if _partial and not project.get("treatment"):
        with st.expander("💾 프로젝트 JSON 저장 (Treatment 진행중 · 확정 전)", expanded=False):
            st.caption(
                "생성된 막은 세션에만 저장되어 있습니다. 확정 전에 세션이 끊겨도 "
                "여기서 JSON을 저장해 두면 해당 시점부터 이어서 진행할 수 있습니다."
            )
            _title_safe = project.get("title", "프로젝트").replace(" ", "_")
            _ts = datetime.now().strftime("%Y%m%d_%H%M")
            _partial_json_str = save_project_to_json(project)
            st.download_button(
                label="💾 프로젝트 저장 (Treatment 진행중)",
                data=_partial_json_str.encode("utf-8"),
                file_name=f"{_title_safe}_Treatment진행중_{_ts}.json",
                mime="application/json",
                use_container_width=True,
                key="treat_partial_save_btn",
            )

    if all(_partial.get(f"act{_n}") for _n in (1, 2, 3)):
        st.success("3개 막 완성 — 확정 실행 시 감정 곡선·Writer 인계 블록·Gate E 채점 후 Treatment가 확정됩니다.")
        if st.button("✅ ④ Treatment 확정 (메타 + Gate E)", type="primary", key="treat_finalize_btn"):
            act1 = _partial["act1"]
            act2 = _partial["act2"]
            act3 = _partial["act3"]
            project["treatment"] = {"act1": act1, "act2": act2, "act3": act3}
            project.pop("treatment_partial", None)  # v2.6.2: 확정 시 부분 저장분 정리
            project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

            with st.spinner("④ 감정 곡선 + 감독 포인트... (약 10초)"):
                meta = call_treatment_meta(act1, act2, act3, core)
            if meta:
                project["treatment"]["meta"] = meta

            # v2.6.0 — Writer Engine v3.7.1 인계용 4블록 자동 생성
            # (시퀀스 사이클 / 적대자 행위 / Setup-Payoff / 물리적 대가)
            try:
                handoff = build_writer_engine_handoff_v26(
                    act1, act2, act3,
                    char_bible=project.get("characters")
                )
                project["treatment"]["writer_handoff_v26"] = handoff
                # 경고가 있으면 사용자에게 표시 (선택적)
                all_warnings = []
                all_warnings.extend(handoff.get("cycle_design", {}).get("warnings", []))
                all_warnings.extend(handoff.get("antagonist_actions", {}).get("warnings", []))
                all_warnings.extend(handoff.get("physical_cost_plan", {}).get("warnings", []))
                # Setup-Payoff 미회수 항목 경고
                sp_table = handoff.get("setup_payoff_table", [])
                unrecovered = [x["item"] for x in sp_table if x.get("status") == "회수 필요"]
                if unrecovered:
                    all_warnings.append(
                        f"Setup-Payoff 미회수 항목 {len(unrecovered)}개: {', '.join(unrecovered)} — "
                        f"삭제 후보 또는 Payoff 추가 필요"
                    )
                if all_warnings:
                    with st.expander(f"⚠️ v2.6.0 사전 방지 경고 {len(all_warnings)}건"):
                        for w in all_warnings:
                            st.warning(w)
            except Exception as e:
                st.warning(f"v2.6.0 후처리 중 비치명적 오류 (Treatment는 정상 저장됨): {e}")

            with st.spinner("⑤ Gate E 채점... (약 15초, 장르·엔딩·논리 검증 포함)"):
                gate_e = call_treatment_gate(
                    project["treatment"],
                    core_data=core,
                    genre=project["genre"],
                )
            if gate_e:
                project["treatment_gate"] = gate_e

            project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            st.rerun()

    # ── Treatment 결과 표시 (16비트 줄글) ──
    if project.get("treatment"):
        treat = project["treatment"]

        act_labels = {1: "1막 — 설정 (Set-up)", 2: "2막 — 대결 (Confrontation)", 3: "3막 — 해결 (Resolution)"}

        for act_num in [1, 2, 3]:
            act_key = f"act{act_num}"
            act_data = treat.get(act_key)
            if act_data:
                st.markdown(f"#### 📖 {act_labels[act_num]}")

                for b in act_data.get("beats", []):
                    beat_no = b.get("beat_no", "")
                    beat_name = b.get("beat_name", "")
                    episode = b.get("episode", "")
                    narrative = b.get("narrative", "").replace("\n", "<br>")
                    char_count = len(b.get("narrative", ""))
                    event_s = b.get("event_summary", "")
                    decision_s = b.get("decision_summary", "")
                    consequence_s = b.get("consequence_summary", "")
                    status_c = b.get("status_change", "")
                    b_story = b.get("b_story_beat", "")
                    cliff = b.get("cliffhanger", "")
                    villain = b.get("villain_beat", "")
                    pp = b.get("plant_payoff", "")

                    ep_tag = f'<span style="background:var(--y);color:var(--n);padding:1px 6px;border-radius:3px;font-size:.7rem;margin-right:6px">{episode}</span>' if episode else ""

                    meta_lines = []
                    if event_s:
                        meta_lines.append(f'<b>사건</b>: {event_s}')
                    if decision_s:
                        meta_lines.append(f'<b>선택</b>: {decision_s}')
                    if consequence_s:
                        meta_lines.append(f'<b>결과</b>: {consequence_s}')
                    if status_c:
                        meta_lines.append(f'<b>변화</b>: {status_c}')
                    if b_story:
                        meta_lines.append(f'<b>B-Story</b>: {b_story}')
                    if villain:
                        meta_lines.append(f'<b>빌런</b>: {villain}')
                    if pp:
                        meta_lines.append(f'<b>🌱 Plant/Payoff</b>: {pp}')
                    if cliff:
                        meta_lines.append(f'<b style="color:var(--r)">CLIFFHANGER</b>: {cliff}')
                    meta_html = "<br>".join(meta_lines)
                    meta_block = f'<div style="background:var(--mist);padding:8px 10px;border-radius:6px;margin-top:8px;font-size:.78rem;line-height:1.6">{meta_html}</div>' if meta_lines else ""

                    st.markdown(
                        f'<div class="card">'
                        f'<div class="cl">{ep_tag}Beat {beat_no}. {beat_name}</div>'
                        f'<div style="line-height:2.0;font-size:.9rem;margin-top:.5rem">'
                        f'{narrative}'
                        f'</div>'
                        f'{meta_block}'
                        f'<div style="text-align:right;font-size:.65rem;color:var(--dim);margin-top:.3rem">{char_count}자</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("")

        # 감정 곡선
        meta = treat.get("meta", {})
        ec = meta.get("emotion_curve", [])
        if ec:
            st.markdown("#### 📈 감정 곡선")
            import plotly.graph_objects as go
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=[p.get("point","") for p in ec],
                y=[p.get("tension",0) for p in ec],
                mode='lines+markers',
                line=dict(color='#191970', width=3),
                marker=dict(size=8, color='#FFCB05', line=dict(color='#191970', width=2)),
                text=[p.get("emotion","") for p in ec],
                hovertemplate='%{x}<br>텐션: %{y}<br>감정: %{text}<extra></extra>'
            ))
            fig.update_layout(
                plot_bgcolor='#FAFAFA', paper_bgcolor='#FAFAFA',
                font_color='#1A1A2E', yaxis_range=[0,10],
                yaxis_title="Tension", height=300,
                margin=dict(l=40,r=20,t=20,b=40),
                yaxis=dict(gridcolor='#E0E0E8'),
                xaxis=dict(gridcolor='#E0E0E8')
            )
            st.plotly_chart(fig, use_container_width=True)

        # 감독용 포인트
        notes = meta.get("director_notes", [])
        if notes:
            st.markdown("#### 🎬 감독용 포인트")
            for i, n in enumerate(notes, 1):
                st.markdown(f"**{i}.** {n}")

        # 투자자 요약
        inv = meta.get("investor_summary", "")
        if inv:
            st.markdown(f'<div class="callout"><div class="cl">💰 투자자용 요약</div>{inv}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Gate E
        if project.get("treatment_gate"):
            tg = project["treatment_gate"]
            ge = tg.get("gate_e_treatment", {})
            ge_avg = ge.get("average", 0)
            ge_ok = ge_avg >= 7.0

            st.markdown("#### 🚪 Gate E: Treatment Gate")
            c1, c2 = st.columns([1, 2])
            with c1:
                cl = "var(--g)" if ge_ok else "var(--r)"
                st.markdown(f'<div style="text-align:center"><div class="big" style="color:{cl}">{ge_avg}</div><div class="sm" style="color:{cl};font-size:1rem;font-weight:700">{"PASS" if ge_ok else "FAIL"}</div></div>', unsafe_allow_html=True)
            with c2:
                for nm, sc in [("영화적 읽힘",ge.get("cinematic_reading",0)),("씬-감정 일치",ge.get("scene_emotion_match",0)),("비트 충실도",ge.get("beat_completeness",0)),("초고 직행 가능",ge.get("screenplay_ready",0))]:
                    st.markdown(f'<div style="display:flex;align-items:center;margin:.2rem 0;font-size:.8rem"><div style="width:100px;color:var(--dim)">{nm}</div><div style="flex:1;background:#E0E0E8;border-radius:4px;height:8px;margin:0 .5rem"><div style="width:{sc*10}%;background:var(--y);height:100%;border-radius:4px"></div></div><div style="width:30px;text-align:right">{sc}</div></div>', unsafe_allow_html=True)
            if ge.get("feedback"):
                st.caption(ge["feedback"])

            if ge_ok:
                st.success("✅ Gate E 통과. 기획개발 완료. Screenplay Writer Engine 연동 준비 완료.")
            else:
                st.warning(f"⚠️ Gate E 미통과 (평균 {ge_avg}). Treatment 보강 필요.")
                if st.button("🔄 Treatment 재실행"):
                    project["treatment"] = None
                    project["treatment_gate"] = None
                    st.rerun()

        # DOCX 2차(최종) 다운로드
        st.markdown("---")
        st.markdown("#### 📥 기획개발보고서 [최종] 다운로드")
        st.caption("Core + Structure + Scene Design + Treatment 전체가 포함된 최종 기획서입니다.")
        title_safe = project.get("title", "프로젝트").replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        docx_buffer = generate_docx(project)
        st.download_button(
            label="📥 기획개발보고서 [최종] 다운로드 (.docx)",
            data=docx_buffer,
            file_name=f"기획개발보고서_{title_safe}_최종_Blue_{timestamp}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

        # JSON 프로젝트 저장 (세션 복구용)
        st.markdown("#### 💾 프로젝트 JSON 저장 (세션 복구용)")
        project_json_str = save_project_to_json(project)
        st.download_button(
            label="💾 프로젝트 저장 (Treatment 완료 시점)",
            data=project_json_str.encode("utf-8"),
            file_name=f"{title_safe}_Treatment완료_{timestamp}.json",
            mime="application/json",
            use_container_width=True,
        )

        # Tone Document 진행
        st.markdown("---")
        st.success("✅ Treatment 완료. Tone Document 진행 가능.")
        if st.button("🎨 Tone Document 진행 →", type="primary", use_container_width=True):
            st.session_state.view = "tone_doc"
            st.rerun()

    else:
        st.markdown(
            '<div style="text-align:center;padding:3rem 0;color:var(--dim)">'
            '📝 Treatment Build를 실행하면 여기에 결과가 표시됩니다.'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption(ENGINE_FOOTER)


# ═══════════════════════════════════════════════════
#  TONE DOCUMENT
# ═══════════════════════════════════════════════════
elif st.session_state.view == "tone_doc" and st.session_state.cur:

    project = st.session_state.projects[st.session_state.cur]
    core = project.get("core", {})
    treatment = project.get("treatment", {})

    st.markdown(f"## {project['title']}")
    st.caption(f"{project['genre']} · {project['target_market']} · {project['format']}")
    render_stepper("tone_doc", project)

    lp = core.get("logline_pack", {})
    if lp.get("washed"):
        st.markdown(f'<div class="callout"><div class="cl">Logline</div>{lp["washed"]}</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-header">🎨 Tone Document <span class="en">VISUAL & TONAL GUIDE</span></div>', unsafe_allow_html=True)
    st.caption("카메라 · 색감 · 페이싱 · 대사 규칙 · 모티프 · 금기 — Writer Engine의 톤 일관성 가이드")

    if not project.get("tone_doc"):
        if st.button("🎨 Tone Document 생성", type="primary"):
            with st.spinner("톤 & 연출 문서 설계 중... (최대 40초)"):
                result = call_tone_document(
                    core, project.get("structure_story", {}),
                    project.get("scene_design", {}), treatment,
                    project.get("char_bible", {}),
                    project["genre"], project["format"],
                    locked_block=_build_project_locked_block(project),
                    fact_based=project.get("fact_based", False),
                    historical=project.get("historical", False),
                    film_type=project.get("film_type", ""),
                )
            if result:
                project["tone_doc"] = result
                project["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.rerun()

    td = project.get("tone_doc", {})
    if td:
        # Visual Style
        vs = td.get("visual_style", {})
        if vs:
            st.markdown('<div class="section-header">🎥 비주얼 스타일 <span class="en">VISUAL STYLE</span></div>', unsafe_allow_html=True)
            for label, key in [("카메라 철학","camera_philosophy"),("색감 팔레트","color_palette"),("조명 규칙","lighting_rule"),("시그니처 쇼트","signature_shot")]:
                val = vs.get(key, "")
                if val:
                    st.markdown(f'<div class="ri"><div class="rl">{label}</div>{val}</div>', unsafe_allow_html=True)

        # Pacing
        pc = td.get("pacing", {})
        if pc:
            st.markdown('<div class="section-header">⏱️ 페이싱 <span class="en">PACING</span></div>', unsafe_allow_html=True)
            for label, key in [("전체 철학","overall"),("1막 템포","act1_tempo"),("2막 템포","act2_tempo"),("3막 템포","act3_tempo"),("대사 비율","dialogue_density")]:
                val = pc.get(key, "")
                if val:
                    st.markdown(f'<div class="ri"><div class="rl">{label}</div>{val}</div>', unsafe_allow_html=True)

        # Dialogue Rules
        dr = td.get("dialogue_rules", {})
        if dr:
            st.markdown('<div class="section-header">💬 대사 규칙 <span class="en">DIALOGUE RULES</span></div>', unsafe_allow_html=True)
            for label, key in [("전체 톤","overall_tone"),("서브텍스트","subtext_rule"),("침묵 활용","silence_usage")]:
                val = dr.get(key, "")
                if val:
                    st.markdown(f'<div class="ri"><div class="rl">{label}</div>{val}</div>', unsafe_allow_html=True)
            forbidden = dr.get("forbidden_phrases", [])
            if forbidden:
                fp_list = forbidden if isinstance(forbidden, list) else [forbidden]
                fp_html = "<br>".join([f"🚫 {f}" for f in fp_list])
                st.markdown(f'<div class="card"><div class="cl">금지 대사 패턴</div>{fp_html}</div>', unsafe_allow_html=True)

        # Motifs
        mt = td.get("motifs", {})
        if mt:
            st.markdown('<div class="section-header">🔄 모티프 <span class="en">RECURRING MOTIFS</span></div>', unsafe_allow_html=True)
            for label, key in [("반복 소품/모티프","recurring_objects"),("반복 장소","recurring_locations")]:
                val = mt.get(key, [])
                if val:
                    items = val if isinstance(val, list) else [val]
                    items_html = "<br>".join([f"• {i}" for i in items])
                    st.markdown(f'<div class="card"><div class="cl">{label}</div>{items_html}</div>', unsafe_allow_html=True)
            wm = mt.get("weather_mood", "")
            if wm:
                st.markdown(f'<div class="ri"><div class="rl">날씨/계절</div>{wm}</div>', unsafe_allow_html=True)

        # Music & Sound
        ms = td.get("music_sound", {})
        if ms:
            st.markdown('<div class="section-header">🎵 사운드 <span class="en">MUSIC & SOUND</span></div>', unsafe_allow_html=True)
            for label, key in [("음악 방향","score_direction"),("무음 활용","silence_scenes")]:
                val = ms.get(key, "")
                if val:
                    st.markdown(f'<div class="ri"><div class="rl">{label}</div>{val}</div>', unsafe_allow_html=True)
            ds = ms.get("diegetic_sounds", [])
            if ds:
                items = ds if isinstance(ds, list) else [ds]
                items_html = " · ".join(items)
                st.markdown(f'<div class="ri"><div class="rl">작품 내 소리</div>{items_html}</div>', unsafe_allow_html=True)

        # Forbidden
        forbidden = td.get("forbidden", [])
        if forbidden:
            st.markdown('<div class="section-header">🚫 금기 <span class="en">FORBIDDEN</span></div>', unsafe_allow_html=True)
            fb_list = forbidden if isinstance(forbidden, list) else [forbidden]
            fb_html = "<br>".join([f"🚫 {f}" for f in fb_list])
            st.markdown(f'<div class="card">{fb_html}</div>', unsafe_allow_html=True)

        # Reference Films
        refs = td.get("reference_films", [])
        if refs:
            st.markdown('<div class="section-header">🎬 참고 작품 <span class="en">REFERENCE FILMS</span></div>', unsafe_allow_html=True)
            for ref in refs:
                title_ref = ref.get("title", "") if isinstance(ref, dict) else str(ref)
                reason = ref.get("reason", "") if isinstance(ref, dict) else ""
                st.markdown(f'<div class="ri"><div class="rl">{title_ref}</div>{reason}</div>', unsafe_allow_html=True)

        # Writer Instruction
        wi = td.get("writer_instruction", "")
        if wi:
            st.markdown(f'<div class="callout" style="border-left-color:var(--y)"><div class="cl">✍️ Writer Engine 최종 지시</div>{wi}</div>', unsafe_allow_html=True)

        # 완료
        st.markdown("---")
        st.success("🎉 기획개발 완료! 전체 9단계 파이프라인이 완성되었습니다.")
        st.info("→ Writer Engine에서 이 기획서를 불러와 시나리오를 생성할 수 있습니다.")

        # 최종 DOCX 다운로드
        title_safe = project.get("title", "프로젝트").replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        docx_buffer = generate_docx(project)
        st.download_button(
            label="📥 기획개발보고서 [최종 + Tone] 다운로드 (.docx)",
            data=docx_buffer,
            file_name=f"기획개발보고서_{title_safe}_최종_Blue_{timestamp}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

        # 최종 프로젝트 JSON 저장 (완성 상태 백업)
        st.markdown("#### 💾 프로젝트 JSON 저장 (완성 상태 백업)")
        st.caption("완성된 프로젝트 전체 상태. 나중에 Writer Engine 투입 전 참고용 또는 백업용.")
        project_json_str = save_project_to_json(project)
        st.download_button(
            label="💾 프로젝트 저장 (최종 완성)",
            data=project_json_str.encode("utf-8"),
            file_name=f"{title_safe}_최종완성_{timestamp}.json",
            mime="application/json",
            use_container_width=True,
        )

    else:
        st.markdown(
            '<div style="text-align:center;padding:3rem 0;color:var(--dim)">'
            '🎨 Tone Document를 생성하면 여기에 결과가 표시됩니다.<br>'
            '카메라 · 색감 · 페이싱 · 대사 규칙 · 모티프 · 참고 작품'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.caption(ENGINE_FOOTER)
