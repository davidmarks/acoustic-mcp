"""Tests for porous absorber models."""

import numpy as np
import pytest

from acoustic.models.porous import (
    allard_champoux,
    delany_bazley,
    jca,
    miki,
    MATERIAL_DATABASE,
)
from acoustic.utils import RHO_0


class TestPorousModels:
    """Verify all four porous models return physically reasonable results."""

    @pytest.fixture
    def freqs(self):
        return np.array([125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0])

    @pytest.fixture
    def sigma_oc703(self):
        return 13000  # typical OC703

    def test_delany_bazley_returns_complex(self, freqs, sigma_oc703):
        Zc, kc = delany_bazley(freqs, sigma_oc703)
        assert Zc.dtype == complex
        assert kc.dtype == complex
        assert len(Zc) == len(freqs)
        assert len(kc) == len(freqs)

    def test_miki_returns_complex(self, freqs, sigma_oc703):
        Zc, kc = miki(freqs, sigma_oc703)
        assert Zc.dtype == complex
        assert kc.dtype == complex

    def test_allard_champoux_returns_complex(self, freqs, sigma_oc703):
        Zc, kc = allard_champoux(freqs, sigma_oc703)
        assert Zc.dtype == complex
        assert kc.dtype == complex

    def test_jca_returns_complex(self, freqs, sigma_oc703):
        # Typical JCA parameters for fiberglass
        Zc, kc = jca(
            freqs,
            sigma=sigma_oc703,
            porosity=0.97,
            tortuosity=1.06,
            viscous_length=120e-6,
            thermal_length=240e-6,
        )
        assert Zc.dtype == complex
        assert kc.dtype == complex

    def test_real_part_positive(self, freqs, sigma_oc703):
        """Real part of Zc should be positive (dissipative medium)."""
        for model in [delany_bazley, miki]:
            Zc, kc = model(freqs, sigma_oc703)
            assert np.all(np.real(Zc) > 0), f"{model.__name__}: Zc real part should be positive"

    def test_imaginary_part_negative(self, freqs, sigma_oc703):
        """Imaginary part of kc should be negative (attenuation)."""
        for model in [delany_bazley, miki]:
            Zc, kc = model(freqs, sigma_oc703)
            assert np.all(np.imag(kc) < 0), f"{model.__name__}: kc imaginary part should be negative"

    def test_higher_sigma_higher_impedance(self, freqs):
        """Higher flow resistivity should give higher characteristic impedance magnitude."""
        Zc_low, _ = miki(freqs, 5000)
        Zc_high, _ = miki(freqs, 20000)
        # At low frequencies, higher sigma → higher |Zc|
        assert np.abs(Zc_high[0]) > np.abs(Zc_low[0])

    def test_models_converge_at_high_freq(self, sigma_oc703):
        """All single-parameter models should converge toward Z_0 at high frequencies."""
        freqs = np.array([10000.0, 20000.0])
        from acoustic.utils import Z_0
        for model in [delany_bazley, miki]:
            Zc, _ = model(freqs, sigma_oc703)
            # At high frequency, Zc should approach Z_0
            ratio = np.abs(Zc[-1]) / Z_0
            assert 0.8 < ratio < 1.5, f"{model.__name__}: |Zc| should approach Z_0 at high freq"


class TestMaterialDatabase:
    def test_database_not_empty(self):
        assert len(MATERIAL_DATABASE) > 0

    def test_all_entries_have_required_keys(self):
        for key, data in MATERIAL_DATABASE.items():
            assert "name" in data
            assert "sigma_range" in data
            assert "sigma_typical" in data
            assert "density_kg_m3" in data
            assert "notes" in data

    def test_sigma_range_ordered(self):
        for key, data in MATERIAL_DATABASE.items():
            low, high = data["sigma_range"]
            assert low < high, f"{key}: sigma_range should be (low, high)"

    def test_sigma_typical_in_range(self):
        for key, data in MATERIAL_DATABASE.items():
            low, high = data["sigma_range"]
            assert low <= data["sigma_typical"] <= high, f"{key}: typical sigma outside range"
