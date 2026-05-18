"""
app/pages/00_home.py
Home — Premium dashboard greeting & project overview.
"""
import streamlit as st
import os
import json
from datetime import datetime

st.markdown("""
<div style="margin-bottom:1.5rem">
    <h1 style="margin:0;font-size:2rem;font-weight:800">
        Bienvenido al Control Tower 👋
    </h1>
    <p style="color:#8892B0;margin:.3rem 0 0;font-size:1rem">
        Sistema estocástico de apoyo a la toma de decisiones para perforación de pilotes
    </p>
</div>
""", unsafe_allow_html=True)

# ── Status flags ───────────────────────────────────────────────
p_ok = "parametros" in st.session_state
r_ok = "resultado" in st.session_state

# ── Stepper ────────────────────────────────────────────────────
steps = [("1", "Parametrización", p_ok), ("2", "Simulación", r_ok), ("3", "Dashboard", r_ok)]
html = '<div class="stepper">'
for i, (n, l, c) in enumerate(steps):
    s = "completed" if c else ("active" if (i == 0 and not p_ok) or (i == 1 and p_ok and not r_ok) or (i == 2 and r_ok) else "")
    icon = "✅" if c else n
    html += f'<div class="stepper-step {s}"><span>{icon}</span><span>{l}</span></div>'
    if i < 2:
        html += '<span class="stepper-arrow">→</span>'
html += '</div>'
st.markdown(html, unsafe_allow_html=True)

# ── KPI Summary Cards ─────────────────────────────────────────
if r_ok:
    k = st.session_state["resultado"].kpis
    params = st.session_state.get("parametros")
    h_dia = params.horas_por_dia if params else 8.0

    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card kpi-accent-green">
            <div class="kpi-label">Duración P50</div>
            <div class="kpi-value">{k.tiempo_proyecto_p50_h:.1f}h</div>
            <div class="kpi-delta neutral">≈ {k.tiempo_proyecto_p50_h / h_dia:.1f} días</div>
        </div>
        <div class="kpi-card kpi-accent-blue">
            <div class="kpi-label">Duración P90</div>
            <div class="kpi-value">{k.tiempo_proyecto_p90_h:.1f}h</div>
            <div class="kpi-delta neutral">≈ {k.tiempo_proyecto_p90_h / h_dia:.1f} días</div>
        </div>
        <div class="kpi-card kpi-accent-yellow">
            <div class="kpi-label">Utilización Mixer</div>
            <div class="kpi-value">{k.utilizacion_mixer_pct:.0f}%</div>
            <div class="kpi-delta {'down' if k.utilizacion_mixer_pct > 85 else 'up'}">
                {'⚠️ Saturado' if k.utilizacion_mixer_pct > 85 else '✓ Normal'}
            </div>
        </div>
        <div class="kpi-card kpi-accent-red">
            <div class="kpi-label">Cuello de Botella</div>
            <div class="kpi-value" style="font-size:1.3rem">{k.cuello_botella.upper()}</div>
            <div class="kpi-delta neutral">
                Espera mixer: {k.tiempo_espera_mixer_promedio_h:.2f}h
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Flow Diagram ───────────────────────────────────────────────
st.markdown("""
<div class="flow-diagram">
    <div class="flow-node">📋 Configurar<br/><small style="color:#8892B0">Parámetros</small></div>
    <span class="flow-arrow">→</span>
    <div class="flow-node">⚙️ Simular<br/><small style="color:#8892B0">Monte Carlo</small></div>
    <span class="flow-arrow">→</span>
    <div class="flow-node">📊 Analizar<br/><small style="color:#8892B0">Dashboard</small></div>
</div>
""", unsafe_allow_html=True)

# ── Module Navigation Cards ───────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("📋 Parametrización", use_container_width=True,
                  type="primary" if not p_ok else "secondary"):
        st.switch_page("pages/01_parametrizacion.py")
    st.markdown("""
    <div class="nav-card">
        <h4>Configuración</h4>
        <p>Dimensiones del pilote, tipo de suelo, flota de mixers, distancia
        al proveedor y parámetros estocásticos de perforación y colado.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    if st.button("⚙️ Simulación", use_container_width=True,
                  type="primary" if (p_ok and not r_ok) else "secondary",
                  disabled=not p_ok):
        st.switch_page("pages/02_simulacion.py")
    st.markdown("""
    <div class="nav-card">
        <h4>Motor Estocástico</h4>
        <p>Ejecute réplicas Monte Carlo sobre el motor de eventos discretos
        (SimPy). Configure réplicas y semilla aleatoria.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    if st.button("📊 Dashboard", use_container_width=True,
                  type="primary" if r_ok else "secondary",
                  disabled=not r_ok):
        st.switch_page("pages/03_dashboard.py")
    st.markdown("""
    <div class="nav-card">
        <h4>Panel Gerencial</h4>
        <p>Cronograma Gantt, distribución de duraciones, KPIs,
        alertas logísticas y exportación a Excel.</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Session Status ────────────────────────────────────────────
st.subheader("📌 Estado de la Sesión")
c_a, c_b, c_c = st.columns(3)
c_a.metric("Parámetros", "✅ Configurados" if p_ok else "⬜ Pendiente")
c_b.metric("Simulación", "✅ Ejecutada" if r_ok else "⬜ Pendiente")
c_c.metric("Resultados", "✅ Listos" if r_ok else "⬜ Pendiente")

# ── Saved Scenarios ───────────────────────────────────────────
st.divider()
st.subheader("📂 Escenarios Guardados")

scenarios_dir = "data/scenarios"
os.makedirs(scenarios_dir, exist_ok=True)
archivos = [f for f in os.listdir(scenarios_dir) if f.endswith(".json")]

if archivos:
    archivos.sort(key=lambda x: os.path.getmtime(os.path.join(scenarios_dir, x)), reverse=True)
    sc1, sc2 = st.columns([2, 1])
    with sc1:
        for archivo in archivos[:5]:
            fp = os.path.join(scenarios_dir, archivo)
            mtime = datetime.fromtimestamp(os.path.getmtime(fp)).strftime("%d/%m/%Y %H:%M")
            try:
                with open(fp, encoding="utf-8") as f:
                    d = json.load(f)
                nombre = d.get("nombre_escenario", archivo.replace(".json", ""))
                pilotes = d.get("cantidad_pilotes", "?")
                mixers = d.get("num_mixers", "?")
            except Exception:
                nombre, pilotes, mixers = archivo.replace(".json", ""), "?", "?"

            st.markdown(f"""
            <div class="scenario-item">
                <div>
                    <div class="scenario-name">{nombre}</div>
                    <div class="scenario-date">{pilotes} pilotes · {mixers} mixers</div>
                </div>
                <div class="scenario-date">{mtime}</div>
            </div>
            """, unsafe_allow_html=True)

    with sc2:
        st.markdown(f"""
        <div class="preview-card">
            <h4>Resumen</h4>
            <div class="preview-row">
                <span class="preview-label">Total escenarios</span>
                <span class="preview-value">{len(archivos)}</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Último</span>
                <span class="preview-value">{archivos[0].replace('.json','')}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No hay escenarios guardados. Comience en **Parametrización** para crear uno.")

st.divider()
st.markdown("""
<div class="alerta-info">
    💡 Navegue en orden: <strong>Parametrización → Simulación → Dashboard</strong>
</div>
""", unsafe_allow_html=True)
