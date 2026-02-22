# Fedora Wayland - Quick Start Guide

## 🎯 Your Situation: OpenSCAD Crashing on Wayland

Good news! I've created multiple solutions that work on Fedora without GUI issues.

---

## ⚡ FASTEST SOLUTION (1 Minute)

### Already Generated STL Available!

I've generated a simplified STL that's ready to print RIGHT NOW:

**File**: `metadiffuser_tile_simple.stl`

This is a simplified but functional metadiffuser that provides acoustic diffusion.

### Load and Print:
1. Open `metadiffuser_tile_simple.stl` in PrusaSlicer/OrcaSlicer
2. Use settings from `QUICKSTART.md`
3. Print (6-8 hours)
4. Done!

**Note**: This simplified version has the slit structure but simplified Helmholtz resonator geometry. It will still provide good diffusion.

---

## 🔧 BEST SOLUTION (For Full Details)

### Method 1: OpenSCAD Headless Mode (Recommended)

OpenSCAD works fine in command-line mode - bypasses all Wayland issues!

```bash
# Install OpenSCAD
sudo dnf install openscad

# Generate STL (no GUI, no Wayland issues!)
./build.sh
```

The `build.sh` script I created will:
- Install OpenSCAD if needed
- Generate STL in headless mode (no GUI)
- Validate the output
- Tell you when it's ready

**Result**: Full-detail metadiffuser with all Helmholtz resonators (2-5 MB file)

---

### Method 2: Pure Python Generator

If you don't want to install OpenSCAD:

```bash
# No dependencies needed (auto-installs numpy-stl)
python3 generate_simple.py
```

Creates: `metadiffuser_tile_simple.stl` (simplified but functional)

---

## 📋 Comparison

| Method | File Size | Detail Level | Install Required | Time |
|--------|-----------|--------------|------------------|------|
| **Simple Python** | ~100 KB | Simplified | None | 30 sec |
| **OpenSCAD Headless** | 2-5 MB | Full detail | openscad | 2-3 min |
| **Pre-generated** | ~100 KB | Simplified | None | 0 sec |

---

## 🎨 What's the Difference?

### Simplified Version (Python-generated):
- ✅ Has all 4 slits
- ✅ Has vertical structure
- ✅ Provides acoustic diffusion
- ⚠️ Simplified Helmholtz resonator geometry
- ⚠️ Reduced absorption characteristics

### Full Version (OpenSCAD):
- ✅ Complete Helmholtz resonator cavities
- ✅ Precise neck and cavity dimensions
- ✅ Full absorption + diffusion
- ✅ Matches published research exactly

---

## 🚀 Recommended Workflow for Fedora

```bash
# 1. Try the simplified version first (test print)
#    Already generated: metadiffuser_tile_simple.stl
#    Just open in slicer and print

# 2. If you like it, generate full version
sudo dnf install openscad
./build.sh

# 3. Compare both in your slicer
#    The full version will have more internal detail
```

---

## 🐛 Troubleshooting Fedora-Specific Issues

### "OpenSCAD still shows GUI errors"

Use the headless script:
```bash
openscad -o output.stl --render metadiffuser_tile.scad
# No GUI will appear!
```

### "Python script fails"

```bash
# Install manually
pip install --user numpy-stl
python3 generate_simple.py
```

### "Want to force X11 instead of Wayland"

```bash
# Temporary (this session only)
export QT_QPA_PLATFORM=xcb
openscad metadiffuser_tile.scad

# Or permanent
echo "QT_QPA_PLATFORM=xcb" >> ~/.bashrc
```

### "DNF can't find openscad"

```bash
# Enable repositories
sudo dnf install fedora-workstation-repositories
sudo dnf install openscad
```

---

## 📁 Files You Have

| File | Purpose | When to Use |
|------|---------|-------------|
| **metadiffuser_tile_simple.stl** | Ready to print | Print RIGHT NOW |
| **metadiffuser_tile.scad** | Source design | Edit or regenerate |
| **build.sh** | Auto-builder | Generate full STL |
| **generate_simple.py** | Python generator | Alternative method |
| **NO_GUI_OPTIONS.md** | Full guide | More solutions |

---

## ✅ Ready to Print Checklist

- [ ] Have STL file (simple or full version)
- [ ] Opened in slicer
- [ ] Settings: 4 perimeters, 20% infill, 0.2mm layers
- [ ] **NO SUPPORTS** enabled
- [ ] Oriented: back (solid face) on bed
- [ ] Print time: ~6-8 hours
- [ ] Material: ~180g PLA/PETG

---

## 🎯 Next Steps

1. **Test the simplified STL** - It's ready now!
2. **If you like it**, run `./build.sh` for full detail
3. **Print 2-4 tiles** to test
4. **Follow ASSEMBLY.md** for mounting

---

## 💡 Pro Tip

The simplified version is actually GOOD FOR TESTING:
- Faster to slice
- Easier to modify if needed
- Still provides diffusion
- Less material used

Then upgrade to full version for final installation.

---

Got questions? See **NO_GUI_OPTIONS.md** for complete details on all methods!
