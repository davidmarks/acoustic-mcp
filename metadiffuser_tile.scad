// Metadiffuser Tile - Acoustic Panel
// Frequency range: 250-2000 Hz
// Based on: Jiménez et al. (2017) Nature Scientific Reports
// Tile size: 160×160×25mm

$fn = 32; // Resolution

module helmholtz_resonator(neck_w, neck_l, cavity_w, cavity_d, slit_w) {
    // Neck connecting slit to cavity
    translate([slit_w/2, -neck_w/2, 0])
        cube([neck_l, neck_w, neck_w]);
    
    // Resonant cavity
    translate([slit_w/2 + neck_l, -cavity_w/2, -cavity_d/2 + neck_w/2])
        cube([cavity_w, cavity_w, cavity_d]);
}

// Main model
difference() {
    // Base block (solid)
    cube([160, 160, 25]);
    
    // Slits and Helmholtz resonators
    // Slit 1 (width: 3.0mm)
    translate([20.0, 0, 2.0]) {
        // Main slit cavity
        translate([-1.5, 0, 0])
            cube([3.0, 160, 23.0]);
        
        // Helmholtz resonators
        // HR 1 at y=5mm
        translate([0, 5, 0])
            helmholtz_resonator(2.0, 2.0, 
                              8.0, 8.0, 3.0);
        // HR 2 at y=12mm
        translate([0, 12, 0])
            helmholtz_resonator(1.5, 2.5, 
                              10.0, 10.0, 3.0);
        // HR 3 at y=19mm
        translate([0, 19, 0])
            helmholtz_resonator(2.5, 1.5, 
                              6.0, 7.0, 3.0);
    }

    // Slit 2 (width: 3.5mm)
    translate([60.0, 0, 2.0]) {
        // Main slit cavity
        translate([-1.75, 0, 0])
            cube([3.5, 160, 23.0]);
        
        // Helmholtz resonators
        // HR 1 at y=6mm
        translate([0, 6, 0])
            helmholtz_resonator(2.5, 2.0, 
                              9.0, 9.0, 3.5);
        // HR 2 at y=16mm
        translate([0, 16, 0])
            helmholtz_resonator(1.8, 3.0, 
                              12.0, 11.0, 3.5);
    }

    // Slit 3 (width: 4.0mm)
    translate([100.0, 0, 2.0]) {
        // Main slit cavity
        translate([-2.0, 0, 0])
            cube([4.0, 160, 23.0]);
        
        // Helmholtz resonators
        // HR 1 at y=4mm
        translate([0, 4, 0])
            helmholtz_resonator(1.5, 2.5, 
                              11.0, 10.0, 4.0);
        // HR 2 at y=11mm
        translate([0, 11, 0])
            helmholtz_resonator(2.0, 2.0, 
                              7.0, 8.0, 4.0);
        // HR 3 at y=18mm
        translate([0, 18, 0])
            helmholtz_resonator(2.5, 1.8, 
                              9.0, 8.5, 4.0);
    }

    // Slit 4 (width: 3.0mm)
    translate([140.0, 0, 2.0]) {
        // Main slit cavity
        translate([-1.5, 0, 0])
            cube([3.0, 160, 23.0]);
        
        // Helmholtz resonators
        // HR 1 at y=7mm
        translate([0, 7, 0])
            helmholtz_resonator(2.2, 2.2, 
                              10.0, 9.0, 3.0);
        // HR 2 at y=15mm
        translate([0, 15, 0])
            helmholtz_resonator(1.6, 2.8, 
                              8.5, 10.5, 3.0);
    }

    // Mounting holes (M4)
    translate([10, 10, 12.5])
        cylinder(d=4.5, h=27, center=true);
    translate([150, 10, 12.5])
        cylinder(d=4.5, h=27, center=true);
    translate([10, 150, 12.5])
        cylinder(d=4.5, h=27, center=true);
    translate([150, 150, 12.5])
        cylinder(d=4.5, h=27, center=true);
}
