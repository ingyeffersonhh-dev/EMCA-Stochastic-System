"""
app/pages/01_parametrizacion.py
Module 1: Parametrization — redesigned with step-by-step UX,
visual sliders, and contextual real-time feedback.
"""
import streamlit as st
import json
import os
import math

from core.models.parametros import ParametrosEntrada, TipoSuelo, TipoDistribucion
from core.models.resultados import ResultadoSimulacion
import dataclasses

from app.components.stepper import render_stepper
from app.components.theme import get_active_tokens, _rgba

t = get_active_tokens()

# ── Page header ────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-bottom:1.5rem">
    <h1 style="margin:0;font-size:1.8rem;font-weight:800">📋 Parámetros de Operación</h1>
    <p style="color:{t.TX2};margin:.2rem 0 0;font-size:.92rem">
        Configure la geometría, logística y variables estocásticas del proyecto
    </p>
</div>
""", unsafe_allow_html=True)

if "mensaje_carga" in st.session_state:
    st.markdown(st.session_state["mensaje_carga"], unsafe_allow_html=True)
    del st.session_state["mensaje_carga"]

# ── Stepper ────────────────────────────────────────────────────
parametros_ok = "parametros" in st.session_state
render_stepper(
    [
        ("1", "Parametrización", True),
        ("2", "Simulación", parametros_ok),
        ("3", "Dashboard", "resultado" in st.session_state),
    ],
    current_step=0,
)

# ── Sidebar: Scenarios ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-title"><h3 style="font-size:1rem">💾 Escenarios</h3></div>', unsafe_allow_html=True)
    scenarios_dir = "data/scenarios"
    os.makedirs(scenarios_dir, exist_ok=True)
    archivos = [f for f in os.listdir(scenarios_dir) if f.endswith(".json")]

    if archivos:
        # Botón "Nuevo escenario" siempre visible
        if st.button("➕ Nuevo escenario", use_container_width=True, type="primary"):
            st.session_state.pop("datos_formulario", None)
            st.session_state.pop("parametros", None)
            st.session_state.pop("resultado", None)
            st.rerun()

        # Lista colapsable de escenarios
        with st.expander(f"📁 Escenarios guardados ({len(archivos)})", expanded=False):
            for archivo in sorted(archivos):
                nombre_esc = archivo.replace(".json", "").replace("_", " ")
                col_btn, col_del = st.columns([4, 1])

                with col_btn:
                    if st.button(f"📂 {nombre_esc}", key=f"load_{archivo}", use_container_width=True):
                        with open(os.path.join(scenarios_dir, archivo), encoding="utf-8") as f:
                            datos = json.load(f)

                        tiene_sim = False
                        if "parametros" in datos:
                            st.session_state["datos_formulario"] = datos["parametros"]
                            st.session_state["parametros"] = ParametrosEntrada.model_validate(datos["parametros"])
                            if "resultado" in datos:
                                st.session_state["resultado"] = ResultadoSimulacion.from_dict(datos["resultado"])
                                tiene_sim = True
                            elif "resultado" in st.session_state:
                                del st.session_state["resultado"]
                        else:
                            st.session_state["datos_formulario"] = datos
                            st.session_state["parametros"] = ParametrosEntrada.model_validate(datos)
                            if "resultado" in st.session_state:
                                del st.session_state["resultado"]

                        nombre_cargado = st.session_state["parametros"].nombre_escenario
                        if tiene_sim:
                            st.session_state["mensaje_carga"] = f'<div class="alerta-success" style="margin-bottom:1.5rem">📂 Escenario <strong>{nombre_cargado}</strong> cargado con éxito. Resultados de simulación listos para ver en el Módulo 3.</div>'
                        else:
                            st.session_state["mensaje_carga"] = f'<div class="alerta-info" style="margin-bottom:1.5rem">📂 Escenario <strong>{nombre_cargado}</strong> cargado. Por favor, ejecute la simulación en el Módulo 2 para persistir los resultados.</div>'
                        st.rerun()

                with col_del:
                    if st.button("  🗑️  ", key=f"del_{archivo}"):
                        os.remove(os.path.join(scenarios_dir, archivo))
                        if "datos_formulario" in st.session_state:
                            prev_name = st.session_state["datos_formulario"].get("nombre_escenario", "")
                            if prev_name == archivo.replace(".json", ""):
                                st.session_state.pop("datos_formulario")
                                if "resultado" in st.session_state:
                                    st.session_state.pop("resultado")
                        st.rerun()
    else:
        st.info("No hay escenarios guardados aún.")
        if st.button("➕ Crear primer escenario", use_container_width=True, type="primary"):
            st.session_state.pop("datos_formulario", None)
            st.session_state.pop("parametros", None)
            st.session_state.pop("resultado", None)
            st.rerun()

prev = st.session_state.get("datos_formulario", {})

# ════════════════════════════════════════════════════════════════
# FORM
# ════════════════════════════════════════════════════════════════
with st.form("form_parametros", clear_on_submit=False):

    tab_geom, tab_log, tab_estoc, tab_save = st.tabs([
        "📏 1. Geometría", 
        "🌍 2. Logística", 
        "⏱️ 3. Estocásticos", 
        "💾 4. Guardar"
    ])

    with tab_geom:
        st.markdown(f"""
        <div style="margin-bottom: 1.2rem;">
            <div style="font-weight:700;font-size:1rem;color:{t.TX1}">Geometría del Pilote</div>
            <div style="font-size:.8rem;color:{t.TX2}">Defina las dimensiones físicas y la cantidad de pilotes del proyecto</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            diametro = st.slider(
                "Diámetro (m)",
                min_value=0.3, max_value=2.0,
                value=float(prev.get("diametro_m", 0.6)),
                step=0.05,
                help="Diámetro del pilote colado in situ. Valores típicos: 0.6 m – 1.2 m"
            )
            st.markdown(f'<div style="text-align:center;font-size:1.4rem;font-weight:800;color:{t.ACC};margin-top:-.5rem">{diametro:.2f} m</div>', unsafe_allow_html=True)
        with c2:
            longitud = st.slider(
                "Longitud (m)",
                min_value=5.0, max_value=60.0,
                value=float(prev.get("longitud_m", 15.0)),
                step=0.5,
                help="Longitud de empotramiento del pilote en el suelo"
            )
            st.markdown(f'<div style="text-align:center;font-size:1.4rem;font-weight:800;color:{t.CYAN};margin-top:-.5rem">{longitud:.1f} m</div>', unsafe_allow_html=True)
        with c3:
            cantidad = st.number_input(
                "Cantidad de pilotes",
                min_value=1, max_value=499,
                value=int(prev.get("cantidad_pilotes", 20)),
                step=1,
                help="Número total de pilotes a construir en esta partida"
            )

        area = math.pi * (diametro / 2) ** 2
        vol_unit = area * longitud
        vol_total = vol_unit * cantidad
        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin:1rem 0 0.5rem">
            <div style="background:{_rgba(t.ACC, 0.08)};border:1px solid {_rgba(t.ACC, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Sección transversal</div>
                <div style="color:{t.TX1};font-size:1.2rem;font-weight:800;margin-top:.3rem">{area:.3f} m²</div>
            </div>
            <div style="background:{_rgba(t.CYAN, 0.08)};border:1px solid {_rgba(t.CYAN, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Volumen por pilote</div>
                <div style="color:{t.TX1};font-size:1.2rem;font-weight:800;margin-top:.3rem">{vol_unit:.3f} m³</div>
            </div>
            <div style="background:{_rgba(t.ACC, 0.08)};border:1px solid {_rgba(t.ACC, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Volumen total de hormigón</div>
                <div style="color:{t.ACC};font-size:1.2rem;font-weight:800;margin-top:.3rem">{vol_total:.1f} m³</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab_log:
        st.markdown(f"""
        <div style="margin-bottom: 1.2rem;">
            <div style="font-weight:700;font-size:1rem;color:{t.TX1}">Condiciones del Terreno y Logística</div>
            <div style="font-size:.8rem;color:{t.TX2}">Tipo de suelo, flota de mixers y distancia a la planta concretera</div>
        </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown(f'<p style="font-weight:600;font-size:.9rem;color:{t.TX1};margin-bottom:.5rem">🌍 Tipo de suelo</p>', unsafe_allow_html=True)
            suelo_opts = ["suelo_seco", "suelo_agua"]
            suelo_lbls = {"suelo_seco": "🟢 Suelo Seco  ×1.0", "suelo_agua": "🔵 Suelo con Agua  ×1.35"}
            suelo_facts = {"suelo_seco": 1.0, "suelo_agua": 1.35}
            suelo_descs = {
                "suelo_seco": "Suelo estable sin nivel freático. Condiciones normales de perforación.",
                "suelo_agua": "Presencia de agua subterránea. Requiere lodo bentonítico y mayor tiempo de perforación (+35%)."
            }

            p_s = prev.get("tipo_suelo", "suelo_seco")
            if p_s not in suelo_opts:
                p_s = "suelo_seco"

            tipo_suelo = st.radio(
                "Tipo de suelo",
                options=suelo_opts,
                format_func=lambda x: suelo_lbls[x],
                index=suelo_opts.index(p_s),
                label_visibility="collapsed"
            )
            factor = suelo_facts[tipo_suelo]
            st.markdown(f'<p style="font-size:.82rem;color:{t.TX2};margin-top:-.3rem">{suelo_descs[tipo_suelo]}</p>', unsafe_allow_html=True)

            uso_lodo = st.checkbox(
                "Usar lodo bentonítico",
                value=prev.get("uso_lodo_bentonitico", True),
                help="Estabiliza las paredes de la excavación en suelos blandos o con agua"
            )

        with col_right:
            st.markdown(f'<p style="font-weight:600;font-size:.9rem;color:{t.TX1};margin-bottom:.5rem">⛏️ Perforadoras disponibles</p>', unsafe_allow_html=True)
            num_perforadoras = st.slider(
                "Perforadoras activas",
                min_value=1, max_value=10,
                value=int(prev.get("num_perforadoras", 2)),
                help="Número de equipos de perforación disponibles simultáneamente. Más perforadoras reducen la serialización de la fase de perforación."
            )

            st.markdown(f'<p style="font-weight:600;font-size:.9rem;color:{t.TX1};margin-bottom:.5rem">🚛 Flota de mixers</p>', unsafe_allow_html=True)
            num_mixers = st.slider(
                "Mixers activos",
                min_value=1, max_value=10,
                value=int(prev.get("num_mixers", 2)),
                help="Número de camiones mixer disponibles simultáneamente para el suministro de hormigón"
            )

            capacidad_mixer = st.number_input(
                "Capacidad mixer (m³)",
                min_value=1.0, max_value=15.0,
                value=float(prev.get("capacidad_mixer_m3", 6.0)),
                step=0.5,
                help="Volumen útil de hormigón que transporta cada mixer"
            )

            distancia = st.slider(
                "Distancia a planta (km)",
                min_value=1.0, max_value=150.0,
                value=float(prev.get("distancia_proveedor_km", 30.0)),
                step=1.0,
                help="Distancia en km desde la planta concretera hasta la obra (solo ida)"
            )

            col_vel1, col_vel2 = st.columns(2)
            with col_vel1:
                vel_media = st.number_input(
                    "V. media (km/h)",
                    min_value=10.0, max_value=119.0,
                    value=float(prev.get("velocidad_transporte_kmh_media", 60.0)),
                    step=5.0,
                    help="Velocidad promedio del mixer en tránsito"
                )
            with col_vel2:
                vel_std = st.number_input(
                    "Desv. velocidad (km/h)",
                    min_value=1.0, max_value=30.0,
                    value=float(prev.get("velocidad_transporte_kmh_std", 10.0)),
                    step=1.0,
                    help="Desviación estándar de la velocidad de transporte (variabilidad del tráfico)"
                )

            horas_dia = st.number_input(
                "Jornada laboral (h/día)",
                min_value=4.0, max_value=24.0,
                value=float(prev.get("horas_por_dia", 8.0)),
                step=0.5,
                help="Horas de trabajo efectivas por día"
            )

        t_transp = (distancia * 2) / vel_media
        viajes_dia = horas_dia / t_transp if t_transp > 0 else 0
        viajes_por_pilote = math.ceil(vol_unit / capacidad_mixer) if capacidad_mixer > 0 else 1
        viajes_totales = viajes_por_pilote * cantidad

        mixer_ok = num_mixers >= math.ceil(t_transp)
        perforadora_ok = num_perforadoras > 1 or cantidad <= num_perforadoras
        color_estado = t.GREEN if (mixer_ok and perforadora_ok) else t.YELLOW
        if not mixer_ok and not perforadora_ok:
            msg_estado = "⚠️ Posibles cuellos de botella en mixer y perforación"
        elif not mixer_ok:
            msg_estado = "⚠️ Flota de mixers puede ser insuficiente"
        elif not perforadora_ok:
            msg_estado = "⚠️ Posible cuello de botella en perforación"
        else:
            msg_estado = "✅ Recursos suficientes"

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:.75rem;margin:1rem 0 0.5rem">
            <div style="background:{_rgba(t.RED, 0.08)};border:1px solid {_rgba(t.RED, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Ciclo de viaje</div>
                <div style="color:{t.TX1};font-size:1.2rem;font-weight:800;margin-top:.3rem">{t_transp:.2f} h</div>
            </div>
            <div style="background:{_rgba(t.YELLOW, 0.08)};border:1px solid {_rgba(t.YELLOW, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Viajes/día por mixer</div>
                <div style="color:{t.TX1};font-size:1.2rem;font-weight:800;margin-top:.3rem">{viajes_dia:.1f}</div>
            </div>
            <div style="background:{_rgba(t.ACC, 0.08)};border:1px solid {_rgba(t.ACC, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Viajes por pilote</div>
                <div style="color:{t.TX1};font-size:1.2rem;font-weight:800;margin-top:.3rem">{viajes_por_pilote}</div>
            </div>
            <div style="background:{_rgba(t.ACC, 0.06)};border:1px solid {_rgba(t.ACC, 0.15)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Estado flota</div>
                <div style="color:{color_estado};font-size:.9rem;font-weight:700;margin-top:.5rem">{msg_estado}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.75rem;margin:.5rem 0 0.5rem">
            <div style="background:{_rgba(t.CYAN, 0.08)};border:1px solid {_rgba(t.CYAN, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Viajes totales estimados</div>
                <div style="color:{t.TX1};font-size:1.2rem;font-weight:800;margin-top:.3rem">{viajes_totales}</div>
            </div>
            <div style="background:{_rgba(t.ACC, 0.08)};border:1px solid {_rgba(t.ACC, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Viajes/día (flota)</div>
                <div style="color:{t.TX1};font-size:1.2rem;font-weight:800;margin-top:.3rem">{viajes_dia*num_mixers:.1f}</div>
            </div>
            <div style="background:{_rgba(t.PURPLE, 0.08)};border:1px solid {_rgba(t.PURPLE, 0.2)};
                border-radius:12px;padding:1rem;text-align:center">
                <div style="color:{t.TX2};font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;font-weight:600">Capacidad mixer</div>
                <div style="color:{t.TX1};font-size:1.2rem;font-weight:800;margin-top:.3rem">{capacidad_mixer:.1f} m³</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if viajes_por_pilote > 10:
            st.markdown(f"""
            <div class="alerta-roja" style="margin-top:1rem">
                ⚠️ <strong>Pilote de gran volumen:</strong> se requieren <strong>{viajes_por_pilote} viajes</strong> por pilote.
                Considerá aumentar la capacidad del mixer o evaluar el suministro con bomba de hormigón.
            </div>
            """, unsafe_allow_html=True)

    with tab_estoc:
        st.markdown(f"""
        <div style="margin-bottom: 1.2rem;">
            <div style="font-weight:700;font-size:1rem;color:{t.TX1}">Variables Estocásticas (Tiempos)</div>
            <div style="font-size:.8rem;color:{t.TX2}">Defina la distribución probabilística de los tiempos de perforación y colado (en minutos)</div>
        </div>
        """, unsafe_allow_html=True)

        col_perf, col_col = st.columns(2)

        with col_perf:
            st.markdown(f'<div style="background:{_rgba(t.ACC, 0.06)};border:1px solid {_rgba(t.ACC, 0.2)};border-radius:14px;padding:1.2rem">', unsafe_allow_html=True)
            st.markdown(f'<p style="font-weight:700;font-size:.95rem;color:{t.ACC};margin:0 0 1rem">🔩 Perforación</p>', unsafe_allow_html=True)

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                t_perf_media = st.number_input(
                    "Media μ (min)",
                    min_value=30, max_value=2880,
                    value=int(prev.get("tiempo_perforacion_min_media", 240)),
                    step=15,
                    help="Tiempo promedio de perforación por pilote en minutos"
                )
            with col_p2:
                t_perf_std = st.number_input(
                    "Desv. σ (min)",
                    min_value=5, max_value=600,
                    value=int(prev.get("tiempo_perforacion_min_std", 48)),
                    step=5,
                    help="Variabilidad del tiempo de perforación (desviación estándar)"
                )

            opts_perf = [e.value for e in TipoDistribucion]
            p_dist_perf = prev.get("dist_perforacion", opts_perf[0])
            if hasattr(p_dist_perf, "value"):
                p_dist_perf = p_dist_perf.value
            idx_perf = opts_perf.index(p_dist_perf) if p_dist_perf in opts_perf else 0
            dist_perf = st.selectbox("Distribución", opts_perf, index=idx_perf, key="dp", help="Distribución estadística que modela el tiempo de perforación")

            t_perf_aj = t_perf_media * factor
            color_perf = t.RED if factor > 1.1 else t.GREEN
            st.markdown(f"""
            <div style="margin-top:.8rem;padding:.6rem .8rem;background:{_rgba(t.TX1, 0.06)};border-radius:8px">
                <span style="font-size:.8rem;color:{t.TX2}">Tiempo ajustado por suelo:</span>
                <span style="font-size:.9rem;font-weight:700;color:{color_perf};margin-left:.4rem">{t_perf_aj:.0f} min ({t_perf_aj/60:.1f}h)</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_col:
            st.markdown(f'<div style="background:{_rgba(t.ACC, 0.06)};border:1px solid {_rgba(t.ACC, 0.2)};border-radius:14px;padding:1.2rem">', unsafe_allow_html=True)
            st.markdown(f'<p style="font-weight:700;font-size:.95rem;color:{t.ACC};margin:0 0 1rem">🪣 Colado</p>', unsafe_allow_html=True)

            col_c1, col_c2 = st.columns(2)
            with col_c1:
                t_colado_media = st.number_input(
                    "Media μ (min)",
                    min_value=15, max_value=1440,
                    value=int(prev.get("tiempo_colado_min_media", 120)),
                    step=15,
                    help="Tiempo promedio de colado de hormigón por pilote en minutos"
                )
            with col_c2:
                t_colado_std = st.number_input(
                    "Desv. σ (min)",
                    min_value=2, max_value=300,
                    value=int(prev.get("tiempo_colado_min_std", 30)),
                    step=5,
                    help="Variabilidad del tiempo de colado"
                )

            opts_col = [e.value for e in TipoDistribucion]
            p_dist_col = prev.get("dist_colado", opts_col[1])
            if hasattr(p_dist_col, "value"):
                p_dist_col = p_dist_col.value
            idx_col = opts_col.index(p_dist_col) if p_dist_col in opts_col else 1
            dist_colado = st.selectbox("Distribución", opts_col, index=idx_col, key="dc", help="Distribución estadística que modela el tiempo de colado")

            ciclo_est = (t_perf_aj + t_colado_media) / 60
            st.markdown(f"""
            <div style="margin-top:.8rem;padding:.6rem .8rem;background:{_rgba(t.TX1, 0.06)};border-radius:8px">
                <span style="font-size:.8rem;color:{t.TX2}">Ciclo estimado por pilote:</span>
                <span style="font-size:.9rem;font-weight:700;color:{t.CYAN};margin-left:.4rem">{ciclo_est:.1f}h</span>
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab_save:
        st.markdown(f"""
        <div style="margin-bottom: 1.2rem;">
            <div style="font-weight:700;font-size:1rem;color:{t.TX1}">Identificación y Guardado</div>
            <div style="font-size:.8rem;color:{t.TX2}">Asigne un nombre a este escenario para guardarlo y poder compararlo después</div>
        </div>
        """, unsafe_allow_html=True)

        col_s1, col_s2 = st.columns([2, 1])
        with col_s1:
            nombre_esc = st.text_input(
                "Nombre del escenario",
                value=prev.get("nombre_escenario", "Escenario Base"),
                placeholder="Ej: Suelo seco — 3 mixers — 20 pilotes",
                help="Nombre único para identificar esta configuración. Se guardará en data/scenarios/"
            )
        with col_s2:
            notas = st.text_area("Notas (opcional)", value=prev.get("notas", ""), height=68, placeholder="Observaciones adicionales...")

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 Validar y Guardar Escenario", use_container_width=True, type="primary")

# ── Actions ────────────────────────────────────────────────────
if submitted:
    try:
        params = ParametrosEntrada(
            diametro_m=diametro, longitud_m=longitud, cantidad_pilotes=int(cantidad),
            tipo_suelo=tipo_suelo, uso_lodo_bentonitico=uso_lodo,
            num_mixers=int(num_mixers), num_perforadoras=int(num_perforadoras),
            capacidad_mixer_m3=float(capacidad_mixer),
            distancia_proveedor_km=distancia,
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
        data_to_save = {"parametros": params.model_dump(mode="json")}
        if "resultado" in st.session_state:
            data_to_save["resultado"] = dataclasses.asdict(st.session_state["resultado"])

        with open(os.path.join(scenarios_dir, nombre_archivo), "w", encoding="utf-8") as f:
            json.dump(data_to_save, f, indent=2, ensure_ascii=False)

        st.markdown(f"""
        <div class="alerta-success" style="margin-bottom:1.5rem">
            ✅ Escenario <strong>{nombre_esc}</strong> validado y guardado correctamente.
            Puede proceder a la simulación en el Módulo 2.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card kpi-accent-cyan">
                <div class="kpi-label">Volumen total (m³)</div>
                <div class="kpi-value">{params.volumen_total_m3:.1f}</div>
            </div>
            <div class="kpi-card kpi-accent-purple">
                <div class="kpi-label">T. Transporte (h)</div>
                <div class="kpi-value">{params.tiempo_transporte_h:.1f}</div>
            </div>
            <div class="kpi-card kpi-accent-green">
                <div class="kpi-label">Días Teóricos</div>
                <div class="kpi-value">{params.dias_estimados:.1f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.markdown(f'<div class="alerta-roja">❌ Error de validación: <strong>{e}</strong></div>', unsafe_allow_html=True)
