"""
core/stochastic/sensibilidad.py
Análisis de sensibilidad global usando índices de Sobol (SALib).
Identifica qué parámetro de entrada tiene mayor impacto en la duración del proyecto.
"""
from __future__ import annotations

from typing import Dict, Any
import numpy as np
from loguru import logger

try:
    from SALib.sample import saltelli
    from SALib.analyze import sobol
    SALIB_DISPONIBLE = True
except ImportError:
    SALIB_DISPONIBLE = False
    logger.warning("SALib no está instalado. El análisis de sensibilidad no estará disponible.")


def definir_problema(params_base: dict) -> dict:
    """
    Define el espacio de parámetros para el análisis de sensibilidad.
    Varía ±30% alrededor de los valores base del usuario.
    """
    return {
        "num_vars": 4,
        "names": [
            "tiempo_perforacion_h_media",
            "tiempo_perforacion_h_std",
            "num_mixers",
            "distancia_proveedor_km",
        ],
        "bounds": [
            [params_base["tiempo_perforacion_h_media"] * 0.7,
             params_base["tiempo_perforacion_h_media"] * 1.3],
            [params_base["tiempo_perforacion_h_std"] * 0.5,
             params_base["tiempo_perforacion_h_std"] * 1.5],
            [max(1, params_base["num_mixers"] - 1),
             params_base["num_mixers"] + 2],
            [params_base["distancia_proveedor_km"] * 0.7,
             params_base["distancia_proveedor_km"] * 1.3],
        ],
    }


def ejecutar_analisis_sobol(
    func_modelo,
    params_base: dict,
    n_samples: int = 256,
) -> Dict[str, Any]:
    """
    Ejecuta análisis de sensibilidad global (índices de Sobol de primer orden y total).

    Args:
        func_modelo: Función callable que acepta un dict de parámetros y retorna
                     el tiempo de proyecto (float) como métrica de salida.
        params_base: Diccionario con los parámetros base del escenario actual.
        n_samples: Tamaño de muestra Saltelli (total = n_samples * (2*D + 2)).

    Returns:
        Diccionario con índices S1 (primer orden) y ST (total) por parámetro.
    """
    if not SALIB_DISPONIBLE:
        return {"error": "SALib no instalado. Ejecute: pip install SALib"}

    problema = definir_problema(params_base)
    X = saltelli.sample(problema, n_samples, calc_second_order=False)
    logger.info(f"Análisis de sensibilidad: {len(X)} evaluaciones del modelo...")

    Y = np.array([func_modelo(x, params_base, problema["names"]) for x in X])

    Si = sobol.analyze(problema, Y, calc_second_order=False, print_to_console=False)

    resultado = {
        "parametros": problema["names"],
        "S1": {name: float(s1) for name, s1 in zip(problema["names"], Si["S1"])},
        "ST": {name: float(st) for name, st in zip(problema["names"], Si["ST"])},
        "S1_conf": {name: float(c) for name, c in zip(problema["names"], Si["S1_conf"])},
        "ST_conf": {name: float(c) for name, c in zip(problema["names"], Si["ST_conf"])},
        "n_evaluaciones": len(X),
    }

    # Identificar el parámetro más influyente
    resultado["parametro_mas_influyente"] = max(resultado["ST"], key=resultado["ST"].get)
    logger.info(f"Parámetro más influyente: {resultado['parametro_mas_influyente']}")

    return resultado
