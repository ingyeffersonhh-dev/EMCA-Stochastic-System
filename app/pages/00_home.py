"""
app/pages/00_home.py
Módulo Home: Página de bienvenida con navegación visual y estado de sesión.
"""
import streamlit as st
import os
import json
from datetime import datetime

st.title("🏗️ EMCA Control Tower")
st.caption("Sistema Estocástico para Planificación de Pilotes — Apoyo a la Toma de Decisiones")

# --- Stepper de progreso ---
parametros_ok = "parametros" in st.session_state
resultado_ok = "resultado" in st.session_state

steps = [
    ("1", "Parametrización", parametros_ok),
    ("2", "Simulación", resultado_ok),
    ("3", "Dashboard", resultado_ok),
]

stepper_html = '<div class="stepper">'
for i, (num, label, completed) in enumerate(steps):
    status = "completed" if completed else ("active" if (i == 0 and not parametros_ok) or (i == 1 and parametros_ok and not resultado_ok) or (i == 2 and resultado_ok) else "")
    if not status:
        status = ""
    icon = "✅" if completed else num
    stepper_html += f'<div class="stepper-step {status}"><span>{icon}</span><span>{label}</span></div>'
    if i < len(steps) - 1:
        stepper_html += '<span class="stepper-arrow">→</span>'
stepper_html += '</div>'
st.markdown(stepper_html, unsafe_allow_html=True)

# --- Flujo visual ---
st.markdown("""
<div class="flow-diagram">
    <div class="flow-node">📋 Configurar<br/><small>Parámetros</small></div>
    <span class="flow-arrow">→</span>
    <div class="flow-node">⚙️ Simular<br/><small>Monte Carlo</small></div>
    <span class="flow-arrow">→</span>
    <div class="flow-node">📊 Analizar<br/><small>Dashboard</small></div>
</div>
""", unsafe_allow_html=True)

# --- Cards navegables ---
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📋 Módulo 1 — Parametrización", use_container_width=True, type="primary" if not parametros_ok else "secondary"):
        st.switch_page("pages/01_parametrizacion.py")
    st.markdown("""
    <div class="nav-card" style="margin-top: 0.5rem;">
        <h4>Configuración del Proyecto</h4>
        <p>Ingrese dimensiones del pilote, tipo de suelo, número de mixers, distancia al proveedor y parámetros estocásticos de perforación y colado.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("⚙️ Módulo 2 — Simulación", use_container_width=True, type="primary" if (parametros_ok and not resultado_ok) else "secondary", disabled=not parametros_ok):
        st.switch_page("pages/02_simulacion.py")
    st.markdown("""
    <div class="nav-card" style="margin-top: 0.5rem;">
        <h4>Motor de Simulación</h4>
        <p>Ejecute réplicas Monte Carlo sobre el motor de eventos discretos (SimPy). Configure cantidad de réplicas y semilla aleatoria.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if st.button("📊 Módulo 3 — Dashboard", use_container_width=True, type="primary" if resultado_ok else "secondary", disabled=not resultado_ok):
        st.switch_page("pages/03_dashboard.py")
    st.markdown("""
    <div class="nav-card" style="margin-top: 0.5rem;">
        <h4>Panel Gerencial</h4>
        <p>Visualice cronograma Gantt, distribución de duraciones, KPIs, alertas logísticas y exporte resultados a Excel.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- Estado actual de la sesión ---
st.subheader("📌 Estado de la Sesión")
col_a, col_b, col_c = st.columns(3)

col_a.metric("Parámetros", "✅ Configurados" if parametros_ok else "⬜ Pendiente")
col_b.metric("Simulación", "✅ Ejecutada" if resultado_ok else "⬜ Pendiente")
col_c.metric("Resultados", "✅ Listos" if resultado_ok else "⬜ Pendiente")

# --- Escenarios recientes ---
st.divider()
st.subheader("📂 Escenarios Guardados")

scenarios_dir = "data/scenarios"
os.makedirs(scenarios_dir, exist_ok=True)
archivos = [f for f in os.listdir(scenarios_dir) if f.endswith(".json")]

if archivos:
    archivos.sort(key=lambda x: os.path.getmtime(os.path.join(scenarios_dir, x)), reverse=True)
    
    c1, c2 = st.columns([2, 1])
    with c1:
        for archivo in archivos[:5]:
            filepath = os.path.join(scenarios_dir, archivo)
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%d/%m/%Y %H:%M")
            try:
                with open(filepath, encoding="utf-8") as f:
                    datos = json.load(f)
                nombre = datos.get("nombre_escenario", archivo.replace(".json", ""))
                pilotes = datos.get("cantidad_pilotes", "?")
                mixers = datos.get("num_mixers", "?")
            except:
                nombre = archivo.replace(".json", "")
                pilotes = "?"
                mixers = "?"
            
            st.markdown(f"""
            <div class="scenario-item">
                <div>
                    <div class="scenario-name">{nombre}</div>
                    <div class="scenario-date">{pilotes} pilotes · {mixers} mixers</div>
                </div>
                <div class="scenario-date">{mtime}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="preview-card">
            <h4>Resumen</h4>
            <div class="preview-row">
                <span class="preview-label">Total escenarios</span>
                <span class="preview-value">{len(archivos)}</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Última modificación</span>
                <span class="preview-value">{archivos[0]}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No hay escenarios guardados. Comience en el **Módulo 1** para crear uno.")

st.divider()
st.info("💡 Navegue por los módulos en orden: **Parametrización → Simulación → Dashboard**")
