"""
app/pages/02_simulacion.py
Módulo 2: Configuración y ejecución del motor de simulación estocástica.
Con barra de progreso animada, métricas en tiempo real y mini preview.
"""
import streamlit as st
import time
import math

from core.simulation.engine import ejecutar_simulacion

# --- Stepper ---
parametros_ok = "parametros" in st.session_state
resultado_ok = "resultado" in st.session_state
stepper_html = '<div class="stepper">'
steps = [
    ("1", "Parametrización", True),
    ("2", "Simulación", True),
    ("3", "Dashboard", resultado_ok),
]
for i, (num, label, completed) in enumerate(steps):
    status = "completed" if completed else ("active" if i == 1 else "")
    icon = "✅" if completed else num
    stepper_html += f'<div class="stepper-step {status}"><span>{icon}</span><span>{label}</span></div>'
    if i < len(steps) - 1:
        stepper_html += '<span class="stepper-arrow">→</span>'
stepper_html += '</div>'
st.markdown(stepper_html, unsafe_allow_html=True)

st.markdown("""
<div class="engine-banner">
    <h2>⚙️ Módulo 2 — Motor de Simulación Estocástica</h2>
    <p>SimPy · Monte Carlo · Teoría de Colas</p>
</div>
""", unsafe_allow_html=True)

# --- Verificar pre-condición ---
if "parametros" not in st.session_state:
    st.warning("⚠️ Primero complete la **Parametrización** en el Módulo 1.")
    st.stop()

params = st.session_state["parametros"]

# --- Resumen del escenario ---
with st.expander("📋 Resumen del escenario configurado", expanded=True):
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Pilotes", params.cantidad_pilotes)
    c2.metric("Mixers", params.num_mixers)
    c3.metric("Distancia (km)", params.distancia_proveedor_km)
    c4.metric("Suelo", params.tipo_suelo.label if hasattr(params.tipo_suelo, 'label') else params.tipo_suelo)
    
    vol_total = math.pi * (params.diametro_m / 2) ** 2 * params.longitud_m * params.cantidad_pilotes
    c5.metric("Vol. total", f"{vol_total:.1f} m³")

# --- Estimación de tiempos ---
t_transporte = (params.distancia_proveedor_km * 2) / params.velocidad_transporte_kmh
t_perf_ajustado = params.tiempo_perforacion_ajustado_media
t_estimado_pilote = t_perf_ajustado + params.tiempo_colado_h_media + t_transporte / params.num_mixers
t_total_estimado = t_estimado_pilote * params.cantidad_pilotes

# Mini preview de resultados esperados
st.markdown(f"""
<div class="preview-card">
    <h4>📊 Estimación Preliminar</h4>
    <div class="preview-row">
        <span class="preview-label">Tiempo estimado por pilote</span>
        <span class="preview-value">{t_estimado_pilote:.2f} h</span>
    </div>
    <div class="preview-row">
        <span class="preview-label">Duración total estimada</span>
        <span class="preview-value">{t_total_estimado:.1f} h ({t_total_estimado/24:.1f} días)</span>
    </div>
    <div class="preview-row">
        <span class="preview-label">Tiempo transporte (ida/vuelta)</span>
        <span class="preview-value">{t_transporte:.2f} h</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Configuración de la simulación ---
st.subheader("⚙️ Configuración del Motor")
col_a, col_b = st.columns(2)
with col_a:
    n_replicas = st.slider(
        "Número de réplicas Monte Carlo",
        min_value=100, max_value=2000, value=500, step=100,
        help="Mayor número → más precisión estadística, mayor tiempo de cómputo"
    )
with col_b:
    seed = st.number_input(
        "Semilla aleatoria (reproducibilidad)",
        min_value=0, max_value=99999, value=42,
        help="Misma semilla → mismos resultados exactos"
    )

t_est_computo = n_replicas * params.cantidad_pilotes // 5000 + 1
st.caption(f"⏱️ Tiempo estimado de cómputo: **{t_est_computo}–{t_est_computo + 2} segundos**")

# --- Ejecutar simulación ---
st.divider()
ejecutar = st.button("🚀 Ejecutar Simulación", use_container_width=True, type="primary")

if ejecutar:
    # Etapas de progreso
    stages_container = st.empty()
    
    stages = [
        ("🔢", "Generando variables aleatorias...", False),
        ("⚙️", "Ejecutando motor SimPy...", False),
        ("📊", "Calculando KPIs y estadísticas...", False),
        ("✅", "Simulación completada", False),
    ]
    
    def render_stages(stages):
        html = ""
        for icon, label, done in stages:
            cls = "done" if done else ("active" if not done and any(not d for _, _, d in stages) and stages.index((icon, label, done)) == next((i for i, (_, _, d) in enumerate(stages) if not d), 0)) else ""
            html += f'<div class="progress-stage {cls}"><span class="progress-icon">{icon}</span><span class="progress-label">{label}</span></div>'
        stages_container.markdown(html, unsafe_allow_html=True)
    
    render_stages(stages)
    time.sleep(0.3)
    
    with st.spinner(""):
        t0 = time.time()
        
        # Stage 1
        stages[0] = ("🔢", "Generando variables aleatorias...", True)
        render_stages(stages)
        time.sleep(0.1)
        
        # Stage 2
        stages[1] = ("⚙️", "Ejecutando motor SimPy...", True)
        render_stages(stages)
        
        resultado = ejecutar_simulacion(params, n_replicas=n_replicas, seed=int(seed))
        
        elapsed = time.time() - t0
        
        # Stage 3
        stages[2] = ("📊", "Calculando KPIs y estadísticas...", True)
        render_stages(stages)
        time.sleep(0.1)
        
        # Stage 4
        stages[3] = ("✅", f"Simulación completada en {elapsed:.1f}s", True)
        render_stages(stages)

    st.session_state["resultado"] = resultado

    # --- Resultados rápidos ---
    if resultado.kpis:
        k = resultado.kpis
        st.subheader("📊 Resultados Clave")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⏱️ Duración P50", f"{k.tiempo_proyecto_p50_h:.1f} h",
                    delta=f"{k.dias_p50:.1f} días")
        col2.metric("📈 Duración P90", f"{k.tiempo_proyecto_p90_h:.1f} h",
                    delta=f"+{k.tiempo_proyecto_p90_h - k.tiempo_proyecto_p50_h:.1f}h vs P50")
        col3.metric("⚡ Cuello de botella", k.cuello_botella)
        col4.metric("🔧 Utilización Mixer", f"{k.utilizacion_mixer_pct:.0f}%",
                    delta="⚠️ Alta" if k.utilizacion_mixer_pct > 85 else "✅ Normal",
                    delta_color="inverse" if k.utilizacion_mixer_pct > 85 else "normal")

        if k.alerta_logistica:
            st.markdown(f"""
            <div class="alerta-roja">
                🚨 <strong>ALERTA LOGÍSTICA</strong>: Tiempo promedio de espera del mixer = 
                <strong>{k.tiempo_espera_mixer_promedio_h:.2f} h</strong> (umbral: 2.0 h). 
                Considere aumentar la flota o reducir la distancia al proveedor.
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="alerta-info">
            ➡️ Vea el análisis completo en el <strong>Módulo 3 — Dashboard</strong>
        </div>
        """, unsafe_allow_html=True)
