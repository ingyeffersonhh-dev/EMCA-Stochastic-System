"""
core/models/resultados.py
Schemas de salida de la simulación. Tipados con Pydantic para garantizar
consistencia entre el motor y el dashboard.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


# ---------------------------------------------------------------------------
# Evento por pilote (resultado granular de la simulación)
# ---------------------------------------------------------------------------

@dataclass
class EventoPilote:
    """Registro de tiempos de un pilote en una réplica de simulación."""
    pilote_id: int
    inicio_perforacion: float = 0.0
    fin_perforacion: float = 0.0
    inicio_espera_mixer: float = 0.0
    inicio_colado: float = 0.0
    fin_colado: float = 0.0

    @property
    def tiempo_perforacion_h(self) -> float:
        return self.fin_perforacion - self.inicio_perforacion

    @property
    def tiempo_espera_mixer_h(self) -> float:
        return max(0.0, self.inicio_colado - self.fin_perforacion)

    @property
    def tiempo_colado_h(self) -> float:
        return self.fin_colado - self.inicio_colado

    @property
    def tiempo_ciclo_total_h(self) -> float:
        return self.fin_colado - self.inicio_perforacion

    def to_dict(self) -> dict:
        return {
            "pilote_id": self.pilote_id,
            "inicio_perforacion": round(self.inicio_perforacion, 3),
            "fin_perforacion": round(self.fin_perforacion, 3),
            "inicio_colado": round(self.inicio_colado, 3),
            "fin_colado": round(self.fin_colado, 3),
            "tiempo_perforacion_h": round(self.tiempo_perforacion_h, 3),
            "tiempo_espera_mixer_h": round(self.tiempo_espera_mixer_h, 3),
            "tiempo_colado_h": round(self.tiempo_colado_h, 3),
            "tiempo_ciclo_total_h": round(self.tiempo_ciclo_total_h, 3),
        }


# ---------------------------------------------------------------------------
# KPIs agregados
# ---------------------------------------------------------------------------

@dataclass
class KPIs:
    """Indicadores clave calculados sobre el conjunto de réplicas."""
    tiempo_proyecto_p10_h: float = 0.0
    tiempo_proyecto_p50_h: float = 0.0
    tiempo_proyecto_p90_h: float = 0.0
    tiempo_proyecto_media_h: float = 0.0
    tiempo_proyecto_std_h: float = 0.0

    tiempo_ciclo_promedio_h: float = 0.0
    tiempo_ciclo_p90_h: float = 0.0

    tiempo_espera_mixer_promedio_h: float = 0.0
    tiempo_espera_mixer_max_h: float = 0.0
    utilizacion_mixer_pct: float = 0.0

    cuello_botella: str = "indefinido"
    alerta_logistica: bool = False
    alerta_capacidad_mixer: bool = False

    # Días laborables (asume turno de 8h, 5 días/semana)
    @property
    def dias_p50(self) -> float:
        return self.tiempo_proyecto_p50_h / 8.0

    @property
    def semanas_p50(self) -> float:
        return self.dias_p50 / 5.0


# ---------------------------------------------------------------------------
# Resultado completo de la simulación
# ---------------------------------------------------------------------------

@dataclass
class ResultadoSimulacion:
    """
    Contenedor de todos los resultados de la ejecución del motor.
    Incluye eventos detallados de la primera réplica (para Gantt)
    y estadísticas agregadas de todas las réplicas.
    """
    # Metadatos
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    nombre_escenario: str = "Escenario Base"
    replicas_ejecutadas: int = 0
    seed_usado: int = 42

    # Datos por réplica
    tiempos_proyecto_todas_replicas: List[float] = field(default_factory=list)

    # Detalle de la primera réplica (para Gantt)
    eventos_replica_base: List[EventoPilote] = field(default_factory=list)

    # KPIs calculados
    kpis: Optional[KPIs] = None

    @property
    def tiene_resultados(self) -> bool:
        return len(self.tiempos_proyecto_todas_replicas) > 0
