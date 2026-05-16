"""
app/main.py
Entry point de la aplicación Streamlit — EMCA Sistema de Pilotes.
"""
import streamlit as st

st.set_page_config(
    page_title="EMCA — Planificación de Pilotes",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS personalizado Premium (Soporte Light/Dark Mode) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Header Principal Glassmorphism */
    .main-header {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.9) 0%, rgba(46, 109, 164, 0.9) 100%);
        backdrop-filter: blur(10px);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2.5rem;
        color: white;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .main-header h1 { 
        color: white; 
        margin: 0; 
        font-size: 2.5rem; 
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    .main-header p  { 
        color: rgba(255,255,255,0.85); 
        margin: 0.8rem 0 0; 
        font-size: 1.1rem; 
        font-weight: 300;
    }

    /* Tarjetas de Navegación (Adaptables al Tema) */
    .nav-card {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 16px;
        padding: 1.8rem;
        margin: 0.5rem 0;
        height: 100%;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .nav-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.15);
        border-color: #3b82f6;
    }

    .nav-card h3 {
        color: var(--text-color);
        margin-top: 0;
        font-weight: 600;
    }
    .nav-card h4 {
        color: #3b82f6;
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    .nav-card p {
        color: var(--text-color);
        opacity: 0.8;
        line-height: 1.6;
        font-size: 0.95rem;
    }

    /* Botones Premium */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        letter-spacing: 0.3px;
        padding: 0.6rem 1.5rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
    }
    
    /* Pestañas (Tabs) estilizdas (Adaptables) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        background-color: transparent;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--secondary-background-color) !important;
        border-bottom: 2px solid #2563eb !important;
        color: var(--text-color) !important;
        font-weight: 600;
    }

    /* Barra Lateral Premium */
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2);
        box-shadow: 2px 0 10px rgba(0,0,0,0.05);
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

