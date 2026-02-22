"""Perforated and slotted panel models.

Three sub-models for panels with holes or slots, each returning the complex
acoustic impedance Z(f) of the panel. These are inserted into the TMM chain
as thin impedance sheet layers.

References:
    Ingard, JASA 25(6) (1953).
    Kristiansen & Vigran, Applied Acoustics 43 (1994).
    Maa, JASA 104(5) (1998).
"""

from __future__ import annotations

import numpy as np

from acoustic.utils import C_0, ETA, RHO_0, Z_0


def _perforate_porosity(hole_diameter_m: float, spacing_m: float) -> float:
    """Porosity of a square-grid perforated panel."""
    if spacing_m <= 0:
        raise ValueError(f"hole_spacing must be positive (got {spacing_m * 1000:.1f} mm)")
    if hole_diameter_m >= spacing_m:
        raise ValueError(
            f"hole_diameter ({hole_diameter_m * 1000:.1f} mm) must be less than "
            f"hole_spacing ({spacing_m * 1000:.1f} mm)"
        )
    epsilon = np.pi * (hole_diameter_m / 2) ** 2 / spacing_m**2
    return epsilon


def perforated_ingard(
    freqs: np.ndarray,
    panel_thickness_m: float,
    hole_diameter_m: float,
    hole_spacing_m: float,
) -> np.ndarray:
    """Acoustic impedance of a macro-perforated panel (Ingard 1953).

    For holes > 1 mm diameter.

    Args:
        freqs: Frequency array (Hz).
        panel_thickness_m: Panel thickness (m).
        hole_diameter_m: Hole diameter (m).
        hole_spacing_m: Hole centre-to-centre spacing (m).

    Returns:
        Complex acoustic impedance array Z(f), shape (N,).
    """
    omega = 2.0 * np.pi * freqs
    r = hole_diameter_m / 2.0
    epsilon = _perforate_porosity(hole_diameter_m, hole_spacing_m)

    # Viscous boundary layer thickness
    delta_v = np.sqrt(2.0 * ETA / (RHO_0 * omega))

    # End correction: flanged opening on both sides
    delta_end = 2.0 * 0.85 * r  # ~1.7 * r for two flanged ends

    # Effective neck length
    t_eff = panel_thickness_m + delta_end

    # Resistive part (viscous losses in the hole)
    R = (8.0 * ETA * t_eff) / (epsilon * r**2) + RHO_0 * omega * delta_v / epsilon

    # Reactive part (mass of air in the hole)
    X = RHO_0 * omega * t_eff / epsilon

    return R + 1j * X


def slotted_kristiansen(
    freqs: np.ndarray,
    panel_thickness_m: float,
    slot_width_m: float,
    slot_spacing_m: float,
) -> np.ndarray:
    """Acoustic impedance of a slotted panel (Kristiansen & Vigran 1994).

    Args:
        freqs: Frequency array (Hz).
        panel_thickness_m: Panel thickness (m).
        slot_width_m: Slot width (m).
        slot_spacing_m: Slot centre-to-centre spacing (m).

    Returns:
        Complex acoustic impedance array Z(f), shape (N,).
    """
    omega = 2.0 * np.pi * freqs
    w = slot_width_m
    epsilon = w / slot_spacing_m  # porosity for slots

    # Viscous boundary layer thickness
    delta_v = np.sqrt(2.0 * ETA / (RHO_0 * omega))

    # End correction for slot: 0.85 * (w/2) per end, two ends
    # w is the full slot width, so half-width is the characteristic length
    delta_end = 2.0 * 0.85 * (w / 2.0)

    t_eff = panel_thickness_m + delta_end

    # Resistive: viscous losses in the slot
    R = (12.0 * ETA * t_eff) / (epsilon * w**2) + RHO_0 * omega * delta_v / epsilon

    # Reactive: mass of air in the slot
    X = RHO_0 * omega * t_eff / epsilon

    return R + 1j * X


def mpp_maa(
    freqs: np.ndarray,
    panel_thickness_m: float,
    hole_diameter_m: float,
    porosity: float,
) -> np.ndarray:
    """Acoustic impedance of a micro-perforated panel (Maa 1998).

    For holes < 1 mm diameter where viscous effects dominate.

    Args:
        freqs: Frequency array (Hz).
        panel_thickness_m: Panel thickness (m).
        hole_diameter_m: Hole diameter (m). Typically 0.1-1.0 mm.
        porosity: Open area ratio (0 to 1).

    Returns:
        Complex acoustic impedance array Z(f), shape (N,).
    """
    omega = 2.0 * np.pi * freqs
    r = hole_diameter_m / 2.0
    d = hole_diameter_m
    t = panel_thickness_m
    p = porosity

    # Perforation constant (Maa's k parameter)
    k = d * np.sqrt(omega * RHO_0 / (4.0 * ETA))

    # Resistive part
    R = (32.0 * ETA * t / (p * d**2)) * (np.sqrt(1.0 + k**2 / 32.0) + np.sqrt(2.0) * k * d / (32.0 * t))

    # Reactive part
    X = (RHO_0 * omega * t / p) * (1.0 + 1.0 / np.sqrt(9.0 + k**2 / 2.0) + 0.85 * d / t)

    return R + 1j * X
