"""Diffuse field (random incidence) absorption integration.

Integrates the angle-dependent absorption coefficient over incidence angles
using the Paris formula and Gaussian quadrature.

References:
    ISO 354:2003.
    Kuttruff (2009), Room Acoustics, Ch. 4.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import fixed_quad

from acoustic.utils import Z_0


def diffuse_field_alpha_from_impedance(
    Zs: np.ndarray,
    n_points: int = 10,
    theta_max_deg: float = 78.0,
    z0: float = Z_0,
) -> np.ndarray:
    """Compute diffuse-field absorption using the locally-reacting surface approximation.

    For a locally-reacting surface, the surface impedance Zs is independent
    of angle. The angle-dependent reflection coefficient is:

        R(theta) = (Zs * cos(theta) - Z0) / (Zs * cos(theta) + Z0)

    and the diffuse-field absorption is integrated via the Paris formula:

        alpha_diff = 2 * integral_0^theta_max [ alpha(theta) * sin(theta) * cos(theta) ] dtheta

    Args:
        Zs: Complex surface impedance array, shape (N,).
        n_points: Number of Gaussian quadrature points (default: 10).
        theta_max_deg: Maximum integration angle in degrees (default: 78°).
        z0: Characteristic impedance of air.

    Returns:
        Diffuse-field absorption coefficient array, shape (N,).
    """
    theta_max_rad = np.radians(theta_max_deg)
    N = len(Zs)

    # Evaluate integrand at all quadrature points at once for efficiency.
    # We use explicit Gauss-Legendre quadrature to avoid scipy's fixed_quad
    # broadcast issues.
    nodes, weights = np.polynomial.legendre.leggauss(n_points)
    # Map from [-1, 1] to [0, theta_max_rad]
    thetas = 0.5 * theta_max_rad * (nodes + 1.0)
    w = 0.5 * theta_max_rad * weights

    result = np.zeros(N)
    for j in range(n_points):
        theta = thetas[j]
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)

        # Locally-reacting: R depends on angle via cos(theta) factor
        R = (Zs * cos_theta - z0) / (Zs * cos_theta + z0)
        alpha_theta = np.clip(1.0 - np.abs(R) ** 2, 0.0, 1.0)

        result += w[j] * alpha_theta * sin_theta * cos_theta

    # Paris formula factor of 2
    alpha_diff = 2.0 * np.real(result)
    return np.clip(alpha_diff, 0.0, 1.0)
