"""
core/models/parametros.py
Schemas de validación para los parámetros de entrada del sistema EMCA.
Usa Pydantic v2 para garantizar integridad de datos desde el formulario.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Enumeraciones del dominio
# ---------------------------------------------------------------------------

class TipoSuelo(str, Enum):
    SUELO_SECO = "suelo_seco"
    SUELO_AGUA = "suelo_agua"
    # Compatibilidad con versión anterior
    ARCILLA_BLANDA = "arcilla_blanda"
    ARCILLA_DURA = "arcilla_dura"
    ARENA_SUELTA = "arena_suelta"
    ARENA_DENSA = "arena_densa"
    ROCA_BLANDA = "roca_blanda"

    @property
    def label(self) -> str:
        labels = {
            "suelo_seco": "Suelo Seco",
            "suelo_agua": "Suelo con Presencia de Agua",
            "arcilla_blanda": "Arcilla Blanda",
            "arcilla_dura": "Arcilla Dura",
            "arena_suelta": "Arena Suelta",
            "arena_densa": "Arena Densa",
            "roca_blanda": "Roca Blanda",
        }
        return labels.get(self.value, self.value)

    @property
    def factor_dificultad(self) -> float:
        factores = {
            "suelo_seco": 1.0,
            "suelo_agua": 1.35,
            "arcilla_blanda": 0.85,
            "arcilla_dura": 1.20,
            "arena_suelta": 0.90,
            "arena_densa": 1.10,
            "roca_blanda": 1.50,
        }
        return factores.get(self.value, 1.0)


class TipoDistribucion(str, Enum):
    LOGNORMAL = "lognormal"
    NORMAL = "normal"
    EXPONENTIAL = "exponential"
    TRIANGULAR = "triangular"


# ---------------------------------------------------------------------------
# Schema principal de parámetros de entrada
# ---------------------------------------------------------------------------

class ParametrosEntrada(BaseModel):
    """
    Parámetros operativos y estocásticos para la simulación de pilotes.
    Acepta campos nuevos (minutos) y viejos (horas) para compatibilidad.
    """

    # --- Geometría del pilote ---
    diametro_m: float = Field(default=0.6, gt=0.3, lt=2.0)
    longitud_m: float = Field(default=15.0, gt=5.0, lt=60.0)
    cantidad_pilotes: int = Field(default=20, gt=0, lt=500)

    # --- Condiciones del entorno ---
    tipo_suelo: TipoSuelo = Field(default=TipoSuelo.SUELO_SECO)
    uso_lodo_bentonitico: bool = Field(default=True)

    # --- Logística y recursos ---
    num_mixers: int = Field(default=2, ge=1, le=10)
    distancia_proveedor_km: float = Field(default=30.0, gt=0.0, lt=200.0)

    # Velocidad: campos nuevos y viejos
    velocidad_transporte_kmh_media: Optional[float] = Field(default=None, gt=10.0, lt=120.0)
    velocidad_transporte_kmh_std: Optional[float] = Field(default=None, gt=0.0)
    # Campo viejo (compatibilidad)
    velocidad_transporte_kmh: Optional[float] = Field(default=None, gt=10.0, lt=120.0)

    # Tiempos perforación: campos nuevos (minutos) y viejos (horas)
    tiempo_perforacion_min_media: Optional[float] = Field(default=None, gt=0.0, lt=2880.0)
    tiempo_perforacion_min_std: Optional[float] = Field(default=None, gt=0.0)
    # Campos viejos (compatibilidad via alias)
    perf_h_media: Optional[float] = Field(default=None, gt=0.0, lt=48.0, validation_alias="tiempo_perforacion_h_media")
    perf_h_std: Optional[float] = Field(default=None, gt=0.0, validation_alias="tiempo_perforacion_h_std")

    dist_perforacion: TipoDistribucion = Field(default=TipoDistribucion.LOGNORMAL)

    # Tiempos colado: campos nuevos (minutos) y viejos (horas)
    tiempo_colado_min_media: Optional[float] = Field(default=None, gt=0.0, lt=1440.0)
    tiempo_colado_min_std: Optional[float] = Field(default=None, gt=0.0)
    # Campos viejos (compatibilidad via alias)
    colado_h_media: Optional[float] = Field(default=None, gt=0.0, lt=24.0, validation_alias="tiempo_colado_h_media")
    colado_h_std: Optional[float] = Field(default=None, gt=0.0, validation_alias="tiempo_colado_h_std")

    dist_colado: TipoDistribucion = Field(default=TipoDistribucion.EXPONENTIAL)

    # --- Configuración de jornada laboral ---
    horas_por_dia: float = Field(default=8.0, gt=0.0, lt=24.0)

    # --- Costos Operativos (Nuevos) ---
    costo_hora_perforadora_usd: float = Field(default=150.0, ge=0.0)
    costo_hora_mixer_usd: float = Field(default=80.0, ge=0.0)
    costo_hora_standby_mixer_usd: float = Field(default=40.0, ge=0.0)

    # --- Metadatos ---
    nombre_escenario: str = Field(default="Escenario Base", max_length=100)
    notas: Optional[str] = Field(default=None, max_length=500)

    # ---------------------------------------------------------------------------
    # Validadores
    # ---------------------------------------------------------------------------

    @model_validator(mode="after")
    def normalizar_campos(self) -> "ParametrosEntrada":
        if self.velocidad_transporte_kmh_media is None:
            self.velocidad_transporte_kmh_media = self.velocidad_transporte_kmh or 60.0
        if self.velocidad_transporte_kmh_std is None:
            self.velocidad_transporte_kmh_std = 10.0

        if self.tiempo_perforacion_min_media is None:
            self.tiempo_perforacion_min_media = (self.perf_h_media * 60) if self.perf_h_media else 240.0
        if self.tiempo_perforacion_min_std is None:
            self.tiempo_perforacion_min_std = (self.perf_h_std * 60) if self.perf_h_std else self.tiempo_perforacion_min_media / 5.0

        if self.tiempo_colado_min_media is None:
            self.tiempo_colado_min_media = (self.colado_h_media * 60) if self.colado_h_media else 120.0
        if self.tiempo_colado_min_std is None:
            self.tiempo_colado_min_std = (self.colado_h_std * 60) if self.colado_h_std else self.tiempo_colado_min_media / 4.0

        return self

    @field_validator("tiempo_perforacion_min_std")
    @classmethod
    def std_perf_coherente(cls, v, info):
        if v is None:
            return v
        data = info.data
        media = data.get("tiempo_perforacion_min_media")
        if media and v >= media:
            raise ValueError(f"Desv. std ({v:.0f} min) no puede ser >= media ({media:.0f} min)")
        return v

    # ---------------------------------------------------------------------------
    # Propiedades calculadas
    # ---------------------------------------------------------------------------

    @property
    def volumen_pilote_m3(self) -> float:
        import math
        return math.pi * (self.diametro_m / 2) ** 2 * self.longitud_m

    @property
    def volumen_total_m3(self) -> float:
        return self.volumen_pilote_m3 * self.cantidad_pilotes

    @property
    def perf_horas_media(self) -> float:
        return self.tiempo_perforacion_min_media / 60.0

    @property
    def perf_horas_std(self) -> float:
        return self.tiempo_perforacion_min_std / 60.0

    @property
    def colado_horas_media(self) -> float:
        return self.tiempo_colado_min_media / 60.0

    @property
    def colado_horas_std(self) -> float:
        return self.tiempo_colado_min_std / 60.0

    @property
    def tiempo_transporte_h(self) -> float:
        return (self.distancia_proveedor_km / self.velocidad_transporte_kmh_media) * 2

    @property
    def tiempo_perforacion_ajustado_media(self) -> float:
        return self.perf_horas_media * self.tipo_suelo.factor_dificultad

    @property
    def dias_estimados(self) -> float:
        t = self.tiempo_perforacion_ajustado_media + self.colado_horas_media + self.tiempo_transporte_h / self.num_mixers
        return (t * self.cantidad_pilotes) / self.horas_por_dia

    # Alias compatibilidad
    @property
    def tiempo_perforacion_h_media(self) -> float:
        return self.perf_horas_media

    @property
    def tiempo_perforacion_h_std(self) -> float:
        return self.perf_horas_std

    @property
    def tiempo_colado_h_media(self) -> float:
        return self.colado_horas_media

    @property
    def tiempo_colado_h_std(self) -> float:
        return self.colado_horas_std

    model_config = ConfigDict(use_enum_values=False)
