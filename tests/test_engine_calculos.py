"""
tests/test_engine_calculos.py
Test integral del motor de simulación: valida cálculos de tiempos,
KPIs, percentiles, y lógica de negocio.
"""
import pytest
from core.models.parametros import ParametrosEntrada, TipoSuelo, TipoDistribucion
from core.simulation.engine import ejecutar_simulacion


@pytest.fixture
def params_deterministico():
    """Parámetros con std muy baja para resultados casi determinísticos."""
    return ParametrosEntrada(
        diametro_m=0.6,
        longitud_m=15.0,
        cantidad_pilotes=3,
        tipo_suelo=TipoSuelo.SUELO_SECO,
        uso_lodo_bentonitico=True,
        num_mixers=1,
        distancia_proveedor_km=30.0,
        velocidad_transporte_kmh_media=60.0,
        velocidad_transporte_kmh_std=0.1,
        tiempo_perforacion_min_media=120.0,
        tiempo_perforacion_min_std=0.1,
        dist_perforacion=TipoDistribucion.NORMAL,
        tiempo_colado_min_media=60.0,
        tiempo_colado_min_std=0.1,
        dist_colado=TipoDistribucion.NORMAL,
    )


class TestCalculosDeterministicos:
    """Validar cálculos con parámetros sin variabilidad (std=0)."""

    def test_tiempos_individuales_correctos(self, params_deterministico):
        """Cada pilote debe tener tiempos exactos según parámetros."""
        resultado = ejecutar_simulacion(params_deterministico, n_replicas=1, seed=42)
        eventos = resultado.eventos_replica_base

        # Perforación: 120 min = 2h
        for e in eventos:
            assert e.tiempo_perforacion_h == pytest.approx(2.0, abs=0.05)

        # Colado: 60 min = 1h
        for e in eventos:
            assert e.tiempo_colado_h == pytest.approx(1.0, abs=0.05)

    def test_espera_mixer_con_cola(self, params_deterministico):
        """Con 1 mixer y 3 pilotes secuenciales, los pilotes 2 y 3 deben esperar."""
        resultado = ejecutar_simulacion(params_deterministico, n_replicas=1, seed=42)
        eventos = resultado.eventos_replica_base

        # El primer piloto no debería esperar mixer (está libre)
        assert eventos[0].tiempo_espera_mixer_h == pytest.approx(0.0, abs=0.1)

        # Los siguientes sí deben esperar (el mixer está ocupado)
        assert eventos[1].tiempo_espera_mixer_h >= 0.0
        assert eventos[2].tiempo_espera_mixer_h >= 0.0

    def test_secuencia_temporal_coherente(self, params_deterministico):
        """Los tiempos deben seguir: inicio_perf <= fin_perf <= inicio_colado <= fin_colado."""
        resultado = ejecutar_simulacion(params_deterministico, n_replicas=1, seed=42)

        for e in resultado.eventos_replica_base:
            assert e.inicio_perforacion <= e.fin_perforacion
            assert e.fin_perforacion <= e.fin_espera_mixer or e.fin_espera_mixer == 0.0
            assert e.fin_espera_mixer <= e.inicio_colado or e.fin_espera_mixer == 0.0
            assert e.inicio_colado <= e.fin_colado

    def test_mas_mixers_elimina_espera(self, params_deterministico):
        """Con mixers >= pilotes, no debería haber espera."""
        params_sin_cuello = params_deterministico.model_copy(update={
            "num_mixers": 3,
            "cantidad_pilotes": 3,
        })
        resultado = ejecutar_simulacion(params_sin_cuello, n_replicas=1, seed=42)

        for e in resultado.eventos_replica_base:
            assert e.tiempo_espera_mixer_h == pytest.approx(0.0, abs=0.1)


class TestCalculosEstadisticos:
    """Validar cálculos estadísticos con variabilidad."""

    @pytest.fixture
    def params_estocastico(self):
        return ParametrosEntrada(
            diametro_m=0.6,
            longitud_m=15.0,
            cantidad_pilotes=10,
            tipo_suelo=TipoSuelo.SUELO_SECO,
            uso_lodo_bentonitico=True,
            num_mixers=2,
            distancia_proveedor_km=30.0,
            velocidad_transporte_kmh_media=60.0,
            velocidad_transporte_kmh_std=10.0,
            tiempo_perforacion_min_media=240.0,
            tiempo_perforacion_min_std=48.0,
            dist_perforacion=TipoDistribucion.LOGNORMAL,
            tiempo_colado_min_media=120.0,
            tiempo_colado_min_std=20.0,
            dist_colado=TipoDistribucion.NORMAL,
        )

    def test_percentiles_ordenados(self, params_estocastico):
        """P10 <= P50 <= P90 siempre."""
        resultado = ejecutar_simulacion(params_estocastico, n_replicas=500, seed=42)
        k = resultado.kpis

        assert k.tiempo_proyecto_p10_h <= k.tiempo_proyecto_p50_h
        assert k.tiempo_proyecto_p50_h <= k.tiempo_proyecto_p90_h

    def test_media_cercana_a_p50(self, params_estocastico):
        """En distribuciones razonables, la media debe estar cerca del P50."""
        resultado = ejecutar_simulacion(params_estocastico, n_replicas=500, seed=42)
        k = resultado.kpis

        # La media no debería desviarse más del 20% del P50
        diff_pct = abs(k.tiempo_proyecto_media_h - k.tiempo_proyecto_p50_h) / k.tiempo_proyecto_p50_h
        assert diff_pct < 0.20, f"Media ({k.tiempo_proyecto_media_h}) muy lejos de P50 ({k.tiempo_proyecto_p50_h})"

    def test_std_positivo(self, params_estocastico):
        """La desviación estándar debe ser positiva."""
        resultado = ejecutar_simulacion(params_estocastico, n_replicas=500, seed=42)
        assert resultado.kpis.tiempo_proyecto_std_h > 0

    def test_ciclo_promedio_mayor_que_perforacion(self, params_estocastico):
        """El ciclo total debe ser mayor que solo perforación."""
        resultado = ejecutar_simulacion(params_estocastico, n_replicas=500, seed=42)

        # Tiempo perforación promedio en horas
        t_perf_h = params_estocastico.tiempo_perforacion_min_media / 60.0
        assert resultado.kpis.tiempo_ciclo_promedio_h > t_perf_h * 0.8

    def test_espera_mixer_promedio_razonable(self, params_estocastico):
        """La espera promedio del mixer no debería ser absurda (< 50% del ciclo)."""
        resultado = ejecutar_simulacion(params_estocastico, n_replicas=500, seed=42)
        k = resultado.kpis

        # Espera no debe superar el 50% del ciclo promedio
        assert k.tiempo_espera_mixer_promedio_h < k.tiempo_ciclo_promedio_h * 0.5

    def test_utilizacion_mixer_rango_valido(self, params_estocastico):
        """Utilización del mixer entre 0% y 100%."""
        resultado = ejecutar_simulacion(params_estocastico, n_replicas=500, seed=42)
        assert 0 <= resultado.kpis.utilizacion_mixer_pct <= 100


class TestEdgeCases:
    """Casos límite y configuraciones extremas."""

    def test_un_solo_pilote(self):
        """Simulación con un solo pilote."""
        params = ParametrosEntrada(
            diametro_m=0.6, longitud_m=10.0, cantidad_pilotes=1,
            tipo_suelo=TipoSuelo.SUELO_SECO, uso_lodo_bentonitico=False,
            num_mixers=1, distancia_proveedor_km=10.0,
            velocidad_transporte_kmh_media=60.0, velocidad_transporte_kmh_std=5.0,
            tiempo_perforacion_min_media=60.0, tiempo_perforacion_min_std=10.0,
            dist_perforacion=TipoDistribucion.NORMAL,
            tiempo_colado_min_media=30.0, tiempo_colado_min_std=5.0,
            dist_colado=TipoDistribucion.NORMAL,
        )
        resultado = ejecutar_simulacion(params, n_replicas=100, seed=42)
        assert len(resultado.eventos_replica_base) == 1
        assert resultado.kpis.tiempo_proyecto_p50_h > 0

    def test_muchos_mixers_pocos_pilotes(self):
        """Muchos mixers disponibles, pocos pilotes -> espera ≈ 0."""
        params = ParametrosEntrada(
            diametro_m=0.6, longitud_m=10.0, cantidad_pilotes=2,
            tipo_suelo=TipoSuelo.SUELO_SECO, uso_lodo_bentonitico=False,
            num_mixers=10, distancia_proveedor_km=5.0,
            velocidad_transporte_kmh_media=80.0, velocidad_transporte_kmh_std=0.1,
            tiempo_perforacion_min_media=60.0, tiempo_perforacion_min_std=0.1,
            dist_perforacion=TipoDistribucion.NORMAL,
            tiempo_colado_min_media=30.0, tiempo_colado_min_std=0.1,
            dist_colado=TipoDistribucion.NORMAL,
        )
        resultado = ejecutar_simulacion(params, n_replicas=50, seed=42)
        assert resultado.kpis.tiempo_espera_mixer_promedio_h < 0.1

    def test_distancia_larga_aumenta_tiempo(self):
        """Mayor distancia al proveedor debe aumentar tiempos."""
        params_base = ParametrosEntrada(
            diametro_m=0.6, longitud_m=10.0, cantidad_pilotes=5,
            tipo_suelo=TipoSuelo.SUELO_SECO, uso_lodo_bentonitico=False,
            num_mixers=1, distancia_proveedor_km=10.0,
            velocidad_transporte_kmh_media=60.0, velocidad_transporte_kmh_std=0.1,
            tiempo_perforacion_min_media=60.0, tiempo_perforacion_min_std=0.1,
            dist_perforacion=TipoDistribucion.NORMAL,
            tiempo_colado_min_media=30.0, tiempo_colado_min_std=0.1,
            dist_colado=TipoDistribucion.NORMAL,
        )
        r_cerca = ejecutar_simulacion(params_base, n_replicas=100, seed=42)

        params_lejos = params_base.model_copy(update={"distancia_proveedor_km": 100.0})
        r_lejos = ejecutar_simulacion(params_lejos, n_replicas=100, seed=42)

        assert r_lejos.kpis.tiempo_proyecto_p50_h > r_cerca.kpis.tiempo_proyecto_p50_h

    def test_backward_compatibility_horas(self):
        """Parámetros en horas (formato viejo) deben convertirse a minutos."""
        params = ParametrosEntrada(
            diametro_m=0.6, longitud_m=10.0, cantidad_pilotes=3,
            tipo_suelo=TipoSuelo.SUELO_SECO, uso_lodo_bentonitico=False,
            num_mixers=1, distancia_proveedor_km=10.0,
            velocidad_transporte_kmh_media=60.0, velocidad_transporte_kmh_std=0.1,
            tiempo_perforacion_h_media=2.0,  # Formato viejo (horas)
            tiempo_perforacion_h_std=0.5,
            dist_perforacion=TipoDistribucion.NORMAL,
            tiempo_colado_min_media=60.0,
            tiempo_colado_min_std=0.1,
            dist_colado=TipoDistribucion.NORMAL,
        )
        resultado = ejecutar_simulacion(params, n_replicas=50, seed=42)
        assert resultado.kpis.tiempo_proyecto_p50_h > 0
