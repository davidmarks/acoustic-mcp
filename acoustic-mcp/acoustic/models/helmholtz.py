"""Helmholtz resonator model.

Resonance frequency, complex impedance, and absorption area calculations
for a single Helmholtz resonator.

References:
    Ingard, JASA 25(6) (1953).
    Kinsler et al., Fundamentals of Acoustics (2000), Ch. 9.
"""

from __future__ import annotations

import numpy as np

from acoustic.utils import C_0, ETA, RHO_0


def helmholtz_resonance(
    neck_length_m: float,
    neck_radius_m: float,
    cavity_volume_m3: float,
    c0: float = C_0,
) -> float:
    """Resonance frequency of a Helmholtz resonator.

    f_0 = (c_0 / (2*pi)) * sqrt(A_neck / (V_cavity * L_eff))

    where L_eff = neck_length + delta, delta = 0.85 * 2r (Ingard flanged end correction).

    Args:
        neck_length_m: Physical neck length (m).
        neck_radius_m: Neck radius (m).
        cavity_volume_m3: Cavity volume (m³).
        c0: Speed of sound (m/s).

    Returns:
        Resonance frequency in Hz.
    """
    A_neck = np.pi * neck_radius_m**2
    # Ingard end correction: flanged opening on both ends of neck
    delta = 0.85 * 2.0 * neck_radius_m
    L_eff = neck_length_m + delta

    f0 = (c0 / (2.0 * np.pi)) * np.sqrt(A_neck / (cavity_volume_m3 * L_eff))
    return float(f0)


def helmholtz_impedance(
    freqs: np.ndarray,
    neck_length_m: float,
    neck_radius_m: float,
    cavity_volume_m3: float,
    viscous_loss: bool = True,
    c0: float = C_0,
    rho0: float = RHO_0,
) -> np.ndarray:
    """Complex acoustic impedance of a Helmholtz resonator.

    Z(f) = R_neck + j*(omega*M_neck - K_cavity/omega)

    where M_neck = rho_0 * L_eff / A_neck (mass),
          K_cavity = rho_0 * c_0^2 / V_cavity (stiffness),
          R_neck = viscous resistance in the neck.

    Args:
        freqs: Frequency array (Hz).
        neck_length_m: Physical neck length (m).
        neck_radius_m: Neck radius (m).
        cavity_volume_m3: Cavity volume (m³).
        viscous_loss: Include viscous neck losses (default: True).
        c0: Speed of sound (m/s).
        rho0: Air density (kg/m³).

    Returns:
        Complex impedance array Z(f), shape (N,).
    """
    omega = 2.0 * np.pi * freqs
    A_neck = np.pi * neck_radius_m**2

    # End correction
    delta = 0.85 * 2.0 * neck_radius_m
    L_eff = neck_length_m + delta

    # Acoustic mass (neck inertance)
    M_neck = rho0 * L_eff / A_neck

    # Acoustic stiffness (cavity compliance)
    K_cavity = rho0 * c0**2 / cavity_volume_m3

    # Viscous resistance in the neck
    if viscous_loss:
        delta_v = np.sqrt(2.0 * ETA / (rho0 * omega))
        R_neck = (8.0 * ETA * L_eff) / (np.pi * neck_radius_m**4) + rho0 * omega * delta_v / A_neck
    else:
        R_neck = np.zeros_like(freqs)

    # Impedance: R + j*(omega*M - K/omega)
    Z = R_neck + 1j * (omega * M_neck - K_cavity / omega)
    return Z


def helmholtz_absorption_area(
    freqs: np.ndarray,
    neck_length_m: float,
    neck_radius_m: float,
    cavity_volume_m3: float,
    c0: float = C_0,
    rho0: float = RHO_0,
) -> np.ndarray:
    """Absorption cross-section (equivalent absorption area) of a Helmholtz resonator.

    A(f) = (4 * R_rad * R_neck) / |Z(f)|^2 * lambda^2 / (4*pi)

    At resonance, theoretical maximum: A_max = lambda^2 / (2*pi).

    Args:
        freqs: Frequency array (Hz).
        neck_length_m: Physical neck length (m).
        neck_radius_m: Neck radius (m).
        cavity_volume_m3: Cavity volume (m³).
        c0: Speed of sound (m/s).
        rho0: Air density (kg/m³).

    Returns:
        Absorption area array A(f) in m², shape (N,).
    """
    omega = 2.0 * np.pi * freqs
    A_neck = np.pi * neck_radius_m**2
    wavelength = c0 / freqs

    Z = helmholtz_impedance(freqs, neck_length_m, neck_radius_m, cavity_volume_m3,
                            viscous_loss=True, c0=c0, rho0=rho0)

    # Radiation resistance (one side, flanged)
    k0 = omega / c0
    R_rad = rho0 * c0 * (k0 * neck_radius_m)**2 / (2.0 * np.pi)

    # Viscous neck resistance
    delta = 0.85 * 2.0 * neck_radius_m
    L_eff = neck_length_m + delta
    delta_v = np.sqrt(2.0 * ETA / (rho0 * omega))
    R_neck = (8.0 * ETA * L_eff) / (np.pi * neck_radius_m**4) + rho0 * omega * delta_v / A_neck

    # Absorption cross-section
    Z0_acoustic = rho0 * c0
    A = wavelength**2 / np.pi * R_rad * R_neck / np.abs(Z)**2

    return np.maximum(A, 0.0)
