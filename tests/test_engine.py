"""
tests/test_engine.py
Pruebas unitarias del motor de simulación SimPy.
"""
import pytest
from core.models.parametros import ParametrosEntrada, TipoSuelo, TipoDistribucion
from core.simulation.engine import ejecutar_simulacion


@pytest.fixture
def params_base():
    return ParametrosEntrada(
        diametro_m=0.6, longitud_m=15.0, cantidad_pilotes=5,
        tipo_suelo=TipoSuelo.ARCILLA_BLANDA, uso_lodo_bentonitico=True,
        num_mixers=2, distancia_proveedor_km=30.0, velocidad_transporte_kmh=60.0,
        tiempo_perforacion_h_media=4.0, tiempo_perforacion_h_std=0.8,
        dist_perforacion=TipoDistribucion.LOGNORMAL,
        tiempo_colado_h_media=2.0, dist_colado=TipoDistribucion.EXPONENTIAL,
    )


class TestEjecutarSimulacion:

    def test_retorna_resultado(self, params_base):
        resultado = ejecutar_simulacion(params_base, n_replicas=50, seed=42)
        assert resultado.tiene_resultados

    def test_replicas_correctas(self, params_base):
        resultado = ejecutar_simulacion(params_base, n_replicas=100, seed=42)
        assert resultado.replicas_ejecutadas == 100
        assert len(resultado.tiempos_proyecto_todas_replicas) == 100

    def test_eventos_replica_base(self, params_base):
        resultado = ejecutar_simulacion(params_base, n_replicas=50, seed=42)
        assert len(resultado.eventos_replica_base) == params_base.cantidad_pilotes

    def test_tiempos_positivos(self, params_base):
        resultado = ejecutar_simulacion(params_base, n_replicas=50, seed=42)
        for t in resultado.tiempos_proyecto_todas_replicas:
            assert t > 0, "Todos los tiempos de proyecto deben ser positivos"

    def test_kpis_coherentes(self, params_base):
        resultado = ejecutar_simulacion(params_base, n_replicas=200, seed=42)
        k = resultado.kpis
        assert k is not None
        assert k.tiempo_proyecto_p10_h <= k.tiempo_proyecto_p50_h <= k.tiempo_proyecto_p90_h

    def test_mas_mixers_reduce_espera(self, params_base):
        """Más mixers debe reducir el tiempo de espera logístico."""
        r1 = ejecutar_simulacion(params_base, n_replicas=100, seed=42)

        params_mas_mixers = params_base.model_copy(update={"num_mixers": 6})
        r2 = ejecutar_simulacion(params_mas_mixers, n_replicas=100, seed=42)

        assert r2.kpis.tiempo_espera_mixer_promedio_h <= r1.kpis.tiempo_espera_mixer_promedio_h

    def test_reproducibilidad(self, params_base):
        r1 = ejecutar_simulacion(params_base, n_replicas=50, seed=99)
        r2 = ejecutar_simulacion(params_base, n_replicas=50, seed=99)
        assert r1.kpis.tiempo_proyecto_p50_h == r2.kpis.tiempo_proyecto_p50_h
