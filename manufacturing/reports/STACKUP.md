# JLCPCB 4-LAYER CONTROLLED IMPEDANCE STACKUP & 50-OHM TRACE CALCULATION

## 1. Stackup Specification: JLC04161H-7628
- **Total Board Thickness:** 1.6 mm ±10%
- **Target Layers:** 4 Copper Layers
- **Finished Copper:** 1 oz Outer (L1, L4), 0.5 oz Inner (L2, L3)
- **Base Material:** Standard FR-4 (Tg 130–140°C)
- **Surface Finish:** Lead-Free HASL or ENIG (Electroless Nickel Immersion Gold recommended for RF)

### Detailed Layer Build-up
| Layer | Name | Type | Thickness | Material / Dielectric Constant |
|---|---|---|---|---|
| Top | Solder Mask | Surface | 0.015 mm | Taiyo Solder Resist (Er = 3.5) |
| L1 | Top Signal / RF | Copper | 0.035 mm (1 oz) | Base Copper Foil |
| Dielectric | L1–L2 Prepreg | Prepreg | 0.2104 mm | 7628 Prepreg (Er = 4.6 @ 868 MHz) |
| L2 | Ground Plane | Copper | 0.0175 mm (0.5 oz)| Solid Reference Plane |
| Dielectric | L2–L3 Core | Core | 1.065 mm | FR-4 Core (Er = 4.5 @ 868 MHz) |
| L3 | Power (3V3) | Copper | 0.0175 mm (0.5 oz)| Split Plane & Internal Signals |
| Dielectric | L3–L4 Prepreg | Prepreg | 0.2104 mm | 7628 Prepreg (Er = 4.6 @ 868 MHz) |
| L4 | Bottom Signal | Copper | 0.035 mm (1 oz) | Secondary Ground Pour & Signals |
| Bottom| Solder Mask | Surface | 0.015 mm | Taiyo Solder Resist (Er = 3.5) |

---

## 2. 50-Ohm RF Transmission Line Geometry

### Target: 50.0 Ω Single-Ended Characteristic Impedance @ 868 MHz
Two transmission line geometries were evaluated referencing Layer 2 solid ground:

### Option A: Surface Microstrip (Reference L2 Ground)
- **Dielectric Height ($h$):** 0.2104 mm (8.28 mil)
- **Dielectric Constant ($\epsilon_r$):** 4.60
- **Copper Thickness ($t$):** 0.035 mm (1.38 mil)
- **Calculated Trace Width ($w$):** 0.350 mm (13.78 mil)
- **Resulting Impedance ($Z_0$):** **50.4 Ω**

### Option B: Grounded Coplanar Waveguide (CPWG) — SELECTED ARCHITECTURE
- **Trace Width ($w$):** **0.290 mm (11.42 mil)**
- **Gap to Top Ground Pour ($s$):** **0.200 mm (7.87 mil)**
- **Dielectric Height to L2 ($h$):** 0.2104 mm
- **Copper Thickness ($t$):** 0.035 mm
- **Ground Stitching Via Pitch:** 1.0 mm along both coplanar ground shields
- **Resulting Impedance ($Z_0$):** **50.0 Ω ± 1.5%**

### Why CPWG Was Selected:
1. **Superior Noise Immunity:** The coplanar ground guards shield sensitive RF voice packets from high-speed digital I2S clock lines and switching noise.
2. **Narrower Trace Width:** At 0.29 mm width, the trace matches the pad widths of 0402 matching components (0.30 mm pad width) with virtually zero parasitic discontinuity or step change in trace geometry.
3. **Reproducibility on JLCPCB:** 0.29 mm trace with 0.20 mm clearance easily complies with standard JLCPCB fabrication limits (minimum 0.127 mm trace / 0.127 mm space).
