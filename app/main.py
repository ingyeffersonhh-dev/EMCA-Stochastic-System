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

from core.utils.auth import verify_jwt, inject_cookie_remover_js

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

# --- Verificación de Sesión / JWT ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# Si no está autenticado en la sesión, intentar leer la cookie JWT
if not st.session_state["authenticated"]:
    try:
        cookies = st.context.cookies
        session_token = cookies.get("emca_session")
        if session_token:
            payload = verify_jwt(session_token)
            if payload:
                st.session_state["authenticated"] = True
                st.session_state["username"] = payload.get("username")
                st.session_state["role"] = payload.get("role")
                st.session_state["nombre_usuario"] = payload.get("nombre")
    except Exception:
        pass

if not st.session_state["authenticated"]:
    # Ruteo restringido: Solo expone la pantalla de login
    pg_login = st.Page("pages/login.py", title="Iniciar Sesión", icon="🔒")
    pg = st.navigation([pg_login])
    pg.run()
else:
    # Ruteo normal
    with st.sidebar:
        # Render del Logo
        st.markdown(
            f'<div style="text-align:center;padding:1rem 0 .8rem;'
            f'border-bottom:1px solid {brd};margin-bottom:.8rem">{logo_svg}</div>',
            unsafe_allow_html=True,
        )
        # Información de sesión activa
        st.markdown(f"""
            <div style="padding: 0.8rem; background: var(--card); border-radius: 12px; border: 1px solid var(--brd); margin-bottom: 1rem; text-align: center;">
                <div style="font-size: 0.72rem; color: var(--tx2); text-transform: uppercase; letter-spacing: 0.8px;">Sesión Activa</div>
                <div style="font-weight: 700; color: var(--acc); font-size: 0.88rem; margin-top: 0.2rem;">{st.session_state.get('nombre_usuario', 'Usuario')}</div>
                <div style="font-size: 0.72rem; color: var(--tx3); margin-top: 0.1rem;">Rol: {str(st.session_state.get('role', '')).upper()}</div>
            </div>
        """, unsafe_allow_html=True)

    pg_home = st.Page("pages/00_home.py", title="Inicio", icon="🏠", default=True)
    pg_param = st.Page("pages/01_parametrizacion.py", title="Parametrización", icon="📋")
    pg_sim   = st.Page("pages/02_simulacion.py", title="Simulación", icon="⚙️")
    pg_dash  = st.Page("pages/03_dashboard.py", title="Dashboard", icon="📊")

    pg = st.navigation({
        "Sistema": [pg_home],
        "Módulos": [pg_param, pg_sim, pg_dash],
    })
    pg.run()
    
    # Botón de cerrar sesión al final del sidebar
    with st.sidebar:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="secondary"):
            st.session_state["authenticated"] = False
            st.session_state.pop("username", None)
            st.session_state.pop("role", None)
            st.session_state.pop("nombre_usuario", None)
            inject_cookie_remover_js()
            st.rerun()
