"""
core/analytics/kpis.py
Cálculo de indicadores clave de rendimiento y detección de alertas operativas.
"""
from __future__ import annotations

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from core.models.resultados import EventoPilote, KPIs, ResultadoSimulacion


def resumen_estadistico(resultado: ResultadoSimulacion) -> Dict[str, Any]:
    """
    Genera un resumen completo de KPIs desde el resultado de la simulación.
    Pensado para alimentar las tarjetas del dashboard.
    """
    if not resultado.tiene_resultados or resultado.kpis is None:
        return {}

    k = resultado.kpis
    return {
        # Tiempo de proyecto
        "Duración P10 (h)": round(k.tiempo_proyecto_p10_h, 1),
        "Duración P50 (h)": round(k.tiempo_proyecto_p50_h, 1),
        "Duración P90 (h)": round(k.tiempo_proyecto_p90_h, 1),
        "Desviación estándar (h)": round(k.tiempo_proyecto_std_h, 2),
        # Días/semanas
        "Duración P50 (días)": round(k.dias_p50, 1),
        "Duración P50 (semanas)": round(k.semanas_p50, 1),
        # Ciclo por pilote
        "Ciclo promedio por pilote (h)": round(k.tiempo_ciclo_promedio_h, 2),
        "Ciclo P90 por pilote (h)": round(k.tiempo_ciclo_p90_h, 2),
        # Logística
        "Espera mixer promedio (h)": round(k.tiempo_espera_mixer_promedio_h, 2),
        "Espera mixer máxima (h)": round(k.tiempo_espera_mixer_max_h, 2),
        "Utilización mixer (%)": round(k.utilizacion_mixer_pct, 1),
        # Diagnóstico
        "Cuello de botella": k.cuello_botella,
        "Alerta logística": "🔴 SÍ" if k.alerta_logistica else "🟢 NO",
        "Alerta capacidad mixer": "🔴 SÍ" if k.alerta_capacidad_mixer else "🟢 NO",
    }


def tabla_eventos_df(eventos: List[EventoPilote]) -> pd.DataFrame:
    """Convierte la lista de eventos de la réplica base a un DataFrame."""
    if not eventos:
        return pd.DataFrame()
    return pd.DataFrame([e.to_dict() for e in eventos])


def distribucion_tiempos_df(tiempos: List[float]) -> pd.DataFrame:
    """DataFrame listo para histograma de duración del proyecto."""
    return pd.DataFrame({"duracion_h": tiempos})
