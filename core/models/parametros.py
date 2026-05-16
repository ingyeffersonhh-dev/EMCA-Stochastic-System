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
        """Factor multiplicador del tiempo de perforación según tipo de suelo."""
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
    Todos los campos tienen validaciones de rango físicamente coherentes.
    """

    # --- Geometría del pilote ---
    diametro_m: float = Field(
        ..., gt=0.3, lt=2.0,
        description="Diámetro del pilote en metros"
    )
    longitud_m: float = Field(
        ..., gt=5.0, lt=60.0,
        description="Longitud del pilote en metros"
    )
    cantidad_pilotes: int = Field(
        ..., gt=0, lt=500,
        description="Número total de pilotes a perforar"
    )

    # --- Condiciones del entorno ---
    tipo_suelo: TipoSuelo = Field(
        ..., description="Condición del suelo: seco o con presencia de agua"
    )
    uso_lodo_bentonitico: bool = Field(
        default=True,
        description="Si se emplea lodo bentonítico para estabilizar la excavación"
    )

    # --- Logística y recursos ---
    num_mixers: int = Field(
        ..., ge=1, le=10,
        description="Número de mixers de concreto disponibles simultáneamente"
    )
    distancia_proveedor_km: float = Field(
        ..., gt=0.0, lt=200.0,
        description="Distancia a la planta de concreto en kilómetros"
    )
    velocidad_transporte_kmh_media: float = Field(
        default=60.0, gt=10.0, lt=120.0,
        description="Velocidad promedio de los mixers en tránsito (km/h)"
    )
    velocidad_transporte_kmh_std: float = Field(
        default=10.0, gt=0.0,
        description="Desviación estándar de la velocidad de transporte (km/h)"
    )

    # --- Parámetros estocásticos: Perforación (en minutos) ---
    tiempo_perforacion_min_media: float = Field(
        ..., gt=0.0, lt=2880.0,
        description="Tiempo promedio de perforación por pilote (minutos)"
    )
    tiempo_perforacion_min_std: float = Field(
        ..., gt=0.0,
        description="Desviación estándar del tiempo de perforación (minutos)"
    )
    dist_perforacion: TipoDistribucion = Field(
        default=TipoDistribucion.LOGNORMAL,
        description="Distribución estadística para el tiempo de perforación"
    )

    # --- Parámetros estocásticos: Colado (en minutos) ---
    tiempo_colado_min_media: float = Field(
        ..., gt=0.0, lt=1440.0,
        description="Tiempo promedio de colado de concreto por pilote (minutos)"
    )
    tiempo_colado_min_std: Optional[float] = Field(
        default=None,
        description="Desviación estándar del colado (usa media/4 si no se especifica)"
    )
    dist_colado: TipoDistribucion = Field(
        default=TipoDistribucion.EXPONENTIAL,
        description="Distribución estadística para el tiempo de colado"
    )

    # --- Configuración de jornada laboral ---
    horas_por_dia: float = Field(
        default=8.0, gt=0.0, lt=24.0,
        description="Horas de trabajo por día"
    )

    # --- Metadatos del escenario ---
    nombre_escenario: str = Field(
        default="Escenario Base",
        max_length=100,
        description="Nombre descriptivo para guardar el escenario"
    )
    notas: Optional[str] = Field(
        default=None, max_length=500,
        description="Observaciones adicionales del operador"
    )

    # ---------------------------------------------------------------------------
    # Validadores
    # ---------------------------------------------------------------------------

    @model_validator(mode="before")
    @classmethod
    def compatibilidad_campos_viejos(cls, data):
        """Convierte campos de versión anterior a los nuevos nombres."""
        if isinstance(data, dict):
            # Velocidad de transporte
            if "velocidad_transporte_kmh" in data and "velocidad_transporte_kmh_media" not in data:
                data["velocidad_transporte_kmh_media"] = data.pop("velocidad_transporte_kmh")
            if "velocidad_transporte_kmh_std" not in data:
                data["velocidad_transporte_kmh_std"] = 10.0

            # Tiempos de perforación (horas -> minutos)
            if "tiempo_perforacion_h_media" in data and "tiempo_perforacion_min_media" not in data:
                data["tiempo_perforacion_min_media"] = data.pop("tiempo_perforacion_h_media") * 60
            if "tiempo_perforacion_h_std" in data and "tiempo_perforacion_min_std" not in data:
                data["tiempo_perforacion_min_std"] = data.pop("tiempo_perforacion_h_std") * 60

            # Tiempos de colado (horas -> minutos)
            if "tiempo_colado_h_media" in data and "tiempo_colado_min_media" not in data:
                data["tiempo_colado_min_media"] = data.pop("tiempo_colado_h_media") * 60
            if "tiempo_colado_h_std" in data and "tiempo_colado_min_std" not in data:
                data["tiempo_colado_min_std"] = data.pop("tiempo_colado_h_std") * 60

            # Horas por día
            if "horas_por_dia" not in data:
                data["horas_por_dia"] = 8.0

        return data

    @field_validator("tiempo_perforacion_min_std")
    @classmethod
    def std_perf_coherente(cls, v: float, info) -> float:
        data = info.data
        if "tiempo_perforacion_min_media" in data:
            media = data["tiempo_perforacion_min_media"]
            if v >= media:
                raise ValueError(
                    f"La desviación estándar ({v:.0f} min) no puede ser ≥ la media ({media:.0f} min)."
                )
            if v / media > 0.6:
                raise ValueError(
                    f"Coeficiente de variación ({v/media:.0%}) excede 60%."
                )
        return v

    @model_validator(mode="after")
    def completar_std_colado(self) -> "ParametrosEntrada":
        if self.tiempo_colado_min_std is None:
            self.tiempo_colado_min_std = self.tiempo_colado_min_media / 4.0
        return self

    # ---------------------------------------------------------------------------
    # Propiedades calculadas
    # ---------------------------------------------------------------------------

    @property
    def volumen_pilote_m3(self) -> float:
        """Volumen teórico de un pilote (m³)."""
        import math
        return math.pi * (self.diametro_m / 2) ** 2 * self.longitud_m

    @property
    def volumen_total_m3(self) -> float:
        """Volumen total de concreto estimado para todos los pilotes (m³)."""
        return self.volumen_pilote_m3 * self.cantidad_pilotes

    @property
    def tiempo_perforacion_h_media(self) -> float:
        """Tiempo promedio de perforación en horas (compatibilidad)."""
        return self.tiempo_perforacion_min_media / 60.0

    @property
    def tiempo_perforacion_h_std(self) -> float:
        """Desviación estándar de perforación en horas (compatibilidad)."""
        return self.tiempo_perforacion_min_std / 60.0

    @property
    def tiempo_colado_h_media(self) -> float:
        """Tiempo promedio de colado en horas (compatibilidad)."""
        return self.tiempo_colado_min_media / 60.0

    @property
    def tiempo_colado_h_std(self) -> float:
        """Desviación estándar de colado en horas (compatibilidad)."""
        return self.tiempo_colado_min_std / 60.0

    @property
    def tiempo_transporte_h(self) -> float:
        """Tiempo de viaje ida + vuelta del mixer (horas)."""
        return (self.distancia_proveedor_km / self.velocidad_transporte_kmh_media) * 2

    @property
    def tiempo_perforacion_ajustado_media(self) -> float:
        """Media de perforación ajustada por el factor de dificultad del suelo (horas)."""
        return self.tiempo_perforacion_h_media * self.tipo_suelo.factor_dificultad

    @property
    def dias_estimados(self) -> float:
        """Días estimados de trabajo basado en horas por día."""
        tiempo_total_h = self.tiempo_perforacion_ajustado_media + self.tiempo_colado_h_media + self.tiempo_transporte_h / self.num_mixers
        return (tiempo_total_h * self.cantidad_pilotes) / self.horas_por_dia

    model_config = ConfigDict(use_enum_values=False)
