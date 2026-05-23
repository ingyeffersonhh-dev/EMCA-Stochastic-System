"""
app/pages/login.py
Módulo de Autenticación Corporativa — Formulario de Inicio de Sesión Premium.
"""
import streamlit as st
import json
import os
import sys

# Asegurar que la raíz esté en el path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.utils.auth import verify_password, create_jwt, inject_cookie_setter_js

# Ruta a la configuración de usuarios
CONFIG_PATH = os.path.join(ROOT_DIR, "config", "config_usuarios.json")

def cargar_usuarios() -> dict:
    """Carga los usuarios pre-configurados desde el archivo JSON."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error al cargar la base de usuarios: {e}")
        return {}

# ── Interfaz de Usuario ────────────────────────────────────────

# Ocultar menú lateral y pie de página predeterminado de Streamlit
st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none!important; }
        [data-testid="stHeader"] { display: none!important; }
    </style>
""", unsafe_allow_html=True)

# Centrar el contenedor del login en la pantalla
c1, c2, c3 = st.columns([1, 1.8, 1])

with c2:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    # Card Contenedor con efecto Glassmorphism y logo
    logo_svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 210 60" width="100%" height="70" style="margin-bottom: 1.5rem;">
      <defs>
        <linearGradient id="g_login" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#00E68A"/>
          <stop offset="100%" style="stop-color:#00CC7A"/>
        </linearGradient>
      </defs>
      <rect x="70" y="2" width="56" height="56" rx="14" fill="url(#g_login)" opacity=".12"/>
      <rect x="75" y="7" width="46" height="46" rx="10" fill="url(#g_login)"/>
      <text x="87" y="42" font-family="Inter,Arial" font-size="28" font-weight="800" fill="#0B0B0F">E</text>
    </svg>
    """
    st.markdown(logo_svg, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="margin: 0; font-size: 1.8rem; font-weight: 800; color: var(--tx1);">Acceso al Portal EMCA</h2>
            <p style="color: var(--tx2); margin-top: 0.4rem; font-size: 0.9rem;">
                Sistema Estocástico de Planificación y Simulación de Pilotes
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Formulario de credenciales
    with st.form("login_form", clear_on_submit=False):
        st.markdown('<div style="padding: 0.5rem 0;">', unsafe_allow_html=True)
        
        username = st.text_input("Usuario Corporativo", placeholder="ej. admin")
        password = st.text_input("Contraseña", type="password", placeholder="••••••••")
        
        col_chk, _ = st.columns([1.5, 1])
        with col_chk:
            remember_me = st.checkbox("Recordar sesión por 24 horas", value=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        submit_btn = st.form_submit_button("🔑 Iniciar Sesión", use_container_width=True)
        
    if submit_btn:
        if not username or not password:
            st.error("⚠️ Por favor, complete todos los campos.")
        else:
            usuarios = cargar_usuarios()
            if username in usuarios:
                user_data = usuarios[username]
                if verify_password(password, user_data["password_hash"], user_data["salt"]):
                    # Guardar estado en st.session_state
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["role"] = user_data["role"]
                    st.session_state["nombre_usuario"] = user_data["nombre"]
                    
                    # Generar JWT e inyectar en la cookie del navegador
                    payload = {"username": username, "role": user_data["role"], "nombre": user_data["nombre"]}
                    # Si recuerda sesión, 24 horas. Si no, se destruirá al cerrar navegador (max_age=0 o None se maneja con max_age=86400 si se recuerda).
                    max_age = 86400 if remember_me else 3600
                    token = create_jwt(payload, expires_in=max_age)
                    
                    # Inyectar JS para guardar la cookie
                    inject_cookie_setter_js(token, max_age=max_age)
                    
                    st.success("✅ Autenticación exitosa. Redirigiendo...")
                    # Forzar recarga para procesar navegación
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta. Inténtelo de nuevo.")
            else:
                st.error("❌ Usuario no registrado en el sistema corporativo.")
                
    # Footer decorativo de la card
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem; font-size: 0.78rem; color: var(--tx3);">
            EMCA stochastic system &copy; 2026. Todos los derechos reservados.
            <br>Acceso confidencial e intransferible.
        </div>
    """, unsafe_allow_html=True)
