"""
core/simulation/engine.py
Motor principal de simulación: SimPy (eventos discretos) + Monte Carlo.
Orquesta el proceso completo de perforación y colado de pilotes.
"""
from __future__ import annotations

from typing import List
import numpy as np
import simpy
from loguru import logger

from core.models.parametros import ParametrosEntrada
from core.models.resultados import EventoPilote, KPIs, ResultadoSimulacion
from core.stochastic.distribuciones import generar_muestras, calcular_percentiles


# ---------------------------------------------------------------------------
# Proceso SimPy para un pilote
# ---------------------------------------------------------------------------

def _proceso_pilote(
    env: simpy.Environment,
    pilote_id: int,
    perforadora: simpy.Resource,
    mixer: simpy.Resource,
    viajes: int,
    t_perforacion: float,
    t_transporte: np.ndarray,
    t_colado: np.ndarray,
    log: List[EventoPilote],
) -> simpy.events.ProcessGenerator:
    """
    Proceso de ciclo completo de un pilote:
      1. Solicitar perforadora y perforar
      2. Para cada viaje del mixer:
         a. Solicitar mixer disponible
         b. Transporte del concreto (tiempo viaje ida+vuelta)
         c. Colado de concreto
         d. Liberar mixer (otros pilotes pueden usarlo entre viajes)
    """
    evento = EventoPilote(pilote_id=pilote_id)

    # Fase 1: Solicitar perforadora y perforar
    evento.inicio_espera_perforadora = env.now
    with perforadora.request() as perf_req:
        yield perf_req
        evento.fin_espera_perforadora = env.now
        evento.inicio_perforacion = env.now
        yield env.timeout(t_perforacion)
        evento.fin_perforacion = env.now

    # Fase 2: Loop de viajes de mixer
    evento.inicio_espera_mixer = env.now
    for viaje_idx in range(viajes):
        with mixer.request() as req:
            yield req
            if viaje_idx == 0:
                evento.fin_espera_mixer = env.now  # Fin de espera en cola (primer viaje)

            # Transporte (muestra estocástica por viaje)
            yield env.timeout(float(t_transporte[viaje_idx]))

            # Colado (muestra estocástica por viaje)
            if viaje_idx == 0:
                evento.inicio_colado = env.now
            yield env.timeout(float(t_colado[viaje_idx]))

            evento.tiempo_total_transporte_h += float(t_transporte[viaje_idx])
            evento.tiempo_total_colado_h += float(t_colado[viaje_idx])

    evento.fin_colado = env.now
    evento.viajes_mixer = viajes

    log.append(evento)


# ---------------------------------------------------------------------------
# Motor principal
# ---------------------------------------------------------------------------

def ejecutar_simulacion(
    params: ParametrosEntrada,
    n_replicas: int = 500,
    seed: int = 42,
) -> ResultadoSimulacion:
    """
    Ejecuta n réplicas de Monte Carlo sobre el motor de eventos discretos SimPy.

    Args:
        params: Parámetros validados del proyecto.
        n_replicas: Número de corridas Monte Carlo.
        seed: Semilla base para reproducibilidad.

    Returns:
        ResultadoSimulacion con KPIs, eventos de la réplica base y distribución de tiempos.
    """
    logger.info(
        f"Iniciando simulación: {params.cantidad_pilotes} pilotes × "
        f"{n_replicas} réplicas | {params.num_mixers} mixer(s)"
    )

    # --- Pre-generar todas las muestras aleatorias (vectorizado) ---
    # Tiempos en horas para el motor SimPy
    t_perf_ajustada_h = params.tiempo_perforacion_ajustado_media
    t_perf_std_h = params.tiempo_perforacion_h_std
    t_colado_media_h = params.tiempo_colado_h_media
    t_colado_std_h = params.tiempo_colado_h_std

    viajes = params.viajes_por_pilote
    pilotes = params.cantidad_pilotes

    t_perforaciones = generar_muestras(
        params.dist_perforacion.value,
        media=t_perf_ajustada_h,
        std=t_perf_std_h,
        n=pilotes * n_replicas,
        seed=seed,
    ).reshape(n_replicas, pilotes)

    # Tiempos de colado por viaje: matriz 3D (réplica × pilote × viaje)
    t_colados = generar_muestras(
        params.dist_colado.value,
        media=t_colado_media_h,
        std=t_colado_std_h,
        n=pilotes * n_replicas * viajes,
        seed=seed + 1,
    ).reshape(n_replicas, pilotes, viajes)

    # Tiempo de transporte con velocidad variable (distribución normal)
    t_transporte_base = params.tiempo_transporte_h
    # Generar variabilidad de transporte basada en velocidad
    t_transportes = generar_muestras(
        "normal",
        media=t_transporte_base,
        std=t_transporte_base * (params.velocidad_transporte_kmh_std / params.velocidad_transporte_kmh_media),
        n=pilotes * n_replicas * viajes,
        seed=seed + 2,
    ).reshape(n_replicas, pilotes, viajes)
    # Asegurar que los tiempos de transporte sean positivos
    t_transportes = np.maximum(t_transportes, 0.1)

    # --- Bucle de réplicas ---
    tiempos_proyecto: List[float] = []
    eventos_replica_base: List[EventoPilote] = []
    tiempos_espera_mixers_all: List[float] = []
    tiempos_mixer_ocupado_all: List[float] = []
    tiempos_espera_perforadoras_all: List[float] = []
    tiempos_perforadora_ocupada_all: List[float] = []
    viajes_mixer_all: List[int] = []

    for r in range(n_replicas):
        env = simpy.Environment()
        perforadora_resource = simpy.Resource(env, capacity=params.num_perforadoras)
        mixer_resource = simpy.Resource(env, capacity=params.num_mixers)
        log_replica: List[EventoPilote] = []

        # Lanzar todos los procesos de pilotes
        for i in range(pilotes):
            env.process(
                _proceso_pilote(
                    env, i, perforadora_resource, mixer_resource,
                    viajes,
                    t_perforaciones[r, i],
                    t_transportes[r, i],
                    t_colados[r, i],
                    log_replica,
                )
            )

        env.run()

        if not log_replica:
            continue

        tiempo_total = max(e.fin_colado for e in log_replica)
        tiempos_proyecto.append(tiempo_total)

        esperas = [e.tiempo_espera_mixer_h for e in log_replica]
        tiempos_espera_mixers_all.extend(esperas)

        # Tiempo real de ocupación del mixer: transporte + colado de todos los viajes
        mixer_ocupado = [
            e.tiempo_total_transporte_h + e.tiempo_total_colado_h for e in log_replica
        ]
        tiempos_mixer_ocupado_all.extend(mixer_ocupado)

        esperas_perf = [e.tiempo_espera_perforadora_h for e in log_replica]
        tiempos_espera_perforadoras_all.extend(esperas_perf)

        perforaciones = [e.tiempo_perforacion_h for e in log_replica]
        tiempos_perforadora_ocupada_all.extend(perforaciones)

        viajes_mixer_all.extend([e.viajes_mixer for e in log_replica])

        # Guardar primera réplica como representativa para el Gantt
        if r == 0:
            eventos_replica_base = log_replica

    if not tiempos_proyecto:
        logger.error("La simulación no produjo resultados válidos.")
        return ResultadoSimulacion(nombre_escenario=params.nombre_escenario)

    arr = np.array(tiempos_proyecto)
    pcts = calcular_percentiles(arr)
    espera_media = float(np.mean(tiempos_espera_mixers_all)) if tiempos_espera_mixers_all else 0.0
    espera_max = float(np.max(tiempos_espera_mixers_all)) if tiempos_espera_mixers_all else 0.0

    espera_perforadora_media = float(np.mean(tiempos_espera_perforadoras_all)) if tiempos_espera_perforadoras_all else 0.0
    espera_perforadora_max = float(np.max(tiempos_espera_perforadoras_all)) if tiempos_espera_perforadoras_all else 0.0

    # Utilización del mixer: tiempo ocupado / tiempo total disponible
    tiempo_mixer_disponible = pcts["p50"] * params.num_mixers
    tiempo_mixer_usado = float(np.sum(tiempos_mixer_ocupado_all)) / n_replicas
    utilizacion_mixer = min(100.0, (tiempo_mixer_usado / tiempo_mixer_disponible) * 100) if tiempo_mixer_disponible > 0 else 0.0

    # Utilización de la perforadora: tiempo ocupado / tiempo total disponible
    tiempo_perforadora_disponible = pcts["p50"] * params.num_perforadoras
    tiempo_perforadora_usado = float(np.sum(tiempos_perforadora_ocupada_all)) / n_replicas
    utilizacion_perforadora = min(100.0, (tiempo_perforadora_usado / tiempo_perforadora_disponible) * 100) if tiempo_perforadora_disponible > 0 else 0.0

    # Métricas de viajes (totales por réplica, no acumulados entre réplicas)
    viajes_mixer_promedio = float(np.mean(viajes_mixer_all)) if viajes_mixer_all else 0.0
    viajes_mixer_total = sum(e.viajes_mixer for e in eventos_replica_base) if eventos_replica_base else 0

    # Identificar cuello de botella considerando ambos recursos
    if espera_perforadora_media > 1.0 and espera_perforadora_media > espera_media:
        cuello = "perforadora"
    elif espera_media > 1.0:
        cuello = "mixer / logística"
    elif pcts["p50"] > params.tiempo_perforacion_ajustado_media * params.cantidad_pilotes * 0.8:
        cuello = "perforación"
    else:
        cuello = "sin cuello de botella crítico"

    kpis = KPIs(
        tiempo_proyecto_p10_h=pcts["p10"],
        tiempo_proyecto_p50_h=pcts["p50"],
        tiempo_proyecto_p90_h=pcts["p90"],
        tiempo_proyecto_media_h=pcts["media"],
        tiempo_proyecto_std_h=pcts["std"],
        tiempo_ciclo_promedio_h=float(
            np.mean([e.tiempo_ciclo_total_h for e in eventos_replica_base])
        ) if eventos_replica_base else 0.0,
        tiempo_ciclo_p90_h=float(
            np.percentile([e.tiempo_ciclo_total_h for e in eventos_replica_base], 90)
        ) if eventos_replica_base else 0.0,
        tiempo_espera_mixer_promedio_h=espera_media,
        tiempo_espera_mixer_max_h=espera_max,
        utilizacion_mixer_pct=utilizacion_mixer,
        tiempo_espera_perforadora_promedio_h=espera_perforadora_media,
        tiempo_espera_perforadora_max_h=espera_perforadora_max,
        utilizacion_perforadora_pct=utilizacion_perforadora,
        viajes_mixer_promedio=viajes_mixer_promedio,
        viajes_mixer_total=viajes_mixer_total,
        cuello_botella=cuello,
        alerta_logistica=espera_media > 2.0,
        alerta_capacidad_mixer=utilizacion_mixer > 85.0,
        alerta_capacidad_perforadora=utilizacion_perforadora > 85.0,
    )

    logger.success(
        f"Simulación completada: P50={pcts['p50']:.1f}h | P90={pcts['p90']:.1f}h | "
        f"Cuello: {cuello}"
    )

    return ResultadoSimulacion(
        nombre_escenario=params.nombre_escenario,
        replicas_ejecutadas=n_replicas,
        seed_usado=seed,
        tiempos_proyecto_todas_replicas=tiempos_proyecto,
        eventos_replica_base=eventos_replica_base,
        kpis=kpis,
    )
