"""
core/stochastic/distribuciones.py
Generadores de variables aleatorias para el motor estocástico.
Todas las funciones garantizan valores positivos mediante clipping.
"""
from __future__ import annotations

import numpy as np
from scipy import stats
from typing import Literal, Dict, Any
from loguru import logger

DistType = Literal["normal", "exponential", "triangular", "lognormal"]


def generar_muestras(
    distribucion: DistType,
    media: float,
    std: float | None = None,
    n: int = 1000,
    seed: int | None = None,
) -> np.ndarray:
    """
    Genera `n` muestras de la distribución especificada.

    Args:
        distribucion: Tipo de distribución estadística.
        media: Valor esperado (media) de la distribución.
        std: Desviación estándar. Requerida para 'normal', 'lognormal', 'triangular'.
             Para 'exponential' se ignora (se infiere de la media).
        n: Número de muestras a generar.
        seed: Semilla para reproducibilidad.

    Returns:
        Array de n muestras positivas.
    """
    rng = np.random.default_rng(seed)

    if distribucion == "normal":
        if std is None:
            raise ValueError("Se requiere 'std' para distribución normal.")
        muestras = rng.normal(loc=media, scale=std, size=n)

    elif distribucion == "exponential":
        # Distribución exponencial: media = 1/lambda → scale = media
        muestras = rng.exponential(scale=media, size=n)

    elif distribucion == "lognormal":
        if std is None:
            raise ValueError("Se requiere 'std' para distribución lognormal.")
        # Parámetros de la distribución log-normal a partir de media y std aritmética
        cv2 = (std / media) ** 2
        sigma_ln = np.sqrt(np.log(1 + cv2))
        mu_ln = np.log(media) - sigma_ln ** 2 / 2
        muestras = rng.lognormal(mean=mu_ln, sigma=sigma_ln, size=n)

    elif distribucion == "triangular":
        if std is None:
            std = media * 0.3  # Default: 30% de la media como semi-rango
        left = max(0.01, media - std * np.sqrt(6))
        right = media + std * np.sqrt(6)
        muestras = rng.triangular(left=left, mode=media, right=right, size=n)

    else:
        raise ValueError(f"Distribución '{distribucion}' no soportada. Use: {DistType}")

    # Garantizar positividad
    muestras = np.clip(muestras, a_min=0.01, a_max=None)
    logger.debug(f"[{distribucion}] μ={np.mean(muestras):.3f} σ={np.std(muestras):.3f} n={n}")
    return muestras


def ajustar_distribucion(datos: np.ndarray) -> Dict[str, Any]:
    """
    Ajusta automáticamente la mejor distribución a un conjunto de datos históricos.
    Usa el test de Kolmogorov-Smirnov para comparar candidatas.

    Args:
        datos: Array de observaciones históricas (ej: tiempos reales de perforación).

    Returns:
        Diccionario con la mejor distribución identificada y estadísticos de ajuste.
    """
    datos = datos[datos > 0]  # Filtrar valores no físicos
    candidatas = {
        "norm": stats.norm,
        "expon": stats.expon,
        "lognorm": stats.lognorm,
        "gamma": stats.gamma,
    }
    resultados: Dict[str, Any] = {}

    for nombre, dist in candidatas.items():
        try:
            params = dist.fit(datos)
            ks_stat, p_valor = stats.kstest(datos, nombre, args=params)
            resultados[nombre] = {
                "params": params,
                "ks_statistic": float(ks_stat),
                "p_valor": float(p_valor),
                "ajuste_bueno": p_valor > 0.05,
            }
        except Exception as e:
            logger.warning(f"Error ajustando {nombre}: {e}")

    mejor = min(resultados, key=lambda k: resultados[k]["ks_statistic"])
    logger.info(f"Mejor distribución ajustada: {mejor} (KS={resultados[mejor]['ks_statistic']:.4f})")

    return {
        "mejor_distribucion": mejor,
        "detalle": resultados,
        "n_observaciones": len(datos),
        "media_datos": float(np.mean(datos)),
        "std_datos": float(np.std(datos)),
    }


def calcular_percentiles(muestras: np.ndarray, percentiles: list[int] = None) -> Dict[str, float]:
    """Calcula percentiles clave de un array de resultados."""
    if percentiles is None:
        percentiles = [10, 25, 50, 75, 90, 95]
    return {
        f"p{p}": float(np.percentile(muestras, p)) for p in percentiles
    } | {
        "media": float(np.mean(muestras)),
        "std": float(np.std(muestras)),
        "min": float(np.min(muestras)),
        "max": float(np.max(muestras)),
    }
