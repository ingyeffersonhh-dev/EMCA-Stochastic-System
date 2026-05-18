"""
app/pages/01_parametrizacion.py
Módulo 1: Formulario de parametrización operativa con validación en tiempo real.
Premium dark theme layout.
"""
import streamlit as st
import json
import os
import math

from core.models.parametros import ParametrosEntrada, TipoSuelo, TipoDistribucion
from core.models.resultados import ResultadoSimulacion
import dataclasses

st.markdown("""
<div style="margin-bottom:1.5rem">
    <h1 style="margin:0;font-size:1.8rem;font-weight:800">📋 Parámetros de Operación</h1>
    <p style="color:#8892B0;margin:.2rem 0 0;font-size:.92rem">
        Configure la geometría, logística y variables estocásticas del proyecto
    </p>
</div>
""", unsafe_allow_html=True)

# ── Stepper ────────────────────────────────────────────────────
parametros_ok = "parametros" in st.session_state
stepper_html = '<div class="stepper">'
steps = [
    ("1", "Parametrización", True),
    ("2", "Simulación", parametros_ok),
    ("3", "Dashboard", "resultado" in st.session_state),
]
for i, (num, label, completed) in enumerate(steps):
    status = "completed" if completed else ("active" if i == 0 else "")
    icon = "✅" if completed else num
    stepper_html += f'<div class="stepper-step {status}"><span>{icon}</span><span>{label}</span></div>'
    if i < len(steps) - 1:
        stepper_html += '<span class="stepper-arrow">→</span>'
stepper_html += '</div>'
st.markdown(stepper_html, unsafe_allow_html=True)

# ── Sidebar: Scenarios ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title"><h3 style="font-size:1rem">💾 Escenarios</h3></div>', unsafe_allow_html=True)
    scenarios_dir = "data/scenarios"
    os.makedirs(scenarios_dir, exist_ok=True)
    archivos = [f for f in os.listdir(scenarios_dir) if f.endswith(".json")]

    if archivos:
        escenario_sel = st.selectbox("Seleccione un escenario:", ["— Nuevo —"] + archivos)
        if escenario_sel != "— Nuevo —":
            c_load, c_del = st.columns(2)
            if c_load.button("📂 Cargar", use_container_width=True):
                with open(os.path.join(scenarios_dir, escenario_sel), encoding="utf-8") as f:
                    datos = json.load(f)
                
                if "parametros" in datos:
                    st.session_state["datos_formulario"] = datos["parametros"]
                    st.session_state["parametros"] = ParametrosEntrada.model_validate(datos["parametros"])
                    if "resultado" in datos:
                        st.session_state["resultado"] = ResultadoSimulacion.from_dict(datos["resultado"])
                    elif "resultado" in st.session_state:
                        del st.session_state["resultado"]
                else:
                    st.session_state["datos_formulario"] = datos
                    st.session_state["parametros"] = ParametrosEntrada.model_validate(datos)
                    if "resultado" in st.session_state:
                        del st.session_state["resultado"]
                st.rerun()
            
            if c_del.button("🗑️ Borrar", use_container_width=True, type="secondary"):
                os.remove(os.path.join(scenarios_dir, escenario_sel))
                if "datos_formulario" in st.session_state:
                    prev_name = st.session_state["datos_formulario"].get("nombre_escenario", "")
                    if prev_name == escenario_sel.replace(".json", ""):
                        st.session_state.pop("datos_formulario")
                        if "resultado" in st.session_state:
                            st.session_state.pop("resultado")
                st.rerun()
    else:
        st.info("No hay escenarios guardados aún.")

prev = st.session_state.get("datos_formulario", {})

# ── Form ───────────────────────────────────────────────────────
with st.form("form_parametros", clear_on_submit=False):

    tab1, tab2, tab3, tab4 = st.tabs(["📐 Geometría", "🌍 Entorno & Logística", "📊 Estocásticos", "💾 Guardar Escenario"])
    
    with tab1:
        st.markdown('<div class="section-title"><h3>Dimensiones y Cantidades</h3></div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            diametro = st.number_input("Diámetro del pilote (m)", 0.3, 2.0,
                value=prev.get("diametro_m", 0.6), step=0.05)
        with c2:
            longitud = st.number_input("Longitud del pilote (m)", 5.0, 60.0,
                value=prev.get("longitud_m", 15.0), step=0.5)
        with c3:
            cantidad = st.number_input("Cantidad de pilotes", 1, 499,
                value=prev.get("cantidad_pilotes", 20))

        vol_unit = math.pi * (diametro / 2) ** 2 * longitud
        vol_total = vol_unit * cantidad
        st.markdown(f"""
        <div class="preview-card">
            <h4>📐 Resumen Geométrico</h4>
            <div class="preview-row"><span class="preview-label">Volumen unitario</span>
                <span class="preview-value">{vol_unit:.3f} m³</span></div>
            <div class="preview-row"><span class="preview-label">Volumen total ({cantidad} pilotes)</span>
                <span class="preview-value">{vol_total:.1f} m³</span></div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        c4, c5 = st.columns([1.5, 1])
        with c4:
            st.markdown('<div class="section-title"><h3>Condiciones del Terreno</h3></div>', unsafe_allow_html=True)
            suelo_opts = ["suelo_seco", "suelo_agua"]
            suelo_lbls = {"suelo_seco": "Suelo Seco", "suelo_agua": "Suelo con Agua"}
            suelo_facts = {"suelo_seco": 1.0, "suelo_agua": 1.35}
            
            p_s = prev.get("tipo_suelo", "suelo_seco")
            if p_s not in suelo_opts: p_s = "suelo_seco"
            
            tipo_suelo = st.radio("Tipo de suelo", options=suelo_opts,
                format_func=lambda x: suelo_lbls[x], index=suelo_opts.index(p_s), horizontal=True)
            
            factor = suelo_facts[tipo_suelo]
            sc = "soil-easy" if factor <= 1.1 else "soil-hard"
            
            st.markdown(f'<div style="margin-top:-.5rem;margin-bottom:1rem"><span class="soil-indicator {sc}">{"🟢" if factor<=1.1 else "🔵"} Dificultad: ×{factor}</span></div>', unsafe_allow_html=True)
            uso_lodo = st.checkbox("Usar lodo bentonítico", value=prev.get("uso_lodo_bentonitico", True))

        with c5:
            st.markdown('<div class="section-title"><h3>Velocidad</h3></div>', unsafe_allow_html=True)
            vel_media = st.number_input("V. media (km/h)", 10.0, 119.0, value=prev.get("velocidad_transporte_kmh_media", 60.0), step=5.0)
            vel_std = st.number_input("Desv. Est. (km/h)", 1.0, 30.0, value=prev.get("velocidad_transporte_kmh_std", 10.0), step=1.0)

        st.markdown('<div class="section-title"><h3>Logística de Suministro</h3></div>', unsafe_allow_html=True)
        c6, c7, c8 = st.columns(3)
        with c6:
            num_mixers = st.slider("Mixers activos", 1, 10, value=prev.get("num_mixers", 2))
        with c7:
            distancia = st.number_input("Distancia a planta (km)", 1.0, 199.0, value=prev.get("distancia_proveedor_km", 30.0), step=1.0)
        with c8:
            horas_dia = st.number_input("Jornada (h/día)", 4.0, 24.0, value=prev.get("horas_por_dia", 8.0), step=0.5)

        t_transp = (distancia * 2) / vel_media
        st.markdown(f"""
        <div class="preview-card">
            <h4>🚛 Logística</h4>
            <div class="preview-row"><span class="preview-label">Ciclo viaje (ida/vuelta)</span>
                <span class="preview-value">{t_transp:.2f} h</span></div>
            <div class="preview-row"><span class="preview-label">Productividad potencial máxima</span>
                <span class="preview-value">{num_mixers/t_transp:.1f} viajes/h</span></div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="section-title"><h3>⏱️ Variables Estocásticas (min)</h3></div>', unsafe_allow_html=True)
        
        c9, c10, c11 = st.columns(3)
        with c9:
            t_perf_media = st.number_input("μ Perforación", 30, 2880, value=int(prev.get("tiempo_perforacion_min_media", 240)), step=15)
        with c10:
            t_perf_std = st.number_input("σ Perforación", 5, 600, value=int(prev.get("tiempo_perforacion_min_std", 48)), step=5)
        with c11:
            opts_perf = [e.value for e in TipoDistribucion]
            p_dist_perf = prev.get("dist_perforacion", opts_perf[0])
            if hasattr(p_dist_perf, "value"):
                p_dist_perf = p_dist_perf.value
            idx_perf = opts_perf.index(p_dist_perf) if p_dist_perf in opts_perf else 0
            dist_perf = st.selectbox("Dist. Perforación", opts_perf, index=idx_perf, key="dp")

        c12, c13, c14 = st.columns(3)
        with c12:
            t_colado_media = st.number_input("μ Colado", 15, 1440, value=int(prev.get("tiempo_colado_min_media", 120)), step=15)
        with c13:
            t_colado_std = st.number_input("σ Colado", 2, 300, value=int(prev.get("tiempo_colado_min_std", 30)), step=5)
        with c14:
            opts_col = [e.value for e in TipoDistribucion]
            p_dist_col = prev.get("dist_colado", opts_col[1])
            if hasattr(p_dist_col, "value"):
                p_dist_col = p_dist_col.value
            idx_col = opts_col.index(p_dist_col) if p_dist_col in opts_col else 1
            dist_colado = st.selectbox("Dist. Colado", opts_col, index=idx_col, key="dc")

        t_perf_aj = t_perf_media * factor
        st.markdown(f"""
        <div class="preview-card" style="margin-top:2rem">
            <h4>📊 Resumen Probabilístico</h4>
            <div class="preview-row"><span class="preview-label">Perf. (T. Base)</span>
                <span class="preview-value">{dist_perf} (μ={t_perf_media}m, σ={t_perf_std}m)</span></div>
            <div class="preview-row"><span class="preview-label">Perf. (Ajustado ×{factor})</span>
                <span class="preview-value" style="color:{'#FF6B6B' if factor>1.1 else '#00E68A'}">{t_perf_aj:.0f}m ({t_perf_aj/60:.1f}h)</span></div>
            <div class="preview-row"><span class="preview-label">Colado</span>
                <span class="preview-value">{dist_colado} (μ={t_colado_media}m, σ={t_colado_std}m)</span></div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="section-title"><h3>🏷️ Identificación y Guardado</h3></div>', unsafe_allow_html=True)
        nombre_esc = st.text_input("Nombre de la configuración", value=prev.get("nombre_escenario", "Escenario Base"))
        notas = st.text_area("Observaciones", value=prev.get("notas", ""), height=80)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 Validar y Guardar Escenario", use_container_width=True, type="primary")

# ── Actions ────────────────────────────────────────────────────
if submitted:
    try:
        params = ParametrosEntrada(
            diametro_m=diametro, longitud_m=longitud, cantidad_pilotes=int(cantidad),
            tipo_suelo=tipo_suelo, uso_lodo_bentonitico=uso_lodo,
            num_mixers=int(num_mixers), distancia_proveedor_km=distancia,
            velocidad_transporte_kmh_media=vel_media, velocidad_transporte_kmh_std=vel_std,
            tiempo_perforacion_min_media=float(t_perf_media), tiempo_perforacion_min_std=float(t_perf_std),
            dist_perforacion=TipoDistribucion(dist_perf),
            tiempo_colado_min_media=float(t_colado_media), tiempo_colado_min_std=float(t_colado_std),
            dist_colado=TipoDistribucion(dist_colado),
            horas_por_dia=horas_dia,
            nombre_escenario=nombre_esc, notas=notas or None,
        )

        st.session_state["parametros"] = params
        st.session_state["datos_formulario"] = params.model_dump(mode="json")

        nombre_archivo = f"{nombre_esc.replace(' ', '_')}.json"
        
        data_to_save = {
            "parametros": params.model_dump(mode="json")
        }
        if "resultado" in st.session_state:
            data_to_save["resultado"] = dataclasses.asdict(st.session_state["resultado"])
            
        with open(os.path.join(scenarios_dir, nombre_archivo), "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

        st.markdown(f"""
        <div class="alerta-success" style="margin-bottom:1.5rem">
            ✅ Escenario validado y asegurado: <strong>{nombre_esc}</strong>.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card kpi-accent-cyan">
                <div class="kpi-label">Volumen (m³)</div>
                <div class="kpi-value">{params.volumen_total_m3:.1f}</div>
            </div>
            <div class="kpi-card kpi-accent-purple">
                <div class="kpi-label">T. Transporte</div>
                <div class="kpi-value">{params.tiempo_transporte_h:.1f}h</div>
            </div>
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Días Teóricos</div>
                <div class="kpi-value">{params.dias_estimados:.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f'<div class="alerta-roja">❌ Error de validación: <strong>{e}</strong></div>', unsafe_allow_html=True)
