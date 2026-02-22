# Quick Start Guide
## Get Printing in 5 Minutes!

---

## Step 1: Open in OpenSCAD (2 min)

1. **Download OpenSCAD**: https://openscad.org/downloads.html (Free!)
2. **Open** the file: `metadiffuser_tile.scad`
3. **Preview** (F5): See the model (fast, low detail)
4. **Render** (F6): Generate final geometry (1-3 minutes)

---

## Step 2: Export STL (30 seconds)

1. **File** → **Export** → **Export as STL**
2. Save as: `metadiffuser_tile.stl`
3. File size should be ~2-5 MB

---

## Step 3: Slice (5 minutes)

### Load into Your Slicer
- **PrusaSlicer** / **OrcaSlicer** / **Bambu Studio** / **Cura**

### Essential Settings
```
┌─────────────────────────────────────┐
│ PRINT SETTINGS                      │
├─────────────────────────────────────┤
│ Material:        PLA / PETG / ABS   │
│ Layer Height:    0.2 mm             │
│ Perimeters:      4 (1.6mm walls)    │
│ Top/Bottom:      5 layers           │
│ Infill:          20%                │
│ Supports:        NONE!              │
│ Brim:            Optional (helps)   │
└─────────────────────────────────────┘
```

### Orientation
```
        Print Bed
┌─────────────────────┐
│                     │
│   ┏━━━━━━━━━━━┓    │  ← Solid back DOWN
│   ┃           ┃    │
│   ┃  Model    ┃    │
│   ┃           ┃    │
│   ┗━━━━━━━━━━━┛    │
│                     │
└─────────────────────┘
```

---

## Step 4: Print! (6-8 hours)

**What to Watch:**
- ✅ First layer sticks well
- ✅ No warping (corners flat)
- ✅ Slits printing cleanly
- ✅ No excessive stringing

**Red Flags:**
- ❌ First layer not sticking → adjust Z-offset
- ❌ Warping → add brim, lower fan speed
- ❌ Slits closing up → reduce flow rate 2-5%

---

## Step 5: Quick Check (1 minute)

After print completes:

1. **Shine flashlight through slits** → should see light
2. **Check mounting holes** → M4 bolt should fit loosely
3. **Inspect resonators** → necks should be open

---

## First Installation

### Minimal Setup (Test before committing)

**What You Need:**
- 2-4 printed tiles
- Command strips OR
- Double-sided mounting tape

**Where to Place:**
- Behind desk/monitor
- On wall opposite speakers
- First reflection point (side wall)

**Test:**
- Clap test: should sound less "ringy"
- Music test: notice subtle smoothing

---

## Next Steps

- **Print more tiles** → 4-9 tiles recommended
- **Read ASSEMBLY.md** → proper mounting
- **Read README.md** → full documentation

---

## Troubleshooting

**"Slits are too narrow and closing up"**
→ Reduce flow rate to 95-98%
→ Calibrate e-steps on printer

**"Model won't stick to bed"**
→ Add 5-10mm brim
→ Clean bed with IPA
→ Increase bed temperature 5°C

**"Taking too long"**
→ Reduce infill to 15%
→ Increase layer height to 0.24mm
→ You can also print multiple tiles at once

**"Resonator cavities sagging"**
→ Reduce print temperature 5°C
→ Increase cooling fan
→ Print slower (40-50 mm/s)

---

## Design Summary

```
╔════════════════════════════════════════╗
║  METADIFFUSER TILE SPECIFICATIONS     ║
╠════════════════════════════════════════╣
║  Dimensions:    160 × 160 × 25 mm     ║
║  Weight:        ~180g (PLA)           ║
║  Print Time:    6-8 hours             ║
║  Material:      150-200g filament     ║
║                                        ║
║  Frequency:     250-2000 Hz           ║
║  Function:      Diffusion + Absorption║
║  Slits:         4 per tile            ║
║  Resonators:    10 total (2-3 per)    ║
╚════════════════════════════════════════╝
```

---

## Tile Layout Visualization

```
Top View (Front Face):
┌────────────────────────────────────┐
│  ○                              ○  │  ← Mounting holes
│                                    │
│     ║   ║    ║      ║             │
│     ║   ║    ║      ║             │  ← Slits (different widths)
│     ║   ║    ║      ║             │
│     ║   ║    ║      ║             │
│     ║   ║    ║      ║             │
│                                    │
│  ○                              ○  │
└────────────────────────────────────┘

Side Cross-Section:
┌────────────────────────────────────┐
│                                    │  ← 2mm back
│  ┃┃═╕ ┃═╕ ┃┃═╕  ┃═╕              │  ← Helmholtz
│  ┃┃ ║ ┃ ║ ┃┃ ║  ┃ ║              │     resonators
│  ┃┃ ║ ┃ ║ ┃┃ ║  ┃ ║              │
│  ┃┃ ║ ┃ ║ ┃┃ ║  ┃ ║              │  ← Slits (23mm deep)
│  ┃┃═╝ ┃═╝ ┃┃═╝  ┃═╝              │
└────────────────────────────────────┘
     ↑    ↑    ↑     ↑
   Slit  Slit Slit  Slit
    1     2    3     4
```

---

## Color Recommendations

**Black PLA**: Professional look, hides dust  
**White PLA**: Bright, clean aesthetic  
**Gray PLA**: Neutral, studio standard  
**Wood PLA**: Warm, home décor friendly  

*Color doesn't affect acoustic performance!*

---

## Cost Estimate

- **Filament per tile**: $3-5 USD
- **4-tile panel**: $12-20 USD
- **9-tile panel**: $27-45 USD

Compare to commercial diffuser: $200-500 for similar coverage!

---

## Support

**Having issues?**
1. Re-read the settings above
2. Check ASSEMBLY.md for installation help
3. Check THEORY.md if you want to understand the science

**Want to modify the design?**
- Edit `metadiffuser_design.json`
- Regenerate with `python3 generate_metadiffuser.py`
- Or edit `metadiffuser_tile.scad` directly in OpenSCAD

---

*Now go make some acoustic magic! 🎵*
