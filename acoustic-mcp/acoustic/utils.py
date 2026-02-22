"""Acoustic utility functions.

Frequency axes, standard metrics (NRC, SAA), and air properties
at standard conditions (20°C, 101.325 kPa).
"""

import numpy as np

# Air properties at 20°C, 101.325 kPa
RHO_0 = 1.204  # kg/m³ — air density
C_0 = 343.0  # m/s — speed of sound
Z_0 = RHO_0 * C_0  # Pa·s/m — characteristic impedance of air

# Dynamic viscosity of air at 20°C
ETA = 1.81e-5  # Pa·s

# Thermal conductivity of air at 20°C
KAPPA_AIR = 0.0257  # W/(m·K)

# Specific heat at constant pressure
CP_AIR = 1005.0  # J/(kg·K)

# Ratio of specific heats
GAMMA = 1.4

# Prandtl number
PR = ETA * CP_AIR / KAPPA_AIR  # ~0.71

# ISO 266 third-octave band center frequencies (Hz)
THIRD_OCTAVE_CENTERS = np.array([
    20, 25, 31.5, 40, 50, 63, 80, 100, 125, 160,
    200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600,
    2000, 2500, 3150, 4000, 5000, 6300, 8000, 10000, 12500, 16000, 20000,
])

# NRC frequencies (ASTM C423)
NRC_FREQUENCIES = np.array([250.0, 500.0, 1000.0, 2000.0])

# SAA third-octave bands 200–2500 Hz (ASTM C423-09a)
SAA_FREQUENCIES = np.array([
    200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500,
], dtype=float)

# Octave band center frequencies for summary
OCTAVE_CENTERS = np.array([63.0, 125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0])


def frequency_axis(
    f_min: float = 20.0,
    f_max: float = 20000.0,
    points_per_octave: int = 12,
) -> np.ndarray:
    """Generate logarithmically spaced frequency axis.

    Args:
        f_min: Minimum frequency in Hz.
        f_max: Maximum frequency in Hz.
        points_per_octave: Number of points per octave (12 = third-octave resolution).

    Returns:
        1-D array of frequencies in Hz.
    """
    n_octaves = np.log2(f_max / f_min)
    n_points = int(np.ceil(n_octaves * points_per_octave)) + 1
    return np.geomspace(f_min, f_max, n_points)


def third_octave_bands(
    f_min: float = 20.0,
    f_max: float = 20000.0,
) -> np.ndarray:
    """Return ISO 266 third-octave band center frequencies within range."""
    mask = (THIRD_OCTAVE_CENTERS >= f_min) & (THIRD_OCTAVE_CENTERS <= f_max)
    return THIRD_OCTAVE_CENTERS[mask].copy()


def _interpolate_at(alpha: np.ndarray, freqs: np.ndarray, target_freqs: np.ndarray) -> np.ndarray:
    """Interpolate alpha values at target frequencies using log-frequency interpolation."""
    return np.interp(np.log10(target_freqs), np.log10(freqs), alpha)


def nrc(alpha: np.ndarray, freqs: np.ndarray) -> float:
    """Noise Reduction Coefficient per ASTM C423.

    Average of absorption coefficients at 250, 500, 1000, and 2000 Hz,
    rounded to the nearest 0.05.

    Args:
        alpha: Absorption coefficient array.
        freqs: Corresponding frequency array in Hz.

    Returns:
        NRC value (0.0 to 1.0).
    """
    values = _interpolate_at(alpha, freqs, NRC_FREQUENCIES)
    raw = float(np.mean(np.clip(values, 0.0, 1.0)))
    return round(raw * 20) / 20  # round to nearest 0.05


def saa(alpha: np.ndarray, freqs: np.ndarray) -> float:
    """Sound Absorption Average per ASTM C423-09a.

    Average of absorption coefficients at 12 third-octave bands
    from 200 to 2500 Hz, rounded to the nearest 0.01.

    Args:
        alpha: Absorption coefficient array.
        freqs: Corresponding frequency array in Hz.

    Returns:
        SAA value (0.0 to 1.0).
    """
    values = _interpolate_at(alpha, freqs, SAA_FREQUENCIES)
    raw = float(np.mean(np.clip(values, 0.0, 1.0)))
    return round(raw, 2)


def octave_band_summary(alpha: np.ndarray, freqs: np.ndarray) -> dict[str, float]:
    """Absorption coefficients at standard octave band centers.

    Returns:
        Dict with keys like "63", "125", "250", "500", "1000", "2000", "4000"
        and float alpha values.
    """
    values = _interpolate_at(alpha, freqs, OCTAVE_CENTERS)
    return {
        str(int(f)): round(float(np.clip(v, 0.0, 1.0)), 3)
        for f, v in zip(OCTAVE_CENTERS, values)
    }
