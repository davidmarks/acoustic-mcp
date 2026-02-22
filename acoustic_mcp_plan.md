# Acoustic Absorber MCP Server — Build Plan

## Project Structure

```
acoustic-mcp/
├── server.py                  # MCP server entry point
├── acoustic/
│   ├── __init__.py
│   ├── models/
│   │   ├── porous.py          # D-B, Miki, JCA, Allard-Champoux
│   │   ├── perforated.py      # Perforated + slotted panels (Ingard, Allard, Maa MPP)
│   │   ├── membrane.py        # Limp membrane / panel absorber
│   │   ├── helmholtz.py       # Helmholtz resonator (Ingard, TU Berlin)
│   │   └── air.py             # Air gap layer
│   ├── tmm.py                 # Transfer Matrix Method engine
│   ├── diffuse.py             # Diffuse field / random incidence integration
│   ├── optimizer.py           # Optimization layer
│   └── utils.py               # Frequency axes, NRC/SAA, unit conversions
├── tests/
│   ├── test_tmm.py            # Validate against acousticmodelling.com reference values
│   ├── test_porous.py
│   └── test_helmholtz.py
├── pyproject.toml
└── README.md
```

---

## Libraries

```toml
[dependencies]
mcp = ">=1.0"                  # Anthropic MCP SDK (pip: mcp[cli])
numpy = ">=1.26"               # Core math
scipy = ">=1.12"               # optimize.minimize, signal processing
acoustipy = ">=0.1"            # TMM engine baseline, D-B/Miki/JCA layers
plotly = ">=5.0"               # Frequency response charts (returned as base64 PNG)
pydantic = ">=2.0"             # Input validation for MCP tool schemas
```

`acoustipy` is used as a validated TMM backbone. Custom layer models (membrane, slotted panel,
Helmholtz) are added on top. Do not use `python-acoustics` — it lacks TMM support.

---

## Phase 1 — TMM Engine (`acoustic/tmm.py`)

### Task 1.1 — Core TMM matrix operations

- Implement `build_layer_matrix(layer) -> np.ndarray (2x2, complex)` for each layer type
- Implement `multiply_chain(matrices) -> np.ndarray` for N-layer stack
- Implement `surface_impedance_from_chain(T, Z0) -> complex array` using rigid-wall termination:
  Z_i = T_11 / T_21
- Implement `alpha_from_impedance(Zi, Z0) -> float array`:
  alpha = 1 - |R|^2,  R = (Z_i - Z_0) / (Z_i + Z_0)
- **Source:** Cox & D'Antonio (2009) *Acoustic Absorbers and Diffusers*, Ch. 2;
  Allard & Atalla (2009) *Propagation of Sound in Porous Media*, Ch. 11

### Task 1.2 — Diffuse field integration (`acoustic/diffuse.py`)

- Integrate normal-incidence alpha over angles 0°–78° using Paris formula:
  alpha_diff = 2 * integral_0^(pi/2) [ alpha(theta) * sin(theta) * cos(theta) ] dtheta
- Use 10-point Gaussian quadrature (`scipy.integrate.fixed_quad`)
- **Source:** ISO 354:2003; Kuttruff (2009) *Room Acoustics*, Ch. 4

### Task 1.3 — Standard metrics (`acoustic/utils.py`)

- `nrc(alpha_array, freqs)` — average of alpha at 250, 500, 1000, 2000 Hz per ASTM C423
- `saa(alpha_array, freqs)` — average of 12 third-octave bands 200–2500 Hz per ASTM C423-09a
- `octave_band_summary(alpha_array, freqs)` — return dict of 63, 125, 250, 500, 1k, 2k, 4k Hz values

---

## Phase 2 — Layer Models

### Task 2.1 — Porous absorber models (`acoustic/models/porous.py`)

Implement all four models selectable by name. Each returns a `(Zc, kc)` tuple.

| Model | Parameters | Source |
|---|---|---|
| `delany_bazley(f, sigma)` | flow resistivity σ [N·s/m⁴] | Delany & Bazley, *Acustica* 23 (1970) |
| `miki(f, sigma)` | flow resistivity σ | Miki, *JASE* 11(1) (1990) |
| `allard_champoux(f, sigma)` | flow resistivity σ | Allard & Champoux, *JASA* 91(6) (1992) |
| `jca(f, sigma, phi, alpha_inf, Lambda, Lambda_prime)` | 5 microstructure params | Johnson et al. (1987) + Champoux & Allard (1991) |

**Implementation notes:**
- Validate D-B/Miki against acousticmodelling.com output for known reference cases
  (OC703 50mm → expected alpha ≈ 0.70 at 500 Hz)
- Validate X = f/sigma unit convention by calibration against reference data — test all three
  interpretations (X = f/sigma, X = rho_0*f/sigma, X = f/(sigma/10)) and lock in the one
  that reproduces known results. Treat as a Phase 1 blocker before proceeding.
- All models must clip alpha to [0, 1] and flag frequencies outside valid X range

### Task 2.2 — Air gap layer (`acoustic/models/air.py`)

- `air_gap_matrix(f, d)` — transfer matrix for a lossless air layer of thickness d [m]:

```
T = | cos(k0*d)          j*Z0*sin(k0*d) |
    | j*sin(k0*d)/Z0     cos(k0*d)      |
```

- **Source:** Allard & Atalla (2009), eq. 11.1

### Task 2.3 — Perforated and slotted panels (`acoustic/models/perforated.py`)

Three sub-models, each returning complex acoustic impedance Z [Pa·s/m]:

| Function | Use case | Hole size | Source |
|---|---|---|---|
| `perforated_ingard(f, t, d_hole, spacing)` | Macro-perforated panel | > 1 mm | Ingard, *JASA* 25(6) (1953) |
| `slotted_kristiansen(f, t, w_slot, spacing)` | Rectangular slot panel | any | Kristiansen & Vigran, *Applied Acoustics* 43 (1994) |
| `mpp_maa(f, t, d_hole, porosity)` | Micro-perforated panel | < 1 mm | Maa, *JASA* 104(5) (1998) |

Each is inserted into the TMM chain as a thin impedance sheet layer (zero-thickness matrix with
off-diagonal Z term).

### Task 2.4 — Limp membrane / panel absorber (`acoustic/models/membrane.py`)

- `membrane_matrix(f, mass_per_area)` — mass-law TMM layer:
  Z_mem = j * omega * m,  where m = surface mass density [kg/m²]
- `panel_absorber_resonance(m, d_air)` — convenience function returning resonance frequency:
  f_0 = (c_0 / 2*pi) * sqrt(rho_0 / (m * d_air))
- **Source:** Kuttruff (2009) *Room Acoustics*, Ch. 6.4; Cox & D'Antonio (2009), Ch. 4

### Task 2.5 — Helmholtz resonator (`acoustic/models/helmholtz.py`)

- `helmholtz_resonance(neck_length, neck_radius, cavity_volume)` — resonance frequency:

  f_0 = (c_0 / 2*pi) * sqrt( A_neck / (V_cavity * (L_neck + delta)) )

  where delta = 0.85 * 2r  (Ingard flanged-opening end correction)

- `helmholtz_impedance(f, neck_length, neck_radius, cavity_volume, viscous_loss=True)`
  — full complex Z(f) including resistive neck losses

- `helmholtz_absorption_area(f, ...)` — A(f) [m²];
  theoretical maximum at resonance: A_max = lambda^2 / (2*pi)

- `neck_loss_factor(f, r)` — viscous + radiation resistance term in neck

- **Source:** Ingard, *JASA* 25(6) (1953); Kinsler et al. *Fundamentals of Acoustics* (2000), Ch. 9;
  TU Berlin Helmholtz Resonator Calculator (2025)

---

## Phase 3 — Optimizer (`acoustic/optimizer.py`)

### Task 3.1 — Single-target frequency optimizer

```python
optimize_for_frequency(
    target_hz: float,
    max_depth_mm: float,
    material_options: list[str]
) -> list[LayerStack]  # top 3 candidates
```

- Uses `scipy.optimize.differential_evolution` over layer thicknesses and sigma values
- Objective: maximize alpha(target_hz) subject to sum(layer thicknesses) <= max_depth_mm
- Returns top 3 candidate designs with full alpha(f) curves

### Task 3.2 — Broadband NRC optimizer

```python
optimize_nrc(
    freq_range: tuple[float, float],
    max_depth_mm: float,
    material_options: list[str]
) -> LayerStack
```

- Objective: maximize NRC or SAA within depth constraint
- Penalty term for designs exceeding depth budget

### Task 3.3 — Room mode targeting (`acoustic/optimizer.py`)

```python
room_mode_frequencies(Lx, Ly, Lz, max_order=3) -> list[float]
```

Axial, tangential, and oblique modes via:

  f_mnp = (c_0 / 2) * sqrt( (m/Lx)^2 + (n/Ly)^2 + (p/Lz)^2 )

- Feeds directly into the optimizer: given room dimensions, identify problematic modes,
  suggest absorber designs targeting each
- **Source:** Kuttruff (2009) *Room Acoustics*, Ch. 2.2

### Task 3.4 — Constraint-aware design classifier

Given target frequency + depth budget, classify the required approach and return
a human-readable rationale alongside numerical results:

| Frequency range | Depth budget | Recommended approach |
|---|---|---|
| > 500 Hz | any | Porous absorber sufficient |
| 150–500 Hz | ≥ 100 mm | Porous absorber + air gap |
| 80–250 Hz | < 150 mm | Helmholtz resonator or MPP + cavity |
| < 80 Hz | any | Panel/membrane absorber or large Helmholtz |

---

## Phase 4 — MCP Server (`server.py`)

All tools accept Pydantic-validated input schemas and return structured JSON.
Responses always include: `frequencies`, `alpha`, `nrc`, `peak_frequency_hz`,
and optionally `chart_base64` (PNG of the alpha(f) curve).

### Task 4.1 — Single layer tools

```
calculate_porous_layer(
    sigma: float,              # flow resistivity [N·s/m⁴]
    thickness_mm: float,
    model: str,                # "delany_bazley" | "miki" | "allard_champoux" | "jca"
    air_gap_mm: float = 0,
    incidence: str = "normal"  # "normal" | "diffuse"
)

calculate_perforated_panel(
    hole_diameter_mm: float,
    hole_spacing_mm: float,
    panel_thickness_mm: float,
    air_gap_mm: float,
    panel_type: str            # "perforated" | "slotted" | "mpp"
)

calculate_membrane_absorber(
    mass_per_area_kg_m2: float,
    air_gap_mm: float
)

calculate_helmholtz(
    neck_length_mm: float,
    neck_radius_mm: float,
    cavity_depth_mm: float,
    cavity_area_m2: float
)
```

### Task 4.2 — Multi-layer tool

```
calculate_multilayer(
    layers: list[LayerSpec],   # discriminated union — see below
    incidence: str = "normal"
)
```

`LayerSpec` is a Pydantic discriminated union:

```python
class PorousLayer(BaseModel):
    type: Literal["porous"]
    sigma: float
    thickness_mm: float
    model: str = "miki"

class AirLayer(BaseModel):
    type: Literal["air"]
    thickness_mm: float

class PerforatedLayer(BaseModel):
    type: Literal["perforated"]
    hole_diameter_mm: float
    hole_spacing_mm: float
    panel_thickness_mm: float
    panel_type: str = "perforated"

class MembraneLayer(BaseModel):
    type: Literal["membrane"]
    mass_per_area_kg_m2: float

LayerSpec = PorousLayer | AirLayer | PerforatedLayer | MembraneLayer
```

**Returns:** alpha at ISO 1/3-octave bands, NRC, SAA, total stack depth, peak absorption
frequency, chart PNG (base64).

### Task 4.3 — Optimization tools

```
optimize_absorber(
    target_hz: float,
    max_depth_mm: float,
    room_dims_m: list[float] | None,   # optional [Lx, Ly, Lz] for mode analysis
    available_materials: list[str]
)

suggest_design(
    problem_description: str           # natural language → structured optimizer call
)
```

`suggest_design` parses natural language inputs (e.g. "I need to treat a 26 Hz room
mode with less than 75mm of panel depth") into structured optimizer parameters and
returns both the design rationale and numerical results.

### Task 4.4 — Reference and lookup tools

```
material_properties(material_name: str)
# Returns: sigma, density, typical thickness range, notes
# Covers: OC703, OC705, Rockwool, Thinsulate SM600L, rPET felt (soft/rigid),
#         Basotect, polyester batting, recycled cotton batt

list_available_models()
# Returns: supported porous models, perforated models, their valid parameter ranges,
#          and citation

absorption_physics_explanation(device_type: str)
# Returns: text explanation suitable for LLM context injection
# device_type: "porous" | "helmholtz" | "mpp" | "membrane" | "air_gap" | "multilayer"
```

---

## Phase 5 — Validation

### Task 5.1 — Cross-validate porous models against acousticmodelling.com

Run identical inputs through the local implementation and the web calculator.
Target reference cases:

| Material | Thickness | Air gap | Expected alpha at 500 Hz |
|---|---|---|---|
| OC703 fiberglass | 50 mm | 0 | ~0.70 |
| OC703 fiberglass | 50 mm | 100 mm | ~0.95 |
| Rockwool 60 kg/m³ | 100 mm | 0 | ~0.90 |
| Soft polyester | 25 mm | 75 mm | ~0.50 |

Lock in D-B unit convention at this step. Do not proceed to Phase 3 until calibrated.

### Task 5.2 — Validate Helmholtz model

- Verify resonance frequency formula against analytical result for known geometry
- Verify absorption area maximum A_max = lambda^2 / (2*pi) at resonance
- Cross-check with Kinsler et al. worked examples

### Task 5.3 — Validate optimizer

- OC703 2" + 4" air gap → peak absorption expected near 500 Hz
- Panel absorber (3mm plywood, 100mm cavity) → resonance expected near 80–100 Hz
- Helmholtz (25mm neck, 10mm radius, 200mm cavity) → compute expected f_0 and verify

---

## Key Implementation Notes

- **D-B unit convention is a Phase 1 blocker.** Resolve before any other porous model work.
  Test all three interpretations and validate against acousticmodelling.com reference outputs.
- **MCP return format:** Always return structured JSON with `frequencies`, `alpha`, `nrc`,
  `peak_frequency`, and optionally `chart_base64`. The LLM should narrate results without
  performing its own arithmetic.
- **Tool granularity:** Keep single-layer tools separate from the multi-layer tool to allow
  the LLM to build up designs incrementally across multiple tool calls.
- **No web scraping of acousticmodelling.com.** Reimplement from published sources only.
  The complete source list is: Cox & D'Antonio (2009), Allard & Atalla (2009),
  Mechel (2002), Ingard (1953), Maa (1998), Kristiansen & Vigran (1994), Kuttruff (2009).
- **Chart output:** Use Plotly to generate frequency response PNGs. Return as base64-encoded
  strings in the JSON response so the LLM host can render them inline.
- **Flow resistivity reference table** (include in `material_properties` tool):

| Material | sigma [N·s/m⁴] | Density [kg/m³] |
|---|---|---|
| Thinsulate SM600L | 3,000–5,000 | ~16 |
| Soft polyester batting | 1,000–3,000 | 10–30 |
| rPET felt, soft grade | 5,000–12,000 | 80–120 |
| rPET rigid board | 50,000–150,000 | 150–250 |
| OC703 fiberglass | 10,000–16,000 | 48 |
| OC705 fiberglass | 20,000–32,000 | 80 |
| Rockwool 60 kg/m³ | 8,000–14,000 | 60 |
| Basotect melamine foam | 3,000–8,000 | 9–11 |
| Recycled cotton batt | 2,000–6,000 | 20–40 |
