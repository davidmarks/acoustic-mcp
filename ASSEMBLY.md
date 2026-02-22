# Assembly & Installation Guide
## Metadiffuser Acoustic Panel System

---

## Part 1: Print Preparation

### Before You Print

1. **Test Print**: Print just one tile first to verify:
   - Dimensional accuracy (measure slit widths with calipers)
   - No warping or elephantfoot
   - HR necks are clear (not closed by overextrusion)

2. **Calculate Your Needs**:
   ```
   Coverage Area = Number of Tiles × 0.0256 m² (160mm × 160mm)
   
   Examples:
   - 4 tiles (2×2) = 0.32×0.32m = 0.10 m²
   - 9 tiles (3×3) = 0.48×0.48m = 0.23 m²
   - 16 tiles (4×4) = 0.64×0.64m = 0.41 m²
   ```

### Print Settings Checklist

- [ ] Filament loaded and dry
- [ ] Bed cleaned and level
- [ ] First layer calibration verified
- [ ] Slicer profile loaded (see README.md)
- [ ] Estimated time acceptable (~6-8 hrs/tile)
- [ ] Material sufficient (typically 150-200g per tile)

---

## Part 2: Post-Processing

### Quality Check Each Tile

1. **Slit Inspection**:
   - Use flashlight to verify slits are through-holes
   - Check for stringing (remove with tweezers)
   - Ensure no sagging on HR cavity ceilings

2. **Hole Clearance**:
   - Test M4 bolts fit through mounting holes
   - Deburr holes if needed (drill bit by hand)

3. **Flatness**:
   - Check back surface with straightedge
   - Front face doesn't need to be perfect

### Optional Finishing

**Structural Improvements:**
- Fill any gaps between slits with epoxy (increases rigidity)
- Sand back surface for better mounting

**Aesthetic (reduces performance ~5-10%):**
- Paint with spray paint (thin coats only!)
- Apply fabric covering (acoustically transparent)
- Clear coat for durability

⚠️ **Do NOT fill or cover the slits or HR openings!**

---

## Part 3: Assembly Strategies

### Option A: Wall-Mounted Grid (Recommended)

**Materials Needed:**
- Tiles (printed)
- M4 × 25mm bolts and washers (4 per tile)
- 20mm spacers or standoffs (4 per tile)
- Wooden backing board (plywood 12-18mm thick)
- Wood screws for mounting board to wall

**Steps:**

1. **Prepare Backing Board**:
   ```
   Board size = (N tiles × 160mm) + (N-1 gaps × 2mm) + margin
   
   For 3×3 grid: 160×3 + 2×4 + 20 = 508mm square
   ```

2. **Mark Tile Positions**:
   - Draw grid on backing board
   - Leave 2mm gap between tiles for alignment tolerance
   - Mark mounting hole positions (10mm from tile corners)

3. **Drill Pilot Holes**:
   - Use 3mm bit for M4 bolts
   - Drill through board thickness

4. **Install Spacers**:
   - Attach 20mm standoffs to backing board
   - Creates air gap for optimal acoustic performance

5. **Mount Tiles**:
   - Place tile over standoffs
   - Insert M4 bolt through tile and spacer
   - Hand-tighten (don't overtighten plastic!)

6. **Wall Installation**:
   - Find studs or use appropriate wall anchors
   - Mount backing board securely
   - Level is important for appearance, not function

### Option B: Frame-Mounted Panel

**For portable acoustic treatment:**

1. **Build Frame**:
   - Use 1×2" lumber or aluminum extrusion
   - Internal dimensions = tile grid size + gaps
   - Add corner braces for rigidity

2. **Attach Backing**:
   - Use 1/4" plywood or hardboard
   - Staple or screw to frame back

3. **Mount Tiles**:
   - Same as Option A (bolts through frame)
   - Or use construction adhesive for permanent bond

4. **Add Hanging Hardware**:
   - D-rings or French cleat
   - Calculate weight: ~200g per tile + frame

### Option C: Direct Adhesive Mount

**Simplest method, permanent installation:**

1. **Surface Preparation**:
   - Clean wall surface (degloss if painted)
   - Mark tile positions with pencil

2. **Apply Adhesive**:
   - Use construction adhesive (PL Premium, Liquid Nails)
   - Apply beads to tile back (avoid center area)
   - Leave slits clear!

3. **Press and Hold**:
   - Align tile to marks
   - Press firmly for 30 seconds
   - Support until adhesive sets (check product instructions)

4. **Gap Filling** (optional):
   - Use flexible caulk between tiles
   - Tool smooth for finished appearance
   - White, gray, or paintable caulk

⚠️ **Removal will damage wall/tiles with this method**

---

## Part 4: Optimal Placement

### Room Acoustics Principles

**Where to Place Diffusers:**

1. **First Reflection Points** (best use):
   - Side walls at listening position
   - Ceiling between speakers and listener
   - Back wall behind listening position

2. **Flutter Echo Zones**:
   - Parallel walls in small rooms
   - Corners (less effective for diffusion but helps)

3. **Behind Speakers**:
   - Reduces rear-wave interference
   - Place 30-60cm behind speaker

### Placement Guide by Room Type

**Home Studio / Critical Listening:**
```
     [Speakers]
        ║ ║
    ╔═══╗ ╔═══╗
    ║ D ║ ║ D ║  D = Diffuser on side walls
    ╚═══╝ ╚═══╝     (first reflection points)
        
        [Listener]
    
    ╔═══════════╗
    ║ Diffuser  ║    Back wall: Diffuser + absorber
    ║  Array    ║    (2×3 or 3×3 grid)
    ╚═══════════╝
```

**Podcast/Voice Recording:**
- Less critical placement
- Use 2-4 tiles to break up parallel walls
- Combine with absorption for vocal clarity

**Living Room / Home Theater:**
- Back wall treatment: 3×2 or 4×2 grid
- Side walls: 2×2 grids at ear height
- Ceiling: optional if flutter echo present

### Height Placement

- **Optimal**: Center panel at ear height (sitting: 100-120cm, standing: 140-160cm)
- **Acceptable**: Anywhere on wall (diffusion works at all heights)
- **Coverage**: More area = better results (aim for 15-30% of wall surface)

---

## Part 5: Testing & Validation

### Subjective Tests

1. **Clap Test**:
   - Clap hands in room before/after
   - Listen for reduction in "slap" echo
   - Should sound less harsh

2. **Music Test**:
   - Play familiar track with good stereo imaging
   - Note improvements in:
     - Stereo width
     - Depth/spaciousness  
     - Reduced harshness
     - Clearer midrange

3. **Voice Test**:
   - Record speech in room
   - Compare before/after
   - Should sound more natural, less boxy

### Objective Measurements (Advanced)

**Equipment Needed:**
- USB measurement microphone (Dayton Audio UMM-6, miniDSP UMIK-1)
- Free software: Room EQ Wizard (REW)

**What to Measure:**
1. **Frequency Response**:
   - Look for smoothing in 250-2000 Hz region
   - Reduced comb filtering (spiky peaks/dips)

2. **RT60 (Reverberation Time)**:
   - May increase slightly (diffusion spreads energy)
   - Decay should be smoother, not harsh

3. **Waterfall Plot**:
   - Resonances should decay faster
   - Reduced modal ringing

---

## Part 6: Troubleshooting

### Problem: Not Hearing Much Difference

**Possible Causes:**
- Not enough coverage (try adding more tiles)
- Placed in wrong location (try first reflection points)
- Room too large (need absorption too)
- Unrealistic expectations (subtle improvement is normal)

**Solutions:**
- Start with 4-6 tiles minimum
- Combine with corner absorbers for bass
- Treat multiple surfaces (not just one wall)

### Problem: Tiles Vibrating/Rattling

**Causes:**
- Insufficient mounting rigidity
- Resonance with room mode

**Solutions:**
- Add more bolts or adhesive
- Use heavier backing board
- Add dampening material behind tiles

### Problem: Tiles Warped After Printing

**Prevention:**
- Print in enclosure (for ABS) or use PLA
- Ensure even bed temperature
- Add brim for better adhesion
- Reduce print speed for large parts

**Fix:**
- Heat gun + flat surface (carefully!)
- Use mounting pressure to flatten
- Slight warping usually OK (still functional)

---

## Part 7: Maintenance

### Cleaning
- Dust with soft brush or compressed air
- Vacuum with brush attachment (gentle)
- Do NOT wet-clean (water in cavities)

### Longevity
- PLA: 5-10 years indoors (may become brittle)
- PETG/ABS: 10+ years
- Avoid direct sunlight (UV degrades plastic)
- Normal room humidity is fine

### Repairs
- Broken tile: Replace individually
- Crack: Plastic weld or epoxy
- Clogged slits: Clear with thin wire

---

## Part 8: Advanced Modifications

### Adding Absorption

**Option 1: Backing Fill**
- Fill 50% of space behind panel with fiberglass/rockwool
- Increases low-frequency absorption
- Reduces pure reflection (more hybrid performance)

**Option 2: Perforated Front**
- Add thin perforated cover over front (5-10% open area)
- Aesthetic + adds impedance matching
- Slight performance change

### Different Tile Orientations

**Checkerboard Pattern**:
```
┌────┬────┐
│ ══ │ ║║ │  Alternate horizontal and vertical
├────┼────┤  (need to print some rotated)
│ ║║ │ ══ │
└────┴────┘
```

**Mixed Array**:
- Print some tiles with different parameters
- Create non-periodic arrangement
- May improve diffusion uniformity

---

## Safety Notes

⚠️ **Important:**
- Panels should be securely mounted (prevent falling)
- Keep away from heat sources (PLA softens at ~60°C)
- Not rated for structural applications
- Follow local building codes for wall attachments

---

## Questions?

**Mounting questions:** See structural engineering guidelines for your wall type  
**Acoustic questions:** Consult acoustics references or hire professional  
**Print questions:** Check printer manufacturer support or 3D printing communities

---

*Good luck with your build! The difference may be subtle at first, but your ears will thank you.*
