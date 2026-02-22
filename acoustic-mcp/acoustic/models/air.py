"""Air gap layer transfer matrix.

Lossless air layer of given thickness, modelled as a simple propagation delay.

Reference:
    Allard & Atalla (2009), Propagation of Sound in Porous Media, eq. 11.1.
"""

from __future__ import annotations

import numpy as np

from acoustic.utils import C_0, Z_0


def air_gap_matrix(
    freqs: np.ndarray,
    thickness_m: float,
    c0: float = C_0,
    z0: float = Z_0,
) -> np.ndarray:
    """Transfer matrix for a lossless air gap.

    T = [[cos(k0*d),      j*Z0*sin(k0*d)],
         [j*sin(k0*d)/Z0, cos(k0*d)      ]]

    Args:
        freqs: Frequency array (Hz), shape (N,).
        thickness_m: Air gap thickness in metres.
        c0: Speed of sound (m/s).
        z0: Characteristic impedance of air (Pa·s/m).

    Returns:
        Transfer matrix array, shape (N, 2, 2), complex.
    """
    k0 = 2.0 * np.pi * freqs / c0
    kd = k0 * thickness_m
    cos_kd = np.cos(kd)
    sin_kd = np.sin(kd)

    N = len(freqs)
    T = np.zeros((N, 2, 2), dtype=complex)
    T[:, 0, 0] = cos_kd
    T[:, 0, 1] = 1j * z0 * sin_kd
    T[:, 1, 0] = 1j * sin_kd / z0
    T[:, 1, 1] = cos_kd
    return T
