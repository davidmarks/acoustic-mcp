"""Porous absorber models.

Four empirical/semi-empirical models for the complex characteristic impedance
(Zc) and wavenumber (kc) of fibrous and porous materials. Each function takes
frequency and flow resistivity (and optionally microstructure parameters) and
returns (Zc, kc) arrays suitable for building TMM layer matrices.

References:
    Delany & Bazley, Acustica 23 (1970).
    Miki, JASE 11(1) (1990).
    Allard & Champoux, JASA 91(6) (1992).
    Johnson et al., JASA 87(1) (1987) + Champoux & Allard, JASA 89(2) (1991).
"""

from __future__ import annotations

import numpy as np

from acoustic.utils import C_0, GAMMA, PR, RHO_0, Z_0, ETA


def delany_bazley(
    freqs: np.ndarray,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Delany-Bazley empirical model (1970).

    Valid for 0.01 < X < 1.0 where X = rho_0 * f / sigma.

    Args:
        freqs: Frequency array (Hz).
        sigma: Flow resistivity (N·s/m⁴), also known as (Pa·s/m²).

    Returns:
        (Zc, kc) — characteristic impedance and wavenumber arrays.
    """
    # Delany-Bazley use X = rho_0 * f / sigma
    X = RHO_0 * freqs / sigma

    Zc = Z_0 * (1.0 + 0.0571 * X**(-0.754) - 1j * 0.0870 * X**(-0.732))

    k0 = 2.0 * np.pi * freqs / C_0
    kc = k0 * (1.0 + 0.0978 * X**(-0.700) - 1j * 0.1890 * X**(-0.595))

    return Zc, kc


def miki(
    freqs: np.ndarray,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Miki model (1990) — improved Delany-Bazley with better low-frequency behaviour.

    Valid for 0.01 < X < 1.0 where X = rho_0 * f / sigma.

    Args:
        freqs: Frequency array (Hz).
        sigma: Flow resistivity (N·s/m⁴).

    Returns:
        (Zc, kc) — characteristic impedance and wavenumber arrays.
    """
    X = RHO_0 * freqs / sigma

    Zc = Z_0 * (1.0 + 0.070 * X**(-0.632) - 1j * 0.107 * X**(-0.632))

    k0 = 2.0 * np.pi * freqs / C_0
    kc = k0 * (1.0 + 0.109 * X**(-0.618) - 1j * 0.160 * X**(-0.618))

    return Zc, kc


def allard_champoux(
    freqs: np.ndarray,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Allard-Champoux model (1992).

    Improved empirical model with separate viscous and thermal effects.
    Valid for 0.01 < X < 1.0 where X = rho_0 * f / sigma.

    Args:
        freqs: Frequency array (Hz).
        sigma: Flow resistivity (N·s/m⁴).

    Returns:
        (Zc, kc) — characteristic impedance and wavenumber arrays.
    """
    omega = 2.0 * np.pi * freqs
    X = RHO_0 * freqs / sigma

    # Effective density (viscous effects)
    rho_eff = RHO_0 * (1.0 + 0.0764 * X**(-0.700) - 1j * 0.136 * X**(-0.700))

    # Effective bulk modulus (thermal effects)
    K_eff = (
        GAMMA * 101325.0  # P0 * gamma
        / (GAMMA - (GAMMA - 1.0) / (1.0 + 0.0668 * X**(-0.707) - 1j * 0.1170 * X**(-0.707)))
    )

    Zc = np.sqrt(rho_eff * K_eff)
    kc = omega * np.sqrt(rho_eff / K_eff)

    return Zc, kc


def jca(
    freqs: np.ndarray,
    sigma: float,
    porosity: float,
    tortuosity: float,
    viscous_length: float,
    thermal_length: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Johnson-Champoux-Allard (JCA) model.

    Five-parameter microstructure model for rigid-frame porous media.

    Args:
        freqs: Frequency array (Hz).
        sigma: Flow resistivity (N·s/m⁴).
        porosity: Open porosity (0 to 1), symbol phi.
        tortuosity: Tortuosity, symbol alpha_inf (>= 1).
        viscous_length: Viscous characteristic length (m), symbol Lambda.
        thermal_length: Thermal characteristic length (m), symbol Lambda'.

    Returns:
        (Zc, kc) — characteristic impedance and wavenumber arrays.
    """
    omega = 2.0 * np.pi * freqs
    P0 = 101325.0  # atmospheric pressure (Pa)

    # Johnson effective density (viscous effects)
    # rho_eff = rho_0 * alpha_inf * (1 + sigma*phi/(j*omega*rho_0*alpha_inf) * sqrt(1 + j*4*alpha_inf^2*eta*rho_0*omega / (sigma^2*Lambda^2*phi^2)))
    omega_safe = np.where(omega == 0, 1e-30, omega)

    sigma_phi = sigma * porosity
    factor_v = (
        4.0 * tortuosity**2 * ETA * RHO_0 * omega_safe
        / (sigma**2 * viscous_length**2 * porosity**2)
    )
    G_v = np.sqrt(1.0 + 1j * factor_v)
    rho_eff = (
        RHO_0 * tortuosity
        * (1.0 + sigma_phi / (1j * omega_safe * RHO_0 * tortuosity) * G_v)
    )

    # Champoux-Allard effective bulk modulus (thermal effects)
    # K_eff = gamma*P0 / (gamma - (gamma-1) / (1 + 8*eta/(j*Lambda'^2*Pr*rho_0*omega) * sqrt(1 + j*rho_0*omega*Pr*Lambda'^2/(16*eta))))
    factor_t = (
        RHO_0 * omega_safe * PR * thermal_length**2
        / (16.0 * ETA)
    )
    G_t = np.sqrt(1.0 + 1j * factor_t)
    thermal_term = 1.0 + 8.0 * ETA / (1j * thermal_length**2 * PR * RHO_0 * omega_safe) * G_t
    K_eff = GAMMA * P0 / (GAMMA - (GAMMA - 1.0) / thermal_term)

    Zc = np.sqrt(rho_eff * K_eff) / porosity
    kc = omega * np.sqrt(rho_eff / K_eff)

    return Zc, kc


# Flow resistivity reference table for common materials
MATERIAL_DATABASE: dict[str, dict] = {
    "oc703_fiberglass": {
        "name": "Owens Corning 703 Fiberglass",
        "sigma_range": (10000, 16000),
        "sigma_typical": 13000,
        "density_kg_m3": 48,
        "notes": "Standard acoustic fiberglass board. Widely used reference material.",
    },
    "oc705_fiberglass": {
        "name": "Owens Corning 705 Fiberglass",
        "sigma_range": (20000, 32000),
        "sigma_typical": 26000,
        "density_kg_m3": 80,
        "notes": "Higher density fiberglass. Better low-frequency performance.",
    },
    "rockwool_60": {
        "name": "Rockwool (60 kg/m³)",
        "sigma_range": (8000, 14000),
        "sigma_typical": 11000,
        "density_kg_m3": 60,
        "notes": "Mineral wool insulation. Common in Europe.",
    },
    "thinsulate_sm600l": {
        "name": "3M Thinsulate SM600L",
        "sigma_range": (3000, 5000),
        "sigma_typical": 4000,
        "density_kg_m3": 16,
        "notes": "Lightweight synthetic. Popular in automotive and DIY studio treatment.",
    },
    "polyester_batting_soft": {
        "name": "Soft Polyester Batting",
        "sigma_range": (1000, 3000),
        "sigma_typical": 2000,
        "density_kg_m3": 20,
        "notes": "Low-density polyester. Moderate absorption, easy to handle.",
    },
    "rpet_felt_soft": {
        "name": "Recycled PET Felt (Soft Grade)",
        "sigma_range": (5000, 12000),
        "sigma_typical": 8000,
        "density_kg_m3": 100,
        "notes": "Recycled polyester felt. Good balance of absorption and rigidity.",
    },
    "rpet_rigid_board": {
        "name": "Recycled PET Rigid Board",
        "sigma_range": (50000, 150000),
        "sigma_typical": 80000,
        "density_kg_m3": 200,
        "notes": "High-density rigid board. Acts more like perforated panel than porous absorber.",
    },
    "basotect_melamine": {
        "name": "Basotect Melamine Foam",
        "sigma_range": (3000, 8000),
        "sigma_typical": 5000,
        "density_kg_m3": 10,
        "notes": "Open-cell melamine foam. Very lightweight, good broadband absorption.",
    },
    "recycled_cotton_batt": {
        "name": "Recycled Cotton Batt",
        "sigma_range": (2000, 6000),
        "sigma_typical": 4000,
        "density_kg_m3": 30,
        "notes": "Recycled denim/cotton. Eco-friendly, moderate performance.",
    },
}
