"""Tests for the TMM engine and utility functions."""

import numpy as np
import pytest

from acoustic import tmm, utils
from acoustic.models.air import air_gap_matrix


class TestUtils:
    def test_frequency_axis_range(self):
        freqs = utils.frequency_axis(20, 20000, 12)
        assert freqs[0] == pytest.approx(20.0)
        assert freqs[-1] == pytest.approx(20000.0)
        assert len(freqs) > 100  # ~120 points for 10 octaves at 12/oct

    def test_frequency_axis_log_spacing(self):
        freqs = utils.frequency_axis(100, 1600, 1)
        # 4 octaves at 1 point/octave = 5 points
        assert len(freqs) == 5

    def test_third_octave_bands(self):
        bands = utils.third_octave_bands(200, 2500)
        assert 250 in bands
        assert 500 in bands
        assert 1000 in bands
        assert 2000 in bands
        assert 100 not in bands

    def test_nrc_calculation(self):
        freqs = utils.frequency_axis(20, 20000, 12)
        # Perfect absorber: alpha=1 everywhere → NRC=1.0
        alpha = np.ones_like(freqs)
        assert utils.nrc(alpha, freqs) == pytest.approx(1.0)

        # No absorption: alpha=0 everywhere → NRC=0.0
        alpha = np.zeros_like(freqs)
        assert utils.nrc(alpha, freqs) == pytest.approx(0.0)

    def test_nrc_rounds_to_005(self):
        freqs = utils.frequency_axis(20, 20000, 12)
        alpha = np.full_like(freqs, 0.33)
        nrc = utils.nrc(alpha, freqs)
        # Should round to nearest 0.05
        assert nrc * 20 == pytest.approx(round(nrc * 20))

    def test_saa_calculation(self):
        freqs = utils.frequency_axis(20, 20000, 12)
        alpha = np.ones_like(freqs)
        assert utils.saa(alpha, freqs) == pytest.approx(1.0)

    def test_octave_band_summary_keys(self):
        freqs = utils.frequency_axis(20, 20000, 12)
        alpha = np.ones_like(freqs)
        summary = utils.octave_band_summary(alpha, freqs)
        expected_keys = {"63", "125", "250", "500", "1000", "2000", "4000"}
        assert set(summary.keys()) == expected_keys


class TestTMM:
    def test_air_layer_identity_at_zero_thickness(self):
        """Zero-thickness air layer should be identity matrix."""
        freqs = np.array([100.0, 500.0, 1000.0])
        T = air_gap_matrix(freqs, 0.0)
        for i in range(len(freqs)):
            np.testing.assert_allclose(T[i], np.eye(2), atol=1e-10)

    def test_air_layer_analytical(self):
        """Air layer matrix should match cos/sin analytical form."""
        freqs = np.array([1000.0])
        d = 0.1  # 100mm
        T = air_gap_matrix(freqs, d)
        k0 = 2 * np.pi * 1000 / utils.C_0
        kd = k0 * d
        assert T[0, 0, 0] == pytest.approx(np.cos(kd), abs=1e-10)
        assert T[0, 1, 1] == pytest.approx(np.cos(kd), abs=1e-10)

    def test_rigid_wall_no_absorption(self):
        """Rigid wall (no absorber) should have zero absorption."""
        freqs = np.array([500.0, 1000.0])
        # Identity matrix = rigid wall directly
        T = np.tile(np.eye(2, dtype=complex), (2, 1, 1))
        Zs = tmm.surface_impedance(T)
        alpha = tmm.absorption_coefficient(Zs)
        np.testing.assert_allclose(alpha, 0.0, atol=1e-10)

    def test_multiply_chain_single(self):
        """Chain of one matrix should equal that matrix."""
        freqs = np.array([500.0])
        T = air_gap_matrix(freqs, 0.05)
        T_chain = tmm.multiply_chain([T])
        np.testing.assert_allclose(T_chain, T, atol=1e-10)

    def test_multiply_chain_two_air_layers(self):
        """Two air layers should equal one layer of combined thickness."""
        freqs = np.array([500.0, 1000.0])
        T1 = air_gap_matrix(freqs, 0.05)
        T2 = air_gap_matrix(freqs, 0.03)
        T_combined = air_gap_matrix(freqs, 0.08)
        T_chain = tmm.multiply_chain([T1, T2])
        np.testing.assert_allclose(T_chain, T_combined, atol=1e-10)

    def test_absorption_bounded(self):
        """Absorption coefficient should always be in [0, 1]."""
        freqs = utils.frequency_axis(20, 20000, 12)
        from acoustic.models.porous import miki
        Zc, kc = miki(freqs, 13000)
        matrices = [tmm.porous_layer_matrix(freqs, Zc, kc, 0.050)]
        alpha = tmm.absorption_from_layers(freqs, matrices)
        assert np.all(alpha >= 0.0)
        assert np.all(alpha <= 1.0)


class TestPorousAbsorber:
    """Integration tests for porous absorber through full TMM pipeline."""

    def test_thicker_absorbs_more(self):
        """Thicker porous layer should absorb more at mid frequencies."""
        freqs = utils.frequency_axis(20, 20000, 12)
        from acoustic.models.porous import miki

        # 25mm vs 100mm
        Zc, kc = miki(freqs, 13000)
        alpha_25 = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc, kc, 0.025)]
        )
        alpha_100 = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc, kc, 0.100)]
        )
        # NRC of 100mm should be higher than 25mm
        assert utils.nrc(alpha_100, freqs) > utils.nrc(alpha_25, freqs)

    def test_air_gap_improves_low_freq(self):
        """Adding air gap should improve low-frequency absorption."""
        freqs = utils.frequency_axis(20, 20000, 12)
        from acoustic.models.porous import miki

        Zc, kc = miki(freqs, 13000)

        # Without air gap
        alpha_no_gap = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc, kc, 0.050)]
        )
        # With 100mm air gap
        alpha_with_gap = tmm.absorption_from_layers(
            freqs,
            [
                tmm.porous_layer_matrix(freqs, Zc, kc, 0.050),
                air_gap_matrix(freqs, 0.100),
            ],
        )

        # Alpha at 250 Hz should be better with air gap
        idx_250 = np.argmin(np.abs(freqs - 250))
        assert alpha_with_gap[idx_250] > alpha_no_gap[idx_250]

    def test_oc703_50mm_reasonable(self):
        """OC703 50mm absorption should be physically reasonable."""
        freqs = utils.frequency_axis(20, 20000, 12)
        from acoustic.models.porous import miki

        Zc, kc = miki(freqs, 13000)
        alpha = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc, kc, 0.050)]
        )

        # At 500 Hz: expect 0.4-0.8 (normal incidence)
        idx_500 = np.argmin(np.abs(freqs - 500))
        assert 0.3 <= alpha[idx_500] <= 0.9

        # At 2000 Hz: expect > 0.9
        idx_2k = np.argmin(np.abs(freqs - 2000))
        assert alpha[idx_2k] > 0.85

        # NRC should be reasonable (0.5-0.9)
        nrc = utils.nrc(alpha, freqs)
        assert 0.4 <= nrc <= 1.0
