"""
app/pages/01_parametrizacion.py
Módulo 1: Formulario de parametrización operativa con validación en tiempo real.
Tiempos en minutos, tipo de suelo simplificado, velocidad variable.
"""
import streamlit as st
import json
import os
import math
from datetime import datetime

from core.models.parametros import ParametrosEntrada, TipoSuelo, TipoDistribucion

st.title("📋 Módulo 1 — Parametrización Operativa")
st.caption("Complete todos los campos para configurar el escenario de simulación.")

# --- Stepper ---
parametros_ok = "parametros" in st.session_state
stepper_html = '<div class="stepper">'
steps = [
    ("1", "Parametrización", True),
    ("2", "Simulación", parametros_ok),
    ("3", "Dashboard", parametros_ok),
]
for i, (num, label, completed) in enumerate(steps):
    status = "completed" if completed else ("active" if i == 0 else "")
    icon = "✅" if completed else num
    stepper_html += f'<div class="stepper-step {status}"><span>{icon}</span><span>{label}</span></div>'
    if i < len(steps) - 1:
        stepper_html += '<span class="stepper-arrow">→</span>'
stepper_html += '</div>'
st.markdown(stepper_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Cargar escenario guardado (sidebar)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.subheader("💾 Gestión de Escenarios")
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
                st.session_state["datos_formulario"] = datos
                st.success(f"Cargado: {escenario_sel}")
                st.rerun()
            
            if c_del.button("🗑️ Borrar", use_container_width=True, type="secondary"):
                os.remove(os.path.join(scenarios_dir, escenario_sel))
                if "datos_formulario" in st.session_state and st.session_state["datos_formulario"].get("nombre_escenario") == escenario_sel.replace(".json", ""):
                    st.session_state.pop("datos_formulario")
                st.success("Escenario eliminado.")
                st.rerun()
    else:
        st.info("No hay escenarios guardados aún.")

prev = st.session_state.get("datos_formulario", {})

# ---------------------------------------------------------------------------
# Formulario (Pestañas)
# ---------------------------------------------------------------------------
with st.form("form_parametros", clear_on_submit=False):

    tab1, tab2, tab3, tab4 = st.tabs(["📐 Geometría", "🌍 Entorno & Logística", "📊 Estocásticos", "💾 Guardar Escenario"])
    
    with tab1:
        st.subheader("Dimensiones y Cantidades")
        c1, c2, c3 = st.columns(3)
        with c1:
            diametro = st.number_input(
                "Diámetro del pilote (m)", 0.3, 2.0,
                value=prev.get("diametro_m", 0.6), step=0.05,
                help="Diámetro de la sección circular del pilote"
            )
        with c2:
            longitud = st.number_input(
                "Longitud del pilote (m)", 5.0, 60.0,
                value=prev.get("longitud_m", 15.0), step=0.5,
                help="Profundidad total de perforación del pilote"
            )
        with c3:
            cantidad = st.number_input(
                "Cantidad de pilotes", 1, 499,
                value=prev.get("cantidad_pilotes", 20),
                help="Número total de pilotes a perforar y colar"
            )

        # Preview en vivo del volumen
        vol_unit = math.pi * (diametro / 2) ** 2 * longitud
        vol_total = vol_unit * cantidad
        st.markdown(f"""
        <div class="preview-card">
            <h4>📐 Resumen Geométrico</h4>
            <div class="preview-row">
                <span class="preview-label">Volumen por pilote</span>
                <span class="preview-value">{vol_unit:.3f} m³</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Volumen total ({cantidad} pilotes)</span>
                <span class="preview-value">{vol_total:.1f} m³</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.subheader("Condiciones del Terreno")
        
        suelo_options = ["suelo_seco", "suelo_agua"]
        suelo_labels = {"suelo_seco": "Suelo Seco", "suelo_agua": "Suelo con Presencia de Agua"}
        suelo_factores = {"suelo_seco": 1.0, "suelo_agua": 1.35}
        
        prev_suelo = prev.get("tipo_suelo", "suelo_seco")
        if prev_suelo not in suelo_options:
            prev_suelo = "suelo_seco"
        
        tipo_suelo = st.radio(
            "Tipo de suelo",
            options=suelo_options,
            format_func=lambda x: suelo_labels[x],
            index=suelo_options.index(prev_suelo),
            horizontal=True,
            help="Seleccione la condición del suelo en el sitio"
        )
        
        factor = suelo_factores[tipo_suelo]
        if factor <= 1.1:
            soil_class = "soil-easy"
            soil_icon = "🟢"
        else:
            soil_class = "soil-hard"
            soil_icon = "🔵"
        
        st.markdown(f"""
        <div class="soil-indicator {soil_class}">
            {soil_icon} Factor de dificultad: ×{factor}
        </div>
        """, unsafe_allow_html=True)

        uso_lodo = st.checkbox(
            "Uso de lodo bentonítico", 
            value=prev.get("uso_lodo_bentonitico", True),
            help="Estabiliza las paredes de la perforación en suelos inestables"
        )

        st.subheader("Logística de Suministro")
        c6, c7, c8 = st.columns(3)
        with c6:
            num_mixers = st.slider(
                "Número de mixers", 1, 10, 
                value=prev.get("num_mixers", 2),
                help="Cantidad de camiones mixer disponibles"
            )
        with c7:
            distancia = st.number_input(
                "Distancia al proveedor (km)", 1.0, 199.0,
                value=prev.get("distancia_proveedor_km", 30.0), step=1.0,
                help="Distancia desde la obra hasta la planta de concreto"
            )
        with c8:
            horas_dia = st.number_input(
                "Horas de trabajo por día", 4.0, 24.0,
                value=prev.get("horas_por_dia", 8.0), step=0.5,
                help="Jornada laboral diaria (por defecto 8 horas)"
            )

        st.subheader("Velocidad de Transporte")
        st.caption("La velocidad no es constante — se modela con distribución normal")
        c9, c10 = st.columns(2)
        with c9:
            vel_media = st.number_input(
                "Velocidad media (km/h)", 10.0, 119.0,
                value=prev.get("velocidad_transporte_kmh_media", 60.0), step=5.0,
                help="Velocidad promedio de los camiones mixer"
            )
        with c10:
            vel_std = st.number_input(
                "Desv. Est. velocidad (km/h)", 1.0, 30.0,
                value=prev.get("velocidad_transporte_kmh_std", 10.0), step=1.0,
                help="Variabilidad de la velocidad (tráfico, condiciones viales)"
            )
        
        # Preview de tiempo de transporte
        t_transporte = (distancia * 2) / vel_media
        st.markdown(f"""
        <div class="preview-card">
            <h4>🚛 Resumen Logístico</h4>
            <div class="preview-row">
                <span class="preview-label">Tiempo viaje (ida y vuelta)</span>
                <span class="preview-value">{t_transporte:.2f} h ({t_transporte*60:.0f} min)</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Mixers disponibles</span>
                <span class="preview-value">{num_mixers}</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Jornada laboral</span>
                <span class="preview-value">{horas_dia:.1f} h/día</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.subheader("⏱️ Tiempos de Perforación (en minutos)")
        st.caption("Ingrese los tiempos estimados en minutos por pilote")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            t_perf_media = st.number_input(
                "Media tiempo perforación (min)", 30, 2880,
                value=int(prev.get("tiempo_perforacion_min_media", 240)), step=15,
                help="Tiempo promedio de perforación por pilote"
            )
        with c2:
            t_perf_std = st.number_input(
                "Desv. Est. perforación (min)", 5, 600,
                value=int(prev.get("tiempo_perforacion_min_std", 48)), step=5,
                help="Variabilidad del tiempo de perforación"
            )
        with c3:
            dist_perf = st.selectbox(
                "Distribución", [e.value for e in TipoDistribucion],
                index=0, key="dist_perf",
                help="Lognormal: recomendada para tiempos de construcción"
            )

        # Ajuste por tipo de suelo
        factor_suelo = suelo_factores[tipo_suelo]
        t_perf_ajustado = t_perf_media * factor_suelo
        st.markdown(f"""
        <div class="preview-card">
            <h4>🔧 Perforación Ajustada</h4>
            <div class="preview-row">
                <span class="preview-label">Tiempo base</span>
                <span class="preview-value">{t_perf_media} min ({t_perf_media/60:.1f} h)</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Factor suelo</span>
                <span class="preview-value">×{factor_suelo}</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Tiempo ajustado</span>
                <span class="preview-value">{t_perf_ajustado:.0f} min ({t_perf_ajustado/60:.1f} h)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🪣 Tiempos de Colado de Concreto (en minutos)")
        st.caption("Tiempo de vaciado de concreto por pilote")
        
        c4, c5 = st.columns(2)
        with c4:
            t_colado_media = st.number_input(
                "Media tiempo colado (min)", 15, 1440,
                value=int(prev.get("tiempo_colado_min_media", 120)), step=15,
                help="Tiempo promedio de vaciado de concreto por pilote"
            )
        with c5:
            dist_colado = st.selectbox(
                "Distribución (Colado)", [e.value for e in TipoDistribucion],
                index=1, key="dist_colado",
                help="Exponential: común para tiempos de servicio"
            )

        # Resumen estocástico
        st.markdown(f"""
        <div class="preview-card">
            <h4>📊 Configuración Estocástica</h4>
            <div class="preview-row">
                <span class="preview-label">Perforación</span>
                <span class="preview-value">{dist_perf} (μ={t_perf_media} min, σ={t_perf_std} min)</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Colado</span>
                <span class="preview-value">{dist_colado} (μ={t_colado_media} min)</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Velocidad transporte</span>
                <span class="preview-value">Normal (μ={vel_media} km/h, σ={vel_std} km/h)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        st.subheader("🏷️ Metadatos y Guardado")
        nombre_esc = st.text_input(
            "Nombre del escenario", 
            value=prev.get("nombre_escenario", "Escenario Base"),
            help="Nombre descriptivo para identificar este escenario"
        )
        notas = st.text_area(
            "Notas / Observaciones", 
            value=prev.get("notas", ""), 
            height=80,
            help="Observaciones adicionales del proyecto"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 Validar y Guardar Parámetros", use_container_width=True, type="primary")

# ---------------------------------------------------------------------------
# Validación y persistencia
# ---------------------------------------------------------------------------
if submitted:
    try:
        params = ParametrosEntrada(
            diametro_m=diametro, longitud_m=longitud, cantidad_pilotes=int(cantidad),
            tipo_suelo=tipo_suelo, uso_lodo_bentonitico=uso_lodo,
            num_mixers=int(num_mixers), distancia_proveedor_km=distancia,
            velocidad_transporte_kmh_media=vel_media, velocidad_transporte_kmh_std=vel_std,
            tiempo_perforacion_min_media=float(t_perf_media), tiempo_perforacion_min_std=float(t_perf_std),
            dist_perforacion=TipoDistribucion(dist_perf),
            tiempo_colado_min_media=float(t_colado_media),
            dist_colado=TipoDistribucion(dist_colado),
            horas_por_dia=horas_dia,
            nombre_escenario=nombre_esc, notas=notas or None,
        )

        st.session_state["parametros"] = params
        st.session_state["datos_formulario"] = params.model_dump(mode="json")

        # Guardar JSON
        nombre_archivo = f"{nombre_esc.replace(' ', '_')}.json"
        archivo_json = os.path.join(scenarios_dir, nombre_archivo)
        with open(archivo_json, "w", encoding="utf-8") as f:
            json.dump(params.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

        st.markdown(f"""
        <div class="alerta-success">
            ✅ Parámetros validados y guardados correctamente como <strong>{nombre_esc}</strong>.
        </div>
        """, unsafe_allow_html=True)

        # Resumen rápido
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        col_r1.metric("Vol. por pilote (m³)", f"{params.volumen_pilote_m3:.2f}")
        col_r2.metric("Vol. total (m³)", f"{params.volumen_total_m3:.1f}")
        col_r3.metric("T. transporte (h/viaje)", f"{params.tiempo_transporte_h:.2f}")
        col_r4.metric("Días estimados", f"{params.dias_estimados:.1f}")

        st.markdown(f"""
        <div class="alerta-info">
            ➡️ Proceda al <strong>Módulo 2 — Simulación</strong> en el menú lateral.
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f"""
        <div class="alerta-roja">
            ❌ Error de validación: <strong>{e}</strong>
        </div>
        """, unsafe_allow_html=True)
