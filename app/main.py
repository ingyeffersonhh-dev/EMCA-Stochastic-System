"""
app/main.py
Entry point de la aplicación Streamlit — EMCA Sistema de Pilotes.
Con sincronización de tema oscuro/claro entre botón personalizado y Streamlit nativo.
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

# Detectar tema de Streamlit
is_dark_theme = st.get_option("theme.backgroundColor") == "#0f172a"

if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = is_dark_theme

def toggle_theme():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]

dark = st.session_state["dark_mode"]

# Colores según modo
if dark:
    bg_primary = "#0f172a"
    bg_card = "#1e293b"
    text_primary = "#f1f5f9"
    text_secondary = "#94a3b8"
    border = "rgba(148, 163, 184, 0.15)"
    shadow = "rgba(0, 0, 0, 0.3)"
    chart_bg = "rgba(30, 41, 59, 0.5)"
    grid_color = "rgba(148, 163, 184, 0.15)"
    hist_color = "#60a5fa"
    hist_fill = "rgba(96, 165, 250, 0.6)"
else:
    bg_primary = "#f8fafc"
    bg_card = "#ffffff"
    text_primary = "#0f172a"
    text_secondary = "#64748b"
    border = "rgba(148, 163, 184, 0.25)"
    shadow = "rgba(0, 0, 0, 0.08)"
    chart_bg = "rgba(255, 255, 255, 0.8)"
    grid_color = "rgba(148, 163, 184, 0.25)"
    hist_color = "#3b82f6"
    hist_fill = "rgba(59, 130, 246, 0.7)"

css = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background-color: {bg_primary} !important;
    }}

    .nav-card {{
        background-color: {bg_card};
        color: {text_primary};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 1.8rem;
        margin: 0.5rem 0;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0px 4px 15px {shadow};
        cursor: pointer;
    }}

    .nav-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0px 12px 24px {shadow};
        border-color: #27ae60;
    }}

    .nav-card h3 {{
        color: {text_primary};
        margin-top: 0;
        font-weight: 700;
        font-size: 1.15rem;
    }}
    .nav-card h4 {{
        color: #2ecc71;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .nav-card p {{
        color: {text_secondary};
        line-height: 1.6;
        font-size: 0.9rem;
    }}

    div[data-testid="metric-container"] {{
        background-color: {bg_card};
        border: 1px solid {border};
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0px 4px 15px {shadow};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-left: 6px solid #27ae60;
    }}
    div[data-testid="metric-container"] > div {{
        color: {text_primary};
    }}
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0px 8px 20px {shadow};
    }}

    .stButton > button {{
        background: #27ae60;
        color: white;
        border: none;
        border-radius: 24px;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(39, 174, 96, 0.25);
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(39, 174, 96, 0.4);
        background: #2ecc71;
        color: white;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        background-color: rgba(128, 128, 128, 0.05);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 8px 20px;
        background-color: transparent;
        transition: all 0.2s ease;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        font-weight: 600;
        box-shadow: 0 2px 5px {shadow};
        border-bottom: none !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {text_primary} !important;
    }}

    p, span, div, label, li {{
        color: {text_primary};
    }}

    .alerta-roja {{
        background-color: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 6px solid #ef4444;
        border-radius: 16px;
        padding: 1.5rem;
        color: {text_primary};
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.05);
    }}

    .alerta-info {{
        background-color: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-left: 6px solid #3b82f6;
        border-radius: 16px;
        padding: 1.5rem;
        color: {text_primary};
        font-weight: 500;
    }}

    .alerta-success {{
        background-color: rgba(39, 174, 96, 0.08);
        border: 1px solid rgba(39, 174, 96, 0.3);
        border-left: 6px solid #27ae60;
        border-radius: 16px;
        padding: 1.5rem;
        color: {text_primary};
        font-weight: 500;
    }}

    .stepper {{
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem 2rem;
        margin-bottom: 1.5rem;
        background: {bg_card};
        border-radius: 16px;
        border: 1px solid {border};
        box-shadow: 0 4px 15px {shadow};
    }}
    .stepper-step {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-weight: 500;
        font-size: 0.85rem;
        color: {text_secondary};
        transition: all 0.2s ease;
    }}
    .stepper-step.active {{
        background: #27ae60;
        color: white;
    }}
    .stepper-step.completed {{
        color: #27ae60;
    }}
    .stepper-arrow {{
        color: {text_secondary};
        margin: 0 0.5rem;
        font-size: 1.2rem;
    }}

    .flow-diagram {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    .flow-node {{
        background: {bg_card};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        font-weight: 600;
        color: {text_primary};
        box-shadow: 0 2px 8px {shadow};
    }}
    .flow-arrow {{
        font-size: 1.5rem;
        color: #27ae60;
    }}

    .scenario-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: 1px solid {border};
        margin: 0.5rem 0;
        background: {bg_card};
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    .scenario-item:hover {{
        border-color: #27ae60;
        transform: translateX(4px);
    }}
    .scenario-name {{
        font-weight: 600;
        color: {text_primary};
        font-size: 0.9rem;
    }}
    .scenario-date {{
        font-size: 0.75rem;
        color: {text_secondary};
    }}

    .soil-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
    }}
    .soil-easy {{ background: rgba(39, 174, 96, 0.15); color: #27ae60; }}
    .soil-medium {{ background: rgba(243, 156, 18, 0.15); color: #f39c12; }}
    .soil-hard {{ background: rgba(231, 76, 60, 0.15); color: #e74c3c; }}

    .preview-card {{
        background: {bg_card};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px {shadow};
    }}
    .preview-card h4 {{
        color: #27ae60;
        margin: 0 0 1rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .preview-row {{
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid {border};
        font-size: 0.9rem;
    }}
    .preview-row:last-child {{ border-bottom: none; }}
    .preview-label {{ color: {text_secondary}; }}
    .preview-value {{ color: {text_primary}; font-weight: 600; }}

    .progress-stage {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        background: {bg_card};
        border: 1px solid {border};
    }}
    .progress-stage.active {{ border-color: #27ae60; }}
    .progress-stage.done {{ border-color: #27ae60; background: rgba(39, 174, 96, 0.08); }}
    .progress-icon {{ font-size: 1.2rem; }}
    .progress-label {{ font-weight: 500; color: {text_primary}; font-size: 0.9rem; }}

    .insight-header {{
        background: linear-gradient(135deg, rgba(39, 174, 96, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
        border: 1px solid {border};
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }}
    .insight-header h3 {{
        color: {text_primary};
        margin: 0 0 0.5rem;
    }}
    .insight-header p {{
        color: {text_secondary};
        margin: 0;
        line-height: 1.6;
    }}

    [data-testid="stSidebar"] {{
        background-color: {bg_card} !important;
        border-right: 1px solid {border};
    }}
    [data-testid="stSidebarNav"] {{
        padding-top: 1rem;
    }}

    [data-testid="stDataFrame"] {{
        background: {bg_card};
        border-radius: 12px;
        border: 1px solid {border};
    }}

    .stExpander {{
        background-color: {bg_card} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
    }}
    .stExpander > div {{
        color: {text_primary} !important;
    }}

    [data-baseweb="select"] > div {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
    }}
    [data-baseweb="select"] input {{
        color: {text_primary} !important;
    }}
    [data-baseweb="popover"] [data-baseweb="menu"] {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
    }}
    [data-baseweb="popover"] [data-baseweb="option"] {{
        color: {text_primary} !important;
    }}

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border-color: {border} !important;
    }}

    .stSlider > div > div > div > div {{
        background-color: #27ae60 !important;
    }}

    .stCheckbox > label > div {{
        background-color: {bg_card} !important;
        border-color: {border} !important;
    }}

    .stRadio > label > div {{
        background-color: {bg_card} !important;
        border-color: {border} !important;
    }}
    .stRadio > label > div > div {{
        background-color: #27ae60 !important;
    }}

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] li {{
        color: {text_primary} !important;
    }}

    [data-testid="stCaption"] {{
        color: {text_secondary} !important;
    }}

    [data-testid="stAlert"] {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border-color: {border} !important;
    }}

    .stPlotlyChart {{
        background: transparent !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Theme sync indicator */
    .theme-sync-indicator {{
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 9999;
        font-size: 0.75rem;
        color: {text_secondary};
        opacity: 0.7;
    }}
</style>
"""

st.markdown(css, unsafe_allow_html=True)

# Logo SVG en sidebar
text_color = "#f1f5f9" if dark else "#0f172a"
sub_color = "#94a3b8" if dark else "#64748b"

logo_svg = f'''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60" width="180" height="54">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#27ae60;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#2ecc71;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="56" height="56" rx="12" fill="url(#grad1)" opacity="0.15"/>
  <rect x="8" y="8" width="44" height="44" rx="8" fill="url(#grad1)"/>
  <text x="20" y="42" font-family="Arial,sans-serif" font-size="28" font-weight="bold" fill="white">E</text>
  <text x="68" y="38" font-family="Inter,Arial,sans-serif" font-size="22" font-weight="700" fill="{text_color}">EMCA</text>
  <text x="68" y="52" font-family="Inter,Arial,sans-serif" font-size="9" font-weight="500" fill="{sub_color}">STOCHASTIC SYSTEM</text>
</svg>
'''

# JavaScript para sincronizar tema
sync_js = """
<script>
(function() {
    // Detectar tema actual de Streamlit
    function getStreamlitTheme() {
        const bgColor = getComputedStyle(document.documentElement).getPropertyValue('--background-color').trim();
        return bgColor === '#0f172a' || bgColor === 'rgb(15, 23, 42)' ? 'dark' : 'light';
    }
    
    // Observar cambios en el tema de Streamlit
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'style' || mutation.attributeName === 'class') {
                const currentTheme = getStreamlitTheme();
                // Actualizar variable CSS para gráficos
                document.documentElement.style.setProperty('--chart-theme', currentTheme);
            }
        });
    });
    
    observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ['style', 'class', 'data-theme']
    });
    
    // Inicializar
    document.documentElement.style.setProperty('--chart-theme', getStreamlitTheme());
})();
</script>
"""

st.markdown(sync_js, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f'<div style="text-align:center;padding:1rem 0;border-bottom:1px solid {border};margin-bottom:1rem">{logo_svg}</div>', unsafe_allow_html=True)
    
    theme_icon = "🌙" if dark else "☀️"
    theme_label = "Modo Claro" if dark else "Modo Oscuro"
    if st.button(f"{theme_icon} {theme_label}", use_container_width=True, type="secondary", on_click=toggle_theme):
        st.rerun()

pg_home = st.Page("pages/00_home.py", title="Inicio", icon="🏠", default=True)
pg_param = st.Page("pages/01_parametrizacion.py", title="1. Parametrización", icon="📋")
pg_sim = st.Page("pages/02_simulacion.py", title="2. Simulación", icon="⚙️")
pg_dash = st.Page("pages/03_dashboard.py", title="3. Dashboard", icon="📊")

pg = st.navigation(
    {
        "Sistema EMCA": [pg_home],
        "Módulos": [pg_param, pg_sim, pg_dash]
    }
)

pg.run()
