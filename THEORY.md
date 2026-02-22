# Technical Theory
## Metadiffuser Acoustic Physics & Design Principles

---

## 1. Background: The Problem with Traditional Diffusers

### Quarter-Wavelength Resonators

Traditional Schroeder diffusers use **quarter-wavelength resonators** (QWRs) - essentially tubes or wells with rigid backing. The resonant frequency is:

```
f₀ = c₀ / (4L)

Where:
- c₀ = speed of sound (343 m/s at 20°C)
- L = well depth
```

For **250 Hz** (low mid-range):
```
L = 343 / (4 × 250) = 0.343 m = 34.3 cm
```

This is **impractically deep** for wall-mounted treatments!

### Phase Grating Principles

Schroeder diffusers work by creating **spatially-dependent phase shifts**:
- Different well depths create different reflection phases
- Sequence chosen so Fourier spectrum is flat
- Energy distributed uniformly across angles

Common sequences:
- **Quadratic Residue (QRD)**: sₙ = n² mod N
- **Primitive Root (PRD)**: sₙ = rⁿ mod P  
- **Ternary Sequence**: sₙ ∈ {-1, 0, 1}

---

## 2. The Metadiffuser Solution

### Key Innovation: Slow Sound

Metadiffusers achieve deep-subwavelength operation by:

1. **Loading slits with Helmholtz resonators**
2. **Creating strong dispersion** → slow sound
3. **Reducing effective wavelength** inside material
4. **Same phase shift, much less depth**

### Helmholtz Resonator Physics

A Helmholtz resonator is an acoustic mass-spring system:

```
        Neck (mass)
         ┃┃┃
      ┏━━┛┗━━┓
      ┃      ┃  Cavity (spring/compliance)
      ┃      ┃
      ┗━━━━━━┛

Resonant frequency:
f_HR = (c₀/2π) × √(A_n / (V_c × l_eff))

Where:
- A_n = neck area
- V_c = cavity volume  
- l_eff = effective neck length (includes end corrections)
```

### Dispersion Relation

When HRs are coupled to a waveguide (slit), the dispersion relation becomes:

```
k²(ω) = (ω²/c₀²) × [1 + σ × F_HR(ω)]

Where:
- k = wavenumber in loaded waveguide
- ω = angular frequency
- σ = porosity (HR neck area / total area)
- F_HR = HR impedance function
```

**Below resonance**: F_HR large and negative → k increases → **slow sound**  
**At resonance**: F_HR → ∞ → **bandgap** (no propagation)  
**Above resonance**: F_HR small → k ≈ k₀ → normal sound

### Phase Speed Reduction

The phase speed in the loaded slit:

```
c_p(ω) = ω / k(ω)

Can be reduced by factor of 10-50×!
```

This means a **2.5 cm deep slit** acts like a **25-125 cm deep well** at the right frequency.

---

## 3. Design Parameters

### Critical Dimensions

**Slit Width (h)**:
- Range: 2-5 mm typical
- **Narrower** → more viscous losses (absorption)
- **Wider** → less damping (more reflection)
- Trade-off: diffusion vs absorption

**Slit Depth (L)**:
- Target: λ₀/20 to λ₀/50
- For 250 Hz: 1.7-4.3 cm
- This design: 25 mm (λ₀/55 at 250 Hz)

**HR Neck Dimensions**:
- Width: 1.5-3 mm
- Length: 1.5-3 mm
- **Smaller** → higher Q (sharper resonance)
- **Larger** → broader bandwidth

**HR Cavity Dimensions**:
- Width: 6-12 mm
- Depth: 7-11 mm
- **Larger** → lower resonant frequency
- Volume determines "spring constant"

**Resonator Spacing**:
- Vertical: 5-20 mm between HRs
- Must fit within slit depth
- More HRs → more resonances → broader bandwidth

### Tuning Strategy

Each slit has different configuration:

| Slit | Width | HR Count | Target Behavior |
|------|-------|----------|-----------------|
| 1 | 3.0 mm | 3 | Low-mid absorption peaks |
| 2 | 3.5 mm | 2 | Mid-frequency diffusion |
| 3 | 4.0 mm | 3 | Mid-high diffusion |
| 4 | 3.0 mm | 2 | Balanced response |

This creates **non-uniform spatial impedance** → diffusion

---

## 4. Loss Mechanisms

### Thermoviscous Losses

In narrow ducts, two loss mechanisms dominate:

**Viscous Losses**:
```
Boundary layer thickness: δ_v = √(2η / (ρ₀ω))

For 1 kHz air: δ_v ≈ 0.18 mm
```

When duct width comparable to boundary layer, viscous drag is significant.

**Thermal Losses**:
```
Thermal boundary layer: δ_t = √(2κ / (ρ₀c_pω))

For 1 kHz air: δ_t ≈ 0.21 mm
```

Heat exchange with walls dissipates acoustic energy.

### Effective Complex Parameters

Losses modeled as complex, frequency-dependent parameters:

```
ρ_eff(ω) = ρ₀ × [1 - tanh(Γ_ρ) / Γ_ρ]⁻¹
κ_eff(ω) = κ₀ × [1 + (γ-1) × tanh(Γ_κ) / Γ_κ]⁻¹

Where:
Γ_ρ = h/2 × √(iωρ₀/η)
Γ_κ = h/2 × √(iωρ₀Pr/η)
```

These give frequency-dependent **attenuation** and **phase velocity**.

### Critical Coupling Condition

Perfect absorption occurs when:
```
Z_surface = Z₀ (impedance matching)
```

This requires:
1. Resonance (reactive part = 0)
2. Resistance = ρ₀c₀ (viscous losses match radiation resistance)

At critical coupling, **all energy is absorbed** (perfect absorber mode).

---

## 5. Diffusion Metrics

### Diffusion Coefficient

Quantifies scattering uniformity:

```
δ_ϕ = [Σ|R(θ)|²]² - Σ|R(θ)|⁴  
      ─────────────────────────
           Σ|R(θ)|⁴

Normalized: δ_n = (δ_ϕ - δ_flat) / (1 - δ_flat)
```

Where R(θ) is polar response at angle θ.

- **δ_n = 0**: All energy in one direction (specular)
- **δ_n = 1**: Perfectly uniform (Lambertian)
- **δ_n > 0.5**: Good diffuser

### Scattering Coefficient

Alternative metric (ISO 17497-1):

```
s = 1 - |R₀|² / Σ|Rᵢ|²

Where:
- R₀ = specular reflection coefficient
- Σ|Rᵢ|² = total scattered energy
```

High scattering coefficient → energy spread away from specular direction.

---

## 6. Frequency Response Prediction

### Transfer Matrix Method

Sound propagation through metamaterial modeled as:

```
[P]     [T₁₁  T₁₂] [P]
[V]   = [T₂₁  T₂₂] [V]
   y=0             y=L

Where T = M_Δl × (M_slit × M_HR × M_slit)^M
```

Each layer has transfer matrix for:
- Slit propagation (with losses)
- HR scattering
- End corrections (radiation impedance)

Reflection coefficient:
```
R = (T₁₁ - Z₀T₂₁) / (T₁₁ + Z₀T₂₁)
```

### Resonance Frequencies (Approximate)

For this design's typical HR:

```
Neck: 2 mm × 2 mm × 2 mm
Cavity: 9 mm × 9 mm × 9 mm

f_HR ≈ 343/(2π) × √(4/(81×10⁻⁶ × 2×10⁻³))
    ≈ 1350 Hz
```

Multiple HRs create **multiple resonances** from 300-3000 Hz range.

### Effective Quarter-Wavelength Depth

The metamaterial acts as if it were a QWR with effective depth:

```
L_eff = c₀/(4f) × c₀/c_p(f)
      = L × c₀/c_p(f)
      ≈ 25 mm × 10-50
      ≈ 0.25 - 1.25 m equivalent!
```

---

## 7. Optimization Considerations

### Design Trade-offs

**More HRs per slit:**
- ✅ Broader bandwidth
- ✅ More absorption peaks
- ❌ More complex to print
- ❌ Reduced structural strength

**Narrower slits:**
- ✅ Higher viscous losses (absorption)
- ✅ Better impedance matching
- ❌ Harder to print accurately
- ❌ Risk of clogging

**Deeper panel:**
- ✅ Lower frequency extension
- ✅ Better low-frequency diffusion
- ❌ Uses more material
- ❌ Deeper wall mounting needed

### Multi-Objective Optimization

Ideal metadiffuser maximizes:

```
Objective = ∫[f_low to f_high] δ_n(f) df

Subject to:
- L < L_max (thickness constraint)
- h > h_min (printability constraint)
- Structural integrity
- Manufacturing constraints
```

This design used manual optimization targeting 250-2000 Hz with L = 25 mm.

---

## 8. Comparison to Traditional Designs

### Performance per Unit Depth

| Design Type | Thickness | Lowest f | λ/thickness |
|-------------|-----------|----------|-------------|
| QRD (250 Hz) | 343 mm | 250 Hz | ~4 |
| Folded QRD | 170 mm | 250 Hz | ~8 |
| Metadiffuser | 25 mm | 250 Hz | **~55** |

Metadiffuser is **14× thinner** than QRD, **7× thinner** than folded QRD.

### Trade-offs

**Advantages:**
- Extremely thin
- Combines diffusion + absorption
- Can be 3D printed
- Frequency-tunable by design

**Disadvantages:**
- More complex to manufacture
- Thermoviscous losses (reduces reflection coefficient)
- Performance drops if features clogged
- Less low-frequency energy than thick panels

---

## 9. Extensions & Future Work

### Potential Improvements

**Broadband Design:**
- More slits (7-11 per tile)
- Wider range of HR sizes
- Multiple HR layers in depth

**Variable Absorption:**
- Some slits critically coupled (perfect absorbers)
- Other slits phase-inverting (pure reflectors)
- Ternary sequence implementation

**Non-Planar Designs:**
- Curved panels
- Corner treatments
- Ceiling clouds

**Material Variants:**
- Printed with flexible filament (TPU) for damping
- Two-material prints (rigid + compliant)
- Hybrid foam + metamaterial

### Active Research Areas

- **Nonlinear metadiffusers**: Amplitude-dependent diffusion
- **Tunable metadiffusers**: Adjustable resonator volumes
- **Metasurfaces**: Single-layer extreme designs
- **Optimization algorithms**: AI-designed diffuser patterns

---

## 10. References & Further Reading

### Key Papers

1. **Original Metadiffuser Paper**:
   Jiménez et al., *Sci. Rep.* 7, 5389 (2017)

2. **Helmholtz Resonator Arrays**:
   Yang et al., *Phys. Rev. Lett.* 101, 204301 (2008)

3. **Perfect Absorption**:
   Romero-García et al., *Sci. Rep.* 6, 19519 (2016)

4. **Slow Sound Metamaterials**:
   Groby et al., *J. Acoust. Soc. Am.* 139, 1660 (2016)

### Books

- Cox & D'Antonio: *Acoustic Absorbers and Diffusers* (3rd ed., 2016)
- Everest & Pohlmann: *Master Handbook of Acoustics* (6th ed., 2015)
- Kinsler et al.: *Fundamentals of Acoustics* (4th ed., 1999)

### Online Resources

- **Acoustic Surfaces Calculator**: http://www.acoustic.ua
- **Room EQ Wizard**: https://www.roomeqwizard.com/
- **Acoustics subreddit**: r/audioengineering, r/acoustics

---

## Appendix: Glossary

**Bandgap**: Frequency range where wave propagation is forbidden  
**Critical coupling**: Impedance matching condition for perfect absorption  
**Dispersion**: Frequency-dependence of wave velocity  
**Helmholtz resonator**: Acoustic cavity resonator (neck + volume)  
**Locally reacting**: Surface response depends only on local pressure (not spatial derivatives)  
**Metasurface**: Subwavelength-structured surface with unusual properties  
**Quarter-wavelength resonator**: Tube with rigid backing, resonant at L = λ/4  
**Schroeder diffuser**: Phase grating diffuser using number-theoretic sequences  
**Slow sound**: Reduced phase velocity due to resonant scattering  
**Thermoviscous losses**: Energy dissipation via viscosity and heat conduction

---

*This document provides the theoretical foundation. For practical implementation, see README.md and ASSEMBLY.md.*
