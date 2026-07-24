"""
app/main.py
Entry point — EMCA Sistema de Pilotes.
Mode-aware UI built on the dual-palette token system (theme.py).
Light is the default; users opt into dark via Streamlit's native theme toggle.
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

# ── Design Tokens — active palette resolved at runtime ──────────
from app.components.theme import get_active_tokens, _rgba

t = get_active_tokens()

css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ═══ Base ═══ */
html, body, [class*="css"] {{ font-family:'Inter',sans-serif; }}
.stApp {{ background:{t.BG}!important; }}
[data-testid="stHeader"] {{ background:transparent!important; }}

/* ═══ Sidebar ═══ */
[data-testid="stSidebar"] {{
    background:{t.BG2}!important;
    border-right:1px solid {t.BRD};
}}
/* Selectbox dropdown — Streamlit 1.60 (React Aria Components).
   The dropdown is a Popover PORTAL rendered at <body>, outside the
   widget tree.  We target every possible container: the RAC Popover
   overlay, the listbox div, and the Virtualizer scroll area. */

/* 1. The Popover overlay (portal at body level) */
div[data-trigger="ComboBox"],
[role="presentation"] > div[role="listbox"],

/* 2. The listbox itself (always a <div>, never <ul>) */
div[role="listbox"],

/* 3. Fallback: any element Streamlit marks as popover or virtual dropdown */
[data-testid="stPopover"],
[data-testid="stVirtualDropdown"],
[data-testid="stSelectboxVirtualDropdown"] {{
    max-height: calc(50vh - 60px) !important;
    overflow-y: auto !important;
}}

/* Scrollbar styling for all the above */
div[data-trigger="ComboBox"]::-webkit-scrollbar,
div[role="listbox"]::-webkit-scrollbar,
[data-testid="stPopover"]::-webkit-scrollbar,
[data-testid="stVirtualDropdown"]::-webkit-scrollbar {{
    width: 6px;
}}
div[data-trigger="ComboBox"]::-webkit-scrollbar-thumb,
div[role="listbox"]::-webkit-scrollbar-thumb,
[data-testid="stPopover"]::-webkit-scrollbar-thumb,
[data-testid="stVirtualDropdown"]::-webkit-scrollbar-thumb {{
    background: {t.TX3}; border-radius: 3px;
}}
/* Scroll vertical del sidebar sin mostrar la barra
   Streamlit maneja el scroll real en [stSidebarContent]; apuntamos a él
   y a los contenedores padres por si el testid cambia entre versiones. */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
[data-testid="stSidebarScrollableContainer"],
[data-testid="stSidebarUserContent"] {{
    overflow-y:auto !important;
    scrollbar-width:none;          /* Firefox */
    -ms-overflow-style:none;       /* IE/Edge legacy */
}}
[data-testid="stSidebar"]::-webkit-scrollbar,
[data-testid="stSidebarContent"]::-webkit-scrollbar,
[data-testid="stSidebarScrollableContainer"]::-webkit-scrollbar,
[data-testid="stSidebarUserContent"]::-webkit-scrollbar {{
    display:none;                  /* Chrome/Safari/Edge */
    width:0; height:0;
}}
[data-testid="stSidebarNav"] {{ padding-top:.5rem; }}
[data-testid="stSidebarNav"] a {{
    border-radius:10px; margin:2px 8px; padding:6px 12px;
    transition:all .2s ease;
}}
[data-testid="stSidebarNav"] a:hover {{ background:{_rgba(t.ACC, 0.1)}; }}
[data-testid="stSidebarNav"] a[aria-selected="true"] {{
    background:{_rgba(t.ACC, 0.15)}!important;
    border-left:3px solid {t.ACC};
}}

/* ═══ Metric Cards ═══ */
div[data-testid="metric-container"] {{
    background:{t.CARD};
    border:1px solid {t.BRD};
    border-radius:16px;
    padding:1.25rem 1.5rem;
    box-shadow:0 4px 20px {t.SHD};
    transition:transform .25s ease,box-shadow .25s ease;
    position:relative;
    overflow:hidden;
}}
div[data-testid="metric-container"]::before {{
    content:'';position:absolute;top:0;left:0;width:4px;height:100%;
    background:linear-gradient(180deg,{t.ACC},{t.CYAN});border-radius:4px 0 0 4px;
}}
div[data-testid="metric-container"]:hover {{
    transform:translateY(-3px);
    box-shadow:0 8px 30px {t.SHD},0 0 20px {_rgba(t.ACC, 0.1)};
}}
div[data-testid="metric-container"] label {{
    color:{t.TX2}!important;font-size:.78rem!important;
    text-transform:uppercase;letter-spacing:.8px;font-weight:600!important;
}}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-size:1.8rem!important;font-weight:800!important;color:{t.TX1}!important;
}}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-size:.8rem!important;font-weight:600!important;
}}

/* ═══ Buttons ═══ */
.stButton > button {{
    background:linear-gradient(135deg,{t.ACC},{t.ACC2})!important;
    color:{t.CARD}!important; border:none!important;
    border-radius:12px; font-weight:700; font-size:.9rem;
    letter-spacing:.3px; padding:.6rem 1.5rem;
    transition:all .25s cubic-bezier(.4,0,.2,1);
    box-shadow:0 4px 15px {_rgba(t.ACC, 0.3)};
}}
.stButton > button:hover {{
    transform:translateY(-2px)!important;
    box-shadow:0 8px 25px {_rgba(t.ACC, 0.4)}!important;
    filter:brightness(1.1);
}}
.stButton > button[kind="secondary"],
.stButton > button[data-testid="stBaseButton-secondary"] {{
    background:{t.CARD}!important; color:{t.TX1}!important;
    border:1px solid {t.BRD}!important;
    box-shadow:0 2px 8px {t.SHD}!important;
}}
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="stBaseButton-secondary"]:hover {{
    background:{t.CARD_H}!important;
    border-color:{_rgba(t.ACC, 0.4)}!important;
}}

/* ═══ Tabs ═══ */
.stTabs [data-baseweb="tab-list"] {{
    background:{t.CARD}; border-radius:14px; padding:4px; gap:4px;
    border:1px solid {t.BRD};
}}
.stTabs [data-baseweb="tab"] {{
    border-radius:10px; padding:10px 22px;
    background:transparent; color:{t.TX2}!important;
    font-weight:500; transition:all .2s ease;
}}
.stTabs [aria-selected="true"] {{
    background:{_rgba(t.ACC, 0.15)}!important;
    color:{t.ACC}!important; font-weight:700;
    box-shadow:0 2px 8px {_rgba(t.ACC, 0.15)};
    border-bottom:none!important;
}}

/* ═══ Typography ═══ */
h1,h2,h3,h4,h5,h6 {{ color:{t.TX1}!important; }}
p,span,div,label,li {{ color:{t.TX1}; }}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {{ color:{t.TX1}!important; }}
[data-testid="stCaption"] {{ color:{t.TX2}!important; }}

/* ═══ Forms & Inputs ═══ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {{
    background:{t.CARD}!important; color:{t.TX1}!important;
    border:1px solid {t.BRD}!important; border-radius:10px!important;
    transition:border-color .2s ease;
}}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {{
    border-color:{t.ACC}!important;
    box-shadow:0 0 0 2px {_rgba(t.ACC, 0.2)}!important;
}}
.stSlider > div > div > div > div {{ background:{t.ACC}!important; }}
.stCheckbox > label > div {{ background:{t.CARD}!important; border-color:{t.BRD}!important; }}
.stRadio > label > div {{ background:{t.CARD}!important; border-color:{t.BRD}!important; }}
[data-baseweb="select"] > div {{
    background:{t.CARD}!important; color:{t.TX1}!important;
    border-color:{t.BRD}!important; border-radius:10px!important;
}}
[data-baseweb="popover"] [data-baseweb="menu"] {{
    background:{t.CARD}!important; border:1px solid {t.BRD}!important;
}}

/* ═══ Tables & DataFrames ═══ */
[data-testid="stDataFrame"] {{
    background:{t.CARD}; border-radius:14px; border:1px solid {t.BRD};
    overflow:hidden;
}}
.stExpander {{
    background:{t.CARD}!important; border:1px solid {t.BRD}!important;
    border-radius:14px!important;
}}
.stExpander > div {{ color:{t.TX1}!important; }}

/* ═══ Alerts ═══ */
[data-testid="stAlert"] {{
    background:{t.CARD}!important; color:{t.TX1}!important;
    border:1px solid {t.BRD}!important; border-radius:12px!important;
}}

/* ═══ Plotly ═══ */
.stPlotlyChart {{ background:transparent!important; }}

/* ═══ Scrollbar ═══ */
::-webkit-scrollbar {{ width:6px; }}
::-webkit-scrollbar-track {{ background:{t.BG}; }}
::-webkit-scrollbar-thumb {{ background:{t.TX3}; border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:{t.TX2}; }}

/* ══════════════════════════════════════════════════════════════
   CUSTOM COMPONENTS
   ══════════════════════════════════════════════════════════════ */

/* ─── Nav Cards ─── */
.nav-card {{
    background:{t.CARD}; border:1px solid {t.BRD}; border-radius:18px;
    padding:1.8rem; margin:.5rem 0; height:100%;
    transition:all .3s cubic-bezier(.4,0,.2,1);
    box-shadow:0 4px 20px {t.SHD}; cursor:pointer;
    position:relative; overflow:hidden;
}}
.nav-card::after {{
    content:'';position:absolute;bottom:0;left:50%;
    width:0;height:3px;background:{t.ACC};
    transition:all .3s ease;transform:translateX(-50%);
}}
.nav-card:hover {{
    transform:translateY(-5px);
    box-shadow:0 12px 35px {t.SHD},0 0 25px {_rgba(t.GREEN, 0.08)};
    border-color:{_rgba(t.GREEN, 0.2)};
}}
.nav-card:hover::after {{ width:60%; }}
.nav-card h3 {{ color:{t.TX1}; margin-top:0; font-weight:700; font-size:1.1rem; }}
.nav-card h4 {{
    color:{t.ACC}; font-size:.8rem; font-weight:700;
    margin-bottom:.8rem; text-transform:uppercase; letter-spacing:1px;
}}
.nav-card p {{ color:{t.TX2}; line-height:1.6; font-size:.88rem; }}

/* ─── Stepper ─── */
.stepper {{
    display:flex; align-items:center; justify-content:center;
    padding:.8rem 1.5rem; margin-bottom:1.5rem;
    background:{t.CARD}; border-radius:14px;
    border:1px solid {t.BRD}; box-shadow:0 4px 15px {t.SHD};
}}
.stepper-step {{
    display:flex; align-items:center; gap:.4rem;
    padding:.5rem 1rem; border-radius:999px;
    font-weight:600; font-size:.82rem; color:{t.TX3};
    transition:all .2s ease;
}}
.stepper-step.active {{ background:{t.ACC}; color:{t.BG}; }}
.stepper-step.completed {{ color:{t.GREEN}; }}
.stepper-arrow {{ color:{t.TX3}; margin:0 .4rem; font-size:1.1rem; }}

/* ─── Flow Diagram ─── */
.flow-diagram {{
    display:flex; align-items:center; justify-content:center;
    gap:1rem; padding:1.5rem; margin:1rem 0;
}}
.flow-node {{
    background:{t.CARD}; border:1px solid {t.BRD}; border-radius:14px;
    padding:1.2rem 1.8rem; text-align:center;
    font-weight:600; color:{t.TX1}; box-shadow:0 2px 10px {t.SHD};
    transition:all .2s ease;
}}
.flow-node:hover {{ border-color:{_rgba(t.GREEN, 0.25)}; transform:translateY(-2px); }}
.flow-arrow {{ font-size:1.5rem; color:{t.ACC}; }}

/* ─── Preview Cards ─── */
.preview-card {{
    background:{t.CARD}; border:1px solid {t.BRD}; border-radius:16px;
    padding:1.5rem; margin:1rem 0; box-shadow:0 4px 15px {t.SHD};
}}
.preview-card h4 {{
    color:{t.ACC}; margin:0 0 1rem; font-size:.82rem;
    text-transform:uppercase; letter-spacing:1px; font-weight:700;
}}
.preview-row {{
    display:flex; justify-content:space-between;
    padding:.55rem 0; border-bottom:1px solid {t.BRD}; font-size:.9rem;
}}
.preview-row:last-child {{ border-bottom:none; }}
.preview-label {{ color:{t.TX2}; }}
.preview-value {{ color:{t.TX1}; font-weight:700; }}

/* ─── Alerts ─── */
.alerta-roja {{
    background:{_rgba(t.RED, 0.06)}; border:1px solid {_rgba(t.RED, 0.2)};
    border-left:4px solid {t.RED}; border-radius:14px;
    padding:1.2rem 1.5rem; color:{t.TX1}; font-weight:500;
}}
.alerta-info {{
    background:{_rgba(t.BLUE, 0.06)}; border:1px solid {_rgba(t.BLUE, 0.2)};
    border-left:4px solid {t.BLUE}; border-radius:14px;
    padding:1.2rem 1.5rem; color:{t.TX1}; font-weight:500;
}}
.alerta-success {{
    background:{_rgba(t.GREEN, 0.06)}; border:1px solid {_rgba(t.GREEN, 0.2)};
    border-left:4px solid {t.GREEN}; border-radius:14px;
    padding:1.2rem 1.5rem; color:{t.TX1}; font-weight:500;
}}

/* ─── Scenario Items ─── */
.scenario-item {{
    display:flex; justify-content:space-between; align-items:center;
    padding:.85rem 1.2rem; border-radius:12px;
    border:1px solid {t.BRD}; margin:.4rem 0;
    background:{t.CARD}; cursor:pointer; transition:all .2s ease;
}}
.scenario-item:hover {{
    border-color:{_rgba(t.GREEN, 0.25)}; transform:translateX(4px);
    background:{t.CARD_H};
}}
.scenario-name {{ font-weight:700; color:{t.TX1}; font-size:.9rem; }}
.scenario-date {{ font-size:.75rem; color:{t.TX2}; }}

/* ─── Soil Indicators ─── */
.soil-indicator {{
    display:inline-flex; align-items:center; gap:.5rem;
    padding:.5rem 1rem; border-radius:999px;
    font-weight:600; font-size:.85rem;
}}
.soil-easy {{ background:{_rgba(t.GREEN, 0.12)}; color:{t.GREEN}; }}
.soil-medium {{ background:{_rgba(t.YELLOW, 0.12)}; color:{t.YELLOW}; }}
.soil-hard {{ background:{_rgba(t.RED, 0.12)}; color:{t.RED}; }}

/* ─── Progress Stages ─── */
.progress-stage {{
    display:flex; align-items:center; gap:.75rem;
    padding:.75rem 1rem; margin:.4rem 0;
    border-radius:12px; background:{t.CARD}; border:1px solid {t.BRD};
    transition:all .3s ease;
}}
.progress-stage.active {{ border-color:{t.ACC}; background:{_rgba(t.GREEN, 0.04)}; }}
.progress-stage.done {{ border-color:{t.ACC}; background:{_rgba(t.GREEN, 0.06)}; }}
.progress-icon {{ font-size:1.2rem; }}
.progress-label {{ font-weight:500; color:{t.TX1}; font-size:.9rem; }}

/* ─── Insight Header ─── */
.insight-header {{
    background:linear-gradient(135deg,{_rgba(t.GREEN, 0.06)} 0%,{_rgba(t.BLUE, 0.06)} 100%);
    border:1px solid {t.BRD}; border-radius:18px;
    padding:1.5rem 2rem; margin-bottom:1.5rem;
}}
.insight-header h3 {{ color:{t.TX1}; margin:0 0 .5rem; }}
.insight-header p {{ color:{t.TX2}; margin:0; line-height:1.6; }}

/* ─── KPI Grid (custom) ─── */
.kpi-grid {{
    display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr));
    gap:1rem; margin:1rem 0;
}}
.kpi-card {{
    background:{t.CARD}; border:1px solid {t.BRD}; border-radius:16px;
    padding:1.5rem; position:relative; overflow:hidden;
    transition:all .25s ease;
}}
.kpi-card:hover {{
    transform:translateY(-3px);
    box-shadow:0 8px 25px {t.SHD};
}}
.kpi-label {{ color:{t.TX2}; font-size:.78rem; text-transform:uppercase;
    letter-spacing:.8px; font-weight:600; margin-bottom:.4rem; }}
.kpi-value {{ font-size:2rem; font-weight:800; color:{t.TX1}; line-height:1.1; }}
.kpi-delta {{ font-size:.82rem; font-weight:600; margin-top:.3rem; }}
.kpi-delta.up {{ color:{t.ACC}; }}
.kpi-delta.down {{ color:{t.RED}; }}
.kpi-delta.neutral {{ color:{t.TX2}; }}
.kpi-accent-green {{ border-top:3px solid {t.GREEN}; }}
.kpi-accent-blue {{ border-top:3px solid {t.BLUE}; }}
.kpi-accent-yellow {{ border-top:3px solid {t.YELLOW}; }}
.kpi-accent-red {{ border-top:3px solid {t.RED}; }}
.kpi-accent-purple {{ border-top:3px solid {t.PURPLE}; }}
.kpi-accent-cyan {{ border-top:3px solid {t.CYAN}; }}

/* ─── Engine Banner ─── */
.engine-banner {{
    background:linear-gradient(135deg,{_rgba(t.GREEN, 0.08)},{_rgba(t.BLUE, 0.08)});
    border:1px solid {t.BRD}; border-radius:18px;
    padding:2rem; margin-bottom:1.5rem; text-align:center;
}}
.engine-banner h2 {{ margin:0 0 .3rem; font-size:1.5rem; }}
.engine-banner p {{ color:{t.TX2}; margin:0; font-size:.9rem; }}

/* ─── Stats Badge Row ─── */
.stats-badge {{
    background:{t.CARD}; border:1px solid {t.BRD};
    border-radius:10px; padding:.45rem 1rem;
    font-size:.82rem; display:inline-flex; gap:.4rem;
}}
.stats-badge-label {{ color:{t.TX2}; }}
.stats-badge-value {{ color:{t.TX1}; font-weight:700; }}

/* ─── Section Divider ─── */
.section-title {{
    display:flex; align-items:center; gap:.75rem;
    margin:1.5rem 0 1rem;
}}
.section-title h3 {{ margin:0; font-size:1.15rem; }}
.section-title .badge {{
    background:{_rgba(t.GREEN, 0.1)}; color:{t.ACC};
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

# ── Dropdown height fix (JS) ─────────────────────────────────────
# Streamlit 1.60 renders selectbox dropdowns as React Aria Popover
# portals at <body> level.  CSS selectors cannot reliably reach them.
# A MutationObserver watches the parent document and constrains any
# [role="listbox"] element the instant it appears in the DOM.
import streamlit.components.v1 as _components

_components.html("""
<script>
(function() {
    var doc = window.parent.document;
    var maxH = 'calc(50vh - 60px)';
    function fix() {
        doc.querySelectorAll('[role="listbox"]').forEach(function(el) {
            el.style.setProperty('max-height', maxH, 'important');
            el.style.setProperty('overflow-y', 'auto', 'important');
        });
    }
    new MutationObserver(fix).observe(doc.body, {childList:true, subtree:true});
})();
</script>
""", height=0)

# ── Logo SVG ───────────────────────────────────────────────────
# Brand gradient stays constant per design open question (brand identity);
# only the text fills below adapt to the active palette.
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
  <text x="19" y="42" font-family="Inter,Arial" font-size="28" font-weight="800" fill="{t.BG}">E</text>
  <text x="68" y="36" font-family="Inter,Arial" font-size="22" font-weight="800" fill="{t.TX1}">EMCA</text>
  <text x="68" y="50" font-family="Inter,Arial" font-size="8.5" font-weight="600" fill="{t.TX2}" letter-spacing="1.5">STOCHASTIC SYSTEM</text>
</svg>
'''

# Detectar si estamos ejecutando desde la raíz o desde la carpeta app/
base_dir = os.path.dirname(__file__)
if not base_dir.endswith("app") and os.path.exists(os.path.join(base_dir, "app")):
    assets_dir = os.path.join(base_dir, "app", "assets")
    pages_dir = os.path.join(base_dir, "app", "pages")
else:
    assets_dir = os.path.join(base_dir, "assets")
    pages_dir = os.path.join(base_dir, "pages")

with st.sidebar:
    logo_path = os.path.join(assets_dir, "logo.png")
    if os.path.exists(logo_path):
        st.markdown(
            f'<div style="padding:1rem 0 .8rem;border-bottom:1px solid {t.BRD};margin-bottom:.8rem;text-align:center">',
            unsafe_allow_html=True
        )
        st.image(logo_path, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div style="text-align:center;padding:1rem 0 .8rem;'
            f'border-bottom:1px solid {t.BRD};margin-bottom:.8rem">'
            f'<span style="font-size:1.4rem;font-weight:800;color:{t.ACC}">🏗️ EMCA</span></div>',
            unsafe_allow_html=True,
        )

    # ── Global state banner
    escenario_activo = None
    sim_ok = False
    if "parametros" in st.session_state:
        escenario_activo = st.session_state["parametros"].nombre_escenario
        sim_ok = "resultado" in st.session_state

    if escenario_activo:
        sim_icon  = "✅" if sim_ok else "⏳"
        sim_label = "Simulado" if sim_ok else "Pendiente"
        sim_color = t.ACC if sim_ok else t.YELLOW
        st.markdown(f"""
        <div style="background:{_rgba(t.ACC, 0.07)};border:1px solid {_rgba(t.ACC, 0.18)};
            border-radius:12px;padding:.85rem 1rem;margin-bottom:.8rem">
            <div style="font-size:.68rem;color:{t.TX2};text-transform:uppercase;letter-spacing:.7px;
                font-weight:600;margin-bottom:.4rem">Escenario activo</div>
            <div style="font-weight:700;color:{t.TX1};font-size:.88rem;margin-bottom:.35rem
                ">{escenario_activo}</div>
            <div style="font-size:.78rem;color:{sim_color};font-weight:600">
                {sim_icon} Simulación: {sim_label}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background:{_rgba(t.YELLOW, 0.06)};border:1px solid {_rgba(t.YELLOW, 0.18)};
            border-radius:12px;padding:.85rem 1rem;margin-bottom:.8rem">
            <div style="font-size:.78rem;color:{t.YELLOW};font-weight:600">
                ⚠️ Sin escenario activo
            </div>
            <div style="font-size:.75rem;color:{t.TX2};margin-top:.2rem">
                Configurá uno en Parametrización
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Navigation ─────────────────────────────────────────────────
pg_home  = st.Page(os.path.join(pages_dir, "00_home.py"), title="Inicio", icon="🏠", default=True)
pg_param = st.Page(os.path.join(pages_dir, "01_parametrizacion.py"), title="Parametrización", icon="📋")
pg_sim   = st.Page(os.path.join(pages_dir, "02_simulacion.py"), title="Simulación", icon="⚙️")
pg_dash  = st.Page(os.path.join(pages_dir, "03_dashboard.py"), title="Dashboard", icon="📊")
pg_comp  = st.Page(os.path.join(pages_dir, "04_comparacion.py"), title="Comparación", icon="🔍")

pg = st.navigation({
    "Sistema": [pg_home],
    "Módulos": [pg_param, pg_sim, pg_dash],
    "Análisis": [pg_comp],
})

# ── JS: dynamically cap selectbox dropdown height ──────────────
# CSS selectors for BaseWeb dropdowns can break across Streamlit
# versions. This MutationObserver patches any open dropdown menu
# so it never extends past the viewport, regardless of testid.
st.markdown("""
<script>
(function() {
    function capDropdown(menu) {
        if (!menu) return;
        const vh = window.innerHeight;
        const rect = menu.getBoundingClientRect();
        // If the menu extends below the viewport, cap its height
        if (rect.bottom > vh) {
            const overflow = rect.bottom - vh + 20;
            const newH = Math.max(150, rect.height - overflow);
            menu.style.maxHeight = newH + 'px';
            menu.style.overflowY = 'auto';
        }
    }
    function scanForOpenMenus() {
        // BaseWeb select dropdown: look for option lists
        const candidates = document.querySelectorAll(
            '[role="listbox"], [data-baseweb="menu"] ul, ' +
            'ul[data-testid="stSelectboxVirtualDropdown"], ' +
            '[data-testid="stSelectbox"] [role="listbox"]'
        );
        candidates.forEach(capDropdown);
    }
    const obs = new MutationObserver(function(muts) {
        for (const m of muts) {
            for (const node of m.addedNodes) {
                if (node.nodeType === 1 && (
                    node.matches && node.matches('[role="listbox"], [data-baseweb="menu"]') ||
                    node.querySelector && (node.querySelector('[role="listbox"]') || node.querySelector('[data-baseweb="menu"]'))
                )) {
                    setTimeout(scanForOpenMenus, 30);
                    setTimeout(scanForOpenMenus, 200);
                }
            }
        }
    });
    obs.observe(document.body, {childList: true, subtree: true});
    // Also cap on any click (dropdown opens on click)
    document.addEventListener('click', function() {
        setTimeout(scanForOpenMenus, 30);
        setTimeout(scanForOpenMenus, 200);
    });
})();
</script>
""", unsafe_allow_html=True)

pg.run()