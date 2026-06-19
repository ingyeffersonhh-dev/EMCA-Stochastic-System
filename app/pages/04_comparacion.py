"""
app/pages/04_comparacion.py
Module 4: Scenario Comparison — compare up to 3 saved scenarios side by side.
"""
import streamlit as st
import json
import os
import plotly.graph_objects as go
import pandas as pd

from core.models.parametros import ParametrosEntrada
from core.models.resultados import ResultadoSimulacion

# ── Design tokens (match main.py)
ACC  = "#4C8BF5"
RED  = "#CC1E2A"
CYN  = "#56B8E8"
YEL  = "#F5A623"
TX1  = "#E8EDF5"
TX2  = "#8A98B8"
CARD = "#111E38"
BRD  = "rgba(76,139,245,0.12)"

PALETTE = [ACC, RED, CYN, YEL, "#7C6FD4"]

st.markdown("""
<div style="margin-bottom:1.5rem">
    <h1 style="margin:0;font-size:1.8rem;font-weight:800">📊 Comparación de Escenarios</h1>
    <p style="color:#8A98B8;margin:.2rem 0 0;font-size:.92rem">
        Seleccioná hasta 3 escenarios guardados y comparalos lado a lado
    </p>
</div>
""", unsafe_allow_html=True)

# ── Load available scenarios
scenarios_dir = "data/scenarios"
os.makedirs(scenarios_dir, exist_ok=True)
archivos = sorted([f for f in os.listdir(scenarios_dir) if f.endswith(".json")])

if len(archivos) < 2:
    st.markdown(f"""
    <div style="background:rgba(76,139,245,.06);border:1px solid rgba(76,139,245,.2);
        border-left:4px solid {ACC};border-radius:14px;padding:1.5rem 2rem;margin-top:1rem">
        <strong>⚠️ Se necesitan al menos 2 escenarios guardados para comparar.</strong><br>
        <span style="color:{TX2};font-size:.9rem">Volvé al Módulo 1 (Parametrización) y guardá diferentes configuraciones.</span>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

nombres = [f.replace(".json", "").replace("_", " ") for f in archivos]

# ── Scenario selector
st.markdown(f"""
<div style="background:{CARD};border:1px solid {BRD};border-radius:16px;padding:1.5rem;margin-bottom:1.5rem">
    <p style="color:{TX2};font-size:.85rem;margin:0 0 1rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Seleccioná los escenarios a comparar</p>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

seleccionados = st.multiselect(
    "Escenarios",
    options=archivos,
    format_func=lambda f: f.replace(".json", "").replace("_", " "),
    max_selections=3,
    default=archivos[:min(2, len(archivos))],
    label_visibility="collapsed"
)

if len(seleccionados) < 2:
    st.info("Seleccioná al menos 2 escenarios para ver la comparación.")
    st.stop()

# ── Load scenario data
@st.cache_data
def cargar_escenario(nombre_archivo):
    with open(os.path.join(scenarios_dir, nombre_archivo), encoding="utf-8") as f:
        return json.load(f)

datos = {}
for archivo in seleccionados:
    raw = cargar_escenario(archivo)
    nombre = archivo.replace(".json", "").replace("_", " ")
    params_dict = raw.get("parametros", raw)
    resultado_dict = raw.get("resultado", None)
    datos[nombre] = {
        "params": params_dict,
        "resultado": resultado_dict,
    }

tiene_resultados = all(d["resultado"] is not None for d in datos.values())

# ── Section 1: Parameters comparison
st.markdown(f"""
<div style="display:flex;align-items:center;gap:.75rem;margin:1.5rem 0 1rem">
    <div style="background:{ACC};width:28px;height:28px;border-radius:50%;
        display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.85rem;color:#fff">1</div>
    <div style="font-weight:700;font-size:1rem;color:{TX1}">Parámetros de Entrada</div>
</div>
""", unsafe_allow_html=True)

param_labels = {
    "diametro_m":                   ("Diámetro pilote", "m"),
    "longitud_m":                   ("Longitud pilote", "m"),
    "cantidad_pilotes":              ("Cantidad de pilotes", "uds"),
    "num_mixers":                    ("Mixers activos", "uds"),
    "distancia_proveedor_km":       ("Distancia a planta", "km"),
    "horas_por_dia":                 ("Jornada laboral", "h/día"),
    "tiempo_perforacion_min_media": ("T. Perforación μ", "min"),
    "tiempo_colado_min_media":      ("T. Colado μ", "min"),
    "tipo_suelo":                    ("Tipo de suelo", ""),
}

rows = []
for key, (label, unit) in param_labels.items():
    row = {"Parámetro": f"{label} ({unit})" if unit else label}
    for nombre, d in datos.items():
        val = d["params"].get(key, "—")
        row[nombre] = str(val)
    rows.append(row)

df_params = pd.DataFrame(rows)
st.dataframe(df_params, use_container_width=True, hide_index=True)

# ── Section 2: Results comparison
tiene_algun_resultado = any(d["resultado"] is not None for d in datos.values())

if not tiene_algun_resultado:
    st.markdown(f"""
    <div style="background:rgba(245,166,35,.06);border:1px solid rgba(245,166,35,.2);
        border-left:4px solid {YEL};border-radius:14px;padding:1.2rem 1.5rem;margin:1.5rem 0">
        ⚠️ Ninguno de los escenarios seleccionados tiene resultados de simulación. Ejecutá la simulación en el Módulo 2 para poder compararlos.
    </div>
    """, unsafe_allow_html=True)
else:
    escenarios_sin_resultado = [nombre for nombre, d in datos.items() if d["resultado"] is None]
    if escenarios_sin_resultado:
        st.markdown(f"""
        <div style="background:rgba(245,166,35,.06);border:1px solid rgba(245,166,35,.2);
            border-left:4px solid {YEL};border-radius:14px;padding:1rem 1.5rem;margin:1.5rem 0">
            ⚠️ Los escenarios <strong>{', '.join(escenarios_sin_resultado)}</strong> aún no fueron simulados. Sus resultados se mostrarán en cero.
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:.75rem;margin:2rem 0 1rem">
        <div style="background:{RED};width:28px;height:28px;border-radius:50%;
            display:flex;align-items:center;justify-content:center;font-weight:800;font-size:.85rem;color:#fff">2</div>
        <div style="font-weight:700;font-size:1rem;color:{TX1}">Resultados de Simulación</div>
    </div>
    """, unsafe_allow_html=True)

    # KPI cards per scenario
    cols = st.columns(len(datos))
    for col, (nombre, d) in zip(cols, datos.items()):
        r = d["resultado"]
        kpis = r.get("kpis", {}) if r else {}
        horas_dia = d["params"].get("horas_por_dia", 8)
        p50 = kpis.get("tiempo_proyecto_p50_h", 0) if kpis else 0
        p90 = kpis.get("tiempo_proyecto_p90_h", 0) if kpis else 0
        util = kpis.get("utilizacion_mixer_pct", 0) if kpis else 0
        espera = kpis.get("tiempo_espera_mixer_promedio_h", 0) if kpis else 0
        cuello = kpis.get("cuello_botella", "—") if kpis else "No simulado"
        color_util = RED if util > 85 else ACC

        col.markdown(f"""
        <div style="background:{CARD};border:1px solid {BRD};border-radius:16px;padding:1.5rem">
            <div style="font-weight:800;font-size:1rem;color:{ACC};margin-bottom:1.2rem;
                border-bottom:1px solid {BRD};padding-bottom:.8rem">{nombre}</div>

            <div style="margin-bottom:.8rem">
                <div style="color:{TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Duración P50</div>
                <div style="color:{TX1};font-size:1.4rem;font-weight:800">{p50:.1f} h</div>
                <div style="color:{TX2};font-size:.8rem">{p50/horas_dia:.1f} días laborales</div>
            </div>
            <div style="margin-bottom:.8rem">
                <div style="color:{TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Duración P90</div>
                <div style="color:{TX1};font-size:1.4rem;font-weight:800">{p90:.1f} h</div>
                <div style="color:{TX2};font-size:.8rem">{p90/horas_dia:.1f} días laborales</div>
            </div>
            <div style="margin-bottom:.8rem">
                <div style="color:{TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Utilización Mixer</div>
                <div style="color:{color_util};font-size:1.4rem;font-weight:800">{util:.0f}%</div>
            </div>
            <div>
                <div style="color:{TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Cuello de botella</div>
                <div style="color:{TX1};font-size:.95rem;font-weight:700;margin-top:.2rem">{cuello}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Bar chart: P50 and P90 comparison
    st.markdown(f"<div style='font-weight:600;color:{TX1};margin-bottom:.5rem'>Duración del Proyecto — P50 vs P90</div>", unsafe_allow_html=True)
    nombres_list = list(datos.keys())
    
    def get_kpi_val(nombre, key):
        r = datos[nombre]["resultado"]
        if not r or not r.get("kpis"): return 0
        return r["kpis"].get(key, 0)
        
    p50s = [get_kpi_val(n, "tiempo_proyecto_p50_h") for n in nombres_list]
    p90s = [get_kpi_val(n, "tiempo_proyecto_p90_h") for n in nombres_list]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(name="P50", x=nombres_list, y=p50s, marker_color=ACC, opacity=0.9))
    fig_bar.add_trace(go.Bar(name="P90", x=nombres_list, y=p90s, marker_color=CYN, opacity=0.9))
    fig_bar.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        barmode="group", height=320,
        font=dict(family="Inter,sans-serif", color=TX1, size=12),
        legend=dict(font=dict(color=TX2)),
        yaxis_title="Horas",
        margin=dict(t=20, b=40, l=50, r=20),
    )
    fig_bar.update_xaxes(gridcolor="rgba(76,139,245,0.08)")
    fig_bar.update_yaxes(gridcolor="rgba(76,139,245,0.08)")
    st.plotly_chart(fig_bar, use_container_width=True)

    # ── Radar chart
    st.markdown(f"<div style='font-weight:600;color:{TX1};margin:.5rem 0'>Perfil de Eficiencia (Radar)</div>", unsafe_allow_html=True)
    cats = ["Velocidad (P50↓)", "Confiabilidad (P90-P50↓)", "Eficiencia Mixer↑", "Sin Esperas↑"]

    def normalizar(val, mn, mx, invertir=False):
        if mx == mn:
            return 0.5
        n = (val - mn) / (mx - mn)
        return 1 - n if invertir else n

    p50_vals = [get_kpi_val(n, "tiempo_proyecto_p50_h") for n in nombres_list]
    p90_vals = [get_kpi_val(n, "tiempo_proyecto_p90_h") for n in nombres_list]
    util_vals = [get_kpi_val(n, "utilizacion_mixer_pct") for n in nombres_list]
    esp_vals  = [get_kpi_val(n, "tiempo_espera_mixer_promedio_h") for n in nombres_list]
    spread_vals = [p90_vals[i] - p50_vals[i] for i in range(len(nombres_list))]

    fig_rad = go.Figure()
    for i, nombre in enumerate(nombres_list):
        r_vals = [
            normalizar(p50_vals[i], min(p50_vals), max(p50_vals), invertir=True),
            normalizar(spread_vals[i], min(spread_vals), max(spread_vals), invertir=True),
            normalizar(util_vals[i], min(util_vals), max(util_vals)),
            normalizar(esp_vals[i], min(esp_vals), max(esp_vals), invertir=True),
        ]
        r_vals.append(r_vals[0])
        fig_rad.add_trace(go.Scatterpolar(
            r=r_vals,
            theta=cats + [cats[0]],
            fill="toself",
            name=nombre,
            line_color=PALETTE[i % len(PALETTE)],
            opacity=0.7,
        ))
    fig_rad.update_layout(
        polar=dict(
            bgcolor="rgba(17,30,56,0.8)",
            radialaxis=dict(visible=True, range=[0, 1], color=TX2),
            angularaxis=dict(color=TX1),
        ),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=380, margin=dict(t=20, b=20, l=60, r=60),
        font=dict(family="Inter,sans-serif", color=TX1),
        legend=dict(font=dict(color=TX2)),
    )
    st.plotly_chart(fig_rad, use_container_width=True)
