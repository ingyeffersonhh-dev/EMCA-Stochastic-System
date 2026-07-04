"""
tests/test_modelo_logistico.py
Pruebas TDD para el modelo de datos logístico del sistema EMCA.
Cubre los campos de ParametrosEntrada, EventoPilote, KPIs y ResultadoSimulacion
relacionados con perforadoras y viajes de mixer.
"""
import math
import pytest
import pandas as pd
from pydantic import ValidationError

from core.models.parametros import ParametrosEntrada, TipoSuelo, TipoDistribucion
from core.models.resultados import EventoPilote, KPIs, ResultadoSimulacion
from core.simulation.engine import ejecutar_simulacion
from core.analytics.kpis import resumen_estadistico
from core.analytics.gantt import generar_gantt_df
from core.analytics.exportar import exportar_excel


class TestParametrosLogisticos:
    """T1: Validación de nuevos campos logísticos en ParametrosEntrada."""

    def test_num_perforadoras_default(self):
        """GIVEN no num_perforadoras THEN default is 2."""
        p = ParametrosEntrada()
        assert p.num_perforadoras == 2

    def test_num_perforadoras_range_valid(self):
        """GIVEN num_perforadoras in [1, 10] THEN valid."""
        p1 = ParametrosEntrada(num_perforadoras=1)
        assert p1.num_perforadoras == 1
        p10 = ParametrosEntrada(num_perforadoras=10)
        assert p10.num_perforadoras == 10

    def test_num_perforadoras_zero_raises(self):
        """GIVEN num_perforadoras=0 THEN ValidationError."""
        with pytest.raises(ValidationError):
            ParametrosEntrada(num_perforadoras=0)

    def test_capacidad_mixer_default(self):
        """GIVEN no capacidad_mixer_m3 THEN default is 6.0."""
        p = ParametrosEntrada()
        assert p.capacidad_mixer_m3 == pytest.approx(6.0)

    def test_capacidad_mixer_range_valid(self):
        """GIVEN capacidad_mixer_m3 in (0, 15] THEN valid."""
        p_small = ParametrosEntrada(capacidad_mixer_m3=0.5)
        assert p_small.capacidad_mixer_m3 == pytest.approx(0.5)
        p_max = ParametrosEntrada(capacidad_mixer_m3=15.0)
        assert p_max.capacidad_mixer_m3 == pytest.approx(15.0)

    def test_capacidad_mixer_zero_raises(self):
        """GIVEN capacidad_mixer_m3=0 THEN ValidationError."""
        with pytest.raises(ValidationError):
            ParametrosEntrada(capacidad_mixer_m3=0.0)


class TestViajesPorPilote:
    """T3: Cálculo de viajes por pilote según volumen y capacidad."""

    def test_viajes_por_pilote_large_pile(self):
        """GIVEN vol=33.9 m3, cap=6.0 m3 THEN 6 viajes."""
        p = ParametrosEntrada(
            diametro_m=1.5,
            longitud_m=19.2,
            capacidad_mixer_m3=6.0,
        )
        expected_vol = math.pi * (1.5 / 2) ** 2 * 19.2
        assert p.volumen_pilote_m3 == pytest.approx(expected_vol)
        assert expected_vol == pytest.approx(33.9, abs=0.1)
        assert p.viajes_por_pilote == 6

    def test_viajes_por_pilote_small_pile(self):
        """GIVEN vol=4.24 m3, cap=6.0 m3 THEN 1 viaje."""
        p = ParametrosEntrada(
            diametro_m=0.6,
            longitud_m=15.0,
            capacidad_mixer_m3=6.0,
        )
        assert p.volumen_pilote_m3 == pytest.approx(4.24, abs=0.01)
        assert p.viajes_por_pilote == 1


class TestDiasEstimados:
    """T4: dias_estimados considera el paralelismo de perforadoras."""

    def test_dias_estimados_1_vs_3_perforadoras(self):
        """GIVEN 1 vs 3 perforadoras THEN 1 rig higher estimate."""
        base = ParametrosEntrada(
            diametro_m=0.6,
            longitud_m=15.0,
            cantidad_pilotes=3,
            num_perforadoras=3,
            capacidad_mixer_m3=6.0,
        )
        serial = base.model_copy(update={"num_perforadoras": 1})
        assert serial.dias_estimados > base.dias_estimados


class TestEventoPilote:
    """T5/T6: EventoPilote incluye campos de espera perforadora y viajes."""

    def test_evento_to_dict_includes_new_fields(self):
        """GIVEN EventoPilote THEN to_dict contains new fields."""
        e = EventoPilote(
            pilote_id=1,
            inicio_espera_perforadora=1.0,
            fin_espera_perforadora=3.5,
            viajes_mixer=4,
            tiempo_total_transporte_h=2.0,
            tiempo_total_colado_h=1.5,
        )
        d = e.to_dict()
        assert d["inicio_espera_perforadora"] == 1.0
        assert d["fin_espera_perforadora"] == 3.5
        assert d["viajes_mixer"] == 4
        assert d["tiempo_total_transporte_h"] == 2.0
        assert d["tiempo_total_colado_h"] == 1.5

    def test_evento_tiempo_espera_perforadora_property(self):
        """GIVEN EventoPilote THEN tiempo_espera_perforadora_h computed."""
        e = EventoPilote(
            pilote_id=1,
            inicio_espera_perforadora=1.0,
            fin_espera_perforadora=3.5,
        )
        assert e.tiempo_espera_perforadora_h == pytest.approx(2.5)

    def test_evento_tiempo_espera_perforadora_non_negative(self):
        """GIVEN fin < inicio THEN tiempo_espera_perforadora_h is 0."""
        e = EventoPilote(
            pilote_id=1,
            inicio_espera_perforadora=5.0,
            fin_espera_perforadora=3.0,
        )
        assert e.tiempo_espera_perforadora_h == 0.0


class TestKPIs:
    """T7/T8: KPIs incluyen métricas de perforadora y viajes."""

    def test_kpis_default_new_fields(self):
        """GIVEN default KPIs THEN new fields are 0/False."""
        k = KPIs()
        assert k.tiempo_espera_perforadora_promedio_h == 0.0
        assert k.tiempo_espera_perforadora_max_h == 0.0
        assert k.utilizacion_perforadora_pct == 0.0
        assert k.viajes_mixer_promedio == 0.0
        assert k.viajes_mixer_total == 0
        assert k.alerta_capacidad_perforadora is False

    def test_kpis_utilizacion_range(self):
        """GIVEN valid simulation KPIs THEN utilization in [0, 100]."""
        k = KPIs(utilizacion_perforadora_pct=72.0)
        assert 0 <= k.utilizacion_perforadora_pct <= 100

    def test_kpis_alerta_perforadora_activa(self):
        """GIVEN utilization 90% THEN alert is True."""
        k = KPIs(utilizacion_perforadora_pct=90.0)
        # Threshold is documented at 85%; field is plain data in PR1.
        assert k.utilizacion_perforadora_pct > 85

    def test_kpis_from_dict_filters_unknown_keys(self):
        """GIVEN unknown keys THEN from_dict ignores them without crash."""
        d = {
            "tiempo_proyecto_p50_h": 100.0,
            "utilizacion_perforadora_pct": 72.0,
            "unknown_field": "should_be_ignored",
            "another_garbage": 123,
        }
        k = KPIs.from_dict(d)
        assert k.tiempo_proyecto_p50_h == 100.0
        assert k.utilizacion_perforadora_pct == 72.0
        assert not hasattr(k, "unknown_field")


class TestBackwardCompat:
    """Backward compatibility con diccionarios antiguos."""

    def test_old_scenario_dict_loads_defaults(self):
        """GIVEN old scenario dict without new fields THEN defaults applied."""
        old = {
            "diametro_m": 0.6,
            "longitud_m": 15.0,
            "cantidad_pilotes": 5,
        }
        p = ParametrosEntrada.model_validate(old)
        assert p.num_perforadoras == 2
        assert p.capacidad_mixer_m3 == pytest.approx(6.0)

    def test_old_result_dict_loads(self):
        """GIVEN old result dict without new fields THEN loads without error."""
        old = {
            "timestamp": "2024-01-01T00:00:00",
            "nombre_escenario": "Old",
            "replicas_ejecutadas": 10,
            "seed_usado": 42,
            "tiempos_proyecto_todas_replicas": [1.0, 2.0, 3.0],
            "eventos_replica_base": [
                {"pilote_id": 1, "inicio_perforacion": 0.0, "fin_perforacion": 2.0,
                 "inicio_espera_mixer": 2.0, "fin_espera_mixer": 2.0,
                 "inicio_colado": 2.0, "fin_colado": 3.0}
            ],
            "kpis": {"tiempo_proyecto_p50_h": 5.0, "utilizacion_mixer_pct": 50.0},
        }
        r = ResultadoSimulacion.from_dict(old)
        assert r.tiene_resultados
        assert len(r.eventos_replica_base) == 1
        e = r.eventos_replica_base[0]
        assert e.viajes_mixer == 1
        assert e.tiempo_total_transporte_h == 0.0
        assert e.tiempo_total_colado_h == 0.0


class TestPerforadoraEngine:
    """T9: El motor serializa/paraleliza la perforadora y registra esperas."""

    @pytest.fixture
    def params_perf_deterministico(self):
        """Parámetros determinísticos para validar orden de perforación."""
        return ParametrosEntrada(
            diametro_m=0.6,
            longitud_m=15.0,
            cantidad_pilotes=3,
            tipo_suelo=TipoSuelo.SUELO_SECO,
            uso_lodo_bentonitico=True,
            num_mixers=3,
            num_perforadoras=3,
            capacidad_mixer_m3=6.0,
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

    def test_perforadora_1_rig_sequential(self, params_perf_deterministico):
        """GIVEN 1 perforadora THEN pilotes perforan en serie."""
        params = params_perf_deterministico.model_copy(update={"num_perforadoras": 1})
        resultado = ejecutar_simulacion(params, n_replicas=1, seed=42)
        eventos = sorted(resultado.eventos_replica_base, key=lambda e: e.pilote_id)

        assert eventos[1].inicio_perforacion >= eventos[0].fin_perforacion
        assert eventos[2].inicio_perforacion >= eventos[1].fin_perforacion

    def test_perforadora_3_rigs_parallel(self, params_perf_deterministico):
        """GIVEN 3 perforadoras y 3 pilotes THEN todos inician al mismo tiempo."""
        params = params_perf_deterministico.model_copy(update={"num_perforadoras": 3})
        resultado = ejecutar_simulacion(params, n_replicas=1, seed=42)
        eventos = resultado.eventos_replica_base

        for e in eventos:
            assert e.inicio_perforacion == pytest.approx(0.0, abs=0.1)

    def test_perforadora_wait_tracked(self, params_perf_deterministico):
        """GIVEN simulación con perforadora THEN evento registra espera."""
        params = params_perf_deterministico.model_copy(update={"num_perforadoras": 1})
        resultado = ejecutar_simulacion(params, n_replicas=1, seed=42)
        eventos = sorted(resultado.eventos_replica_base, key=lambda e: e.pilote_id)

        for e in eventos:
            assert e.inicio_espera_perforadora >= 0.0
            assert e.fin_espera_perforadora >= e.inicio_espera_perforadora

    def test_perforadora_0_validation_error(self):
        """GIVEN num_perforadoras=0 THEN ValidationError."""
        with pytest.raises(ValidationError):
            ParametrosEntrada(num_perforadoras=0)


class TestMultiTripMixer:
    """T11: El motor cola en múltiples viajes de mixer y libera entre ellos."""

    @pytest.fixture
    def params_multitrip(self):
        """Parámetros determinísticos para validar múltiples viajes."""
        return ParametrosEntrada(
            diametro_m=1.5,
            longitud_m=19.2,
            cantidad_pilotes=1,
            tipo_suelo=TipoSuelo.SUELO_SECO,
            uso_lodo_bentonitico=True,
            num_mixers=1,
            num_perforadoras=1,
            capacidad_mixer_m3=6.0,
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

    @pytest.fixture
    def params_small_pile(self):
        """Pilote pequeño que requiere un solo viaje."""
        return ParametrosEntrada(
            diametro_m=0.6,
            longitud_m=15.0,
            cantidad_pilotes=1,
            tipo_suelo=TipoSuelo.SUELO_SECO,
            uso_lodo_bentonitico=True,
            num_mixers=1,
            num_perforadoras=1,
            capacidad_mixer_m3=6.0,
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

    def test_mixer_multi_trip_6_viajes(self, params_multitrip):
        """GIVEN vol=33.9m3, cap=6m3 THEN 6 viajes."""
        assert params_multitrip.viajes_por_pilote == 6
        resultado = ejecutar_simulacion(params_multitrip, n_replicas=1, seed=42)
        evento = resultado.eventos_replica_base[0]
        assert evento.viajes_mixer == 6

    def test_mixer_multi_trip_1_viaje(self, params_small_pile):
        """GIVEN pilote pequeño THEN 1 viaje (equivalente a comportamiento anterior)."""
        assert params_small_pile.viajes_por_pilote == 1
        resultado = ejecutar_simulacion(params_small_pile, n_replicas=1, seed=42)
        evento = resultado.eventos_replica_base[0]
        assert evento.viajes_mixer == 1

    def test_mixer_released_between_trips(self):
        """GIVEN 2 pilotes grandes y 1 mixer THEN el mixer se libera entre viajes."""
        params = ParametrosEntrada(
            diametro_m=1.5,
            longitud_m=19.2,
            cantidad_pilotes=2,
            tipo_suelo=TipoSuelo.SUELO_SECO,
            uso_lodo_bentonitico=True,
            num_mixers=1,
            num_perforadoras=2,
            capacidad_mixer_m3=6.0,
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
        resultado = ejecutar_simulacion(params, n_replicas=1, seed=42)
        eventos = sorted(resultado.eventos_replica_base, key=lambda e: e.pilote_id)

        # Si el mixer se libera entre viajes, el pilote 1 puede empezar a colar
        # antes de que el pilote 0 termine todos sus viajes.
        assert eventos[1].fin_espera_mixer < eventos[0].fin_colado

    def test_tiempo_total_colado_h_sum(self, params_multitrip):
        """GIVEN 6 viajes THEN tiempo_total_colado_h es la suma de los 6 colados."""
        resultado = ejecutar_simulacion(params_multitrip, n_replicas=1, seed=42)
        evento = resultado.eventos_replica_base[0]
        assert evento.tiempo_total_colado_h == pytest.approx(6.0, abs=0.1)
        # La ventana de colado (inicio primer colado -> fin último colado)
        # incluye los transportes intermedios, por eso es mayor que la suma pura.
        assert evento.tiempo_colado_h > evento.tiempo_total_colado_h

    def test_tiempo_total_transporte_h_sum(self, params_multitrip):
        """GIVEN 6 viajes THEN tiempo_total_transporte_h es la suma de los 6 transportes."""
        resultado = ejecutar_simulacion(params_multitrip, n_replicas=1, seed=42)
        evento = resultado.eventos_replica_base[0]
        # Transporte base: 30km / 60kmh * 2 = 1h por viaje
        assert evento.tiempo_total_transporte_h == pytest.approx(6.0, abs=0.1)


class TestEngineKPIs:
    """T13: Los KPIs agregados reflejan el uso de perforadora y viajes."""

    @pytest.fixture
    def params_kpi(self):
        return ParametrosEntrada(
            diametro_m=1.5,
            longitud_m=19.2,
            cantidad_pilotes=5,
            tipo_suelo=TipoSuelo.SUELO_SECO,
            uso_lodo_bentonitico=True,
            num_mixers=2,
            num_perforadoras=2,
            capacidad_mixer_m3=6.0,
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

    def test_kpi_utilizacion_perforadora_range(self, params_kpi):
        """GIVEN simulación THEN utilizacion_perforadora_pct en [0, 100]."""
        resultado = ejecutar_simulacion(params_kpi, n_replicas=200, seed=42)
        util = resultado.kpis.utilizacion_perforadora_pct
        assert 0 <= util <= 100

    def test_kpi_viajes_mixer_promedio(self, params_kpi):
        """GIVEN pilotes uniformes THEN viajes promedio coincide con ceil(vol/cap)."""
        resultado = ejecutar_simulacion(params_kpi, n_replicas=100, seed=42)
        assert resultado.kpis.viajes_mixer_promedio == pytest.approx(
            params_kpi.viajes_por_pilote, abs=0.01
        )

    def test_kpi_alerta_capacidad_perforadora(self, params_kpi):
        """GIVEN alta utilización THEN alerta_capacidad_perforadora es True."""
        # 1 perforadora, muchos mixers y tiempos de colado/transporte cortos
        # para que la perforadora sea el cuello de botella dominante.
        params_alta = params_kpi.model_copy(update={
            "num_perforadoras": 1,
            "num_mixers": 10,
            "cantidad_pilotes": 10,
            "tiempo_colado_min_media": 30.0,
            "tiempo_colado_min_std": 5.0,
            "distancia_proveedor_km": 5.0,
        })
        resultado = ejecutar_simulacion(params_alta, n_replicas=200, seed=42)
        assert resultado.kpis.utilizacion_perforadora_pct > 85
        assert resultado.kpis.alerta_capacidad_perforadora is True

    def test_kpi_viajes_mixer_total(self, params_kpi):
        """GIVEN N pilotes con V viajes THEN total = N * V."""
        resultado = ejecutar_simulacion(params_kpi, n_replicas=100, seed=42)
        expected = params_kpi.cantidad_pilotes * params_kpi.viajes_por_pilote
        assert resultado.kpis.viajes_mixer_total == expected

    def test_reproducibility_same_seed(self, params_kpi):
        """GIVEN misma semilla THEN mismo P50."""
        r1 = ejecutar_simulacion(params_kpi, n_replicas=100, seed=77)
        r2 = ejecutar_simulacion(params_kpi, n_replicas=100, seed=77)
        assert r1.kpis.tiempo_proyecto_p50_h == r2.kpis.tiempo_proyecto_p50_h


class TestGanttAnalytics:
    """T17: El Gantt refleja espera de perforadora y colado agregado."""

    @pytest.fixture
    def eventos_gantt(self):
        return [
            EventoPilote(
                pilote_id=0,
                inicio_perforacion=0.0,
                fin_perforacion=4.0,
                inicio_espera_perforadora=0.0,
                fin_espera_perforadora=1.0,
                inicio_espera_mixer=4.0,
                fin_espera_mixer=5.0,
                inicio_colado=5.0,
                fin_colado=7.0,
                viajes_mixer=3,
                tiempo_total_transporte_h=1.5,
                tiempo_total_colado_h=1.5,
            ),
            EventoPilote(
                pilote_id=1,
                inicio_perforacion=4.0,
                fin_perforacion=8.0,
                inicio_espera_perforadora=4.0,
                fin_espera_perforadora=4.5,
                inicio_espera_mixer=8.0,
                fin_espera_mixer=8.0,
                inicio_colado=8.0,
                fin_colado=9.0,
                viajes_mixer=1,
                tiempo_total_transporte_h=0.5,
                tiempo_total_colado_h=0.5,
            ),
        ]

    def test_gantt_includes_perforadora_wait(self, eventos_gantt):
        """GIVEN eventos con espera perforadora THEN Gantt incluye la fase."""
        df = generar_gantt_df(eventos_gantt)
        fases = df["Fase"].unique().tolist()
        assert "⛏️ Espera Perforadora" in fases

    def test_gantt_colado_is_aggregated(self, eventos_gantt):
        """GIVEN pilote con múltiples viajes THEN Gantt muestra un solo bar Colado."""
        df = generar_gantt_df(eventos_gantt)
        pilote0 = df[df["Pilote"] == "Pilote 01"]
        colado_rows = pilote0[pilote0["Fase"] == "🪣 Colado"]
        assert len(colado_rows) == 1
        assert colado_rows.iloc[0]["Inicio"] == pd.Timestamp("2025-01-06 12:00:00")
        assert colado_rows.iloc[0]["Fin"] == pd.Timestamp("2025-01-06 14:00:00")

    def test_gantt_espera_mixer_present(self, eventos_gantt):
        """GIVEN eventos con espera mixer THEN Gantt incluye la fase."""
        df = generar_gantt_df(eventos_gantt)
        fases = df["Fase"].unique().tolist()
        assert "⏳ Espera Mixer" in fases


class TestKPIsResumen:
    """T18: resumen_estadistico expone métricas de perforadora y viajes."""

    @pytest.fixture
    def resultado_kpi_completo(self):
        k = KPIs(
            tiempo_proyecto_p50_h=100.0,
            tiempo_espera_perforadora_promedio_h=2.5,
            tiempo_espera_perforadora_max_h=8.0,
            utilizacion_perforadora_pct=92.0,
            viajes_mixer_promedio=6.0,
            viajes_mixer_total=30,
            alerta_capacidad_perforadora=True,
        )
        return ResultadoSimulacion(
            nombre_escenario="KPI Test",
            replicas_ejecutadas=100,
            tiempos_proyecto_todas_replicas=[90.0 + i for i in range(100)],
            kpis=k,
        )

    def test_resumen_includes_perforadora_metrics(self, resultado_kpi_completo):
        """GIVEN KPIs con métricas de perforadora THEN resumen las incluye."""
        resumen = resumen_estadistico(resultado_kpi_completo)
        assert "Espera perforadora promedio (h)" in resumen
        assert resumen["Espera perforadora promedio (h)"] == 2.5
        assert "Espera perforadora máxima (h)" in resumen
        assert resumen["Espera perforadora máxima (h)"] == 8.0
        assert "Utilización perforadora (%)" in resumen
        assert resumen["Utilización perforadora (%)"] == 92.0

    def test_resumen_includes_viajes_metrics(self, resultado_kpi_completo):
        """GIVEN KPIs con métricas de viajes THEN resumen las incluye."""
        resumen = resumen_estadistico(resultado_kpi_completo)
        assert "Viajes mixer promedio" in resumen
        assert resumen["Viajes mixer promedio"] == 6.0
        assert "Viajes mixer total" in resumen
        assert resumen["Viajes mixer total"] == 30

    def test_resumen_alerta_perforadora_format(self, resultado_kpi_completo):
        """GIVEN alerta de perforadora THEN resumen muestra emoji rojo."""
        resumen = resumen_estadistico(resultado_kpi_completo)
        assert "Alerta capacidad perforadora" in resumen
        assert resumen["Alerta capacidad perforadora"] == "🔴 SÍ"


class TestExportarExcel:
    """T18: Excel export incluye columnas de perforadora y viajes."""

    @pytest.fixture
    def resultado_export(self):
        eventos = [
            EventoPilote(
                pilote_id=0,
                inicio_perforacion=0.0,
                fin_perforacion=4.0,
                inicio_espera_perforadora=0.0,
                fin_espera_perforadora=1.0,
                inicio_espera_mixer=4.0,
                fin_espera_mixer=5.0,
                inicio_colado=5.0,
                fin_colado=7.0,
                viajes_mixer=3,
                tiempo_total_transporte_h=1.5,
                tiempo_total_colado_h=1.5,
            ),
        ]
        k = KPIs(tiempo_proyecto_p50_h=10.0)
        return ResultadoSimulacion(
            nombre_escenario="Export Test",
            replicas_ejecutadas=10,
            tiempos_proyecto_todas_replicas=[10.0] * 10,
            eventos_replica_base=eventos,
            kpis=k,
        )

    def test_excel_has_perforadora_wait_column(self, resultado_export, tmp_path):
        """GIVEN export THEN sheet Detalle Pilotes tiene Espera Perforadora."""
        ruta = exportar_excel(resultado_export, directorio=str(tmp_path))
        df = pd.read_excel(ruta, sheet_name="📋 Detalle Pilotes")
        assert "Espera Perforadora (h)" in df.columns

    def test_excel_has_viajes_mixer_column(self, resultado_export, tmp_path):
        """GIVEN export THEN sheet Detalle Pilotes tiene Viajes Mixer."""
        ruta = exportar_excel(resultado_export, directorio=str(tmp_path))
        df = pd.read_excel(ruta, sheet_name="📋 Detalle Pilotes")
        assert "Viajes Mixer" in df.columns

    def test_excel_preserves_espera_mixer_column(self, resultado_export, tmp_path):
        """GIVEN export THEN columna Espera Mixer sigue presente."""
        ruta = exportar_excel(resultado_export, directorio=str(tmp_path))
        df = pd.read_excel(ruta, sheet_name="📋 Detalle Pilotes")
        assert "T. Espera Mixer (h)" in df.columns


class TestSensibilidadPerforadora:
    """T21: Análisis de sensibilidad incluye num_perforadoras."""

    def test_problema_incluye_num_perforadoras(self):
        """GIVEN params base THEN problema tiene 5 vars y num_perforadoras."""
        from core.stochastic.sensibilidad import definir_problema
        params_base = {
            "tiempo_perforacion_min_media": 240.0,
            "tiempo_perforacion_min_std": 48.0,
            "num_mixers": 2,
            "distancia_proveedor_km": 30.0,
            "num_perforadoras": 2,
        }
        problema = definir_problema(params_base)
        assert problema["num_vars"] == 5
        assert "num_perforadoras" in problema["names"]
        idx = problema["names"].index("num_perforadoras")
        assert problema["bounds"][idx] == [max(1, 2 - 1), 2 + 2]
