"""
app/pages/02_simulacion.py
Módulo 2: Configuración y ejecución del motor de simulación estocástica.
Premium dark theme layout.
"""
import streamlit as st
import time
import math

from core.simulation.engine import ejecutar_simulacion

st.markdown("""
<div style="margin-bottom:1.5rem">
    <h1 style="margin:0;font-size:1.8rem;font-weight:800">⚙️ Motor Estocástico</h1>
    <p style="color:#8892B0;margin:.2rem 0 0;font-size:.92rem">
        Configuración y ejecución de la simulación de Monte Carlo (SimPy)
    </p>
</div>
""", unsafe_allow_html=True)

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


# --- Verificar pre-condición ---
if "parametros" not in st.session_state:
    st.markdown('<div class="alerta-roja">⚠️ Primero complete la <strong>Parametrización</strong> en el Módulo 1.</div>', unsafe_allow_html=True)
    st.stop()

params = st.session_state["parametros"]

# --- Resumen del escenario ---
with st.expander("📋 Resumen del escenario configurado", expanded=True):
    vol_total = math.pi * (params.diametro_m / 2) ** 2 * params.longitud_m * params.cantidad_pilotes
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card" style="padding:1rem">
            <div class="kpi-label">Pilotes</div>
            <div class="kpi-value" style="font-size:1.4rem">{params.cantidad_pilotes}</div>
        </div>
        <div class="kpi-card" style="padding:1rem">
            <div class="kpi-label">Mixers</div>
            <div class="kpi-value" style="font-size:1.4rem">{params.num_mixers}</div>
        </div>
        <div class="kpi-card" style="padding:1rem">
            <div class="kpi-label">Distancia</div>
            <div class="kpi-value" style="font-size:1.4rem">{params.distancia_proveedor_km} km</div>
        </div>
        <div class="kpi-card" style="padding:1rem">
            <div class="kpi-label">Suelo</div>
            <div class="kpi-value" style="font-size:1.4rem">{params.tipo_suelo.label}</div>
        </div>
        <div class="kpi-card kpi-accent-cyan" style="padding:1rem">
            <div class="kpi-label">Vol. Total</div>
            <div class="kpi-value" style="font-size:1.4rem">{vol_total:.1f} m³</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Estimación de tiempos ---
horas_dia = params.horas_por_dia
t_transporte = params.tiempo_transporte_h
t_perf_ajustado = params.tiempo_perforacion_ajustado_media
t_colado = params.tiempo_colado_h_media
t_estimado_pilote = t_perf_ajustado + t_colado + t_transporte / params.num_mixers
t_total_estimado = t_estimado_pilote * params.cantidad_pilotes
dias_estimados = t_total_estimado / horas_dia

# Mini preview de resultados esperados
st.markdown(f"""
<div class="preview-card" style="margin-top:1.5rem">
    <h4>📊 Estimación Preliminar Teórica</h4>
    <div class="preview-row">
        <span class="preview-label">Tiempo por pilote (promedio)</span>
        <span class="preview-value">{t_estimado_pilote:.2f} h ({t_estimado_pilote*60:.0f} min)</span>
    </div>
    <div class="preview-row">
        <span class="preview-label">Duración total estimada</span>
        <span class="preview-value">{t_total_estimado:.1f} h ({dias_estimados:.1f} días de {horas_dia:.0f}h)</span>
    </div>
    <div class="preview-row">
        <span class="preview-label">Ciclo de Transporte (ida/vuelta)</span>
        <span class="preview-value">{t_transporte:.2f} h</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Configuración de la simulación ---
st.markdown('<div class="section-title"><h3>⚙️ Configuración del Motor</h3></div>', unsafe_allow_html=True)
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
st.markdown("<br>", unsafe_allow_html=True)
ejecutar = st.button("🚀 Iniciar Simulación Estocástica", use_container_width=True, type="primary")

if ejecutar:
    stages_container = st.empty()
    
    stages = [
        ("🔢", "Generando variables aleatorias...", False),
        ("⚙️", "Ejecutando motor SimPy...", False),
        ("📊", "Calculando KPIs y estadísticas...", False),
        ("✅", "Simulación completada", False),
    ]
    
    def render_stages(stages):
        html = ""
        first_incomplete = next((i for i, (_, _, d) in enumerate(stages) if not d), len(stages))
        for idx, (icon, label, done) in enumerate(stages):
            if done:
                cls = "done"
            elif idx == first_incomplete:
                cls = "active"
            else:
                cls = ""
            html += f'<div class="progress-stage {cls}"><span class="progress-icon">{icon}</span><span class="progress-label">{label}</span></div>'
        stages_container.markdown(html, unsafe_allow_html=True)
    
    render_stages(stages)
    time.sleep(0.3)
    
    with st.spinner(""):
        t0 = time.time()
        
        stages[0] = ("🔢", "Generando variables aleatorias...", True)
        render_stages(stages)
        time.sleep(0.1)
        
        stages[1] = ("⚙️", "Ejecutando motor SimPy...", True)
        render_stages(stages)
        
        resultado = ejecutar_simulacion(params, n_replicas=n_replicas, seed=int(seed))
        
        elapsed = time.time() - t0
        
        stages[2] = ("📊", "Calculando KPIs y estadísticas...", True)
        render_stages(stages)
        time.sleep(0.1)
        
        stages[3] = ("✅", f"Simulación completada en {elapsed:.1f}s", True)
        render_stages(stages)

    st.session_state["resultado"] = resultado

    # --- Auto-guardar el escenario con resultados ---
    try:
        import os
        import json
        import dataclasses
        scenarios_dir = "data/scenarios"
        os.makedirs(scenarios_dir, exist_ok=True)
        nombre_esc = params.nombre_escenario
        nombre_archivo = f"{nombre_esc.replace(' ', '_')}.json"
        
        data_to_save = {
            "parametros": params.model_dump(mode="json"),
            "resultado": dataclasses.asdict(resultado)
        }
        with open(os.path.join(scenarios_dir, nombre_archivo), "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)
        st.toast(f"💾 Escenario '{nombre_esc}' auto-guardado con resultados.", icon="✅")
    except Exception as e:
        st.warning(f"No se pudo auto-guardar el escenario: {e}")

    # --- Resultados rápidos ---
    if resultado.kpis:
        k = resultado.kpis
        st.markdown('<div class="section-title" style="margin-top:2rem"><h3>📊 Resultados Clave</h3></div>', unsafe_allow_html=True)
        
        util_color = "kpi-accent-purple" if k.utilizacion_mixer_pct <= 85 else "kpi-accent-red"
        
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Duración P50</div>
                <div class="kpi-value">{k.tiempo_proyecto_p50_h:.1f} h</div>
                <div style="color:#A0AEC0;font-size:0.8rem;margin-top:0.2rem">{k.tiempo_proyecto_p50_h/horas_dia:.1f} días</div>
            </div>
            <div class="kpi-card kpi-accent-cyan">
                <div class="kpi-label">Duración P90</div>
                <div class="kpi-value">{k.tiempo_proyecto_p90_h:.1f} h</div>
                <div style="color:#A0AEC0;font-size:0.8rem;margin-top:0.2rem">{k.tiempo_proyecto_p90_h/horas_dia:.1f} días</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Cuello de botella</div>
                <div class="kpi-value" style="font-size:1.2rem;margin-top:0.4rem">{k.cuello_botella}</div>
            </div>
            <div class="kpi-card {util_color}">
                <div class="kpi-label">Utilización Mixer</div>
                <div class="kpi-value">{k.utilizacion_mixer_pct:.0f}%</div>
                <div style="color:#A0AEC0;font-size:0.8rem;margin-top:0.2rem">{'⚠️ Alta' if k.utilizacion_mixer_pct > 85 else '✅ Normal'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if k.alerta_logistica:
            st.markdown(f"""
            <div class="alerta-roja" style="margin-top:1.5rem">
                🚨 <strong>ALERTA LOGÍSTICA</strong>: Tiempo promedio de espera del mixer = 
                <strong>{k.tiempo_espera_mixer_promedio_h:.2f} h</strong> (umbral: 2.0 h). 
                Considere aumentar la flota o reducir la distancia al proveedor.
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="alerta-info" style="margin-top:1.5rem">
            ➡️ Vea el análisis completo en el <strong>Módulo 3 — Dashboard</strong>
        </div>
        """, unsafe_allow_html=True)
