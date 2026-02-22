"""Transfer Matrix Method (TMM) engine.

Computes absorption coefficients for multi-layer acoustic absorber stacks
backed by a rigid wall. Each layer is represented by a 2×2 complex transfer
matrix relating pressure and particle velocity between the layer's front and
back faces.

References:
    Cox & D'Antonio (2009), Acoustic Absorbers and Diffusers, Ch. 2.
    Allard & Atalla (2009), Propagation of Sound in Porous Media, Ch. 11.
"""

from __future__ import annotations

import numpy as np

from acoustic.utils import Z_0


def porous_layer_matrix(
    freqs: np.ndarray,
    Zc: np.ndarray,
    kc: np.ndarray,
    thickness: float,
) -> np.ndarray:
    """Transfer matrix for a porous layer with characteristic impedance Zc and wavenumber kc.

    Args:
        freqs: Frequency array (Hz). Used only for shape; Zc and kc are pre-computed.
        Zc: Complex characteristic impedance array, shape (N,).
        kc: Complex wavenumber array, shape (N,).
        thickness: Layer thickness in metres.

    Returns:
        Transfer matrix array of shape (N, 2, 2), complex.
    """
    kd = kc * thickness
    cos_kd = np.cos(kd)
    sin_kd = np.sin(kd)

    N = len(freqs)
    T = np.zeros((N, 2, 2), dtype=complex)
    T[:, 0, 0] = cos_kd
    T[:, 0, 1] = 1j * Zc * sin_kd
    T[:, 1, 0] = 1j * sin_kd / Zc
    T[:, 1, 1] = cos_kd
    return T


def impedance_sheet_matrix(
    freqs: np.ndarray,
    Z: np.ndarray,
) -> np.ndarray:
    """Transfer matrix for a thin impedance sheet (e.g. perforated panel).

    A zero-thickness layer with acoustic impedance Z. Used for perforated
    panels, slotted panels, and micro-perforated panels.

    Args:
        freqs: Frequency array (Hz), shape (N,).
        Z: Complex acoustic impedance array, shape (N,).

    Returns:
        Transfer matrix array of shape (N, 2, 2), complex.
    """
    N = len(freqs)
    T = np.zeros((N, 2, 2), dtype=complex)
    T[:, 0, 0] = 1.0
    T[:, 0, 1] = Z
    T[:, 1, 0] = 0.0
    T[:, 1, 1] = 1.0
    return T


def multiply_chain(matrices: list[np.ndarray]) -> np.ndarray:
    """Multiply a chain of transfer matrices (front to back, left to right).

    Args:
        matrices: List of arrays, each shape (N, 2, 2). Ordered from the
            outermost layer (sound-incident side) to the layer nearest the
            rigid backing.

    Returns:
        Total transfer matrix, shape (N, 2, 2).
    """
    if not matrices:
        raise ValueError("At least one layer matrix is required")

    T_total = matrices[0].copy()
    for T in matrices[1:]:
        # Per-frequency 2×2 matrix multiplication
        T_total = np.einsum("nij,njk->nik", T_total, T)
    return T_total


def surface_impedance(T: np.ndarray) -> np.ndarray:
    """Surface impedance from total transfer matrix with rigid-wall backing.

    For a rigid wall (u=0 at the back), Z_s = T[0,0] / T[1,0].

    Args:
        T: Total transfer matrix, shape (N, 2, 2).

    Returns:
        Complex surface impedance array, shape (N,).
    """
    # When T[1,0] is zero (identity matrix / rigid wall), impedance is infinite
    # → reflection coefficient R = 1 → alpha = 0 (perfect reflection)
    with np.errstate(divide="ignore", invalid="ignore"):
        Zs = T[:, 0, 0] / T[:, 1, 0]
    # Replace inf/nan with a very large impedance (perfect reflector)
    Zs = np.where(np.isfinite(Zs), Zs, 1e30 + 0j)
    return Zs


def absorption_coefficient(
    Zs: np.ndarray,
    Z0: float = Z_0,
    clip: bool = True,
) -> np.ndarray:
    """Normal-incidence absorption coefficient from surface impedance.

    alpha = 1 - |R|^2, where R = (Zs - Z0) / (Zs + Z0).

    Args:
        Zs: Complex surface impedance array, shape (N,).
        Z0: Characteristic impedance of air (default: standard conditions).
        clip: If True, clip result to [0, 1].

    Returns:
        Absorption coefficient array, shape (N,).
    """
    R = (Zs - Z0) / (Zs + Z0)
    alpha = 1.0 - np.abs(R) ** 2
    if clip:
        alpha = np.clip(alpha, 0.0, 1.0)
    return np.real(alpha)


def absorption_from_layers(
    freqs: np.ndarray,
    layer_matrices: list[np.ndarray],
    Z0: float = Z_0,
) -> np.ndarray:
    """Convenience: compute normal-incidence absorption from a list of layer matrices.

    Args:
        freqs: Frequency array (Hz), shape (N,).
        layer_matrices: List of transfer matrices, each (N, 2, 2).
        Z0: Characteristic impedance of air.

    Returns:
        Absorption coefficient array, shape (N,).
    """
    T = multiply_chain(layer_matrices)
    Zs = surface_impedance(T)
    return absorption_coefficient(Zs, Z0)
