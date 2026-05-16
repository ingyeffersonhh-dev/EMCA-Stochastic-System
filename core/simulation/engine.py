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
    mixer: simpy.Resource,
    t_perforacion: float,
    t_transporte: float,
    t_colado: float,
    log: List[EventoPilote],
) -> simpy.events.ProcessGenerator:
    """
    Proceso de ciclo completo de un pilote:
      1. Perforación (paralela con otros pilotes si hay equipos)
      2. Espera de mixer disponible (cuello de botella logístico)
      3. Transporte del concreto (tiempo viaje ida+vuelta)
      4. Colado de concreto
    """
    evento = EventoPilote(pilote_id=pilote_id)

    # Fase 1: Perforación
    evento.inicio_perforacion = env.now
    yield env.timeout(t_perforacion)
    evento.fin_perforacion = env.now

    # Fase 2: Solicitar mixer (puede generar cola de espera)
    evento.inicio_espera_mixer = env.now
    with mixer.request() as req:
        yield req
        # Fase 3: Transporte (tiempo de viaje del mixer)
        yield env.timeout(t_transporte)

        # Fase 4: Colado
        evento.inicio_colado = env.now
        yield env.timeout(t_colado)
        evento.fin_colado = env.now

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
    t_perf_ajustada = params.tiempo_perforacion_ajustado_media
    t_perf_std = params.tiempo_perforacion_h_std

    t_perforaciones = generar_muestras(
        params.dist_perforacion.value,
        media=t_perf_ajustada,
        std=t_perf_std,
        n=params.cantidad_pilotes * n_replicas,
        seed=seed,
    ).reshape(n_replicas, params.cantidad_pilotes)

    t_colados = generar_muestras(
        params.dist_colado.value,
        media=params.tiempo_colado_h_media,
        std=params.tiempo_colado_h_std,
        n=params.cantidad_pilotes * n_replicas,
        seed=seed + 1,
    ).reshape(n_replicas, params.cantidad_pilotes)

    t_transporte = params.tiempo_transporte_h

    # --- Bucle de réplicas ---
    tiempos_proyecto: List[float] = []
    eventos_replica_base: List[EventoPilote] = []
    tiempos_espera_mixers_all: List[float] = []
    tiempos_mixer_ocupado_all: List[float] = []

    for r in range(n_replicas):
        env = simpy.Environment()
        mixer_resource = simpy.Resource(env, capacity=params.num_mixers)
        log_replica: List[EventoPilote] = []

        # Lanzar todos los procesos de pilotes
        for i in range(params.cantidad_pilotes):
            env.process(
                _proceso_pilote(
                    env, i, mixer_resource,
                    t_perforaciones[r, i],
                    t_transporte,
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

        colados = [e.tiempo_colado_h for e in log_replica]
        tiempos_mixer_ocupado_all.extend(colados)

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

    # Utilización del mixer: tiempo ocupado / tiempo total disponible
    tiempo_mixer_disponible = pcts["p50"] * params.num_mixers
    tiempo_mixer_usado = float(np.sum(tiempos_mixer_ocupado_all)) / n_replicas
    utilizacion = min(100.0, (tiempo_mixer_usado / tiempo_mixer_disponible) * 100) if tiempo_mixer_disponible > 0 else 0.0

    # Identificar cuello de botella
    if espera_media > 1.0:
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
        utilizacion_mixer_pct=utilizacion,
        cuello_botella=cuello,
        alerta_logistica=espera_media > 2.0,
        alerta_capacidad_mixer=utilizacion > 85.0,
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
