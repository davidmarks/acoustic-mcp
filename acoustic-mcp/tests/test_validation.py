"""Validation tests against published reference data and analytical formulas.

Tests use tight quantitative checks rather than wide qualitative ranges,
validating models against hand-calculated values from original publications
and analytical results from standard acoustics textbooks.

References:
    Delany & Bazley, Acustica 23 (1970).
    Miki, JASE 11(1) (1990).
    Allard & Champoux, JASA 91(6) (1992).
    Ingard, JASA 25(6) (1953).
    Kinsler et al., Fundamentals of Acoustics (2000), Ch. 9.
    Kuttruff, Room Acoustics (2009), Ch. 2.2, 6.4.
    Maa, JASA 104(5) (1998).
"""

import numpy as np
import pytest

from acoustic import tmm, utils
from acoustic.models.air import air_gap_matrix
from acoustic.models.helmholtz import helmholtz_impedance, helmholtz_resonance
from acoustic.models.membrane import panel_absorber_resonance
from acoustic.models.perforated import mpp_maa, perforated_ingard
from acoustic.models.porous import allard_champoux, delany_bazley, jca, miki


def alpha_at_freq(alpha: np.ndarray, freqs: np.ndarray, target_hz: float) -> float:
    """Interpolate alpha at target frequency using log-frequency interpolation."""
    return float(np.interp(np.log10(target_hz), np.log10(freqs), alpha))


@pytest.fixture
def freqs():
    """Standard frequency axis at third-octave resolution."""
    return utils.frequency_axis(20, 20000, 12)


# ---------------------------------------------------------------------------
# 1. Porous model coefficient verification
# ---------------------------------------------------------------------------


class TestPorousModelCoefficients:
    """Verify porous models reproduce their published formula coefficients."""

    def test_miki_zc_at_x01(self):
        """Miki Zc at X=0.1 — hand-calculated from Miki (1990) coefficients.

        X^(-0.632) = 10^0.632 ≈ 4.2856
        Zc = Z_0 * (1 + 0.070*4.2856 - j*0.107*4.2856)
           = Z_0 * (1.300 - 0.4586j)
        """
        sigma = 13000
        f = 0.1 * sigma / utils.RHO_0  # X = 0.1
        freqs = np.array([f])
        Zc, _ = miki(freqs, sigma)

        assert Zc[0].real == pytest.approx(utils.Z_0 * 1.300, abs=1.0)
        assert Zc[0].imag == pytest.approx(-utils.Z_0 * 0.4586, abs=1.0)

    def test_miki_kc_at_x01(self):
        """Miki kc at X=0.1 — hand-calculated from Miki (1990) coefficients.

        X^(-0.618) = 10^0.618 ≈ 4.1498
        kc = k0 * (1 + 0.109*4.1498 - j*0.160*4.1498)
           = k0 * (1.4523 - 0.6640j)
        """
        sigma = 13000
        f = 0.1 * sigma / utils.RHO_0
        freqs = np.array([f])
        _, kc = miki(freqs, sigma)

        k0 = 2 * np.pi * f / utils.C_0
        assert kc[0].real == pytest.approx(k0 * 1.4523, abs=0.01)
        assert kc[0].imag == pytest.approx(-k0 * 0.6640, abs=0.01)

    def test_delany_bazley_zc_at_x01(self):
        """D-B Zc at X=0.1 — from Delany & Bazley (1970) coefficients.

        X^(-0.754) ≈ 5.675, X^(-0.732) ≈ 5.393
        Zc = Z_0 * (1 + 0.0571*5.675 - j*0.0870*5.393)
           = Z_0 * (1.324 - 0.4692j)
        """
        sigma = 13000
        f = 0.1 * sigma / utils.RHO_0
        freqs = np.array([f])
        Zc, _ = delany_bazley(freqs, sigma)

        assert Zc[0].real == pytest.approx(utils.Z_0 * 1.324, abs=1.0)
        assert Zc[0].imag == pytest.approx(-utils.Z_0 * 0.4692, abs=1.0)

    def test_allard_champoux_structure(self):
        """A-C: effective density and bulk modulus approach free-air values at high freq.

        From Zc = sqrt(rho_eff * K_eff) and kc = omega * sqrt(rho_eff / K_eff),
        recover rho_eff and K_eff and verify they converge to rho_0 and gamma*P0.
        """
        freqs = np.array([500.0, 1000.0, 5000.0, 20000.0])
        sigma = 13000
        Zc, kc = allard_champoux(freqs, sigma)
        omega = 2 * np.pi * freqs

        # Recover effective density and bulk modulus
        rho_eff = Zc * kc / omega
        K_eff = Zc * omega / kc

        # Physical: positive real parts at all frequencies
        assert np.all(rho_eff.real > 0)
        assert np.all(K_eff.real > 0)

        # At high frequency, rho_eff → RHO_0
        assert rho_eff[-1].real == pytest.approx(utils.RHO_0, rel=0.05)
        # At high frequency, K_eff → gamma * P0 = 141855 Pa
        assert K_eff[-1].real == pytest.approx(utils.GAMMA * 101325.0, rel=0.05)


# ---------------------------------------------------------------------------
# 2. Porous absorption validation (OC703 reference)
# ---------------------------------------------------------------------------


class TestPorousAbsorptionValidation:
    """Validate OC703 absorption against CLAUDE.md reference and physical expectations.

    Ref: CLAUDE.md ("alpha ≈ 0.50 at 500 Hz ... consistent with impedance tube data")
    """

    @pytest.fixture
    def oc703_50mm(self, freqs):
        """OC703 50mm normal-incidence absorption via Miki model."""
        Zc, kc = miki(freqs, 13000)
        T = tmm.porous_layer_matrix(freqs, Zc, kc, 0.050)
        return tmm.absorption_from_layers(freqs, [T])

    def test_alpha_250hz(self, freqs, oc703_50mm):
        """OC703 50mm at 250 Hz: ~0.20 (low-frequency, thin absorber)."""
        alpha = alpha_at_freq(oc703_50mm, freqs, 250)
        assert alpha == pytest.approx(0.20, abs=0.05)

    def test_alpha_500hz(self, freqs, oc703_50mm):
        """OC703 50mm at 500 Hz: ~0.50 (CLAUDE.md reference point)."""
        alpha = alpha_at_freq(oc703_50mm, freqs, 500)
        assert alpha == pytest.approx(0.50, abs=0.05)

    def test_alpha_1000hz(self, freqs, oc703_50mm):
        """OC703 50mm at 1000 Hz: ~0.90."""
        alpha = alpha_at_freq(oc703_50mm, freqs, 1000)
        assert alpha == pytest.approx(0.90, abs=0.05)

    def test_alpha_2000hz(self, freqs, oc703_50mm):
        """OC703 50mm at 2000 Hz: >0.95 (well above quarter-wavelength)."""
        alpha = alpha_at_freq(oc703_50mm, freqs, 2000)
        assert alpha > 0.95

    def test_nrc(self, freqs, oc703_50mm):
        """OC703 50mm NRC: ~0.65 (average of 250/500/1000/2000 Hz)."""
        nrc = utils.nrc(oc703_50mm, freqs)
        assert nrc == pytest.approx(0.65, abs=0.05)

    def test_100mm_nrc(self, freqs):
        """OC703 100mm NRC: ~0.85 (doubled thickness)."""
        Zc, kc = miki(freqs, 13000)
        alpha = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc, kc, 0.100)]
        )
        nrc = utils.nrc(alpha, freqs)
        assert nrc == pytest.approx(0.85, abs=0.10)

    def test_quarter_wavelength_peak(self, freqs):
        """At quarter-wavelength frequency (c/4d ≈ 1715 Hz), alpha approaches 1.0."""
        d = 0.050  # 50mm
        f_qw = utils.C_0 / (4 * d)  # ~1715 Hz
        Zc, kc = miki(freqs, 13000)
        alpha = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc, kc, d)]
        )
        alpha_qw = alpha_at_freq(alpha, freqs, f_qw)
        assert alpha_qw > 0.95


# ---------------------------------------------------------------------------
# 3. Cross-model agreement
# ---------------------------------------------------------------------------


class TestCrossModelAgreement:
    """D-B, Miki, and A-C models should agree for standard materials."""

    def test_db_vs_miki_nrc_frequencies(self, freqs):
        """D-B vs Miki: alpha difference < 0.05 at NRC frequencies for OC703 50mm."""
        sigma = 13000
        d = 0.050

        Zc_db, kc_db = delany_bazley(freqs, sigma)
        alpha_db = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc_db, kc_db, d)]
        )

        Zc_m, kc_m = miki(freqs, sigma)
        alpha_m = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc_m, kc_m, d)]
        )

        for f_target in [250, 500, 1000, 2000]:
            a_db = alpha_at_freq(alpha_db, freqs, f_target)
            a_m = alpha_at_freq(alpha_m, freqs, f_target)
            assert abs(a_db - a_m) < 0.05, (
                f"D-B vs Miki differ by {abs(a_db - a_m):.3f} at {f_target} Hz"
            )

    def test_high_frequency_convergence(self):
        """All 3 models: |Zc|/Z_0 converges toward 1.0 at 20 kHz."""
        freqs = np.array([20000.0])
        sigma = 13000

        for model_fn in [delany_bazley, miki, allard_champoux]:
            Zc, _ = model_fn(freqs, sigma)
            ratio = abs(Zc[0]) / utils.Z_0
            assert 0.95 < ratio < 1.10, (
                f"{model_fn.__name__}: |Zc|/Z_0 = {ratio:.3f} at 20 kHz"
            )

    def test_jca_vs_miki_nrc(self, freqs):
        """JCA with typical OC703 microstructure: NRC within 0.10 of Miki."""
        sigma = 13000
        d = 0.050

        Zc_m, kc_m = miki(freqs, sigma)
        alpha_m = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc_m, kc_m, d)]
        )
        nrc_m = utils.nrc(alpha_m, freqs)

        # JCA with typical OC703 microstructure parameters
        Zc_j, kc_j = jca(
            freqs, sigma,
            porosity=0.97,
            tortuosity=1.06,
            viscous_length=120e-6,
            thermal_length=240e-6,
        )
        alpha_j = tmm.absorption_from_layers(
            freqs, [tmm.porous_layer_matrix(freqs, Zc_j, kc_j, d)]
        )
        nrc_j = utils.nrc(alpha_j, freqs)

        assert abs(nrc_j - nrc_m) < 0.10, (
            f"JCA NRC={nrc_j:.2f} vs Miki NRC={nrc_m:.2f}"
        )


# ---------------------------------------------------------------------------
# 4. Helmholtz resonator validation
# ---------------------------------------------------------------------------


class TestHelmholtzValidation:
    """Analytical resonance frequency checks against hand calculations.

    Ref: Kinsler et al. (2000) Ch. 9; Ingard (1953).
    """

    def test_classic_bottle(self):
        """Classic bottle: V=1L, S=3cm^2, L=5cm -> f_0 ~ 116 Hz.

        Hand calculation:
            r = sqrt(3e-4 / pi) ~ 9.77 mm
            L_eff = 0.05 + 0.85*2*r ~ 0.0666 m
            f_0 = (343/2pi) * sqrt(3e-4 / (1e-3 * L_eff)) ~ 115.9 Hz
        """
        r = np.sqrt(3e-4 / np.pi)
        f0 = helmholtz_resonance(
            neck_length_m=0.05,
            neck_radius_m=r,
            cavity_volume_m3=1e-3,
        )

        # Verify against analytical formula with end correction
        L_eff = 0.05 + 0.85 * 2 * r
        f0_expected = (utils.C_0 / (2 * np.pi)) * np.sqrt(
            np.pi * r**2 / (1e-3 * L_eff)
        )
        assert f0 == pytest.approx(f0_expected, rel=1e-6)
        assert f0 == pytest.approx(116, abs=1.0)

    def test_arbitrary_geometry(self):
        """L=10mm, r=5mm, V=50cm^3 -> exact formula check."""
        r = 0.005
        L = 0.010
        V = 50e-6
        f0 = helmholtz_resonance(L, r, V)

        A = np.pi * r**2
        L_eff = L + 0.85 * 2 * r
        f0_expected = (utils.C_0 / (2 * np.pi)) * np.sqrt(A / (V * L_eff))

        assert f0 == pytest.approx(f0_expected, rel=1e-10)

    def test_end_correction_magnitude(self):
        """Verify L_eff = L + 0.85 * 2r (flanged end correction on both ends)."""
        r = 0.01  # 10mm
        L = 0.02  # 20mm
        V = 1e-4  # 100 cm^3
        L_eff_expected = L + 0.85 * 2 * r  # 0.037 m

        f0 = helmholtz_resonance(L, r, V)
        # Frequency without end correction
        A = np.pi * r**2
        f0_no_corr = (utils.C_0 / (2 * np.pi)) * np.sqrt(A / (V * L))

        # With end correction, frequency is lower
        assert f0 < f0_no_corr
        # Verify exact frequency ratio matches sqrt(L / L_eff)
        assert f0 / f0_no_corr == pytest.approx(np.sqrt(L / L_eff_expected), rel=1e-10)

    def test_impedance_imaginary_zero_at_resonance(self):
        """Im(Z) crosses zero at resonance (lossless case)."""
        r = 0.005
        L = 0.01
        V = 50e-6
        f0 = helmholtz_resonance(L, r, V)

        freqs = np.linspace(f0 * 0.5, f0 * 1.5, 10000)
        Z = helmholtz_impedance(freqs, L, r, V, viscous_loss=False)
        im_Z = Z.imag

        # Below resonance: stiffness dominates -> Im(Z) < 0
        # Above resonance: mass dominates -> Im(Z) > 0
        idx = np.argmin(np.abs(freqs - f0))
        assert im_Z[max(0, idx - 10)] * im_Z[min(len(im_Z) - 1, idx + 10)] < 0, (
            "Im(Z) should change sign at resonance"
        )


# ---------------------------------------------------------------------------
# 5. Panel absorber validation
# ---------------------------------------------------------------------------


class TestPanelAbsorberValidation:
    """Panel resonance frequency validation against standard formula.

    f_0 = (c_0 / 2pi) * sqrt(rho_0 / (m * d))

    Ref: Kuttruff (2009) Ch. 6.4.
    """

    def test_3mm_plywood_100mm(self):
        """3mm plywood (1.5 kg/m^2) + 100mm cavity -> ~155 Hz."""
        f0 = panel_absorber_resonance(1.5, 0.100)
        assert f0 == pytest.approx(155, abs=5)

    def test_6mm_mdf_50mm(self):
        """6mm MDF (4.5 kg/m^2) + 50mm cavity -> ~126 Hz."""
        f0 = panel_absorber_resonance(4.5, 0.050)
        assert f0 == pytest.approx(126, abs=5)

    def test_12mm_plywood_200mm(self):
        """12mm plywood (7.2 kg/m^2) + 200mm cavity -> ~50 Hz."""
        f0 = panel_absorber_resonance(7.2, 0.200)
        assert f0 == pytest.approx(50, abs=3)

    def test_approximation_60_over_sqrt_md(self):
        """Exact formula matches classic 60/sqrt(md) approximation within 1%.

        The approximation 60/sqrt(m*d) (m in kg/m^2, d in m) is derived from
        f_0 = (c_0/2pi)*sqrt(rho_0/md) using standard air properties.
        """
        test_cases = [(1.5, 0.100), (4.5, 0.050), (7.2, 0.200), (2.0, 0.075)]

        for m, d in test_cases:
            f0_exact = panel_absorber_resonance(m, d)
            f0_approx = 60.0 / np.sqrt(m * d)
            assert f0_exact == pytest.approx(f0_approx, rel=0.01), (
                f"m={m}, d={d}: exact={f0_exact:.1f} Hz, approx={f0_approx:.1f} Hz"
            )


# ---------------------------------------------------------------------------
# 6. Room mode validation
# ---------------------------------------------------------------------------


class TestRoomModesValidation:
    """Analytical room mode frequencies for standard room dimensions.

    f_mnp = (c_0/2) * sqrt((m/Lx)^2 + (n/Ly)^2 + (p/Lz)^2)

    Ref: Kuttruff (2009) Ch. 2.2.
    """

    @pytest.fixture
    def modes_5x4x3(self):
        """Room modes for a 5m x 4m x 3m room."""
        from acoustic.optimizer import room_mode_frequencies

        return room_mode_frequencies(5.0, 4.0, 3.0)

    def _find_mode(self, modes, mode_tuple):
        for m in modes:
            if m["mode"] == mode_tuple:
                return m
        raise ValueError(f"Mode {mode_tuple} not found")

    def test_axial_modes(self, modes_5x4x3):
        """Axial modes: (1,0,0)=34.3, (0,1,0)=42.9, (0,0,1)=57.2 Hz."""
        m100 = self._find_mode(modes_5x4x3, (1, 0, 0))
        assert m100["frequency_hz"] == pytest.approx(34.3, abs=0.1)
        assert m100["type"] == "axial"

        m010 = self._find_mode(modes_5x4x3, (0, 1, 0))
        assert m010["frequency_hz"] == pytest.approx(42.9, abs=0.1)
        assert m010["type"] == "axial"

        m001 = self._find_mode(modes_5x4x3, (0, 0, 1))
        assert m001["frequency_hz"] == pytest.approx(57.2, abs=0.1)
        assert m001["type"] == "axial"

    def test_tangential_mode(self, modes_5x4x3):
        """Tangential mode (1,1,0) = 54.9 Hz."""
        m110 = self._find_mode(modes_5x4x3, (1, 1, 0))
        assert m110["frequency_hz"] == pytest.approx(54.9, abs=0.1)
        assert m110["type"] == "tangential"

    def test_oblique_mode(self, modes_5x4x3):
        """Oblique mode (1,1,1) = 79.3 Hz."""
        m111 = self._find_mode(modes_5x4x3, (1, 1, 1))
        assert m111["frequency_hz"] == pytest.approx(79.3, abs=0.1)
        assert m111["type"] == "oblique"

    def test_mode_classification(self, modes_5x4x3):
        """Verify mode type classification is consistent with index counts."""
        for m in modes_5x4x3:
            nx, ny, nz = m["mode"]
            nonzero = sum(1 for x in (nx, ny, nz) if x > 0)
            if nonzero == 1:
                assert m["type"] == "axial"
            elif nonzero == 2:
                assert m["type"] == "tangential"
            else:
                assert m["type"] == "oblique"

    def test_cube_degenerate_modes(self):
        """Cube 4x4x4m: three degenerate first axial modes at 42.9 Hz."""
        from acoustic.optimizer import room_mode_frequencies

        modes = room_mode_frequencies(4.0, 4.0, 4.0)

        m100 = self._find_mode(modes, (1, 0, 0))
        m010 = self._find_mode(modes, (0, 1, 0))
        m001 = self._find_mode(modes, (0, 0, 1))

        expected = 343.0 / (2 * 4.0)  # = 42.875 Hz
        assert m100["frequency_hz"] == pytest.approx(expected, abs=0.1)
        assert m010["frequency_hz"] == pytest.approx(expected, abs=0.1)
        assert m001["frequency_hz"] == pytest.approx(expected, abs=0.1)


# ---------------------------------------------------------------------------
# 7. Perforated panel validation
# ---------------------------------------------------------------------------


class TestPerforatedPanelValidation:
    """Physical behavior checks for perforated and micro-perforated panels.

    Ref: Maa, JASA 104(5) (1998); Ingard, JASA 25(6) (1953).
    """

    def _perforated_alpha(self, freqs, panel_impedance_fn, cavity_depth_m, **kwargs):
        """Compute absorption for a perforated panel + air cavity via TMM."""
        Z = panel_impedance_fn(freqs, **kwargs)
        T_panel = tmm.impedance_sheet_matrix(freqs, Z)
        T_air = air_gap_matrix(freqs, cavity_depth_m)
        return tmm.absorption_from_layers(freqs, [T_panel, T_air])

    def test_mpp_peak_absorption(self, freqs):
        """MPP (0.5mm holes, 1mm panel, 50mm cavity): peak alpha > 0.90."""
        alpha = self._perforated_alpha(
            freqs, mpp_maa, 0.050,
            panel_thickness_m=0.001,
            hole_diameter_m=0.0005,
            porosity=0.01,
        )
        assert np.max(alpha) > 0.90

    def test_mpp_peak_frequency_range(self, freqs):
        """MPP (0.5mm holes, 1mm panel, 50mm cavity): peak in 200-700 Hz."""
        alpha = self._perforated_alpha(
            freqs, mpp_maa, 0.050,
            panel_thickness_m=0.001,
            hole_diameter_m=0.0005,
            porosity=0.01,
        )
        peak_freq = freqs[np.argmax(alpha)]
        assert 200 < peak_freq < 700

    def test_macro_perforated_peak_range(self, freqs):
        """Perforated panel (5mm holes, 6mm panel, 100mm cavity): peak in 200-500 Hz."""
        alpha = self._perforated_alpha(
            freqs, perforated_ingard, 0.100,
            panel_thickness_m=0.006,
            hole_diameter_m=0.005,
            hole_spacing_m=0.025,
        )
        peak_freq = freqs[np.argmax(alpha)]
        assert 200 < peak_freq < 500

    def test_deeper_cavity_shifts_peak_lower(self, freqs):
        """Deeper cavity should shift MPP absorption peak to lower frequency."""
        alpha_shallow = self._perforated_alpha(
            freqs, mpp_maa, 0.025,
            panel_thickness_m=0.001,
            hole_diameter_m=0.0005,
            porosity=0.01,
        )
        alpha_deep = self._perforated_alpha(
            freqs, mpp_maa, 0.100,
            panel_thickness_m=0.001,
            hole_diameter_m=0.0005,
            porosity=0.01,
        )
        peak_shallow = freqs[np.argmax(alpha_shallow)]
        peak_deep = freqs[np.argmax(alpha_deep)]
        assert peak_deep < peak_shallow

    def test_mpp_broader_than_macro_perforated(self, freqs):
        """MPP should have broader absorption bandwidth than macro-perforated panel.

        Micro-perforations provide higher viscous resistance, giving wider
        absorption bandwidth compared to macro holes.
        """
        alpha_mpp = self._perforated_alpha(
            freqs, mpp_maa, 0.050,
            panel_thickness_m=0.001,
            hole_diameter_m=0.0005,
            porosity=0.01,
        )
        alpha_macro = self._perforated_alpha(
            freqs, perforated_ingard, 0.050,
            panel_thickness_m=0.006,
            hole_diameter_m=0.005,
            hole_spacing_m=0.025,
        )

        # Count frequency bins where alpha > 0.5
        bw_mpp = np.sum(alpha_mpp > 0.5)
        bw_macro = np.sum(alpha_macro > 0.5)
        assert bw_mpp > bw_macro, (
            f"MPP bandwidth ({bw_mpp} bins > 0.5) should exceed "
            f"macro-perforated ({bw_macro} bins > 0.5)"
        )
