"""
Idea Engine v2.0
BLUE JEANS PICTURES · Creative Discovery & Triage Engine

v1.0: TRIAGE 트랙 (7-Stage 진단·판정 → LOCKED 시드)
v1.1: Creator Engine v2.5.2 정합 — 5개 신규 LOCKED 키 출력
      (locked_core_decisions / locked_music_rules / locked_visual_motifs
       / locked_ending_form / locked_creator_questions)
v2.0: HUNTER 트랙 추가 (5개 입구 아이디어 발굴 엔진)

[모드 분기]
HOME → [HUNTER 발굴 | TRIAGE 진단] 선택
HUNTER 출력 시드 → TRIAGE Stage 1 자동 전달

[설계 철학]
"카탈로그를 보여주는 게 아니라 작가 안에 잠재된 답을 끌어내기"

Writer Engine v3.1 디자인 시스템 적용
"""

import json
import re
import io
import os
from datetime import datetime
from typing import Dict, Any, Optional

import streamlit as st
import plotly.graph_objects as go
from anthropic import Anthropic
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import prompt as P

# ─────────────────────────────────────
# Engine Info
# ─────────────────────────────────────
ENGINE_VERSION = "v2.0"
ENGINE_BUILD_DATE = "2026-05-05"
ENGINE_PATCH_LEVEL = "v2.0 (HUNTER 골격) + v1.1 패치 (Creator Engine v2.5.2 정합 5키)"

ANTHROPIC_MODEL_SONNET = "claude-sonnet-4-6"
ANTHROPIC_MODEL_OPUS = "claude-opus-4-7"
MAX_TOKENS = 16000

# ─────────────────────────────────────
# Page Config
# ─────────────────────────────────────
st.set_page_config(
    page_title="BLUE JEANS · Idea Engine",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════════════════════
# Session State + Mode-Switch Helpers
# (사이드바보다 먼저 정의되어야 함 — 사이드바 버튼이 호출함)
# ═══════════════════════════════════════════════════════════
def init_session_state():
    defaults = {
        # ── v2.0 모드 분기 ──
        "mode": "HOME",                # HOME | HUNTER | TRIAGE
        # ── HUNTER 트랙 (v2.0 신규) ──
        "hunter_entry": None,          # None | "0" | "1" | "2" | "3" | "4" | "5"
        "hunter_input": "",            # 입구 0 자유 텍스트 또는 입구별 입력
        "hunter_classified": None,     # 입구 0 자동분류 결과 (Sonnet)
        "hunter_stage_data": {},       # 입구별 진행 데이터 (질문 응답, 시드 후보 등)
        "hunter_output": None,         # 최종 LOCKED 시드 JSON (TRIAGE 입력으로 전달)
        # ── TRIAGE 트랙 (v1.0 호환) ──
        "current_stage": 1,
        "stage_1_input": None,
        "stage_2_logline": None,
        "stage_3_hook": None,
        "stage_4_format": None,
        "stage_5_reference": None,
        "stage_6_market": None,
        "stage_7_verdict": None,
        "selected_logline": None,
        "seed_loaded_from_hunter": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_session():
    keys_to_clear = [
        "mode",
        "hunter_entry", "hunter_input", "hunter_classified",
        "hunter_stage_data", "hunter_output",
        "current_stage", "stage_1_input", "stage_2_logline",
        "stage_3_hook", "stage_4_format", "stage_5_reference",
        "stage_6_market", "stage_7_verdict", "selected_logline",
        "seed_loaded_from_hunter",
    ]
    for k in keys_to_clear:
        if k in st.session_state:
            del st.session_state[k]
    init_session_state()


def reset_triage_only():
    """TRIAGE 트랙만 리셋 (HUNTER 결과는 보존)."""
    keys = [
        "current_stage", "stage_1_input", "stage_2_logline",
        "stage_3_hook", "stage_4_format", "stage_5_reference",
        "stage_6_market", "stage_7_verdict", "selected_logline",
        "seed_loaded_from_hunter",
    ]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state["current_stage"] = 1
    st.session_state["seed_loaded_from_hunter"] = False


def reset_hunter_only():
    """HUNTER 트랙만 리셋 (TRIAGE 진행 상태는 보존)."""
    keys = [
        "hunter_entry", "hunter_input", "hunter_classified",
        "hunter_stage_data", "hunter_output",
    ]
    for k in keys:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state["hunter_entry"] = None
    st.session_state["hunter_input"] = ""
    st.session_state["hunter_stage_data"] = {}


def transfer_hunter_seed_to_triage():
    """HUNTER 출력 시드를 TRIAGE Stage 1 입력 형식으로 변환 후 전달.

    HUNTER 시드 JSON 예상 스키마:
    {
        "title": str, "genre": str, "target_market": str,
        "format_pref": str, "raw_idea": str,
        "hunter_meta": {"entry": "1"~"5", "discovery_notes": [...]}
    }
    """
    seed = st.session_state.get("hunter_output")
    if not seed:
        return False

    st.session_state["stage_1_input"] = {
        "title": seed.get("title", "(제목 미정)"),
        "genre": seed.get("genre", "장르 미정"),
        "target_market": seed.get("target_market", "한국 + 글로벌"),
        "format": seed.get("format_pref", "미정 (Idea Engine이 추천)"),
        "raw_idea": seed.get("raw_idea", ""),
        "_hunter_meta": seed.get("hunter_meta", {}),
    }
    st.session_state["current_stage"] = 1
    st.session_state["seed_loaded_from_hunter"] = True
    return True


init_session_state()

# ─────────────────────────────────────
# Sidebar Engine Info (Writer Engine 동일)
# ─────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:12px;background:#F0F2FF;border-radius:8px;border-left:3px solid #191970;font-family:'Pretendard',sans-serif;">
        <div style="font-size:.72rem;color:#191970;font-weight:700;letter-spacing:.05em;margin-bottom:4px;">ENGINE INFO</div>
        <div style="font-size:1.05rem;font-weight:700;color:#191970;">Idea Engine</div>
        <div style="font-size:1.25rem;font-weight:900;color:#FFCB05;background:#191970;padding:2px 8px;border-radius:4px;display:inline-block;margin-top:4px;">
            {ENGINE_VERSION}
        </div>
        <div style="font-size:.7rem;color:#666;margin-top:8px;">
            Build: {ENGINE_BUILD_DATE}<br>
            HUNTER 발굴 + TRIAGE 진단<br>
            <span style="color:#191970;font-weight:600;">+ v1.1 Creator v2.5.2 정합</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── 모드 전환 패널 (v2.0 신규) ──
    current_mode = st.session_state.get("mode", "HOME")
    mode_label_map = {
        "HOME": "🏠 HOME",
        "HUNTER": "🎯 HUNTER (발굴)",
        "TRIAGE": "🔍 TRIAGE (진단)",
    }
    st.markdown(f"""
    <div style="padding:10px;background:#191970;border-radius:8px;font-family:'Pretendard',sans-serif;">
        <div style="font-size:.7rem;color:#FFCB05;font-weight:700;letter-spacing:.05em;margin-bottom:4px;">CURRENT MODE</div>
        <div style="font-size:.95rem;color:#fff;font-weight:700;">{mode_label_map[current_mode]}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown("###### 🔀 모드 전환")

    if st.button("🏠 홈", key="nav_home", use_container_width=True):
        st.session_state["mode"] = "HOME"
        st.rerun()
    if st.button("🎯 HUNTER 트랙", key="nav_hunter", use_container_width=True):
        st.session_state["mode"] = "HUNTER"
        st.session_state["hunter_entry"] = None
        st.rerun()
    if st.button("🔍 TRIAGE 트랙", key="nav_triage", use_container_width=True):
        st.session_state["mode"] = "TRIAGE"
        st.rerun()

    # ── HUNTER → TRIAGE 시드 전송 (시드 준비된 경우만 노출) ──
    if st.session_state.get("hunter_output"):
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="padding:8px 10px;background:#FFCB05;border-radius:6px;font-family:'Pretendard',sans-serif;font-size:.75rem;color:#191970;font-weight:700;">
            🔗 HUNTER 시드 준비됨
        </div>
        """, unsafe_allow_html=True)
        if st.button("→ TRIAGE로 전송", key="seed_to_triage", use_container_width=True, type="primary"):
            transfer_hunter_seed_to_triage()
            st.session_state["mode"] = "TRIAGE"
            st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="padding:10px;background:#FFF8DC;border-radius:8px;font-family:'Pretendard',sans-serif;font-size:.78rem;">
        <div style="font-weight:700;color:#191970;margin-bottom:4px;">🤖 모델 정책</div>
        <div style="color:#444;">진단 ②~⑥: <b>Sonnet 4.6</b></div>
        <div style="color:#444;">최종 판정 ⑦: <b>Opus 4.7</b></div>
        <div style="color:#444;">HUNTER 발굴: <b>Sonnet 4.6</b></div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("버전이 최신인지 확인하세요.")

# ─────────────────────────────────────
# Custom CSS (Writer Engine v3.1 동일 톤)
# ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://cdn.jsdelivr.net/gh/projectnoonnu/2408-3@latest/Paperlogy.css');
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&display=swap');

:root {
    --navy: #191970; --y: #FFCB05; --bg: #F7F7F5;
    --card: #FFFFFF; --card-border: #E2E2E0; --t: #1A1A2E;
    --g: #2EC484; --r: #D33F49; --o: #E8B800;
    --dim: #8E8E99; --light-bg: #EEEEF6;
    --serif: 'Paperlogy', 'Noto Serif KR', 'Georgia', serif;
    --display: 'Playfair Display', 'Paperlogy', 'Georgia', serif;
    --body: 'Pretendard', -apple-system, sans-serif;
    --heading: 'Paperlogy', 'Pretendard', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--body); color: var(--t); -webkit-font-smoothing: antialiased;
}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], [data-testid="stHeader"],
[data-testid="stBottom"] {
    background-color: var(--bg) !important; color: var(--t) !important;
}
.stMarkdown, .stText, .stCode { color: var(--t) !important; }
h1,h2,h3,h4,h5,h6 { color: var(--navy) !important; font-family: var(--heading) !important; }
p, span, label, div, li { color: inherit; }

.stTextInput input, .stTextArea textarea,
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background-color: var(--card) !important; color: var(--t) !important;
    border: 1.5px solid var(--card-border) !important; border-radius: 8px !important;
    font-family: var(--body) !important; font-size: 0.92rem !important;
    padding: 0.65rem 0.85rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus,
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 2px rgba(25,25,112,0.08) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder,
[data-testid="stTextInput"] input::placeholder, [data-testid="stTextArea"] textarea::placeholder {
    color: var(--dim) !important; font-size: 0.85rem !important;
}
.stSelectbox > div > div, [data-baseweb="select"] > div, [data-baseweb="select"] input {
    background-color: var(--card) !important; color: var(--t) !important;
    border-color: var(--card-border) !important; border-radius: 8px !important;
}
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"], [role="option"] {
    background-color: var(--card) !important; color: var(--t) !important;
}
[role="option"]:hover { background-color: var(--light-bg) !important; }
.stTextInput label, .stTextArea label, .stSelectbox label, .stRadio label, .stFileUploader label {
    color: var(--t) !important; font-weight: 600 !important;
    font-size: 0.82rem !important; margin-bottom: 0.3rem !important;
}

.stButton > button {
    color: var(--t) !important; border: 1.5px solid var(--card-border) !important;
    background-color: var(--card) !important; border-radius: 8px !important;
    font-family: var(--body) !important; font-weight: 700 !important;
    font-size: 0.88rem !important; padding: 0.55rem 1.2rem !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    border-color: var(--navy) !important;
    box-shadow: 0 2px 8px rgba(25,25,112,0.08) !important;
}
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background-color: var(--y) !important; color: var(--navy) !important;
    border-color: var(--y) !important; font-weight: 800 !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background-color: #E8B800 !important;
    box-shadow: 0 2px 12px rgba(255,203,5,0.3) !important;
}
.stDownloadButton > button {
    color: var(--navy) !important; border: 1.5px solid var(--y) !important;
    background-color: var(--y) !important; border-radius: 8px !important;
    font-family: var(--body) !important; font-weight: 800 !important;
    font-size: 0.88rem !important; padding: 0.55rem 1.2rem !important;
}
.stExpander, details, details summary {
    background-color: var(--card) !important; color: var(--t) !important;
    border: 1px solid var(--card-border) !important; border-radius: 8px !important;
}
details[open] > div { background-color: var(--card) !important; }
.stExpander summary, .stExpander summary span { color: var(--t) !important; }
.stAlert { color: var(--t) !important; border-radius: 8px !important; }
[data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"],
[data-testid="stColumn"] { background-color: transparent !important; }

.header {
    font-size: 0.85rem; font-weight: 700; color: var(--navy);
    letter-spacing: 0.15em; font-family: var(--heading);
}
.brand-title {
    font-size: 2.6rem; font-weight: 900; color: var(--navy);
    font-family: var(--display); letter-spacing: -0.02em;
    position: relative; display: inline-block;
}
.brand-title::after {
    content: ''; position: absolute; bottom: 2px; left: 0;
    width: 100%; height: 4px; background: var(--y); border-radius: 2px;
}
.sub {
    font-size: 0.7rem; color: var(--dim); letter-spacing: 0.15em;
    margin-top: 0.5rem; margin-bottom: 1.5rem;
}
.callout {
    background: var(--light-bg); border-left: 4px solid var(--navy);
    padding: 0.9rem 1.1rem; margin: 0.5rem 0;
    border-radius: 0 8px 8px 0; font-size: 0.88rem; color: var(--t);
}
.cl {
    color: var(--navy); font-weight: 700; font-size: 0.72rem;
    letter-spacing: 0.03em; margin-bottom: 0.3rem; text-transform: uppercase;
}
.section-header {
    background: var(--y); color: var(--navy);
    padding: 0.6rem 1rem; border-radius: 6px;
    font-weight: 800; font-size: 1rem; font-family: var(--heading);
    margin: 1.5rem 0 0.8rem 0;
    display: flex; justify-content: space-between; align-items: center;
}
.section-header .en {
    font-family: var(--display); font-size: 0.75rem;
    font-weight: 700; letter-spacing: 0.05em; opacity: 0.7;
}
.small-meta {
    font-size: 0.78rem; color: var(--dim);
    margin-top: -0.2rem; margin-bottom: 0.5rem;
}
.beat-tag {
    background: var(--navy); color: var(--y);
    display: inline-block; padding: 0.2rem 0.7rem;
    border-radius: 4px; font-size: 0.78rem; font-weight: 800;
    letter-spacing: 0.04em; margin-bottom: 0.4rem;
}
.act-tag {
    background: var(--navy); color: #fff;
    display: inline-block; padding: 0.25rem 0.8rem;
    border-radius: 4px; font-size: 0.82rem; font-weight: 800;
    letter-spacing: 0.06em;
}

/* ── Idea Engine 전용 컴포넌트 ── */
.stepper {
    display: flex; gap: 4px; margin: 1.5rem 0;
    padding: 0.8rem; background: var(--card);
    border-radius: 10px; border: 1px solid var(--card-border);
    overflow-x: auto;
}
.step {
    flex: 1; text-align: center; padding: 0.5rem 0.4rem;
    border-radius: 6px; font-size: 0.75rem;
    font-family: var(--heading); font-weight: 700;
    color: var(--dim); border: 1.5px solid transparent;
    min-width: 90px;
}
.step.active {
    background: var(--y); color: var(--navy);
    border-color: var(--y);
}
.step.done {
    background: var(--light-bg); color: var(--navy);
    border-color: var(--navy);
}
.step .num {
    font-size: 1rem; font-weight: 900; display: block;
    font-family: var(--display);
}

.score-card {
    background: var(--card); border: 1px solid var(--card-border);
    border-radius: 8px; padding: 0.9rem 1.1rem; margin: 0.5rem 0;
    border-left-width: 5px;
}
.score-card.pass { border-left-color: var(--g); }
.score-card.warn { border-left-color: var(--o); }
.score-card.fail { border-left-color: var(--r); }
.score-card .axis-name {
    font-weight: 800; font-family: var(--heading);
    color: var(--navy); font-size: 0.95rem;
}
.score-card .axis-score {
    font-family: var(--display); font-weight: 900;
    font-size: 1.4rem; margin-left: 0.5rem;
}
.score-card .axis-comment {
    color: var(--dim); font-size: 0.85rem; margin-top: 0.2rem;
}

.metric-tile {
    background: var(--card); border: 1px solid var(--card-border);
    border-radius: 10px; padding: 1rem; text-align: center;
}
.metric-tile .num {
    font-family: var(--display); font-size: 2.2rem; font-weight: 900;
    color: var(--navy); line-height: 1;
}
.metric-tile .label {
    font-size: 0.75rem; color: var(--dim); margin-top: 0.4rem;
    text-transform: uppercase; letter-spacing: 0.08em;
    font-family: var(--heading); font-weight: 700;
}

.verdict-box {
    padding: 2.5rem 2rem; border-radius: 12px; margin: 1.5rem 0;
    text-align: center; font-family: var(--display);
    border: 3px solid;
}
.verdict-box.go { background: linear-gradient(135deg,#E8F5E9,#C8E6C9); border-color: var(--g); }
.verdict-box.cond { background: linear-gradient(135deg,#FFF8E1,#FFECB3); border-color: var(--o); }
.verdict-box.nogo { background: linear-gradient(135deg,#FFEBEE,#FFCDD2); border-color: var(--r); }
.verdict-box .verdict-label {
    font-size: 3rem; font-weight: 900; letter-spacing: 0.12em;
    margin: 0; line-height: 1;
}

.locked-card {
    background: var(--navy); color: white;
    padding: 1.5rem 1.7rem; border-radius: 10px; margin: 1rem 0;
    border-left: 6px solid var(--y);
}
.locked-card .field-label {
    color: var(--y); font-size: 0.72rem;
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-bottom: 0.3rem; font-family: var(--heading); font-weight: 700;
}
.locked-card .field-value {
    color: white; font-size: 0.95rem; margin-bottom: 1rem;
    line-height: 1.5;
}
.locked-card .field-value:last-child { margin-bottom: 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────
# Anthropic Client + JSON Parser
# ─────────────────────────────────────
def get_anthropic_client() -> Optional[Anthropic]:
    api_key = st.secrets.get("ANTHROPIC_API_KEY", os.getenv("ANTHROPIC_API_KEY"))
    return Anthropic(api_key=api_key) if api_key else None


def safe_json_loads(text: str) -> Dict[str, Any]:
    """4단계 JSON 복구 시스템"""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        pass

    try:
        candidate = text[text.find("{"):text.rfind("}") + 1]
        for _ in range(30):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError as e:
                pos = e.pos
                if 0 < pos < len(candidate):
                    candidate = candidate[:pos] + " " + candidate[pos + 1:]
                else:
                    break
    except Exception:
        pass

    try:
        cleaned = re.sub(r'(?<="):\s*"([^"]*)"\s*([,\}])',
                         lambda m: f': "{m.group(1).replace(chr(34), chr(39))}" {m.group(2)}',
                         text)
        return json.loads(cleaned)
    except Exception:
        return {"_parse_error": True, "_raw": text}


def call_claude(client: Anthropic, prompt_text: str, model: str = ANTHROPIC_MODEL_SONNET) -> Dict[str, Any]:
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt_text}],
    )
    raw = response.content[0].text
    return safe_json_loads(raw)


# ─────────────────────────────────────
# DOCX Export
# ─────────────────────────────────────
def add_section_header_docx(doc, kr: str, en: str):
    p = doc.add_paragraph()
    run_kr = p.add_run(kr + " ")
    run_kr.font.size = Pt(14)
    run_kr.font.bold = True
    run_kr.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
    run_en = p.add_run(en)
    run_en.font.size = Pt(11)
    run_en.font.italic = True
    run_en.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'FFCB05')
    pPr.append(shd)


def add_para(doc, text: str, bold: bool = False, italic: bool = False, size: int = 11):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic


def build_diagnostic_docx(state: Dict[str, Any]) -> bytes:
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run("IDEA DIAGNOSTIC REPORT")
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
    
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run("아이디어 진단 보고서")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)
    
    doc.add_paragraph()
    inp = state["stage_1_input"]
    
    tp = doc.add_paragraph()
    tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = tp.add_run(inp["title"])
    run.font.size = Pt(20)
    run.font.bold = True
    
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = info.add_run(f"{inp['genre']} · {inp['format']} · {inp['target_market']}")
    run.font.size = Pt(11)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)

    doc.add_paragraph()
    doc.add_paragraph()
    
    today = doc.add_paragraph()
    today.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = today.add_run(f"발행일: {datetime.now().strftime('%Y년 %m월 %d일')}")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)
    
    bjp = doc.add_paragraph()
    bjp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = bjp.add_run(f"BLUE JEANS PICTURES · Idea Engine {ENGINE_VERSION}")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
    run.font.bold = True

    doc.add_page_break()

    add_section_header_docx(doc, "1. 원본 아이디어", "ORIGINAL IDEA")
    add_para(doc, inp["raw_idea"])
    doc.add_paragraph()

    if state["stage_2_logline"]:
        add_section_header_docx(doc, "2. 로그라인 정제", "LOGLINE REFINEMENT")
        ll = state["stage_2_logline"]
        for v in ll.get("logline_variants", []):
            add_para(doc, f"[{v['variant']}안 - {v['label']}]", bold=True)
            add_para(doc, v["logline"])
            add_para(doc, f"  강점: {v['strength']}", italic=True, size=10)
            add_para(doc, f"  약점: {v['weakness']}", italic=True, size=10)
            doc.add_paragraph()
        add_para(doc, f"▶ 추천: {ll.get('recommended', '')}안", bold=True)
        add_para(doc, ll.get("recommendation_reason", ""))
        doc.add_paragraph()

    if state["stage_3_hook"]:
        add_section_header_docx(doc, "3. 후크 진단 (Gate 0)", "HOOK DIAGNOSTIC")
        hk = state["stage_3_hook"]
        scores = hk.get("scores", {})
        
        tbl = doc.add_table(rows=6, cols=3)
        tbl.style = "Light Grid Accent 1"
        h = tbl.rows[0].cells
        h[0].text = "축"; h[1].text = "점수"; h[2].text = "코멘트"
        
        axis_kr = {
            "specificity": "구체성", "conflict_visibility": "갈등 가시성",
            "genre_clarity": "장르 명확성", "stakes": "판돈", "originality": "독창성"
        }
        for i, (k, kr) in enumerate(axis_kr.items(), 1):
            sc = scores.get(k, {})
            r = tbl.rows[i].cells
            r[0].text = kr
            r[1].text = f"{sc.get('score', 0)}/10"
            r[2].text = sc.get("comment", "")
        
        doc.add_paragraph()
        add_para(doc, f"총점: {hk.get('total_score', 0)}/50 — {hk.get('gate_status', '')}", bold=True, size=13)
        doc.add_paragraph()
        
        add_para(doc, "강점", bold=True)
        for s in hk.get("key_strengths", []):
            add_para(doc, f"  • {s}")
        doc.add_paragraph()
        add_para(doc, "약점", bold=True)
        for w in hk.get("key_weaknesses", []):
            add_para(doc, f"  • {w}")
        doc.add_paragraph()
        add_para(doc, "보강 제안", bold=True)
        for s in hk.get("improvement_suggestions", []):
            add_para(doc, f"  • {s}")
        doc.add_paragraph()

    if state["stage_4_format"]:
        add_section_header_docx(doc, "4. 포맷 추천", "FORMAT RECOMMENDATION")
        fm = state["stage_4_format"]
        fs = fm.get("format_scores", {})
        
        tbl = doc.add_table(rows=6, cols=3)
        tbl.style = "Light Grid Accent 1"
        h = tbl.rows[0].cells
        h[0].text = "포맷"; h[1].text = "점수"; h[2].text = "근거"
        
        format_kr = {
            "feature_film": "장편 영화", "ott_series": "OTT 시리즈",
            "mini_series": "미니시리즈", "short_form": "숏폼 드라마", "web_novel": "웹소설"
        }
        for i, (k, kr) in enumerate(format_kr.items(), 1):
            f = fs.get(k, {})
            r = tbl.rows[i].cells
            r[0].text = kr
            r[1].text = f"{f.get('score', 0)}/10"
            r[2].text = f.get("reason", "")
        
        doc.add_paragraph()
        primary = fm.get("primary_format_detail", {})
        add_para(doc, f"▶ 1순위: {primary.get('format_name', '')}", bold=True, size=13)
        if primary.get("episode_count"):
            add_para(doc, f"  회차: {primary['episode_count']}")
        if primary.get("runtime_per_episode"):
            add_para(doc, f"  회당 분량: {primary['runtime_per_episode']}")
        doc.add_paragraph()
        add_para(doc, "IP 빌딩 전략", bold=True)
        add_para(doc, fm.get("ip_building_strategy", ""))
        doc.add_paragraph()

    if state["stage_5_reference"]:
        add_section_header_docx(doc, "5. 레퍼런스 매핑", "REFERENCE MAPPING")
        rf = state["stage_5_reference"]
        for ref in rf.get("references", []):
            add_para(doc, f"《{ref['title']}》 ({ref.get('year', '')}, {ref.get('country', '')}) - {ref.get('format', '')}", bold=True)
            add_para(doc, f"  유사 차원: {ref.get('similarity_axis', '')}", italic=True, size=10)
            add_para(doc, f"  공통점: {ref.get('common_points', '')}")
            add_para(doc, f"  차별점: {ref.get('differentiation', '')}")
            doc.add_paragraph()
        warn = rf.get("lethal_similarity_warning", {})
        if warn.get("exists"):
            add_para(doc, "⚠ 치명적 유사작 경고", bold=True)
            add_para(doc, warn.get("details", ""))
        else:
            add_para(doc, "✓ 치명적 유사작 없음 - 안전", bold=True)
        doc.add_paragraph()
        add_para(doc, "차별화 요약", bold=True)
        add_para(doc, rf.get("differentiation_summary", ""))
        doc.add_paragraph()
        add_para(doc, "투자자 미팅 답변용", bold=True)
        add_para(doc, rf.get("investor_pitch_answer", ""))
        doc.add_paragraph()

    if state["stage_6_market"]:
        add_section_header_docx(doc, "6. 시장성 진단", "MARKET DIAGNOSTIC")
        mk = state["stage_6_market"]
        
        dom = mk.get("domestic_market", {})
        add_para(doc, f"한국 시장 ({'★' * dom.get('stars', 0)})", bold=True, size=13)
        ta = dom.get("target_audience", {})
        add_para(doc, f"  타겟: {ta.get('gender', '')} {ta.get('age_range', '')} - {ta.get('psychographic', '')}")
        add_para(doc, f"  예산: {dom.get('budget_estimate', '')}")
        add_para(doc, f"  유통: {', '.join(dom.get('distribution', []))}")
        add_para(doc, f"  IP 확장: {', '.join(dom.get('ip_extension_potential', []))}")
        doc.add_paragraph()
        
        glb = mk.get("global_market", {})
        add_para(doc, f"글로벌 시장 ({'★' * glb.get('stars', 0)})", bold=True, size=13)
        add_para(doc, f"  1차 타겟: {glb.get('primary_target_country', '')}")
        add_para(doc, f"  어필: {glb.get('global_appeal_strength', '')}")
        add_para(doc, f"  진입경로: {', '.join(glb.get('entry_path', []))}")
        add_para(doc, f"  약점: {glb.get('weakness', '')}")
        doc.add_paragraph()
        
        ott = mk.get("ott_market", {})
        add_para(doc, f"OTT 시장 ({'★' * ott.get('stars', 0)})", bold=True, size=13)
        fc = ott.get("first_choice_platform", {})
        sc = ott.get("second_choice_platform", {})
        add_para(doc, f"  1순위: {fc.get('name', '')} - {fc.get('reason', '')}")
        add_para(doc, f"  2순위: {sc.get('name', '')} - {sc.get('reason', '')}")
        add_para(doc, f"  최적 회차: {ott.get('optimal_episode_count', '')}")
        add_para(doc, f"  경쟁: {ott.get('competition_analysis', '')}")
        doc.add_paragraph()
        
        timing = mk.get("timing_fit", {})
        add_para(doc, f"시기적 적합성 ({'★' * timing.get('score', 0)})", bold=True)
        add_para(doc, timing.get("reason", ""))
        doc.add_paragraph()
        
        add_para(doc, "위험 신호", bold=True)
        for r in mk.get("risk_signals", []):
            add_para(doc, f"  • {r}")
        doc.add_paragraph()

    if state["stage_7_verdict"]:
        add_section_header_docx(doc, "7. 최종 판정", "FINAL VERDICT")
        vd = state["stage_7_verdict"]
        
        verdict = vd.get("final_verdict", "")
        vp = doc.add_paragraph()
        vp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = vp.add_run(f"  {verdict}  ")
        run.font.size = Pt(28)
        run.font.bold = True
        if verdict == "GO":
            run.font.color.rgb = RGBColor(0x2E, 0x7D, 0x32)
        elif verdict == "CONDITIONAL":
            run.font.color.rgb = RGBColor(0xF9, 0xA8, 0x25)
        else:
            run.font.color.rgb = RGBColor(0xC6, 0x28, 0x28)
        doc.add_paragraph()
        
        add_para(doc, "판정 사유", bold=True)
        add_para(doc, vd.get("verdict_reasoning", ""))
        doc.add_paragraph()
        
        if vd.get("conditional_requirements"):
            add_para(doc, "충족 조건 (CONDITIONAL)", bold=True)
            for c in vd["conditional_requirements"]:
                add_para(doc, f"  • {c}")
            doc.add_paragraph()
        
        if vd.get("nogo_alternative"):
            add_para(doc, "대안 제시 (NOGO)", bold=True)
            add_para(doc, vd["nogo_alternative"])
            doc.add_paragraph()
        
        add_para(doc, "확정된 핵심 결정", bold=True)
        for k in vd.get("key_decisions_made", []):
            add_para(doc, f"  • {k}")
        doc.add_paragraph()
        
        add_para(doc, "Creator Engine에서 결정해야 할 질문", bold=True)
        for q in vd.get("pending_decisions_for_creator", []):
            add_para(doc, f"  • {q}")
        doc.add_paragraph()
        
        add_section_header_docx(doc, "임원 요약", "EXECUTIVE SUMMARY")
        add_para(doc, vd.get("executive_summary", ""))
        doc.add_paragraph()
        
        add_section_header_docx(doc, "LOCKED 시드 패키지", "LOCKED SEED PACKAGE")
        add_para(doc, "Creator Engine 입력용 데이터 ─ 이 항목들은 Creator Engine에서 변경하지 않는다.", italic=True, size=10)
        doc.add_paragraph()
        
        seed = vd.get("locked_seed_package", {})
        add_para(doc, f"Project ID: {seed.get('project_id', '')}", bold=True, size=11)
        add_para(doc, f"제목 (KR): {seed.get('title_kr', '')}")
        add_para(doc, f"제목 (EN): {seed.get('title_en', '')}")
        doc.add_paragraph()
        
        add_para(doc, "LOCKED LOGLINE", bold=True)
        add_para(doc, seed.get("locked_logline", ""))
        doc.add_paragraph()
        
        add_para(doc, "LOCKED GENRE", bold=True)
        gn = seed.get("locked_genre", {})
        add_para(doc, f"  Primary: {gn.get('primary', '')}")
        add_para(doc, f"  Secondary: {gn.get('secondary', '')}")
        if gn.get("tertiary"):
            add_para(doc, f"  Tertiary: {gn['tertiary']}")
        doc.add_paragraph()
        
        add_para(doc, "LOCKED FORMAT", bold=True)
        ft = seed.get("locked_format", {})
        add_para(doc, f"  Primary: {ft.get('primary', '')}")
        if ft.get("episode_count"):
            add_para(doc, f"  Episodes: {ft['episode_count']}")
        if ft.get("runtime"):
            add_para(doc, f"  Runtime: {ft['runtime']}")
        add_para(doc, f"  IP Strategy: {ft.get('ip_strategy', '')}")
        doc.add_paragraph()
        
        add_para(doc, "LOCKED TARGET", bold=True)
        tg = seed.get("locked_target", {})
        add_para(doc, f"  Domestic: {tg.get('domestic', '')}")
        add_para(doc, f"  Global: {tg.get('global', '')}")
        doc.add_paragraph()
        
        add_para(doc, "LOCKED THEME", bold=True)
        th = seed.get("locked_theme", {})
        add_para(doc, f"  Surface: {th.get('surface', '')}")
        add_para(doc, f"  Deep: {th.get('deep', '')}")
        doc.add_paragraph()
        
        add_para(doc, "LOCKED REFERENCES", bold=True)
        for r in seed.get("locked_references", []):
            add_para(doc, f"  • {r}")
        doc.add_paragraph()
        
        add_para(doc, f"Hook Score: {seed.get('locked_hook_score', '')}/50", bold=True)
        ms = seed.get("locked_market_stars", {})
        add_para(doc, f"Market Stars: 한국 {'★' * ms.get('domestic', 0)} / 글로벌 {'★' * ms.get('global', 0)} / OTT {'★' * ms.get('ott', 0)}")
        add_para(doc, f"Distribution Priority: {seed.get('locked_distribution_priority', '')}")
        doc.add_paragraph()
        
        add_para(doc, "Creator Engine 진행 시 다뤄야 할 위험", bold=True)
        for risk in seed.get("locked_risks_to_address", []):
            add_para(doc, f"  • {risk}")

        # ════════════════════════════════════════════════════════
        # v1.1 — Creator Engine v2.5.2 정합 5개 신규 LOCKED 영역
        # ════════════════════════════════════════════════════════
        doc.add_paragraph()
        add_section_header_docx(
            doc, "v1.1 신규 LOCKED 영역",
            "CREATOR ENGINE v2.5.2 ABSORPTION KEYS"
        )
        add_para(
            doc,
            "Creator Engine v2.5.2가 작품 본질로 절대 보존하는 5개 영역. "
            "「오랜만에」 검증에서 발견된 핵심 모티프 휘발(61%)을 차단하기 위해 도입.",
            italic=True, size=10,
        )
        doc.add_paragraph()

        # ① locked_core_decisions
        core_decisions = seed.get("locked_core_decisions", []) or []
        add_para(doc, f"① 확정된 핵심 결정 (locked_core_decisions) — {len(core_decisions)}건", bold=True)
        if not core_decisions:
            add_para(doc, "  (이 작품에는 별도로 LOCK된 핵심 결정이 없음 — 빈 배열)", italic=True, size=10)
        else:
            for d in core_decisions:
                if isinstance(d, dict):
                    cat = d.get("category", "")
                    rule = d.get("rule", "") or d.get("decision", "")
                    rationale = d.get("rationale", "")
                    if cat and rule:
                        add_para(doc, f"  • [{cat}] {rule}")
                    elif rule:
                        add_para(doc, f"  • {rule}")
                    if rationale:
                        add_para(doc, f"      근거: {rationale}", italic=True, size=10)
                elif isinstance(d, str):
                    add_para(doc, f"  • {d}")
        doc.add_paragraph()

        # ② locked_music_rules
        music_rules = seed.get("locked_music_rules", {}) or {}
        add_para(
            doc,
            f"② 음악 사용 규약 (locked_music_rules) — {'있음' if music_rules else '없음 (빈 객체)'}",
            bold=True,
        )
        if not music_rules:
            add_para(doc, "  (이 작품에는 음악 사용 규약이 없음 — 액션·스릴러·호러에서 자주 발생)", italic=True, size=10)
        elif isinstance(music_rules, dict):
            for k, v in music_rules.items():
                if isinstance(v, list):
                    add_para(doc, f"  • [{k}]")
                    for item in v:
                        add_para(doc, f"      - {item}")
                else:
                    add_para(doc, f"  • [{k}] {v}")
        elif isinstance(music_rules, list):
            for r in music_rules:
                add_para(doc, f"  • {r}")
        else:
            add_para(doc, f"  • {music_rules}")
        doc.add_paragraph()

        # ③ locked_visual_motifs
        visual_motifs = seed.get("locked_visual_motifs", []) or []
        add_para(doc, f"③ 시각 모티프 (locked_visual_motifs) — {len(visual_motifs)}건", bold=True)
        if not visual_motifs:
            add_para(doc, "  (이 작품에는 LOCK된 시각 모티프가 없음 — 빈 배열)", italic=True, size=10)
        else:
            for m in visual_motifs:
                if isinstance(m, dict):
                    motif = m.get("motif", "") or m.get("name", "")
                    function = m.get("function", "") or m.get("role", "")
                    if motif and function:
                        add_para(doc, f"  • {motif} → {function}")
                    elif motif:
                        add_para(doc, f"  • {motif}")
                elif isinstance(m, str):
                    add_para(doc, f"  • {m}")
        doc.add_paragraph()

        # ④ locked_ending_form
        ending_form = seed.get("locked_ending_form", {}) or {}
        add_para(
            doc,
            f"④ 결말 형식 (locked_ending_form) — {'LOCK됨' if ending_form else '미확정 (빈 객체)'}",
            bold=True,
        )
        if not ending_form:
            add_para(doc, "  (결말 형식이 LOCK되지 않음 — Creator Engine이 결정)", italic=True, size=10)
        elif isinstance(ending_form, dict):
            if ending_form.get("type"):
                add_para(doc, f"  • 결말 유형: {ending_form['type']}")
            if ending_form.get("emotional_resolution"):
                add_para(doc, f"  • 정서적 해소: {ending_form['emotional_resolution']}")
            if ending_form.get("final_image"):
                add_para(doc, f"  • 마지막 이미지: {ending_form['final_image']}")
            if ending_form.get("forbidden"):
                add_para(doc, f"  • 금지 패턴: {ending_form['forbidden']}")
        else:
            add_para(doc, f"  • {ending_form}")
        doc.add_paragraph()

        # ⑤ locked_creator_questions
        creator_questions = seed.get("locked_creator_questions", []) or []
        add_para(
            doc,
            f"⑤ Creator Engine 결정 의제 (locked_creator_questions) — {len(creator_questions)}건",
            bold=True,
        )
        if not creator_questions:
            add_para(doc, "  (Creator Engine이 답할 의제가 없음 — 빈 배열)", italic=True, size=10)
        else:
            for q in creator_questions:
                if isinstance(q, dict):
                    question = q.get("question", "")
                    options = q.get("options", []) or []
                    importance = q.get("importance", "")
                    line = f"  • {question}"
                    if importance:
                        line += f"  [중요도: {importance.upper()}]"
                    add_para(doc, line)
                    if options:
                        add_para(doc, f"      후보: {' / '.join(str(o) for o in options)}", italic=True, size=10)
                elif isinstance(q, str):
                    add_para(doc, f"  • {q}")

    doc.add_paragraph()
    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run(f"© 2026 BLUE JEANS PICTURES · Idea Engine {ENGINE_VERSION}")
    run.font.size = Pt(9)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def build_seed_json(state: Dict[str, Any]) -> str:
    if not state.get("stage_7_verdict"):
        return "{}"
    seed = state["stage_7_verdict"].get("locked_seed_package", {})

    # ─── v1.1: Creator Engine v2.5.2 정합 5개 신규 키 빈 값 보장 ───
    # 작품 특성상 해당 없는 영역도 키 자체는 명시 출력 (Creator Engine이
    # "Idea Engine이 의식적으로 비웠다"는 신호로 해석)
    seed.setdefault("locked_core_decisions", [])
    seed.setdefault("locked_music_rules", {})
    seed.setdefault("locked_visual_motifs", [])
    seed.setdefault("locked_ending_form", {})
    seed.setdefault("locked_creator_questions", [])

    creator_input = {
        "_idea_engine_meta": {
            "version": ENGINE_VERSION,
            "patch": "v1.1 (Creator Engine v2.5.2 정합 5키)",
            "generated_at": datetime.now().isoformat(),
            "project_id": seed.get("project_id", ""),
            "verdict": state["stage_7_verdict"].get("final_verdict", ""),
            "hook_score": seed.get("locked_hook_score", 0),
        },
        "title": seed.get("title_kr", ""),
        "raw_idea": seed.get("locked_logline", ""),
        "genre": seed.get("locked_genre", {}).get("primary", ""),
        "target_market": seed.get("locked_target", {}).get("domestic", ""),
        "format": seed.get("locked_format", {}).get("primary", ""),
        "locked_seed": seed,
        "executive_summary": state["stage_7_verdict"].get("executive_summary", ""),
        "pending_decisions": state["stage_7_verdict"].get("pending_decisions_for_creator", []),
    }
    return json.dumps(creator_input, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════
# HEADER (Writer Engine 양식 동일)
# ═══════════════════════════════════════════════════════════
st.markdown(
    '<div style="text-align:center;padding:1rem 0 0 0">'
    '<div class="header">B L U E &nbsp; J E A N S &nbsp; P I C T U R E S</div>'
    '<div class="brand-title">IDEA ENGINE</div>'
    '<div class="sub">Y O U N G &nbsp; · &nbsp; V I N T A G E &nbsp; · &nbsp; F R E E &nbsp; · &nbsp; I N N O V A T I V E</div>'
    '</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────
# Stepper
# ─────────────────────────────────────
def render_stepper(current: int):
    stages_meta = [
        (1, "아이디어"), (2, "로그라인"), (3, "Hook"),
        (4, "Format"), (5, "Reference"), (6, "Market"), (7, "최종 판정")
    ]
    completed_keys = {
        1: "stage_1_input", 2: "stage_2_logline", 3: "stage_3_hook",
        4: "stage_4_format", 5: "stage_5_reference", 6: "stage_6_market",
        7: "stage_7_verdict"
    }
    
    html = '<div class="stepper">'
    for num, name in stages_meta:
        completed = bool(st.session_state.get(completed_keys[num]))
        if num == current:
            cls = "step active"
            label_num = f"<span class='num'>{num}</span>"
        elif completed:
            cls = "step done"
            label_num = "<span class='num'>✓</span>"
        else:
            cls = "step"
            label_num = f"<span class='num'>{num}</span>"
        html += f'<div class="{cls}">{label_num}{name}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def section_header(kr: str, en: str):
    st.markdown(
        f'<div class="section-header">{kr} <span class="en">{en}</span></div>',
        unsafe_allow_html=True,
    )


def small_meta(text: str):
    st.markdown(f'<div class="small-meta">{text}</div>', unsafe_allow_html=True)


# ─────────────────────────────────────
# STAGE PAGES
# ─────────────────────────────────────
def page_stage_1():
    section_header("📥 STEP 1 · 아이디어 입력", "FROM RAW IDEA")
    small_meta("모호한 아이디어 한 줄부터 한 단락까지 자유롭게 입력하세요. Idea Engine이 정제하여 Creator Engine이 받아먹을 수 있는 LOCKED 시드 패키지로 변환합니다.")
    
    with st.form("s1"):
        c1, c2 = st.columns([2, 1])
        with c1:
            title = st.text_input("프로젝트 제목 (가제)", placeholder="예: 만물트럭 탐정")
        with c2:
            genre = st.selectbox(
                "장르",
                ["미지정", "범죄/스릴러", "드라마", "액션", "로맨스", "코미디",
                 "호러/공포", "SF", "판타지", "코지 미스터리", "느와르", "사회파", "직접 입력"]
            )
            if genre == "직접 입력":
                genre = st.text_input("장르 직접 입력", key="genre_direct")
        
        c3, c4 = st.columns(2)
        with c3:
            target_market = st.selectbox(
                "타겟 시장",
                ["한국 + 글로벌", "한국 (국내)", "글로벌 (해외)", "일본", "동남아", "직접 입력"]
            )
            if target_market == "직접 입력":
                target_market = st.text_input("타겟 시장 직접 입력", key="market_direct")
        with c4:
            format_pref = st.selectbox(
                "선호 포맷",
                ["미정 (Idea Engine이 추천)", "장편 영화", "OTT 시리즈", "미니시리즈",
                 "숏폼 드라마", "웹소설", "웹툰"]
            )
        
        raw_idea = st.text_area(
            "원본 아이디어 (필수)",
            height=220,
            placeholder=(
                "예시:\n"
                "만물트럭(한국) - 이동편의점(일본) 결합\n"
                "만물트럭 탐정 — 셜록홈즈 탐정물\n"
                "고령화된 마을을 돌아다니며 사건 해결\n"
                "추리소설 광이었던 주인공이 깨어나보니 만물트럭 운전사가 되어있었다\n"
                "1. 사라진 시체 / 2. 독극물 살인사건 / 3. 아무도 죽이지 않았다"
            ),
        )
        
        submitted = st.form_submit_button("진단 시작 →", type="primary", use_container_width=True)
        
        if submitted:
            if not title.strip() or not raw_idea.strip():
                st.error("제목과 원본 아이디어는 필수입니다.")
            else:
                st.session_state["stage_1_input"] = {
                    "title": title.strip(),
                    "genre": genre if genre != "미지정" else "장르 미정",
                    "target_market": target_market,
                    "format": format_pref,
                    "raw_idea": raw_idea.strip(),
                }
                st.session_state["current_stage"] = 2
                st.rerun()


def page_stage_2():
    section_header("✍ STEP 2 · 로그라인 정제", "REFINE TO STANDARD")
    small_meta("원본 아이디어를 산업 표준 로그라인 3개 변형으로 정제합니다. Sonnet이 작성합니다.")
    
    inp = st.session_state["stage_1_input"]
    
    if not st.session_state.get("stage_2_logline"):
        if st.button("🪄 로그라인 정제 실행", type="primary", use_container_width=True):
            client = get_anthropic_client()
            if not client:
                st.warning("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
                return
            with st.spinner("Sonnet이 로그라인 3개 변형 작성 중..."):
                prompt_text = P.LOGLINE_REFINE_PROMPT.format(**inp)
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패. 다시 시도해주세요.")
                    with st.expander("Raw 응답"):
                        st.text(result.get("_raw", ""))
                    return
                st.session_state["stage_2_logline"] = result
                st.rerun()
    else:
        ll = st.session_state["stage_2_logline"]
        for v in ll.get("logline_variants", []):
            st.markdown(f"**[{v['variant']}안 — {v['label']}]**")
            st.markdown(f"<div class='callout'>{v['logline']}</div>", unsafe_allow_html=True)
            cs, cw = st.columns(2)
            with cs:
                st.caption(f"✓ 강점: {v['strength']}")
            with cw:
                st.caption(f"✗ 약점: {v['weakness']}")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        
        st.success(f"**▶ 추천: {ll.get('recommended', '')}안** — {ll.get('recommendation_reason', '')}")
        st.markdown("---")
        st.markdown("**채택할 로그라인을 선택하세요**")
        
        options = {f"{v['variant']}안 - {v['label']}": v['logline']
                   for v in ll.get("logline_variants", [])}
        recommended_key = None
        for k in options:
            if k.startswith(ll.get("recommended", "A")):
                recommended_key = k
                break
        
        choice = st.radio(
            "로그라인 선택",
            list(options.keys()),
            index=list(options.keys()).index(recommended_key) if recommended_key else 0,
            label_visibility="collapsed"
        )
        st.session_state["selected_logline"] = options[choice]
        
        cb, cr, cn = st.columns([1, 1, 2])
        with cb:
            if st.button("← 이전"):
                st.session_state["current_stage"] = 1
                st.rerun()
        with cr:
            if st.button("재실행"):
                st.session_state["stage_2_logline"] = None
                st.rerun()
        with cn:
            if st.button("Hook 진단으로 →", type="primary", use_container_width=True):
                st.session_state["current_stage"] = 3
                st.rerun()


def page_stage_3():
    section_header("🎯 STEP 3 · 후크 진단", "GATE 0 · 5-AXIS SCORING")
    small_meta("5축 × 10점 = 50점 만점으로 채점. 35점 이상 PASS / 25~34 CONDITIONAL / 24 이하 FAIL.")
    
    inp = st.session_state["stage_1_input"]
    logline = st.session_state.get("selected_logline", "")
    
    if not st.session_state.get("stage_3_hook"):
        if st.button("🎯 Hook 진단 실행", type="primary", use_container_width=True):
            client = get_anthropic_client()
            if not client:
                st.warning("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
                return
            with st.spinner("Sonnet이 5축 진단 중..."):
                prompt_text = P.HOOK_DIAGNOSTIC_PROMPT.format(
                    title=inp["title"], logline=logline,
                    genre=inp["genre"], format=inp["format"], raw_idea=inp["raw_idea"],
                )
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패")
                    return
                st.session_state["stage_3_hook"] = result
                st.rerun()
    else:
        hk = st.session_state["stage_3_hook"]
        scores = hk.get("scores", {})
        axis_kr = {
            "specificity": "구체성", "conflict_visibility": "갈등 가시성",
            "genre_clarity": "장르 명확성", "stakes": "판돈", "originality": "독창성"
        }
        
        categories = list(axis_kr.values())
        values = [scores.get(k, {}).get("score", 0) for k in axis_kr.keys()]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values, theta=categories, fill='toself', name='Hook Score',
            line=dict(color='#191970', width=2),
            fillcolor='rgba(255, 203, 5, 0.4)'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=12, family='Pretendard'))
            ),
            showlegend=False, height=400, margin=dict(l=80, r=80, t=40, b=40),
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
        )
        
        cc, cs = st.columns([1, 1])
        with cc:
            st.plotly_chart(fig, use_container_width=True)
        with cs:
            total = hk.get("total_score", 0)
            status = hk.get("gate_status", "")
            st.markdown(f"""
            <div class="metric-tile">
                <div class="num">{total}/50</div>
                <div class="label">TOTAL HOOK SCORE</div>
            </div>
            """, unsafe_allow_html=True)
            
            if status == "PASS":
                st.success(f"🟢 **{status}** — 35점 이상으로 GO 진행 가능")
            elif status == "CONDITIONAL":
                st.warning(f"🟡 **{status}** — 약점 보강 필요")
            else:
                st.error(f"🔴 **{status}** — 재고 권장")
        
        st.markdown("**축별 진단**")
        for k, kr in axis_kr.items():
            sc = scores.get(k, {})
            score = sc.get("score", 0)
            cls = "pass" if score >= 7 else "warn" if score >= 5 else "fail"
            st.markdown(f"""
            <div class="score-card {cls}">
                <span class="axis-name">{kr}</span>
                <span class="axis-score">{score}/10</span>
                <div class="axis-comment">{sc.get('comment', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        cs1, cw1 = st.columns(2)
        with cs1:
            st.markdown("**핵심 강점**")
            for s in hk.get("key_strengths", []):
                st.markdown(f"- {s}")
        with cw1:
            st.markdown("**핵심 약점**")
            for w in hk.get("key_weaknesses", []):
                st.markdown(f"- {w}")
        
        st.markdown("**보강 제안**")
        for s in hk.get("improvement_suggestions", []):
            st.markdown(f"- {s}")
        
        st.markdown("---")
        cb, cr, cn = st.columns([1, 1, 2])
        with cb:
            if st.button("← 이전"):
                st.session_state["current_stage"] = 2
                st.rerun()
        with cr:
            if st.button("재실행"):
                st.session_state["stage_3_hook"] = None
                st.rerun()
        with cn:
            if status == "FAIL":
                st.error("🔴 FAIL — Override 시 진행 가능")
                if st.button("⚠ Override하고 Format으로 →", use_container_width=True):
                    st.session_state["current_stage"] = 4
                    st.rerun()
            else:
                if st.button("Format 추천으로 →", type="primary", use_container_width=True):
                    st.session_state["current_stage"] = 4
                    st.rerun()


def page_stage_4():
    section_header("📐 STEP 4 · 포맷 추천", "5 FORMAT FIT")
    small_meta("5개 포맷 적합도를 동시 판정합니다. 1순위 포맷이 자동 추천됩니다.")
    
    inp = st.session_state["stage_1_input"]
    logline = st.session_state.get("selected_logline", "")
    
    if not st.session_state.get("stage_4_format"):
        if st.button("📐 포맷 추천 실행", type="primary", use_container_width=True):
            client = get_anthropic_client()
            with st.spinner("Sonnet이 5개 포맷 적합도 판정 중..."):
                prompt_text = P.FORMAT_RECOMMEND_PROMPT.format(
                    title=inp["title"], logline=logline,
                    genre=inp["genre"], raw_idea=inp["raw_idea"],
                )
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패")
                    return
                st.session_state["stage_4_format"] = result
                st.rerun()
    else:
        fm = st.session_state["stage_4_format"]
        fs = fm.get("format_scores", {})
        format_kr = {
            "feature_film": "장편 영화", "ott_series": "OTT 시리즈",
            "mini_series": "미니시리즈", "short_form": "숏폼 드라마", "web_novel": "웹소설"
        }
        
        for k, kr in format_kr.items():
            f = fs.get(k, {})
            score = f.get("score", 0)
            cls = "pass" if score >= 7 else "warn" if score >= 5 else "fail"
            st.markdown(f"""
            <div class="score-card {cls}">
                <span class="axis-name">{kr}</span>
                <span class="axis-score">{score}/10</span>
                <div class="axis-comment">{f.get('reason', '')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        primary = fm.get("primary_format_detail", {})
        st.markdown(f"### ▶ 1순위: **{primary.get('format_name', '')}**")
        
        ic = st.columns(3)
        with ic[0]:
            if primary.get("episode_count"):
                st.metric("회차", primary["episode_count"])
        with ic[1]:
            if primary.get("runtime_per_episode"):
                st.metric("회당 분량", primary["runtime_per_episode"])
        with ic[2]:
            if primary.get("total_runtime"):
                st.metric("전체 분량", primary["total_runtime"])
        
        st.markdown("**IP 빌딩 전략**")
        st.markdown(f'<div class="callout">{fm.get("ip_building_strategy", "")}</div>', unsafe_allow_html=True)
        
        if fm.get("unsuitable_formats"):
            st.markdown("**부적합 포맷**")
            for u in fm["unsuitable_formats"]:
                st.markdown(f"- **{u['format']}**: {u['reason']}")
        
        st.markdown("---")
        cb, cr, cn = st.columns([1, 1, 2])
        with cb:
            if st.button("← 이전"):
                st.session_state["current_stage"] = 3
                st.rerun()
        with cr:
            if st.button("재실행"):
                st.session_state["stage_4_format"] = None
                st.rerun()
        with cn:
            if st.button("Reference로 →", type="primary", use_container_width=True):
                st.session_state["current_stage"] = 5
                st.rerun()


def page_stage_5():
    section_header("🔍 STEP 5 · 레퍼런스 매핑", "SIMILAR 5 + DIFFERENTIATION")
    small_meta("유사작 5편 발굴 + 차별점 + 치명적 유사작 검증.")
    
    inp = st.session_state["stage_1_input"]
    logline = st.session_state.get("selected_logline", "")
    fm = st.session_state["stage_4_format"]
    primary_format = fm.get("primary_format_detail", {}).get("format_name", inp["format"])
    
    if not st.session_state.get("stage_5_reference"):
        if st.button("🔍 Reference 매핑 실행", type="primary", use_container_width=True):
            client = get_anthropic_client()
            with st.spinner("Sonnet이 유사작 5편 분석 중..."):
                prompt_text = P.REFERENCE_MAPPING_PROMPT.format(
                    title=inp["title"], logline=logline,
                    genre=inp["genre"], format=primary_format, raw_idea=inp["raw_idea"],
                )
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패")
                    return
                st.session_state["stage_5_reference"] = result
                st.rerun()
    else:
        rf = st.session_state["stage_5_reference"]
        for ref in rf.get("references", []):
            st.markdown(f"### 《{ref['title']}》")
            st.caption(f"{ref.get('year', '')} · {ref.get('country', '')} · {ref.get('format', '')} · 유사 차원: {ref.get('similarity_axis', '')}")
            st.markdown(f"**공통점**: {ref.get('common_points', '')}")
            st.markdown(f"**차별점**: {ref.get('differentiation', '')}")
            st.markdown("---")
        
        warn = rf.get("lethal_similarity_warning", {})
        if warn.get("exists"):
            st.error(f"⚠ **치명적 유사작 경고**\n\n{warn.get('details', '')}")
        else:
            st.success(f"✓ **치명적 유사작 없음** — {warn.get('details', '안전')}")
        
        st.markdown("**차별화 요약**")
        st.markdown(f'<div class="callout">{rf.get("differentiation_summary", "")}</div>', unsafe_allow_html=True)
        
        st.markdown("**투자자 미팅용 답변**")
        st.markdown(f'> {rf.get("investor_pitch_answer", "")}')
        
        st.markdown("---")
        cb, cr, cn = st.columns([1, 1, 2])
        with cb:
            if st.button("← 이전"):
                st.session_state["current_stage"] = 4
                st.rerun()
        with cr:
            if st.button("재실행"):
                st.session_state["stage_5_reference"] = None
                st.rerun()
        with cn:
            if st.button("Market 진단으로 →", type="primary", use_container_width=True):
                st.session_state["current_stage"] = 6
                st.rerun()


def page_stage_6():
    section_header("📊 STEP 6 · 시장성 진단", "3 MARKET STARS")
    small_meta("한국·글로벌·OTT 3개 시장을 동시에 별점 평가합니다.")
    
    inp = st.session_state["stage_1_input"]
    logline = st.session_state.get("selected_logline", "")
    fm = st.session_state["stage_4_format"]
    primary_format = fm.get("primary_format_detail", {}).get("format_name", inp["format"])
    
    if not st.session_state.get("stage_6_market"):
        if st.button("📊 Market 진단 실행", type="primary", use_container_width=True):
            client = get_anthropic_client()
            with st.spinner("Sonnet이 3개 시장 진단 중..."):
                prompt_text = P.MARKET_DIAGNOSTIC_PROMPT.format(
                    title=inp["title"], logline=logline,
                    genre=inp["genre"], primary_format=primary_format, raw_idea=inp["raw_idea"],
                )
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패")
                    return
                st.session_state["stage_6_market"] = result
                st.rerun()
    else:
        mk = st.session_state["stage_6_market"]
        
        c1, c2, c3 = st.columns(3)
        for col, key, label in [
            (c1, "domestic_market", "한국 시장"),
            (c2, "global_market", "글로벌 시장"),
            (c3, "ott_market", "OTT 시장"),
        ]:
            stars = mk.get(key, {}).get("stars", 0)
            with col:
                st.markdown(f"""
                <div class="metric-tile">
                    <div class="num">{'★' * stars}</div>
                    <div class="label">{label}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        dom = mk.get("domestic_market", {})
        with st.expander("🇰🇷 한국 시장 (Domestic)", expanded=True):
            ta = dom.get("target_audience", {})
            st.markdown(f"**타겟**: {ta.get('gender', '')} {ta.get('age_range', '')}")
            st.markdown(f"  └ {ta.get('psychographic', '')}")
            st.markdown(f"**예산**: {dom.get('budget_estimate', '')}")
            st.markdown(f"**유통**: {', '.join(dom.get('distribution', []))}")
            st.markdown(f"**IP 확장**: {', '.join(dom.get('ip_extension_potential', []))}")
        
        glb = mk.get("global_market", {})
        with st.expander("🌏 글로벌 시장 (International)", expanded=True):
            st.markdown(f"**1차 타겟**: {glb.get('primary_target_country', '')}")
            st.markdown(f"**어필 포인트**: {glb.get('global_appeal_strength', '')}")
            st.markdown(f"**진입 경로**: {', '.join(glb.get('entry_path', []))}")
            st.markdown(f"**약점**: {glb.get('weakness', '')}")
        
        ott = mk.get("ott_market", {})
        with st.expander("📺 OTT 시장 (Platform)", expanded=True):
            fc = ott.get("first_choice_platform", {})
            sc = ott.get("second_choice_platform", {})
            st.markdown(f"**1순위**: {fc.get('name', '')}")
            st.markdown(f"  └ {fc.get('reason', '')}")
            st.markdown(f"**2순위**: {sc.get('name', '')}")
            st.markdown(f"  └ {sc.get('reason', '')}")
            st.markdown(f"**최적 회차**: {ott.get('optimal_episode_count', '')}")
            st.markdown(f"**경쟁 분석**: {ott.get('competition_analysis', '')}")
        
        timing = mk.get("timing_fit", {})
        st.markdown(f"### 시기적 적합성: {'★' * timing.get('score', 0)}")
        st.markdown(f'<div class="callout">{timing.get("reason", "")}</div>', unsafe_allow_html=True)
        
        st.markdown("### ⚠ 위험 신호")
        for r in mk.get("risk_signals", []):
            st.markdown(f"- {r}")
        
        st.markdown("---")
        cb, cr, cn = st.columns([1, 1, 2])
        with cb:
            if st.button("← 이전"):
                st.session_state["current_stage"] = 5
                st.rerun()
        with cr:
            if st.button("재실행"):
                st.session_state["stage_6_market"] = None
                st.rerun()
        with cn:
            if st.button("최종 판정으로 → (Opus)", type="primary", use_container_width=True):
                st.session_state["current_stage"] = 7
                st.rerun()


def page_stage_7():
    section_header("⚖ STEP 7 · 최종 판정", "OPUS · GO / CONDITIONAL / NOGO")
    small_meta("Opus 4.7이 6개 진단 결과를 종합하여 최종 판정과 LOCKED 시드 패키지를 확정합니다.")

    inp = st.session_state["stage_1_input"]

    if not st.session_state.get("stage_7_verdict"):
        st.markdown("""
        <div class="callout">
        <b>Opus 4.7 최종 판정</b><br>
        모든 진단 데이터를 종합하여 GO/CONDITIONAL/NOGO 판정을 내리고, Creator Engine 입력용 LOCKED 시드 패키지를 확정합니다.<br>
        <span style="color:#191970;font-weight:600;">v1.1 — Creator Engine v2.5.2 정합:</span> 핵심 결정·음악 규약·시각 모티프·결말 형식·Creator 의제 5개 신규 LOCKED 영역도 함께 산출됩니다.<br>
        소요 시간: 60~90초
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("⚖ Opus 최종 판정 실행", type="primary", use_container_width=True):
            client = get_anthropic_client()
            with st.spinner("Opus가 종합 판정 중... (60~90초)"):
                prompt_text = P.FINAL_VERDICT_PROMPT.format(
                    title=inp["title"], raw_idea=inp["raw_idea"],
                    logline_data=json.dumps(st.session_state["stage_2_logline"], ensure_ascii=False, indent=2),
                    hook_data=json.dumps(st.session_state["stage_3_hook"], ensure_ascii=False, indent=2),
                    format_data=json.dumps(st.session_state["stage_4_format"], ensure_ascii=False, indent=2),
                    reference_data=json.dumps(st.session_state["stage_5_reference"], ensure_ascii=False, indent=2),
                    market_data=json.dumps(st.session_state["stage_6_market"], ensure_ascii=False, indent=2),
                )
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_OPUS)
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패")
                    with st.expander("Raw 응답"):
                        st.text(result.get("_raw", ""))
                    return
                st.session_state["stage_7_verdict"] = result
                st.rerun()
    else:
        vd = st.session_state["stage_7_verdict"]
        verdict = vd.get("final_verdict", "")
        
        if verdict == "GO":
            st.markdown("""
            <div class="verdict-box go">
                <p class="verdict-label" style="color:#2E7D32;">🟢 GO</p>
            </div>
            """, unsafe_allow_html=True)
        elif verdict == "CONDITIONAL":
            st.markdown("""
            <div class="verdict-box cond">
                <p class="verdict-label" style="color:#F9A825;">🟡 CONDITIONAL</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="verdict-box nogo">
                <p class="verdict-label" style="color:#C62828;">🔴 NOGO</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 판정 사유")
        st.markdown(f'<div class="callout">{vd.get("verdict_reasoning", "")}</div>', unsafe_allow_html=True)
        
        if vd.get("conditional_requirements"):
            st.markdown("### 충족 조건")
            for c in vd["conditional_requirements"]:
                st.markdown(f"- {c}")
        
        if vd.get("nogo_alternative"):
            st.markdown("### 대안 제시")
            st.warning(vd["nogo_alternative"])
        
        cd, cp = st.columns(2)
        with cd:
            st.markdown("**✓ 확정된 결정**")
            for k in vd.get("key_decisions_made", []):
                st.markdown(f"- {k}")
        with cp:
            st.markdown("**? Creator Engine에서 결정할 것**")
            for q in vd.get("pending_decisions_for_creator", []):
                st.markdown(f"- {q}")
        
        st.markdown("---")
        st.markdown("### 임원 요약 (Executive Summary)")
        st.success(vd.get("executive_summary", ""))
        
        st.markdown("---")
        section_header("🔑 LOCKED 시드 패키지", "LOCKED SEED PACKAGE")
        
        seed = vd.get("locked_seed_package", {})
        
        st.markdown(f"""
        <div class="locked-card">
            <div class="field-label">Project ID</div>
            <div class="field-value">{seed.get('project_id', '')}</div>
            <div class="field-label">Title (KR / EN)</div>
            <div class="field-value">{seed.get('title_kr', '')} / {seed.get('title_en', '')}</div>
            <div class="field-label">Locked Logline</div>
            <div class="field-value">{seed.get('locked_logline', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        cg, cf = st.columns(2)
        with cg:
            gn = seed.get("locked_genre", {})
            st.markdown("**Genre**")
            st.markdown(f"- Primary: {gn.get('primary', '')}")
            st.markdown(f"- Secondary: {gn.get('secondary', '')}")
            if gn.get("tertiary"):
                st.markdown(f"- Tertiary: {gn['tertiary']}")
        with cf:
            ft = seed.get("locked_format", {})
            st.markdown("**Format**")
            st.markdown(f"- Primary: {ft.get('primary', '')}")
            if ft.get("episode_count"):
                st.markdown(f"- Episodes: {ft['episode_count']}")
            if ft.get("runtime"):
                st.markdown(f"- Runtime: {ft['runtime']}")
        
        ct, cth = st.columns(2)
        with ct:
            tg = seed.get("locked_target", {})
            st.markdown("**Target**")
            st.markdown(f"- Domestic: {tg.get('domestic', '')}")
            st.markdown(f"- Global: {tg.get('global', '')}")
        with cth:
            th = seed.get("locked_theme", {})
            st.markdown("**Theme**")
            st.markdown(f"- Surface: {th.get('surface', '')}")
            st.markdown(f"- Deep: {th.get('deep', '')}")
        
        ms = seed.get("locked_market_stars", {})
        st.markdown("**Score Summary**")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Hook", f"{seed.get('locked_hook_score', 0)}/50")
        with c2:
            st.metric("한국", "★" * ms.get("domestic", 0))
        with c3:
            st.metric("글로벌", "★" * ms.get("global", 0))
        with c4:
            st.metric("OTT", "★" * ms.get("ott", 0))
        
        st.markdown("**Risks to Address (Creator Engine 진행 시 다룰 것)**")
        for r in seed.get("locked_risks_to_address", []):
            st.markdown(f"- {r}")

        # ═══════════════════════════════════════════════════════
        # v1.1 — Creator Engine v2.5.2 정합 5개 신규 LOCKED 영역
        # ═══════════════════════════════════════════════════════
        st.markdown("---")
        section_header(
            "🔒 v1.1 신규 LOCKED 영역",
            "CREATOR ENGINE v2.5.2 ABSORPTION KEYS"
        )
        st.caption(
            "Creator Engine v2.5.2가 작품 본질로 절대 보존하는 5개 영역. "
            "「오랜만에」 검증에서 발견된 핵심 모티프 휘발(61%)을 차단하기 위해 도입."
        )

        # ① locked_core_decisions
        core_decisions = seed.get("locked_core_decisions", []) or []
        with st.expander(
            f"① 확정된 핵심 결정 (locked_core_decisions) · {len(core_decisions)}건",
            expanded=bool(core_decisions),
        ):
            if not core_decisions:
                st.caption("이 작품에는 별도로 LOCK된 핵심 결정이 없습니다 (빈 배열).")
            else:
                for d in core_decisions:
                    if isinstance(d, dict):
                        cat = d.get("category", "")
                        rule = d.get("rule", "") or d.get("decision", "")
                        rationale = d.get("rationale", "")
                        if cat:
                            st.markdown(f"**[{cat}]** {rule}")
                        else:
                            st.markdown(f"- {rule}")
                        if rationale:
                            st.caption(f"근거: {rationale}")
                    elif isinstance(d, str):
                        st.markdown(f"- {d}")

        # ② locked_music_rules
        music_rules = seed.get("locked_music_rules", {}) or {}
        with st.expander(
            f"② 음악 사용 규약 (locked_music_rules) · {'있음' if music_rules else '없음'}",
            expanded=bool(music_rules),
        ):
            if not music_rules:
                st.caption("이 작품에는 음악 사용 규약이 없습니다 (빈 객체). 액션·스릴러·호러에서 자주 발생.")
            elif isinstance(music_rules, dict):
                for k, v in music_rules.items():
                    if isinstance(v, list):
                        st.markdown(f"**{k}**")
                        for item in v:
                            st.markdown(f"- {item}")
                    else:
                        st.markdown(f"**{k}**: {v}")
            elif isinstance(music_rules, list):
                for r in music_rules:
                    st.markdown(f"- {r}")
            else:
                st.markdown(str(music_rules))

        # ③ locked_visual_motifs
        visual_motifs = seed.get("locked_visual_motifs", []) or []
        with st.expander(
            f"③ 시각 모티프 (locked_visual_motifs) · {len(visual_motifs)}건",
            expanded=bool(visual_motifs),
        ):
            if not visual_motifs:
                st.caption("이 작품에는 LOCK된 시각 모티프가 없습니다 (빈 배열).")
            else:
                for m in visual_motifs:
                    if isinstance(m, dict):
                        motif = m.get("motif", "") or m.get("name", "")
                        function = m.get("function", "") or m.get("role", "")
                        if motif and function:
                            st.markdown(f"**{motif}** → {function}")
                        elif motif:
                            st.markdown(f"- {motif}")
                    elif isinstance(m, str):
                        st.markdown(f"- {m}")

        # ④ locked_ending_form
        ending_form = seed.get("locked_ending_form", {}) or {}
        with st.expander(
            f"④ 결말 형식 (locked_ending_form) · {'LOCK됨' if ending_form else '미확정'}",
            expanded=bool(ending_form),
        ):
            if not ending_form:
                st.caption("결말 형식이 LOCK되지 않았습니다 (빈 객체). Creator Engine이 결정.")
            elif isinstance(ending_form, dict):
                if ending_form.get("type"):
                    st.markdown(f"**결말 유형**: {ending_form['type']}")
                if ending_form.get("emotional_resolution"):
                    st.markdown(f"**정서적 해소**: {ending_form['emotional_resolution']}")
                if ending_form.get("final_image"):
                    st.markdown(f"**마지막 이미지**: {ending_form['final_image']}")
                if ending_form.get("forbidden"):
                    st.warning(f"**금지 패턴**: {ending_form['forbidden']}")
            else:
                st.markdown(str(ending_form))

        # ⑤ locked_creator_questions
        creator_questions = seed.get("locked_creator_questions", []) or []
        with st.expander(
            f"⑤ Creator Engine 결정 의제 (locked_creator_questions) · {len(creator_questions)}건",
            expanded=bool(creator_questions),
        ):
            if not creator_questions:
                st.caption("Creator Engine이 답할 의제가 없습니다 (빈 배열).")
            else:
                for q in creator_questions:
                    if isinstance(q, dict):
                        question = q.get("question", "")
                        options = q.get("options", []) or []
                        importance = q.get("importance", "")
                        line = f"**{question}**"
                        if importance:
                            badge_color = {
                                "high": "#C62828",
                                "medium": "#F9A825",
                                "low": "#2E7D32",
                            }.get(importance.lower(), "#666")
                            line += (
                                f" <span style='background:{badge_color};color:white;"
                                f"font-size:.7rem;padding:2px 6px;border-radius:4px;"
                                f"margin-left:6px;'>{importance.upper()}</span>"
                            )
                        st.markdown(line, unsafe_allow_html=True)
                        if options:
                            st.caption(f"후보: {' / '.join(str(o) for o in options)}")
                    elif isinstance(q, str):
                        st.markdown(f"- {q}")

        st.markdown("---")
        section_header("⬇ STEP 8 · 다운로드", "EXPORT")
        
        d1, d2 = st.columns(2)
        with d1:
            docx_bytes = build_diagnostic_docx(dict(st.session_state))
            st.download_button(
                label="📄 진단보고서 DOCX 다운로드",
                data=docx_bytes,
                file_name=f"IdeaDiagnostic_{inp['title']}_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with d2:
            json_str = build_seed_json(dict(st.session_state))
            st.download_button(
                label="🔑 LOCKED 시드 JSON 다운로드",
                data=json_str.encode("utf-8"),
                file_name=f"IdeaSeed_{seed.get('project_id', 'unknown')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
            )
        
        st.info("📌 **Creator Engine 사용법** — Creator Engine ① 화면 상단의 'Idea Engine JSON 업로드' 버튼을 눌러 위 JSON 파일을 업로드하면 ① 입력 필드가 자동으로 채워집니다.")
        
        with st.expander("JSON 미리보기"):
            st.code(json_str, language="json")
        
        st.markdown("---")
        cb, cr = st.columns([1, 1])
        with cb:
            if st.button("← 이전"):
                st.session_state["current_stage"] = 6
                st.rerun()
        with cr:
            if st.button("🔄 새 프로젝트 시작", use_container_width=True):
                reset_session()
                st.rerun()


# ═══════════════════════════════════════════════════════════
# v2.0 — HOME PAGE
# ═══════════════════════════════════════════════════════════
def page_home():
    """모드 선택 진입 화면. HUNTER vs TRIAGE 두 카드 제시."""
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="callout">'
        '<b>Idea Engine v2.0</b>은 두 개의 트랙으로 구성됩니다. '
        '머릿속에 아직 아이디어가 없다면 <b>HUNTER</b>로 발굴하시고, '
        '이미 아이디어가 있다면 <b>TRIAGE</b>로 진단하세요. '
        'HUNTER에서 발굴한 시드는 자동으로 TRIAGE Stage 1로 전달됩니다.'
        '</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("""
        <div style="border:2px solid #E2E2E0;border-radius:14px;padding:28px 26px;background:#fff;height:100%;">
            <div style="display:inline-block;background:#FFCB05;color:#191970;font-size:.72rem;font-weight:700;padding:4px 10px;border-radius:999px;letter-spacing:.05em;margin-bottom:12px;">HUNTER · 발굴</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:#191970;margin-bottom:6px;">아이디어가 아직 없을 때</div>
            <div style="color:#6B6B7A;font-size:.95rem;margin-bottom:18px;line-height:1.5;">5개의 입구 중 하나로 들어가 작가 안에 잠재된 답을 끌어냅니다.</div>
            <div style="color:#1A1A2E;font-size:.9rem;line-height:1.85;">
                <b>입구 1</b> — 욕망 ("로맨스 만들고 싶다")<br>
                <b>입구 2</b> — 시대 ("IMF 때 이야기")<br>
                <b>입구 3</b> — 트렌드 ("회빙환 해야 하나")<br>
                <b>입구 4</b> — What if ("로또+일주일 루프")<br>
                <b>입구 5</b> — 사실 ("1945.8.15. 일본인")<br>
                <b>입구 0</b> — 자유 텍스트 (자동 분류)
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("🎯 HUNTER 트랙 시작", key="home_to_hunter", type="primary", use_container_width=True):
            st.session_state["mode"] = "HUNTER"
            st.session_state["hunter_entry"] = None
            st.rerun()

    with col2:
        st.markdown("""
        <div style="border:2px solid #E2E2E0;border-radius:14px;padding:28px 26px;background:#fff;height:100%;">
            <div style="display:inline-block;background:#191970;color:#FFCB05;font-size:.72rem;font-weight:700;padding:4px 10px;border-radius:999px;letter-spacing:.05em;margin-bottom:12px;">TRIAGE · 진단</div>
            <div style="font-family:'Playfair Display',serif;font-size:1.8rem;font-weight:700;color:#191970;margin-bottom:6px;">이미 아이디어가 있을 때</div>
            <div style="color:#6B6B7A;font-size:.95rem;margin-bottom:18px;line-height:1.5;">7단계 진단으로 GO/CONDITIONAL/NOGO 판정 + LOCKED 시드 패키지 생성.</div>
            <div style="color:#1A1A2E;font-size:.9rem;line-height:1.85;">
                <b>1</b> 아이디어 입력<br>
                <b>2</b> 로그라인 정제<br>
                <b>3</b> Hook 진단 (Gate 0)<br>
                <b>4</b> Format 추천<br>
                <b>5</b> Reference 매핑<br>
                <b>6</b> Market 진단<br>
                <b>7</b> 최종 판정 (Opus 4.7)
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        if st.button("🔍 TRIAGE 트랙 시작", key="home_to_triage", use_container_width=True):
            st.session_state["mode"] = "TRIAGE"
            st.rerun()

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align:center;color:#8E8E99;font-size:.82rem;font-family:Pretendard,sans-serif;">'
        '"카탈로그를 보여주는 게 아니라 작가 안에 잠재된 답을 끌어내기"'
        '</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════
# v2.0 — HUNTER PAGES (골격 — 2~4단계에서 채움)
# ═══════════════════════════════════════════════════════════
def page_hunter_select():
    """입구 선택 화면. 입구 0 자유 텍스트 + 입구 1~5 카드."""
    section_header("🎯 HUNTER · 입구 선택", "CHOOSE YOUR ENTRY")
    small_meta(
        "5개 입구 중 하나로 들어가시거나, 입구 0에 자유롭게 입력하시면 자동 분류됩니다. "
        "각 입구는 작가의 영감 유형에 맞춘 사고 확장 엔진입니다."
    )

    st.info("🚧 **2단계 작업 예정** — 입구 0 자유 텍스트 입력 + 입구 1~5 선택 카드 UI를 다음 단계에서 구현합니다.")

    # 임시 디버그 (개발 중 모드 확인용)
    with st.expander("개발자: 현재 HUNTER 상태", expanded=False):
        st.json({
            "mode": st.session_state.get("mode"),
            "hunter_entry": st.session_state.get("hunter_entry"),
            "hunter_input": st.session_state.get("hunter_input"),
            "hunter_output": st.session_state.get("hunter_output"),
        })


def page_hunter_entry(entry_id: str):
    """입구별 페이지 (1~5). 3단계에서 prompt.py 추가 후 4단계에서 본격 구현."""
    entry_titles = {
        "1": ("욕망 트리거", "DESIRE PROMPT"),
        "2": ("시대 트리거", "PERIOD PROMPT"),
        "3": ("트렌드 협상", "TREND NEGOTIATION"),
        "4": ("What if 확장", "HYPOTHESIS EXPANSION"),
        "5": ("사실 발굴", "FACT EXCAVATION"),
    }
    kr, en = entry_titles.get(entry_id, ("입구", "ENTRY"))
    section_header(f"🎯 HUNTER · 입구 {entry_id} — {kr}", en)

    st.info(f"🚧 **4단계 작업 예정** — 입구 {entry_id}({kr}) 페이지 구현은 prompt.py 작성(3단계) 이후 진행됩니다.")

    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← 입구 선택으로", key=f"hunter_back_{entry_id}", use_container_width=True):
            st.session_state["hunter_entry"] = None
            st.rerun()


# ═══════════════════════════════════════════════════════════
# MAIN ROUTING (v2.0 — 3-way mode dispatch)
# ═══════════════════════════════════════════════════════════
mode = st.session_state.get("mode", "HOME")

if mode == "HOME":
    page_home()

elif mode == "HUNTER":
    entry = st.session_state.get("hunter_entry")
    if entry is None:
        page_hunter_select()
    else:
        page_hunter_entry(entry)

elif mode == "TRIAGE":
    # HUNTER에서 시드가 전달된 경우 안내 배너 노출
    if st.session_state.get("seed_loaded_from_hunter"):
        st.success(
            "🔗 HUNTER 트랙에서 발굴한 시드가 Stage 1에 자동 입력되었습니다. "
            "내용을 확인하시고 진단을 시작하세요."
        )

    render_stepper(st.session_state.get("current_stage", 1))

    stage = st.session_state.get("current_stage", 1)

    if stage == 1:
        page_stage_1()
    elif stage == 2:
        if not st.session_state.get("stage_1_input"):
            st.warning("Stage 1을 먼저 완료해주세요.")
        else:
            page_stage_2()
    elif stage == 3:
        if not st.session_state.get("stage_2_logline") or not st.session_state.get("selected_logline"):
            st.warning("Stage 2를 먼저 완료해주세요.")
        else:
            page_stage_3()
    elif stage == 4:
        if not st.session_state.get("stage_3_hook"):
            st.warning("Stage 3을 먼저 완료해주세요.")
        else:
            page_stage_4()
    elif stage == 5:
        if not st.session_state.get("stage_4_format"):
            st.warning("Stage 4를 먼저 완료해주세요.")
        else:
            page_stage_5()
    elif stage == 6:
        if not st.session_state.get("stage_5_reference"):
            st.warning("Stage 5를 먼저 완료해주세요.")
        else:
            page_stage_6()
    elif stage == 7:
        if not st.session_state.get("stage_6_market"):
            st.warning("Stage 6을 먼저 완료해주세요.")
        else:
            page_stage_7()

else:
    # 알 수 없는 모드 — 안전 fallback
    st.warning("알 수 없는 모드입니다. 홈으로 돌아갑니다.")
    st.session_state["mode"] = "HOME"
    st.rerun()

st.markdown("---")
st.caption(f"© 2026 BLUE JEANS PICTURES · Idea Engine {ENGINE_VERSION}")
