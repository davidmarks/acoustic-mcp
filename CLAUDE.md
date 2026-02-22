# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Acoustic room treatment design toolkit with two components:

1. **Acoustic Absorber MCP Server** (`acoustic-mcp/`) — Python library and MCP server for acoustic absorber design, simulation, and optimization using the Transfer Matrix Method. 10 MCP tools for calculating absorption of porous, perforated, membrane, and Helmholtz absorbers, plus an optimizer and room mode calculator.

2. **Metadiffuser Tile** (root-level files) — A 3D-printable deep-subwavelength acoustic diffuser (160x160x25mm) using Helmholtz resonator arrays, targeting 250-2000 Hz. Based on Jiménez et al. (2017). The OpenSCAD design and STL are complete. This serves as prior art for the long-term goal of designing treatments for fabrication.

## Build & Run Commands

### MCP Server
```bash
cd acoustic-mcp
TMPDIR=/tmp/claude-1000 UV_CACHE_DIR=/tmp/claude-1000/uv-cache uv sync   # install deps
TMPDIR=/tmp/claude-1000 UV_CACHE_DIR=/tmp/claude-1000/uv-cache uv run acoustic-mcp  # start server
```

### Tests
```bash
cd acoustic-mcp
TMPDIR=/tmp/claude-1000 UV_CACHE_DIR=/tmp/claude-1000/uv-cache uv run --with pytest pytest tests/ -v
```

### STL Generation (OpenSCAD)
```bash
./build.sh                    # Generates metadiffuser_tile.stl (headless, Wayland-safe)
```

## Architecture — MCP Server

```
acoustic-mcp/
├── pyproject.toml
├── acoustic/
│   ├── server.py          # FastMCP server entry point — all 10 tool definitions + Pydantic schemas
│   ├── tmm.py             # Transfer Matrix Method engine: matrix chain, surface impedance, α(f)
│   ├── diffuse.py         # Diffuse field integration (Paris formula, Gaussian quadrature)
│   ├── optimizer.py       # scipy differential_evolution optimizer + room mode calculator
│   ├── utils.py           # Air constants, NRC/SAA metrics, frequency axes, material database
│   └── models/
│       ├── porous.py      # 4 models: Delany-Bazley, Miki, Allard-Champoux, JCA + material database
│       ├── perforated.py  # 3 models: Ingard macro-perforated, Kristiansen slotted, Maa MPP
│       ├── membrane.py    # Limp membrane mass-law layer + panel absorber resonance
│       ├── helmholtz.py   # Helmholtz resonator: resonance, impedance, absorption area
│       └── air.py         # Lossless air gap transfer matrix
└── tests/
    ├── test_tmm.py        # TMM engine, utils, and integration tests (porous + air gap)
    ├── test_porous.py     # Porous model properties and material database
    └── test_helmholtz.py  # Helmholtz, membrane, and perforated model tests
```

### Core computation flow
Layer models produce `(Zc, kc)` characteristic impedance/wavenumber → `tmm.py` builds per-layer 2×2 transfer matrices → `multiply_chain()` chains them → `surface_impedance()` with rigid-wall termination → `absorption_coefficient()` via `α = 1 - |R|²` → NRC/SAA metrics via `utils.py`.

Perforated/membrane layers use `impedance_sheet_matrix()` (zero-thickness, off-diagonal Z term) instead of `porous_layer_matrix()`.

### MCP Tools (10 total)
- `ping` — health check
- `calculate_porous_layer` — single porous absorber + optional air gap
- `calculate_perforated_panel` — perforated/slotted/MPP + air cavity
- `calculate_membrane_absorber` — membrane/panel + air cavity
- `calculate_helmholtz` — Helmholtz resonator from geometry
- `calculate_multilayer` — arbitrary layer stack (discriminated union of layer specs)
- `material_properties` — flow resistivity lookup for 9 common materials
- `list_available_models` — model catalogue with citations and valid ranges
- `optimize_absorber` — optimize design for target frequency or broadband NRC
- `room_modes` — rectangular room mode frequencies

### Key physics notes
- Porous models use `X = ρ₀f/σ` dimensionless parameter (MKS convention). D-B/Miki coefficients produce normal-incidence α ≈ 0.50 at 500 Hz for 50mm OC703 (σ=13000), consistent with impedance tube data.
- Perforated/slotted panels are inserted as thin impedance sheet layers.
- Diffuse field: Paris formula integration 0°–78°, 10-point Gaussian quadrature.
- No web scraping of acousticmodelling.com — all models reimplemented from published sources.
- Surface impedance handles T[1,0]=0 edge case (rigid wall) by substituting very large impedance.

## Key References
- Cox & D'Antonio (2009) — *Acoustic Absorbers and Diffusers*
- Allard & Atalla (2009) — *Propagation of Sound in Porous Media*
- Kuttruff (2009) — *Room Acoustics*
- Kinsler et al. (2000) — *Fundamentals of Acoustics*
- Jiménez et al. (2017) — Original metadiffuser paper

## Platform Notes
- Fedora Linux with Wayland — OpenSCAD GUI crashes; use headless mode or `QT_QPA_PLATFORM=xcb openscad`
- Python 3.10+ / uv package manager
- Sandbox tmp dirs: use `TMPDIR=/tmp/claude-1000 UV_CACHE_DIR=/tmp/claude-1000/uv-cache` prefix for uv commands
