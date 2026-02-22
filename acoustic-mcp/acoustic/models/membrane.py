"""Membrane / panel absorber model.

Limp membrane (mass-law) layer for TMM calculations, and convenience function
for panel absorber resonance frequency.

References:
    Kuttruff (2009), Room Acoustics, Ch. 6.4.
    Cox & D'Antonio (2009), Acoustic Absorbers and Diffusers, Ch. 4.
"""

from __future__ import annotations

import numpy as np

from acoustic.utils import C_0, RHO_0


def membrane_matrix(
    freqs: np.ndarray,
    mass_per_area: float,
) -> np.ndarray:
    """Transfer matrix for a limp membrane (mass-law layer).

    The membrane impedance is Z = j * omega * m, where m is the surface
    mass density. This is a zero-thickness impedance sheet.

    Args:
        freqs: Frequency array (Hz), shape (N,).
        mass_per_area: Surface mass density (kg/m²).

    Returns:
        Transfer matrix array, shape (N, 2, 2), complex.
    """
    omega = 2.0 * np.pi * freqs
    Z_mem = 1j * omega * mass_per_area

    N = len(freqs)
    T = np.zeros((N, 2, 2), dtype=complex)
    T[:, 0, 0] = 1.0
    T[:, 0, 1] = Z_mem
    T[:, 1, 0] = 0.0
    T[:, 1, 1] = 1.0
    return T


def panel_absorber_resonance(
    mass_per_area: float,
    air_gap_m: float,
    c0: float = C_0,
    rho0: float = RHO_0,
) -> float:
    """Resonance frequency of a panel absorber (membrane + air gap).

    f_0 = (c_0 / (2*pi)) * sqrt(rho_0 / (m * d))

    where m is surface mass density and d is air gap depth.

    Args:
        mass_per_area: Surface mass density (kg/m²).
        air_gap_m: Air gap depth behind panel (m).
        c0: Speed of sound (m/s).
        rho0: Air density (kg/m³).

    Returns:
        Resonance frequency in Hz.
    """
    return (c0 / (2.0 * np.pi)) * np.sqrt(rho0 / (mass_per_area * air_gap_m))
