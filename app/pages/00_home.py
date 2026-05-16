import streamlit as st

# --- Header ---
st.markdown("""
<div class="main-header">
    <h1>🏗️ EMCA — Sistema de Planificación de Pilotes</h1>
    <p>Sistema de Información Estocástico | Apoyo a la Toma de Decisiones Gerenciales</p>
</div>
""", unsafe_allow_html=True)

# --- Navegación visual ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="nav-card">
        <h3>📋 Módulo 1</h3>
        <h4>Parametrización Operativa</h4>
        <p>Ingrese las condiciones del proyecto: tipo de suelo, dimensiones del pilote,
        número de mixers y logística de transporte.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="nav-card">
        <h3>⚙️ Módulo 2</h3>
        <h4>Motor de Simulación</h4>
        <p>Ejecute la simulación Monte Carlo sobre el motor de eventos discretos (SimPy).
        Configure el número de réplicas y la semilla aleatoria.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="nav-card">
        <h3>📊 Módulo 3</h3>
        <h4>Panel de Control Gerencial</h4>
        <p>Visualice el cronograma Gantt, distribución de duraciones, KPIs,
        alertas logísticas y exporte resultados a Excel.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- Estado actual de la sesión ---
st.subheader("Estado de la Sesión")
col_a, col_b, col_c = st.columns(3)

parametros_ok = "parametros" in st.session_state
resultado_ok = "resultado" in st.session_state

col_a.metric("Parámetros", "✅ Configurados" if parametros_ok else "⬜ Pendiente")
col_b.metric("Simulación", "✅ Ejecutada" if resultado_ok else "⬜ Pendiente")
col_c.metric("Resultados", "✅ Listos" if resultado_ok else "⬜ Pendiente")

st.info("💡 Navegue por las páginas del menú lateral para completar el flujo: **Parametrización → Simulación → Dashboard**")
