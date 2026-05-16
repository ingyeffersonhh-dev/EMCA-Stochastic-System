"""
app/pages/03_dashboard.py
Módulo 3: Panel de Control Gerencial — Visualización completa de resultados.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from core.analytics.kpis import resumen_estadistico, tabla_eventos_df, distribucion_tiempos_df
from core.analytics.gantt import generar_gantt_df, generar_curva_s
from core.analytics.exportar import exportar_excel

st.markdown("""
<style>
    /* Tarjetas KPI nativas de Streamlit (st.metric) */
    div[data-testid="metric-container"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 1.2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        border-left: 5px solid #3b82f6;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.15);
    }

    .alerta-roja {
        background-color: rgba(239, 68, 68, 0.1);
        border: 1px solid #ef4444;
        border-left: 5px solid #ef4444;
        border-radius: 12px;
        padding: 1.2rem;
        color: var(--text-color);
        font-weight: 500;
        box-shadow: 0 4px 6px rgba(239, 68, 68, 0.05);
    }
    
    .dash-title {
        background: linear-gradient(135deg, rgba(30, 58, 95, 0.9) 0%, rgba(46, 109, 164, 0.9) 100%);
        backdrop-filter: blur(10px);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(30, 58, 95, 0.15);
    }
    .dash-title h2 { color: white; margin: 0; font-weight: 700; letter-spacing: -0.5px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="dash-title">
    <h2>📊 Módulo 3 — Panel de Control Gerencial</h2>
</div>
""", unsafe_allow_html=True)

# --- Pre-condición ---
if "resultado" not in st.session_state:
    st.warning("⚠️ Ejecute primero la simulación en el **Módulo 2**.")
    st.stop()

resultado = st.session_state["resultado"]
params = st.session_state.get("parametros")
kpis = resultado.kpis

if kpis is None:
    st.error("No hay KPIs disponibles. Vuelva a ejecutar la simulación.")
    st.stop()

# ===========================================================================
# SECCIÓN 1: KPI Cards
# ===========================================================================
st.subheader("📌 Indicadores Clave del Proyecto")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("⏱️ Duración P10", f"{kpis.tiempo_proyecto_p10_h:.1f} h", help="Escenario optimista (10% de probabilidad de terminar antes)")
col2.metric("📊 Duración P50", f"{kpis.tiempo_proyecto_p50_h:.1f} h", help="Mediana — estimación central")
col3.metric("📈 Duración P90", f"{kpis.tiempo_proyecto_p90_h:.1f} h", help="Escenario conservador (90% de confianza)")
col4.metric("📅 Duración P50", f"{kpis.dias_p50:.1f} días", delta=f"{kpis.semanas_p50:.1f} semanas")
col5.metric("🔧 Utilización Mixer", f"{kpis.utilizacion_mixer_pct:.0f}%")

col6, col7, col8 = st.columns(3)
col6.metric("🔄 Ciclo promedio/pilote", f"{kpis.tiempo_ciclo_promedio_h:.2f} h")
col7.metric("⏳ Espera mixer promedio", f"{kpis.tiempo_espera_mixer_promedio_h:.2f} h")
col8.metric("⚡ Cuello de botella", kpis.cuello_botella)

# Alertas
if kpis.alerta_logistica or kpis.alerta_capacidad_mixer:
    st.markdown("<br>", unsafe_allow_html=True)
    if kpis.alerta_logistica:
        st.markdown(f"""<div class="alerta-roja">
            🚨 ALERTA LOGÍSTICA: Espera promedio del mixer = {kpis.tiempo_espera_mixer_promedio_h:.2f}h
            (máx: {kpis.tiempo_espera_mixer_max_h:.2f}h). Umbral crítico: 2.0h.
            Recomendación: Aumentar flota de mixers o contratar proveedor más cercano.
        </div>""", unsafe_allow_html=True)
    if kpis.alerta_capacidad_mixer:
        st.markdown(f"""<div class="alerta-roja" style="margin-top:0.5rem">
            ⚠️ ALTA UTILIZACIÓN DE MIXER: {kpis.utilizacion_mixer_pct:.0f}% (umbral: 85%).
            El sistema de suministro de concreto está saturado.
        </div>""", unsafe_allow_html=True)

st.divider()

# ===========================================================================
# SECCIÓN 2: Distribución de duración del proyecto
# ===========================================================================
st.subheader("📊 Distribución de la Duración del Proyecto (Monte Carlo)")

tiempos = resultado.tiempos_proyecto_todas_replicas
if tiempos:
    arr = np.array(tiempos)
    fig_hist = go.Figure()

    fig_hist.add_trace(go.Histogram(
        x=arr, nbinsx=40, name="Réplicas",
        marker_color="#2E6DA4", opacity=0.75,
        hovertemplate="Duración: %{x:.1f}h<br>Frecuencia: %{y}<extra></extra>"
    ))

    for pct, color, label in [
        (kpis.tiempo_proyecto_p10_h, "#27AE60", "P10"),
        (kpis.tiempo_proyecto_p50_h, "#F39C12", "P50 (mediana)"),
        (kpis.tiempo_proyecto_p90_h, "#E74C3C", "P90"),
    ]:
        fig_hist.add_vline(x=pct, line_dash="dash", line_color=color,
                           annotation_text=f"{label}: {pct:.1f}h",
                           annotation_position="top")

    fig_hist.update_layout(
        xaxis_title="Duración del proyecto (h)",
        yaxis_title="Frecuencia",
        plot_bgcolor="white",
        height=380,
        showlegend=False,
        margin=dict(t=40, b=40),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ===========================================================================
# SECCIÓN 3: Gantt
# ===========================================================================
st.subheader("📅 Cronograma Proyectado — Gantt (Réplica Base)")

fecha_inicio = st.date_input("Fecha de inicio del proyecto", value=None,
                              help="Seleccione la fecha real de inicio para el cronograma")
hora_str = f"{fecha_inicio} 07:00:00" if fecha_inicio else "2025-01-06 07:00:00"

gantt_df = generar_gantt_df(resultado.eventos_replica_base, hora_inicio_proyecto=hora_str)

if not gantt_df.empty:
    COLOR_MAP = {
        "🔩 Perforación": "#1E3A5F",
        "⏳ Espera Mixer": "#E74C3C",
        "🪣 Colado": "#27AE60",
    }
    fig_gantt = px.timeline(
        gantt_df, x_start="Inicio", x_end="Fin",
        y="Pilote", color="Fase",
        color_discrete_map=COLOR_MAP,
        hover_data=["Duración_h"],
        labels={"Duración_h": "Duración (h)"},
    )
    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.update_layout(
        height=max(400, len(gantt_df["Pilote"].unique()) * 28 + 80),
        plot_bgcolor="white",
        margin=dict(t=40, b=40),
        legend_title="Fase",
    )
    st.plotly_chart(fig_gantt, use_container_width=True)

st.divider()

# ===========================================================================
# SECCIÓN 4: Curva S de avance
# ===========================================================================
st.subheader("📈 Curva S — Avance Acumulado del Proyecto")

curva_df = generar_curva_s(resultado.eventos_replica_base)
if not curva_df.empty:
    fig_s = px.area(
        curva_df, x="tiempo_h", y="avance_pct",
        labels={"tiempo_h": "Tiempo (h)", "avance_pct": "Pilotes completados (%)"},
        color_discrete_sequence=["#2E6DA4"],
    )
    fig_s.update_layout(
        plot_bgcolor="white", height=300,
        margin=dict(t=20, b=40),
        yaxis=dict(range=[0, 105]),
    )
    st.plotly_chart(fig_s, use_container_width=True)

st.divider()

# ===========================================================================
# SECCIÓN 5: Tabla de detalle
# ===========================================================================
with st.expander("🗂️ Tabla de Detalle por Pilote (réplica base)", expanded=False):
    df_tabla = tabla_eventos_df(resultado.eventos_replica_base)
    if not df_tabla.empty:
        st.dataframe(
            df_tabla.rename(columns={
                "pilote_id": "Pilote",
                "tiempo_perforacion_h": "Perf. (h)",
                "tiempo_espera_mixer_h": "Espera Mixer (h)",
                "tiempo_colado_h": "Colado (h)",
                "tiempo_ciclo_total_h": "Ciclo Total (h)",
            })[[
                "Pilote", "Perf. (h)", "Espera Mixer (h)", "Colado (h)", "Ciclo Total (h)"
            ]].style.background_gradient(
                subset=["Espera Mixer (h)"], cmap="RdYlGn_r"
            ).format("{:.2f}", subset=["Perf. (h)", "Espera Mixer (h)", "Colado (h)", "Ciclo Total (h)"]),
            use_container_width=True,
        )

st.divider()

# ===========================================================================
# SECCIÓN 6: Exportar a Excel
# ===========================================================================
st.subheader("📥 Exportar Resultados")
if st.button("📊 Descargar Reporte Excel", use_container_width=True, type="secondary"):
    with st.spinner("Generando Excel..."):
        ruta = exportar_excel(resultado, directorio="exports")
    with open(ruta, "rb") as f:
        st.download_button(
            label="⬇️ Descargar archivo Excel",
            data=f.read(),
            file_name=ruta.split("\\")[-1].split("/")[-1],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    st.success(f"✅ Reporte generado: `{ruta}`")
