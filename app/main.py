"""
app/main.py
Entry point — EMCA Sistema de Pilotes.
Premium dark UI inspired by modern SaaS dashboards.
"""
import streamlit as st
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

st.set_page_config(
    page_title="EMCA — Planificación de Pilotes",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design Tokens ──────────────────────────────────────────────
bg      = "#0B0B0F"
bg2     = "#111118"
card    = "#161625"
card_h  = "#1E1E32"
tx1     = "#E2E8F0"
tx2     = "#8892B0"
tx3     = "#4A5568"
brd     = "rgba(255,255,255,0.06)"
shd     = "rgba(0,0,0,0.45)"
acc     = "#00E68A"
acc2    = "#00CC7A"
blue    = "#4D7CFE"
yellow  = "#FFD43B"
red     = "#FF6B6B"
purple  = "#A855F7"
cyan    = "#22D3EE"

css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ═══ Base ═══ */
html, body, [class*="css"] {{ font-family:'Inter',sans-serif; }}
.stApp {{ background:{bg}!important; }}
[data-testid="stHeader"] {{ background:transparent!important; }}

/* ═══ Sidebar ═══ */
[data-testid="stSidebar"] {{
    background:{bg2}!important;
    border-right:1px solid {brd};
}}
[data-testid="stSidebarNav"] {{ padding-top:.5rem; }}
[data-testid="stSidebarNav"] a {{
    border-radius:10px; margin:2px 8px; padding:6px 12px;
    transition:all .2s ease;
}}
[data-testid="stSidebarNav"] a:hover {{ background:rgba(0,230,138,.08); }}
[data-testid="stSidebarNav"] a[aria-selected="true"] {{
    background:rgba(0,230,138,.12)!important;
    border-left:3px solid {acc};
}}

/* ═══ Metric Cards ═══ */
div[data-testid="metric-container"] {{
    background:{card};
    border:1px solid {brd};
    border-radius:16px;
    padding:1.25rem 1.5rem;
    box-shadow:0 4px 20px {shd};
    transition:transform .25s ease,box-shadow .25s ease;
    position:relative;
    overflow:hidden;
}}
div[data-testid="metric-container"]::before {{
    content:'';position:absolute;top:0;left:0;width:4px;height:100%;
    background:linear-gradient(180deg,{acc},{cyan});border-radius:4px 0 0 4px;
}}
div[data-testid="metric-container"]:hover {{
    transform:translateY(-3px);
    box-shadow:0 8px 30px {shd},0 0 20px rgba(0,230,138,.06);
}}
div[data-testid="metric-container"] label {{
    color:{tx2}!important;font-size:.78rem!important;
    text-transform:uppercase;letter-spacing:.8px;font-weight:600!important;
}}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-size:1.8rem!important;font-weight:800!important;color:{tx1}!important;
}}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-size:.8rem!important;font-weight:600!important;
}}

/* ═══ Buttons ═══ */
.stButton > button {{
    background:linear-gradient(135deg,{acc},{acc2})!important;
    color:#0B0B0F!important; border:none!important;
    border-radius:12px; font-weight:700; font-size:.9rem;
    letter-spacing:.3px; padding:.6rem 1.5rem;
    transition:all .25s cubic-bezier(.4,0,.2,1);
    box-shadow:0 4px 15px rgba(0,230,138,.25);
}}
.stButton > button:hover {{
    transform:translateY(-2px)!important;
    box-shadow:0 8px 25px rgba(0,230,138,.35)!important;
    filter:brightness(1.1);
}}
.stButton > button[kind="secondary"],
.stButton > button[data-testid="stBaseButton-secondary"] {{
    background:{card}!important; color:{tx1}!important;
    border:1px solid {brd}!important;
    box-shadow:0 2px 8px {shd}!important;
}}
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="stBaseButton-secondary"]:hover {{
    background:{card_h}!important;
    border-color:rgba(0,230,138,.3)!important;
}}

/* ═══ Tabs ═══ */
.stTabs [data-baseweb="tab-list"] {{
    background:{card}; border-radius:14px; padding:4px; gap:4px;
    border:1px solid {brd};
}}
.stTabs [data-baseweb="tab"] {{
    border-radius:10px; padding:10px 22px;
    background:transparent; color:{tx2}!important;
    font-weight:500; transition:all .2s ease;
}}
.stTabs [aria-selected="true"] {{
    background:rgba(0,230,138,.12)!important;
    color:{acc}!important; font-weight:700;
    box-shadow:0 2px 8px rgba(0,230,138,.1);
    border-bottom:none!important;
}}

/* ═══ Typography ═══ */
h1,h2,h3,h4,h5,h6 {{ color:{tx1}!important; }}
p,span,div,label,li {{ color:{tx1}; }}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {{ color:{tx1}!important; }}
[data-testid="stCaption"] {{ color:{tx2}!important; }}

/* ═══ Forms & Inputs ═══ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {{
    background:{card}!important; color:{tx1}!important;
    border:1px solid {brd}!important; border-radius:10px!important;
    transition:border-color .2s ease;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {{
    border-color:{acc}!important;
    box-shadow:0 0 0 2px rgba(0,230,138,.15)!important;
}}
.stSlider > div > div > div > div {{ background:{acc}!important; }}
.stCheckbox > label > div {{ background:{card}!important; border-color:{brd}!important; }}
.stRadio > label > div {{ background:{card}!important; border-color:{brd}!important; }}
[data-baseweb="select"] > div {{
    background:{card}!important; color:{tx1}!important;
    border-color:{brd}!important; border-radius:10px!important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
    background:{card}!important; border:1px solid {brd}!important;
}}

/* ═══ Tables & DataFrames ═══ */
[data-testid="stDataFrame"] {{
    background:{card}; border-radius:14px; border:1px solid {brd};
    overflow:hidden;
}}
.stExpander {{
    background:{card}!important; border:1px solid {brd}!important;
    border-radius:14px!important;
}}
.stExpander > div {{ color:{tx1}!important; }}

/* ═══ Alerts ═══ */
[data-testid="stAlert"] {{
    background:{card}!important; color:{tx1}!important;
    border:1px solid {brd}!important; border-radius:12px!important;
}}

/* ═══ Plotly ═══ */
.stPlotlyChart {{ background:transparent!important; }}

/* ═══ Scrollbar ═══ */
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:{bg}; }}
::-webkit-scrollbar-thumb {{ background:{tx3}; border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:{tx2}; }}

/* ══════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════════════════════ */

/* ─── Nav Cards ─── */
.nav-card {{
    background:{card}; border:1px solid {brd}; border-radius:18px;
    padding:1.8rem; margin:.5rem 0; height:100%;
    transition:all .3s cubic-bezier(.4,0,.2,1);
    box-shadow:0 4px 20px {shd}; cursor:pointer;
    position:relative; overflow:hidden;
}}
.nav-card::after {{
    content:'';position:absolute;bottom:0;left:50%;
    width:0;height:3px;background:{acc};
    transition:all .3s ease;transform:translateX(-50%);
}}
.nav-card:hover {{
    transform:translateY(-5px);
    box-shadow:0 12px 35px {shd},0 0 25px rgba(0,230,138,.08);
    border-color:rgba(0,230,138,.2);
}}
.nav-card:hover::after {{ width:60%; }}
.nav-card h3 {{ color:{tx1}; margin-top:0; font-weight:700; font-size:1.1rem; }}
.nav-card h4 {{
    color:{acc}; font-size:.8rem; font-weight:700;
    margin-bottom:.8rem; text-transform:uppercase; letter-spacing:1px;
}}
.nav-card p {{ color:{tx2}; line-height:1.6; font-size:.88rem; }}

/* ─── Stepper ─── */
.stepper {{
    display:flex; align-items:center; justify-content:center;
    padding:.8rem 1.5rem; margin-bottom:1.5rem;
    background:{card}; border-radius:14px;
    border:1px solid {brd}; box-shadow:0 4px 15px {shd};
}}
.stepper-step {{
    display:flex; align-items:center; gap:.4rem;
    padding:.5rem 1rem; border-radius:999px;
    font-weight:600; font-size:.82rem; color:{tx3};
    transition:all .2s ease;
}}
.stepper-step.active {{ background:{acc}; color:#0B0B0F; }}
.stepper-step.completed {{ color:{acc}; }}
.stepper-arrow {{ color:{tx3}; margin:0 .4rem; font-size:1.1rem; }}

/* ─── Flow Diagram ─── */
.flow-diagram {{
    display:flex; align-items:center; justify-content:center;
    gap:1rem; padding:1.5rem; margin:1rem 0;
}}
.flow-node {{
    background:{card}; border:1px solid {brd}; border-radius:14px;
    padding:1.2rem 1.8rem; text-align:center;
    font-weight:600; color:{tx1}; box-shadow:0 2px 10px {shd};
    transition:all .2s ease;
}}
.flow-node:hover {{ border-color:rgba(0,230,138,.25); transform:translateY(-2px); }}
.flow-arrow {{ font-size:1.5rem; color:{acc}; }}

/* ─── Preview Cards ─── */
.preview-card {{
    background:{card}; border:1px solid {brd}; border-radius:16px;
    padding:1.5rem; margin:1rem 0; box-shadow:0 4px 15px {shd};
}}
.preview-card h4 {{
    color:{acc}; margin:0 0 1rem; font-size:.82rem;
    text-transform:uppercase; letter-spacing:1px; font-weight:700;
}}
.preview-row {{
    display:flex; justify-content:space-between;
    padding:.55rem 0; border-bottom:1px solid {brd}; font-size:.9rem;
}}
.preview-row:last-child {{ border-bottom:none; }}
.preview-label {{ color:{tx2}; }}
.preview-value {{ color:{tx1}; font-weight:700; }}

/* ─── Alerts ─── */
.alerta-roja {{
    background:rgba(255,107,107,.06); border:1px solid rgba(255,107,107,.2);
    border-left:4px solid {red}; border-radius:14px;
    padding:1.2rem 1.5rem; color:{tx1}; font-weight:500;
}}
.alerta-info {{
    background:rgba(77,124,254,.06); border:1px solid rgba(77,124,254,.2);
    border-left:4px solid {blue}; border-radius:14px;
    padding:1.2rem 1.5rem; color:{tx1}; font-weight:500;
}}
.alerta-success {{
    background:rgba(0,230,138,.06); border:1px solid rgba(0,230,138,.2);
    border-left:4px solid {acc}; border-radius:14px;
    padding:1.2rem 1.5rem; color:{tx1}; font-weight:500;
}}

/* ─── Scenario Items ─── */
.scenario-item {{
    display:flex; justify-content:space-between; align-items:center;
    padding:.85rem 1.2rem; border-radius:12px;
    border:1px solid {brd}; margin:.4rem 0;
    background:{card}; cursor:pointer; transition:all .2s ease;
}}
.scenario-item:hover {{
    border-color:rgba(0,230,138,.25); transform:translateX(4px);
    background:{card_h};
}}
.scenario-name {{ font-weight:700; color:{tx1}; font-size:.9rem; }}
.scenario-date {{ font-size:.75rem; color:{tx2}; }}

/* ─── Soil Indicators ─── */
.soil-indicator {{
    display:inline-flex; align-items:center; gap:.5rem;
    padding:.5rem 1rem; border-radius:999px;
    font-weight:600; font-size:.85rem;
}}
.soil-easy {{ background:rgba(0,230,138,.12); color:{acc}; }}
.soil-medium {{ background:rgba(255,212,59,.12); color:{yellow}; }}
.soil-hard {{ background:rgba(255,107,107,.12); color:{red}; }}

/* ─── Progress Stages ─── */
.progress-stage {{
    display:flex; align-items:center; gap:.75rem;
    padding:.75rem 1rem; margin:.4rem 0;
    border-radius:12px; background:{card}; border:1px solid {brd};
    transition:all .3s ease;
}}
.progress-stage.active {{ border-color:{acc}; background:rgba(0,230,138,.04); }}
.progress-stage.done {{ border-color:{acc}; background:rgba(0,230,138,.06); }}
.progress-icon {{ font-size:1.2rem; }}
.progress-label {{ font-weight:500; color:{tx1}; font-size:.9rem; }}

/* ─── Insight Header ─── */
.insight-header {{
    background:linear-gradient(135deg,rgba(0,230,138,.06) 0%,rgba(77,124,254,.06) 100%);
    border:1px solid {brd}; border-radius:18px;
    padding:1.5rem 2rem; margin-bottom:1.5rem;
}}
.insight-header h3 {{ color:{tx1}; margin:0 0 .5rem; }}
.insight-header p {{ color:{tx2}; margin:0; line-height:1.6; }}

/* ─── KPI Grid (custom) ─── */
.kpi-grid {{
    display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
    gap:1rem; margin:1rem 0;
}}
.kpi-card {{
    background:{card}; border:1px solid {brd}; border-radius:16px;
    padding:1.5rem; position:relative; overflow:hidden;
    transition:all .25s ease;
}}
.kpi-card:hover {{
    transform:translateY(-3px);
    box-shadow:0 8px 25px {shd};
}}
.kpi-label {{ color:{tx2}; font-size:.78rem; text-transform:uppercase;
    letter-spacing:.8px; font-weight:600; margin-bottom:.4rem; }}
.kpi-value {{ font-size:2rem; font-weight:800; color:{tx1}; line-height:1.1; }}
.kpi-delta {{ font-size:.82rem; font-weight:600; margin-top:.3rem; }}
.kpi-delta.up {{ color:{acc}; }}
.kpi-delta.down {{ color:{red}; }}
.kpi-delta.neutral {{ color:{tx2}; }}
.kpi-accent-green {{ border-top:3px solid {acc}; }}
.kpi-accent-blue {{ border-top:3px solid {blue}; }}
.kpi-accent-yellow {{ border-top:3px solid {yellow}; }}
.kpi-accent-red {{ border-top:3px solid {red}; }}
.kpi-accent-purple {{ border-top:3px solid {purple}; }}
.kpi-accent-cyan {{ border-top:3px solid {cyan}; }}

/* ─── Engine Banner ─── */
.engine-banner {{
    background:linear-gradient(135deg,rgba(0,230,138,.08),rgba(77,124,254,.08));
    border:1px solid {brd}; border-radius:18px;
    padding:2rem; margin-bottom:1.5rem; text-align:center;
}}
.engine-banner h2 {{ margin:0 0 .3rem; font-size:1.5rem; }}
.engine-banner p {{ color:{tx2}; margin:0; font-size:.9rem; }}

/* ─── Stats Badge Row ─── */
.stats-badge {{
    background:{card}; border:1px solid {brd};
    border-radius:10px; padding:.45rem 1rem;
    font-size:.82rem; display:inline-flex; gap:.4rem;
}}
.stats-badge-label {{ color:{tx2}; }}
.stats-badge-value {{ color:{tx1}; font-weight:700; }}

/* ─── Section Divider ─── */
.section-title {{
    display:flex; align-items:center; gap:.75rem;
    margin:1.5rem 0 1rem;
}}
.section-title h3 {{ margin:0; font-size:1.15rem; }}
.section-title .badge {{
    background:rgba(0,230,138,.1); color:{acc};
    padding:.2rem .7rem; border-radius:6px;
    font-size:.7rem; font-weight:700; text-transform:uppercase;
}}

/* ═══ Animations ═══ */
@keyframes fadeInUp {{
    from {{ opacity:0; transform:translateY(12px); }}
    to {{ opacity:1; transform:translateY(0); }}
}}
@keyframes pulse {{
    0%,100% {{ opacity:1; }}
    50% {{ opacity:.6; }}
}}
.animate-in {{ animation:fadeInUp .4s ease forwards; }}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# ── Logo SVG ───────────────────────────────────────────────────
logo_svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 60" width="190" height="56">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#00E68A"/>
      <stop offset="100%" style="stop-color:#00CC7A"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="56" height="56" rx="14" fill="url(#g1)" opacity=".12"/>
  <rect x="7" y="7" width="46" height="46" rx="10" fill="url(#g1)"/>
  <text x="19" y="42" font-family="Inter,Arial" font-size="28" font-weight="800" fill="#0B0B0F">E</text>
  <text x="68" y="36" font-family="Inter,Arial" font-size="22" font-weight="800" fill="{tx1}">EMCA</text>
  <text x="68" y="50" font-family="Inter,Arial" font-size="8.5" font-weight="600" fill="{tx2}" letter-spacing="1.5">STOCHASTIC SYSTEM</text>
</svg>
'''

with st.sidebar:
    st.markdown(
        f'<div style="text-align:center;padding:1rem 0 .8rem;'
        f'border-bottom:1px solid {brd};margin-bottom:.8rem">{logo_svg}</div>',
        unsafe_allow_html=True,
    )

# ── Navigation ─────────────────────────────────────────────────
pg_home = st.Page("pages/00_home.py", title="Inicio", icon="🏠", default=True)
pg_param = st.Page("pages/01_parametrizacion.py", title="Parametrización", icon="📋")
pg_sim   = st.Page("pages/02_simulacion.py", title="Simulación", icon="⚙️")
pg_dash  = st.Page("pages/03_dashboard.py", title="Dashboard", icon="📊")

pg = st.navigation({
    "Sistema": [pg_home],
    "Módulos": [pg_param, pg_sim, pg_dash],
})
pg.run()
