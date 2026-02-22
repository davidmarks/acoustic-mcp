#!/bin/bash
# Metadiffuser STL Generator for Fedora
# Handles Wayland issues with OpenSCAD

set -e  # Exit on error

echo "======================================"
echo "METADIFFUSER STL GENERATOR"
echo "Fedora/Wayland Compatible"
echo "======================================"
echo

# Check if OpenSCAD is installed
if ! command -v openscad &> /dev/null; then
    echo "OpenSCAD not found. Installing..."
    echo
    sudo dnf install -y openscad
    echo
fi

# Generate STL using headless mode (bypasses Wayland GUI issues)
echo "Generating STL using OpenSCAD (headless mode)..."
echo "This may take 1-3 minutes..."
echo

openscad -o metadiffuser_tile.stl \
         --render \
         --export-format binstl \
         metadiffuser_tile.scad

echo
echo "✓ STL Generated Successfully!"
echo

# Validate
if [ -f metadiffuser_tile.stl ]; then
    SIZE=$(stat --format=%s metadiffuser_tile.stl)
    SIZE_KB=$((SIZE / 1024))
    echo "File: metadiffuser_tile.stl"
    echo "Size: ${SIZE_KB} KB"
    echo
    
    if [ $SIZE_KB -lt 100 ]; then
        echo "⚠ Warning: File seems small. Model may be incomplete."
        echo "   Try running again or use Python method."
    else
        echo "✓ File size looks good!"
        echo
        echo "Next steps:"
        echo "1. Open metadiffuser_tile.stl in your slicer"
        echo "2. Follow settings in QUICKSTART.md"
        echo "3. Print with NO SUPPORTS"
    fi
else
    echo "✗ Error: STL file not created"
    echo
    echo "Alternative method:"
    echo "  python3 generate_stl_build123d.py"
fi

echo
echo "======================================"
