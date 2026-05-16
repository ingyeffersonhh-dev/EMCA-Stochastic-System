"""
app/main.py
Entry point de la aplicación Streamlit — EMCA Sistema de Pilotes.
"""
import streamlit as st
import os
import sys

# --- Configuración de Rutas para Deploy ---
# Esto asegura que la carpeta 'core' sea visible desde cualquier módulo
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

st.set_page_config(
    page_title="EMCA — Planificación de Pilotes",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS personalizado Premium (Estilo Lumina/Logistics SaaS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Fondo principal muy sutil para dar contraste a las tarjetas */
    .stApp {
        background-color: var(--secondary-background-color);
    }

    /* Tarjetas de Navegación */
    .nav-card {
        background-color: var(--background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 0.5rem 0;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.03);
    }
    
    .nav-card:hover {
        transform: translateY(-4px);
        box-shadow: 0px 12px 24px rgba(0, 0, 0, 0.08);
        border-color: #27ae60;
    }

    .nav-card h3 {
        color: var(--text-color);
        margin-top: 0;
        font-weight: 700;
        font-size: 1.15rem;
    }
    .nav-card h4 {
        color: #2ecc71;
        font-size: 0.95rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .nav-card p {
        color: var(--text-color);
        opacity: 0.75;
        line-height: 1.6;
        font-size: 0.9rem;
    }

    /* Estilo de métricas (st.metric) unificado al diseño de tarjetas */
    div[data-testid="metric-container"] {
        background-color: var(--background-color);
        border: 1px solid rgba(128, 128, 128, 0.15);
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-left: 6px solid #2ecc71; /* Acento verde/azulado sutil */
    }
    div[data-testid="metric-container"] > div {
        color: var(--text-color);
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0px 8px 20px rgba(0,0,0,0.08);
    }

    /* Botones estilo SaaS (pills redondos y limpios) */
    .stButton > button {
        background: #27ae60;
        color: white;
        border: none;
        border-radius: 24px; /* Pill shape */
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(39, 174, 96, 0.25);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(39, 174, 96, 0.4);
        background: #2ecc71;
        color: white;
    }
    
    /* Pestañas (Tabs) estilo Segmented Control Lumina */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(128, 128, 128, 0.05);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        background-color: transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--background-color) !important;
        color: var(--text-color) !important;
        font-weight: 600;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
        border-bottom: none !important;
    }

    /* Títulos limpios */
    h1, h2 {
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Alerta logística roja rediseñada */
    .alerta-roja {
        background-color: rgba(239, 68, 68, 0.08);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-left: 6px solid #ef4444;
        border-radius: 16px;
        padding: 1.5rem;
        color: var(--text-color);
        font-weight: 500;
        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.05);
    }

    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: var(--background-color);
        border-right: 1px solid rgba(128, 128, 128, 0.1);
    }
    [data-testid="stSidebarNav"] {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Configuración de Páginas (st.navigation) ---
pg_home = st.Page("pages/00_home.py", title="Inicio", icon="🏠", default=True)
pg_param = st.Page("pages/01_parametrizacion.py", title="1. Parametrización Operativa", icon="📋")
pg_sim = st.Page("pages/02_simulacion.py", title="2. Motor de Simulación", icon="⚙️")
pg_dash = st.Page("pages/03_dashboard.py", title="3. Dashboard Gerencial", icon="📊")

# --- Construir navegación visual de la barra lateral ---
pg = st.navigation(
    {
        "Sistema EMCA": [pg_home],
        "Módulos": [pg_param, pg_sim, pg_dash]
    }
)

# Ejecutar el enrutador
pg.run()

