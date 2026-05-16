"""
tests/test_kpis.py
Pruebas unitarias del módulo de analytics y KPIs.
"""
import pytest
from core.models.resultados import EventoPilote, ResultadoSimulacion, KPIs
from core.analytics.kpis import resumen_estadistico, tabla_eventos_df
from core.analytics.gantt import generar_gantt_df, generar_curva_s


@pytest.fixture
def eventos_mock():
    eventos = []
    for i in range(5):
        e = EventoPilote(
            pilote_id=i,
            inicio_perforacion=i * 6.0,
            fin_perforacion=i * 6.0 + 4.0,
            inicio_espera_mixer=i * 6.0 + 4.0,
            inicio_colado=i * 6.0 + 5.0,
            fin_colado=i * 6.0 + 7.0,
        )
        eventos.append(e)
    return eventos


@pytest.fixture
def resultado_mock(eventos_mock):
    k = KPIs(
        tiempo_proyecto_p10_h=28.0, tiempo_proyecto_p50_h=32.0,
        tiempo_proyecto_p90_h=38.0, tiempo_proyecto_media_h=32.5,
        tiempo_proyecto_std_h=3.2, tiempo_ciclo_promedio_h=7.0,
        tiempo_ciclo_p90_h=8.5, tiempo_espera_mixer_promedio_h=1.0,
        tiempo_espera_mixer_max_h=2.5, utilizacion_mixer_pct=70.0,
        cuello_botella="perforación", alerta_logistica=False,
        alerta_capacidad_mixer=False,
    )
    return ResultadoSimulacion(
        nombre_escenario="Test",
        replicas_ejecutadas=100,
        tiempos_proyecto_todas_replicas=[30.0 + i * 0.5 for i in range(100)],
        eventos_replica_base=eventos_mock,
        kpis=k,
    )


class TestKPIs:

    def test_resumen_tiene_claves(self, resultado_mock):
        resumen = resumen_estadistico(resultado_mock)
        assert "Duración P50 (h)" in resumen
        assert "Cuello de botella" in resumen

    def test_tabla_eventos_columnas(self, eventos_mock):
        df = tabla_eventos_df(eventos_mock)
        assert "tiempo_ciclo_total_h" in df.columns
        assert len(df) == 5

    def test_gantt_fases(self, eventos_mock):
        df = generar_gantt_df(eventos_mock)
        fases = df["Fase"].unique().tolist()
        assert "🔩 Perforación" in fases
        assert "🪣 Colado" in fases

    def test_curva_s_100_pct(self, eventos_mock):
        df = generar_curva_s(eventos_mock)
        assert df["avance_pct"].max() == 100.0

    def test_evento_propiedades(self, eventos_mock):
        e = eventos_mock[0]
        assert e.tiempo_perforacion_h == pytest.approx(4.0)
        assert e.tiempo_espera_mixer_h == pytest.approx(1.0)
        assert e.tiempo_ciclo_total_h == pytest.approx(7.0)
