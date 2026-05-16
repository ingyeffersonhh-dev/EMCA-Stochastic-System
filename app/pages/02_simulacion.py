"""
app/pages/02_simulacion.py
Módulo 2: Configuración y ejecución del motor de simulación estocástica.
"""
import streamlit as st
import time

from core.simulation.engine import ejecutar_simulacion

st.markdown("""
<style>
    .engine-banner {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.9) 0%, rgba(46, 109, 164, 0.9) 100%);
        backdrop-filter: blur(10px);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    }
    .engine-banner h2 { color: white; margin: 0; }
    .engine-banner p  { color: rgba(255,255,255,0.75); margin: 0.3rem 0 0; }
</style>
""", unsafe_allow_html=True)

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

# --- Mostrar resumen del escenario ---
with st.expander("📋 Resumen del escenario configurado", expanded=True):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Pilotes", params.cantidad_pilotes)
    c2.metric("Mixers", params.num_mixers)
    c3.metric("Distancia (km)", params.distancia_proveedor_km)
    c4.metric("Suelo", params.tipo_suelo.label if hasattr(params.tipo_suelo, 'label') else params.tipo_suelo)

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

st.caption(f"⏱️ Tiempo estimado de cómputo: **{n_replicas * params.cantidad_pilotes // 5000 + 1}–{n_replicas * params.cantidad_pilotes // 2000 + 3} segundos**")

# --- Ejecutar simulación ---
st.divider()
ejecutar = st.button("🚀 Ejecutar Simulación", use_container_width=True, type="primary")

if ejecutar:
    progress_bar = st.progress(0, text="Inicializando motor SimPy...")
    status = st.empty()

    with st.spinner(""):
        t0 = time.time()

        for pct in [10, 30, 60]:
            time.sleep(0.05)
            progress_bar.progress(pct, text=f"Generando variables aleatorias y ejecutando réplicas... {pct}%")

        resultado = ejecutar_simulacion(params, n_replicas=n_replicas, seed=int(seed))
        elapsed = time.time() - t0

        progress_bar.progress(100, text="✅ Simulación completada")
        time.sleep(0.3)
        progress_bar.empty()

    st.session_state["resultado"] = resultado
    st.success(f"✅ Simulación completada en **{elapsed:.1f} segundos** | {n_replicas} réplicas")

    # --- Resultados rápidos ---
    if resultado.kpis:
        k = resultado.kpis
        st.subheader("📊 Resultados Clave")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("⏱️ Duración P50", f"{k.tiempo_proyecto_p50_h:.1f} h",
                    delta=f"{k.dias_p50:.1f} días")
        col2.metric("📈 Duración P90", f"{k.tiempo_proyecto_p90_h:.1f} h")
        col3.metric("⚡ Cuello de botella", k.cuello_botella)
        col4.metric("🔧 Utilización Mixer", f"{k.utilizacion_mixer_pct:.0f}%",
                    delta="⚠️ Alta" if k.utilizacion_mixer_pct > 85 else "✅ Normal",
                    delta_color="inverse" if k.utilizacion_mixer_pct > 85 else "normal")

        if k.alerta_logistica:
            st.error(f"🚨 **ALERTA LOGÍSTICA**: Tiempo promedio de espera del mixer = "
                     f"**{k.tiempo_espera_mixer_promedio_h:.2f} h** (umbral: 2.0 h). "
                     f"Considere aumentar la flota o reducir la distancia al proveedor.")

        st.info("➡️ Vea el análisis completo en el **Módulo 3 — Dashboard**")
