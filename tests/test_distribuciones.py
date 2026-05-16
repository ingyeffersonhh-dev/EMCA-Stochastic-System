"""
tests/test_distribuciones.py
Pruebas unitarias del módulo de generadores estocásticos.
"""
import pytest
import numpy as np
from core.stochastic.distribuciones import generar_muestras, calcular_percentiles


class TestGenerarMuestras:

    def test_lognormal_positividad(self):
        muestras = generar_muestras("lognormal", media=4.0, std=0.8, n=1000, seed=42)
        assert np.all(muestras > 0), "Lognormal debe generar solo valores positivos"

    def test_lognormal_media_aproximada(self):
        muestras = generar_muestras("lognormal", media=4.0, std=0.8, n=10000, seed=42)
        assert abs(np.mean(muestras) - 4.0) < 0.2, "Media lognormal debe aproximarse al valor dado"

    def test_normal_positividad_clipping(self):
        muestras = generar_muestras("normal", media=2.0, std=0.5, n=1000, seed=99)
        assert np.all(muestras >= 0.01), "Normal debe ser clippeada a positivos"

    def test_exponencial_media_aproximada(self):
        muestras = generar_muestras("exponential", media=2.0, n=10000, seed=1)
        assert abs(np.mean(muestras) - 2.0) < 0.15

    def test_triangular_positividad(self):
        muestras = generar_muestras("triangular", media=3.0, std=0.5, n=500, seed=7)
        assert np.all(muestras > 0)

    def test_distribucion_invalida(self):
        with pytest.raises(ValueError):
            generar_muestras("beta_invalida", media=2.0, n=10)

    def test_seed_reproducible(self):
        m1 = generar_muestras("lognormal", media=3.0, std=0.6, n=100, seed=42)
        m2 = generar_muestras("lognormal", media=3.0, std=0.6, n=100, seed=42)
        np.testing.assert_array_equal(m1, m2)

    def test_percentiles_coherentes(self):
        muestras = generar_muestras("lognormal", media=5.0, std=1.0, n=5000, seed=42)
        pcts = calcular_percentiles(muestras)
        assert pcts["p10"] < pcts["p50"] < pcts["p90"]
        assert pcts["min"] <= pcts["p10"]
        assert pcts["p90"] <= pcts["max"]
