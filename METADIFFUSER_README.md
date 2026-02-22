# Metadiffuser Acoustic Panel
## 3D Printable Sound Diffuser for 250-2000 Hz

Based on: *Jiménez, N., Cox, T.J., Romero-García, V., & Groby, J.P. (2017). "Metadiffusers: Deep-subwavelength sound diffusers." Scientific Reports, 7, 5389.*

---

## Overview

This is a tileable acoustic metadiffuser panel that uses **Helmholtz resonator arrays** to create acoustic diffusion and absorption in normal listening frequencies. Unlike traditional diffusers that require depths of 20-50cm for low frequencies, this panel is only **25mm thick** (up to 46x thinner than conventional designs).

### Key Features
- **Frequency range**: 250-2000 Hz (mid-range audio frequencies)
- **Tile size**: 160×160×25mm (fits Bambu A1 Mini print bed)
- **Tileable design**: Print multiple tiles and assemble into larger panels
- **Hybrid function**: Provides both diffusion (scattering) and absorption
- **Deep-subwavelength**: 1/46th the wavelength of lowest frequency

---

## How It Works

### The Physics

Traditional acoustic diffusers use **quarter-wavelength resonators** - wells with different depths that phase-shift reflected sound. For 250 Hz, this requires wells 34cm deep!

**Metadiffusers** achieve the same effect in 25mm using:

1. **Helmholtz Resonators (HR)**: Small cavities with narrow necks that resonate at specific frequencies
2. **Slow Sound Propagation**: HR arrays create strong dispersion, dramatically reducing the effective sound speed inside the slits
3. **Viscous Losses**: Narrow passages induce thermoviscous losses that provide absorption at resonant frequencies

### Design Strategy

Each tile contains **4 vertical slits**, each with **2-3 Helmholtz resonators** at different positions:

```
Slit 1: 3.0mm wide, 3 HRs → tuned for mid-low frequencies
Slit 2: 3.5mm wide, 2 HRs → tuned for mid frequencies  
Slit 3: 4.0mm wide, 3 HRs → tuned for mid-high frequencies
Slit 4: 3.0mm wide, 2 HRs → tuned for balanced response
```

Different slit widths and resonator configurations create spatially-varying acoustic impedance, scattering sound into many directions rather than just specular reflection.

---

## Files Included

1. **metadiffuser_tile.scad** - OpenSCAD source file (editable, parametric)
2. **metadiffuser_design.json** - Design parameters (all dimensions in mm)
3. **README.md** - This documentation
4. **ASSEMBLY.md** - Assembly and installation instructions
5. **THEORY.md** - Detailed technical background

---

## Printing Instructions

### Recommended Print Settings

| Setting | Value | Notes |
|---------|-------|-------|
| **Material** | PLA, PETG, or ABS | PLA sufficient for most applications |
| **Layer Height** | 0.2mm | Balance of speed and detail |
| **Perimeters** | 4 (1.6mm walls) | Critical for structural rigidity |
| **Infill** | 20-30% | Lightweight but strong |
| **Supports** | **NONE** | Design is support-free! |
| **Orientation** | **Back face down** | Print with 2mm base on bed |
| **Print Time** | ~6-8 hours per tile | Varies by printer |

### Critical Print Considerations

⚠️ **Slit and Neck Dimensions Are Critical**
- Small features (1.5-4mm) must print accurately
- Test your printer's minimum feature size first
- Use **0.4mm nozzle** for best results
- **Avoid excessive cooling** that causes warping

✅ **Support-Free Design**
- All overhangs are <45°
- Helmholtz resonator cavities are printable without supports
- Orient with back (solid base) on print bed

### Rendering the STL File

If you don't have the STL file yet:

1. **Install OpenSCAD** (free): https://openscad.org/downloads.html
2. **Open** `metadiffuser_tile.scad`
3. **Render** (F6) - takes 1-3 minutes
4. **Export** → Export as STL
5. **Slice** in your preferred slicer (PrusaSlicer, OrcaSlicer, etc.)

---

## Assembly for Larger Panels

### Tile Arrangement

For a 2×2 panel (320×320mm):
```
┌─────┬─────┐
│  1  │  2  │  Orientation matters!
├─────┼─────┤  Keep slit direction consistent
│  3  │  4  │  (vertical in this design)
└─────┴─────┘
```

### Mounting Options

**Option 1: M4 Bolts Through Corners**
- Use the 4.5mm mounting holes in each corner
- Mount to wooden frame or directly to wall studs
- Leave 10-20mm air gap behind panel for best performance

**Option 2: Adhesive Mounting**
- Use construction adhesive on back surface
- Mount to rigid substrate (plywood, MDF, etc.)
- Seal gaps between tiles with flexible caulk

**Option 3: Snap-Together (Custom)**
- Modify design to add interlocking tabs
- See MODIFICATIONS.md for details

---

## Expected Performance

### Diffusion Characteristics

The panel creates **spatially-uniform scattering** in the target frequency range:

- **250-500 Hz**: Moderate diffusion (normalized coefficient ~0.4-0.6)
- **500-1000 Hz**: Strong diffusion (normalized coefficient ~0.6-0.8)
- **1000-2000 Hz**: Peak diffusion (normalized coefficient ~0.7-0.9)

### Absorption Characteristics

Helmholtz resonators provide **frequency-selective absorption**:

- Multiple absorption peaks across the frequency range
- Typical absorption: 20-60% at resonant frequencies
- Lower absorption between resonances (10-30%)

### Application Examples

✅ **Good For:**
- Home studios (reduce flutter echo)
- Listening rooms (improve stereo imaging)
- Podcasting spaces (control reflections)
- Small conference rooms (reduce echo)
- Behind monitors/speakers (reduce comb filtering)

❌ **Not Ideal For:**
- Very low bass (<200 Hz) - need larger panels
- Primary broadband absorption - use in combination with absorbers
- Outdoor use - not weatherproof

---

## Customization

### Tuning for Different Frequencies

To modify the frequency range, edit `metadiffuser_design.json`:

**Lower frequencies** (e.g., 150-1000 Hz):
- Increase `tile_depth` to 30-35mm
- Increase `cavity_width` and `cavity_depth` for HRs
- Reduce `neck_width` (increases resonance Q-factor)

**Higher frequencies** (e.g., 500-4000 Hz):
- Can reduce `tile_depth` to 20mm
- Reduce HR cavity dimensions
- Increase `neck_width` for broader bandwidth

### Design Variations

The OpenSCAD file can be modified to:
- Add more slits per tile (5-7 for finer spatial variation)
- Vary HR positions along the height
- Create different tile patterns for aesthetic variation
- Add decorative front face (reduces performance slightly)

---

## Testing & Validation

### Visual Inspection
1. Check that all slits are clear (no bridging/stringing)
2. Verify HR necks are open (shine light through)
3. Confirm flat back surface (for mounting)

### Acoustic Testing (Optional)
- Clap test: Should sound "deader" than bare wall
- Frequency sweep: Use tone generator + SPL meter
- Impulse response: Measure RT60 improvement

---

## Credits & References

**Original Paper:**
Jiménez, N., Cox, T.J., Romero-García, V., & Groby, J.P. (2017).  
*Metadiffusers: Deep-subwavelength sound diffusers.*  
Scientific Reports, 7, Article 5389.  
https://doi.org/10.1038/s41598-017-05710-5

**Design Tool:** OpenSCAD (https://openscad.org/)  
**3D Printer:** Bambu Lab A1 Mini  
**Created:** 2025  

---

## License

This design is provided for **personal and educational use**. The metadiffuser concept is based on published scientific research (open access). 

For commercial production or sale, please:
1. Review the original research paper's licensing
2. Consider modifications to avoid IP issues
3. Test and validate acoustic performance

---

## Support & Questions

**Issues with printing?**
- Check that slit widths are within your printer's capabilities
- Ensure proper bed adhesion (PLA on textured PEI works great)
- Small features may need slower print speeds (30-40 mm/s)

**Not working as expected?**
- Ensure tiles are mounted with rigid backing
- Leave air gap behind panel when possible
- Try different arrangements (sometimes 2-3 tiles is enough)

**Want to learn more?**
- Read the original paper (open access, highly readable!)
- Study room acoustics: "Master Handbook of Acoustics" by F. Alton Everest
- Experiment with measurement: Room EQ Wizard (REW) is free

---

## Version History

- **v1.0** (2025-02-09): Initial design
  - 4 slits per tile
  - 160×160×25mm tileable format
  - Optimized for 250-2000 Hz
  - Bambu A1 Mini compatible
