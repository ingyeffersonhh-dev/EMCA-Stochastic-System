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

# ── Carga Dinámica de CSS ──────────────────────────────────────
css_file = os.path.join(ROOT_DIR, "app", "assets", "style.css")
try:
    with open(css_file, "r", encoding="utf-8") as f:
        static_css = f.read()
except FileNotFoundError:
    static_css = ""

root_vars = f"""
:root {{
    --bg: {bg};
    --bg2: {bg2};
    --card: {card};
    --card-h: {card_h};
    --tx1: {tx1};
    --tx2: {tx2};
    --tx3: {tx3};
    --brd: {brd};
    --shd: {shd};
    --acc: {acc};
    --acc2: {acc2};
    --blue: {blue};
    --yellow: {yellow};
    --red: {red};
    --purple: {purple};
    --cyan: {cyan};
}}
"""

st.markdown(f"<style>\n{root_vars}\n{static_css}\n</style>", unsafe_allow_html=True)

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
