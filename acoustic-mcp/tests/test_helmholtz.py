"""Tests for Helmholtz resonator and other layer models."""

import numpy as np
import pytest

from acoustic.models.helmholtz import (
    helmholtz_absorption_area,
    helmholtz_impedance,
    helmholtz_resonance,
)
from acoustic.models.membrane import membrane_matrix, panel_absorber_resonance
from acoustic.models.perforated import mpp_maa, perforated_ingard, slotted_kristiansen
from acoustic.utils import C_0


class TestHelmholtzResonance:
    def test_known_geometry(self):
        """Verify resonance frequency for a simple geometry."""
        # neck: 2mm long, 1mm radius; cavity: 10mm cube
        f0 = helmholtz_resonance(0.002, 0.001, 1e-6)
        # Should be in the kHz range for small resonator
        assert 500 < f0 < 10000

    def test_larger_cavity_lower_freq(self):
        """Larger cavity → lower resonance frequency."""
        f0_small = helmholtz_resonance(0.002, 0.001, 1e-6)
        f0_large = helmholtz_resonance(0.002, 0.001, 8e-6)
        assert f0_large < f0_small

    def test_larger_neck_higher_freq(self):
        """Wider neck → higher resonance frequency."""
        f0_narrow = helmholtz_resonance(0.002, 0.0005, 1e-6)
        f0_wide = helmholtz_resonance(0.002, 0.002, 1e-6)
        assert f0_wide > f0_narrow

    def test_longer_neck_lower_freq(self):
        """Longer neck → lower resonance frequency."""
        f0_short = helmholtz_resonance(0.002, 0.001, 1e-6)
        f0_long = helmholtz_resonance(0.010, 0.001, 1e-6)
        assert f0_long < f0_short


class TestHelmholtzImpedance:
    def test_impedance_imaginary_zero_at_resonance(self):
        """At resonance, reactive part should cross zero."""
        freqs = np.linspace(100, 5000, 10000)
        Z = helmholtz_impedance(freqs, 0.002, 0.001, 1e-6)
        f0 = helmholtz_resonance(0.002, 0.001, 1e-6)

        # Find frequency closest to resonance
        idx = np.argmin(np.abs(freqs - f0))
        # Imaginary part should be near zero at resonance
        assert abs(np.imag(Z[idx])) < abs(np.imag(Z[0]))

    def test_viscous_loss_adds_resistance(self):
        """Viscous losses should add positive real impedance."""
        freqs = np.array([1000.0])
        Z_lossy = helmholtz_impedance(freqs, 0.002, 0.001, 1e-6, viscous_loss=True)
        Z_lossless = helmholtz_impedance(freqs, 0.002, 0.001, 1e-6, viscous_loss=False)
        assert np.real(Z_lossy[0]) > np.real(Z_lossless[0])


class TestHelmholtzAbsorption:
    def test_absorption_area_positive(self):
        """Absorption area should be non-negative."""
        freqs = np.linspace(100, 5000, 500)
        A = helmholtz_absorption_area(freqs, 0.002, 0.001, 1e-6)
        assert np.all(A >= 0)

    def test_peak_near_resonance(self):
        """Absorption area peak should be near the resonance frequency."""
        freqs = np.linspace(100, 5000, 1000)
        f0 = helmholtz_resonance(0.002, 0.001, 1e-6)
        A = helmholtz_absorption_area(freqs, 0.002, 0.001, 1e-6)
        peak_freq = freqs[np.argmax(A)]
        # Peak should be within 20% of analytical resonance
        assert abs(peak_freq - f0) / f0 < 0.2


class TestMembrane:
    def test_panel_resonance_formula(self):
        """3mm plywood (1.5 kg/m²) + 100mm cavity → ~155 Hz."""
        f0 = panel_absorber_resonance(1.5, 0.100)
        assert 100 < f0 < 200

    def test_heavier_panel_lower_freq(self):
        f0_light = panel_absorber_resonance(1.0, 0.100)
        f0_heavy = panel_absorber_resonance(5.0, 0.100)
        assert f0_heavy < f0_light

    def test_deeper_cavity_lower_freq(self):
        f0_shallow = panel_absorber_resonance(2.0, 0.050)
        f0_deep = panel_absorber_resonance(2.0, 0.200)
        assert f0_deep < f0_shallow

    def test_membrane_matrix_shape(self):
        freqs = np.array([250.0, 500.0, 1000.0])
        T = membrane_matrix(freqs, 2.0)
        assert T.shape == (3, 2, 2)
        # Should be impedance sheet (T[0,0]=1, T[1,0]=0, T[1,1]=1)
        np.testing.assert_allclose(T[:, 0, 0], 1.0)
        np.testing.assert_allclose(T[:, 1, 0], 0.0)
        np.testing.assert_allclose(T[:, 1, 1], 1.0)


class TestPerforated:
    @pytest.fixture
    def freqs(self):
        return np.linspace(100, 4000, 100)

    def test_ingard_returns_complex(self, freqs):
        Z = perforated_ingard(freqs, 0.003, 0.005, 0.020)
        assert Z.dtype == complex
        assert len(Z) == len(freqs)

    def test_slotted_returns_complex(self, freqs):
        Z = slotted_kristiansen(freqs, 0.003, 0.003, 0.015)
        assert Z.dtype == complex

    def test_mpp_returns_complex(self, freqs):
        Z = mpp_maa(freqs, 0.001, 0.0003, 0.01)
        assert Z.dtype == complex

    def test_positive_resistance(self, freqs):
        """Real part of impedance should be positive (energy dissipation)."""
        Z = perforated_ingard(freqs, 0.003, 0.005, 0.020)
        assert np.all(np.real(Z) > 0)

    def test_positive_reactance(self, freqs):
        """Imaginary part should be positive (mass-like reactance)."""
        Z = perforated_ingard(freqs, 0.003, 0.005, 0.020)
        assert np.all(np.imag(Z) > 0)
