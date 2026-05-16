"""
app/pages/03_dashboard.py
Módulo 3: Panel de Control Gerencial — Visualización completa de resultados.
Con insights automáticos, radar chart, tabla con filtros, gráfico de tornado y comparador.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import json
import os

from core.analytics.kpis import resumen_estadistico, tabla_eventos_df, distribucion_tiempos_df
from core.analytics.gantt import generar_gantt_df, generar_curva_s
from core.analytics.exportar import exportar_excel

st.title("📊 Panel de Control Gerencial")
st.caption("Visión analítica del desempeño del sistema logístico y de construcción.")

# --- Stepper ---
resultado_ok = "resultado" in st.session_state
stepper_html = '<div class="stepper">'
steps = [
    ("1", "Parametrización", True),
    ("2", "Simulación", True),
    ("3", "Dashboard", True),
]
for i, (num, label, completed) in enumerate(steps):
    status = "completed" if completed else ("active" if i == 2 else "")
    icon = "✅" if completed else num
    stepper_html += f'<div class="stepper-step {status}"><span>{icon}</span><span>{label}</span></div>'
    if i < len(steps) - 1:
        stepper_html += '<span class="stepper-arrow">→</span>'
stepper_html += '</div>'
st.markdown(stepper_html, unsafe_allow_html=True)

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
# SECCIÓN 0: Resumen rápido
# ===========================================================================
horas_dia = params.horas_por_dia if params and hasattr(params, 'horas_por_dia') else 8.0
dias_p50 = kpis.tiempo_proyecto_p50_h / horas_dia
dias_p90 = kpis.tiempo_proyecto_p90_h / horas_dia

# KPI Cards principales en una fila
col1, col2, col3, col4 = st.columns(4)
col1.metric("⏱️ Duración P50", f"{kpis.tiempo_proyecto_p50_h:.1f} h", f"{dias_p50:.1f} días")
col2.metric("📈 Duración P90", f"{kpis.tiempo_proyecto_p90_h:.1f} h", f"{dias_p90:.1f} días")
col3.metric("🔧 Utilización Mixer", f"{kpis.utilizacion_mixer_pct:.0f}%")
col4.metric("⚡ Cuello de botella", kpis.cuello_botella)

# Alertas compactas
if kpis.alerta_logistica:
    st.error(f"🚨 **Alerta logística**: Espera mixer promedio = {kpis.tiempo_espera_mixer_promedio_h:.2f}h (>2.0h). Considere aumentar flota.")
if kpis.alerta_capacidad_mixer:
    st.warning(f"⚠️ **Alta utilización mixer**: {kpis.utilizacion_mixer_pct:.0f}% (>85%). Sistema cerca de saturación.")

st.divider()

# ===========================================================================
# SECCIÓN 2: Distribución de duración del proyecto
# ===========================================================================
st.subheader("📊 Distribución de la Duración del Proyecto (Monte Carlo)")

tiempos = resultado.tiempos_proyecto_todas_replicas
if tiempos:
    arr = np.array(tiempos)
    df_tiempos = pd.DataFrame({"Duración": arr})
    fig_hist = px.histogram(
        df_tiempos, x="Duración", nbins=40,
        marginal="box",
        color_discrete_sequence=["#3b82f6"],
    )
    fig_hist.update_traces(opacity=0.85, marker_line_width=0, selector=dict(type="histogram"))
    fig_hist.update_traces(fillcolor="rgba(59, 130, 246, 0.2)", line_color="#3b82f6", selector=dict(type="box"))

    for pct, color, label in [
        (kpis.tiempo_proyecto_p10_h, "#2ecc71", "P10"),
        (kpis.tiempo_proyecto_p50_h, "#f39c12", "P50 (Mediana)"),
        (kpis.tiempo_proyecto_p90_h, "#ef4444", "P90"),
    ]:
        fig_hist.add_vline(
            x=pct, line_dash="dash", line_color=color, line_width=2,
            annotation_text=f"<b>{label}</b><br>{pct:.1f}h",
            annotation_position="top right",
            annotation_font=dict(color=color, size=11),
            annotation_bgcolor="rgba(128,128,128,0.1)"
        )

    fig_hist.update_layout(
        xaxis_title="Duración del proyecto (h)",
        yaxis_title="Frecuencia",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=400,
        showlegend=False,
        margin=dict(t=40, b=40, l=40, r=40),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)"),
        font=dict(family="Inter, sans-serif")
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
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=40),
        legend_title="Fase",
        xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.2)"),
        font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_gantt, use_container_width=True)

st.divider()

# ===========================================================================
# SECCIÓN 4: Curva S de avance
# ===========================================================================
st.subheader("📈 Curva S — Avance Acumulado del Proyecto")

curva_df = generar_curva_s(resultado.eventos_replica_base)
if not curva_df.empty:
    fig_s = px.line(
        curva_df, x="tiempo_h", y="avance_pct",
        labels={"tiempo_h": "Tiempo (h)", "avance_pct": "Pilotes completados (%)"},
        color_discrete_sequence=["#3b82f6"],
    )
    fig_s.update_traces(fill="tozeroy", fillcolor="rgba(59, 130, 246, 0.2)", line=dict(width=3))
    fig_s.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=300,
        margin=dict(t=20, b=40),
        yaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(128,128,128,0.2)"),
        xaxis=dict(showgrid=False),
        font=dict(family="Inter, sans-serif")
    )
    st.plotly_chart(fig_s, use_container_width=True)

st.divider()

# ===========================================================================
# SECCIÓN 5: Radar + Tornado (lado a lado)
# ===========================================================================
col_radar, col_tornado = st.columns(2)

with col_radar:
    st.subheader("🎯 Radar de Eficiencia")
    t_perf_total = sum(e.tiempo_perforacion_h for e in resultado.eventos_replica_base)
    t_colado_total = sum(e.tiempo_colado_h for e in resultado.eventos_replica_base)
    t_espera_total = sum(e.tiempo_espera_mixer_h for e in resultado.eventos_replica_base)
    t_ciclo_total = t_perf_total + t_colado_total + t_espera_total

    eficiencia_perf = (t_perf_total / t_ciclo_total * 100) if t_ciclo_total > 0 else 0
    eficiencia_colado = (t_colado_total / t_ciclo_total * 100) if t_ciclo_total > 0 else 0
    eficiencia_logistica = max(0, 100 - (t_espera_total / t_ciclo_total * 100)) if t_ciclo_total > 0 else 0
    utilizacion_mixer = kpis.utilizacion_mixer_pct
    predictibilidad = max(0, 100 - kpis.tiempo_proyecto_std_h / max(kpis.tiempo_proyecto_p50_h, 0.01) * 100)

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[eficiencia_perf, eficiencia_colado, eficiencia_logistica, utilizacion_mixer, predictibilidad],
        theta=["Perforación", "Colado", "Logística", "Mixer", "Predictibilidad"],
        fill="toself", fillcolor="rgba(59, 130, 246, 0.15)",
        line_color="#3b82f6", line_width=2,
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=320, showlegend=False, margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_tornado:
    st.subheader("🌪️ Sensibilidad")
    params_sens = {"Perforación": 0.35, "Colado": 0.25, "Mixers": 0.20, "Distancia": 0.12, "Suelo": 0.08}
    fig_tornado = go.Figure()
    fig_tornado.add_trace(go.Bar(
        y=list(params_sens.keys()), x=list(params_sens.values()), orientation='h',
        marker=dict(color=list(params_sens.values()), colorscale='RdYlGn_r'),
        text=[f"{v:.0%}" for v in params_sens.values()], textposition='outside',
    ))
    fig_tornado.update_layout(
        yaxis=dict(autorange="reversed"), height=320, margin=dict(t=20, b=40, l=90),
        xaxis=dict(range=[0, 0.5]), showlegend=False,
    )
    st.plotly_chart(fig_tornado, use_container_width=True)

st.divider()

st.divider()

# ===========================================================================
# SECCIÓN 7: Tabla de detalle con filtros
# ===========================================================================
st.subheader("🗂️ Tabla de Detalle por Pilote (réplica base)")

df_tabla = tabla_eventos_df(resultado.eventos_replica_base)
if not df_tabla.empty:
    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        min_espera = df_tabla["tiempo_espera_mixer_h"].min()
        max_espera = df_tabla["tiempo_espera_mixer_h"].max()
        filtro_espera = st.slider(
            "Filtrar por espera mixer (h)",
            float(min_espera), float(max_espera),
            (float(min_espera), float(max_espera)),
            step=0.1
        )
    with col_f2:
        min_ciclo = df_tabla["tiempo_ciclo_total_h"].min()
        max_ciclo = df_tabla["tiempo_ciclo_total_h"].max()
        filtro_ciclo = st.slider(
            "Filtrar por ciclo total (h)",
            float(min_ciclo), float(max_ciclo),
            (float(min_ciclo), float(max_ciclo)),
            step=0.1
        )
    with col_f3:
        ordenar = st.selectbox("Ordenar por", [
            "Pilote ID", "Perforación", "Espera Mixer", "Colado", "Ciclo Total"
        ])
    
    # Aplicar filtros
    df_filtrado = df_tabla[
        (df_tabla["tiempo_espera_mixer_h"] >= filtro_espera[0]) &
        (df_tabla["tiempo_espera_mixer_h"] <= filtro_espera[1]) &
        (df_tabla["tiempo_ciclo_total_h"] >= filtro_ciclo[0]) &
        (df_tabla["tiempo_ciclo_total_h"] <= filtro_ciclo[1])
    ].copy()
    
    # Ordenar
    orden_map = {
        "Pilote ID": "pilote_id",
        "Perforación": "tiempo_perforacion_h",
        "Espera Mixer": "tiempo_espera_mixer_h",
        "Colado": "fin_colado",
        "Ciclo Total": "tiempo_ciclo_total_h",
    }
    df_filtrado = df_filtrado.sort_values(by=orden_map[ordenar], ascending=True)
    
    st.caption(f"Mostrando {len(df_filtrado)} de {len(df_tabla)} pilotes")
    
    st.dataframe(
        df_filtrado.rename(columns={
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
# SECCIÓN 8: Comparador de Escenarios
# ===========================================================================
st.subheader("⚖️ Comparador de Escenarios")

scenarios_dir = "data/scenarios"
os.makedirs(scenarios_dir, exist_ok=True)
archivos = [f for f in os.listdir(scenarios_dir) if f.endswith(".json")]

if len(archivos) >= 2:
    col_comp1, col_comp2 = st.columns(2)
    with col_comp1:
        esc1 = st.selectbox("Escenario A", archivos, key="comp_a")
    with col_comp2:
        esc2 = st.selectbox("Escenario B", archivos, key="comp_b")
    
    if esc1 and esc2 and esc1 != esc2:
        with open(os.path.join(scenarios_dir, esc1), encoding="utf-8") as f:
            datos1 = json.load(f)
        with open(os.path.join(scenarios_dir, esc2), encoding="utf-8") as f:
            datos2 = json.load(f)
        
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown(f"""
            <div class="preview-card">
                <h4>📋 {datos1.get('nombre_escenario', esc1)}</h4>
                <div class="preview-row">
                    <span class="preview-label">Pilotes</span>
                    <span class="preview-value">{datos1.get('cantidad_pilotes', '?')}</span>
                </div>
                <div class="preview-row">
                    <span class="preview-label">Mixers</span>
                    <span class="preview-value">{datos1.get('num_mixers', '?')}</span>
                </div>
                <div class="preview-row">
                    <span class="preview-label">Distancia (km)</span>
                    <span class="preview-value">{datos1.get('distancia_proveedor_km', '?')}</span>
                </div>
                <div class="preview-row">
                    <span class="preview-label">T. Perforación (h)</span>
                    <span class="preview-value">{datos1.get('tiempo_perforacion_min_media', '?')} min</span>
                </div>
                <div class="preview-row">
                    <span class="preview-label">T. Colado (min)</span>
                    <span class="preview-value">{datos1.get('tiempo_colado_min_media', '?')} min</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_c2:
            st.markdown(f"""
            <div class="preview-card">
                <h4>📋 {datos2.get('nombre_escenario', esc2)}</h4>
                <div class="preview-row">
                    <span class="preview-label">Pilotes</span>
                    <span class="preview-value">{datos2.get('cantidad_pilotes', '?')}</span>
                </div>
                <div class="preview-row">
                    <span class="preview-label">Mixers</span>
                    <span class="preview-value">{datos2.get('num_mixers', '?')}</span>
                </div>
                <div class="preview-row">
                    <span class="preview-label">Distancia (km)</span>
                    <span class="preview-value">{datos2.get('distancia_proveedor_km', '?')}</span>
                </div>
                <div class="preview-row">
                    <span class="preview-label">T. Perforación (h)</span>
                    <span class="preview-value">{datos2.get('tiempo_perforacion_min_media', '?')} min</span>
                </div>
                <div class="preview-row">
                    <span class="preview-label">T. Colado (min)</span>
                    <span class="preview-value">{datos2.get('tiempo_colado_min_media', '?')} min</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    elif esc1 == esc2:
        st.info("Seleccione dos escenarios diferentes para comparar.")
else:
    st.info("Se necesitan al menos 2 escenarios guardados para usar el comparador.")

st.divider()

# ===========================================================================
# SECCIÓN 9: Exportar
# ===========================================================================
st.subheader("📥 Exportar Resultados")
if st.button("📊 Descargar Reporte Excel", use_container_width=True, type="secondary"):
    with st.spinner("Generando..."):
        ruta = exportar_excel(resultado, directorio="exports")
    with open(ruta, "rb") as f:
        st.download_button(
            label="⬇️ Descargar Excel",
            data=f.read(),
            file_name=ruta.split("\\")[-1].split("/")[-1],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
