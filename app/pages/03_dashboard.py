"""
app/pages/03_dashboard.py
Módulo 3: Panel de Control Gerencial — Premium dark theme charts.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import os

from core.analytics.kpis import tabla_eventos_df
from core.analytics.gantt import generar_gantt_df, generar_curva_s
from core.analytics.exportar import exportar_excel, _formatear_tiempo
from app.components.theme import get_active_tokens, _rgba
from app.components.stepper import render_stepper

t = get_active_tokens()

def _layout(fig, h=400, **kw):
    """Apply consistent EMCA brand layout to any Plotly figure (mode-aware)."""
    t = get_active_tokens()
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=h,
        margin=dict(t=30, b=50, l=60, r=30),
        font=dict(family="Inter,sans-serif", color=t.TX, size=12),
        legend=dict(font=dict(color=t.TX2)),
        **kw,
    )
    fig.update_xaxes(showgrid=True, gridcolor=t.GRD, gridwidth=1, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=t.GRD, gridwidth=1, zeroline=False)

# ── Title ──────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:.5rem">
    <h1 style="margin:0;font-size:1.8rem;font-weight:800">📊 Panel de Control Gerencial</h1>
    <p style="color:{t.TX2};margin:.2rem 0 0;font-size:.92rem">
        Visión analítica del desempeño del sistema logístico y de construcción
    </p>
</div>
""", unsafe_allow_html=True)

# ── Stepper ────────────────────────────────────────────────────
render_stepper([("1", "Parametrización"), ("2", "Simulación"), ("3", "Dashboard")])

# ── Pre-condition ──────────────────────────────────────────────
if "resultado" not in st.session_state:
    st.warning("⚠️ Ejecute primero la simulación en el **Módulo 2**.")
    st.stop()

resultado = st.session_state["resultado"]
params = st.session_state.get("parametros")
kpis = resultado.kpis

if kpis is None:
    st.error("No hay KPIs disponibles. Vuelva a ejecutar la simulación.")
    st.stop()

# ══════════════════════════════════════════════════════════════
# EXPORT BUTTON
# ══════════════════════════════════════════════════════════════
col_title, col_export = st.columns([4, 1])
with col_export:
    try:
        # exportar_excel expects (resultado, directorio), returns file path
        ruta_excel = exportar_excel(resultado)
        with open(ruta_excel, "rb") as f:
            excel_bytes = f.read()
            
        nombre_esc = params.nombre_escenario if params else "reporte"
        st.download_button(
            label="📥 Exportar Excel",
            data=excel_bytes,
            file_name=f"EMCA_{nombre_esc.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary",
        )
    except Exception as e:
        st.caption(f"Export no disponible: {e}")

# ══════════════════════════════════════════════════════════════
# KPI CARDS
# ══════════════════════════════════════════════════════════════
h_dia = params.horas_por_dia if params and hasattr(params, 'horas_por_dia') else 8.0

st.markdown(f"""
<div class="kpi-grid" style="grid-template-columns:repeat(5,1fr)">
    <div class="kpi-card kpi-accent-green">
        <div class="kpi-label">Duración P10</div>
        <div class="kpi-value" style="font-size:1.6rem">{_formatear_tiempo(kpis.tiempo_proyecto_p10_h)}</div>
        <div class="kpi-delta up">Optimista · {kpis.tiempo_proyecto_p10_h/h_dia:.1f}d</div>
    </div>
    <div class="kpi-card kpi-accent-blue">
        <div class="kpi-label">Duración P50</div>
        <div class="kpi-value" style="font-size:1.6rem">{_formatear_tiempo(kpis.tiempo_proyecto_p50_h)}</div>
        <div class="kpi-delta neutral">Mediana · {kpis.tiempo_proyecto_p50_h/h_dia:.1f}d</div>
    </div>
    <div class="kpi-card kpi-accent-yellow">
        <div class="kpi-label">Duración P90</div>
        <div class="kpi-value" style="font-size:1.6rem">{_formatear_tiempo(kpis.tiempo_proyecto_p90_h)}</div>
        <div class="kpi-delta neutral">Conservador · {kpis.tiempo_proyecto_p90_h/h_dia:.1f}d</div>
    </div>
    <div class="kpi-card kpi-accent-red">
        <div class="kpi-label">Utilización Mixer</div>
        <div class="kpi-value">{kpis.utilizacion_mixer_pct:.0f}%</div>
        <div class="kpi-delta {'down' if kpis.utilizacion_mixer_pct > 85 else 'up'}">
            {'⚠️ Saturado' if kpis.utilizacion_mixer_pct > 85 else '✓ Normal'}
        </div>
    </div>
    <div class="kpi-card kpi-accent-purple">
        <div class="kpi-label">Utilización Perforadora</div>
        <div class="kpi-value">{kpis.utilizacion_perforadora_pct:.0f}%</div>
        <div class="kpi-delta {'down' if kpis.utilizacion_perforadora_pct > 85 else 'up'}">
            {'⚠️ Saturado' if kpis.utilizacion_perforadora_pct > 85 else '✓ Normal'}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

if kpis.alerta_logistica:
    st.markdown(f"""
    <div class="alerta-roja">
        🚨 <strong>ALERTA LOGÍSTICA</strong>: Espera mixer promedio =
        <strong>{_formatear_tiempo(kpis.tiempo_espera_mixer_promedio_h)}</strong>.
        Considere aumentar la flota o reducir la distancia.
    </div>
    """, unsafe_allow_html=True)

if kpis.alerta_capacidad_perforadora:
    st.markdown(f"""
    <div class="alerta-roja">
        ⛏️ <strong>ALERTA PERFORACIÓN</strong>: Utilización de perforadora =
        <strong>{kpis.utilizacion_perforadora_pct:.0f}%</strong>.
        Considere agregar más equipos de perforación para evitar serialización.
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# RECOMENDACIONES AUTOMÁTICAS (Sugerencias Inteligentes)
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title" style="margin-top:2rem"><h3>💡 Sugerencias de Optimización</h3><span class="badge">IA Analítica</span></div>', unsafe_allow_html=True)

sugerencias = []

# Logística y Mixers
if kpis.utilizacion_mixer_pct > 85:
    sugerencias.append(("⚠️", "Alta Saturación Logística", f"Los mixers tienen una utilización del {kpis.utilizacion_mixer_pct:.0f}%. Considere agregar 1 o 2 unidades a la flota para aliviar la saturación y proteger el avance.", t.RED))
elif kpis.utilizacion_mixer_pct < 45:
    sugerencias.append(("🔄", "Flota Subutilizada", f"La utilización de la flota es baja ({kpis.utilizacion_mixer_pct:.0f}%). Considere redistribuir los mixers o ajustar los turnos para equilibrar la carga operativa sin afectar el cronograma.", t.ACC))

# Perforadora
if kpis.utilizacion_perforadora_pct > 85:
    sugerencias.append(("⛏️", "Alta Saturación de Perforadora", f"La perforadora está al {kpis.utilizacion_perforadora_pct:.0f}%. Considerá agregar 1 perforadora más para reducir la serialización de la fase de perforación.", t.RED))
elif kpis.utilizacion_perforadora_pct < 45:
    sugerencias.append(("🔄", "Perforadora Subutilizada", f"La utilización de la perforadora es baja ({kpis.utilizacion_perforadora_pct:.0f}%). Podés redistribuir trabajos o ajustar turnos para equilibrar la carga operativa.", t.ACC))

if kpis.tiempo_espera_mixer_promedio_h > 1.5:
    sugerencias.append(("🚚", "Sincronización de Despachos", f"El tiempo promedio de espera del mixer en obra es alto ({_formatear_tiempo(kpis.tiempo_espera_mixer_promedio_h)}). Mejorar la coordinación con la planta concretera para despachar justo al finalizar la perforación reducirá los tiempos muertos y acelerará el ciclo total.", t.YELLOW))

# Riesgo / Incertidumbre
incertidumbre = (kpis.tiempo_proyecto_p90_h - kpis.tiempo_proyecto_p50_h) / kpis.tiempo_proyecto_p50_h
if incertidumbre > 0.15:
    sugerencias.append(("📈", "Alta Volatilidad de Tiempos", f"Existe gran diferencia entre su escenario esperado (P50) y el pesimista (P90) ({incertidumbre:.0%} de desvío). Se recomienda asegurar contratos blindados para imprevistos climáticos o mecánicos.", t.RED))
elif incertidumbre < 0.05:
    sugerencias.append(("🎯", "Alta Predictibilidad", "El sistema tiene una baja variabilidad. El cronograma actual es robusto, lo que facilita fijar compromisos agresivos con el cliente final.", t.ACC))

html_sug = '<div style="display:flex; flex-direction:column; gap:1rem;">'
for icon, title, text, color in sugerencias:
    html_sug += f'''
<div class="kpi-card" style="display:flex; align-items:center; gap:1.2rem; padding:1.2rem; background:{_rgba(t.CARD, 0.7)}; border-left:4px solid {color}; text-align:left;">
    <div style="font-size:2rem;">{icon}</div>
    <div>
        <h4 style="margin:0; font-size:1.1rem; font-weight:600; color:{t.TX};">{title}</h4>
        <p style="margin:0.3rem 0 0; font-size:0.95rem; color:{t.TX2}; line-height:1.4;">{text}</p>
    </div>
</div>
'''
html_sug += '</div>'
st.markdown(html_sug, unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# HISTOGRAM — Monte Carlo Distribution
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title"><h3>📊 Distribución Monte Carlo</h3><span class="badge">Probabilístico</span></div>', unsafe_allow_html=True)

tiempos = resultado.tiempos_proyecto_todas_replicas
if tiempos:
    arr = np.array(tiempos)
    media_v = np.mean(arr)
    std_v = np.std(arr)

    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=arr, nbinsx=40,
        marker=dict(color=t.BLUE, line=dict(width=0)),
        opacity=0.85, name="Duración",
    ))

    # Percentile lines
    for val, color, label, yp in [
        (kpis.tiempo_proyecto_p10_h, t.ACC, "P10", 0.92),
        (kpis.tiempo_proyecto_p50_h, t.YELLOW, "P50", 0.82),
        (kpis.tiempo_proyecto_p90_h, t.RED, "P90", 0.72),
    ]:
        fig_hist.add_vline(x=val, line_dash="dash", line_color=color, line_width=2)
        fig_hist.add_annotation(
            x=val, y=yp, text=f"<b>{label}</b><br>{_formatear_tiempo(val)}",
            font=dict(color=color, size=11), bgcolor=_rgba(t.CARD, 0.9),
            bordercolor=color, borderwidth=1, borderpad=4,
            showarrow=False, yref="paper",
        )

    # P10-P90 band
    fig_hist.add_vrect(
        x0=kpis.tiempo_proyecto_p10_h, x1=kpis.tiempo_proyecto_p90_h,
        fillcolor=_rgba(t.BLUE, 0.06), layer="below", line_width=0,
    )

    _layout(fig_hist, h=420, showlegend=False,
            xaxis_title="Duración del proyecto (h)",
            yaxis_title="Frecuencia")

    # Stats badges
    st.markdown(f"""
    <div style="display:flex;gap:.6rem;margin-bottom:.8rem;flex-wrap:wrap">
        <div class="stats-badge"><span class="stats-badge-label">Media:</span>
            <span class="stats-badge-value">{_formatear_tiempo(media_v)}</span></div>
        <div class="stats-badge"><span class="stats-badge-label">Desv.Est:</span>
            <span class="stats-badge-value">{_formatear_tiempo(std_v)}</span></div>
        <div class="stats-badge"><span class="stats-badge-label">Réplicas:</span>
            <span class="stats-badge-value">{len(arr)}</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# GANTT CHART
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title"><h3>📅 Cronograma Gantt</h3><span class="badge">Réplica Base</span></div>', unsafe_allow_html=True)

fecha_inicio = st.date_input("Fecha de inicio del proyecto", value=None,
                              help="Seleccione la fecha real de inicio")
hora_str = f"{fecha_inicio} 07:00:00" if fecha_inicio else "2025-01-06 07:00:00"
gantt_df = generar_gantt_df(resultado.eventos_replica_base, hora_inicio_proyecto=hora_str)

if not gantt_df.empty:
    COLOR_MAP = {
        "🔩 Perforación": t.BLUE,
        "⛏️ Espera Perforadora": t.PURPLE,
        "⏳ Espera Mixer": t.RED,
        "🪣 Colado": t.ACC,
    }
    fig_g = px.timeline(gantt_df, x_start="Inicio", x_end="Fin", y="Pilote",
                         color="Fase", color_discrete_map=COLOR_MAP,
                         hover_data=["Duración_h"],
                         labels={"Duración_h": "Duración (h)"})
    fig_g.update_yaxes(autorange="reversed")
    _layout(fig_g, h=max(400, len(gantt_df["Pilote"].unique()) * 28 + 80),
            legend_title="Fase")
    st.plotly_chart(fig_g, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# S-CURVE
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title"><h3>📈 Curva S — Avance Acumulado</h3><span class="badge">Progreso</span></div>', unsafe_allow_html=True)

curva_df = generar_curva_s(resultado.eventos_replica_base)
if not curva_df.empty:
    fig_s = go.Figure()
    fig_s.add_trace(go.Scatter(
        x=curva_df["tiempo_h"], y=curva_df["avance_pct"],
        mode="lines", fill="tozeroy",
        line=dict(color=t.CYAN, width=3),
        fillcolor=_rgba(t.CYAN, 0.08),
    ))
    _layout(fig_s, h=300, showlegend=False,
            xaxis_title="Tiempo (h)",
            yaxis_title="Pilotes completados (%)",
            yaxis=dict(range=[0, 105], showgrid=True, gridcolor=t.GRD))
    st.plotly_chart(fig_s, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# RADAR + TORNADO  (side by side)
# ══════════════════════════════════════════════════════════════
col_r, col_t = st.columns(2)

with col_r:
    st.markdown('<div class="section-title"><h3>🎯 Eficiencia</h3><span class="badge">Radar</span></div>', unsafe_allow_html=True)
    ev = resultado.eventos_replica_base
    tp = sum(e.tiempo_perforacion_h for e in ev)
    tc = sum(e.tiempo_colado_h for e in ev)
    te = sum(e.tiempo_espera_mixer_h for e in ev)
    tt = tp + tc + te
    # Eficiencia de perforadora: 100% cuando no hay espera; tiende a 0 con esperas largas.
    espera_perf = kpis.tiempo_espera_perforadora_promedio_h
    sin_espera_perf = max(0, 100 - espera_perf * 10)
    vals = [
        (tp / tt * 100) if tt > 0 else 0,
        (tc / tt * 100) if tt > 0 else 0,
        kpis.utilizacion_mixer_pct,
        sin_espera_perf,
        max(0, 100 - kpis.tiempo_proyecto_std_h / max(kpis.tiempo_proyecto_p50_h, .01) * 100),
    ]
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=vals,
        theta=["Perforación", "Colado", "Mixer", "Sin Espera Perforadora↑", "Predictibilidad"],
        fill="toself", fillcolor=_rgba(t.GREEN, 0.1),
        line=dict(color=t.ACC, width=2),
        marker=dict(size=6, color=t.ACC),
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor=t.GRD,
                            tickfont=dict(size=10, color=t.TX2)),
            angularaxis=dict(gridcolor=t.GRD, tickfont=dict(color=t.TX2)),
            bgcolor="rgba(0,0,0,0)",
        ),
        height=340, showlegend=False, margin=dict(t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)", font=dict(color=t.TX),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_t:
    st.markdown('<div class="section-title"><h3>🌪️ Sensibilidad</h3><span class="badge">Tornado</span></div>', unsafe_allow_html=True)
    ps = {"Perforación": 0.35, "Colado": 0.25, "Mixers": 0.20, "Distancia": 0.12, "Suelo": 0.08}
    colors = [t.RED, t.YELLOW, t.ACC, t.BLUE, t.GREEN]
    fig_t = go.Figure()
    fig_t.add_trace(go.Bar(
        y=list(ps.keys()), x=list(ps.values()), orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"{v:.0%}" for v in ps.values()], textposition='outside',
        textfont=dict(color=t.TX, size=12, family="Inter"),
    ))
    _layout(fig_t, h=340, showlegend=False,
            yaxis=dict(autorange="reversed", gridcolor=t.GRD),
            xaxis=dict(range=[0, 0.5], gridcolor=t.GRD))
    fig_t.update_layout(margin=dict(l=100))
    st.plotly_chart(fig_t, use_container_width=True)

st.divider()

# ══════════════════════════════════════════════════════════════
# DETAIL TABLE
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title"><h3>🗂️ Detalle por Pilote</h3><span class="badge">Réplica Base</span></div>', unsafe_allow_html=True)
st.markdown(f'''
<div style="display:flex; gap: 1rem; margin-bottom: 1rem; font-size: 0.9rem; background:{t.GRD}; padding: 0.5rem 1rem; border-radius: 0.5rem; justify-content: center;">
  <div>🟩 <b>Óptimo</b> (0h - 2h)</div>
  <div>🟨 <b>Moderado</b> (2h - 5h)</div>
  <div>🟥 <b>Crítico</b> (> 5h)</div>
</div>
''', unsafe_allow_html=True)

df_tabla = tabla_eventos_df(resultado.eventos_replica_base)
if not df_tabla.empty:
    cf1, cf2, cf3 = st.columns(3)
    with cf1:
        mn_ep, mx_ep = float(df_tabla["tiempo_espera_perforadora_h"].min()), float(df_tabla["tiempo_espera_perforadora_h"].max())
        filtro_ep = st.slider("Filtrar espera perforadora (h)", mn_ep, mx_ep, (mn_ep, mx_ep), step=0.1)
    with cf2:
        mn_em, mx_em = float(df_tabla["tiempo_espera_mixer_h"].min()), float(df_tabla["tiempo_espera_mixer_h"].max())
        filtro_em = st.slider("Filtrar espera mixer (h)", mn_em, mx_em, (mn_em, mx_em), step=0.1)
    with cf3:
        ordenar = st.selectbox("Ordenar por", ["Pilote ID", "Perforación", "Espera Perforadora", "Espera Mixer", "Colado", "Ciclo Total"])

    df_f = df_tabla[
        (df_tabla["tiempo_espera_perforadora_h"] >= filtro_ep[0]) &
        (df_tabla["tiempo_espera_perforadora_h"] <= filtro_ep[1]) &
        (df_tabla["tiempo_espera_mixer_h"] >= filtro_em[0]) &
        (df_tabla["tiempo_espera_mixer_h"] <= filtro_em[1])
    ].copy()

    om = {"Pilote ID": "pilote_id", "Perforación": "tiempo_perforacion_h",
          "Espera Perforadora": "tiempo_espera_perforadora_h",
          "Espera Mixer": "tiempo_espera_mixer_h", "Colado": "fin_colado",
          "Ciclo Total": "tiempo_ciclo_total_h"}
    df_f = df_f.sort_values(by=om[ordenar])

    st.caption(f"Mostrando {len(df_f)} de {len(df_tabla)} pilotes")
    st.dataframe(
        df_f.rename(columns={
            "pilote_id": "Pilote", "tiempo_perforacion_h": "Perf. (h)",
            "tiempo_espera_perforadora_h": "Espera Perforadora (h)",
            "tiempo_espera_mixer_h": "Espera Mixer (h)",
            "tiempo_colado_h": "Colado (h)", "tiempo_ciclo_total_h": "Ciclo Total (h)",
        })[["Pilote", "Perf. (h)", "Espera Perforadora (h)", "Espera Mixer (h)", "Colado (h)", "Ciclo Total (h)"]
        ].style.background_gradient(subset=["Espera Perforadora (h)", "Espera Mixer (h)"], cmap="RdYlGn_r")
        .format("{:.2f}", subset=["Perf. (h)", "Espera Perforadora (h)", "Espera Mixer (h)", "Colado (h)", "Ciclo Total (h)"]),
        use_container_width=True,
    )

st.divider()

# ══════════════════════════════════════════════════════════════
# SCENARIO COMPARATOR
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title"><h3>⚖️ Comparador de Escenarios</h3><span class="badge">Side-by-side</span></div>', unsafe_allow_html=True)

scenarios_dir = "data/scenarios"
os.makedirs(scenarios_dir, exist_ok=True)
archivos = [f for f in os.listdir(scenarios_dir) if f.endswith(".json")]

if len(archivos) >= 2:
    cc1, cc2 = st.columns(2)
    with cc1: esc1 = st.selectbox("Escenario A", archivos, key="comp_a")
    with cc2: esc2 = st.selectbox("Escenario B", archivos, key="comp_b")

    if esc1 and esc2 and esc1 != esc2:
        with open(os.path.join(scenarios_dir, esc1), encoding="utf-8") as f: d1 = json.load(f)
        with open(os.path.join(scenarios_dir, esc2), encoding="utf-8") as f: d2 = json.load(f)

        for col, d in [(cc1, d1), (cc2, d2)]:
            # Scenarios are saved as {"parametros": {...}, "resultado": {...}}.
            # Fall back to root dict for old-format scenarios without the wrapper.
            p = d.get("parametros", d)
            with col:
                st.markdown(f"""
                <div class="preview-card">
                    <h4>📋 {p.get('nombre_escenario', '?')}</h4>
                    <div class="preview-row"><span class="preview-label">Pilotes</span>
                        <span class="preview-value">{p.get('cantidad_pilotes','?')}</span></div>
                    <div class="preview-row"><span class="preview-label">Mixers</span>
                        <span class="preview-value">{p.get('num_mixers','?')}</span></div>
                    <div class="preview-row"><span class="preview-label">Perforadoras</span>
                        <span class="preview-value">{p.get('num_perforadoras','?')}</span></div>
                    <div class="preview-row"><span class="preview-label">Distancia (km)</span>
                        <span class="preview-value">{p.get('distancia_proveedor_km','?')}</span></div>
                    <div class="preview-row"><span class="preview-label">T. Perforación</span>
                        <span class="preview-value">{p.get('tiempo_perforacion_min_media','?')} min</span></div>
                    <div class="preview-row"><span class="preview-label">T. Colado</span>
                        <span class="preview-value">{p.get('tiempo_colado_min_media','?')} min</span></div>
                </div>
                """, unsafe_allow_html=True)
    elif esc1 == esc2:
        st.info("Seleccione dos escenarios diferentes para comparar.")
else:
    st.info("Se necesitan al menos 2 escenarios guardados para el comparador.")

st.divider()

# ══════════════════════════════════════════════════════════════
# EXPORT
# ══════════════════════════════════════════════════════════════
st.markdown('<div class="section-title"><h3>📥 Exportar Resultados</h3><span class="badge">Excel</span></div>', unsafe_allow_html=True)

if st.button("📊 Descargar Reporte Excel", use_container_width=True, type="secondary"):
    with st.spinner("Generando..."):
        ruta = exportar_excel(resultado, directorio="exports")
    with open(ruta, "rb") as f:
        st.download_button(
            label="⬇️ Descargar Excel", data=f.read(),
            file_name=ruta.split("\\")[-1].split("/")[-1],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
