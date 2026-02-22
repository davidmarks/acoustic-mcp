"""Acoustic absorber optimizer.

Uses scipy.optimize.differential_evolution to find optimal absorber designs
for target frequencies or broadband NRC, subject to depth constraints.

References:
    Kuttruff (2009), Room Acoustics, Ch. 2.2 (room modes).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import differential_evolution

from acoustic import tmm, utils
from acoustic.models import air, porous


@dataclass
class LayerStack:
    """A candidate absorber design."""

    material: str
    sigma: float
    thickness_mm: float
    air_gap_mm: float
    model: str
    alpha: np.ndarray
    freqs: np.ndarray
    nrc: float
    saa: float
    peak_freq_hz: float
    peak_alpha: float


# Subset of materials suitable for optimization
OPTIMIZER_MATERIALS = {
    "oc703_fiberglass": 13000,
    "oc705_fiberglass": 26000,
    "rockwool_60": 11000,
    "thinsulate_sm600l": 4000,
    "polyester_batting_soft": 2000,
    "rpet_felt_soft": 8000,
    "basotect_melamine": 5000,
    "recycled_cotton_batt": 4000,
}


def _evaluate_design(
    freqs: np.ndarray,
    sigma: float,
    thickness_m: float,
    air_gap_m: float,
    model_name: str = "miki",
) -> tuple[np.ndarray, float, float]:
    """Compute alpha, NRC, SAA for a single porous layer + air gap design."""
    model_fn = getattr(porous, model_name)
    Zc, kc = model_fn(freqs, sigma)

    matrices = [tmm.porous_layer_matrix(freqs, Zc, kc, thickness_m)]
    if air_gap_m > 0:
        matrices.append(air.air_gap_matrix(freqs, air_gap_m))

    alpha = tmm.absorption_from_layers(freqs, matrices)
    nrc_val = utils.nrc(alpha, freqs)
    saa_val = utils.saa(alpha, freqs)
    return alpha, nrc_val, saa_val


def optimize_for_frequency(
    target_hz: float,
    max_depth_mm: float,
    material_options: list[str] | None = None,
    model: str = "miki",
) -> list[LayerStack]:
    """Find absorber designs that maximize absorption at a target frequency.

    Optimizes material thickness and air gap depth (within total depth budget)
    for each candidate material.

    Args:
        target_hz: Target frequency in Hz.
        max_depth_mm: Maximum total depth budget in mm.
        material_options: List of material keys from OPTIMIZER_MATERIALS.
            If None, all materials are tried.
        model: Porous model to use.

    Returns:
        Top 3 candidate designs sorted by alpha at target frequency.
    """
    freqs = utils.frequency_axis(20, 20000, 12)
    target_idx = int(np.argmin(np.abs(freqs - target_hz)))

    if max_depth_mm < 5:
        raise ValueError(f"max_depth_mm must be at least 5 mm (got {max_depth_mm})")

    if material_options is None:
        material_options = list(OPTIMIZER_MATERIALS.keys())

    candidates: list[LayerStack] = []

    for mat_name in material_options:
        sigma = OPTIMIZER_MATERIALS.get(mat_name)
        if sigma is None:
            continue

        max_depth_m = max_depth_mm / 1000.0

        def objective(x: np.ndarray, _sigma: float = sigma) -> float:
            thickness_m, air_gap_m = x
            if thickness_m + air_gap_m > max_depth_m:
                return 1.0  # penalty
            alpha, _, _ = _evaluate_design(freqs, _sigma, thickness_m, air_gap_m, model)
            return -alpha[target_idx]  # minimize negative alpha

        # Bounds: thickness 5mm to max_depth, air gap 0 to max_depth
        min_thick = 0.005
        bounds = [
            (min_thick, max_depth_m),
            (0.0, max_depth_m - min_thick),
        ]

        result = differential_evolution(
            objective,
            bounds,
            seed=42,
            maxiter=50,
            tol=1e-4,
            polish=True,
        )

        thickness_m, air_gap_m = result.x
        # Enforce depth constraint
        if thickness_m + air_gap_m > max_depth_m:
            air_gap_m = max_depth_m - thickness_m

        alpha, nrc_val, saa_val = _evaluate_design(freqs, sigma, thickness_m, air_gap_m, model)
        peak_idx = int(np.argmax(alpha))

        candidates.append(LayerStack(
            material=mat_name,
            sigma=sigma,
            thickness_mm=round(thickness_m * 1000, 1),
            air_gap_mm=round(air_gap_m * 1000, 1),
            model=model,
            alpha=alpha,
            freqs=freqs,
            nrc=nrc_val,
            saa=saa_val,
            peak_freq_hz=round(float(freqs[peak_idx]), 1),
            peak_alpha=round(float(alpha[peak_idx]), 4),
        ))

    # Sort by alpha at target frequency (descending)
    candidates.sort(key=lambda c: -c.alpha[target_idx])
    return candidates[:3]


def optimize_nrc(
    max_depth_mm: float,
    material_options: list[str] | None = None,
    model: str = "miki",
    freq_range: tuple[float, float] = (200.0, 2500.0),
) -> list[LayerStack]:
    """Find absorber designs that maximize broadband NRC/SAA.

    Args:
        max_depth_mm: Maximum total depth budget in mm.
        material_options: List of material keys. If None, all are tried.
        model: Porous model to use.
        freq_range: Frequency range for SAA calculation (default 200-2500 Hz).

    Returns:
        Top 3 candidate designs sorted by SAA.
    """
    if max_depth_mm < 5:
        raise ValueError(f"max_depth_mm must be at least 5 mm (got {max_depth_mm})")

    freqs = utils.frequency_axis(20, 20000, 12)

    if material_options is None:
        material_options = list(OPTIMIZER_MATERIALS.keys())

    candidates: list[LayerStack] = []

    for mat_name in material_options:
        sigma = OPTIMIZER_MATERIALS.get(mat_name)
        if sigma is None:
            continue

        max_depth_m = max_depth_mm / 1000.0

        def objective(x: np.ndarray, _sigma: float = sigma) -> float:
            thickness_m, air_gap_m = x
            if thickness_m + air_gap_m > max_depth_m:
                return 1.0
            _, _, saa_val = _evaluate_design(freqs, _sigma, thickness_m, air_gap_m, model)
            return -saa_val

        min_thick = 0.005
        bounds = [
            (min_thick, max_depth_m),
            (0.0, max_depth_m - min_thick),
        ]

        result = differential_evolution(
            objective,
            bounds,
            seed=42,
            maxiter=50,
            tol=1e-4,
            polish=True,
        )

        thickness_m, air_gap_m = result.x
        if thickness_m + air_gap_m > max_depth_m:
            air_gap_m = max_depth_m - thickness_m

        alpha, nrc_val, saa_val = _evaluate_design(freqs, sigma, thickness_m, air_gap_m, model)
        peak_idx = int(np.argmax(alpha))

        candidates.append(LayerStack(
            material=mat_name,
            sigma=sigma,
            thickness_mm=round(thickness_m * 1000, 1),
            air_gap_mm=round(air_gap_m * 1000, 1),
            model=model,
            alpha=alpha,
            freqs=freqs,
            nrc=nrc_val,
            saa=saa_val,
            peak_freq_hz=round(float(freqs[peak_idx]), 1),
            peak_alpha=round(float(alpha[peak_idx]), 4),
        ))

    candidates.sort(key=lambda c: -c.saa)
    return candidates[:3]


def room_mode_frequencies(
    lx: float,
    ly: float,
    lz: float,
    max_order: int = 3,
    c0: float = utils.C_0,
) -> list[dict]:
    """Calculate room mode frequencies.

    Computes axial, tangential, and oblique modes for a rectangular room.

    f_mnp = (c_0/2) * sqrt((m/Lx)² + (n/Ly)² + (p/Lz)²)

    Args:
        lx: Room length in metres.
        ly: Room width in metres.
        lz: Room height in metres.
        max_order: Maximum mode order to compute (default 3).
        c0: Speed of sound (m/s).

    Returns:
        List of dicts with keys: frequency_hz, mode (m,n,p), type (axial/tangential/oblique).
    """
    modes = []
    for m in range(0, max_order + 1):
        for n in range(0, max_order + 1):
            for p in range(0, max_order + 1):
                if m == 0 and n == 0 and p == 0:
                    continue

                f = (c0 / 2.0) * np.sqrt(
                    (m / lx) ** 2 + (n / ly) ** 2 + (p / lz) ** 2
                )

                # Classify mode type
                nonzero = sum(1 for x in (m, n, p) if x > 0)
                if nonzero == 1:
                    mode_type = "axial"
                elif nonzero == 2:
                    mode_type = "tangential"
                else:
                    mode_type = "oblique"

                modes.append({
                    "frequency_hz": round(float(f), 1),
                    "mode": (m, n, p),
                    "type": mode_type,
                })

    modes.sort(key=lambda x: x["frequency_hz"])
    return modes


def classify_design_approach(
    target_hz: float,
    depth_budget_mm: float,
) -> dict:
    """Classify the recommended absorber approach based on frequency and depth constraints.

    Args:
        target_hz: Target frequency in Hz.
        depth_budget_mm: Available depth in mm.

    Returns:
        Dict with recommended_approach and rationale.
    """
    if target_hz > 500:
        return {
            "recommended_approach": "porous_absorber",
            "rationale": (
                f"At {target_hz} Hz, a porous absorber (fiberglass, mineral wool, or foam) "
                f"is sufficient. Quarter-wavelength depth is {343 / (4 * target_hz) * 1000:.0f} mm."
            ),
        }
    elif 150 <= target_hz <= 500 and depth_budget_mm >= 100:
        return {
            "recommended_approach": "porous_absorber_with_air_gap",
            "rationale": (
                f"At {target_hz} Hz with {depth_budget_mm} mm depth budget, use a porous absorber "
                f"with an air gap. The air gap shifts the absorption peak to lower frequencies."
            ),
        }
    elif 80 <= target_hz <= 250 and depth_budget_mm < 150:
        return {
            "recommended_approach": "helmholtz_or_mpp",
            "rationale": (
                f"At {target_hz} Hz with only {depth_budget_mm} mm depth, a Helmholtz resonator "
                f"or micro-perforated panel with cavity provides narrowband absorption in a "
                f"compact form factor."
            ),
        }
    elif target_hz < 80:
        return {
            "recommended_approach": "panel_absorber_or_large_helmholtz",
            "rationale": (
                f"At {target_hz} Hz, a panel/membrane absorber or large Helmholtz resonator "
                f"is needed. These provide low-frequency absorption through mass-spring resonance."
            ),
        }
    else:
        return {
            "recommended_approach": "porous_absorber_with_air_gap",
            "rationale": (
                f"At {target_hz} Hz, a porous absorber with an air gap is recommended. "
                f"Optimize the gap depth to shift absorption to the target frequency."
            ),
        }
