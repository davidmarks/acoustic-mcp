"""Acoustic absorber design MCP server.

Provides tools for calculating absorption coefficients of porous absorbers,
perforated panels, membrane absorbers, and Helmholtz resonators using the
Transfer Matrix Method (TMM).
"""

from __future__ import annotations

from typing import Annotated, Literal

import numpy as np
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

from acoustic import optimizer, tmm, utils
from acoustic.diffuse import diffuse_field_alpha_from_impedance
from acoustic.models import air, helmholtz, membrane, perforated, porous

mcp = FastMCP("acoustic-mcp")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class AbsorptionResult(BaseModel):
    """Standard response for all absorption calculations."""

    frequencies: list[float] = Field(description="Frequency array (Hz)")
    alpha: list[float] = Field(description="Absorption coefficient at each frequency")
    nrc: float = Field(description="Noise Reduction Coefficient (ASTM C423)")
    saa: float = Field(description="Sound Absorption Average (ASTM C423-09a)")
    peak_frequency_hz: float = Field(description="Frequency of maximum absorption")
    peak_alpha: float = Field(description="Maximum absorption coefficient")
    octave_summary: dict[str, float] = Field(
        description="Absorption at octave band centers (63-4000 Hz)"
    )


class HelmholtzResult(BaseModel):
    """Response for Helmholtz resonator calculations."""

    resonance_frequency_hz: float
    frequencies: list[float]
    impedance_real: list[float]
    impedance_imag: list[float]
    absorption_area_m2: list[float]
    peak_absorption_area_m2: float
    theoretical_max_area_m2: float = Field(
        description="lambda^2 / (2*pi) at resonance"
    )


class MaterialInfo(BaseModel):
    """Material properties lookup result."""

    name: str
    sigma_range: tuple[int, int] = Field(description="Flow resistivity range (N·s/m⁴)")
    sigma_typical: int = Field(description="Typical flow resistivity (N·s/m⁴)")
    density_kg_m3: int
    notes: str


class PorousLayerSpec(BaseModel):
    type: Literal["porous"] = "porous"
    sigma: float = Field(description="Flow resistivity (N·s/m⁴)")
    thickness_mm: float = Field(description="Layer thickness (mm)")
    model: str = Field(
        default="miki",
        description="Porous model: delany_bazley, miki, allard_champoux, or jca",
    )


class AirLayerSpec(BaseModel):
    type: Literal["air"] = "air"
    thickness_mm: float = Field(description="Air gap thickness (mm)")


class PerforatedLayerSpec(BaseModel):
    type: Literal["perforated"] = "perforated"
    hole_diameter_mm: float = Field(description="Hole diameter (mm)")
    hole_spacing_mm: float = Field(description="Hole centre-to-centre spacing (mm)")
    panel_thickness_mm: float = Field(description="Panel thickness (mm)")
    panel_type: str = Field(
        default="perforated",
        description="Panel type: perforated, slotted, or mpp",
    )


class MembraneLayerSpec(BaseModel):
    type: Literal["membrane"] = "membrane"
    mass_per_area_kg_m2: float = Field(description="Surface mass density (kg/m²)")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

POROUS_MODELS = {
    "delany_bazley": porous.delany_bazley,
    "miki": porous.miki,
    "allard_champoux": porous.allard_champoux,
}


def _get_porous_model(name: str):
    if name == "jca":
        return porous.jca
    model = POROUS_MODELS.get(name)
    if model is None:
        raise ValueError(f"Unknown porous model '{name}'. Available: {list(POROUS_MODELS.keys()) + ['jca']}")
    return model


def _make_absorption_result(freqs: np.ndarray, alpha: np.ndarray) -> AbsorptionResult:
    peak_idx = int(np.argmax(alpha))
    return AbsorptionResult(
        frequencies=[round(float(f), 2) for f in freqs],
        alpha=[round(float(a), 4) for a in alpha],
        nrc=utils.nrc(alpha, freqs),
        saa=utils.saa(alpha, freqs),
        peak_frequency_hz=round(float(freqs[peak_idx]), 1),
        peak_alpha=round(float(alpha[peak_idx]), 4),
        octave_summary=utils.octave_band_summary(alpha, freqs),
    )


def _build_perforated_impedance(
    freqs: np.ndarray,
    spec: PerforatedLayerSpec,
) -> np.ndarray:
    t_m = spec.panel_thickness_mm / 1000.0
    if spec.panel_type == "perforated":
        return perforated.perforated_ingard(
            freqs, t_m, spec.hole_diameter_mm / 1000.0, spec.hole_spacing_mm / 1000.0
        )
    elif spec.panel_type == "slotted":
        return perforated.slotted_kristiansen(
            freqs, t_m, spec.hole_diameter_mm / 1000.0, spec.hole_spacing_mm / 1000.0
        )
    elif spec.panel_type == "mpp":
        porosity = perforated._perforate_porosity(
            spec.hole_diameter_mm / 1000.0, spec.hole_spacing_mm / 1000.0
        )
        return perforated.mpp_maa(freqs, t_m, spec.hole_diameter_mm / 1000.0, porosity)
    else:
        raise ValueError(f"Unknown panel type '{spec.panel_type}'. Use: perforated, slotted, mpp")


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def ping() -> str:
    """Health check — verify the acoustic MCP server is running."""
    return "acoustic-mcp is running"


@mcp.tool()
def calculate_porous_layer(
    sigma: Annotated[float, Field(description="Flow resistivity in N·s/m⁴ (e.g. 13000 for OC703)")],
    thickness_mm: Annotated[float, Field(description="Material thickness in mm")],
    model: Annotated[str, Field(description="Porous model: delany_bazley, miki, or allard_champoux")] = "miki",
    air_gap_mm: Annotated[float, Field(description="Air gap behind material in mm")] = 0.0,
    incidence: Annotated[str, Field(description="Incidence type: normal or diffuse")] = "normal",
) -> AbsorptionResult:
    """Calculate absorption coefficient of a porous absorber layer.

    Computes the frequency-dependent absorption coefficient for fibrous or
    porous materials (fiberglass, mineral wool, foam, polyester) using the
    Transfer Matrix Method. Optionally includes an air gap behind the material.

    Common materials and their flow resistivities:
    - OC703 fiberglass: 10000-16000 (typical 13000)
    - OC705 fiberglass: 20000-32000 (typical 26000)
    - Rockwool 60 kg/m³: 8000-14000 (typical 11000)
    - Thinsulate SM600L: 3000-5000 (typical 4000)
    - Basotect melamine foam: 3000-8000 (typical 5000)
    """
    if model == "jca":
        raise ValueError("JCA model requires 5 microstructure parameters. Use calculate_multilayer with a full JCA layer spec instead.")

    freqs = utils.frequency_axis(20, 20000, 12)
    model_fn = _get_porous_model(model)
    Zc, kc = model_fn(freqs, sigma)

    matrices = [tmm.porous_layer_matrix(freqs, Zc, kc, thickness_mm / 1000.0)]
    if air_gap_mm > 0:
        matrices.append(air.air_gap_matrix(freqs, air_gap_mm / 1000.0))

    if incidence == "diffuse":
        # Locally-reacting surface approximation for diffuse field
        T = tmm.multiply_chain(matrices)
        Zs = tmm.surface_impedance(T)
        alpha = diffuse_field_alpha_from_impedance(Zs)
    else:
        alpha = tmm.absorption_from_layers(freqs, matrices)

    return _make_absorption_result(freqs, alpha)


@mcp.tool()
def calculate_perforated_panel(
    hole_diameter_mm: Annotated[float, Field(description="Hole diameter in mm (or slot width for slotted panels)")],
    hole_spacing_mm: Annotated[float, Field(description="Hole centre-to-centre spacing in mm")],
    panel_thickness_mm: Annotated[float, Field(description="Panel thickness in mm")],
    air_gap_mm: Annotated[float, Field(description="Air cavity depth behind panel in mm")],
    panel_type: Annotated[str, Field(description="Panel type: perforated (>1mm holes), slotted (rectangular slots), or mpp (micro-perforated <1mm)")] = "perforated",
) -> AbsorptionResult:
    """Calculate absorption coefficient of a perforated, slotted, or micro-perforated panel.

    Models a panel with holes or slots backed by an air cavity and rigid wall.
    The panel acts as a tuned absorber, with peak absorption near a resonance
    frequency determined by the panel geometry and cavity depth.
    """
    freqs = utils.frequency_axis(20, 20000, 12)

    spec = PerforatedLayerSpec(
        hole_diameter_mm=hole_diameter_mm,
        hole_spacing_mm=hole_spacing_mm,
        panel_thickness_mm=panel_thickness_mm,
        panel_type=panel_type,
    )
    Z = _build_perforated_impedance(freqs, spec)

    matrices = [
        tmm.impedance_sheet_matrix(freqs, Z),
        air.air_gap_matrix(freqs, air_gap_mm / 1000.0),
    ]
    alpha = tmm.absorption_from_layers(freqs, matrices)
    return _make_absorption_result(freqs, alpha)


@mcp.tool()
def calculate_membrane_absorber(
    mass_per_area_kg_m2: Annotated[float, Field(description="Surface mass density in kg/m² (e.g. 3mm plywood ≈ 1.5 kg/m²)")],
    air_gap_mm: Annotated[float, Field(description="Air cavity depth behind membrane in mm")],
) -> AbsorptionResult:
    """Calculate absorption coefficient of a membrane / panel absorber.

    Models a limp membrane or thin panel backed by an air cavity and rigid wall.
    The system resonates at a frequency determined by the panel mass and cavity depth,
    providing low-frequency absorption.

    Common panel masses:
    - 3mm plywood: ~1.5 kg/m²
    - 6mm MDF: ~4.5 kg/m²
    - 1mm steel: ~7.8 kg/m²
    - Vinyl sheet: ~3-5 kg/m²
    """
    freqs = utils.frequency_axis(20, 20000, 12)

    f0 = membrane.panel_absorber_resonance(mass_per_area_kg_m2, air_gap_mm / 1000.0)

    matrices = [
        membrane.membrane_matrix(freqs, mass_per_area_kg_m2),
        air.air_gap_matrix(freqs, air_gap_mm / 1000.0),
    ]
    alpha = tmm.absorption_from_layers(freqs, matrices)
    result = _make_absorption_result(freqs, alpha)
    result.peak_frequency_hz = round(f0, 1)  # override with analytical resonance
    return result


@mcp.tool()
def calculate_helmholtz(
    neck_length_mm: Annotated[float, Field(description="Neck length in mm")],
    neck_radius_mm: Annotated[float, Field(description="Neck radius in mm")],
    cavity_depth_mm: Annotated[float, Field(description="Cavity depth in mm")],
    cavity_width_mm: Annotated[float, Field(description="Cavity width in mm (assuming square cross-section)")],
) -> HelmholtzResult:
    """Calculate resonance frequency, impedance, and absorption area of a Helmholtz resonator.

    Models a single Helmholtz resonator with a cylindrical neck and rectangular cavity.
    Returns the resonance frequency, complex impedance curve, and absorption area
    as a function of frequency.
    """
    freqs = utils.frequency_axis(20, 20000, 12)

    neck_l = neck_length_mm / 1000.0
    neck_r = neck_radius_mm / 1000.0
    cav_vol = (cavity_width_mm / 1000.0) ** 2 * (cavity_depth_mm / 1000.0)

    f0 = helmholtz.helmholtz_resonance(neck_l, neck_r, cav_vol)
    Z = helmholtz.helmholtz_impedance(freqs, neck_l, neck_r, cav_vol)
    A = helmholtz.helmholtz_absorption_area(freqs, neck_l, neck_r, cav_vol)

    wavelength_at_f0 = utils.C_0 / f0
    A_max_theoretical = wavelength_at_f0**2 / (2.0 * np.pi)

    peak_idx = int(np.argmax(A))

    return HelmholtzResult(
        resonance_frequency_hz=round(f0, 1),
        frequencies=[round(float(f), 2) for f in freqs],
        impedance_real=[round(float(z), 2) for z in np.real(Z)],
        impedance_imag=[round(float(z), 2) for z in np.imag(Z)],
        absorption_area_m2=[round(float(a), 6) for a in A],
        peak_absorption_area_m2=round(float(A[peak_idx]), 6),
        theoretical_max_area_m2=round(A_max_theoretical, 4),
    )


@mcp.tool()
def calculate_multilayer(
    layers: Annotated[
        list[dict],
        Field(
            description=(
                'List of layer specifications from front (sound side) to back (wall side). '
                'Each layer is a dict with "type" key: '
                '"porous" (sigma, thickness_mm, model), '
                '"air" (thickness_mm), '
                '"perforated" (hole_diameter_mm, hole_spacing_mm, panel_thickness_mm, panel_type), '
                '"membrane" (mass_per_area_kg_m2).'
            )
        ),
    ],
    incidence: Annotated[str, Field(description="normal or diffuse")] = "normal",
) -> AbsorptionResult:
    """Calculate absorption of an arbitrary multi-layer absorber stack.

    Build up complex absorber designs by stacking layers. Layers are ordered
    from the sound-incident side to the rigid wall backing.

    Example: porous absorber + air gap = [
        {"type": "porous", "sigma": 13000, "thickness_mm": 50, "model": "miki"},
        {"type": "air", "thickness_mm": 100}
    ]
    """
    freqs = utils.frequency_axis(20, 20000, 12)
    matrices = []

    for layer_dict in layers:
        layer_type = layer_dict.get("type")

        if layer_type == "porous":
            spec = PorousLayerSpec(**layer_dict)
            model_fn = _get_porous_model(spec.model)
            Zc, kc = model_fn(freqs, spec.sigma)
            matrices.append(tmm.porous_layer_matrix(freqs, Zc, kc, spec.thickness_mm / 1000.0))

        elif layer_type == "air":
            spec = AirLayerSpec(**layer_dict)
            matrices.append(air.air_gap_matrix(freqs, spec.thickness_mm / 1000.0))

        elif layer_type == "perforated":
            spec = PerforatedLayerSpec(**layer_dict)
            Z = _build_perforated_impedance(freqs, spec)
            matrices.append(tmm.impedance_sheet_matrix(freqs, Z))

        elif layer_type == "membrane":
            spec = MembraneLayerSpec(**layer_dict)
            matrices.append(membrane.membrane_matrix(freqs, spec.mass_per_area_kg_m2))

        else:
            raise ValueError(f"Unknown layer type '{layer_type}'. Use: porous, air, perforated, membrane")

    if not matrices:
        raise ValueError("At least one layer is required")

    alpha = tmm.absorption_from_layers(freqs, matrices)
    return _make_absorption_result(freqs, alpha)


@mcp.tool()
def material_properties(
    material_name: Annotated[str, Field(description="Material name or keyword to search (e.g. 'oc703', 'rockwool', 'polyester')")],
) -> list[MaterialInfo]:
    """Look up acoustic properties of common absorber materials.

    Returns flow resistivity, density, and usage notes for materials matching
    the search term. Use this to find the right sigma value for porous absorber
    calculations.
    """
    query = material_name.lower().replace(" ", "").replace("-", "").replace("_", "")
    results = []
    for key, data in porous.MATERIAL_DATABASE.items():
        searchable = (key + data["name"]).lower().replace(" ", "").replace("-", "").replace("_", "")
        if query in searchable:
            results.append(MaterialInfo(
                name=data["name"],
                sigma_range=data["sigma_range"],
                sigma_typical=data["sigma_typical"],
                density_kg_m3=data["density_kg_m3"],
                notes=data["notes"],
            ))
    if not results:
        # Return all materials if no match
        for data in porous.MATERIAL_DATABASE.values():
            results.append(MaterialInfo(
                name=data["name"],
                sigma_range=data["sigma_range"],
                sigma_typical=data["sigma_typical"],
                density_kg_m3=data["density_kg_m3"],
                notes=data["notes"],
            ))
    return results


@mcp.tool()
def list_available_models() -> dict:
    """List all supported acoustic models with their parameters and valid ranges.

    Returns a catalogue of available porous absorber models, perforated panel
    models, and other layer types with their input parameters, valid ranges,
    and literature citations.
    """
    return {
        "porous_models": {
            "delany_bazley": {
                "parameters": ["sigma (N·s/m⁴)"],
                "valid_range": "0.01 < rho_0*f/sigma < 1.0",
                "citation": "Delany & Bazley, Acustica 23 (1970)",
                "notes": "Original empirical model. Simple but may give unphysical results at low frequencies.",
            },
            "miki": {
                "parameters": ["sigma (N·s/m⁴)"],
                "valid_range": "0.01 < rho_0*f/sigma < 1.0",
                "citation": "Miki, JASE 11(1) (1990)",
                "notes": "Improved D-B model. Better low-frequency behaviour. Recommended default.",
            },
            "allard_champoux": {
                "parameters": ["sigma (N·s/m⁴)"],
                "valid_range": "0.01 < rho_0*f/sigma < 1.0",
                "citation": "Allard & Champoux, JASA 91(6) (1992)",
                "notes": "Separates viscous and thermal effects. Good general-purpose model.",
            },
            "jca": {
                "parameters": [
                    "sigma (N·s/m⁴)",
                    "porosity (0-1)",
                    "tortuosity (>=1)",
                    "viscous_length (m)",
                    "thermal_length (m)",
                ],
                "citation": "Johnson et al., JASA 87(1) (1987) + Champoux & Allard, JASA 89(2) (1991)",
                "notes": "Five-parameter microstructure model. Most accurate but requires detailed material data.",
            },
        },
        "perforated_models": {
            "perforated (Ingard)": {
                "parameters": ["hole_diameter_mm", "hole_spacing_mm", "panel_thickness_mm"],
                "valid_range": "hole diameter > 1 mm",
                "citation": "Ingard, JASA 25(6) (1953)",
            },
            "slotted (Kristiansen)": {
                "parameters": ["slot_width_mm", "slot_spacing_mm", "panel_thickness_mm"],
                "valid_range": "any slot width",
                "citation": "Kristiansen & Vigran, Applied Acoustics 43 (1994)",
            },
            "mpp (Maa)": {
                "parameters": ["hole_diameter_mm", "hole_spacing_mm", "panel_thickness_mm"],
                "valid_range": "hole diameter < 1 mm",
                "citation": "Maa, JASA 104(5) (1998)",
            },
        },
        "other_layers": {
            "membrane": {
                "parameters": ["mass_per_area_kg_m2"],
                "citation": "Kuttruff (2009), Room Acoustics, Ch. 6.4",
            },
            "helmholtz": {
                "parameters": ["neck_length_mm", "neck_radius_mm", "cavity_depth_mm", "cavity_width_mm"],
                "citation": "Ingard, JASA 25(6) (1953); Kinsler et al. (2000), Ch. 9",
            },
            "air_gap": {
                "parameters": ["thickness_mm"],
                "citation": "Allard & Atalla (2009), eq. 11.1",
            },
        },
    }


@mcp.tool()
def optimize_absorber(
    target_hz: Annotated[float, Field(description="Target frequency to absorb (Hz)")],
    max_depth_mm: Annotated[float, Field(description="Maximum total depth budget (mm)")],
    material_options: Annotated[
        list[str] | None,
        Field(description="Material keys to consider (e.g. ['oc703_fiberglass', 'rockwool_60']). None = try all."),
    ] = None,
    optimize_for: Annotated[str, Field(description="'frequency' to maximize alpha at target_hz, or 'broadband' to maximize NRC/SAA")] = "frequency",
    room_dims_m: Annotated[
        list[float] | None,
        Field(description="Optional room dimensions [length, width, height] in metres for mode analysis"),
    ] = None,
) -> dict:
    """Optimize an absorber design for a target frequency or broadband performance.

    Searches across materials and layer configurations to find the best design
    within the depth budget. Returns top 3 candidates with full absorption curves.

    Available materials: oc703_fiberglass, oc705_fiberglass, rockwool_60,
    thinsulate_sm600l, polyester_batting_soft, rpet_felt_soft,
    basotect_melamine, recycled_cotton_batt.
    """
    result: dict = {}

    # Room mode analysis if dimensions provided
    if room_dims_m and len(room_dims_m) == 3:
        modes = optimizer.room_mode_frequencies(room_dims_m[0], room_dims_m[1], room_dims_m[2])
        # Filter to modes near the target frequency
        nearby = [m for m in modes if abs(m["frequency_hz"] - target_hz) < target_hz * 0.3]
        result["room_modes_near_target"] = nearby[:10]

    # Design classification
    result["design_guidance"] = optimizer.classify_design_approach(target_hz, max_depth_mm)

    # Run optimizer
    if optimize_for == "broadband":
        candidates = optimizer.optimize_nrc(max_depth_mm, material_options)
    else:
        candidates = optimizer.optimize_for_frequency(target_hz, max_depth_mm, material_options)

    result["candidates"] = []
    for c in candidates:
        result["candidates"].append({
            "material": c.material,
            "sigma": c.sigma,
            "thickness_mm": c.thickness_mm,
            "air_gap_mm": c.air_gap_mm,
            "total_depth_mm": round(c.thickness_mm + c.air_gap_mm, 1),
            "nrc": c.nrc,
            "saa": c.saa,
            "peak_frequency_hz": c.peak_freq_hz,
            "peak_alpha": c.peak_alpha,
            "octave_summary": utils.octave_band_summary(c.alpha, c.freqs),
        })

    return result


@mcp.tool()
def room_modes(
    length_m: Annotated[float, Field(description="Room length in metres")],
    width_m: Annotated[float, Field(description="Room width in metres")],
    height_m: Annotated[float, Field(description="Room height in metres")],
    max_order: Annotated[int, Field(description="Maximum mode order")] = 3,
) -> dict:
    """Calculate room mode frequencies for a rectangular room.

    Returns axial, tangential, and oblique modes up to the specified order.
    Useful for identifying problematic resonances that need treatment.
    """
    modes = optimizer.room_mode_frequencies(length_m, width_m, height_m, max_order)

    # Convert tuples to lists for JSON serialization
    for m in modes:
        m["mode"] = list(m["mode"])

    # Summary
    axial = [m for m in modes if m["type"] == "axial"]
    tangential = [m for m in modes if m["type"] == "tangential"]
    oblique = [m for m in modes if m["type"] == "oblique"]

    return {
        "modes": modes,
        "summary": {
            "total_modes": len(modes),
            "axial_modes": len(axial),
            "tangential_modes": len(tangential),
            "oblique_modes": len(oblique),
            "lowest_mode_hz": modes[0]["frequency_hz"] if modes else None,
            # Schroeder frequency: f_s = 2000 * sqrt(T60 / V)
            # Using T60 = 0.5 s as a typical untreated room assumption
            "schroeder_frequency_hz": round(
                2000 * np.sqrt(0.5 / (length_m * width_m * height_m)),
                1,
            ) if length_m and width_m and height_m else None,
            "schroeder_t60_assumption_s": 0.5,
        },
    }


def main():
    mcp.run()


if __name__ == "__main__":
    main()
