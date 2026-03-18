import streamlit as st
import tempfile
import os
from backend import run_matching

st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="⭐",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
    --bg: #f8f9fb;
    --surface: #ffffff;
    --border: #e4e8f0;
    --accent: #3354e8;
    --accent-lt: #eef1fd;
    --text-h: #111827;
    --text-b: #374151;
    --text-m: #6b7280;
    --text-s: #9ca3af;
    --pass: #16a34a;
    --pass-bg: #f0fdf4;
    --pass-bd: #bbf7d0;
    --fail: #dc2626;
    --fail-bg: #fff5f5;
    --fail-bd: #fecaca;
    --r: 10px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text-b);
    font-size: 14px;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1rem 3rem !important; max-width: 860px !important; margin: 0 auto !important; }

/* NAV */
.nav {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 2rem; padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.nav-brand {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1.3rem; color: var(--text-h);
    display: flex; align-items: center; gap: 0.4rem;
}
.nav-tag {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.08em;
    color: var(--accent); background: var(--accent-lt);
    border-radius: 20px; padding: 0.2rem 0.6rem;
}

/* PAGE TITLE */
.page-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1.65rem; color: var(--text-h);
    margin-bottom: 0.3rem;
}
.page-sub { font-size: 0.85rem; color: var(--text-m); margin-bottom: 1.6rem; font-weight: 300; }

/* UPLOAD ROW */
.upload-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 0.75rem; }
.upload-label {
    font-size: 0.75rem; font-weight: 600; color: var(--text-h);
    margin-bottom: 0.35rem; display: flex; align-items: center; gap: 0.3rem;
}
.step { font-size: 0.6rem; font-weight: 700; color: var(--accent);
    background: var(--accent-lt); border-radius: 4px; padding: 0.1rem 0.35rem; }
[data-testid="stFileUploadDropzone"] {
    background: var(--surface) !important;
    border: 1.5px dashed var(--border) !important;
    border-radius: var(--r) !important;
    min-height: 72px !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploadDropzone"]:hover { border-color: var(--accent) !important; }

.pill {
    display: inline-flex; align-items: center; gap: 0.3rem;
    background: var(--pass-bg); border: 1px solid var(--pass-bd);
    border-radius: 20px; padding: 0.2rem 0.65rem;
    font-size: 0.72rem; color: var(--pass); font-weight: 600; margin-top: 0.3rem;
}

/* BUTTON */
div.stButton > button {
    background: var(--accent) !important; color: #fff !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important; font-size: 0.9rem !important;
    border: none !important; border-radius: var(--r) !important;
    padding: 0.65rem 1.5rem !important; width: 100% !important;
    box-shadow: 0 4px 14px rgba(51,84,232,0.25) !important;
    transition: all 0.15s !important; cursor: pointer !important;
}
div.stButton > button:hover {
    background: #2241c4 !important;
    box-shadow: 0 6px 20px rgba(51,84,232,0.35) !important;
    transform: translateY(-1px) !important;
}

/* DIVIDER */
.divider { border: none; border-top: 1px solid var(--border); margin: 1.6rem 0; }

/* VERDICT ROW */
.verdict-row {
    display: flex; align-items: center; justify-content: space-between;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 1.2rem 1.5rem;
    margin-bottom: 1rem; box-shadow: 0 1px 8px rgba(0,0,0,0.05);
}
.verdict-left { display: flex; flex-direction: column; gap: 0.2rem; }
.verdict-label { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--text-s); }
.verdict-word {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 1.7rem; line-height: 1; letter-spacing: 0.04em;
}
.verdict-word.pass { color: var(--pass); }
.verdict-word.fail { color: var(--fail); }
.verdict-desc { font-size: 0.8rem; color: var(--text-m); max-width: 380px; line-height: 1.5; }

.score-chip {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; width: 72px; height: 72px; border-radius: 50%;
    flex-shrink: 0;
}
.score-chip.pass { background: var(--pass-bg); border: 2.5px solid var(--pass); }
.score-chip.fail { background: var(--fail-bg); border: 2.5px solid var(--fail); }
.score-n { font-family: 'Poppins', sans-serif; font-weight: 700; font-size: 1.55rem; line-height: 1; }
.score-n.pass { color: var(--pass); }
.score-n.fail { color: var(--fail); }
.score-d { font-size: 0.58rem; color: var(--text-s); font-weight: 600; }

/* BAR */
.bar-wrap { margin-top: 0.6rem; }
.bar-meta { display: flex; justify-content: space-between;
    font-size: 0.72rem; color: var(--text-m); margin-bottom: 0.3rem; }
.bar-track { height: 5px; background: var(--border); border-radius: 99px; overflow: hidden; }
.bar-fill-pass { height: 100%; background: linear-gradient(90deg,#4ade80,#16a34a); border-radius: 99px; }
.bar-fill-fail { height: 100%; background: linear-gradient(90deg,#fca5a5,#dc2626); border-radius: 99px; }

/* TWO COL */
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--r); padding: 1rem 1.2rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.card-title { font-size: 0.63rem; font-weight: 700; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--text-s);
    border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; margin-bottom: 0.75rem; }
.item { display: flex; align-items: flex-start; gap: 0.4rem;
    font-size: 0.83rem; color: var(--text-b); line-height: 1.5; margin-bottom: 0.45rem; }
.dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; margin-top: 0.5rem; }
.dot.p { background: var(--pass); }
.dot.f { background: var(--fail); }

/* SUMMARY */
.summary {
    background: var(--surface); border: 1px solid var(--border);
    border-left: 3px solid var(--accent); border-radius: var(--r);
    padding: 1rem 1.2rem; box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.summary-title { font-size: 0.63rem; font-weight: 700; letter-spacing: 0.16em;
    text-transform: uppercase; color: var(--accent); margin-bottom: 0.5rem; }
.summary-text { font-size: 0.83rem; color: var(--text-b); line-height: 1.6; font-weight: 400; }

/* EMPTY */
.empty { text-align: center; padding: 2rem 1rem; color: var(--text-s); }
.empty-icon { font-size: 2.2rem; opacity: 0.3; margin-bottom: 0.5rem; }
.empty-title { font-family: 'DM Serif Display', serif; font-size: 1rem; color: var(--text-m); }
.empty-sub { font-size: 0.8rem; margin-top: 0.3rem; }

[data-testid="stSpinner"] { color: var(--accent) !important; }
[data-testid="stAlert"] { border-radius: var(--r) !important; font-size: 0.84rem !important; }
</style>
""", unsafe_allow_html=True)

# ── NAV ──
st.markdown("""
<div class="nav">
    <div class="nav-brand">⭐ HR Screening Assistant</div>
    <span class="nav-tag">GenAI · Powered </span>
</div>
<div class="page-title">Resume Match Analyzer</div>
<div class="page-sub">Upload a job description and resume — get instant strengths, gaps & a hiring signal.</div>
""", unsafe_allow_html=True)

# ── UPLOAD ROW (two columns, side by side) ──
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown('<div class="upload-label"><span class="step">STEP 1</span> Job Description</div>', unsafe_allow_html=True)
    jd_file = st.file_uploader("jd", type=["pdf","docx"], key="jd", label_visibility="collapsed")
    if jd_file:
        st.markdown(f'<div class="pill">✓ {jd_file.name}</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="upload-label"><span class="step">STEP 2</span> Candidate Resume</div>', unsafe_allow_html=True)
    resume_file = st.file_uploader("resume", type=["pdf","docx"], key="resume", label_visibility="collapsed")
    if resume_file:
        st.markdown(f'<div class="pill">✓ {resume_file.name}</div>', unsafe_allow_html=True)

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
run_btn = st.button("🔍  Analyse Match", use_container_width=True)

if run_btn:
    if not jd_file:
        st.error("Please upload a Job Description.")
    elif not resume_file:
        st.error("Please upload a Resume.")

st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ── RESULTS ──
if not run_btn:
    st.markdown("""
    <div class="empty">
        <div class="empty-icon">📋</div>
        <div class="empty-title">Results will appear here</div>
        <div class="empty-sub">Upload both documents above and click Analyse Match.</div>
    </div>
    """, unsafe_allow_html=True)

elif not jd_file or not resume_file:
    st.markdown("""
    <div class="empty">
        <div class="empty-icon">⚠️</div>
        <div class="empty-title">Missing documents</div>
        <div class="empty-sub">Please upload both files before running the analysis.</div>
    </div>
    """, unsafe_allow_html=True)

else:
    with st.spinner("Analysing candidate fit — this may take up to 30 seconds..."):
        result = None
        jd_path = res_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{jd_file.name.rsplit('.',1)[-1]}") as f:
                f.write(jd_file.read()); jd_path = f.name
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.rsplit('.',1)[-1]}") as f:
                f.write(resume_file.read()); res_path = f.name
            result = run_matching(jd_path, res_path)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
        finally:
            for p in [jd_path, res_path]:
                if p:
                    try: os.unlink(p)
                    except: pass

    if result:
        decision   = str(result.get("decision","")).upper()
        score_raw  = result.get("match_score","0")
        strengths  = result.get("strengths") or result.get("top_strengths") or []
        gaps       = result.get("gaps") or result.get("key_gaps") or []
        summary    = result.get("summary") or result.get("final_summary") or ""

        try: score_int = int(str(score_raw).strip().rstrip("%"))
        except: score_int = 0

        is_pass = decision == "PASS"
        cls = "pass" if is_pass else "fail"
        verdict_desc = (
            "Candidate meets role requirements — recommended for the next stage."
            if is_pass else
            "Candidate does not meet the minimum requirements for this role."
        )

        # VERDICT ROW
        st.markdown(f"""
        <div class="verdict-row">
            <div class="verdict-left">
                <span class="verdict-label">Recruitment Decision</span>
                <span class="verdict-word {cls}">{"PASS" if is_pass else "FAIL"}</span>
                <span class="verdict-desc">{verdict_desc}</span>
                <div class="bar-wrap">
                    <div class="bar-meta"><span>Match Score</span><span>{score_raw} / 100</span></div>
                    <div class="bar-track">
                        <div class="bar-fill-{cls}" style="width:{score_int}%"></div>
                    </div>
                </div>
            </div>
            <div class="score-chip {cls}">
                <div class="score-n {cls}">{score_raw}</div>
                <div class="score-d">/ 100</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # STRENGTHS & GAPS
        s_html = "".join(f'<div class="item"><div class="dot p"></div><span>{s}</span></div>' for s in strengths) \
                 or '<div class="item"><div class="dot p"></div><span>None identified</span></div>'
        g_html = "".join(f'<div class="item"><div class="dot f"></div><span>{g}</span></div>' for g in gaps) \
                 or '<div class="item"><div class="dot f"></div><span>None identified</span></div>'

        st.markdown(f"""
        <div class="two-col">
            <div class="card">
                <div class="card-title">💪 Strengths</div>{s_html}
            </div>
            <div class="card">
                <div class="card-title">🔍 Gaps &amp; Missing Skills</div>{g_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # SUMMARY
        st.markdown(f"""
        <div class="summary">
            <div class="summary-title">📋 Analyst Summary</div>
            <div class="summary-text">{summary or "No summary returned by the model."}</div>
        </div>
        """, unsafe_allow_html=True)