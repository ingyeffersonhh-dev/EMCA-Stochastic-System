"""
app/pages/01_parametrizacion.py
Módulo 1: Formulario de parametrización operativa con validación en tiempo real,
preview en vivo e indicador visual de tipo de suelo.
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
                help="Diámetro de la sección circular del pilote. Valores típicos: 0.4–1.2m"
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
        import math
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
            <div class="preview-row">
                <span class="preview-label">Área de sección</span>
                <span class="preview-value">{math.pi * (diametro/2)**2:.4f} m²</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.subheader("Condiciones del Terreno")
        c4, c5 = st.columns(2)
        with c4:
            tipo_suelo_vals = [e.value for e in TipoSuelo]
            tipo_suelo_labels = {e.value: e.label for e in TipoSuelo}
            tipo_suelo = st.selectbox(
                "Tipo de suelo",
                options=tipo_suelo_vals,
                format_func=lambda x: tipo_suelo_labels[x],
                index=tipo_suelo_vals.index(prev.get("tipo_suelo", "arcilla_blanda")),
                help="Seleccione el tipo de suelo predominante en el sitio"
            )
            
            # Indicador visual del tipo de suelo
            factor = TipoSuelo(tipo_suelo).factor_dificultad
            if factor <= 1.1:
                soil_class = "soil-easy"
                soil_icon = "🟢"
            elif factor <= 1.3:
                soil_class = "soil-medium"
                soil_icon = "🟡"
            else:
                soil_class = "soil-hard"
                soil_icon = "🔴"
            
            st.markdown(f"""
            <div class="soil-indicator {soil_class}">
                {soil_icon} Factor de dificultad: ×{factor}
            </div>
            """, unsafe_allow_html=True)
            
        with c5:
            uso_lodo = st.checkbox(
                "Uso de lodo bentonítico", 
                value=prev.get("uso_lodo_bentonitico", True),
                help="El lodo bentonítico estabiliza las paredes de la perforación en suelos inestables"
            )

        st.subheader("Logística de Suministro")
        c6, c7, c8 = st.columns(3)
        with c6:
            num_mixers = st.slider(
                "Número de mixers", 1, 10, 
                value=prev.get("num_mixers", 2),
                help="Cantidad de camiones mixer disponibles para suministro de concreto"
            )
        with c7:
            distancia = st.number_input(
                "Distancia al proveedor (km)", 1.0, 199.0,
                value=prev.get("distancia_proveedor_km", 30.0), step=1.0,
                help="Distancia desde la obra hasta la planta de concreto"
            )
        with c8:
            velocidad = st.number_input(
                "Velocidad de transporte (km/h)", 10.0, 119.0,
                value=prev.get("velocidad_transporte_kmh", 60.0),
                help="Velocidad promedio de los camiones mixer (considerar tráfico)"
            )
        
        # Preview de tiempo de transporte
        t_transporte = (distancia * 2) / velocidad
        st.markdown(f"""
        <div class="preview-card">
            <h4>🚛 Resumen Logístico</h4>
            <div class="preview-row">
                <span class="preview-label">Tiempo de viaje (ida y vuelta)</span>
                <span class="preview-value">{t_transporte:.2f} h</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Mixers disponibles</span>
                <span class="preview-value">{num_mixers}</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Capacidad estimada</span>
                <span class="preview-value">{num_mixers / max(t_transporte, 0.1):.1f} viajes/h</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        st.subheader("⏱️ Tiempos de Perforación")
        c9, c10, c11 = st.columns(3)
        with c9:
            t_perf_media = st.number_input(
                "Media tiempo perforación (h)", 0.5, 47.9,
                value=prev.get("tiempo_perforacion_h_media", 4.0), step=0.25,
                help="Tiempo promedio de perforación por pilote (incluye preparación)"
            )
        with c10:
            t_perf_std = st.number_input(
                "Desv. Est. tiempo perforación (h)", 0.1, 10.0,
                value=prev.get("tiempo_perforacion_h_std", 0.8), step=0.1,
                help="Desviación estándar del tiempo de perforación (típicamente media/4 a media/5)"
            )
        with c11:
            dist_perf = st.selectbox(
                "Distribución", [e.value for e in TipoDistribucion],
                index=0, key="dist_perf",
                help="Lognormal: recomendada para tiempos de construcción. Exponential: para procesos sin memoria."
            )

        # Ajuste por tipo de suelo
        factor_suelo = TipoSuelo(tipo_suelo).factor_dificultad
        t_perf_ajustado = t_perf_media * factor_suelo
        st.markdown(f"""
        <div class="preview-card">
            <h4>🔧 Perforación Ajustada</h4>
            <div class="preview-row">
                <span class="preview-label">Tiempo base</span>
                <span class="preview-value">{t_perf_media:.2f} h</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Factor suelo ({tipo_suelo_labels[tipo_suelo]})</span>
                <span class="preview-value">×{factor_suelo}</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Tiempo ajustado</span>
                <span class="preview-value">{t_perf_ajustado:.2f} h</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("🪣 Tiempos de Colado de Concreto")
        c12, c13 = st.columns(2)
        with c12:
            t_colado_media = st.number_input(
                "Media tiempo colado (h)", 0.0, 23.9,
                value=prev.get("tiempo_colado_h_media", 2.0), step=0.25,
                help="Tiempo promedio de vaciado de concreto por pilote"
            )
        with c13:
            dist_colado = st.selectbox(
                "Distribución (Colado)", [e.value for e in TipoDistribucion],
                index=1, key="dist_colado",
                help="Exponential: común para tiempos de servicio. Uniforme: cuando hay límites claros."
            )

        # Resumen estocástico
        st.markdown(f"""
        <div class="preview-card">
            <h4>📊 Configuración Estocástica</h4>
            <div class="preview-row">
                <span class="preview-label">Perforación</span>
                <span class="preview-value">{dist_perf} (μ={t_perf_media:.1f}h, σ={t_perf_std:.1f}h)</span>
            </div>
            <div class="preview-row">
                <span class="preview-label">Colado</span>
                <span class="preview-value">{dist_colado} (μ={t_colado_media:.1f}h)</span>
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
            help="Observaciones adicionales, condiciones especiales del proyecto, etc."
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
            tipo_suelo=TipoSuelo(tipo_suelo), uso_lodo_bentonitico=uso_lodo,
            num_mixers=int(num_mixers), distancia_proveedor_km=distancia,
            velocidad_transporte_kmh=velocidad,
            tiempo_perforacion_h_media=t_perf_media, tiempo_perforacion_h_std=t_perf_std,
            dist_perforacion=TipoDistribucion(dist_perf),
            tiempo_colado_h_media=t_colado_media,
            dist_colado=TipoDistribucion(dist_colado),
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
        col_r4.metric("T. perf. ajustado (h)", f"{params.tiempo_perforacion_ajustado_media:.2f}")

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
