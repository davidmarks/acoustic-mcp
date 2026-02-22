# STL Generation Without GUI
## Solutions for Wayland/Fedora Issues

---

## ⚡ Quick Solution (Recommended)

### Option 1: Python Generator with build123d

```bash
# Run the Python generator (installs dependencies automatically)
python3 generate_stl_build123d.py
```

This will create `metadiffuser_tile_b123d.stl` - ready to slice!

---

## 🔧 All Available Methods

### Method 1: Build123d (Python, No GUI)
**Best for: Most reliable, modern CAD kernel**

```bash
# Install build123d
pip install build123d --break-system-packages

# Generate STL
python3 generate_stl_build123d.py
```

**Pros:**
- ✅ No GUI required
- ✅ Robust boolean operations  
- ✅ Fast
- ✅ Validates output

**Cons:**
- Larger dependency install (~100MB)

---

### Method 2: OpenSCAD Headless (CLI Only)
**Best for: If you have OpenSCAD installed**

```bash
# Install OpenSCAD (headless works fine)
sudo dnf install openscad

# Generate STL from command line (no GUI!)
openscad -o metadiffuser_tile.stl \
         --render \
         metadiffuser_tile.scad
```

**Pros:**
- ✅ No GUI interaction needed
- ✅ Official OpenSCAD engine
- ✅ Bypasses Wayland issue

**Cons:**
- Needs OpenSCAD installed
- Can be slow (1-3 minutes render)

**Environment variable workaround for Wayland:**
```bash
# If GUI mode needed, force X11:
QT_QPA_PLATFORM=xcb openscad metadiffuser_tile.scad
```

---

### Method 3: FreeCAD Python Console
**Best for: If you already have FreeCAD**

```bash
# Install FreeCAD
sudo dnf install freecad

# Create FreeCAD script
cat > generate_freecad.py << 'FREECAD_SCRIPT'
import FreeCAD
import Part
import Mesh
import json

# Load design
with open('metadiffuser_design.json', 'r') as f:
    design = json.load(f)

tile_w = design['tile_size']['width']
tile_h = design['tile_size']['height']
tile_d = design['tile_size']['depth']
back_thickness = design['print_settings']['back_thickness']

# Create base
doc = FreeCAD.newDocument("Metadiffuser")
base = doc.addObject("Part::Box", "Base")
base.Length = tile_w
base.Width = tile_h
base.Height = tile_d

# Calculate slit positions
n_slits = design['n_slits']
spacing = design['slit_spacing']
start_x = (tile_w - (n_slits - 1) * spacing) / 2

cuts = []

# Create slits
for i, slit_config in enumerate(design['slits']):
    slit_center_x = start_x + i * spacing
    slit_w = slit_config['slit_width']
    slit_depth = tile_d - back_thickness
    
    # Main slit cut
    slit = doc.addObject("Part::Box", f"Slit{i}")
    slit.Length = slit_w
    slit.Width = tile_h
    slit.Height = slit_depth
    slit.Placement.Base = FreeCAD.Vector(
        slit_center_x - slit_w/2, 
        0, 
        back_thickness
    )
    cuts.append(slit)
    
    # Helmholtz resonators
    for j, hr in enumerate(slit_config['resonators']):
        # Neck
        neck = doc.addObject("Part::Box", f"Neck{i}_{j}")
        neck.Length = hr['neck_length']
        neck.Width = hr['neck_width']
        neck.Height = hr['neck_width']
        neck.Placement.Base = FreeCAD.Vector(
            slit_center_x + slit_w/2,
            hr['position'] - hr['neck_width']/2,
            back_thickness
        )
        cuts.append(neck)
        
        # Cavity
        cavity = doc.addObject("Part::Box", f"Cavity{i}_{j}")
        cavity.Length = hr['cavity_width']
        cavity.Width = hr['cavity_width']
        cavity.Height = hr['cavity_depth']
        cavity.Placement.Base = FreeCAD.Vector(
            slit_center_x + slit_w/2 + hr['neck_length'],
            hr['position'] - hr['cavity_width']/2,
            back_thickness
        )
        cuts.append(cavity)

doc.recompute()

# Perform boolean operations
print("Performing boolean cuts...")
result = base.Shape
for cut in cuts:
    result = result.cut(cut.Shape)

# Add mounting holes
hole_dia = design['mounting']['screw_hole_diameter']
corner_inset = design['mounting']['corner_inset']

hole_positions = [
    (corner_inset, corner_inset),
    (tile_w - corner_inset, corner_inset),
    (corner_inset, tile_h - corner_inset),
    (tile_w - corner_inset, tile_h - corner_inset)
]

for hx, hy in hole_positions:
    hole = Part.makeCylinder(hole_dia/2, tile_d, 
                             FreeCAD.Vector(hx, hy, 0),
                             FreeCAD.Vector(0, 0, 1))
    result = result.cut(hole)

# Export to STL
print("Exporting STL...")
Mesh.export([result], 'metadiffuser_tile_freecad.stl')

print("✓ STL generated: metadiffuser_tile_freecad.stl")

FreeCAD.closeDocument(doc.Name)
FREECAD_SCRIPT

# Run headless
freecad --console generate_freecad.py
```

**Pros:**
- ✅ No GUI needed
- ✅ Powerful CAD engine
- ✅ Good for modifications

**Cons:**
- FreeCAD can be heavy install
- Boolean ops can be slow

---

### Method 4: Use Online Service (Last Resort)
**Best for: Quick one-time generation**

1. Upload `metadiffuser_tile.scad` to **OpenJSCAD** (web-based):
   - https://openjscad.xyz/ (may need conversion)

2. Or use **OnShape** (free CAD, cloud-based):
   - Import SCAD or rebuild geometry
   - Export STL

**Pros:**
- ✅ No local install
- ✅ Works from any browser

**Cons:**
- Requires internet
- Need to convert SCAD format

---

## 📦 Pre-Generated STL Available

I can also generate the STL in this environment and provide it to you directly:

```bash
# Run either:
python3 generate_stl_build123d.py

# Or simpler (already ran):
python3 generate_stl.py
```

The `metadiffuser_tile.stl` file (28KB) is already generated, but appears to be simplified. Let me generate a better version...

---

## 🔍 Validation

After generating, validate your STL:

```bash
# Check with Python
python3 << 'EOF'
import trimesh
mesh = trimesh.load('YOUR_FILE.stl')
print(f"Vertices: {len(mesh.vertices):,}")
print(f"Faces: {len(mesh.faces):,}")
print(f"Watertight: {mesh.is_watertight}")
print(f"Volume: {mesh.volume:,.0f} mm³")
print(f"Expected: ~450,000-500,000 mm³")
EOF
```

Expected results:
- **Vertices**: 1,000-10,000
- **Faces**: 2,000-20,000  
- **Volume**: ~450,000-500,000 mm³ (with cuts)
- **Watertight**: True

---

## ⚙️ Which Method Should I Use?

| Scenario | Recommended Method |
|----------|-------------------|
| Want it NOW | Python generator (Method 1) |
| Have OpenSCAD installed | Headless command (Method 2) |
| Have FreeCAD installed | FreeCAD script (Method 3) |
| Want to modify design | Edit .scad + Method 2 |
| No dependencies wanted | Use online service (Method 4) |

---

## 🐛 Troubleshooting

**"build123d install fails"**
```bash
# Try system packages first
sudo dnf install python3-build123d
# Or use venv
python3 -m venv ~/metadiffuser-env
source ~/metadiffuser-env/bin/activate
pip install build123d
```

**"OpenSCAD command not found"**
```bash
sudo dnf install openscad
# Or download from: https://openscad.org/downloads.html
```

**"Generated STL looks wrong in slicer"**
- Check file size (should be >500KB for complete model)
- Verify with validation script above
- Try different generation method

**"Still getting Wayland errors"**
```bash
# Force X11 for this session
export QT_QPA_PLATFORM=xcb
openscad metadiffuser_tile.scad

# Or use headless mode (no GUI at all)
openscad -o output.stl --render metadiffuser_tile.scad
```

---

## 📝 Next Steps

1. Choose your method above
2. Generate the STL
3. Validate it (check size ~500KB+, not 28KB)
4. Load into your slicer (PrusaSlicer, OrcaSlicer, etc.)
5. Follow QUICKSTART.md for print settings

---

## 💡 Want to Modify the Design?

Edit `metadiffuser_design.json` then regenerate:

```json
{
  "tile_size": {
    "width": 160,     // Change dimensions
    "height": 160,
    "depth": 30       // Make thicker for lower freq
  },
  // ... modify resonator dimensions
}
```

Then run your chosen generator again!
