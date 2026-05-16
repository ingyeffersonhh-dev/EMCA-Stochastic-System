"""
core/analytics/gantt.py
Generación del cronograma Gantt desde los eventos de la simulación.
Produce DataFrames compatibles con Plotly Express timeline.
"""
from __future__ import annotations

from typing import List
import pandas as pd
import numpy as np

from core.models.resultados import EventoPilote


def generar_gantt_df(
    eventos: List[EventoPilote],
    hora_inicio_proyecto: str = "2025-01-06 07:00:00",
) -> pd.DataFrame:
    """
    Convierte la lista de eventos en un DataFrame de fases para Gantt.

    Args:
        eventos: Lista de EventoPilote de la réplica base.
        hora_inicio_proyecto: Fecha/hora real de inicio (para mostrar fechas en el eje X).

    Returns:
        DataFrame con columnas: Pilote, Fase, Inicio, Fin, Duración_h
    """
    if not eventos:
        return pd.DataFrame()

    origen = pd.Timestamp(hora_inicio_proyecto)
    rows = []

    for e in eventos:
        label = f"Pilote {e.pilote_id + 1:02d}"

        rows.append({
            "Pilote": label,
            "Fase": "🔩 Perforación",
            "Inicio": origen + pd.Timedelta(hours=e.inicio_perforacion),
            "Fin": origen + pd.Timedelta(hours=e.fin_perforacion),
            "Duración_h": round(e.tiempo_perforacion_h, 2),
        })

        if e.tiempo_espera_mixer_h > 0.05:
            rows.append({
                "Pilote": label,
                "Fase": "⏳ Espera Mixer",
                "Inicio": origen + pd.Timedelta(hours=e.fin_perforacion),
                "Fin": origen + pd.Timedelta(hours=e.inicio_colado),
                "Duración_h": round(e.tiempo_espera_mixer_h, 2),
            })

        rows.append({
            "Pilote": label,
            "Fase": "🪣 Colado",
            "Inicio": origen + pd.Timedelta(hours=e.inicio_colado),
            "Fin": origen + pd.Timedelta(hours=e.fin_colado),
            "Duración_h": round(e.tiempo_colado_h, 2),
        })

    return pd.DataFrame(rows)


def generar_curva_s(eventos: List[EventoPilote]) -> pd.DataFrame:
    """
    Genera los datos de la curva S de avance acumulado del proyecto.
    Retorna el porcentaje de pilotes completados en función del tiempo.
    """
    if not eventos:
        return pd.DataFrame()

    hitos = sorted([(e.fin_colado, i + 1) for i, e in enumerate(eventos)])
    tiempo_max = hitos[-1][0]
    tiempos = np.linspace(0, tiempo_max, 200)

    completados = []
    total = len(eventos)
    for t in tiempos:
        n = sum(1 for fin, _ in hitos if fin <= t)
        completados.append(round(n / total * 100, 1))

    return pd.DataFrame({
        "tiempo_h": tiempos,
        "avance_pct": completados,
    })
