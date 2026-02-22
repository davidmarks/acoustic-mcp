# acoustic-mcp

An MCP (Model Context Protocol) server for acoustic room treatment design. Calculates absorption coefficients for porous absorbers, perforated panels, membrane absorbers, and Helmholtz resonators using the Transfer Matrix Method (TMM).

Designed to be used with Claude or other LLM clients to interactively design acoustic treatments for studios, listening rooms, and other spaces.

## Tools

| Tool | Description |
|------|-------------|
| `calculate_porous_layer` | Absorption of fibrous/foam absorbers (fiberglass, mineral wool, polyester, melamine) with optional air gap. Models: Delany-Bazley, Miki, Allard-Champoux. |
| `calculate_perforated_panel` | Absorption of perforated, slotted, or micro-perforated panels backed by an air cavity. |
| `calculate_membrane_absorber` | Absorption of membrane/panel absorbers (plywood, MDF, vinyl) backed by an air cavity. |
| `calculate_helmholtz` | Resonance frequency, impedance, and absorption area of a Helmholtz resonator. |
| `calculate_multilayer` | Arbitrary multi-layer absorber stacks — combine porous, air, perforated, and membrane layers. |
| `optimize_absorber` | Optimize absorber design for a target frequency or broadband NRC within a depth budget. |
| `room_modes` | Calculate room mode frequencies and Schroeder frequency for a rectangular room. |
| `material_properties` | Look up flow resistivity and density for 9 common absorber materials. |
| `list_available_models` | Catalogue of all supported acoustic models with parameters, valid ranges, and citations. |

## Quick Start

### Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) package manager

### Install and Run

```bash
cd acoustic-mcp
uv sync
uv run acoustic-mcp
```

### Claude Code Integration

The `.mcp.json` at the project root configures the server for Claude Code:

```json
{
  "mcpServers": {
    "acoustic-mcp": {
      "command": "uv",
      "args": ["--directory", "acoustic-mcp", "run", "acoustic-mcp"]
    }
  }
}
```

### Run Tests

```bash
cd acoustic-mcp
uv run --with pytest pytest tests/ -v
```

## Architecture

```
acoustic-mcp/
├── acoustic/
│   ├── server.py          # FastMCP server — tool definitions and Pydantic schemas
│   ├── tmm.py             # Transfer Matrix Method engine
│   ├── diffuse.py         # Diffuse field integration (Paris formula)
│   ├── optimizer.py       # Absorber optimizer and room mode calculator
│   ├── utils.py           # Air constants, NRC/SAA metrics, frequency axes
│   └── models/
│       ├── porous.py      # Delany-Bazley, Miki, Allard-Champoux, JCA
│       ├── perforated.py  # Ingard, Kristiansen, Maa MPP
│       ├── membrane.py    # Limp membrane / panel absorber
│       ├── helmholtz.py   # Helmholtz resonator
│       └── air.py         # Air gap layer
└── tests/
```

### How It Works

The server uses the **Transfer Matrix Method** to compute absorption coefficients:

1. Each acoustic layer (porous material, air gap, perforated panel, membrane) is represented by a 2x2 complex transfer matrix
2. Layer matrices are multiplied front-to-back to get the total system matrix
3. Surface impedance is extracted assuming a rigid wall backing
4. Absorption coefficient is calculated from the reflection coefficient: `α = 1 - |R|²`
5. Standard metrics (NRC, SAA, octave-band summary) are computed from the absorption curve

## Acoustic Models

### Porous Absorbers

Four empirical/semi-empirical models for fibrous and porous materials. Each takes frequency and flow resistivity (σ) as primary inputs.

| Model | Source | Notes |
|-------|--------|-------|
| Delany-Bazley | Acustica 23 (1970) | Original empirical model |
| Miki | JASE 11(1) (1990) | Improved low-frequency behaviour. Default. |
| Allard-Champoux | JASA 91(6) (1992) | Separates viscous and thermal effects |
| JCA | Johnson (1987) + Champoux-Allard (1991) | 5-parameter microstructure model |

### Perforated Panels

| Model | Source | Use Case |
|-------|--------|----------|
| Ingard | JASA 25(6) (1953) | Macro-perforated panels (holes > 1 mm) |
| Kristiansen-Vigran | Applied Acoustics 43 (1994) | Slotted panels |
| Maa | JASA 104(5) (1998) | Micro-perforated panels (holes < 1 mm) |

### Other Layers

- **Membrane**: Mass-law impedance sheet (Kuttruff 2009)
- **Helmholtz resonator**: Ingard formula with viscous losses (Kinsler et al. 2000)
- **Air gap**: Lossless propagation layer (Allard & Atalla 2009)

## Material Database

| Material | Flow Resistivity (N·s/m⁴) | Density (kg/m³) |
|----------|---------------------------|-----------------|
| OC703 Fiberglass | 10,000–16,000 | 48 |
| OC705 Fiberglass | 20,000–32,000 | 80 |
| Rockwool 60 kg/m³ | 8,000–14,000 | 60 |
| Thinsulate SM600L | 3,000–5,000 | 16 |
| Basotect Melamine | 3,000–8,000 | 10 |
| Soft Polyester Batting | 1,000–3,000 | 20 |
| rPET Felt (Soft) | 5,000–12,000 | 100 |
| rPET Rigid Board | 50,000–150,000 | 200 |
| Recycled Cotton Batt | 2,000–6,000 | 30 |

## Other Project Files

This repository also includes design files for a 3D-printable metadiffuser acoustic panel:

- `metadiffuser_tile.scad` — OpenSCAD parametric design (160x160x25mm tile)
- `METADIFFUSER_README.md` — Metadiffuser design documentation
- `THEORY.md` — Acoustic theory background (Helmholtz resonators, dispersion, TMM)
- `ASSEMBLY.md` — Assembly, mounting, and testing instructions
- `QUICKSTART.md` / `FEDORA_QUICKSTART.md` — Quick start guides
- `build.sh` — STL generation script (headless OpenSCAD)

## References

- Cox, T.J. & D'Antonio, P. (2009). *Acoustic Absorbers and Diffusers*
- Allard, J.F. & Atalla, N. (2009). *Propagation of Sound in Porous Media*
- Kuttruff, H. (2009). *Room Acoustics*
- Kinsler, L.E. et al. (2000). *Fundamentals of Acoustics*
- Jiménez, N. et al. (2017). *Metadiffusers: Deep-subwavelength sound diffusers.* Scientific Reports, 7, 5389.

## License

This project is provided for personal and educational use.
