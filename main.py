"""
Idea Engine v1.0
BLUE JEANS PICTURES · Creative Triage Engine

Creator Engine 입구의 진단·판정 엔진.
모호한 아이디어 → Hook 진단 → Format 추천 → Reference 매핑 →
Market 진단 → 최종 GO/NoGo 판정 → LOCKED 시드 패키지 출력
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
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import prompt as P

# ============================================================================
# CONFIG
# ============================================================================

ANTHROPIC_MODEL_SONNET = "claude-sonnet-4-6"
ANTHROPIC_MODEL_OPUS = "claude-opus-4-7"
MAX_TOKENS = 16000

st.set_page_config(
    page_title="Idea Engine · BLUE JEANS",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================================
# DESIGN SYSTEM (Creator Engine과 동일)
# ============================================================================

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

:root {
    --navy: #191970;
    --yellow: #FFCB05;
    --bg: #F7F7F5;
    --bg2: #EEEEF6;
    --text: #1A1A2E;
    --muted: #6B6B7B;
    --border: #D8D8E0;
    --display: 'Playfair Display', serif;
    --heading: 'Noto Sans KR', sans-serif;
    --body: 'Noto Sans KR', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--body);
    color: var(--text);
}

h1, h2, h3 {
    font-family: var(--heading);
    font-weight: 700;
    letter-spacing: -0.01em;
}

.brand-header {
    border-bottom: 3px solid var(--navy);
    padding-bottom: 1rem;
    margin-bottom: 2rem;
}
.brand-title {
    font-family: var(--display);
    font-size: 2.4rem;
    font-weight: 900;
    color: var(--navy);
    margin: 0;
    letter-spacing: -0.02em;
}
.brand-subtitle {
    font-family: var(--heading);
    font-size: 0.95rem;
    color: var(--muted);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-top: 0.3rem;
}

.section-header {
    background: var(--yellow);
    padding: 0.8rem 1.2rem;
    margin: 1.5rem 0 1rem 0;
    border-left: 6px solid var(--navy);
    font-family: var(--heading);
    font-weight: 700;
    color: var(--navy);
    font-size: 1.1rem;
    letter-spacing: 0.02em;
}
.section-header .en {
    font-family: var(--display);
    font-style: italic;
    font-weight: 400;
    color: var(--text);
    margin-left: 0.6rem;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
}

.score-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.score-pass {
    border-left: 6px solid #2E7D32;
}
.score-cond {
    border-left: 6px solid #F9A825;
}
.score-fail {
    border-left: 6px solid #C62828;
}

.verdict-box {
    padding: 2rem;
    border-radius: 12px;
    margin: 1.5rem 0;
    text-align: center;
    font-family: var(--display);
}
.verdict-go {
    background: linear-gradient(135deg, #E8F5E9, #C8E6C9);
    border: 3px solid #2E7D32;
}
.verdict-cond {
    background: linear-gradient(135deg, #FFF8E1, #FFECB3);
    border: 3px solid #F9A825;
}
.verdict-nogo {
    background: linear-gradient(135deg, #FFEBEE, #FFCDD2);
    border: 3px solid #C62828;
}
.verdict-label {
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: 0.1em;
    margin: 0;
}

.metric-tile {
    background: white;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
.metric-tile .num {
    font-family: var(--display);
    font-size: 2.2rem;
    font-weight: 900;
    color: var(--navy);
    line-height: 1;
}
.metric-tile .label {
    font-size: 0.85rem;
    color: var(--muted);
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.locked-card {
    background: var(--navy);
    color: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 6px solid var(--yellow);
}
.locked-card .field-label {
    color: var(--yellow);
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.locked-card .field-value {
    font-size: 1rem;
    margin-bottom: 1rem;
}

.stButton > button {
    background: var(--navy);
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.6rem 1.5rem;
    font-family: var(--heading);
    font-weight: 600;
    transition: all 0.15s ease;
}
.stButton > button:hover {
    background: var(--yellow);
    color: var(--navy);
    transform: translateY(-1px);
}

.footer {
    margin-top: 4rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--muted);
    font-size: 0.85rem;
    font-family: var(--display);
    letter-spacing: 0.05em;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ============================================================================
# UTILITIES
# ============================================================================

def section_header(kr: str, en: str):
    st.markdown(
        f'<div class="section-header">{kr}<span class="en">{en}</span></div>',
        unsafe_allow_html=True,
    )


def get_anthropic_client() -> Optional[Anthropic]:
    api_key = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY", None)
    if not api_key:
        return None
    return Anthropic(api_key=api_key)


def safe_json_loads(text: str) -> Dict[str, Any]:
    """4단계 JSON 복구 시스템 (Creator Engine 방식)"""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # 1차: 그대로
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2차: 첫 { 부터 마지막 } 까지
    try:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        pass

    # 3차: 에러 위치 반복 수정
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

    # 4차: 강제 치환
    try:
        cleaned = re.sub(r'(?<="):\s*"([^"]*)"\s*([,\}])',
                         lambda m: f': "{m.group(1).replace(chr(34), chr(39))}" {m.group(2)}',
                         text)
        return json.loads(cleaned)
    except Exception:
        return {"_parse_error": True, "_raw": text}


def call_claude(client: Anthropic, prompt_text: str, model: str = ANTHROPIC_MODEL_SONNET) -> Dict[str, Any]:
    """Claude API 호출. 모델은 Sonnet (진단) 또는 Opus (최종 판정)"""
    response = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt_text}],
    )
    raw = response.content[0].text
    return safe_json_loads(raw)


def init_session_state():
    defaults = {
        "current_stage": 1,
        "stage_1_input": None,
        "stage_2_logline": None,
        "stage_3_hook": None,
        "stage_4_format": None,
        "stage_5_reference": None,
        "stage_6_market": None,
        "stage_7_verdict": None,
        "selected_logline": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_session():
    keys_to_clear = [
        "current_stage", "stage_1_input", "stage_2_logline",
        "stage_3_hook", "stage_4_format", "stage_5_reference",
        "stage_6_market", "stage_7_verdict", "selected_logline"
    ]
    for k in keys_to_clear:
        if k in st.session_state:
            del st.session_state[k]
    init_session_state()


# ============================================================================
# DOCX EXPORT
# ============================================================================

def add_section_header_to_docx(doc, kr: str, en: str):
    """노란 하이라이트 + 한글/영문 병기 헤더"""
    p = doc.add_paragraph()
    run_kr = p.add_run(kr + " ")
    run_kr.font.size = Pt(14)
    run_kr.font.bold = True
    run_kr.font.color.rgb = RGBColor(0x19, 0x19, 0x70)

    run_en = p.add_run(en)
    run_en.font.size = Pt(11)
    run_en.font.italic = True
    run_en.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)

    # 노란 하이라이트
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'FFCB05')
    pPr.append(shd)


def add_paragraph(doc, text: str, bold: bool = False, italic: bool = False, size: int = 11):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic


def build_diagnostic_docx(state: Dict[str, Any]) -> bytes:
    """진단 보고서 DOCX 생성"""
    doc = Document()
    
    # 페이지 여백
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # 커버
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_p.add_run("IDEA DIAGNOSTIC REPORT")
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("아이디어 진단 보고서")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)
    
    doc.add_paragraph()
    
    inp = state["stage_1_input"]
    title_main = doc.add_paragraph()
    title_main.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title_main.add_run(inp["title"])
    run.font.size = Pt(20)
    run.font.bold = True
    
    info_p = doc.add_paragraph()
    info_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = info_p.add_run(f"{inp['genre']} · {inp['format']} · {inp['target_market']}")
    run.font.size = Pt(11)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)

    doc.add_paragraph()
    doc.add_paragraph()
    
    today_p = doc.add_paragraph()
    today_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = today_p.add_run(f"발행일: {datetime.now().strftime('%Y년 %m월 %d일')}")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)
    
    bjp_p = doc.add_paragraph()
    bjp_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = bjp_p.add_run("BLUE JEANS PICTURES · Idea Engine v1.0")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x19, 0x19, 0x70)
    run.font.bold = True

    doc.add_page_break()

    # 1. 원본 아이디어
    add_section_header_to_docx(doc, "1. 원본 아이디어", "ORIGINAL IDEA")
    add_paragraph(doc, inp["raw_idea"])
    doc.add_paragraph()

    # 2. 로그라인 정제
    if state["stage_2_logline"]:
        add_section_header_to_docx(doc, "2. 로그라인 정제", "LOGLINE REFINEMENT")
        ll = state["stage_2_logline"]
        for v in ll.get("logline_variants", []):
            add_paragraph(doc, f"[{v['variant']}안 - {v['label']}]", bold=True)
            add_paragraph(doc, v["logline"])
            add_paragraph(doc, f"  강점: {v['strength']}", italic=True, size=10)
            add_paragraph(doc, f"  약점: {v['weakness']}", italic=True, size=10)
            doc.add_paragraph()
        add_paragraph(doc, f"▶ 추천: {ll.get('recommended', '')}안", bold=True)
        add_paragraph(doc, ll.get("recommendation_reason", ""))
        doc.add_paragraph()

    # 3. Hook 진단
    if state["stage_3_hook"]:
        add_section_header_to_docx(doc, "3. 후크 진단 (Gate 0)", "HOOK DIAGNOSTIC")
        hk = state["stage_3_hook"]
        scores = hk.get("scores", {})
        
        score_table = doc.add_table(rows=6, cols=3)
        score_table.style = "Light Grid Accent 1"
        hdr = score_table.rows[0].cells
        hdr[0].text = "축"
        hdr[1].text = "점수"
        hdr[2].text = "코멘트"
        
        axis_kr = {
            "specificity": "구체성",
            "conflict_visibility": "갈등 가시성",
            "genre_clarity": "장르 명확성",
            "stakes": "판돈",
            "originality": "독창성"
        }
        for i, (k, kr) in enumerate(axis_kr.items(), 1):
            sc = scores.get(k, {})
            row = score_table.rows[i].cells
            row[0].text = kr
            row[1].text = f"{sc.get('score', 0)}/10"
            row[2].text = sc.get("comment", "")
        
        doc.add_paragraph()
        add_paragraph(doc, f"총점: {hk.get('total_score', 0)}/50 — {hk.get('gate_status', '')}", bold=True, size=13)
        doc.add_paragraph()
        
        add_paragraph(doc, "강점", bold=True)
        for s in hk.get("key_strengths", []):
            add_paragraph(doc, f"  • {s}")
        doc.add_paragraph()
        
        add_paragraph(doc, "약점", bold=True)
        for w in hk.get("key_weaknesses", []):
            add_paragraph(doc, f"  • {w}")
        doc.add_paragraph()
        
        add_paragraph(doc, "보강 제안", bold=True)
        for s in hk.get("improvement_suggestions", []):
            add_paragraph(doc, f"  • {s}")
        doc.add_paragraph()

    # 4. Format 추천
    if state["stage_4_format"]:
        add_section_header_to_docx(doc, "4. 포맷 추천", "FORMAT RECOMMENDATION")
        fm = state["stage_4_format"]
        fs = fm.get("format_scores", {})
        
        fmt_table = doc.add_table(rows=6, cols=3)
        fmt_table.style = "Light Grid Accent 1"
        hdr = fmt_table.rows[0].cells
        hdr[0].text = "포맷"
        hdr[1].text = "점수"
        hdr[2].text = "근거"
        
        format_kr = {
            "feature_film": "장편 영화",
            "ott_series": "OTT 시리즈",
            "mini_series": "미니시리즈",
            "short_form": "숏폼 드라마",
            "web_novel": "웹소설"
        }
        for i, (k, kr) in enumerate(format_kr.items(), 1):
            f = fs.get(k, {})
            row = fmt_table.rows[i].cells
            row[0].text = kr
            row[1].text = f"{f.get('score', 0)}/10"
            row[2].text = f.get("reason", "")
        
        doc.add_paragraph()
        primary = fm.get("primary_format_detail", {})
        add_paragraph(doc, f"▶ 1순위: {primary.get('format_name', '')}", bold=True, size=13)
        if primary.get("episode_count"):
            add_paragraph(doc, f"  회차: {primary['episode_count']}")
        if primary.get("runtime_per_episode"):
            add_paragraph(doc, f"  회당 분량: {primary['runtime_per_episode']}")
        doc.add_paragraph()
        
        add_paragraph(doc, "IP 빌딩 전략", bold=True)
        add_paragraph(doc, fm.get("ip_building_strategy", ""))
        doc.add_paragraph()

    # 5. Reference 매핑
    if state["stage_5_reference"]:
        add_section_header_to_docx(doc, "5. 레퍼런스 매핑", "REFERENCE MAPPING")
        rf = state["stage_5_reference"]
        
        for ref in rf.get("references", []):
            add_paragraph(doc, f"《{ref['title']}》 ({ref.get('year', '')}, {ref.get('country', '')}) - {ref.get('format', '')}", bold=True)
            add_paragraph(doc, f"  유사 차원: {ref.get('similarity_axis', '')}", italic=True, size=10)
            add_paragraph(doc, f"  공통점: {ref.get('common_points', '')}")
            add_paragraph(doc, f"  차별점: {ref.get('differentiation', '')}")
            doc.add_paragraph()
        
        warn = rf.get("lethal_similarity_warning", {})
        if warn.get("exists"):
            add_paragraph(doc, "⚠ 치명적 유사작 경고", bold=True)
            add_paragraph(doc, warn.get("details", ""))
        else:
            add_paragraph(doc, "✓ 치명적 유사작 없음 - 안전", bold=True)
        doc.add_paragraph()
        
        add_paragraph(doc, "차별화 요약", bold=True)
        add_paragraph(doc, rf.get("differentiation_summary", ""))
        doc.add_paragraph()
        
        add_paragraph(doc, "투자자 미팅 답변용", bold=True)
        add_paragraph(doc, rf.get("investor_pitch_answer", ""))
        doc.add_paragraph()

    # 6. Market 진단
    if state["stage_6_market"]:
        add_section_header_to_docx(doc, "6. 시장성 진단", "MARKET DIAGNOSTIC")
        mk = state["stage_6_market"]
        
        # 한국
        dom = mk.get("domestic_market", {})
        add_paragraph(doc, f"한국 시장 ({'★' * dom.get('stars', 0)})", bold=True, size=13)
        ta = dom.get("target_audience", {})
        add_paragraph(doc, f"  타겟: {ta.get('gender', '')} {ta.get('age_range', '')} - {ta.get('psychographic', '')}")
        add_paragraph(doc, f"  예산: {dom.get('budget_estimate', '')}")
        add_paragraph(doc, f"  유통: {', '.join(dom.get('distribution', []))}")
        add_paragraph(doc, f"  IP 확장: {', '.join(dom.get('ip_extension_potential', []))}")
        doc.add_paragraph()
        
        # 글로벌
        glb = mk.get("global_market", {})
        add_paragraph(doc, f"글로벌 시장 ({'★' * glb.get('stars', 0)})", bold=True, size=13)
        add_paragraph(doc, f"  1차 타겟: {glb.get('primary_target_country', '')}")
        add_paragraph(doc, f"  어필: {glb.get('global_appeal_strength', '')}")
        add_paragraph(doc, f"  진입경로: {', '.join(glb.get('entry_path', []))}")
        add_paragraph(doc, f"  약점: {glb.get('weakness', '')}")
        doc.add_paragraph()
        
        # OTT
        ott = mk.get("ott_market", {})
        add_paragraph(doc, f"OTT 시장 ({'★' * ott.get('stars', 0)})", bold=True, size=13)
        fc = ott.get("first_choice_platform", {})
        sc = ott.get("second_choice_platform", {})
        add_paragraph(doc, f"  1순위: {fc.get('name', '')} - {fc.get('reason', '')}")
        add_paragraph(doc, f"  2순위: {sc.get('name', '')} - {sc.get('reason', '')}")
        add_paragraph(doc, f"  최적 회차: {ott.get('optimal_episode_count', '')}")
        add_paragraph(doc, f"  경쟁: {ott.get('competition_analysis', '')}")
        doc.add_paragraph()
        
        # 시기적 적합성
        timing = mk.get("timing_fit", {})
        add_paragraph(doc, f"시기적 적합성 ({'★' * timing.get('score', 0)})", bold=True)
        add_paragraph(doc, timing.get("reason", ""))
        doc.add_paragraph()
        
        # 위험 신호
        add_paragraph(doc, "위험 신호", bold=True)
        for r in mk.get("risk_signals", []):
            add_paragraph(doc, f"  • {r}")
        doc.add_paragraph()

    # 7. 최종 판정
    if state["stage_7_verdict"]:
        add_section_header_to_docx(doc, "7. 최종 판정", "FINAL VERDICT")
        vd = state["stage_7_verdict"]
        
        verdict = vd.get("final_verdict", "")
        verdict_p = doc.add_paragraph()
        verdict_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = verdict_p.add_run(f"  {verdict}  ")
        run.font.size = Pt(28)
        run.font.bold = True
        if verdict == "GO":
            run.font.color.rgb = RGBColor(0x2E, 0x7D, 0x32)
        elif verdict == "CONDITIONAL":
            run.font.color.rgb = RGBColor(0xF9, 0xA8, 0x25)
        else:
            run.font.color.rgb = RGBColor(0xC6, 0x28, 0x28)
        doc.add_paragraph()
        
        add_paragraph(doc, "판정 사유", bold=True)
        add_paragraph(doc, vd.get("verdict_reasoning", ""))
        doc.add_paragraph()
        
        if vd.get("conditional_requirements"):
            add_paragraph(doc, "충족 조건 (CONDITIONAL)", bold=True)
            for c in vd["conditional_requirements"]:
                add_paragraph(doc, f"  • {c}")
            doc.add_paragraph()
        
        if vd.get("nogo_alternative"):
            add_paragraph(doc, "대안 제시 (NOGO)", bold=True)
            add_paragraph(doc, vd["nogo_alternative"])
            doc.add_paragraph()
        
        add_paragraph(doc, "확정된 핵심 결정", bold=True)
        for k in vd.get("key_decisions_made", []):
            add_paragraph(doc, f"  • {k}")
        doc.add_paragraph()
        
        add_paragraph(doc, "Creator Engine에서 결정해야 할 질문", bold=True)
        for q in vd.get("pending_decisions_for_creator", []):
            add_paragraph(doc, f"  • {q}")
        doc.add_paragraph()
        
        # Executive Summary
        add_section_header_to_docx(doc, "임원 요약", "EXECUTIVE SUMMARY")
        add_paragraph(doc, vd.get("executive_summary", ""))
        doc.add_paragraph()
        
        # LOCKED 시드 패키지
        add_section_header_to_docx(doc, "LOCKED 시드 패키지", "LOCKED SEED PACKAGE")
        add_paragraph(doc, "Creator Engine 입력용 데이터 ─ 이 항목들은 Creator Engine에서 변경하지 않는다.", italic=True, size=10)
        doc.add_paragraph()
        
        seed = vd.get("locked_seed_package", {})
        
        add_paragraph(doc, f"Project ID: {seed.get('project_id', '')}", bold=True, size=11)
        add_paragraph(doc, f"제목 (KR): {seed.get('title_kr', '')}")
        add_paragraph(doc, f"제목 (EN): {seed.get('title_en', '')}")
        doc.add_paragraph()
        
        add_paragraph(doc, "LOCKED LOGLINE", bold=True)
        add_paragraph(doc, seed.get("locked_logline", ""))
        doc.add_paragraph()
        
        add_paragraph(doc, "LOCKED GENRE", bold=True)
        gn = seed.get("locked_genre", {})
        add_paragraph(doc, f"  Primary: {gn.get('primary', '')}")
        add_paragraph(doc, f"  Secondary: {gn.get('secondary', '')}")
        if gn.get("tertiary"):
            add_paragraph(doc, f"  Tertiary: {gn['tertiary']}")
        doc.add_paragraph()
        
        add_paragraph(doc, "LOCKED FORMAT", bold=True)
        ft = seed.get("locked_format", {})
        add_paragraph(doc, f"  Primary: {ft.get('primary', '')}")
        if ft.get("episode_count"):
            add_paragraph(doc, f"  Episodes: {ft['episode_count']}")
        if ft.get("runtime"):
            add_paragraph(doc, f"  Runtime: {ft['runtime']}")
        add_paragraph(doc, f"  IP Strategy: {ft.get('ip_strategy', '')}")
        doc.add_paragraph()
        
        add_paragraph(doc, "LOCKED TARGET", bold=True)
        tg = seed.get("locked_target", {})
        add_paragraph(doc, f"  Domestic: {tg.get('domestic', '')}")
        add_paragraph(doc, f"  Global: {tg.get('global', '')}")
        doc.add_paragraph()
        
        add_paragraph(doc, "LOCKED THEME", bold=True)
        th = seed.get("locked_theme", {})
        add_paragraph(doc, f"  Surface: {th.get('surface', '')}")
        add_paragraph(doc, f"  Deep: {th.get('deep', '')}")
        doc.add_paragraph()
        
        add_paragraph(doc, "LOCKED REFERENCES", bold=True)
        for r in seed.get("locked_references", []):
            add_paragraph(doc, f"  • {r}")
        doc.add_paragraph()
        
        add_paragraph(doc, f"Hook Score: {seed.get('locked_hook_score', '')}/50", bold=True)
        ms = seed.get("locked_market_stars", {})
        add_paragraph(doc, f"Market Stars: 한국 {'★' * ms.get('domestic', 0)} / 글로벌 {'★' * ms.get('global', 0)} / OTT {'★' * ms.get('ott', 0)}")
        add_paragraph(doc, f"Distribution Priority: {seed.get('locked_distribution_priority', '')}")
        doc.add_paragraph()
        
        add_paragraph(doc, "Creator Engine 진행 시 다뤄야 할 위험", bold=True)
        for risk in seed.get("locked_risks_to_address", []):
            add_paragraph(doc, f"  • {risk}")

    # Footer
    doc.add_paragraph()
    doc.add_paragraph()
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("© 2026 BLUE JEANS PICTURES · Idea Engine v1.0")
    run.font.size = Pt(9)
    run.font.italic = True
    run.font.color.rgb = RGBColor(0x6B, 0x6B, 0x7B)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def build_seed_json(state: Dict[str, Any]) -> str:
    """Creator Engine 입력용 JSON 시드 패키지"""
    if not state.get("stage_7_verdict"):
        return "{}"
    
    seed = state["stage_7_verdict"].get("locked_seed_package", {})
    
    # Creator Engine ① 화면 형식과 매칭
    creator_input = {
        "_idea_engine_meta": {
            "version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "project_id": seed.get("project_id", ""),
            "verdict": state["stage_7_verdict"].get("final_verdict", ""),
            "hook_score": seed.get("locked_hook_score", 0),
        },
        # Creator Engine ① 입력 자동 채움용
        "title": seed.get("title_kr", ""),
        "raw_idea": seed.get("locked_logline", ""),
        "genre": seed.get("locked_genre", {}).get("primary", ""),
        "target_market": seed.get("locked_target", {}).get("domestic", ""),
        "format": seed.get("locked_format", {}).get("primary", ""),
        # 추가 LOCKED 데이터 (Creator Engine이 참조)
        "locked_seed": seed,
        "executive_summary": state["stage_7_verdict"].get("executive_summary", ""),
        "pending_decisions": state["stage_7_verdict"].get("pending_decisions_for_creator", []),
    }
    
    return json.dumps(creator_input, ensure_ascii=False, indent=2)


# ============================================================================
# UI: STAGE PAGES
# ============================================================================

def page_stage_1_input():
    """Stage 1 - 아이디어 입력"""
    section_header("① 아이디어 입력", "INPUT")
    
    st.markdown("""
    모호한 아이디어 한 줄부터 한 단락까지 자유롭게 입력하세요.
    Idea Engine이 이를 정제하여 Creator Engine이 받아먹을 수 있는 LOCKED 시드 패키지로 변환합니다.
    """)
    
    with st.form("stage_1_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            title = st.text_input("제목 (가제)", placeholder="예: 만물트럭 탐정")
        with col2:
            genre = st.selectbox(
                "장르 (선택)",
                ["미지정", "스릴러", "코지 미스터리", "드라마", "로맨스", "코미디",
                 "액션", "호러", "SF", "판타지", "범죄", "느와르", "사회파", "직접 입력"]
            )
            if genre == "직접 입력":
                genre = st.text_input("장르 직접 입력")
        
        col3, col4 = st.columns(2)
        with col3:
            target_market = st.selectbox(
                "타겟 시장",
                ["한국 + 글로벌", "한국 (국내)", "글로벌 (해외)", "일본", "동남아", "직접 입력"]
            )
            if target_market == "직접 입력":
                target_market = st.text_input("타겟 시장 직접 입력")
        with col4:
            format_pref = st.selectbox(
                "선호 포맷 (선택)",
                ["미정 (Idea Engine이 추천)", "장편 영화", "OTT 시리즈", "미니시리즈",
                 "숏폼 드라마", "웹소설", "웹툰"]
            )
        
        raw_idea = st.text_area(
            "원본 아이디어",
            height=200,
            placeholder=(
                "예시:\n"
                "만물트럭(한국) - 이동편의점(일본) 결합\n"
                "만물트럭 탐정 — 셜록홈즈 탐정물\n"
                "고령화된 마을을 돌아다니며 사건 해결\n"
                "추리소설 광이었던 주인공이 깨어나보니 만물트럭 운전사가 되어있었다\n"
                "1. 사라진 시체 / 2. 독극물 살인사건 / 3. 아무도 죽이지 않았다"
            ),
        )
        
        submitted = st.form_submit_button("진단 시작 →")
        
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


def page_stage_2_logline():
    """Stage 2 - 로그라인 정제 (Sonnet)"""
    section_header("② 로그라인 정제", "LOGLINE REFINEMENT")
    
    inp = st.session_state["stage_1_input"]
    
    if not st.session_state.get("stage_2_logline"):
        if st.button("🪄 로그라인 정제 실행", type="primary"):
            client = get_anthropic_client()
            if not client:
                st.error("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
                return
            
            with st.spinner("Sonnet이 로그라인 3개 변형을 작성 중..."):
                prompt_text = P.LOGLINE_REFINE_PROMPT.format(**inp)
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패. 다시 시도해주세요.")
                    with st.expander("Raw 응답 보기"):
                        st.text(result.get("_raw", ""))
                    return
                
                st.session_state["stage_2_logline"] = result
                st.rerun()
    else:
        ll = st.session_state["stage_2_logline"]
        
        for v in ll.get("logline_variants", []):
            with st.container():
                st.markdown(f"**[{v['variant']}안 — {v['label']}]**")
                st.markdown(f"> {v['logline']}")
                col_s, col_w = st.columns(2)
                with col_s:
                    st.caption(f"✓ 강점: {v['strength']}")
                with col_w:
                    st.caption(f"✗ 약점: {v['weakness']}")
                st.divider()
        
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
        
        col_back, col_next = st.columns([1, 3])
        with col_back:
            if st.button("← 다시 생성"):
                st.session_state["stage_2_logline"] = None
                st.rerun()
        with col_next:
            if st.button("Hook 진단으로 →", type="primary"):
                st.session_state["current_stage"] = 3
                st.rerun()


def page_stage_3_hook():
    """Stage 3 - Hook 진단 (Sonnet) - Gate 0"""
    section_header("③ 후크 진단", "HOOK DIAGNOSTIC · GATE 0")
    
    inp = st.session_state["stage_1_input"]
    logline = st.session_state.get("selected_logline", "")
    
    if not st.session_state.get("stage_3_hook"):
        if st.button("🎯 Hook 진단 실행", type="primary"):
            client = get_anthropic_client()
            if not client:
                st.error("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
                return
            
            with st.spinner("Sonnet이 5축 진단 중..."):
                prompt_text = P.HOOK_DIAGNOSTIC_PROMPT.format(
                    title=inp["title"],
                    logline=logline,
                    genre=inp["genre"],
                    format=inp["format"],
                    raw_idea=inp["raw_idea"],
                )
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패. 다시 시도해주세요.")
                    return
                
                st.session_state["stage_3_hook"] = result
                st.rerun()
    else:
        hk = st.session_state["stage_3_hook"]
        
        # 점수 시각화
        scores = hk.get("scores", {})
        axis_kr = {
            "specificity": "구체성",
            "conflict_visibility": "갈등 가시성",
            "genre_clarity": "장르 명확성",
            "stakes": "판돈",
            "originality": "독창성"
        }
        
        # 레이더 차트
        categories = list(axis_kr.values())
        values = [scores.get(k, {}).get("score", 0) for k in axis_kr.keys()]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Hook Score',
            line=dict(color='#191970', width=2),
            fillcolor='rgba(255, 203, 5, 0.4)'
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], tickfont=dict(size=10)),
                angularaxis=dict(tickfont=dict(size=12, family='Noto Sans KR'))
            ),
            showlegend=False,
            height=400,
            margin=dict(l=80, r=80, t=40, b=40)
        )
        
        col_chart, col_summary = st.columns([1, 1])
        with col_chart:
            st.plotly_chart(fig, use_container_width=True)
        with col_summary:
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
        
        # 5축 상세
        st.markdown("**축별 진단**")
        for k, kr in axis_kr.items():
            sc = scores.get(k, {})
            score = sc.get("score", 0)
            color = "#2E7D32" if score >= 7 else "#F9A825" if score >= 5 else "#C62828"
            st.markdown(f"""
            <div class="score-card" style="border-left: 6px solid {color};">
                <strong>{kr}</strong> &nbsp;<span style="font-size:1.3rem; color:{color};">{score}/10</span><br>
                <span style="color: var(--muted); font-size: 0.95rem;">{sc.get('comment', '')}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("**핵심 강점**")
            for s in hk.get("key_strengths", []):
                st.markdown(f"- {s}")
        with col_w:
            st.markdown("**핵심 약점**")
            for w in hk.get("key_weaknesses", []):
                st.markdown(f"- {w}")
        
        st.markdown("**보강 제안**")
        for s in hk.get("improvement_suggestions", []):
            st.markdown(f"- {s}")
        
        st.markdown("---")
        col_back, col_redo, col_next = st.columns([1, 1, 2])
        with col_back:
            if st.button("← 로그라인"):
                st.session_state["current_stage"] = 2
                st.rerun()
        with col_redo:
            if st.button("재실행"):
                st.session_state["stage_3_hook"] = None
                st.rerun()
        with col_next:
            if status == "FAIL":
                st.error("🔴 FAIL — Override 시 진행 가능")
                if st.button("⚠ Override하고 Format 추천으로 →"):
                    st.session_state["current_stage"] = 4
                    st.rerun()
            else:
                if st.button("Format 추천으로 →", type="primary"):
                    st.session_state["current_stage"] = 4
                    st.rerun()


def page_stage_4_format():
    """Stage 4 - Format 추천 (Sonnet)"""
    section_header("④ 포맷 추천", "FORMAT RECOMMENDATION")
    
    inp = st.session_state["stage_1_input"]
    logline = st.session_state.get("selected_logline", "")
    
    if not st.session_state.get("stage_4_format"):
        if st.button("📐 포맷 추천 실행", type="primary"):
            client = get_anthropic_client()
            with st.spinner("Sonnet이 5개 포맷 적합도 판정 중..."):
                prompt_text = P.FORMAT_RECOMMEND_PROMPT.format(
                    title=inp["title"],
                    logline=logline,
                    genre=inp["genre"],
                    raw_idea=inp["raw_idea"],
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
            "feature_film": "장편 영화",
            "ott_series": "OTT 시리즈",
            "mini_series": "미니시리즈",
            "short_form": "숏폼 드라마",
            "web_novel": "웹소설"
        }
        
        # 포맷별 점수 바
        for k, kr in format_kr.items():
            f = fs.get(k, {})
            score = f.get("score", 0)
            color = "#2E7D32" if score >= 7 else "#F9A825" if score >= 5 else "#C62828"
            st.markdown(f"""
            <div class="score-card" style="border-left: 6px solid {color};">
                <strong>{kr}</strong> &nbsp;<span style="font-size:1.3rem; color:{color};">{score}/10</span><br>
                <span style="color: var(--muted); font-size: 0.95rem;">{f.get('reason', '')}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        primary = fm.get("primary_format_detail", {})
        st.markdown(f"### ▶ 1순위: **{primary.get('format_name', '')}**")
        
        info_cols = st.columns(3)
        with info_cols[0]:
            if primary.get("episode_count"):
                st.metric("회차", primary["episode_count"])
        with info_cols[1]:
            if primary.get("runtime_per_episode"):
                st.metric("회당 분량", primary["runtime_per_episode"])
        with info_cols[2]:
            if primary.get("total_runtime"):
                st.metric("전체 분량", primary["total_runtime"])
        
        st.markdown("**IP 빌딩 전략**")
        st.info(fm.get("ip_building_strategy", ""))
        
        if fm.get("unsuitable_formats"):
            st.markdown("**부적합 포맷**")
            for u in fm["unsuitable_formats"]:
                st.markdown(f"- **{u['format']}**: {u['reason']}")
        
        st.markdown("---")
        col_back, col_redo, col_next = st.columns([1, 1, 2])
        with col_back:
            if st.button("← Hook"):
                st.session_state["current_stage"] = 3
                st.rerun()
        with col_redo:
            if st.button("재실행"):
                st.session_state["stage_4_format"] = None
                st.rerun()
        with col_next:
            if st.button("Reference 매핑으로 →", type="primary"):
                st.session_state["current_stage"] = 5
                st.rerun()


def page_stage_5_reference():
    """Stage 5 - Reference 매핑 (Sonnet)"""
    section_header("⑤ 레퍼런스 매핑", "REFERENCE MAPPING")
    
    inp = st.session_state["stage_1_input"]
    logline = st.session_state.get("selected_logline", "")
    fm = st.session_state["stage_4_format"]
    primary_format = fm.get("primary_format_detail", {}).get("format_name", inp["format"])
    
    if not st.session_state.get("stage_5_reference"):
        if st.button("🔍 Reference 매핑 실행", type="primary"):
            client = get_anthropic_client()
            with st.spinner("Sonnet이 유사작 5편 + 차별점 분석 중..."):
                prompt_text = P.REFERENCE_MAPPING_PROMPT.format(
                    title=inp["title"],
                    logline=logline,
                    genre=inp["genre"],
                    format=primary_format,
                    raw_idea=inp["raw_idea"],
                )
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패")
                    return
                st.session_state["stage_5_reference"] = result
                st.rerun()
    else:
        rf = st.session_state["stage_5_reference"]
        
        # 유사작 5편
        for ref in rf.get("references", []):
            with st.container():
                st.markdown(f"### 《{ref['title']}》")
                st.caption(f"{ref.get('year', '')} · {ref.get('country', '')} · {ref.get('format', '')} · 유사 차원: {ref.get('similarity_axis', '')}")
                st.markdown(f"**공통점**: {ref.get('common_points', '')}")
                st.markdown(f"**차별점**: {ref.get('differentiation', '')}")
                st.divider()
        
        # 치명적 유사작 경고
        warn = rf.get("lethal_similarity_warning", {})
        if warn.get("exists"):
            st.error(f"⚠ **치명적 유사작 경고**\n\n{warn.get('details', '')}")
        else:
            st.success(f"✓ **치명적 유사작 없음** — {warn.get('details', '안전')}")
        
        st.markdown("**차별화 요약**")
        st.info(rf.get("differentiation_summary", ""))
        
        st.markdown("**투자자 미팅용 답변**")
        st.markdown(f'> {rf.get("investor_pitch_answer", "")}')
        
        st.markdown("---")
        col_back, col_redo, col_next = st.columns([1, 1, 2])
        with col_back:
            if st.button("← Format"):
                st.session_state["current_stage"] = 4
                st.rerun()
        with col_redo:
            if st.button("재실행"):
                st.session_state["stage_5_reference"] = None
                st.rerun()
        with col_next:
            if st.button("Market 진단으로 →", type="primary"):
                st.session_state["current_stage"] = 6
                st.rerun()


def page_stage_6_market():
    """Stage 6 - Market 진단 (Sonnet)"""
    section_header("⑥ 시장성 진단", "MARKET DIAGNOSTIC")
    
    inp = st.session_state["stage_1_input"]
    logline = st.session_state.get("selected_logline", "")
    fm = st.session_state["stage_4_format"]
    primary_format = fm.get("primary_format_detail", {}).get("format_name", inp["format"])
    
    if not st.session_state.get("stage_6_market"):
        if st.button("📊 Market 진단 실행", type="primary"):
            client = get_anthropic_client()
            with st.spinner("Sonnet이 한국·글로벌·OTT 3개 시장 진단 중..."):
                prompt_text = P.MARKET_DIAGNOSTIC_PROMPT.format(
                    title=inp["title"],
                    logline=logline,
                    genre=inp["genre"],
                    primary_format=primary_format,
                    raw_idea=inp["raw_idea"],
                )
                result = call_claude(client, prompt_text, ANTHROPIC_MODEL_SONNET)
                if result.get("_parse_error"):
                    st.error("응답 파싱 실패")
                    return
                st.session_state["stage_6_market"] = result
                st.rerun()
    else:
        mk = st.session_state["stage_6_market"]
        
        # 3개 시장 별점 요약
        col1, col2, col3 = st.columns(3)
        with col1:
            stars = mk.get("domestic_market", {}).get("stars", 0)
            st.markdown(f"""
            <div class="metric-tile">
                <div class="num">{'★' * stars}</div>
                <div class="label">한국 시장</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            stars = mk.get("global_market", {}).get("stars", 0)
            st.markdown(f"""
            <div class="metric-tile">
                <div class="num">{'★' * stars}</div>
                <div class="label">글로벌 시장</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            stars = mk.get("ott_market", {}).get("stars", 0)
            st.markdown(f"""
            <div class="metric-tile">
                <div class="num">{'★' * stars}</div>
                <div class="label">OTT 시장</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # 한국 시장
        dom = mk.get("domestic_market", {})
        with st.expander("🇰🇷 한국 시장 (Domestic)", expanded=True):
            ta = dom.get("target_audience", {})
            st.markdown(f"**타겟**: {ta.get('gender', '')} {ta.get('age_range', '')}")
            st.markdown(f"  └ {ta.get('psychographic', '')}")
            st.markdown(f"**예산**: {dom.get('budget_estimate', '')}")
            st.markdown(f"**유통**: {', '.join(dom.get('distribution', []))}")
            st.markdown(f"**IP 확장**: {', '.join(dom.get('ip_extension_potential', []))}")
        
        # 글로벌 시장
        glb = mk.get("global_market", {})
        with st.expander("🌏 글로벌 시장 (International)", expanded=True):
            st.markdown(f"**1차 타겟**: {glb.get('primary_target_country', '')}")
            st.markdown(f"**어필 포인트**: {glb.get('global_appeal_strength', '')}")
            st.markdown(f"**진입 경로**: {', '.join(glb.get('entry_path', []))}")
            st.markdown(f"**약점**: {glb.get('weakness', '')}")
        
        # OTT 시장
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
        
        # 시기적 적합성 + 위험
        timing = mk.get("timing_fit", {})
        st.markdown(f"### 시기적 적합성: {'★' * timing.get('score', 0)}")
        st.info(timing.get("reason", ""))
        
        st.markdown("### ⚠ 위험 신호")
        for r in mk.get("risk_signals", []):
            st.markdown(f"- {r}")
        
        st.markdown("---")
        col_back, col_redo, col_next = st.columns([1, 1, 2])
        with col_back:
            if st.button("← Reference"):
                st.session_state["current_stage"] = 5
                st.rerun()
        with col_redo:
            if st.button("재실행"):
                st.session_state["stage_6_market"] = None
                st.rerun()
        with col_next:
            if st.button("최종 판정으로 → (Opus)", type="primary"):
                st.session_state["current_stage"] = 7
                st.rerun()


def page_stage_7_verdict():
    """Stage 7 - 최종 판정 (Opus)"""
    section_header("⑦ 최종 판정", "FINAL VERDICT · OPUS")
    
    inp = st.session_state["stage_1_input"]
    
    if not st.session_state.get("stage_7_verdict"):
        st.markdown("""
        모든 진단 데이터를 종합하여, **Opus 4.7**이 최종 GO/CONDITIONAL/NOGO 판정을 내리고
        Creator Engine 입력용 LOCKED 시드 패키지를 확정합니다.
        """)
        
        if st.button("⚖ Opus 최종 판정 실행", type="primary"):
            client = get_anthropic_client()
            with st.spinner("Opus가 6개 진단을 종합하여 최종 판정 중... (60~90초 소요)"):
                prompt_text = P.FINAL_VERDICT_PROMPT.format(
                    title=inp["title"],
                    raw_idea=inp["raw_idea"],
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
        
        # 판정 박스
        verdict = vd.get("final_verdict", "")
        if verdict == "GO":
            st.markdown(f"""
            <div class="verdict-box verdict-go">
                <p class="verdict-label" style="color: #2E7D32;">🟢 GO</p>
            </div>
            """, unsafe_allow_html=True)
        elif verdict == "CONDITIONAL":
            st.markdown(f"""
            <div class="verdict-box verdict-cond">
                <p class="verdict-label" style="color: #F9A825;">🟡 CONDITIONAL</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="verdict-box verdict-nogo">
                <p class="verdict-label" style="color: #C62828;">🔴 NOGO</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("### 판정 사유")
        st.info(vd.get("verdict_reasoning", ""))
        
        # 조건부 / NOGO 처리
        if vd.get("conditional_requirements"):
            st.markdown("### 충족 조건 (Conditional Requirements)")
            for c in vd["conditional_requirements"]:
                st.markdown(f"- {c}")
        
        if vd.get("nogo_alternative"):
            st.markdown("### 대안 제시")
            st.warning(vd["nogo_alternative"])
        
        # 확정된 결정 + 펜딩
        col_d, col_p = st.columns(2)
        with col_d:
            st.markdown("**✓ 확정된 결정**")
            for k in vd.get("key_decisions_made", []):
                st.markdown(f"- {k}")
        with col_p:
            st.markdown("**? Creator Engine에서 결정할 것**")
            for q in vd.get("pending_decisions_for_creator", []):
                st.markdown(f"- {q}")
        
        st.markdown("---")
        st.markdown("### 임원 요약 (Executive Summary)")
        st.success(vd.get("executive_summary", ""))
        
        # LOCKED 시드 패키지
        st.markdown("---")
        section_header("LOCKED 시드 패키지", "LOCKED SEED PACKAGE")
        
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
        
        col_g, col_f = st.columns(2)
        with col_g:
            gn = seed.get("locked_genre", {})
            st.markdown("**Genre**")
            st.markdown(f"- Primary: {gn.get('primary', '')}")
            st.markdown(f"- Secondary: {gn.get('secondary', '')}")
            if gn.get("tertiary"):
                st.markdown(f"- Tertiary: {gn['tertiary']}")
        with col_f:
            ft = seed.get("locked_format", {})
            st.markdown("**Format**")
            st.markdown(f"- Primary: {ft.get('primary', '')}")
            if ft.get("episode_count"):
                st.markdown(f"- Episodes: {ft['episode_count']}")
            if ft.get("runtime"):
                st.markdown(f"- Runtime: {ft['runtime']}")
        
        col_t, col_th = st.columns(2)
        with col_t:
            tg = seed.get("locked_target", {})
            st.markdown("**Target**")
            st.markdown(f"- Domestic: {tg.get('domestic', '')}")
            st.markdown(f"- Global: {tg.get('global', '')}")
        with col_th:
            th = seed.get("locked_theme", {})
            st.markdown("**Theme**")
            st.markdown(f"- Surface: {th.get('surface', '')}")
            st.markdown(f"- Deep: {th.get('deep', '')}")
        
        ms = seed.get("locked_market_stars", {})
        st.markdown("**Score Summary**")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Hook", f"{seed.get('locked_hook_score', 0)}/50")
        with col_s2:
            st.metric("한국", "★" * ms.get("domestic", 0))
        with col_s3:
            st.metric("글로벌", "★" * ms.get("global", 0))
        with col_s4:
            st.metric("OTT", "★" * ms.get("ott", 0))
        
        st.markdown("**Risks to Address (Creator Engine 진행 시 다룰 것)**")
        for r in seed.get("locked_risks_to_address", []):
            st.markdown(f"- {r}")
        
        st.markdown("---")
        section_header("⑧ 다운로드", "EXPORT")
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            docx_bytes = build_diagnostic_docx(dict(st.session_state))
            st.download_button(
                label="📄 진단보고서 DOCX 다운로드",
                data=docx_bytes,
                file_name=f"IdeaDiagnostic_{inp['title']}_{datetime.now().strftime('%Y%m%d')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with col_dl2:
            json_str = build_seed_json(dict(st.session_state))
            st.download_button(
                label="🔑 LOCKED 시드 JSON 다운로드",
                data=json_str.encode("utf-8"),
                file_name=f"IdeaSeed_{seed.get('project_id', 'unknown')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True,
            )
        
        st.info("📌 **Creator Engine 사용법**\n\nCreator Engine ① 화면 상단의 **'Idea Engine JSON 업로드'** 버튼을 눌러 위 JSON 파일을 업로드하면, ① 입력 필드가 자동으로 채워집니다.")
        
        with st.expander("JSON 미리보기"):
            st.code(json_str, language="json")
        
        st.markdown("---")
        col_back, col_reset = st.columns([1, 1])
        with col_back:
            if st.button("← Market 진단"):
                st.session_state["current_stage"] = 6
                st.rerun()
        with col_reset:
            if st.button("🔄 새 프로젝트 시작"):
                reset_session()
                st.rerun()


# ============================================================================
# MAIN
# ============================================================================

def main():
    init_session_state()
    
    # 헤더
    st.markdown("""
    <div class="brand-header">
        <h1 class="brand-title">Idea Engine</h1>
        <div class="brand-subtitle">BLUE JEANS PICTURES · CREATIVE TRIAGE ENGINE · v1.0</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바 - 파이프라인 진행 상태
    with st.sidebar:
        st.markdown("### 파이프라인 진행 상태")
        
        stages = [
            ("①", "아이디어 입력", 1, st.session_state.get("stage_1_input")),
            ("②", "로그라인 정제", 2, st.session_state.get("stage_2_logline")),
            ("③", "Hook 진단", 3, st.session_state.get("stage_3_hook")),
            ("④", "Format 추천", 4, st.session_state.get("stage_4_format")),
            ("⑤", "Reference 매핑", 5, st.session_state.get("stage_5_reference")),
            ("⑥", "Market 진단", 6, st.session_state.get("stage_6_market")),
            ("⑦", "최종 판정", 7, st.session_state.get("stage_7_verdict")),
        ]
        
        current = st.session_state.get("current_stage", 1)
        for num, name, idx, completed in stages:
            if completed:
                marker = "✅"
            elif idx == current:
                marker = "▶"
            else:
                marker = "○"
            
            if completed and st.button(f"{marker} {num} {name}", key=f"nav_{idx}", use_container_width=True):
                st.session_state["current_stage"] = idx
                st.rerun()
            else:
                st.markdown(f"{marker} {num} {name}")
        
        st.markdown("---")
        st.markdown("### 모델 정책")
        st.caption("진단 (②~⑥): **Sonnet 4.6**")
        st.caption("최종 판정 (⑦): **Opus 4.7**")
        
        st.markdown("---")
        if st.button("🔄 전체 초기화", use_container_width=True):
            reset_session()
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <div class="footer">
        © 2026 BLUE JEANS PICTURES<br>
        Idea Engine v1.0
        </div>
        """, unsafe_allow_html=True)
    
    # 메인 페이지 라우팅
    stage = st.session_state.get("current_stage", 1)
    
    if stage == 1:
        page_stage_1_input()
    elif stage == 2:
        if not st.session_state.get("stage_1_input"):
            st.warning("Stage 1을 먼저 완료해주세요.")
            if st.button("← Stage 1로"):
                st.session_state["current_stage"] = 1
                st.rerun()
        else:
            page_stage_2_logline()
    elif stage == 3:
        if not st.session_state.get("stage_2_logline") or not st.session_state.get("selected_logline"):
            st.warning("Stage 2를 먼저 완료해주세요.")
        else:
            page_stage_3_hook()
    elif stage == 4:
        if not st.session_state.get("stage_3_hook"):
            st.warning("Stage 3을 먼저 완료해주세요.")
        else:
            page_stage_4_format()
    elif stage == 5:
        if not st.session_state.get("stage_4_format"):
            st.warning("Stage 4을 먼저 완료해주세요.")
        else:
            page_stage_5_reference()
    elif stage == 6:
        if not st.session_state.get("stage_5_reference"):
            st.warning("Stage 5을 먼저 완료해주세요.")
        else:
            page_stage_6_market()
    elif stage == 7:
        if not st.session_state.get("stage_6_market"):
            st.warning("Stage 6을 먼저 완료해주세요.")
        else:
            page_stage_7_verdict()


if __name__ == "__main__":
    main()
