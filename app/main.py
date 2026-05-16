"""
app/main.py
Entry point de la aplicación Streamlit — EMCA Sistema de Pilotes.
"""
import streamlit as st
import os
import sys
from datetime import datetime

# --- Configuración de Rutas para Deploy ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

st.set_page_config(
    page_title="EMCA — Planificación de Pilotes",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Modo Oscuro / Claro ---
if "dark_mode" not in st.session_state:
    st.session_state["dark_mode"] = True

def toggle_theme():
    st.session_state["dark_mode"] = not st.session_state["dark_mode"]

# --- CSS personalizado Premium (Estilo Lumina/Logistics SaaS) ---
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Variables de tema */
    :root {{
        --bg-primary: {"#0f172a" if st.session_state["dark_mode"] else "#f8fafc"};
        --bg-card: {"#1e293b" if st.session_state["dark_mode"] else "#ffffff"};
        --text-primary: {"#f1f5f9" if st.session_state["dark_mode"] else "#0f172a"};
        --text-secondary: {"#94a3b8" if st.session_state["dark_mode"] else "#64748b"};
        --accent: #27ae60;
        --accent-hover: #2ecc71;
        --border: {"rgba(148, 163, 184, 0.15)" if st.session_state["dark_mode"] else "rgba(148, 163, 184, 0.25)"};
        --shadow: {"rgba(0, 0, 0, 0.3)" if st.session_state["dark_mode"] else "rgba(0, 0, 0, 0.08)"};
    }}

    .stApp {{
        background-color: var(--bg-primary);
    }}

    /* Tarjetas de Navegación */
    .nav-card {{
        background-color: var(--bg-card);
        color: var(--text-primary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 0.5rem 0;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0px 4px 15px var(--shadow);
        cursor: pointer;
    }}
    
    .nav-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0px 12px 24px var(--shadow);
        border-color: var(--accent);
    }}

    .nav-card h3 {{
        color: var(--text-primary);
        margin-top: 0;
        font-weight: 700;
        font-size: 1.15rem;
    }}
    .nav-card h4 {{
        color: var(--accent);
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .nav-card p {{
        color: var(--text-secondary);
        line-height: 1.6;
        font-size: 0.9rem;
    }}

    /* Métricas estilo tarjeta */
    div[data-testid="metric-container"] {{
        background-color: var(--bg-card);
        border: 1px solid var(--border);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0px 4px 15px var(--shadow);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-left: 6px solid var(--accent);
    }}
    div[data-testid="metric-container"] > div {{
        color: var(--text-primary);
    }}
    div[data-testid="metric-container"]:hover {{
        transform: translateY(-3px);
        box-shadow: 0px 8px 20px var(--shadow);
    }}

    /* Botones estilo SaaS */
    .stButton > button {{
        background: var(--accent);
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
        background: var(--accent-hover);
        color: white;
    }}
    
    /* Tabs estilo Segmented Control */
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
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        font-weight: 600;
        box-shadow: 0 2px 5px var(--shadow);
        border-bottom: none !important;
    }}

    /* Títulos limpios */
    h1, h2 {{
        font-weight: 700;
        letter-spacing: -0.5px;
        color: var(--text-primary);
    }}

    h3, h4, h5, h6 {{
        color: var(--text-primary);
    }}
    
    /* Alerta logística roja */
    .alerta-roja {{
        background-color: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 6px solid #ef4444;
        border-radius: 16px;
        padding: 1.5rem;
        color: var(--text-primary);
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.05);
    }}

    /* Alerta info */
    .alerta-info {{
        background-color: rgba(59, 130, 246, 0.08);
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-left: 6px solid #3b82f6;
        border-radius: 16px;
        padding: 1.5rem;
        color: var(--text-primary);
        font-weight: 500;
    }}

    /* Alerta éxito */
    .alerta-success {{
        background-color: rgba(39, 174, 96, 0.08);
        border: 1px solid rgba(39, 174, 96, 0.3);
        border-left: 6px solid var(--accent);
        border-radius: 16px;
        padding: 1.5rem;
        color: var(--text-primary);
        font-weight: 500;
    }}

    /* Stepper de progreso */
    .stepper {{
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem 2rem;
        margin-bottom: 1.5rem;
        background: var(--bg-card);
        border-radius: 16px;
        border: 1px solid var(--border);
        box-shadow: 0 4px 15px var(--shadow);
    }}
    .stepper-step {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-weight: 500;
        font-size: 0.85rem;
        color: var(--text-secondary);
        transition: all 0.2s ease;
    }}
    .stepper-step.active {{
        background: var(--accent);
        color: white;
    }}
    .stepper-step.completed {{
        color: var(--accent);
    }}
    .stepper-arrow {{
        color: var(--text-secondary);
        margin: 0 0.5rem;
        font-size: 1.2rem;
    }}

    /* Sidebar branding */
    .sidebar-brand {{
        text-align: center;
        padding: 1rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1rem;
    }}
    .sidebar-brand h2 {{
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--accent);
        margin: 0;
    }}
    .sidebar-brand .version {{
        font-size: 0.75rem;
        color: var(--text-secondary);
    }}

    /* Theme toggle button */
    .theme-toggle {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 9999;
    }}

    /* Flow diagram */
    .flow-diagram {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
    }}
    .flow-node {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
        font-weight: 600;
        color: var(--text-primary);
        box-shadow: 0 2px 8px var(--shadow);
    }}
    .flow-arrow {{
        font-size: 1.5rem;
        color: var(--accent);
    }}

    /* Scenario history */
    .scenario-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.75rem 1rem;
        border-radius: 12px;
        border: 1px solid var(--border);
        margin: 0.5rem 0;
        background: var(--bg-card);
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    .scenario-item:hover {{
        border-color: var(--accent);
        transform: translateX(4px);
    }}
    .scenario-name {{
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.9rem;
    }}
    .scenario-date {{
        font-size: 0.75rem;
        color: var(--text-secondary);
    }}

    /* Soil indicator */
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

    /* Live preview card */
    .preview-card {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px var(--shadow);
    }}
    .preview-card h4 {{
        color: var(--accent);
        margin: 0 0 1rem;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .preview-row {{
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--border);
        font-size: 0.9rem;
    }}
    .preview-row:last-child {{ border-bottom: none; }}
    .preview-label {{ color: var(--text-secondary); }}
    .preview-value {{ color: var(--text-primary); font-weight: 600; }}

    /* Progress bar animada */
    .progress-stage {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        background: var(--bg-card);
        border: 1px solid var(--border);
    }}
    .progress-stage.active {{ border-color: var(--accent); }}
    .progress-stage.done {{ border-color: var(--accent); background: rgba(39, 174, 96, 0.08); }}
    .progress-icon {{ font-size: 1.2rem; }}
    .progress-label {{ font-weight: 500; color: var(--text-primary); font-size: 0.9rem; }}

    /* Radar container */
    .radar-container {{
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }}

    /* Insight header */
    .insight-header {{
        background: linear-gradient(135deg, rgba(39, 174, 96, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }}
    .insight-header h3 {{
        color: var(--text-primary);
        margin: 0 0 0.5rem;
    }}
    .insight-header p {{
        color: var(--text-secondary);
        margin: 0;
        line-height: 1.6;
    }}

    /* Barra lateral */
    [data-testid="stSidebar"] {{
        background-color: var(--bg-card);
        border-right: 1px solid var(--border);
    }}
    [data-testid="stSidebarNav"] {{
        padding-top: 1rem;
    }}

    /* Inputs y selects */
    input, select, textarea {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-color: var(--border) !important;
    }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        background: var(--bg-card);
        border-radius: 12px;
        border: 1px solid var(--border);
    }}
</style>
""", unsafe_allow_html=True)

# --- Theme toggle en sidebar ---
with st.sidebar:
    theme_icon = "🌙" if st.session_state["dark_mode"] else "☀️"
    theme_label = "Modo Claro" if st.session_state["dark_mode"] else "Modo Oscuro"
    if st.button(f"{theme_icon} {theme_label}", use_container_width=True, type="secondary", on_click=toggle_theme):
        st.rerun()

    st.markdown("""
    <div class="sidebar-brand">
        <h2>🏗️ EMCA</h2>
        <div class="version">v1.0.0 — Stochastic System</div>
        <div class="version">{date}</div>
    </div>
    """.format(date=datetime.now().strftime("%b %Y")), unsafe_allow_html=True)

# --- Configuración de Páginas ---
pg_home = st.Page("pages/00_home.py", title="Inicio", icon="🏠", default=True)
pg_param = st.Page("pages/01_parametrizacion.py", title="1. Parametrización", icon="📋")
pg_sim = st.Page("pages/02_simulacion.py", title="2. Simulación", icon="⚙️")
pg_dash = st.Page("pages/03_dashboard.py", title="3. Dashboard", icon="📊")

# --- Navegación ---
pg = st.navigation(
    {
        "Sistema EMCA": [pg_home],
        "Módulos": [pg_param, pg_sim, pg_dash]
    }
)

# Ejecutar
pg.run()

